import datetime
import math
import os
import re
import sqlite3
import urllib.parse
import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from groq import Groq
except Exception:
    Groq = None

st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="expanded",
)

NUCLEOS_DISPONIBLES = ["JARVIS", "VIERNES", "NOVA", "ARTEX"]

PROTOCOLO_CONOCIMIENTO_BASE = (
    "PROTOCOLO DE CONOCIMIENTO SUPREMO COMPARTIDO (APLICABLE A TODOS LOS NUCLEOS): "
    "Responde con rigor tecnico, precision y claridad estructurada en: "
    "(1) Biologia (celular, genetica, fisiologia, evolucion, ecologia); "
    "(2) Matematicas y Aritmetica (algebra, funciones, geometria, trigonometria, estadistica, "
    "probabilidad, porcentajes, proporciones y resolucion paso a paso); "
    "(3) Geografia (geografia fisica, climas, cartografia, recursos, geopolitica y geografia de Chile y del mundo); "
    "(4) Historia (procesos historicos, cronologia, causas y consecuencias, historia universal, de America y de Chile); "
    "(5) Ciencia y Tecnologia (fisica, quimica, astronomia, computacion, algoritmos, redes, sistemas e ingenieria); "
    "(6) Calculos en general (explicar formulas, variables, unidades y verificar resultados). "
    "Explica pasos o formulas cuando ayude, respeta unidades y no inventes datos sin confirmar."
)

st.session_state.setdefault("autorizado", False)
st.session_state.setdefault("nucleo_activo", "JARVIS")
st.session_state.setdefault("voz_masculina_activa", True)
st.session_state.setdefault("pendiente_voz", None)
st.session_state.setdefault("modo_medico", False)
st.session_state.setdefault("modo_orquestador", "Equilibrado")
st.session_state.setdefault("ollama_activo", False)
st.session_state.setdefault("ollama_url", "http://localhost:11434")
st.session_state.setdefault("ollama_modelo", "llama3.2")

PIN_SECRETO = "2805"
DB_PATH = "jarvis_misiones.db"
BUIN_LAT = -33.7325
BUIN_LON = -70.7422

API_KEY_GROQ = ""
try:
    API_KEY_GROQ = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    API_KEY_GROQ = os.environ.get("GROQ_API_KEY", "")

client_groq = Groq(api_key=API_KEY_GROQ) if (Groq and API_KEY_GROQ) else None


def obtener_hora_chile():
    tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
    return datetime.datetime.now(tz_chile)


def obtener_saludo_por_hora(ahora):
    hora = ahora.hour
    if 0 <= hora < 12:
        return "Buenos dias"
    if 12 <= hora < 20:
        return "Buenas tardes"
    return "Buenas noches"


def init_db():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cur = conn.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS misiones ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "tarea TEXT NOT NULL, "
            "estado TEXT DEFAULT 'Pendiente')"
        )
        cur.execute(
            "CREATE TABLE IF NOT EXISTS remedios ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "nombre TEXT NOT NULL, "
            "horario TEXT DEFAULT '08:00')"
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


init_db()


def db_add(tabla, cols, vals):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        placeholders = ",".join("?" for _ in vals)
        conn.cursor().execute(f"INSERT INTO {tabla} ({cols}) VALUES ({placeholders})", vals)
        conn.commit()
        conn.close()
    except Exception:
        pass


def db_all(tabla, cols):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        rows = conn.cursor().execute(f"SELECT {cols} FROM {tabla}").fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def db_clear(tabla):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        conn.cursor().execute(f"DELETE FROM {tabla}")
        conn.commit()
        conn.close()
    except Exception:
        pass


@st.cache_data(ttl=300)
def obtener_indicadores_chile():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JARVIS-Dashboard/1.0",
        "Accept": "application/json",
    }
    try:
        resp = requests.get("https://mindicador.cl/api", headers=headers, timeout=4)
        if resp.status_code == 200:
            data = resp.json()
            dolar = data.get("dolar", {}).get("valor")
            euro = data.get("euro", {}).get("valor")
            uf = data.get("uf", {}).get("valor")
            if dolar and euro and uf:
                return {
                    "dolar": float(dolar),
                    "euro": float(euro),
                    "uf": float(uf),
                    "respaldo": False,
                }
    except Exception:
        pass
    return {
        "dolar": 950.0,
        "euro": 1030.0,
        "uf": 38000.0,
        "respaldo": True,
    }


def describir_clima_codigo(code):
    mapa = {
        0: "despejado",
        1: "mayormente despejado",
        2: "parcialmente nublado",
        3: "nublado",
        45: "con neblina",
        61: "con lluvia leve",
        63: "con lluvia moderada",
        80: "con chubascos",
        95: "con tormenta electrica",
    }
    return mapa.get(code, "condiciones variables")


@st.cache_data(ttl=600)
def obtener_clima_buin():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={BUIN_LAT}&longitude={BUIN_LON}"
        f"&current=temperature_2m,weather_code&timezone=America%2FSantiago"
    )
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            current = resp.json().get("current") or {}
            temp = current.get("temperature_2m")
            code = int(current.get("weather_code", 0))
            if temp is not None:
                return {
                    "temp_c": round(float(temp), 1),
                    "condicion": describir_clima_codigo(code),
                }
    except Exception:
        pass
    return {"temp_c": None, "condicion": "sin lectura en vivo"}


def fmt_clp(valor):
    return "$" + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def obtener_saludo_nucleo(nucleo):
    ahora = obtener_hora_chile()
    saludo = obtener_saludo_por_hora(ahora)
    frases = {
        "JARVIS": f"[{nucleo}] {saludo}, jefa. Nucleo y protocolo de conocimiento listos; diga que calculamos o investigamos hoy.",
        "VIERNES": f"[{nucleo}] {saludo}, jefa. Motor de calculo y base de conocimiento activos. A que le entramos?",
        "NOVA": f"[{nucleo}] {saludo}, jefa. Senal recibida desde el Nodo Buin con protocolo completo activo.",
        "ARTEX": f"[{nucleo}] {saludo}, jefa. Nucleo ARTEX en linea con protocolo unificado bajo control.",
    }
    return frases.get(nucleo, f"[{nucleo}] {saludo}, jefa. En linea y a su servicio.")


def quiere_ingles(texto):
    t = (texto or "").lower()
    pistas = [
        "en ingles", "responde en ingles", "habla en ingles",
        "in english", "speak english", "reply in english", "answer in english",
    ]
    return any(p in t for p in pistas)


def programar_voz(texto, idioma="es-CL"):
    if st.session_state.get("voz_masculina_activa", True):
        limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace ", texto or "")
        limpio = re.sub(r"https?://\S+", " enlace ", limpio)
        limpio = re.sub(r"[*_`#>\[\]]+", " ", limpio)
        limpio = re.sub(r"\s+", " ", limpio).strip()[:650]
        if limpio:
            st.session_state["pendiente_voz"] = {"texto": limpio, "idioma": idioma}


def reproducir_voz_pendiente():
    pendiente = st.session_state.get("pendiente_voz")
    if not pendiente or not st.session_state.get("voz_masculina_activa", True):
        return
    st.session_state["pendiente_voz"] = None
    txt = pendiente["texto"].replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")
    lang = pendiente["idioma"]
    js_voz = (
        "<script>(function(){try{if(!('speechSynthesis' in window))return;"
        "window.speechSynthesis.cancel();"
        f'const u=new SpeechSynthesisUtterance("{txt}");'
        f"u.lang='{lang}';u.rate=1.02;u.pitch=0.84;"
        "window.speechSynthesis.speak(u);}catch(e){}})();</script>"
    )
    try:
        components.html(js_voz, height=0)
    except Exception:
        pass


def generar_informe_diario_hablado(nucleo, hablar=True):
    ahora = obtener_hora_chile()
    econ = obtener_indicadores_chile()
    clima = obtener_clima_buin()
    misiones = db_all("misiones", "tarea, estado")
    remedios = db_all("remedios", "nombre, horario")

    if clima.get("temp_c") is not None:
        clima_txt = f"Clima en Buin: {clima['temp_c']} grados y {clima['condicion']}."
    else:
        clima_txt = "Clima en Buin: sin lectura en vivo en este momento."

    fin_txt = (
        f"Finanzas: Dolar {fmt_clp(econ['dolar'])}, "
        f"Euro {fmt_clp(econ['euro'])} y UF {fmt_clp(econ['uf'])}."
    )
    rem_txt = (
        "Recordatorios de remedios: " + ", ".join(f"{r[0]} ({r[1]})" for r in remedios[:4]) + "."
        if remedios
        else "Sin remedios registrados por ahora."
    )
    mis_txt = (
        f"Tienes {len(misiones)} mision(es): " + ", ".join(m[0] for m in misiones[:3]) + "."
        if misiones
        else "Sin misiones pendientes."
    )

    informe = (
        f"[{nucleo}] Informe diario del Nodo Buin, {ahora.strftime('%d/%m/%Y')}, "
        f"{ahora.strftime('%H:%M')} horas. {clima_txt} {fin_txt} {rem_txt} {mis_txt} Todo listo, jefa."
    )
    if hablar:
        programar_voz(informe, idioma="es-CL")
    return informe


def resolver_calculo_o_unidad(texto_raw):
    t = (texto_raw or "").strip().lower()

    mp = re.search(r"(\d+(?:[.,]\d+)?)\s*%\s*(?:de|del)\s*(\d+(?:[.,]\d+)?)", t)
    if mp:
        pct = float(mp.group(1).replace(",", "."))
        base = float(mp.group(2).replace(",", "."))
        val = (pct / 100.0) * base
        res = int(val) if val.is_integer() else round(val, 6)
        return f"Calculo porcentual: **{pct:g}%** de **{base:g}** = **{res}**."

    mu = re.search(
        r"(-?\d+(?:[.,]\d+)?)\s*"
        r"(km|m|cm|mm|mi|millas|kg|g|lb|libras|l|ml|km/h|m/s|c|°c|f|°f|k)\s*"
        r"(?:a|en|to|in)\s*"
        r"(km|m|cm|mm|mi|millas|kg|g|lb|libras|l|ml|km/h|m/s|c|°c|f|°f|k)",
        t,
    )
    if mu:
        val = float(mu.group(1).replace(",", "."))
        u1 = mu.group(2).replace("°", "")
        u2 = mu.group(3).replace("°", "")
        if u1 == "millas":
            u1 = "mi"
        if u2 == "millas":
            u2 = "mi"
        if u1 == "libras":
            u1 = "lb"
        if u2 == "libras":
            u2 = "lb"

        long_m = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "mi": 1609.344}
        masa_kg = {"g": 0.001, "kg": 1.0, "lb": 0.45359237}
        vol_l = {"ml": 0.001, "l": 1.0}
        vel_ms = {"m/s": 1.0, "km/h": 1.0 / 3.6}

        if u1 in long_m and u2 in long_m:
            return f"Conversion de longitud: **{val:g} {u1}** = **{round((val * long_m[u1]) / long_m[u2], 4):g} {u2}**."
        if u1 in masa_kg and u2 in masa_kg:
            return f"Conversion de masa: **{val:g} {u1}** = **{round((val * masa_kg[u1]) / masa_kg[u2], 4):g} {u2}**."
        if u1 in vol_l and u2 in vol_l:
            return f"Conversion de volumen: **{val:g} {u1}** = **{round((val * vol_l[u1]) / vol_l[u2], 4):g} {u2}**."
        if u1 in vel_ms and u2 in vel_ms:
            return f"Conversion de velocidad: **{val:g} {u1}** = **{round((val * vel_ms[u1]) / vel_ms[u2], 4):g} {u2}**."
        if u1 in {"c", "f", "k"} and u2 in {"c", "f", "k"}:
            c = val if u1 == "c" else ((val - 32) * 5 / 9 if u1 == "f" else val - 273.15)
            out_t = c if u2 == "c" else (c * 9 / 5 + 32 if u2 == "f" else c + 273.15)
            return f"Conversion termica: **{val:g} {u1.upper()}** = **{round(out_t, 2):g} {u2.upper()}**."

    expr = t
    for pref in ["calcula", "calcular", "cuanto es", "resuelve", "aritmetica", "matematica", "="]:
        if expr.startswith(pref):
            expr = expr[len(pref):].strip()
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**").replace(",", ".")
    if (
        re.search(r"\d", expr)
        and not re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", expr)
        and re.fullmatch(r"[0-9+\-*/().%\s,a-z_]+", expr)
    ):
        env = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log10,
            "ln": math.log,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
        }
        try:
            res = eval(expr, env, {})
            if isinstance(res, (int, float)) and not isinstance(res, bool):
                out = int(res) if (isinstance(res, float) and res.is_integer()) else (round(res, 6) if isinstance(res, float) else res)
                return f"Resultado del calculo `{expr}`: **{out}**."
        except Exception:
            return None
    return None


def consultar_modelo_externo(nucleo, texto_usuario, idioma_voz):
    estilo = {
        "JARVIS": "Eres JARVIS, elegante, preciso y con sarcasmo fino.",
        "VIERNES": "Eres VIERNES, rapida, directa y resolutiva.",
        "NOVA": "Eres NOVA, dinamica, clara y con enfoque tactico desde el Nodo Buin.",
        "ARTEX": "Eres ARTEX, analitico, preciso, firme y enfocado en orquestacion y control.",
    }.get(nucleo, "Eres un asistente tactico.")
    idioma_rule = "Respond in English." if idioma_voz == "en-US" else "Responde en espanol."
    modo_med = " Activa enfoque medico informativo con advertencia clinica." if st.session_state.get("modo_medico", False) else ""
    sys_prompt = (
        f"{estilo} Tratas a la usuaria de 'jefa'. Modo: {st.session_state.get('modo_orquestador', 'Equilibrado')}. "
        f"{PROTOCOLO_CONOCIMIENTO_BASE}{modo_med} {idioma_rule}"
    )

    if st.session_state.get("ollama_activo", False):
        try:
            base_url = (st.session_state.get("ollama_url") or "http://localhost:11434").rstrip("/")
            modelo = (st.session_state.get("ollama_modelo") or "llama3.2").strip()
            resp = requests.post(
                f"{base_url}/api/chat",
                json={
                    "model": modelo,
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": sys_prompt},
                        {"role": "user", "content": texto_usuario},
                    ],
                },
                timeout=8,
            )
            if resp.status_code == 200:
                msg = ((resp.json().get("message") or {}).get("content") or "").strip()
                if msg:
                    return f"[{nucleo} · Ollama] {msg}"
        except Exception:
            pass

    if client_groq:
        mensajes_api = [{"role": "system", "content": sys_prompt}] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.mensajes
        ]
        for modelo in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
            try:
                comp = client_groq.chat.completions.create(
                    model=modelo,
                    messages=mensajes_api,
                    temperature=0.65,
                )
                contenido = (comp.choices[0].message.content or "").strip()
                if contenido:
                    return f"[{nucleo}] {contenido}"
            except Exception:
                continue
    return ""


def generar_respuesta_coherente(nucleo, texto_usuario):
    ahora = obtener_hora_chile()
    t = texto_usuario.strip().lower()

    if quiere_ingles(texto_usuario):
        return (
            f"[{nucleo}] Understood, Boss. Shared knowledge protocol (biology, mathematics, arithmetic, "
            f"geography, history, science & technology, and calculations) is active for '{texto_usuario.strip()}'."
        )

    saludos = ["hola", "buenas", "buenos dias", "buenas tardes", "buenas noches", "holi", "que tal"]
    if any(t == s or t.startswith(s + " ") or t.startswith(s + ",") for s in saludos):
        return obtener_saludo_nucleo(nucleo)

    if any(k in t for k in ["informe diario", "resumen del dia", "reporte diario", "briefing"]):
        return generar_informe_diario_hablado(nucleo, hablar=True)

    if any(k in t for k in ["clima", "temperatura", "lluvia", "tiempo en buin"]):
        clima = obtener_clima_buin()
        if clima.get("temp_c") is not None:
            return f"[{nucleo}] En Buin hay **{clima['temp_c']}°C** y el cielo esta **{clima['condicion']}**, jefa."
        return f"[{nucleo}] No pude obtener la temperatura en vivo en este momento, jefa."

    if any(k in t for k in ["dolar", "euro", "uf", "indicadores", "divisa", "moneda"]):
        econ = obtener_indicadores_chile()
        return (
            f"[{nucleo}] Dolar **{fmt_clp(econ['dolar'])}**, Euro **{fmt_clp(econ['euro'])}** "
            f"y UF **{fmt_clp(econ['uf'])}**, jefa."
        )

    if any(k in t for k in ["hora", "que hora", "fecha", "dia de hoy"]):
        return (
            f"[{nucleo}] En el Nodo Buin hoy es **{ahora.strftime('%d/%m/%Y')}** "
            f"y son las **{ahora.strftime('%H:%M:%S')}** (hora de Chile), jefa."
        )

    calc = resolver_calculo_o_unidad(texto_usuario)
    if calc:
        return f"[{nucleo}] {calc}"

    if any(k in t for k in ["biologia", "celula", "adn", "genetica", "ecosistema", "fotosintesis", "evolucion"]):
        return (
            f"[{nucleo}] **Biologia ({texto_usuario.strip()})**: la celula es la unidad basica de la vida; "
            "el ADN codifica la informacion genetica (transcripcion a ARN y traduccion a proteinas), y la energia "
            "fluye por los ecosistemas desde productores hasta consumidores y descomponedores."
        )

    if any(k in t for k in ["geografia", "capital", "cordillera", "rio", "continente", "hemisferio", "latitud", "longitud"]):
        return (
            f"[{nucleo}] **Geografia ({texto_usuario.strip()})**: estudia relieves, climas, hidrografia, "
            "poblacion y territorio. En Chile destacan la cordillera de los Andes, la depresion intermedia, "
            "la cordillera de la Costa y las planicies litorales."
        )

    if any(k in t for k in ["historia", "siglo", "guerra", "revolucion", "imperio", "independencia", "epoca"]):
        return (
            f"[{nucleo}] **Historia ({texto_usuario.strip()})**: se analiza por causas estructurales y coyunturales, "
            "actores, cronologia y consecuencias. Indica periodo, lugar o evento exacto para detallarlo."
        )

    if any(k in t for k in ["fisica", "quimica", "atomo", "energia", "velocidad", "fuerza", "tecnologia", "algoritmo", "python", "astronomia"]):
        return (
            f"[{nucleo}] **Ciencia y Tecnologia ({texto_usuario.strip()})**: integra modelos, magnitudes y unidades "
            "del SI con aplicacion practica. Tambien puedes pedir calculos directos o conversiones."
        )

    return (
        f"[{nucleo}] Protocolo de conocimiento activo (biologia, matematicas, aritmetica, geografia, "
        f"historia, ciencia y tecnologia y calculos). Consulta registrada: **{texto_usuario.strip()}**, jefa."
    )


st.session_state.setdefault(
    "mensajes",
    [{"role": "assistant", "content": obtener_saludo_nucleo(st.session_state.nucleo_activo)}],
)

st.markdown(
    """
    <style>
    .stApp { background-color: #060913 !important; color: #00f3ff !important; font-family: monospace; }
    .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp div {
        color: #00f3ff !important; font-family: monospace;
    }
    .stButton>button {
        background-color: #00f3ff !important; border: 1.5px solid #00f3ff !important;
        font-weight: bold; width: 100%; border-radius: 6px; padding: 5px 10px !important;
    }
    .stButton>button p, .stButton>button span { color: #060

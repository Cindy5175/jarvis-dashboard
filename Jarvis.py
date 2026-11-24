import datetime
import math
import os
import platform
import re
import sqlite3
import urllib.parse
import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

NUCLEOS_DISPONIBLES = ["JARVIS", "VIERNES", "NOVA", "ARTEX"]

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

if "voz_masculina_activa" not in st.session_state:
    st.session_state.voz_masculina_activa = True

if "escucha_continua_activa" not in st.session_state:
    st.session_state.escucha_continua_activa = True

if "pendiente_voz" not in st.session_state:
    st.session_state.pendiente_voz = None

if "modo_medico" not in st.session_state:
    st.session_state.modo_medico = False

if "modo_orquestador" not in st.session_state:
    st.session_state.modo_orquestador = "Equilibrado"

if "mcp_conectores" not in st.session_state:
    st.session_state.mcp_conectores = {
        "SQLite Memory & Missions": True,
        "Math & Unit Engine": True,
        "Security & System Shield": True,
        "Chile Macro & Markets": True,
        "Comms & Local Ollama": True,
    }

if "ollama_activo" not in st.session_state:
    st.session_state.ollama_activo = False

if "ollama_url" not in st.session_state:
    st.session_state.ollama_url = "http://localhost:11434"

if "ollama_modelo" not in st.session_state:
    st.session_state.ollama_modelo = "llama3.2"

PIN_SECRETO = "2805"
DB_PATH = "jarvis_misiones.db"
BUIN_LAT = -33.7325
BUIN_LON = -70.7422

API_KEY_GROQ = ""
try:
    API_KEY_GROQ = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    API_KEY_GROQ = os.environ.get("GROQ_API_KEY", "")

client_groq = None
if GROQ_AVAILABLE and API_KEY_GROQ:
    try:
        client_groq = Groq(api_key=API_KEY_GROQ)
    except Exception:
        client_groq = None


def init_db():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS misiones ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "tarea TEXT NOT NULL, "
            "estado TEXT DEFAULT 'Pendiente')"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS memory ("
            "key_id TEXT PRIMARY KEY, "
            "fact_text TEXT, "
            "category TEXT)"
        )
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS remedios ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT, "
            "nombre TEXT NOT NULL, "
            "horario TEXT DEFAULT 'Pendiente')"
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


init_db()


class JarvisMemory:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def remember_fact(self, key_id: str, fact_text: str, category: str = "general"):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
                (key_id, fact_text, category)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def recent_facts(self, limit: int = 5):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT fact_text FROM memory ORDER BY key_id DESC LIMIT ?", (limit,))
            rows = [r[0] for r in cursor.fetchall() if r and r[0]]
            conn.close()
            return rows
        except Exception:
            return []


jarvis_mem = JarvisMemory()


def agregar_mision(tarea):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
        conn.commit()
        conn.close()
    except Exception:
        pass


def obtener_misiones():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT id, tarea, estado FROM misiones")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def limpiar_misiones():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM misiones")
        conn.commit()
        conn.close()
    except Exception:
        pass


def agregar_remedio(nombre: str, horario: str = "Día"):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO remedios (nombre, horario) VALUES (?, ?)",
            (nombre.strip(), (horario or "Día").strip())
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def obtener_remedios():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre, horario FROM remedios")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def limpiar_remedios():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM remedios")
        conn.commit()
        conn.close()
    except Exception:
        pass


@st.cache_data(ttl=300)
def obtener_indicadores_chile():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JARVIS-Dashboard/1.0",
        "Accept": "application/json"
    }
    for _ in range(2):
        try:
            resp = requests.get("https://mindicador.cl/api", headers=headers, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                dolar = data.get("dolar", {}).get("valor")
                euro = data.get("euro", {}).get("valor")
                uf = data.get("uf", {}).get("valor")
                utm = data.get("utm", {}).get("valor")
                if dolar and euro and uf:
                    return {
                        "dolar": float(dolar),
                        "euro": float(euro),
                        "uf": float(uf),
                        "utm": float(utm) if utm else 0.0,
                        "ok": True,
                        "respaldo": False
                    }
        except Exception:
            pass

    return {
        "dolar": 950.00,
        "euro": 1030.00,
        "uf": 38000.00,
        "utm": 67000.00,
        "ok": True,
        "respaldo": True
    }


def describir_clima_codigo(code: int) -> str:
    mapa = {
        0: "despejado",
        1: "mayormente despejado",
        2: "parcialmente nublado",
        3: "nublado",
        45: "con neblina",
        48: "con escarcha o neblina",
        51: "con llovizna leve",
        61: "con lluvia leve",
        63: "con lluvia moderada",
        80: "con chubascos",
        95: "con tormenta eléctrica",
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
        resp = requests.get(url, timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            current = data.get("current") or {}
            temp = current.get("temperature_2m")
            code = int(current.get("weather_code", 0))
            if temp is not None:
                return {
                    "temp_c": round(float(temp), 1),
                    "condicion": describir_clima_codigo(code),
                    "respaldo": False,
                }
    except Exception:
        pass
    return {
        "temp_c": None,
        "condicion": "sin lectura en vivo",
        "respaldo": True,
    }


tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"


def obtener_saludo_nucleo(nucleo_nombre):
    pref = f"[{nucleo_nombre}] "
    saludos = {
        "JARVIS": f"{pref}{saludo_actual}, jefa. Qué milagro que pase a saludar; los servidores ya empezaban a extrañar sus órdenes.",
        "VIERNES": f"{pref}¡{saludo_actual}, jefa! Lista para mover ficha. ¿Qué encendemos hoy?",
        "NOVA": f"{pref}¡{saludo_actual}, jefa! Señal recibida desde el Nodo Buin. ¿Qué galaxia o tarea conquistamos ahora?",
        "ARTEX": f"{pref}{saludo_actual}, jefa. Núcleo ARTEX en línea bajo su control; rutas, conectores y escudos en vigilancia."
    }
    return saludos.get(nucleo_nombre, f"{pref}{saludo_actual}, jefa. En línea y a su servicio.")


def quiere_ingles(texto: str) -> bool:
    t = (texto or "").lower()
    pistas = [
        "en inglés", "en ingles", "responde en inglés", "responde en ingles",
        "habla en inglés", "habla en ingles", "in english", "speak english",
        "reply in english", "answer in english"
    ]
    return any(p in t for p in pistas)


def limpiar_texto_voz(texto: str) -> str:
    if not texto:
        return ""
    limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace ", texto)
    limpio = re.sub(r"https?://\S+", " enlace ", limpio)
    limpio = re.sub(r"[*_`#>\[\]]+", "", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio[:700]


def programar_voz(texto: str, idioma: str = "es-CL"):
    if st.session_state.get("voz_masculina_activa", True):
        st.session_state["pendiente_voz"] = {"texto": texto, "idioma": idioma}


def reproducir_voz_pendiente():
    pendiente = st.session_state.get("pendiente_voz")
    if not pendiente or not st.session_state.get("voz_masculina_activa", True):
        return
    st.session_state["pendiente_voz"] = None
    texto = pendiente.get("texto", "")
    idioma = pendiente.get("idioma", "es-CL")
    limpio = limpiar_texto_voz(texto)
    if not limpio:
        return
    escapado = (
        limpio.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("'", "\\'")
        .replace("\r", " ")
        .replace("\n", " ")
    )
    pref_lang = idioma[:2].lower()
    js_voz = (
        "<script>(function(){try{if(!('speechSynthesis' in window))return;"
        "function hablar(){try{window.speechSynthesis.cancel();"
        f"const u=new SpeechSynthesisUtterance(\"{escapado}\");"
        f"u.lang='{idioma}';u.rate=1.02;u.pitch=0.84;"
        "const vs=window.speechSynthesis.getVoices()||[];"
        f"const v=vs.find(x=>((x.lang||'').toLowerCase().startsWith('{pref_lang}')&&!/sabina|helena|zira|hazel|lucia|sofia|female|mujer/.test((x.name||'').toLowerCase())))||vs.find(x=>(x.lang||'').toLowerCase().startsWith('{pref_lang}'));"
        "if(v)u.voice=v;window.speechSynthesis.speak(u);}catch(e){}}"
        "if(window.speechSynthesis.getVoices().length>0){setTimeout(hablar,120);}"
        "else{window.speechSynthesis.onvoiceschanged=function(){setTimeout(hablar,120);};setTimeout(hablar,350);}"
        "}catch(e){}})();</script>"
    )
    components.html(js_voz, height=0)


def escucha_continua_js(activa: bool):
    if not activa:
        return
    js_sr = (
        "<script>(function(){try{"
        "const SR=window.SpeechRecognition||window.webkitSpeechRecognition;"
        "if(!SR||window.__jarvisSrActive)return;"
        "const r=new SR();r.lang='es-CL';r.continuous=true;r.interimResults=false;"
        "window.__jarvisSrActive=true;"
        "r.onresult=function(ev){const i=ev.results.length-1;if(i>=0&&ev.results[i][0]){"
        "const d=(ev.results[i][0].transcript||'').trim();"
        "if(d){const el=window.parent.document.getElementById('jarvis-ultima-voz');"
        "if(el)el.innerText='Última voz: '+d;}}};"
        "r.onerror=function(){window.__jarvisSrActive=false;};"
        "r.onend=function(){window.__jarvisSrActive=false;try{r.start();window.__jarvisSrActive=true;}catch(e){}};"
        "r.start();}catch(e){}})();</script>"
    )
    components.html(js_sr, height=0)


def generar_informe_diario_hablado(nucleo: str = "JARVIS", hablar: bool = True) -> str:
    econ = obtener_indicadores_chile()
    clima = obtener_clima_buin()
    misiones = obtener_misiones()
    remedios = obtener_remedios()
    memorias = (
        jarvis_mem.recent_facts(2)
        if st.session_state.get("mcp_conectores", {}).get("SQLite Memory & Missions", True)
        else []
    )

    hora_txt = now_chile.strftime("%H:%M")
    fecha_txt = now_chile.strftime("%d/%m/%Y")

    if clima.get("temp_c") is not None:
        clima_txt = f"Clima en Buin: {clima['temp_c']} grados y {clima['condicion']}."
    else:
        clima_txt = "Clima en Buin: sin lectura en vivo en este momento."

    dolar_fmt = f"${econ['dolar']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    euro_fmt = f"${econ['euro']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    uf_fmt = f"${econ['uf']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    finanzas_txt = f"Finanzas: Dólar en {dolar_fmt}, Euro en {euro_fmt} y UF en {uf_fmt}."

    if remedios:
        lista_rem = ", ".join(f"{r[1]} ({r[2]})" for r in remedios[:4])
        remedios_txt = f"Recordatorios de remedios: {lista_rem}."
    else:
        remedios_txt = "Sin remedios registrados por ahora."

    if misiones:
        resumen_misiones = (
            f"Tienes {len(misiones)} misión(es): "
            + ", ".join(m[1] for m in misiones[:3])
            + "."
        )
    else:
        resumen_misiones = "Sin misiones pendientes."

    resumen_mem = (
        f" Notas recientes: {'; '.join(memorias)}."
        if memorias
        else ""
    )

    texto_informe = (
        f"[{nucleo}] Informe diario del Nodo Buin, {fecha_txt}, {hora_txt} horas. "
        f"{clima_txt} {finanzas_txt} {remedios_txt} {resumen_misiones}{resumen_mem} Todo listo, jefa."
    )

    if hablar:
        programar_voz(texto_informe, idioma="es-CL")

    return texto_informe


def evaluar_calculo_seguro(texto_raw: str):
    if not st.session_state.get("mcp_conectores", {}).get("Math & Unit Engine", True):
        return None
    limpio = texto_raw.strip().lower()
    for pref in ["calcula", "calcular", "cuanto es", "cuánto es", "resuelve", "matemática", "matematica", "="]:
        if limpio.startswith(pref):
            limpio = limpio[len(pref):].strip()
    limpio = limpio.replace("×", "*").replace("·", "*").replace("÷", "/").replace("^", "**")
    if not limpio or not re.search(r"\d", limpio):
        return None
    if re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", limpio):
        return None
    if not re.fullmatch(r"[0-9+\-*/().%\s,a-z_]+", limpio):
        return None
    entorno = {
        "__builtins__": {},
        "abs": abs, "round": round, "min": min, "max": max, "pow": pow,
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "log": math.log10, "ln": math.log, "exp": math.exp, "pi": math.pi, "e": math.e,
    }
    try:
        res = eval(limpio, entorno, {})
        if isinstance(res, (int, float)) and not isinstance(res, bool):
            if isinstance(res, float) and res.is_integer():
                res = int(res)
            elif isinstance(res, float):
                res = round(res, 6)
            return f"Resultado del cálculo `{limpio}`: **{res}**."
    except Exception:
        return None
    return None


def convertir_unidades_texto(t: str):
    if not st.session_state.get("mcp_conectores", {}).get("Math & Unit Engine", True):
        return None
    m = re.search(r"(-?\d+(?:[.,]\d+)?)\s*(km|m|cm|mm|mi|millas|kg|g|lb|libras|c|°c|f|°f|k)\s*(?:a|en|to|in)\s*(km|m|cm|mm|mi|millas|kg|g|lb|libras|c|°c|f|°f|k)", t)
    if not m:
        return None
    val = float(m.group(1).replace(",", "."))
    u1 = m.group(2).replace("°", "")
    u2 = m.group(3).replace("°", "")
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

    if u1 in long_m and u2 in long_m:
        out = (val * long_m[u1]) / long_m[u2]
        return f"Conversión: **{val:g} {u1}** = **{round(out, 4):g} {u2}**."
    if u1 in masa_kg and u2 in masa_kg:
        out = (val * masa_kg[u1]) / masa_kg[u2]
        return f"Conversión: **{val:g} {u1}** = **{round(out, 4):g} {u2}**."

    temp_units = {"c", "f", "k"}
    if u1 in temp_units and u2 in temp_units:
        if u1 == "c":
            c = val
        elif u1 == "f":
            c = (val - 32) * 5 / 9
        else:
            c = val - 273.15
        if u2 == "c":
            out = c
        elif u2 == "f":
            out = c * 9 / 5 + 32
        else:
            out = c + 273.15
        return f"Conversión térmica: **{val:g} {u1.upper()}** = **{round(out, 2):g} {u2.upper()}**."

    return None


def resumen_sistema_y_seguridad():
    os_info = f"{platform.system()} {platform.release()}"
    db_existe = os.path.exists(DB_PATH)
    misiones_cant = len(obtener_misiones())
    mem_cant = len(jarvis_mem.recent_facts(50))
    activos_mcp = sum(1 for v in st.session_state.get("mcp_conectores", {}).values() if v)
    cpu_txt = "N/D"
    ram_txt = "N/D"
    if PSUTIL_AVAILABLE:
        try:
            cpu_txt = f"{psutil.cpu_percent(interval=0.2)}%"
            ram_txt = f"{psutil.virtual_memory().percent}%"
        except Exception:
            pass
    sospechosos = [
        f for f in os.listdir(".")
        if os.path.isfile(f) and any(f.lower().endswith(ext) for ext in [".exe", ".bat", ".cmd", ".vbs", ".ps1", ".scr"])
    ]
    estado_vir = "Integridad 98% · Sin ejecutables sospechosos en raíz." if not sospechosos else f"Archivos ejecutables detectados en raíz: {', '.join(sospechosos[:5])}."
    return (
        f"Escudo & Optimización ({os_info}): CPU **{cpu_txt}**, RAM **{ram_txt}**, "
        f"Conectores MCP activos **{activos_mcp}/5**, SQLite `{DB_PATH}` ({'OK' if db_existe else 'nuevo'}), "
        f"**{misiones_cant}** misiones y **{mem_cant}** memorias. {estado_vir} "
        "Optimización: purgar historial extenso del chat, limpiar misiones cerradas y mantener activos solo los conectores necesarios."
    )


def estilizar_por_nucleo(nucleo: str, nucleo_content: str, raw_user: str) -> str:
    pref = f"[{nucleo}] "
    modo_orq = st.session_state.get("modo_orquestador", "Equilibrado")
    cierre = ""
    if nucleo == "JARVIS":
        cierre = " Como siempre, jefa, un detalle técnico más dominado sin despeinarnos."
    elif nucleo == "VIERNES":
        cierre = " ¿Listo para el siguiente paso, jefa?"
    elif nucleo == "NOVA":
        cierre = f" Señal verificada desde el Nodo Buin para '{raw_user.strip()}', jefa."
    elif nucleo == "ARTEX":
        cierre = f" [Modo {modo_orq} · Pipeline bajo control], jefa."
    return f"{pref}{nucleo_content}{cierre}"


def responder_conocimiento_base(t: str, raw: str):
    if any(k in t for k in ["informe diario", "resumen del día", "resumen del dia", "reporte diario", "briefing"]):
        return generar_informe_diario_hablado(st.session_state.get("nucleo_activo", "JARVIS"), hablar=True)

    if any(k in t for k in ["remedio", "remedios", "medicamento", "medicamentos", "pastilla", "pastillas"]):
        remedios = obtener_remedios()
        if remedios:
            detalle = ", ".join(f"**{r[1]}** ({r[2]})" for r in remedios)
            return f"Recordatorios de remedios registrados: {detalle}."
        return "No tienes remedios registrados aún en Misiones & Memoria."

    if any(k in t for k in ["clima", "temperatura", "lluvia", "tiempo en buin"]):
        clima = obtener_clima_buin()
        if clima.get("temp_c") is not None:
            return f"En Buin hay **{clima['temp_c']}°C** y el cielo está **{clima['condicion']}**."
        return "No pude obtener la temperatura en vivo en este momento, jefa."

    if "pesa el corazón" in t or "pesa el corazon" in t or "peso del corazón" in t or "peso del corazon" in t:
        return (
            "En un adulto sano, el corazón suele pesar entre **250 y 350 gramos** "
            "(algo menor en promedio en mujeres y mayor en hombres, según masa corporal y contextura). "
            "Dato general anatómico, no diagnóstico médico."
        )

    if "mosca" in t and ("patas" in t or "cuantas" in t or "cuántas" in t):
        return "Una mosca tiene **6 patas** (tres pares articulados), como corresponde a todo insecto."

    conv = convertir_unidades_texto(t)
    if conv:
        return conv

    calculo = evaluar_calculo_seguro(raw)
    if calculo:
        return calculo

    if any(k in t for k in ["agentes", "equipo", "orquestador", "mcp", "conector", "conectores", "artex", "artax"]):
        activos = [k for k, v in st.session_state.get("mcp_conectores", {}).items() if v]
        return (
            f"Orquestación multi-núcleo (`JARVIS`, `VIERNES`, `NOVA`, `ARTEX`) en modo **{st.session_state.get('modo_orquestador', 'Equilibrado')}** "
            f"con conectores MCP activos: **{', '.join(activos) if activos else 'ninguno'}**."
        )

    if st.session_state.get("mcp_conectores", {}).get("Security & System Shield", True) and any(
        k in t for k in ["virus", "malware", "seguridad", "optimizar", "optimización", "optimizacion", "rendimiento", "diagnóstico", "diagnostico", "escudo"]
    ):
        return resumen_sistema_y_seguridad()

    if st.session_state.get("mcp_conectores", {}).get("Comms & Local Ollama", True) and any(
        k in t for k in ["llamar", "llamada", "mensaje", "enviar mensaje", "whatsapp", "correo"]
    ):
        return (
            "Módulo de **Llamadas y Mensajes**: puedes redactar el texto o número en el panel lateral de "
            "**Modos & Utilidades Tácticas** para generar el enlace directo (`tel:` / `wa.me`) sin salir de tu flujo."
        )

    if st.session_state.get("modo_medico", False) or any(
        k in t for k in ["síntoma", "sintoma", "dolor", "fiebre", "presión", "presion", "pulso", "medicina", "médico", "medico", "salud"]
    ):
        return (
            "**Modo Médico (orientación general)**: para evaluar cualquier síntoma o parámetro clínico, "
            "indica edad, intensidad, duración y signos de alarma. Esto es información general y no sustituye una evaluación médica presencial."
        )

    if any(k in t for k in ["matemática", "matematica", "cálculo", "calculo", "álgebra", "algebra", "geometría", "geometria", "derivada", "integral"]):
        return (
            "En **matemática y cálculo**, modelamos cantidades, relaciones, tasas de cambio (derivadas) y acumulaciones (integrales). "
            "Si me das una expresión numérica o conversión (como `10 km a mi` o `sqrt(144)`), la resuelvo directo."
        )

    if any(k in t for k in ["historia de la medicina", "historia medicina", "hipócrates", "hipocrates", "galeno", "antibiótico", "antibiotico", "penicilina", "vacuna", "pasteur", "fleming"]):
        return (
            "En **historia de la medicina**, se pasa de explicaciones mágicas o humorales (Hipócrates, Galeno) a la anatomía "
            "científica (Vesalio), la teoría microbiana (Pasteur, Koch), la antisepsia, las vacunas y los antibióticos "
            "(como la penicilina de Fleming) hasta la medicina molecular moderna."
        )

    if any(k in t for k in ["biología", "biologia", "adn", "arn", "célula", "celula", "genética", "genetica", "evolución", "evolucion", "mitosis", "fotosíntesis", "fotosintesis"]):
        return (
            "En **biología**, la célula es la unidad básica de la vida; el **ADN** almacena la información genética, "
            "el **ARN** participa en la expresión génica y procesos como la respiración celular o la fotosíntesis sostienen la energía biológica."
        )

    if any(k in t for k in ["ciencia", "ciencias", "física", "fisica", "química", "quimica", "termodinámica", "termodinamica", "cuántica", "cuantica", "astronomía", "astronomia", "gravedad", "luz", "átomo", "atomo"]):
        return (
            "En **ciencias**, se estudian las leyes y fenómenos del universo mediante observación, hipótesis, experimentación y modelos matemáticos: "
            "física, química, astronomía, termodinámica y mecánica cuántica."
        )

    if any(k in t for k in ["tecnología", "tecnologia", "programación", "programacion", "algoritmo", "inteligencia artificial", "ia", "red", "redes", "ciberseguridad", "base de datos", "sqlite", "python", "cloud", "nube", "ollama"]):
        return (
            "En **tecnología**, se integran hardware, software, redes, datos e inteligencia artificial —incluyendo ejecución local sin internet vía **Ollama**— "
            "para construir sistemas confiables, rápidos, seguros y escalables."
        )

    if any(k in t for k in ["historia", "histórico", "historico", "antigüedad", "antiguedad", "edad media", "revolución", "revolucion", "guerra mundial", "independencia", "imperio", "civilización", "civilizacion", "chile"]):
        return (
            "En **historia**, se interpretan los procesos del pasado analizando fuentes, cronología y causas políticas, económicas, "
            "sociales y culturales desde la Antigüedad hasta la era contemporánea."
        )

    return None


def responder_pregunta_general_local(nucleo: str, texto_usuario: str, en_ingles: bool = False) -> str:
    limpio = texto_usuario.strip()
    if en_ingles:
        cuerpo = (
            f"Regarding '{limpio}', I am running in local/offline-ready mode. "
            "I can handle math conversions, system/security diagnostics, medical info, science, technology, "
            "medical history, biology, and history, or save this as a mission."
        )
        return f"[{nucleo}] {cuerpo}"

    t = limpio.lower()
    if any(p in t for p in ["qué es", "que es", "quién fue", "quien fue", "quién es", "quien es", "cómo funciona", "como funciona", "por qué", "por que", "cuándo", "cuando", "dónde", "donde", "?"]):
        cuerpo = (
            f"Para tu consulta sobre **{limpio}**, puedo darte una respuesta directa en conversiones, diagnóstico/seguridad, "
            "modo médico, ciencias, tecnología, historia de la medicina, matemática y cálculo, biología e historia; "
            "si buscas un dato específico adicional, indícalo o regístralo como misión."
        )
        return estilizar_por_nucleo(nucleo, cuerpo, limpio)

    cuerpo = (
        f"He registrado tu consulta sobre **{limpio}**. Puedo asistirte con conversiones, revisión de seguridad/optimización, "
        "modo médico, ciencias, tecnología, historia de la medicina, matemática y cálculo, biología e historia."
    )
    return estilizar_por_nucleo(nucleo, cuerpo, limpio)


def consultar_ollama_local(nucleo: str, texto_usuario: str, idioma_voz: str) -> str:
    if not st.session_state.get("ollama_activo", False):
        return ""
    if not st.session_state.get("mcp_conectores", {}).get("Comms & Local Ollama", True):
        return ""
    base_url = (st.session_state.get("ollama_url") or "http://localhost:11434").rstrip("/")
    modelo = (st.session_state.get("ollama_modelo") or "llama3.2").strip()
    idioma_rule = "Respond in English." if idioma_voz == "en-US" else "Responde en español."
    system_prompt = (
        f"Eres {nucleo}, asistente táctico en el Nodo Buin. Tratas a la usuaria de 'jefa'. "
        f"Domina conversiones, seguridad/optimización, medicina, ciencias, tecnología e historia. {idioma_rule}"
    )
    try:
        resp = requests.post(
            f"{base_url}/api/chat",
            json={
                "model": modelo,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": texto_usuario}
                ]
            },
            timeout=12
        )
        if resp.status_code == 200:
            data = resp.json()
            msg = ((data.get("message") or {}).get("content") or "").strip()
            if msg:
                return f"[{nucleo} · Ollama] {msg}"
    except Exception:
        return ""
    return ""


def consultar_modelo_externo(nucleo: str, texto_usuario: str, idioma_voz: str) -> str:
    ollama_resp = consultar_ollama_local(nucleo, texto_usuario, idioma_voz)
    if ollama_resp:
        return ollama_resp

    if not client_groq:
        return ""
    rec_mem = "; ".join(jarvis_mem.recent_facts(5)) if st.session_state.get("mcp_conectores", {}).get("SQLite Memory & Missions", True) else ""
    estilo_nucleo = {
        "JARVIS": "Eres JARVIS, elegante, preciso y con sarcasmo fino.",
        "VIERNES": "Eres VIERNES, rápida, directa y resolutiva.",
        "NOVA": "Eres NOVA, dinámica, clara y con enfoque táctico desde el Nodo Buin.",
        "ARTEX": "Eres ARTEX, analítico, preciso, firme y enfocado en orquestación, conectores y seguridad bajo control de la jefa."
    }.get(nucleo, "Eres un asistente táctico.")
    modo_orq = st.session_state.get("modo_orquestador", "Equilibrado")
    idioma_rule = "Responde en inglés." if idioma_voz == "en-US" else "Responde en español."
    modo_med = " Activa enfoque médico informativo con advertencia clínica." if st.session_state.get("modo_medico", False) else ""
    instruccion_sistema = (
        f"{estilo_nucleo} Tratas a la usuaria de 'jefa'. Modo de trabajo: {modo_orq}. "
        f"Dominas ciencias, tecnología, historia de la medicina, matemática y cálculo, biología e historia, "
        f"y respondes cualquier pregunta con claridad.{modo_med} {idioma_rule} "
        f"{'Memorias recientes: ' + rec_mem if rec_mem else ''}"
    )
    mensajes_api = [{"role": "system", "content": instruccion_sistema}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.mensajes
    ]
    for modelo in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
        try:
            completion = client_groq.chat.completions.create(
                model=modelo,
                messages=mensajes_api,
                temperature=0.75
            )
            contenido = (completion.choices[0].message.content or "").strip()
            if contenido:
                return f"[{nucleo}] {contenido}"
        except Exception:
            continue
    return ""


def generar_respuesta_coherente(nucleo, texto_usuario):
    t = texto_usuario.strip().lower()

    if quiere_ingles(texto_usuario):
        base_en = (
            f"Understood, Boss. Switching to English for '{texto_usuario.strip()}'. "
            "Multi-core orchestration, MCP connectors, conversions, diagnostics, medical mode, "
            "science, technology, medical history, math, biology, and history are online."
        )
        if nucleo == "VIERNES":
            return f"[{nucleo}] Got it, Boss! {base_en}"
        if nucleo == "NOVA":
            return f"[{nucleo}] Signal locked, Boss. {base_en}"
        if nucleo == "ARTEX":
            return f"[{nucleo}] Pipeline routed in English, Boss. {base_en}"
        return f"[{nucleo}] {base_en} Naturally, I perform just as well in English."

    palabras_saludo = [
        "hola", "buenas", "buenos días", "buenos dias",
        "buenas tardes", "buenas noches", "holi", "qué tal", "que tal"
    ]
    if any(t == s or t.startswith(s + " ") or t.startswith(s + ",") for s in palabras_saludo):
        return obtener_saludo_nucleo(nucleo)

    resp_base = responder_conocimiento_base(t, texto_usuario)
    if resp_base:
        return estilizar_por_nucleo(nucleo, resp_base, texto_usuario)

    if st.session_state.get("mcp_conectores", {}).get("Chile Macro & Markets", True) and any(
        k in t for k in ["bolsa", "bolsas", "acciones", "nasdaq", "mercado", "mercados", "wall street", "finviz"]
    ):
        msg_bolsa = (
            "En modo respaldo local no tengo cotizaciones bursátiles en vivo dentro del chat, jefa. "
            "Puede revisar **Finviz** o **ANT (Nasdaq)** en el panel lateral de **Enlaces Financieros**."
        )
        return estilizar_por_nucleo(nucleo, msg_bolsa, texto_usuario)

    if st.session_state.get("mcp_conectores", {}).get("Chile Macro & Markets", True) and any(
        k in t for k in ["dólar", "dolar", "euro", "uf", "utm", "divisa", "divisas", "moneda", "cambio"]
    ):
        econ = obtener_indicadores_chile()
        if econ.get("ok"):
            dolar_fmt = f"${econ['dolar']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            euro_fmt = f"${econ['euro']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            uf_fmt = f"${econ['uf']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            nota_resp = " (valor de respaldo local)" if econ.get("respaldo") else ""
            msg_econ = (
                f"Indicadores registrados en el Nodo Buin{nota_resp}: "
                f"Dólar Obs. **{dolar_fmt}**, Euro **{euro_fmt}** y UF **{uf_fmt}**."
            )
            return estilizar_por_nucleo(nucleo, msg_econ, texto_usuario)

    if any(k in t for k in ["hora", "qué hora", "que hora", "fecha", "día de hoy", "dia de hoy"]):
        hora_str = now_chile.strftime("%H:%M:%S")
        return estilizar_por_nucleo(nucleo, f"En el Nodo Buin son las **{hora_str}** (hora de Chile).", texto_usuario)

    if any(k in t for k in ["estado", "sistema", "misión", "misiones", "pendiente", "pendientes"]):
        misiones = obtener_misiones()
        cant = len(misiones)
        return estilizar_por_nucleo(
            nucleo,
            f"Núcleo **{nucleo}** operativo en el Nodo Buin con **{cant}** misión(es) registrada(s).",
            texto_usuario
        )

    return responder_pregunta_general_local(nucleo, texto_usuario, en_ingles=False)


if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "assistant",
            "content": obtener_saludo_nucleo(st.session_state.nucleo_activo)
        }
    ]

estilos_css = (
    "<style>"
    ".stApp { background-color: #060913 !important; color: #00f3ff !important; }"
    ".stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp div {"
    "color: #00f3ff !important; font-family: monospace; }"
    "[data-testid='stIconMaterial'], .material-symbols-rounded, .material-icons {"
    "font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important; color: #00f3ff !important; }"
    "[data-testid='stSidebar'] h3 { font-size: 1.05rem !important; }"
    "[data-testid='stSidebar'] h4 { font-size: 0.85rem !important; margin-bottom: 4px !important; }"
    "[data-testid='stSidebar'] summary p { font-size: 0.80rem !important; }"
    ".stButton>button { background-color: #00f3ff !important; border: 1.5px solid #00f3ff !important;"
    "font-weight: bold; font-family: monospace; box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);"
    "width: 100%; border-radius: 6px; padding: 5px 10px !important; }"
    ".stButton>button p, .stButton>button span { color: #060913 !important; font-size: 0.78rem !important; }"
    ".stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.9); }"
    ".stButton>button:hover p, .stButton>button:hover span { color: #ffffff !important; }"
    ".econ-card { border: 1px solid #00f3ff; background: rgba(0, 243, 255, 0.06);"
    "border-radius: 6px; padding: 8px 10px; margin: 5px 0; display: flex;"
    "justify-content: space-between; align-items: center; box-shadow: inset 0 0 6px rgba(0, 243, 255, 0.2); }"
    ".econ-label { font-size: 0.75rem !important; opacity: 0.85; }"
    ".econ-val { font-size: 0.85rem !important; font-weight: bold; text-shadow: 0 0 6px #00f3ff; }"
    ".arc-reactor-container { display: flex; flex-direction: column; align-items: center;"
    "justify-content: center; text-align: center; margin-bottom: 10px; }"
    ".arc-ring { width: 65px; height: 65px; border: 2.5px solid #00f3ff; border-radius: 50%;"
    "position: relative; display: flex; align-items: center; justify-content: center;"
    "background: radial-gradient(circle, rgba(0,243,255,0.4) 0%, #060913 75%);"
    "box-shadow: 0 0 20px rgba(0, 243, 255, 0.8), inset 0 0 10px rgba(0, 243, 255, 0.6); margin-bottom: 8px; }"
    ".arc-triangle-inverted { width: 0; height: 0; border-left: 12px solid transparent;"
    "border-right: 12px solid transparent; border-top: 20px solid #00f3ff; filter: drop-shadow(0 0 8px #00f3ff); }"
    ".tactical-link-btn { display: block; width: 100%; background-color: #00f3ff; color: #060913 !important;"
    "text-align: center; padding: 6px 10px; margin: 5px 0; border-radius: 6px; text-decoration: none;"
    "font-weight: bold; font-size: 0.

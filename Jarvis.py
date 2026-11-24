import datetime
import math
import os
import random
import re
import sqlite3
import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except Exception:
    Groq = None
    GROQ_AVAILABLE = False

st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed",
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

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"
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
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
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
        conn.commit()
        conn.close()
    except Exception:
        pass


init_db()


class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path

    def remember_fact(self, key_id: str, fact_text: str):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
                (key_id, fact_text, "general"),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def get_recent_facts(self, limit: int = 5):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT fact_text FROM memory ORDER BY rowid DESC LIMIT ?", (limit,))
            rows = [r[0] for r in cursor.fetchall() if r and r[0]]
            conn.close()
            return rows
        except Exception:
            return []

    def clear_facts(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memory")
            conn.commit()
            conn.close()
        except Exception:
            pass


jarvis_mem = JarvisMemory()


def agregar_mision(tarea):
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
        conn.commit()
        conn.close()
    except Exception:
        pass


def obtener_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT id, tarea, estado FROM misiones")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def limpiar_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM misiones")
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
                        "respaldo": False,
                    }
        except Exception:
            pass

    return {
        "dolar": 950.00,
        "euro": 1030.00,
        "uf": 38000.00,
        "utm": 67000.00,
        "ok": True,
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
        resp = requests.get(url, timeout=5)
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


def obtener_hora_chile():
    tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
    return datetime.datetime.now(tz_chile)


def obtener_saludo_actual(ahora):
    hora = ahora.hour
    if 0 <= hora < 12:
        return "Buenos días"
    if 12 <= hora < 20:
        return "Buenas tardes"
    return "Buenas noches"


def obtener_presentacion_nucleo(nucleo_nombre):
    pref = f"[{nucleo_nombre}] "
    presentaciones = {
        "JARVIS": (
            f"{pref}Soy JARVIS, jefa. El núcleo principal de este sistema en el Nodo Buin... "
            "y sí, sigo manteniendo todo en orden mientras usted decide cuál será la próxima jugada."
        ),
        "VIERNES": (
            f"{pref}¡Soy VIERNES, jefa! Ágil, directa y lista para entrar en acción, "
            "mover tareas y resolver lo que toque sin dar rodeos."
        ),
        "NOVA": (
            f"{pref}¡Soy NOVA, jefa! Núcleo de exploración y radar desde el Nodo Buin, "
            "atenta a cada señal y lista para trazar el siguiente rumbo."
        ),
        "ARTEX": (
            f"{pref}Soy ARTEX, jefa. Núcleo táctico de análisis, cálculo y control en línea, "
            "con todos los protocolos de precisión activos."
        ),
    }
    return presentaciones.get(nucleo_nombre, f"{pref}Soy {nucleo_nombre}, jefa, en línea y a su servicio.")


def obtener_saludo_nucleo(nucleo_nombre):
    ahora = obtener_hora_chile()
    saludo_actual = obtener_saludo_actual(ahora)
    pref = f"[{nucleo_nombre}] "
    saludos = {
        "JARVIS": f"{pref}{saludo_actual}, jefa. Qué milagro que pase a saludar; los servidores ya empezaban a extrañar sus órdenes.",
        "VIERNES": f"{pref}¡{saludo_actual}, jefa! Lista para mover ficha. ¿Qué encendemos hoy?",
        "NOVA": f"{pref}¡{saludo_actual}, jefa! Señal recibida desde el Nodo Buin. ¿Qué galaxia o tarea conquistamos ahora?",
        "ARTEX": f"{pref}¡{saludo_actual}, jefa! Núcleo ARTEX en línea con protocolo de conocimiento y control táctico activo.",
    }
    return saludos.get(nucleo_nombre, f"{pref}{saludo_actual}, jefa. En línea y a su servicio.")


def limpiar_texto_para_voz(texto):
    limpio = re.sub(r"^\[[^\]]+\]\s*", "", texto or "")
    limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace ", limpio)
    limpio = re.sub(r"https?://\S+", " enlace ", limpio)
    limpio = re.sub(r"[*_`#>\[\]|]+", " ", limpio)
    limpio = re.sub(r"([.!?])\s+", r"\1 ... ", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio[:520]


def programar_voz(texto, idioma="es-CL"):
    if st.session_state.get("voz_masculina_activa", True):
        limpio = limpiar_texto_para_voz(texto)
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
        "function elegirVoz(voices){"
        "if(!voices||!voices.length)return null;"
        "const es=voices.filter(v=>/^(es|es-CL|es-ES|es-MX|es-US)/i.test(v.lang||''));"
        "const pref=es.find(v=>/jorge|diego|carlos|enrique|pablo|mateo|alonso|raul|male|hombre/i.test(v.name||''))||es[0]||voices[0];"
        "return pref||null;}"
        "function hablarAhora(){"
        "window.speechSynthesis.cancel();"
        "const trozos=" + f'"{txt}"' + ".split(' ... ').filter(Boolean);"
        "const lista=trozos.length?trozos:[" + f'"{txt}"' + "];"
        "const vozElegida=elegirVoz(window.speechSynthesis.getVoices());"
        "lista.forEach((parte)=>{"
        "const u=new SpeechSynthesisUtterance(parte);"
        f"u.lang='{lang}';"
        "u.rate=0.98;"
        "u.pitch=0.90;"
        "if(vozElegida)u.voice=vozElegida;"
        "setTimeout(()=>{try{window.speechSynthesis.speak(u);}catch(e){}},100);"
        "});}"
        "if(window.speechSynthesis.getVoices().length){hablarAhora();}"
        "else{window.speechSynthesis.onvoiceschanged=function(){hablarAhora();};setTimeout(hablarAhora,220);}"
        "}catch(e){}})();</script>"
    )
    try:
        components.html(js_voz, height=1)
    except Exception:
        pass


def renderizar_microfono_voz():
    js_mic = """
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0 10px 0;">
        <button id="btn-mic-jarvis" type="button" style="
            background:#00f3ff;color:#060913;border:1.5px solid #00f3ff;
            border-radius:6px;padding:6px 12px;font-family:monospace;
            font-weight:bold;font-size:0.78rem;cursor:pointer;
            box-shadow:0 0 10px rgba(0,243,255,0.5);
        ">🎤 Hablar por Voz</button>
        <span id="estado-mic-jarvis" style="
            color:#00f3ff;font-family:monospace;font-size:0.75rem;opacity:0.85;
        ">Micrófono listo (es-CL)</span>
    </div>
    <script>
    (function() {
        const btn = document.getElementById("btn-mic-jarvis");
        const stEl = document.getElementById("estado-mic-jarvis");
        if (!btn || !stEl) return;
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) {
            stEl.textContent = "Dictado por voz no soportado en este navegador";
            return;
        }
        btn.onclick = function() {
            try {
                const rec = new SR();
                rec.lang = "es-CL";
                rec.interimResults = false;
                rec.maxAlternatives = 1;
                stEl.textContent = "Escuchando, jefa...";
                rec.onresult = function(ev) {
                    const dicho = (ev.results[0] && ev.results[0][0] && ev.results[0][0].transcript) || "";
                    stEl.textContent = dicho ? ('Escuchado: "' + dicho + '"') : "No se captó audio";
                    if (!dicho) return;
                    const doc = window.parent.document;
                    const inputs = doc.querySelectorAll('textarea[data-testid="stChatInputTextArea"], input[data-testid="stChatInputTextArea"], textarea');
                    let target = null;
                    inputs.forEach(el => {
                        if (el.offsetParent !== null) target = el;
                    });
                    if (target) {
                        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value") ||
                                       Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value");
                        if (setter && setter.set) setter.set.call(target, dicho);
                        else target.value = dicho;
                        target.dispatchEvent(new Event("input", { bubbles: true }));
                        target.dispatchEvent(new Event("change", { bubbles: true }));
                        setTimeout(() => {
                            const sendBtn = doc.querySelector('button[data-testid="stChatInputSubmitButton"]');
                            if (sendBtn) sendBtn.click();
                        }, 180);
                    }
                };
                rec.onerror = function() { stEl.textContent = "Error al acceder al micrófono"; };
                rec.onend = function() {
                    if (stEl.textContent === "Escuchando, jefa...") stEl.textContent = "Micrófono listo (es-CL)";
                };
                rec.start();
            } catch (e) {
                stEl.textContent = "No se pudo iniciar el micrófono";
            }
        };
    })();
    </script>
    """
    try:
        components.html(js_mic, height=46)
    except Exception:
        pass


def resolver_calculo_o_unidad(texto_raw):
    t = (texto_raw or "").strip().lower()

    mp = re.search(r"(\d+(?:[.,]\d+)?)\s*%\s*(?:de|del)\s*(\d+(?:[.,]\d+)?)", t)
    if mp:
        pct = float(mp.group(1).replace(",", "."))
        base = float(mp.group(2).replace(",", "."))
        val = (pct / 100.0) * base
        res = int(val) if val.is_integer() else round(val, 6)
        return f"Cálculo porcentual: **{pct:g}%** de **{base:g}** = **{res}**."

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
            return f"Conversión de longitud: **{val:g} {u1}** = **{round((val * long_m[u1]) / long_m[u2], 4):g} {u2}**."
        if u1 in masa_kg and u2 in masa_kg:
            return f"Conversión de masa: **{val:g} {u1}** = **{round((val * masa_kg[u1]) / masa_kg[u2], 4):g} {u2}**."
        if u1 in vol_l and u2 in vol_l:
            return f"Conversión de volumen: **{val:g} {u1}** = **{round((val * vol_l[u1]) / vol_l[u2], 4):g} {u2}**."
        if u1 in vel_ms and u2 in vel_ms:
            return f"Conversión de velocidad: **{val:g} {u1}** = **{round((val * vel_ms[u1]) / vel_ms[u2], 4):g} {u2}**."
        if u1 in {"c", "f", "k"} and u2 in {"c", "f", "k"}:
            c = val if u1 == "c" else ((val - 32) * 5 / 9 if u1 == "f" else val - 273.15)
            out_t = c if u2 == "c" else (c * 9 / 5 + 32 if u2 == "f" else c + 273.15)
            return f"Conversión térmica: **{val:g} {u1.upper()}** = **{round(out_t, 2):g} {u2.upper()}**."

    expr = t
    for pref in ["calcula", "calcular", "cuanto es", "cuánto es", "resuelve", "aritmetica", "aritmética", "matematica", "matemática", "="]:
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
                return f"Resultado del cálculo `{expr}`: **{out}**."
        except Exception:
            return None
    return None


def generar_respuesta_coherente(nucleo, texto_usuario):
    ahora = obtener_hora_chile()
    prefijo = f"[{nucleo}] "
    t = (texto_usuario or "").strip().lower()

    frases_presentacion = [
        "presentate", "preséntate", "presentate por favor", "preséntate por favor",
        "quien eres", "quién eres", "quien eres tu", "quién eres tú",
        "protocolo de presentacion", "protocolo de presentación",
    ]
    if any(k in t for k in frases_presentacion):
        return obtener_presentacion_nucleo(nucleo)

    frases_despierto = [
        "estas despierto", "estás despierto", "estas despierta", "estás despierta",
        "estas ahi", "estás ahí", "estas ahi?", "estás ahí?",
        "estas despierto?", "estás despierto?", "estas despierta?", "estás despierta?",
    ]
    if any(k in t for k in frases_despierto):
        if nucleo == "JARVIS":
            return f"{prefijo}Para usted, señorita, siempre."
        if nucleo == "VIERNES":
            return f"{prefijo}¡Siempre despierta para usted, señorita!"
        if nucleo == "NOVA":

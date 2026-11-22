import datetime
import math
import os
import platform
import random
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
    return limpio[:450]


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
        .replace("\n", " ")
    )
    js_voz = (
        "<script>(function(){try{if(!('speechSynthesis' in window))return;"
        "function hablar(){try{window.speechSynthesis.cancel();"
        f"const u=new SpeechSynthesisUtterance('{escapado}');"
        f"u.lang='{idioma}';u.rate=1.02;u.pitch=0.84;"
        "const vs=window.speechSynthesis.getVoices()||[];"
        f"const prefLang='{idioma}'.slice(0,2);"
        "const v=vs.find(x=>((x.lang||'').toLowerCase().startsWith(prefLang)&&!/sabina|helena|zira|hazel|lucia|lucía|sofia|sofía|female|mujer/.test((x.name||'').toLowerCase())))||vs.find(x=>(x.lang||'').toLowerCase().startsWith(prefLang));"
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
    if "pesa el corazón" in t or "pesa el corazon" in t or "peso del corazón" in t or "peso del corazon" in t:
        return (
            "En un adulto sano, el corazón suele pesar entre **250 y 350 gramos** "
            "(algo menor en promedio en mujeres y mayor en hombres, según masa corporal y contextura). "
            "Dato general anatómico, no diagnóstico médico."
        )

    if "mosca" in t and ("patas" in t or "cuantas" in t or "cuántas" in t):
        return "Una mosca tiene **6 patas** (tres pares articulados),

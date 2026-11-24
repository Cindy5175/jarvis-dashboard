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


def agregar_remedio(nombre: str, horario: str = "Dia"):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO remedios (nombre, horario) VALUES (?, ?)",
            (nombre.strip(), (horario or "Dia").strip())
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
            resp = requests.get("https://mindicador.cl/api", headers=headers, timeout=4)
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
    saludo_actual = "Buenos dias"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"


def obtener_saludo_nucleo(nucleo_nombre):
    pref = f"[{nucleo_nombre}] "
    saludos = {
        "JARVIS": f"{pref}{saludo_actual}, jefa. Que milagro que pase a saludar; los servidores ya empezaban a extranar sus ordenes.",
        "VIERNES": f"{pref}{saludo_actual}, jefa. Lista para mover ficha. Que encendemos hoy?",
        "NOVA": f"{pref}{saludo_actual}, jefa. Senal recibida desde el Nodo Buin. Que tarea conquistamos ahora?",
        "ARTEX": f"{pref}{saludo_actual}, jefa. Nucleo ARTEX en linea bajo su control; rutas, conectores y escudos en vigilancia."
    }
    return saludos.get(nucleo_nombre, f"{pref}{saludo_actual}, jefa. En linea y a su servicio.")


def quiere_ingles(texto: str) -> bool:
    t = (texto or "").lower()
    pistas = [
        "en ingles", "responde en ingles", "habla en ingles",
        "in english", "speak english", "reply in english", "answer in english"
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
    try:
        components.html(js_voz, height=0)
    except Exception:
        pass


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
        "if(el)el.innerText='Ultima voz: '+d;}}};"
        "r.onerror=function(){window.__jarvisSrActive=false;};"
        "r.onend=function(){window.__jarvisSrActive=false;try{r.start();window.__jarvisSrActive=true;}catch(e){}};"
        "r.start();}catch(e){}})();</script>"
    )
    try:
        components.html(js_sr, height=0)
    except Exception:
        pass


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
    finanzas_txt = f"Finanzas: Dolar en {dolar_fmt}, Euro en {euro_fmt} y UF en {uf_fmt}."

    if remedios:
        lista_rem = ", ".join(f"{r[1]} ({r[2]})" for r in remedios[:4])
        remedios_txt = f"Recordatorios de remedios: {lista_rem}."
    else:
        remedios_txt = "Sin remedios registrados por ahora."

    if misiones:
        resumen_misiones = (
            f"Tienes {len(misiones)} mision(es): "
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

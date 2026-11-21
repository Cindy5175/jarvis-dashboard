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
except ImportError:
    GROQ_AVAILABLE = False

st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

if "voz_masculina_activa" not in st.session_state:
    st.session_state.voz_masculina_activa = True

if "escucha_continua_activa" not in st.session_state:
    st.session_state.escucha_continua_activa = True

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
        "NOVA": f"{pref}¡{saludo_actual}, jefa! Señal recibida desde el Nodo Buin. ¿Qué galaxia o tarea conquistamos ahora?"
    }
    return saludos.get(nucleo_nombre, f"{pref}{saludo_actual}, jefa. En línea y a su servicio.")


def limpiar_texto_voz(texto: str) -> str:
    if not texto:
        return ""
    limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace ", texto)
    limpio = re.sub(r"https?://\S+", " enlace ", limpio)
    limpio = re.sub(r"\$[^$]+\$", " fórmula ", limpio)
    limpio = re.sub(r"[*_`#>\[\]]+", "", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio[:450]


def hablar_voz_masculina(texto: str, activa: bool = True):
    if not activa:
        return
    limpio = limpiar_texto_voz(texto)
    if not limpio:
        return
    escapado = (
        limpio.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("'", "\\'")
        .replace("\n", " ")
    )
    js_voz = f"""
    <script>
      (function() {{
        try {{
          if ("speechSynthesis" in window) {{
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance("{escapado}");
            utter.lang = "es-CL";
            utter.rate = 1.02;
            utter.pitch = 0.84;
            const voices = window.speechSynthesis.getVoices() || [];
            const maleEs = voices.find(v => {{
              const n = (v.

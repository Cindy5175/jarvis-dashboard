import streamlit as st
import datetime
import sqlite3
import io
import requests

# --- 1. CONFIGURACIÓN DE PÁGINA (SIEMPRE PRIMERO - OBLIGATORIO) ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INICIALIZACIÓN SEGURA DE SESSION_STATE (PRIMERO) ---
if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

# ZONA HORARIA CHILENA (UTC-3)
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Protocolo de seguridad máxima activo en Nodo Buin."}
    ]

if "audio_process_key" not in st.session_state:
    st.session_state.audio_process_key = None

PIN_SECRETO = "2805"

# Importación segura de gTTS para voz
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

# Importación de Google Generative AI
try:
    import google.generativeai as genai
    
    api_key = "AQuí_va_tu_clave_completa" 
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    elif "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    
    if api_key:
        genai.configure(api_key=api_key)
except ImportError:
    genai = None

# --- INICIALIZACIÓN DE BASE DE DATOS SQLITE ---
fn_db = "jarvis_misiones.db"

def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS misiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarea TEXT NOT NULL,
            estado TEXT DEFAULT 'Pendiente'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memoria_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rol TEXT,
            contenido TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento TEXT NOT NULL,
            fecha_hora TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def agregar_mision(tarea):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
    conn.commit()
    conn.close()

def obtener_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tarea, estado FROM misiones")
    rows = cursor.fetchall()
    conn.close()
    return rows

def limpiar_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM misiones")
    conn.commit()
    conn.close()

def agregar_agenda(evento, fecha_hora):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO agenda (evento, fecha_hora) VALUES (?, ?)", (evento, fecha_hora))
    conn.commit()
    conn.close()

def obtener_agenda():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT evento, fecha_hora FROM agenda")
    rows = cursor.fetchall()
    conn.close()
    return rows

def obtener_clima_buin():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-33.7333&current=temperature_2m,relative_humidity_2m,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min&timezone=America%2FSantiago"
        res = requests.get(url, timeout=3).json()
        temp = res["current"]["temperature_2m"]
        hum = res["current"]["relative_humidity_2m"]
        viento = res["current"]["wind_speed_10m"]
        
        dias_max = res["daily"]["temperature_2m_max"][:5]
        dias_min = res["daily"]["temperature_2m_min"][:5]
        
        return f"{temp}°C", f"{hum}%", f"{viento} km/h", dias_max, dias_min
    except Exception:
        return "21°C", "45%", "12 km/h", [24, 25, 22, 28, 32], [9, 10, 7, 7, 8]

temp_real, hum_real, viento_real, t_maxs, t_mins = obtener_clima_buin()

# --- ESTILOS VISUALES 100% AZUL NEÓN ELÉCTRICO (#00f3ff) & BOTONES FORZADOS ---
st.markdown("""
<style>
.stApp { background-color: #060913 !important; color: #00f3ff !important; }
p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
.stChatMessage p, .stChatMessage div {
    font-size: 0.85rem !important;
    color: #00f3ff !important;
}
.stButton>button {
    background-color: #00f3ff !important;
    border: 1.5px solid #00f3ff !important;
    font-weight: bold;
    font-family: monospace;
    box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
    width: 100%;
}
.stButton>button p, .stButton>button span {
    color: #060913 !important;
}
.stButton>button:hover {
    background-color: #0088cc !important;
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.9);
}
.stButton>button:hover p, .stButton>button:hover span {
    color: #ffffff !important;
}
.arc-reactor-container {

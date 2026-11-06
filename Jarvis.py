import streamlit as st
import datetime
import sqlite3
import io

# Importación segura de gTTS para voz y autorefresh
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# Importación de Google Generative AI
try:
    import google.generativeai as genai
    
    # Tu clave de API activa
    api_key = "AQuí_va_tu_clave_completa" 
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    elif "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    
    if api_key:
        genai.configure(api_key=api_key)
except ImportError:
    genai = None

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Reloj con segundero en vivo estable (cada 1 segundo)
if st_autorefresh:
    st_autorefresh(interval=1000, key="datetimereload")

# --- INICIALIZACIÓN DE BASE DE DATOS SQLITE PARA MISIONES ---
def init_db():
    conn = sqlite3.connect("jarvis_misiones.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS misiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarea TEXT NOT NULL,
            estado TEXT DEFAULT 'Pendiente'
        )
    """)
    conn.commit()
    conn.close()

init_db()

def agregar_mision(tarea):
    conn = sqlite3.connect("jarvis_misiones.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
    conn.commit()
    conn.close()

def obtener_misiones():
    conn = sqlite3.connect("jarvis_misiones.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tarea, estado FROM misiones")
    rows = cursor.fetchall()
    conn.close()
    return rows

def limpiar_misiones():
    conn = sqlite3.connect("jarvis_misiones.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM misiones")
    conn.commit()
    conn.close()

# --- ESTILOS VISUALES 100% AZUL NEÓN (#00ffcc) ---
st.markdown("""
    <style>
        .stApp { background-color: #0b0f19 !important; color: #00ffcc !important; }
        
        .arc-reactor-container h4 { color: #00ffcc !important; font-size: 1.1rem !important; font-family: monospace; }
        
        p, span, label, h1, h2, h3, h4, div { color: #00ffcc !important; font-family: monospace; }
        
        .stChatMessage p, .stChatMessage div {
            font-size: 0.85rem !important;
            color: #00ffcc !important;
        }

        /* Botones en Azul Neón absoluto */
        .stButton>button {
            color: #0b0f19 !important;
            background-color: #00ffcc !important;
            border: 1.5px solid #00ffcc !important;
            font-weight: bold;
            font-family: monospace;
            box-shadow: 0 0 8px rgba(0, 255, 204, 0.5);
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #00b388 !important;
            color: #ffffff !important;
            box-shadow: 0 0 12px rgba(0, 255, 204, 0.8);
        }
        
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 10px;
        }
        .arc-ring {
            width: 45px;
            height: 45px;
            border: 

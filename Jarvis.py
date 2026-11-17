import streamlit as st
import datetime
import sqlite3
import requests
import os
import sys

# Importaciones de las IA
from zhipuai import ZhipuAI
import google.generativeai as genai

# --- 1. CONFIGURACION DE PAGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INICIALIZACION DE SESSION_STATE ---
if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"

# --- CONFIGURACIÓN DE LLAVES Y CLIENTES PARA LOS 3 MOTORES ---
API_KEY_GLM = "8477d61a32664b00aac4d04904c0fe09.4rcBmMQdqChiktB1"
API_KEY_GEMINI = "TU_API_KEY_DE_GEMINI"  # Inserta tu clave de Gemini si la usas
API_KEY_ZAPIA = "TU_API_KEY_DE_ZAPIA"    # Inserta tu clave de ZapIA si la usas

# Inicialización de clientes
client_glm = ZhipuAI(api_key=API_KEY_GLM) if API_KEY_GLM else None

if API_KEY_GEMINI and API_KEY_GEMINI != "TU_API_KEY_DE_GEMINI":
    genai.configure(api_key=API_KEY_GEMINI)

# --- BASE DE DATOS SQLITE ---
def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
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

init_db()

class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path
    def remember_fact(self, key_id: str, fact_text: str):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
            (key_id, fact_text, "general")
        )
        conn.commit()
        conn.close()

jarvis_mem = JarvisMemory()

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

# --- OBTENCIÓN DE INDICADORES ECONÓMICOS EN TIEMPO REAL (CHILE) ---
@st.cache_data(ttl=300)
def obtener_indicadores_chile():
    try:
        resp = requests.get("https://mindicador.cl/api", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "dolar": data.get("dolar", {}).get("valor"),
                "euro": data.get("euro", {}).get("valor"),
                "uf": data.get("uf", {}).get("valor"),
                "utm": data.get("utm", {}).get("valor"),
                "ok": True
            }
    except Exception:
        pass
    return {"ok": False}

# ZONA HORARIA CHILENA
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
        {
            "role": "assistant",
            "content": (
                f"{saludo_actual}, jefa. Nodo Buin en línea, enlazado en paralelo a "
                "GLM, Google Gemini y ZapIA. ¿Qué dominamos hoy?"
            )
        }
    ]

# --- ESTILOS VISUALES: REACTOR ARC ESTILO STARK & BOTONES COMPACTOS ---
estilos_css = """
<style>
    .stApp { background-color: #060913 !important; color: #00f3ff !important; font-family: monospace; }
    p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
    
    /* AJUSTE FINO DE TEXTOS EN BARRA LATERAL Y MINI MÓDULOS */
    [data-testid="stSidebar"] h3 { font-size: 1.05rem !important; }
    [data-testid="stSidebar"] h4 { font-size: 0.85rem !important; margin-bottom: 4px !important; }
    [data-testid="stSidebar"] summary p { font-size: 0.80rem !important; }
    
    .stButton>button {
        background-color: #00f3ff !important;
        border: 1.5px solid #00f3ff !important;
        font-weight: bold;
        font-family: monospace;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
        width: 100%;
        border-radius: 6px;
        padding: 5px 10px !important;
    }
    .stButton>button p, .stButton>button span { color: #060913 !important; font-size: 0.78rem !important; }
    .stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.9); }
    .stButton>button:hover p, .stButton>button:hover span { color: #ffffff !important; }
    
    /* TARJETA DE INDICADORES ECONÓMICOS EN VIVO */
    .econ-card {
        border: 1px solid #00f3ff;
        background: rgba(0, 243, 255, 0.06);
        border-radius: 6px;
        padding: 8px 10px;
        margin: 5px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: inset 0 0 6px rgba(0, 243, 255, 0.2);
    }
    .econ-label { font-size: 0.75rem !important; opacity: 0.85; }
    .econ-val { font-size: 0.85rem !important; font-weight: bold; text-shadow: 0 0 6px #00f3ff; }

    /* REACTOR ARC ESTILO STARK - INVERTIDO */
    .arc-reactor-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-bottom: 10px;
    }
    .arc-ring {
        width: 65px;
        height: 65px;
        border: 2.5px solid #00f3ff;
        border-radius: 50%;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle, rgba(0,243,255,0.4) 0%, #060913 75%);
        box-shadow: 0 0 20px rgba(0, 243, 255, 0.8), inset 0 0 10px rgba(0, 243, 255, 0.6);
        margin-bottom: 8px;
    }
    .arc-triangle-inverted {
        width: 0;
        height: 0;
        border-left: 12px solid transparent;
        border-right: 12px solid transparent;
        border-top: 20px solid #00f3ff;
        filter: drop-shadow(0 0 8px #00f3ff);
    }
    
    /* BOTÓN TÁCTICO HTML COMPACTO */
    .tactical-link-btn {
        display: block;
        width: 100%;
        background-color: #00f3ff;
        color: #060913 !important;
        text-align: center;
        padding: 6px 10px;
        margin: 5px 0;
        border-radius: 5px;
        font-size: 0.76rem !important;
        font-weight: bold;
        text-decoration: none;
        font-family: monospace;
        box-shadow: 0 0 8px rgba(0, 243, 255, 0.5);
        transition: all 0.25s ease;
    }
    .tactical-link-btn:hover {
        background-color: #0088cc;
        color: #ffffff !important;
        box-shadow: 0 0 12px rgba(0, 243, 255, 0.9);
    }

    .holo-brain-box {
        border: 1.5px solid #00f3ff;
        background: linear-gradient(135deg, #0a1128 0%, #060913 100%);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.3), inset 0 0 10px rgba(0, 243, 255, 0.15);
        margin: 0 auto 20px auto;
        max-width: 800px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(estilos_css, unsafe_allow_html=True)

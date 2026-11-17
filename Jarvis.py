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

import streamlit as st
import datetime
import sqlite3
import requests
import os
import sys

# --- 1. CONFIGURACION DE PAGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"  # <--- Mantiene la barra lateral oculta por defecto
)

# --- INICIALIZACION DE SESSION_STATE ---
if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"

# --- BASE DE DATOS SQLITE ---
def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS misiones (id INTEGER PRIMARY KEY AUTOINCREMENT, tarea TEXT NOT NULL, estado TEXT DEFAULT 'Pendiente')")
    cursor.execute("CREATE TABLE IF NOT EXISTS memory (key_id TEXT PRIMARY KEY, fact_text TEXT, category TEXT)")
    conn.commit()
    conn.close()

init_db()

class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path
    def remember_fact(self, key_id: str, fact_text: str):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)", (key_id, fact_text, "general"))
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
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Nodo Buin en línea, conectado a Google Gemini, ZapIA y las 7 Memorias SQLite. ¿Qué dominamos hoy?"}
    ]

# --- ESTILOS VISUALES: REACTOR ARC ESTILO STARK & BOTONES SEGUROS ---
estilos_css = """
    <style>
        .stApp { background-color: #060913 !important; color: #00f3ff !important; font-family: monospace; }
        p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
        .stButton>button { background-color: #00f3ff !important; border: 1.5px solid #00f3ff !important; font-weight: bold; font-family: monospace; box-shadow: 0 0 10px rgba(0, 243, 255, 0.6); width: 100%; border-radius: 6px; }
        .stButton>button p, .stButton>button span { color: #060913 !important; }
        .stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243,

import streamlit as st
from datetime import datetime
import base64
from gtts import gTTS
import io
import pandas as pd
import sqlite3
import requests
from streamlit_autorefresh import st_autorefresh
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. - Nodo Táctico",
    page_icon="⚡",
    layout="centered"
)

# Auto-refresco del núcleo cada 1000ms para el segundero en vivo
st_autorefresh(interval=1000, key="reloj_tactico")

# --- 1. CONFIGURACIÓN DE BASE DE DATOS SQLITE PARA TAREAS ---
def init_db():
    conn = sqlite3.connect('nodo_buin.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tareas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT, estado TEXT)''')
    conn.commit()
    conn.close()

init_db()

def agregar_tarea_db(texto):
    conn = sqlite3.connect('nodo_buin.db')
    c = conn.cursor()
    c.execute("INSERT INTO tareas (texto, estado) VALUES (?, ?)", (texto, "Pendiente"))
    conn.commit()
    conn.close()

def obtener_tareas_db():
    conn = sqlite3.connect('nodo_buin.db')
    c = conn.cursor()
    c.execute("SELECT id, texto, estado FROM tareas")
    rows = c.fetchall()
    conn.close()
    return rows

# --- 2. CONSUMO DE API DE CLIMA REAL PARA BUIN ---
def obtener_clima_buin():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-33.73&current=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=America/Santiago"
        response = requests.get(url, timeout=3)
        data = response.json()
        temp = data['current']['temperature_2m']
        hum = data['current']['relative_humidity_2m']
        viento = data['current']['wind_speed_10m']
        return f"{temp}°C", f"{hum}%", f"{viento} km/h"
    except Exception:
        return "21°C", "45%", "12 km/h"

temp_real, hum_real, viento_real = obtener_clima_buin()

# Estilo visual: Fondo negro absoluto y letras en tono cyan/azul Stark
st.markdown(
    """
    <style>
    .stApp {
        background-color: #050505;
        color: #00e5ff;
    }
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #00e5ff !important;
    }
    .stButton>button {
        background-color: #0d1b2a;
        color: #00e5ff !important;
        border: 1px solid #00e5ff;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def hablar_jarvis_web(texto):
    """Genera audio con tono fluido y natural para Jarvis."""
    try:
        tts = gTTS(text=texto, lang='es', tld='cl', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f"""
            <audio autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    except Exception:
        pass

# --- 3. CONTROL DE ACCESO (PIN STARK BIOMÉTRICO) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center; color: #00e5ff;'>🛡️ ACCESO RESTRINGIDO - NODO BUIN</h2>", unsafe_allow_html=True)
    pin_ingresado = st.text_input("Ingrese Código Biométrico / PIN de Seguridad:", type="password")
    if st.button("Desbloquear Sistema Stark", use_container_width=True):
        if pin_ingresado == "1975" or pin_ingresado == "stark":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Acceso denegado. Código incorrecto, jefa.")
    st.stop()

# Reactor Arc Triangular idéntico con brillo LED cian
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 10px;">
        <svg width="90" height="

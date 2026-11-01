import streamlit as st
import datetime
import json
import os
import sqlite3
from gtts import gTTS
import base64
import pandas as pd
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES STARK ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        h1, h2, h3, h4, label, span { color: #00d2ff !important; font-family: monospace; text-align: left !important; }
        
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 20px;
        }
        .arc-ring {
            width: 60px;
            height: 60px;
            border: 3px solid #3a4454;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00d2ff 0%, #060911 70%);
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.6), inset 0 0 10px rgba(0, 210, 255, 0.4);
            margin-bottom: 8px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-bottom: 20px solid #ffffff;
            filter: drop-shadow(0 0 6px #00d2ff);
        }

        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 10px;
            padding: 15px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 15px;
            box-shadow: 0 0 10px rgba(0, 210, 255, 0.1);
            text-align: left !important;
        }
        .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #00d2ff !important;
        }
        .stMarkdown, p, li, span, div, .stChatMessage p {
            color: #00d2ff !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADO PARA LA VOZ ---
if "ultimo_texto_hablado" not in st.session_state:
    st.session_state.ultimo_texto_hablado = "Sistemas operativos y listos, jefa."

# --- FUNCIÓN DE SÍNTESIS DE VOZ (JARVIS TTS) ---
def hablar_como_jarvis(texto):
    st.session_state.ultimo_texto_hablado = texto
    voz_activa = st.session_state.get("toggle_voz_jarvis", True)
    if not voz_activa:
        return
        
    try:
        tts = gTTS(text=texto, lang='es', slow=False)
        audio_file = "jarvis_voz.mp3"
        tts.save(audio_file)
        
        audio_bytes = open(audio_file, 'rb').read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        audio_html = f"""
            <audio autoplay style="display:none;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        print(f"Error en síntesis de voz: {e}")

# --- SISTEMA DE AUTENTICACIÓN (CLAVE DE ACCESO) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("""
        <div class="arc-reactor-container" style="margin-top: 50px;">
            <div class="arc-ring"><div class="arc-triangle"></div></div>
            <h2 style="margin: 0; padding: 0; font-size: 1.8rem; text-align: center !important; color: #00d2ff !important;">ACCESO RESTRINGIDO</h2>
            <p style="margin: 0; font-family: monospace; font-size: 0.85rem; color: #00d2ff !important; text-align: center !important;">[ PROTOCOLO DE SEGURIDAD NODO BUIN ]</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_centro_auth = st.columns([1, 1.5, 1])[1]
    with col_centro_auth:
        clave_ingresada = st.text_input("Ingrese la clave de seguridad del búnker:", type="password")
        if st.button("🔓 Desbloquear Sistema", use_container_width=True):
            if clave_ingresada == "Jarvis":
                st.session_state.autenticado = True
                st.success("Acceso concedido. Bienvenida, jefa.")
                hablar_como_jarvis("Acceso concedido. Bienvenida, jefa. Todos los sistemas del búnker operativos.")
                st.rerun()
            else:
                st.error("Clave incorrecta. Acceso denegado.")
    st.stop()

# --- CÁLCULO DE HORA LOCAL EN CHILE (UTC-3) ---
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
hora_actual = datetime.datetime.now(tz_chile).hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

# --- BASE DE DATOS SQLITE ---
DB_NAME = "jarvis_bunker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tareas (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alertas (id INTEGER PRIMARY KEY AUTOINCREMENT, mensaje TEXT, nivel TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS biometria (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hr INTEGER, spo2 INTEGER, sueno TEXT)''')
    conn.commit()
    
    c.execute("SELECT COUNT(*) FROM tareas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Revisar exámenes médicos y electrolitos (Sodio/Potasio)",))
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Monitorear nodo operativo en Buin",))
        conn.commit()
        
    c.execute("SELECT COUNT(*) FROM alertas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", ("Temperatura Buin óptima (21°C)", "INFO"))
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", ("Blindaje de Familia y Zona Médica ACTIVO", "OK"))
        conn.commit()
    conn.close()

init_db()

def get_db_tareas():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, texto FROM tareas")
    rows = c.fetchall()
    conn.close()
    return rows

def add_db_tarea(texto):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO tareas (texto) VALUES (?)", (texto,))
    conn.commit()
    conn.close()

def delete_db_tarea(id_t):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tareas WHERE id = ?", (id_t,))
    conn.commit()
    conn.close()

def get_db_alertas():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT mensaje, nivel FROM alertas")
    rows = c.fetchall()
    conn.close()
    return rows

def add_biometria(hr, spo2, sueno):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    fecha_hoy = datetime.datetime.now(tz_chile).strftime('%Y-%m-%d %H:%M')
    c.execute("INSERT INTO biometria (fecha, hr, spo2, sueno) VALUES (?, ?, ?, ?)", (fecha_hoy, hr, spo2, sueno))
    conn.commit()
    conn.close()

def get_latest_biometria():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT fecha, hr, spo2, sueno FROM biometria ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row

if "mensajes" not in st.session

import streamlit as st
import time
from groq import Groq
import streamlit.components.v1 as components
from gtts import gTTS
import os
import base64
import sqlite3
import yfinance as yf
import requests
from audio_recorder_streamlit import audio_recorder
from datetime import datetime
import pytz

# 1. Configuración de página
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos globales para forzar el azul neón
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6, span.neon-title {
        color: #00d2ff !important;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.6);
    }
    .stMarkdown p, label, .streamlit-expanderHeader span, div[data-testid="stExpander"] summary span {
        color: #00d2ff !important;
        text-shadow: 0 0 6px rgba(0, 210, 255, 0.4);
    }
    div[data-testid="stMetricLabel"] {
        color: #00d2ff !important;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        text-shadow: 0 0 10px #00d2ff;
    }
    .stSelectbox label, .stCheckbox span {
        color: #00d2ff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Base de datos persistente (SQLite)
def inicializar_db():
    conn = sqlite3.connect("jarvis_tactical.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bitacora (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nota TEXT
        )
    """)
    conn.commit()
    return conn

db_conn = inicializar_db()

def guardar_mensaje_db(role, content):
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
    db_conn.commit()

def cargar_mensajes_db():
    cursor = db_conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history")
    rows = cursor.fetchall()
    return [{"role": r[0], "content": r[1]} for r in rows]

def purgar_db():
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM chat_history")
    db_conn.commit()

# Cargar mensajes en session_state desde SQLite con saludo dinámico
if "messages" not in st.session_state:
    st.session_state.messages = cargar_mensajes_db()
    if not st.session_state.messages:
        chile_tz = pytz.timezone("America/Santiago")
        hora_actual = datetime.now(chile_tz).hour
        if 5 <= hora_actual < 12:
            saludo_inicial = "Buenos días, Jefa. Sistemas tácticos en línea y operando al 100%. ¿Qué protocolos ejecutamos hoy?"
        elif 12 <= hora_actual < 20:
            saludo_inicial = "Buenas tardes, Jefa. La base de Buin está estable y los sistemas rinden al máximo. ¿En qué le sirvo?"
        else:
            saludo_inicial = "Buenas noches, Jefa. Trabajando en horario extendido, como corresponde a este taller. ¿Cuál es la orden?"
        
        st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})
        guardar_mensaje_db("assistant", saludo_inicial)

# Función para reproducir voz sintetizada automáticamente
def hablar_jarvis(texto):
    try:
        tts = gTTS(text=texto, lang='es', slow=False)
        audio_path = "jarvis_voice.mp3"
        tts.save(audio_path)
        with open(audio_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            audio_html = f"""
                <audio autoplay style="display:none;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
    except Exception:
        pass

# Función para generar reporte HTML descargable
def generar_html_pdf(historial):
    html_content = """
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: monospace; color: #002244; padding: 20px; }
            h1 { color: #00d2ff; border-bottom: 2px solid #00d2ff; padding-bottom: 5px; }
            .msg { margin-bottom: 15px; padding: 10px; border-radius: 5px; background: #f0f8ff; }
            .user { font-weight: bold; color: #004488; }
            .jarvis { font-weight: bold; color: #0088cc; }
        </style>
    </head>
    <body>
        <h1>CENTRO DE COMANDO J.A.R.V.I.S. - INFORME TÁCTICO</h1>
    """
    for msg in historial:
        rol_class = "user" if msg["role"] == "user" else "jarvis"
        rol_nombre = "Jefa" if msg["role"] == "user" else "J.A.R.V.I.S."
        html_content += f'<div class="msg"><span class="{rol_class}">{rol_nombre}:</span><p>{msg["content"]}</p></div>'
    html_content += "</body></html>"
    return html_content

# Visor Holográfico 3D
def renderizar_gods_eye(hex_color):
    try:
        gods_eye_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <style>
                body {{ margin: 0; overflow: hidden; background: transparent; }}
                #canvas-container {{ width: 100%; height: 280px; position: relative; cursor: pointer; }}
                #hud-text {{
                    position: absolute; top: 10px; left: 10px; 
                    font-family: monospace; color: {hex_color}; font-size: 11px;
                    background: rgba(0,0,0,0.8); padding: 4px 8px; border-radius: 4px;
                    border: 1px solid {hex_color}; z-index: 10;
                }}
                #seismic-hud {{
                    position: absolute; bottom: 10px; left: 10px; 
                    font-family: monospace; color: #00ffcc; font-size: 10px;
                    background: rgba(0,0,0,0.7); padding: 3px 6px; border-radius: 3px;
                    z-index: 10;
                }}
                #cam-link {{
                    position: absolute; bottom: 10px; right: 10px;
                    font-family: monospace; color: #ffffff; font-size: 10px;
                    background: rgba(0, 150, 255, 0.6); padding: 4px 8px; border-radius: 4px;
                    text-decoration: none; z-index: 10; border: 1px solid #00d2ff;
                }}
                #cam-link:hover {{ background: rgba(0, 210, 255, 0.9); }}
            </style>
        </head>
        <body>
            <div id="canvas-container">
                <div id="hud-text">GOD's EYE VIEW // RED SÍSMICA GLOBAL & CÁMARAS</div>
                <div id="seismic-hud">Sistema nominal operativo.</div>
                <a id="cam-link" href="https://www.windy.com/-Webcams/Chile/Santiago/Santiago/webcams/1423152643" target="_blank">📹 Cámaras Globales</a>
            </div>
            <script>
                const container = document.getElementById('canvas-container');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(4

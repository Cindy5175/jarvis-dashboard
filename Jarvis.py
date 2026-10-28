import streamlit as str_lit
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
import psutil

# 1. Configuración de página
str_lit.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Control de Estado para Código Rojo y Enlace Satelital
if "codigo_rojo" not in str_lit.session_state:
    str_lit.session_state.codigo_rojo = False

if "enlace_satelital" not in str_lit.session_state:
    str_lit.session_state.enlace_satelital = True

color_neon_principal = "#ff3333" if str_lit.session_state.codigo_rojo else "#00d2ff"
color_sombra_neon = "rgba(255, 51, 51, 0.8)" if str_lit.session_state.codigo_rojo else "rgba(0, 210, 255, 0.6)"

# Estilos globales dinámicos
str_lit.markdown(f"""
    <style>
    h1, h2, h3, h4, h5, h6, span.neon-title {{
        color: {color_neon_principal} !important;
        text-shadow: 0 0 10px {color_sombra_neon};
    }}
    .stMarkdown p, label, .streamlit-expanderHeader span, div[data-testid="stExpander"] summary span {{
        color: {color_neon_principal} !important;
        text-shadow: 0 0 6px {color_sombra_neon};
    }}
    div[data-testid="stMetricLabel"] {{
        color: {color_neon_principal} !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: #ffffff !important;
        text-shadow: 0 0 10px {color_neon_principal};
    }}
    .stSelectbox label, .stCheckbox span {{
        color: {color_neon_principal} !important;
    }}
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS misiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarea TEXT,
            estado TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clima_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            detalles TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentos_rag (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            contenido TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones_archivadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            resumen TEXT
        )
    """)
    conn.commit()
    return conn

db_conn = inicializar_db()

def guardar_mensaje_db(role, content):
    cursor = db_conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history ORDER BY id DESC LIMIT 1")
    ultimo = cursor.fetchone()
    if not ultimo or ultimo[0] != role or ultimo[1] != content:
        cursor.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
        db_conn.commit()

def cargar_mensajes_db():
    cursor = db_conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history")
    rows = cursor.fetchall()
    return [{"role": r[0], "content": r[1]} for r in rows]

def purgar_db():
    cursor = db_conn.cursor()
    cursor.execute("SELECT content FROM chat_history LIMIT 1")
    row = cursor.fetchone()
    if row:
        fecha_sesion = datetime.now(pytz.timezone("America/Santiago")).strftime("%Y-%m-%d %H:%M")
        c_db = db_conn.cursor()
        c_db.execute("INSERT INTO sesiones_archivadas (fecha, resumen) VALUES (?, ?)", (fecha_sesion, f"Sesión iniciada con: {row[0][:40]}..."))
        db_conn.commit()
    
    cursor.execute("DELETE FROM chat_history")
    db_conn.commit()

if "messages" not in str_lit.session_state:
    str_lit.session_state.messages = cargar_mensajes_db()
    if not str_lit.session_state.messages:
        chile_tz = pytz.timezone("America/Santiago")
        hora_actual = datetime.now(chile_tz).hour
        
        clima_info = ""
        try:
            res_c = requests.get("https://api.open-meteo.com/v1/forecast?latitude=-33.7331&longitude=-70.7072&current_weather=true", timeout=2).json()
            t_val = res_c["current_weather"]["temperature"]
            w_val = res_c["current_weather"]["windspeed"]
            clima_info = f" [Reporte Buin: {t_val}°C, Viento {w_val} km/h]."
        except Exception:
            clima_info = " [Reporte Buin: Estable]."

        tipo_enlace = "enlace satelital Stark" if str_lit.session_state.enlace_satelital else "red terrestre de fibra"
        if 5 <= hora_actual < 12:
            saludo_inicial = f"Buenos días, Jefa.{clima_info} Enrutado mediante {tipo_enlace}. Sistemas tácticos al 100%. ¿Qué proyectos ejecutamos hoy?"
        elif 12 <= hora_actual < 20:
            saludo_inicial = f"Buenas tardes, Jefa.{clima_info} Conexión vía {tipo_enlace} estable en Buin. ¿En qué puedo acompañarla o ayudarle hoy?"
        else:
            saludo_inicial = f"Buenas noches, Jefa.{clima_info} Operando en horario extendido a través de {tipo_enlace}. Aquí estoy listo para lo que necesite."
        
        str_lit.session_state.messages.append({"role": "assistant", "content": saludo_inicial})
        guardar_mensaje_db("assistant", saludo_inicial)

def hablar_jarvis(texto):
    try:
        velocidad = str_lit.session_state.get("voz_lenta", False)
        tts = gTTS(text=texto, lang='es', slow=velocidad)
        audio_path = "jarvis_voice.mp3"
        tts.save(audio_path)
        with open(audio_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            audio_html = '<audio autoplay style="display:none;"><source src="data:audio/mp3;base64,' + b64 + '" type="audio/mp3"></audio>'
            str_lit.markdown(audio_html, unsafe_allow_html=True)
    except Exception:
        pass

def enviar_alerta_telegram(mensaje_alerta):
    try:
        token = str_lit.secrets.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = str_lit.secrets.get("TELEGRAM_CHAT_ID", "")
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": f"🚨 [JARVIS BUIN ALERTA]: {mensaje_alerta}"}
            requests.post(url, json=payload, timeout=3)
    except Exception:
        pass

def generar_html_pdf(historial):
    html_content = "<html><head><meta charset='utf-8'>"
    html_content += "<style>"
    html_content += "body { font-family: monospace; color: #002244; padding: 20px; }"
    html_content += "h1 { color: #00d2ff; border-bottom: 2px solid #00d2ff; padding-bottom: 5px; }"
    html_content += ".msg { margin-bottom: 15px; padding: 10px; border-radius: 5px; background: #f0f8ff; }"
    html_content += ".user { font-weight: bold; color: #004488; }"
    html_content += ".jarvis { font-weight: bold; color: #0088cc; }"
    html_content += "</style></head><body>"
    html_content += "<h1>CENTRO DE COM

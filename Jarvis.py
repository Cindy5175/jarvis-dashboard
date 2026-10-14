import streamlit as st
import streamlit.components.v1 as components
import datetime
import random
import json
import os
import subprocess

# Configuración de página en modo ancho
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónoma // Hologram Core", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ARCHIVO DE MEMORIA PERSISTENTE LOCAL
MEMORY_FILE = "jarvis_memory.json"

def cargar_memoria():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "usuario": {
            "nombre": "Cindy",
            "titulo": "Jefa",
            "ubicacion": "Buin, Chile"
        },
        "notas": ["Búnker activado en Buin, Chile.", "Satélite Serafín en enlace estable."],
        "habilidades": {
            "Diagnostico": "st.write('Todos los sistemas operativos al 100%')"
        },
        "canales_multiplataforma": {
            "Telegram": {"estado": "Conectado", "bot_id": "@JarvisBunkerBot"}
        },
        "preferencias_voz": {
            "voz_activa": "Español (Neutro)",
            "elevenlabs_api_key": "",
            "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM"
        }
    }

def guardar_memoria(memoria):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error guardando memoria: {e}")

if "memoria" not in st.session_state:
    st.session_state.memoria = cargar_memoria()

nombre_jefa = st.session_state.memoria.get("usuario", {}).get("nombre", "Cindy")
titulo_jefa = st.session_state.memoria.get("usuario", {}).get("titulo", "Jefa")

# ESTILOS CSS TÁCTICOS Y HOLOGRÁFICOS
st.markdown("""
    <style>
    .stApp, .main {
        background-color: #000000 !important;
        color: #ffffff;
    }
    .main-header {
        color: #00d2ff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
        letter-spacing: 2px;
        text-align: center;
        margin-bottom: 0px;
    }
    .status-bar {
        text-align: center;
        color: #00d2ff;
        font-size: 13px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-bottom: 20px;
    }
    .holo-card {
        background-color: #050505;
        border: 1px solid #00d2ff;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.2);
    }
    .holo-title {
        color: #00d2ff;
        font-size: 14px;
        font-weight: bold;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #050505 !important;
        color: #00d2ff !important;
        border: 1px solid #00d2ff !important;
        border-radius: 8px !important;
    }
    label[data-testid="stWidgetLabel"] {
        color: #00d2ff !important;
        font-weight: bold !important;
    }
    div.stButton > button, div.stFormSubmitButton > button {
        background-color: #050505 !important;
        color: #00d2ff !important;
        border: 1px solid #00d2ff !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: #00d2ff !important;
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# CABECERA HOLOGRÁFICA
st.markdown('<h1 class="main-header">⚡ J.A.R.V.I.S. CORE 3.0</h1>', unsafe_allow_html=True)
st.markdown(f'<div class="status-bar">CORE STATUS: ONLINE &nbsp;|&nbsp; OPERANDO PARA {titulo_jefa.upper()} {nombre_jefa.upper()} &nbsp;|&nbsp; FULL VOICE ENGINE: ENABLED</div>', unsafe_allow_html=True)

# DISPOSICIÓN EN 3 COLUMNAS
col_telemetria, col_orbe, col_chat = st.columns([1, 1.4, 1.2])

with col_telemetria:
    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.markdown('<div class="holo-title">⚙️ SYSTEM TELEMETRY</div>', unsafe_allow_html=True)
    
    gauges_html = """
    <div style="display: flex; justify-content: space-around; align-items: center; padding: 10px 0;">
        <div style="text-align: center;">
            <div style="width: 60px; height: 60px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">38%</div>
            <span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">CPU</span>
        </div>
        <div style="text-align: center;">
            <div style="width: 60px; height: 60px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">57%</div>
            <span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">RAM</span>
        </div>
        <div style="text-align: center;">
            <div style="width: 60px; height: 60px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">100%</div>
            <span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">PWR</span>
        </div>
    </div>
    """
    components.html(gauges_html, height=100)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.markdown('<div class="holo-title">📍 BASE & SATÉLITE</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#00d2ff; font-size:12px; margin:2px 0;'>Ubicación: {st.session_state.memoria['usuario'].get('ubicacion', 'Buin, Chile')}</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d2ff; font-size:12px; margin:2px 0;'>Serafín-Sat: Órbita Estable</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d2ff; font-size:12px; margin:2px 0;'>USD/CLP:

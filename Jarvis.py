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
        "misiones": ["Verificar sistemas del búnker", "Sincronizar red táctica"],
        "habilidades": {
            "Diagnostico": "st.write('Todos los sistemas operativos al 100%')"
        },
        "canales_multiplataforma": {
            "Telegram": {"estado": "Conectado", "bot_id": "@JarvisBunkerBot"}
        },
        "preferencias_voz": {
            "voz_activa": "Español (Neutro)",
            "elevenlabs_api_key": "",
            "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",
            "ai_api_key": ""
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

# ESTILOS CSS TÁCTICOS, EXPANDER NEÓN Y HOLOGRÁFICOS
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
        font-size: 12px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }
    .market-ticker {
        background: #050505;
        border: 1px solid #00d2ff;
        border-radius: 8px;
        padding: 6px 12px;
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-bottom: 15px;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.2);
        font-family: monospace;
        font-size: 12px;
    }
    .market-item {
        color: #00d2ff;
    }
    .market-value {
        color: #00ffaa;
        font-weight: bold;
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

    /* ESTILO AZUL NEÓN PARA LOS DESPLEGABLES (st.expander) */
    div[data-testid="stExpander"] {
        background-color: #050505 !important;
        border: 1px solid #00d2ff !important;
        border-radius: 8px !important;
        box-shadow: 0 0 12px rgba(0, 210, 255, 0.25) !important;
        margin-bottom: 10px !important;
    }
    div[data-testid="stExpander"] details summary {
        background-color: #050505 !important;
        color: #00d2ff !important;
        font-weight: bold !important;
    }
    div[data-testid="stExpander"] details summary p, 
    div[data-testid="stExpander"] details summary svg {
        color: #00d2ff !important;
        fill: #00d2ff !important;
    }
    </style>
""", unsafe_allow_html=True)

# CABECERA HOLOGRÁFICA
st.markdown('<h1 class="main-header">⚡ J.A.R.V.I.S. CORE 3.0</h1>', unsafe_allow_html=True)
st.markdown(f'<div class="status-bar">CORE STATUS: ONLINE &nbsp;|&nbsp; OPERANDO PARA {titulo_jefa.upper()} {nombre_jefa.upper()} &nbsp;|&nbsp; VOICE & RADAR ENGINE: ACTIVE</div>', unsafe_allow_html=True)

# TICKER FINANCIERO TÁCTICO (USD, EURO, IPSA)
st.markdown("""
    <div class="market-ticker">
        <span class="market-item">💵 USD/CLP: <span class="market-value">$930.50 ▲ +0.2%</span></span>
        <span class="market-item">💶 EUR/CLP: <span class="market-value">$1,012.40 ▲ +0.1%</span></span>
        <span class="market-item">📈 IPSA CHILE: <span class="market-value">6,480.12 pts ▲ +0.4%</span></span>
        <span class="market-item">📡 SERAFÍN-SAT: <span class="market-value">LINK 100%</span></span>
    </div>
""", unsafe_allow_html=True)

# DISPOSICIÓN EN 3 COLUMNAS
col_telemetria, col_orbe, col_chat = st.columns([1, 1.4, 1.2])

with col_telemetria:
    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.markdown('<div class="holo-title">⚙️ SYSTEM TELEMETRY</div>', unsafe_allow_html=True)
    
    gauges_html = """
    <div style="display: flex; justify-content: space-around; align-items: center; padding: 5px 0;">
        <div style="text-align: center;">
            <div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">38%</div>
            <span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">CPU</span>
        </div>
        <div style="text-align: center;">
            <div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">57%</div>
            <span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">RAM</span>
        </div>
        <div style="text-align: center;">
            <div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">100%</div>
            <span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">PWR</span>
        </div>
    </div>
    """
    components.html(gauges_html, height=90)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.markdown('<div class="holo-title">📍 BASE & SATÉLITE</div>', unsafe_allow_html=True)
    
    globe_html = """
    <div style="display: flex; align-items: center; gap: 12px; padding: 2px 0;">
        <div class="globe-container">
            <div class="globe">
                <div class="buin-pin" title="Ubicación: Buin, Chile"></div>
            </div>
        </div>
        <div>
            <p style='color:#00d2ff; font-size:12px; margin:2px 0; font-weight:bold;'>🌍 Ubicación: Buin, Chile</p>
            <p style='color:#00d2ff; font-size:11px; margin:2px 0;'>🛰️ Serafín-Sat: Órbita Estable</p>
        </div>
    </div>

    <style>
    .globe-container { width: 55px; height: 55px; perspective: 400px; }
    .globe {
        width: 50px; height: 50px; border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, #00d2ff 0%, #003366 60%, #000511 100%);
        border: 1px solid #00d2ff; box-shadow: 0 0 12px rgba(0, 210, 255, 0.6);
        position: relative; overflow: hidden;
    }
    .globe::before {
        content: ''; position: absolute; width: 100%; height: 100%; border-radius: 50%;
        border: 1px dashed rgba(0, 210, 255, 0.4); animation: rotateGlobe 8s linear infinite;
    }
    .buin-pin {
        position: absolute; top: 65%; left: 30%; width: 6px; height: 6px;
        background-color: #ff0055; border-radius: 50%; box-shadow: 0 0 8px #ff0055;
        animation: pulsePin 1.5s ease-in-out infinite alternate;
    }
    @keyframes rotateGlobe { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    @keyframes pulsePin { 0% { transform: scale(0.8); } 100% { transform: scale(1.5); } }
    </style>
    """
    components.html(globe_html, height=65)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.markdown('<div class="holo-title">📡 RADAR DE ENLACE TÁCTICO</div>', unsafe_allow_html=True)
    radar_html = """
    <div style="display: flex; justify-content: center; align-items: center; padding: 5px 0;">
        <div class="radar">
            <div class="sweep"></div>
            <div class="target t1"></div>
            <div class="target t2"></div>
        </div>
    </div>
    <style>
    .radar {
        width: 100px; height: 100px; border-radius: 50%;
        border: 1px solid #00d2ff; background: #000000;
        box-shadow: 0 0 12px rgba(0, 210, 255, 0.3);
        position: relative; overflow: hidden;
    }
    .radar::before {
        content: ''; position: absolute; top: 50%; left: 0; width: 100%; height: 1px; background: rgba(0, 210, 255, 0.3);
    }
    .radar::after {
        content: ''; position: absolute; left: 50%; top: 0; width: 1px; height: 100%; background: rgba(0, 210, 255, 0.3);
    }
    .sweep {
        width: 100%; height: 100%; border-radius: 50%;
        background: conic-gradient(from 0deg, rgba(0,

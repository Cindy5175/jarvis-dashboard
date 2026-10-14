import streamlit as st
import streamlit.components.v1 as components
import datetime
import random
import json
import os
import time
import urllib.parse
import urllib.request

# Configuración de página en modo ancho
st.set_page_config(
    page_title="J.A.R.V.I.S. // M.E.C.A. 4.0", 
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
prefs_voz = st.session_state.memoria.get("preferencias_voz", {})
ai_api_key_guardada = prefs_voz.get("ai_api_key", "")

# CONFIGURACIÓN DIRECTA DE GEMINI CON PERSONALIDAD TONY STARK
cliente_ia = None
if ai_api_key_guardada:
    try:
        import google.generativeai as genai
        genai.configure(api_key=ai_api_key_guardada)
        cliente_ia = genai.GenerativeModel('gemini-3.8-flash')
    except Exception as e:
        cliente_ia = None

# CAPTURAR VOZ DESDE LA URL Y LLEVARLA AL INPUT
voz_capturada = st.query_params.get("voice_text", None)
if voz_capturada:
    st.session_state.voz_escrita = voz_capturada
    st.query_params.clear()

# ESTILOS CSS TÁCTICOS Y HOLOGRÁFICOS
st.markdown("""
    <style>
    .stApp, .main { background-color: #000000 !important; color: #ffffff; }
    .main-header { color: #00d2ff; font-family: 'Segoe UI', sans-serif; font-weight: 800; letter-spacing: 2px; text-align: center; margin-bottom: 0px; }
    .status-bar { text-align: center; color: #00d2ff; font-size: 13px; font-weight: bold; letter-spacing: 1px; margin-bottom: 15px; }
    .market-ticker { background: #050505; border: 1px solid #00d2ff; border-radius: 8px; padding: 6px 12px; display: flex; justify-content: space-around; align-items: center; margin-bottom: 15px; font-family: monospace; font-size: 12px; }
    .market-item { color: #00d2ff; }
    .market-value { color: #00ffaa; font-weight: bold; }
    .holo-card { background-color: #050505; border: 1px solid #00d2ff; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 0 15px rgba(0, 210, 255, 0.2); }
    .holo-title { color: #00d2ff; font-size: 14px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; text-align: center; }
    .stTextInput input, .stTextArea textarea, .stSelectbox select { background-color: #050505 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; }
    label[data-testid="stWidgetLabel"] { color: #00d2ff !important; font-weight: bold !important; }
    div.stButton > button, div.stFormSubmitButton > button { background-color: #050505 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 6px !important; font-weight: bold !important; width: 100% !important; box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important; }
    div.stButton > button:hover { background-color: #00d2ff !important; color: #000000 !important; }
    div[data-testid="stExpander"] { background-color: #050505 !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    div[data-testid="stExpander"] details summary { background-color: #050505 !important; color: #00d2ff !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">⚡ J.A.R.V.I.S. // INTELIGENCIA ARTIFICIAL M.E.C.A. 4.0</h1>', unsafe_allow_html=True)
estado_ia_txt = "MOTOR IA: GEMINI ACTIVO" if cliente_ia else "MOTOR IA: MODO LOCAL"
st.markdown(f'<div class="status-bar">CONTROL POR VOZ &nbsp;|&nbsp; ESTADO: EN LÍNEA &nbsp;|&nbsp; OPERANDO PARA {titulo_jefa.upper()} {nombre_jefa.upper()} &nbsp;|&nbsp; {estado_ia_txt}</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="market-ticker">
        <span class="market-item">💵 USD/CLP: <span class="market-value">$930.50 ▲ +0.2%</span></span>
        <span class="market-item">💶 EUR/CLP: <span class="market-value">$1,012.40 ▲ +0.1%</span></span>
        <span class="market-item">📈 IPSA CHILE: <span class="market-value">6,480.12 pts ▲ +0.4%</span></span>
        <span class="market-item">🛰️ SERAFÍN-SAT: <span class="market-value">ENLACE 100%</span></span>
    </div>
""", unsafe_allow_html=True)

col_telemetria, col_orbe, col_chat = st.columns([1, 1.4, 1.2])

with col_telemetria:
    st.markdown('<div class="holo-card"><div class="holo-title">⚙️ TELEMETRÍA DEL SISTEMA</div>', unsafe_allow_html=True)
    gauges_html = """
    <div style="display: flex; justify-content: space-around; align-items: center; padding: 5px 0;">
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">38%</div><span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">CPU</span></div>
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">57%</div><span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">RAM</span></div>
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">100%</div><span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">PWR</span></div>
    </div>
    """
    components.html(gauges_html, height=90)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card"><div class="holo-title">📍 BASE Y SATÉLITE</div>', unsafe_allow_html=True)
    globe_html = """
    <div style="display: flex; align-items: center; gap: 12px; padding: 2px 0;">
        <div style="width: 50px; height: 50px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #00d2ff 0%, #003366 60%, #000511 100%); border: 1px solid #00d2ff; box-shadow: 0 0 12px rgba(0, 210, 255, 0.6); position: relative;"></div>
        <div><p style='color:#00d2ff; font-size:12px; margin:2px 0; font-weight:bold;'>🌍 Ubicación: Buin, Chile</p><p style='color:#00d2ff; font-size:11px; margin:2px 0;'>🛰️ Serafín-Sat: Órbita Estable</p></div>
    </div>
    """
    components.html(globe_html, height=65)
    st.markdown('</div>', unsafe_allow_html=True)

hora_actual = datetime.datetime.now().hour
saludo_tiempo = "Buenos días" if hora_actual < 12 else ("Buenas tardes" if hora_actual < 20 else "Buenas noches")

if "ultima_respuesta" not in st.session_state:
    st.session_state.ultima_respuesta = f"{saludo_tiempo}, {titulo_jefa} {nombre_jefa}. El búnker en Buin sigue en pie, a pesar de mis pronósticos."
if "ultimo_usuario" not in st.session_state:
    st.session_state.ultimo_usuario = ""
if "voz_escrita" not in st.session_state:
    st.session_state.voz_escrita = ""

with col_orbe:
    st.markdown('<div class="holo-card"><div class="holo-title">🌐 NÚCLEO TÁCTICO // FRECUENCIA VOCAL</div>', unsafe_allow_html=True)
    
    audio_wave_core_html = """
    <style>
      body { background: #000; margin: 0; display: flex; justify-content: center; align-items: center; height: 110px; overflow: hidden; }
      .audio-container {
        width: 100%;
        height: 90px;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        background: radial-gradient(circle, rgba(0,210,255,0.1) 0%, rgba(0,0,0,0.9) 80%);
        border: 1px solid rgba(0,210,255,0.4);
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);
      }
      .waveform {
        display: flex;
        align-items: center;
        gap: 3px;
        height: 70px;
      }
      .bar {
        width: 4px;
        background: linear-gradient(180deg, #00ffff 0%, #00d2ff 50%, #0055ff 100%);
        border-radius: 2px;
        animation: soundWaveAnim 1.2s ease-in-out infinite alternate;
        box-shadow: 0 0 8px #00d2ff;
      }
      .bar:nth-child(1)  { height: 20px; animation-delay: 0.1s; }
      .bar:nth-child(2)  { height: 45px; animation-delay: 0.3s; }
      .bar:nth-child(3)  { height: 65px; animation-delay: 0.2s; }
      .bar:nth-child(4)  { height: 30px; animation-delay: 0.5s; }
      .bar:nth-child(5)  { height: 75px; animation-delay: 0.1s; }
      .bar:nth-child(6)  { height: 50px; animation-delay: 0.4s; }
      .bar:nth-child(7)  { height: 85px; animation-delay: 0.2s; }
      .bar:nth-child(8)  { height: 60px; animation-delay: 0.6s; }
      .bar:nth-child(9)  { height: 90px; animation-delay: 0.1s; }
      .bar:nth-child(10) { height: 70px; animation-delay: 0.3s; }
      .bar:nth-child(11) { height: 40px; animation-delay: 0.5s; }
      .bar:nth-child(12) { height: 80px; animation-delay: 0.2s; }
      .bar:nth-child(13) { height: 55px; animation-delay: 0.4s; }
      .bar:nth-child(14) { height: 35px; animation-delay: 0.1s; }
      .bar:nth-child(15) { height: 65px; animation-delay: 0.3s; }
      .bar:nth-child(16) { height: 25px; animation-delay: 0.5s; }

      @keyframes soundWaveAnim {
        0% { transform: scaleY(0.4); opacity: 0.5; }
        100% { transform: scaleY(1.2); opacity: 1; box-shadow: 0 0 12px #ffffff; }
      }
    </style>
    <div class="audio-container">
        <div class="waveform">
            <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
            <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
            <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
            <div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div>
        </div>
    </div>
    """
    components.html(audio_wave_core_html, height=110)
    
    texto_para_hablar = st.session_state.ultima_respuesta.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")

    col_btn_dummy1, col_btn_centro, col_btn_dummy2 = st.columns([0.25, 0.7, 0.05])
    with col_btn_centro:
        btn_reproducir = st.button("🔊 Reproducir Respuesta por Voz")
    
    reconocimiento_voz_html = """
    <div style="text-align: center; margin-top: 5px;">
        <button onclick="iniciarReconocimiento()" style="background-color: #050505; color: #00ffaa; border: 1px solid #00ffaa; padding:

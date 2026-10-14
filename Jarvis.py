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

# PUNTO 3: TICKER FINANCIERO TÁCTICO (USD, EURO, IPSA)
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
    
    # GLOBO TERRÁQUEO CON PIN EN BUIN
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

    # PUNTO 1: RADAR TÁCTICO DE ENLACE SATELITAL
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
        background: conic-gradient(from 0deg, rgba(0, 210, 255, 0.4) 0deg, transparent 60deg);
        animation: radarSweep 4s linear infinite;
    }
    .target { position: absolute; width: 4px; height: 4px; background: #00ffaa; border-radius: 50%; box-shadow: 0 0 6px #00ffaa; }
    .t1 { top: 30%; left: 70%; }
    .t2 { top: 75%; left: 40%; }
    @keyframes radarSweep { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    </style>
    """
    components.html(radar_html, height=110)
    st.markdown('</div>', unsafe_allow_html=True)

# LÓGICA DE RESPUESTA Y SALUDOS DINÁMICOS
hora_actual = datetime.datetime.now().hour
if hora_actual < 12:
    saludo_tiempo = "Buenos días"
elif hora_actual < 20:
    saludo_tiempo = "Buenas tardes"
else:
    saludo_tiempo = "Buenas noches"

if "ultima_respuesta" not in st.session_state:
    st.session_state.ultima_respuesta = f"{saludo_tiempo}, {titulo_jefa} {nombre_jefa}. Todos los sistemas y radares en línea en Buin."
if "ultimo_usuario" not in st.session_state:
    st.session_state.ultimo_usuario = ""

with col_orbe:
    texto_para_hablar = st.session_state.ultima_respuesta.replace('"', '\\"').replace("'", "\\'")
    
    orb_component = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 350px;">
        <div class="orb-container" onclick="hablarJarvis()" style="cursor: pointer;" title="Toca el orbe para escuchar a J.A.R.V.I.S.">
            <div id="ring" class="outer-ring"></div>
            <div id="core" class="inner-core"></div>
        </div>
        <div class="sound-wave" id="waveBox">
            <span class="bar"></span><span class="bar"></span><span class="bar"></span>
            <span class="bar"></span><span class="bar"></span><span class="bar"></span>
        </div>
        
        <div style="margin-top: 12px; display: flex; gap: 8px;">
            <button onclick="hablarJarvis()" style="background-color: #050505; color: #00d2ff; border: 1px solid #00d2ff; padding: 6px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11px;">🔊 Reproducir Respuesta</button>
            <button onclick="activarMicrofono()" style="background-color: #00d2ff; color: #000; border: none; padding: 6px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11px; box-shadow: 0 0 10px rgba(0,210,255,0.4);">🎤 Dictar Comando</button>
        </div>

        <p id="orbStatus" style="color: #00d2ff; font-size: 11px; margin-top: 8px; font-family: monospace;">[ SISTEMA DE VOZ ONLINE, JEFA ]</p>
    </div>

    <style>
    .orb-container {{ position: relative; width: 170px; height: 170px; display: flex; align-items: center; justify-content: center; }}
    .outer-ring {{
        position: absolute; width: 160px; height: 160px; border: 2px dashed #00d2ff; border-radius: 50%;
        animation: rotateRing 12s linear infinite; box-shadow: 0 0 15px rgba(0, 210, 255, 0.4); transition: all 0.3s ease;
    }}
    .inner-core {{
        width: 100px; height: 100px; background: radial-gradient(circle, #00d2ff 0%, #005580 70%, #000000 100%);
        border-radius: 50%; box-shadow: 0 0 35px #00d2ff, inset 0 0 15px #ffffff;
        animation: pulseCore 2.5s ease-in-out infinite alternate; transition: all 0.3s ease;
    }}
    .speaking-core {{
        background: radial-gradient(circle, #00ffff 0%, #0088cc 70%, #001122 100%) !important;
        box-shadow: 0 0 60px #00ffff, inset 0 0 25px #ffffff !important;
        animation: pulseFast 0.8s ease-in-out infinite alternate !important;
    }}
    .listening-core {{
        background: radial-gradient(circle, #ff0055 0%, #880022 70%, #000000 100%) !important;
        box-shadow: 0 0 60px #ff0055, inset 0 0 25px #ffffff !important;
    }}
    .speaking-ring {{ border-color: #00ffff !important; box-shadow: 0 0 30px #00ffff !important; animation: rotateRing 3s linear infinite !important; }}
    .sound-wave {{ display: flex; gap: 5px; margin-top: 12px; }}
    .bar {{ width: 4px; height: 8px; background-color: #00d2ff; border-radius: 2px; transition: all 0.2s ease; }}
    .active-wave .bar {{ animation: wave 0.6s ease-in-out infinite alternate; }}
    .active-wave .bar:nth-child(2) {{ animation-delay: 0.1s; }}
    .active-wave .bar:nth-child(3) {{ animation-delay: 0.2s; }}
    .active-wave .bar:nth-child(4) {{ animation-delay: 0.3s; }}
    .active-wave .bar:nth-child(5) {{ animation-delay: 0.2s; }}
    .active-wave .bar:nth-child(6) {{ animation-delay: 0.1s; }}

    @keyframes rotateRing {{ from {{ transform: rotate(0deg); }} to {{ transform: rotate(360deg); }} }}
    @keyframes pulseCore {{ 0% {{ transform: scale(0.92); box-shadow: 0 0 20px #00d2ff; }} 100% {{ transform: scale(1.08); box-shadow: 0 0 45px #00d2ff; }} }}
    @keyframes pulseFast {{ 0% {{ transform: scale(0.88); }} 100% {{ transform: scale(1.15); }} }}
    @keyframes wave {{ 0% {{ height: 6px; }} 100% {{ height: 32px; }} }}
    </style>

    <script>
    function hablarJarvis() {{
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        const texto = "{texto_para_hablar}";
        const utterance = new SpeechSynthesisUtterance(texto);
        utterance.lang = 'es-ES'; utterance.rate = 1.0; utterance.pitch = 0.9;

        const ring = document.getElementById("ring");
        const core = document.getElementById("core");
        const waveBox = document.getElementById("waveBox");
        const orbStatus = document.getElementById("orbStatus");

        utterance.onstart = function() {{
            core.classList.add("speaking-core"); ring.classList.add("speaking-ring");
            waveBox.classList.add("active-wave"); orbStatus.innerText = "⚡ [ J.A.R.V.I.S. HABLANDO ]"; orbStatus.style.color = "#00ffff";
        }};

        utterance.onend = function() {{
            core.classList.remove("speaking-core"); ring.classList.remove("speaking-ring");
            waveBox.classList.remove("active-wave"); orbStatus.innerText = "[ SISTEMA EN ESPERA ]"; orbStatus.style.color = "#00d2ff";
        }};

        window.speechSynthesis.speak(utterance);
    }}

    function activarMicrofono() {{
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) return;
        const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
        recognition.lang = 'es-CL'; recognition.interimResults = false;

        const core = document.getElementById("core");
        const orbStatus = document.getElementById("orbStatus");

        orbStatus.innerText = "🎙️ [ ESCUCHANDO A LA JEFA... ]"; orbStatus.style.color = "#ff0055"; core.classList.add("listening-core");

        recognition.onresult = function(event) {{
            const comando = event.results[0][0].transcript;
            core.classList.remove("listening-

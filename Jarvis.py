import streamlit as st
import os
import pytz
from datetime import datetime
import yfinance as yf
from gtts import gTTS
from audio_recorder_streamlit import audio_recorder

# Configuración inicial de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Centro de Control",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados (Estética Holográfica Neón / Modo Oscuro Stark)
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #00ffcc;
    }
    .sidebar .sidebar-content {
        background-color: #05070b;
    }
    h1, h2, h3 {
        color: #00ffff !important;
        font-family: 'Courier New', monospace;
    }
    .stMetric {
        background-color: rgba(0, 255, 204, 0.05);
        border: 1px solid #00ffcc;
        padding: 10px;
        border-radius: 5px;
    }
    .holo-box {
        border: 1px solid #00ffff;
        padding: 15px;
        border-radius: 8px;
        background: rgba(0, 255, 255, 0.03);
        box-shadow: 0 0 15px rgba(0, 255, 255, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL: TALLER DE BUIN & CONFIGURACIÓN STARK ---
st.sidebar.markdown("### ⚡ Enlace Satelital Stark")
satellite_link = st.sidebar.toggle("Activar Enlace Satelital", value=True)

if satellite_link:
    st.sidebar.info("📡 Enrutando vía Constelación Satelital Stark-1 (Banda Ku). Ubicación: Buin, Chile.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 2. Biblioteca de Voz (ElevenLabs)")
eleven_api_key = st.sidebar.text_input("ElevenLabs API Key:", type="password")

voice_option = st.sidebar.selectbox(
    "Seleccionar Voz Cinematográfica:",
    ["Antoni (Suave / Sofisticada)", "Adam (Profunda / Narrativa)", "Arnold (Imponente / Varonil)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 3. Visualizador de Voz (Holograma)")
st.sidebar.markdown("🟢 *Estado del Núcleo: Operativo*")

# --- PANEL PRINCIPAL ---
st.markdown("# 🛡️ J.A.R.V.I.S. v4.0 - Interfaz Táctica Principal")
st.markdown("---")

# Columnas de Telemetría y Estado
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="holo-box">', unsafe_allow_html=True)
    st.metric(label="Zona Operativa", value="Buin, CL", delta="Conectado")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="holo-box">', unsafe_allow_html=True)
    chile_tz = pytz.timezone('America/Santiago')
    current_time = datetime.now(chile_tz).strftime('%H:%M:%S')
    st.metric(label="Hora Local (Buin)", value=current_time, delta="Sincronizado")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="holo-box">', unsafe_allow_html=True)
    st.metric(label="Subsistema de Voz", value="ElevenLabs" if eleven_api_key else "gTTS (Respaldo)", delta="Listo")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("\n")

# --- INTERACCIÓN CON EL USUARIO ---
st.markdown("### 💬 Canal de Comunicación con J.A.R.V.I.S.")
user_query = st.text_input("Escriba su comando o consulta para el sistema:")

if user_query:
    st.markdown(f"> **Comando recibido:** {user_query}")
    response_text = f"Entendido, Jefa. Procesando instrucción desde el taller de Buin con los protocolos de seguridad activos."
    st.success(response_text)
    
    # Simulación de síntesis de voz (Compatible con ElevenLabs o gTTS de respaldo)
    if eleven_api_key:
        st.info("🎙️ [Simulación] Generando audio de alta gama mediante ElevenLabs API Key.")
    else:
        tts = gTTS(text=response_text, lang='es')
        audio_path = "temp_response.mp3"
        tts.save(audio_path)
        st.audio(audio_path, format="audio/mp3", autoplay=True)

st.markdown("---")
st.markdown("*Sistema desarrollado bajo especificaciones de la iniciativa N.O.V.A. / J.A.R.V.I.S. — Buin, Chile.*")

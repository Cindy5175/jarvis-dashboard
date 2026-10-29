import streamlit as st
import os
import pytz
from datetime import datetime
import pandas as pd
import numpy as np
from gtts import gTTS
from audio_recorder_streamlit import audio_recorder

# Configuración inicial de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS avanzados (Estética Holográfica Neón / Redes Neuronales Stark)
st.markdown("""
    <style>
    .main {
        background-color: #070913;
        color: #00ffcc;
        font-family: 'Courier New', monospace;
    }
    .sidebar .sidebar-content {
        background-color: #030408;
    }
    h1, h2, h3 {
        color: #00ffff !important;
        text-shadow: 0 0 10px rgba(0, 255, 255, 0.5);
    }
    .holo-card {
        border: 1px solid #00ffff;
        padding: 20px;
        border-radius: 10px;
        background: rgba(0, 255, 255, 0.02);
        box-shadow: 0 0 20px rgba(0, 255, 255, 0.15);
        margin-bottom: 20px;
    }
    .terminal-box {
        background-color: #03050a;
        border-left: 3px solid #00ffcc;
        padding: 15px;
        font-family: 'Courier New', monospace;
        color: #00ffcc;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL: NÚCLEO Y ENLACE STARK ---
st.sidebar.markdown("### ⚡ Enlace Satelital Stark")
satellite_link = st.sidebar.toggle("Activar Enlace Satelital", value=True)

if satellite_link:
    st.sidebar.info("📡 Enrutando vía Constelación Satelital Stark-1 (Banda Ku). Ubicación: Buin, Chile.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎙️ Subsistema de Voz (ElevenLabs)")
eleven_api_key = st.sidebar.text_input("ElevenLabs API Key:", type="password")

voice_option = st.sidebar.selectbox(
    "Seleccionar Voz Cinematográfica:",
    ["Antoni (Suave / Sofisticada)", "Adam (Profunda / Narrativa)", "Arnold (Imponente / Varonil)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🌐 Estado de Red Neuronal")
st.sidebar.markdown("🟢 *Flujo de Datos: Estable (99.8%)*")
st.sidebar.markdown("🔵 *Latencia Global: 1.2ms*")

# --- PANEL PRINCIPAL ---
st.markdown("# 🛡️ J.A.R.V.I.S. v4.0 — Centro de Mando Táctico")
st.markdown("---")

# Fila 1: Métricas holográficas
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.metric(label="Zona Operativa", value="Buin, CL", delta="Seguro / Encriptado")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    chile_tz = pytz.timezone('America/Santiago')
    current_time = datetime.now(chile_tz).strftime('%H:%M:%S')
    st.metric(label="Sincronización Temporal", value=current_time, delta="Precisión Óptima")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.metric(label="Motor de Síntesis", value="ElevenLabs" if eleven_api_key else "gTTS (Respaldo)", delta="Activo")
    st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL DE FLUJO DE DATOS Y TELEMETRÍA (Estilo Red Neuronal) ---
st.markdown("### 📊 Telemetría de Flujo y Redes en Tiempo Real")
chart_data = pd.DataFrame(
    np.random.randn(20, 3) * [10, 5, 2] + [100, 50, 25],
    columns=['Flujo Satelital', 'Actividad Neuronal', 'Ancho de Banda']
)
st.line_chart(chart_data, color=["#00ffff", "#00ffcc", "#ff007f"])

# --- INTERACCIÓN CON EL USUARIO ---
st.markdown("### 💬 Interfaz de Comandos Vocales y Texto")
user_query = st.text_input("Ingrese directiva para J.A.R.V.I.S.:")

if user_query:
    st.markdown(f'<div class="terminal-box">> [COMANDO REGISTRADO]: {user_query}</div>', unsafe_allow_html=True)
    response_text = f"Procesando directiva con los protocolos de la red central en Buin, Jefa."
    st.success(response_text)
    
    if eleven_api_key:
        st.info("🎙️ [ElevenLabs] Sintetizando audio cinematográfico con la voz seleccionada.")
    else:
        tts = gTTS(text=response_text, lang='es')
        audio_path = "temp_response.mp3"
        tts.save(audio_path)
        st.audio(audio_path, format="audio/mp3", autoplay=True)

st.markdown("---")
st.markdown("*Iniciativa N.O.V.A. / Arquitectura de Inteligencia Autónoma — Buin, Chile.*")

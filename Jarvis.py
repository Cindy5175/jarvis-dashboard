import streamlit as st
import datetime
import sqlite3
from gtts import gTTS
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

# --- ESTADO DE VOZ ---
if "ultimo_texto_hablado" not in st.session_state:
    st.session_state.ultimo_texto_hablado = "Sistemas operativos y listos, jefa."

def hablar_como_jarvis(texto):
    st.session_state.ultimo_texto_hablado = texto
    if not st.session_state.get("toggle_voz_jarvis", True):
        return
    try:
        tts = gTTS(text=texto, lang='es', slow=False)
        audio_file = "jarvis_voz.mp3"
        tts.save(audio_file)
        st.audio(audio_file, format='audio/mp3', autoplay=True)
    except Exception as e:
        print(f"Error en voz: {e}")

# --- AUTENTICACIÓN ---
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

# --- HORA CHILE ---
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
hora_actual = datetime.datetime.now(tz_chile).hour
saludo_actual = "Buenos días" if 0 <= hora_actual < 12 else ("Buenas tardes" if 12 <= hora_actual < 20 else "Buenas noches")

# --- BASE DE DATOS ---
DB_NAME = "jarvis_bunker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tareas (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alertas (id INTEGER PRIMARY KEY AUTOINCREMENT, mensaje TEXT, nivel TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS biometria (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hr INTEGER, spo2 INTEGER, sueno TEXT)''')
    conn.commit()
    conn.close()

init_db()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Núcleo búnker sincronizado. ¿Qué ordenamos hoy?"}
    ]

# --- ENCABEZADO ---
st.markdown("""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h2 style="margin: 0; padding: 0; font-size: 1.5rem; text-align: center !important; color: #00d2ff !important;">J.A.R.V.I.S IA</h2>
        <p style="margin: 0; font-family: monospace; font-size: 0.75rem; color: #00d2ff !important; text-align: center !important;">[ STARK INDUSTRIES // NODO BUIN, CHILE ]</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# --- 3 COLUMNAS ---
col_izq, col_centro, col_der = st.columns([1, 2.2, 1])

with col_izq:
    st.markdown("### 🌐 SECTOR ALPHA")
    with st.expander("🛡️ Blindaje & Alertas", expanded=True):
        st.markdown("• **Zona Familia:** Blindada\n• **Zona Médica:** Protegida\n• **Finanzas:** Monitoreo activo")

with col_centro:
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin:0; font-size: 1.1rem; color: #00d2ff !important;'>🛰️ Ojo de Dios & Telemetría ISS</h4>", unsafe_allow_html=True)
    tab_ojo, tab_iss = st.tabs(["🗺️ Mapa Táctico", "🌍 ISS Directo"])
    with tab_ojo:
        st.link_button("🌐 Abrir Visor Satelital (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
    with tab_iss:
        st.video("https://www.youtube.com/watch?v=alJMoaKpV_E")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(f"<span style='color: #00d2ff !important;'>{m['content']}</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if prompt_usuario := st.chat_input("Escriba su mensaje..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
        respuesta = f"Entendido, jefa. Procesando instrucción en el núcleo central..."
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
        hablar_como_jarvis(respuesta)
        st.rerun()

with col_der:
    st.markdown("### ⚡ SECTOR BETA")
    with st.expander("🎙️ Núcleo de Voz J.A.R.V.I.S.", expanded=True):
        st.toggle("Activar Síntesis de Voz Varonil", value=True, key="toggle_voz_jarvis")
        if st.button("🔊 Repetir Último Comando", use_container_width=True):
            hablar_como_jarvis(st.session_state.ultimo_texto_hablado)
            st.success("Emitiendo audio...")

    with st.expander("🕵️‍♂️ Módulo OSINT & Monitoreo Global", expanded=True):
        st.markdown("Recopilación y análisis táctico de fuentes abiertas[cite: 1]:")
        st.link_button("🌐 OSINT Framework", "https://osintframework.com", use_container_width=True)
        st.link_button("✈️ Flightradar24", "https://www.flightradar24.com", use_container_width=True)
        st.link_button("🚢 MarineTraffic", "https://www.marinetraffic.com", use_container_width=True)
        st.link_button("🔍 Shodan", "https://www.shodan.io", use_container_width=True)

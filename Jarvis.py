import streamlit as st
import datetime
import sqlite3
from gtts import gTTS
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES STARK & CAJA DE CHAT ---
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

        .stChatInputContainer {
            border: 1.5px solid #00d2ff !important;
            border-radius: 10px !important;
            background-color: rgba(0, 210, 255, 0.05) !important;
            box-shadow: 0 0 10px rgba(0, 210, 255, 0.15) !important;
        }
        .stChatInputContainer textarea {
            color: #00d2ff !important;
            font-family: monospace !important;
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
                hablar_como_jarvis("Acceso concedido. Bienvenida, jefa. Menos mal recordó la contraseña.")
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
    
    c.execute("SELECT COUNT(*) FROM tareas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Revisar exámenes médicos y electrolitos",))
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Monitorear nodo operativo en Buin",))
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

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. El nodo de Buin está operativo... aunque alguien tenía que venir a vigilarlo."}
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

# --- 3 COLUMNAS TÁCTICAS ---
col_izq, col_centro, col_der = st.columns([1, 2.2, 1])

# ==========================================
# COLUMNA IZQUIERDA: SECTOR ALPHA
# ==========================================
with col_izq:
    st.markdown("### 🌐 SECTOR ALPHA")
    
    with st.expander("🛡️ Blindaje & Alertas", expanded=True):
        st.markdown("• **Zona Familia:** Blindada\n• **Zona Médica:** Protegida\n• **Finanzas:** Monitoreo activo")

    with st.expander("⌚ Mi Band (Telemetría Médica)", expanded=True):
        hr_input = st.number_input("Frecuencia Cardíaca (BPM):", min_value=40, max_value=200, value=72)
        spo2_input = st.number_input("Oxígeno SpO2 (%):", min_value=70, max_value=100, value=98)
        sueno_input = st.text_input("Calidad de Sueño / Notas:", value="Óptimo - 7.5 hrs")
        if st.button("💾 Guardar Datos Mi Band", use_container_width=True):
            st.success("¡Registrado con éxito!")
            hablar_como_jarvis("Datos biométricos guardados. Espero que al menos haya descansado.")

    with st.expander("📝 Tareas del Búnker"):
        nueva_tarea = st.text_input("Nueva tarea rápida:", key="inp_tarea")
        if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
            add_db_tarea(nueva_tarea)
            st.rerun()
        for tid, t in get_db_tareas():
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"• {t}")
            with c2:
                if st.button("❌", key=f"del_{tid}"):
                    delete_db_tarea(tid)
                    st.rerun()

    with st.expander("🌤️ Clima Local (Buin)", expanded=True):
        st.markdown("• **Condición:** Despejado\n• **Temperatura:** 21°C\n• **Humedad:** 45%")

# ==========================================
# COLUMNA CENTRAL: OJO DE DIOS, CÁMARA & CHAT SARCÁSTICO
# ==========================================
with col_centro:
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin:0; font-size: 1.1rem; color: #00d2ff !important;'>🛰️ Ojo de Dios & Telemetría ISS</h4>", unsafe_allow_html=True)
    tab_ojo, tab_iss1, tab_iss2, tab_aurora = st.tabs(["🗺️ Mapa Táctico", "🌍 ISS Diurno", "🛰️ Tierra 24/7", "🌌 Auroras"])
    with tab_ojo:
        st.link_button("🌐 Abrir Visor Satelital (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
    with tab_iss1:
        st.video("https://www.youtube.com/watch?v=alJMoaKpV_E")
    with tab_iss2:
        st.video("

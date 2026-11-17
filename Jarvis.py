import streamlit as st
import datetime
import sqlite3
import os
import sys

# Importaciones de las IA
from zhipuai import ZhipuAI
import google.generativeai as genai

# --- 1. CONFIGURACION DE PAGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INICIALIZACION DE SESSION_STATE ---
if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"

# --- CONFIGURACIÓN DE LLAVES Y CLIENTES PARA LOS 3 MOTORES ---
API_KEY_GLM = "8477d61a32664b00aac4d04904c0fe09.4rcBmMQdqChiktB1"
API_KEY_GEMINI = "TU_API_KEY_DE_GEMINI"  # Inserta tu clave de Gemini si la usas
API_KEY_ZAPIA = "TU_API_KEY_DE_ZAPIA"    # Inserta tu clave de ZapIA si la usas

# Inicialización de clientes
client_glm = ZhipuAI(api_key=API_KEY_GLM) if API_KEY_GLM else None

if API_KEY_GEMINI and API_KEY_GEMINI != "TU_API_KEY_DE_GEMINI":
    genai.configure(api_key=API_KEY_GEMINI)

# --- BASE DE DATOS SQLITE ---
def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS misiones ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "tarea TEXT NOT NULL, "
        "estado TEXT DEFAULT 'Pendiente')"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS memory ("
        "key_id TEXT PRIMARY KEY, "
        "fact_text TEXT, "
        "category TEXT)"
    )
    conn.commit()
    conn.close()

init_db()

class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path
    def remember_fact(self, key_id: str, fact_text: str):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
            (key_id, fact_text, "general")
        )
        conn.commit()
        conn.close()

jarvis_mem = JarvisMemory()

def agregar_mision(tarea):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
    conn.commit()
    conn.close()

def obtener_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tarea, estado FROM misiones")
    rows = cursor.fetchall()
    conn.close()
    return rows

def limpiar_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM misiones")
    conn.commit()
    conn.close()

# ZONA HORARIA CHILENA
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "assistant",
            "content": (
                f"{saludo_actual}, jefa. Nodo Buin en línea, enlazado en paralelo a "
                "GLM, Google Gemini y ZapIA. ¿Qué dominamos hoy?"
            )
        }
    ]

# --- ESTILOS VISUALES: REACTOR ARC ESTILO STARK & BOTONES COMPACTOS ---
estilos_css = """
    <style>
        .stApp { background-color: #060913 !important; color: #00f3ff !important; font-family: monospace; }
        p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
       
        /* AJUSTE FINO DE TEXTOS EN BARRA LATERAL Y MINI MÓDULOS */
        [data-testid="stSidebar"] h3 { font-size: 1.05rem !important; }
        [data-testid="stSidebar"] h4 { font-size: 0.85rem !important; margin-bottom: 4px !important; }
        [data-testid="stSidebar"] summary p { font-size: 0.80rem !important; }
       
        .stButton>button {
            background-color: #00f3ff !important;
            border: 1.5px solid #00f3ff !important;
            font-weight: bold;
            font-family: monospace;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
            width: 100%;
            border-radius: 6px;
            padding: 5px 10px !important;
        }
        .stButton>button p, .stButton>button span { color: #060913 !important; font-size: 0.78rem !important; }
        .stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.9); }
        .stButton>button:hover p, .stButton>button:hover span { color: #ffffff !important; }

        /* REACTOR ARC ESTILO STARK - INVERTIDO */
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 10px;
        }
        .arc-ring {
            width: 65px;
            height: 65px;
            border: 2.5px solid #00f3ff;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, rgba(0,243,255,0.4) 0%, #060913 75%);
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.8), inset 0 0 10px rgba(0, 243, 255, 0.6);
            margin-bottom: 8px;
        }
        .arc-triangle-inverted {
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-top: 20px solid #00f3ff;
            filter: drop-shadow(0 0 8px #00f3ff);
        }
       
        /* BOTÓN TÁCTICO HTML COMPACTO */
        .tactical-link-btn {
            display: block;
            width: 100%;
            background-color: #00f3ff;
            color: #060913 !important;
            text-align: center;
            padding: 6px 10px;
            margin: 5px 0;
            border-radius: 5px;
            font-size: 0.76rem !important;
            font-weight: bold;
            text-decoration: none;
            font-family: monospace;
            box-shadow: 0 0 8px rgba(0, 243, 255, 0.5);
            transition: all 0.25s ease;
        }
        .tactical-link-btn:hover {
            background-color: #0088cc;
            color: #ffffff !important;
            box-shadow: 0 0 12px rgba(0, 243, 255, 0.9);
        }

        .holo-brain-box {
            border: 1.5px solid #00f3ff;
            background: linear-gradient(135deg, #0a1128 0%, #060913 100%);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.3), inset 0 0 10px rgba(0, 243, 255, 0.15);
            margin: 0 auto 20px auto;
            max-width: 800px;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""
st.markdown(estilos_css, unsafe_allow_html=True)

# --- 1. PANTALLA DE BLOQUEO DE SEGURIDAD ---
if not st.session_state.get("autorizado", False):
    st.markdown(
        '<div style="text-align: center; margin-top: 50px;">'
        '<h2 style="color: #00f3ff;">ACCESO RESTRINGIDO - NODO BUIN</h2>'
        '<p style="color: #00f3ff; opacity: 0.8; font-size: 0.85rem;">INGRESE PIN DE SEGURIDAD PARA ACTIVAR LA ARMADURA</p>'
        '</div>',
        unsafe_allow_html=True
    )
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button("Desbloquear Sistema")
        if btn_entrar:
            if pin_input.strip() == PIN_SECRETO:
                st.session_state.autorizado = True
                st.success("Acceso concedido. Bienvenido de nuevo, jefa.")
                st.rerun()
            else:
                st.error("PIN incorrecto. Acceso denegado.")
    st.stop()

# --- 2. PANEL LATERAL OCULTO (ARSENAL DE MÓDULOS COMPLETO) ---
with st.sidebar:
    st.markdown("### 🛡️ Arsenal de Módulos")
    st.markdown("---")
   
    if st.button("🔒 Bloquear Sistema", use_container_width=True):
        st.session_state.autorizado = False
        st.rerun()
       
    if st.button("🔄 Reinicio Total", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🧠 Selector de Núcleo (IA)")
    nuevo_nucleo = st.radio(
        "Seleccionar Asistente Activo:",
        ["JARVIS", "VIERNES", "NOVA"],
        index=["JARVIS", "VIERNES", "NOVA"].index(st.session_state.nucleo_activo),
        label_visibility="collapsed"
    )
    if nuevo_nucleo != st.session_state.nucleo_activo:
        st.session_state.nucleo_activo = nuevo_nucleo
        st.success(f"Núcleo cambiado a {nuevo_nucleo}.")
        st.rerun()

    st.markdown("---")
    st.markdown("#### 💾 Memoria y Datos")
    with st.expander("Gestionar Memoria SQLite", expanded=False):
        dato_mem = st.text_input("Dato a guardar:", placeholder="Ej: Preferencia...")
        if st.button("Guardar en Memoria", use_container_width=True):
            if dato_mem.strip():
                jarvis_mem.remember_fact(f"mem_{datetime.datetime.now().timestamp()}", dato_mem.strip())
                st.success("¡Memoria guardada!")

    st.markdown("---")
    st.markdown("#### 📋 Misiones Tácticas")
    with st.expander("Base de Datos Misiones", expanded=False):
        nueva_tarea = st.text_input("Nueva Misión:", placeholder="Ej: Revisar nodos...")
        if st.button("Registrar Tarea", use_container_width=True):
            if nueva_tarea.strip():
                agregar_mision(nueva_tarea.strip())
                st.success("¡Misión registrada!")
                st.rerun()
        misiones_guardadas = obtener_misiones()
        if misiones_guardadas:
            for m_id, m_text, m_est in misiones_guardadas:
                st.markdown(f"- `{m_text}`")
            if st.button("Limpiar Misiones", use_container_width=True):
                limpiar_misiones()
                st.rerun()

    st.markdown("---")
    st.markdown("#### 🎧 Frecuencias de Enfoque")
    with st.expander("Deep Work & Música IA", expanded=False):
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.youtube.com/watch?v=6pUPGG7LLEc" target="_blank">'
            '🎧 CEO Mode (Deep Work)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.youtube.com/watch?v=jC-Xb4XNMlE" target="_blank">'
            '🚀 Futuristic Garage Beats'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.youtube.com/watch?v=QBOZ1CaUPYE" target="_blank">'
            '⚡ Hyperfocus Mode'
            '</a>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### 📷 Videovigilancia y Cámaras")
    with st.expander("Cámaras en Vivo / Satélite", expanded=False):
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.skylinewebcams.com/es/webcam/chile.html" target="_blank">'
            'Stgo / Chile (Skyline)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://liveworldwebcams.com/es/concepcion-webcam/" target="_blank">'
            'Concepción Webcam'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.windy.com/es/-C%C3%A1maras-web/webcams?39.880,-5.449,7" target="_blank">'
            'Windy Radars & Cams'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.earthcam.com/usa/texas/galveston/port/?cam=pg_terminal28" target="_blank">'
            'Galveston Port, Texas'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.skylinewebcams.com/es/webcam/espana/comunidad-de-madrid/madrid/puerta-del-sol-tio-pepe.html" target="_blank">'
            'Puerta del Sol, Madrid'
            '</a>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### 🛰️ Telemetría Global & Satélites")
    with st.expander("Sistemas Satelitales y Rastreo", expanded=False):
        st.markdown(
            '<a class="tactical-link-btn" href="https://osirisai.live/" target="_blank">'
            'OSIRIS (Ojo de Dios)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.planet.com/" target="_blank">'
            'PlanetEar (Satélites)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://worldview.earthdata.nasa.gov/" target="_blank">'
            'NASA Worldview'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.n2yo.com/" target="_blank">'
            'N2YO (Órbita en Vivo)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.flightradar24.com/" target="_blank">'
            'Flightradar24 (Aéreo)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical

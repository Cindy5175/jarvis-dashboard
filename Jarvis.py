import streamlit as st
import datetime
import sqlite3
import requests

# --- 1. CONFIGURACIÓN DE PÁGINA (SIEMPRE PRIMERO) ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Importación segura de Google Generative AI
try:
    import google.generativeai as genai
    api_key = ""
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    elif "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    if api_key:
        genai.configure(api_key=api_key)
except ImportError:
    genai = None

# --- INICIALIZACIÓN DE BASE DE DATOS SQLITE ---
fn_db = "jarvis_misiones.db"

def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memoria_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rol TEXT,
            contenido TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- ESTILOS VISUALES 100% AZUL NEÓN ELÉCTRICO (#00f3ff) ---
st.markdown(
    """
    <style>
        .stApp { background-color: #060913 !important; color: #00f3ff !important; }
        p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
        .stButton>button {
            color: #060913 !important;
            background-color: #00f3ff !important;
            border: 1.5px solid #00f3ff !important;
            font-weight: bold;
            font-family: monospace;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
            width: 100%;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# --- ESTADO DE SESIÓN & CONTROL DE ACCESO (PIN: 2805) ---
if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "Buenos días, jefa. Protocolo de seguridad máxima activo en Nodo Buin."}
    ]

PIN_SECRETO = "2805"

# =========================================================================
# 1. PANTALLA DE BLOQUEO
# =========================================================================
if not st.session_state.autorizado:
    st.markdown(
        """
        <div style="text-align: center; margin-top: 50px;">
            <h2 style="color: #00f3ff; font-family: monospace;">🔒 ACCESO RESTRINGIDO - NODO BUIN</h2>
            <p style="color: #00f3ff; opacity: 0.8; font-size: 0.85rem;">INGRESE PIN DE SEGURIDAD</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto Numérico:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button("🛡️ Desbloquear Armadura")
            
            if btn_entrar:
                if pin_input.strip() == PIN_SECRETO:
                    st.session_state.autorizado = True
                    st.success("⚡ Acceso concedido. Desplegando J.A.R.V.I.S...")
                    st.rerun()
                else:
                    st.error("❌ PIN incorrecto. Acceso denegado.")
    st.stop()

# =========================================================================
# 2. SISTEMA DESBLOQUEADO
# =========================================================================
st.markdown("<h2 style='text-align: center;'>J.A.R.V.I.S IA — NODO BUIN</h2>", unsafe_allow_html=True)
st.markdown("---")

# Panel lateral con opciones rápidas
with st.sidebar:
    st.markdown("### 🌐 CONTROL TÁCTICO")
    if st.button("🔒 Bloquear Sistema", use_container_width=True):
        st.session_state.autorizado = False
        st.rerun()

# Caja de chat principal
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

prompt_usuario = st.chat_input("Escríbele a JARVIS...")

if prompt_usuario:
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(f"<span>{prompt_usuario}</span>", unsafe_allow_html=True)
    
    respuesta_ia = ""
    query_lower = prompt_usuario.lower()
    
    if "escaneo" in query_lower or "computador" in query_lower:
        respuesta_ia = "Jefa, escaneo del Nodo Buin en curso. Diagnóstico: Red estable, 0 vulnerabilidades y CPU al 14%. Todo en orden."
    elif "hola" in query_lower or "jarvis" in query_lower:
        respuesta_ia = "Aquí sigo, jefa, aguantando tus ocurrencias desde el nodo de Buin. ¿Qué se te ofrece?"
    else:
        respuesta_ia = f"Orden procesada, jefa. Analizando '{prompt_usuario}' desde el Nodo Buin sin novedad."

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
    st.rerun()

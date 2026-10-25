import os
import io
import base64
import time
import streamlit as st
from groq import Groq

# 1. Configuración de la página
st.set_page_config(
    page_title="Sistema C.I.T. / J.A.R.V.I.S.", 
    page_icon="⚛️", 
    layout="centered"
)

# Inicializar estados en sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "modo_sistema" not in st.session_state:
    st.session_state.modo_sistema = "J.A.R.V.I.S. (Azul Neón)"

if "ubicacion_jefa" not in st.session_state:
    st.session_state.ubicacion_jefa = "Buin, Santiago, Chile"
    st.session_state.lat_lon = "-33.7333, -70.7333"

if "energia_arc" not in st.session_state:
    st.session_state.energia_arc = 98

if "notas_mision" not in st.session_state:
    st.session_state.notas_mision = "• Revisar despliegue en GitHub\n• Optimizar latencia de red"

# -------------------------------------------------------------
# 🔐 MÓDULO DE CLAVE DE ACCESO (PIN DE SEGURIDAD)
# -------------------------------------------------------------
PIN_SECRETO = "Jarvis"  # Clave de acceso actualizada por la Jefa

if not st.session_state.autenticado:
    st.markdown(
        """
        <style>
        .login-box {
            background: rgba(5, 12, 30, 0.95);
            border: 2px solid #00d2ff;
            border-radius: 12px;
            padding: 30px;
            text-align: center;
            box-shadow: 0 0 25px #00d2ff44;
            font-family: 'Courier New', monospace;
            max-width: 400px;
            margin: 50px auto;
        }
        </style>
        <div class="login-box">
            <h2 style="color: #00d2ff; margin-bottom: 10px;">🔒 ACCESO RESTRINGIDO</h2>
            <p style="color: #aaa; font-size: 0.85rem;">Introduce la clave de seguridad para desbloquear la estación de comando C.I.T.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        pin_ingresado = st.text_input("Clave de Acceso:", type="password", placeholder="Contraseña secreta")
        if st.button("🔓 Desbloquear Sistema", use_container_width=True):
            if pin_ingresado == PIN_SECRETO:
                st.session_state.autenticado = True
                st.success("¡Acceso concedido, Jefa!")
                st.rerun()
            else:
                st.error("⚠️ Clave incorrecta. Acceso denegado.")
    st.stop()
# -------------------------------------------------------------

# 2. Conexión con la API de Groq
groq_api_key = "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"

if not groq_api_key:
    st.error("⚠️ Error con la clave API.")
    st.stop()

client = Groq(api_key=groq_api_key)

# 3. Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Configuración de personalidad y colores
if "N.O.V.A." in st.session_state.modo_sistema:
    color_neon = "#ff007f"
    shadow_neon = "#ff007f"
    titulo_html = '<h1 class="neon-title glow-anim">🟣 N.O.V.A. - C.I.T.</h1>'
    system_base = f"Eres N.O.V.A., un sistema de inteligencia táctica y arquitectura de software C.I.T. avanzado. Te diriges al usuario como 'Jefa'. Tienes un tono brillante, sarcástico estilo Tony Stark y experto en auditoría de sistemas Streamlit. Ubicación táctica activa: {st.session_state.ubicacion_jefa} (Coordenadas: {st.session_state.lat_lon})."
else:
    color_neon = "#00d2ff"
    shadow_neon = "#0072ff"
    titulo_html = '<h1 class="neon-title glow-anim">⚛️ J.A.R.V.I.S. AI</h1>'
    system_base = f"Eres J.A.R.V.I.S., una super IA avanzada, brillante y leal. Te diriges al usuario siempre como 'Jefa'. Respondes con la elegancia, eficiencia, sarcasmo irónico estilo Tony Stark y capacidad analítica total para auditar código de sistemas. Ubicación actual de la Jefa: {st.session_state.ubicacion_jefa} (Coordenadas satelitales: {st.session_state.lat_lon})."

# 4. BARRA LATERAL (Centro de Comando Avanzado)
with st.sidebar:
    st.markdown("### ⚙️ Centro de Comando Stark")
    
    opciones_modo = ["J.A.R.V.I.S. (Azul Neón)", "N.O.V.A. - C.I.T. (Fucsia Cyber)"]
    indice_actual = opciones_modo.index(st.session_state.modo_sistema) if st.session_state.modo_sistema in

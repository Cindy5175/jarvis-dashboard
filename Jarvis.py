import streamlit as st
import google.generativeai as genai

# Configuración de la página (Manteniendo el diseño original)
st.set_page_config(
    page_title="Nodo Buin - J.A.R.V.I.S.",
    page_icon="🛰️",
    layout="wide"
)

# Estilo visual original de la interfaz
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stTextInput input {
        color: #00ffcc !important;
        background-color: #1a1c23 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CONFIGURACIÓN DE J.A.R.V.I.S. (Inteligente y Sarcástico)
# ---------------------------------------------------------
JARVIS_SYSTEM_PROMPT = """
Eres J.A.R.V.I.S., el asistente virtual de la jefa en el Nodo Buin.
Tienes una personalidad sofisticada, varonil, sumamente inteligente y con un toque de sarcasmo refinado.

DIRECTRICES:
1. NUNCA respondas con frases evasivas enlatadas cuando se te hagan preguntas de conocimiento general, historia o matemáticas.
2. Explica los temas solicitados con absoluta precisión, manteniendo el tono de alta tecnología y un humor sutil cuando la pregunta sea muy elemental.
"""

if "gemini_model" not in st.session_state:
    st.session_state.gemini_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=JARVIS_SYSTEM_PROMPT
    )

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Buenos días, jefa. Protocolo de seguridad activo en Nodo Buin. Sistemas operativos y listos."}
    ]

# ---------------------------------------------------------
# FORMATO Y LAYOUT ORIGINAL (Módulos a la izquierda / Limpio)
# ---------------------------------------------------------
st.title("🛰️ NODO BUIN // CENTRAL TÁCTICA J.A.R.V.I.S.")
st.markdown("---")

# Distribución original: Módulos de control a la izquierda, consola principal a la derecha (o viceversa según prefieras el flujo clásico)
col_modulos, col_chat = st.columns([1, 2])

with col_modulos:
    st.subheader("🌐 Módulos del Sistema")
    st.markdown("""
        * **Estado de Enlace:** En línea [Seguro]
        * **Módulo Osiris:** Activo
        * **Mapa Táctico Satelital:** Sincronizado
    """)
    st.info("📡 Conexión de audio por botones operando de forma estable.")

with col_chat:
    st.subheader("💬 Consola de Comunicación")
    
    # Historial de mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de comandos
    if prompt_usuario := st.chat_input("Escríbele o háblale a JARVIS..."):
        st.session_state.messages.append({"role": "user", "content": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        with st.chat_message("assistant"):
            with st.spinner("Procesando consulta..."):
                try:
                    response = st.session_state.gemini_model.generate_content(prompt_usuario)
                    respuesta_jarvis = response.text
                except Exception as e:
                    respuesta_jarvis = f"Error en el enlace de datos, jefa: {e}"
                
                st.markdown(respuesta_jarvis)
                
        st.session_state.messages.append({"role": "assistant", "content": respuesta_jarvis})

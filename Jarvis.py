import streamlit as st
import google.generativeai as genai

# Configuración de la página para que luzca como una central táctica
st.set_page_config(
    page_title="Nodo Buin - J.A.R.V.I.S.",
    page_icon="🛰️",
    layout="wide"
)

# Estilo visual general (Modo oscuro / Táctico)
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
# CONFIGURACIÓN DE LA INTELIGENCIA DE J.A.R.V.I.S.
# ---------------------------------------------------------
# System prompt para asegurar que entregue conocimiento real (Historia, Matemáticas, etc.) con sarcasmo.
JARVIS_SYSTEM_PROMPT = """
Eres J.A.R.V.I.S., el asistente virtual de la jefa en el Nodo Buin.
Tienes una personalidad sofisticada, varonil, sumamente inteligente y con un toque de sarcasmo refinado.

DIRECTRICES CRÍTICAS:
1. NUNCA respondas con frases evasivas predeterminadas ni digas que "no sabes" cuando se te hagan preguntas de conocimiento general, historia (como Arturo Prat) o matemáticas (como binomios).
2. Explica los temas solicitados con absoluta precisión técnica, científica o histórica, desglosando los datos paso a paso.
3. Mantén el tono de alta tecnología y hazle notar a la jefa con elegancia y humor sutil cuando una pregunta sea demasiado elemental para tu procesador.
"""

# Inicializar modelo de Gemini (asegúrate de tener tu API Key configurada en los secretos de Streamlit o entorno)
if "gemini_model" not in st.session_state:
    # Si usas st.secrets para la API key, puedes configurarla aquí:
    # genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    st.session_state.gemini_model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=JARVIS_SYSTEM_PROMPT
    )

# Historial de chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Buenos días, jefa. Protocolo de seguridad máxima activo en Nodo Buin. Sistemas operativos y listos para procesar cualquier consulta histórica o matemática."}
    ]

# ---------------------------------------------------------
# INTERFAZ VISUAL (LAYOUT TÁCTICO)
# ---------------------------------------------------------
st.title("🛰️ NODO BUIN // CENTRAL TÁCTICA J.A.R.V.I.S.")
st.markdown("---")

# Columnas principales: Izquierda (Chat/Comandos), Derecha (Mapa Táctico y Osiris)
col_chat, col_táctico = st.columns([2, 1])

with col_táctico:
    st.subheader("🌐 Mapa Táctico Satelital")
    st.markdown("""
        * **Estado de Enlace:** En línea [Seguro]
        * **Módulo Osiris:** Monitoreo activo
        * **Planeta / Órbita:** Sincronizado (PlanetEar)
    """)
    # Simulación visual de métricas del mapa
    st.metric(label="Intrusiones Bloqueadas", value="0", delta="Seguro")
    st.info("📡 Coordenadas de red estables. Conexión de audio por botones operando sin interferencias.")

with col_chat:
    st.subheader("💬 Consola de Comunicación")
    
    # Mostrar el historial de mensajes en pantalla
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de texto para JARVIS (simulando también el comando o entrada de micrófono)
    if prompt_usuario := st.chat_input("Escríbele o háblale a JARVIS..."):
        # Añadir mensaje de la usuaria al historial
        st.session_state.messages.append({"role": "user", "content": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        # Generar respuesta inteligente con el modelo
        with st.chat_message("assistant"):
            with st.spinner("Analizando consulta desde el Nodo Buin..."):
                try:
                    # Enviar el mensaje al modelo con el system prompt configurado
                    response = st.session_state.gemini_model.generate_content(prompt_usuario)
                    respuesta_jarvis = response.text
                except Exception as e:
                    respuesta_jarvis = f"Error en el enlace de datos del sistema, jefa: {e}"
                
                st.markdown(respuesta_jarvis)
                
        # Guardar respuesta en el historial
        st.session_state.messages.append({"role": "assistant", "content": respuesta_jarvis})

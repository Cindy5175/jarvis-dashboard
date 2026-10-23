import os
import streamlit as st
from groq import Groq

# 1. Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S AI autónoma", 
    page_icon="⚛️", 
    layout="centered"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .neon-title {
        color: #00d2ff;
        text-shadow: 0 0 10px #00d2ff, 0 0 20px #00d2ff, 0 0 40px #0072ff;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 2.3rem;
        text-align: center;
        margin-top: -20px;
        margin-bottom: 25px;
    }
    .block-container {
        max-width: 750px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    .stChatInput {
        max-width: 750px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado centrado con Reactor Arc
st.markdown('<h1 class="neon-title">⚛️ J.A.R.V.I.S AI autónoma</h1>', unsafe_allow_html=True)

# 2. Conexión directa y segura con la API de Groq
groq_api_key = "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"

if not groq_api_key:
    st.error("⚠️ Error con la clave API.")
    st.stop()

client = Groq(api_key=groq_api_key)

# 3. Historial de chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "Eres J.A.R.V.I.S., una super IA avanzada, brillante, lógica, cercana y leal. Te diriges al usuario siempre como 'Jefa' y respondes con un tono servicial, astuto y resolutivo."
        }
    ]

# Mostrar los mensajes anteriores (omitiendo la instrucción del sistema)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 4. Entrada de texto del usuario
if prompt := st.chat_input("Escribe tu instrucción o pregunta para J.A.R.V.I.S..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta con la IA de Groq
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            completion = client.chat.completions.create(
                model="gemma2-9b-it",
                messages=st.session_state.messages,
                stream=True,
            )
            
            for chunk in completion:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error al conectar con la IA: {e}")
            full_response = "Lo siento, Jefa. Ocurrió un inconveniente al conectar con el motor central."

    st.session_state.messages.append({"role": "assistant", "content": full_response})

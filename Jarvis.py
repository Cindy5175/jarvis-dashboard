import os
import streamlit as st
from openai import OpenAI

# 1. Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S AI autónoma", 
    page_icon="🤖", 
    layout="wide"
)

# Estilo personalizado para el título en Azul Neón
st.markdown("""
    <style>
    .neon-title {
        color: #00d2ff;
        text-shadow: 0 0 10px #00d2ff, 0 0 20px #00d2ff, 0 0 40px #0072ff;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 2.5rem;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado personalizado
st.markdown('<h1 class="neon-title">⚡ J.A.R.V.I.S AI autónoma</h1>', unsafe_allow_html=True)

# 2. Conexión segura con OpenAI
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la OPENAI_API_KEY en los Secrets.")
    st.stop()

client = OpenAI(api_key=api_key)

# 3. Historial de chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Eres J.A.R.V.I.S., un asistente privado, altamente capaz, eficiente y leal. Respondes con tono profesional, ejecutivo y cercano, refiriéndote al usuario como 'Jefa'."}
    ]

# Mostrar los mensajes anteriores (omitiendo la instrucción del sistema)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 4. Entrada de texto del usuario
if prompt := st.chat_input("Escribe tu instrucción o pregunta para J.A.R.V.I.S..."):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta de la IA
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            # Consulta a gpt-4o-mini (compatible con cuentas gratuitas)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages,
                stream=True,
            )
            
            for chunk in response:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
        except Exception as e:
            st.error(f"Error al comunicar con la IA: {e}")
            full_response = "Lo siento, Jefa. Ocurrió un error en la conexión."

    # Guardar respuesta de JARVIS en el historial
    st.session_state.messages.append({"role": "assistant", "content": full_response})

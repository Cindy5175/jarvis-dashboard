import streamlit as st
from gtts import gTTS
import os

st.set_page_config(page_title="J.A.R.V.I.S. IA", layout="wide")

st.markdown("### J.A.R.V.I.S. IA")
st.markdown("[ NODO BUIN, CHILE // Sábado, 07 de noviembre de 2026 ]")

# Inicializar historial de chat si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Saludo inicial del sistema
    welcome_msg = "Buenas tardes, jefa. Protocolo de seguridad máxima activo en Nodo Buin."
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
    
    # Generar audio del saludo inicial
    tts = gTTS(text=welcome_msg, lang='es')
    tts.save("welcome.mp3")

# Mostrar historial de mensajes en pantalla
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "welcome.mp3" in locals() and message == st.session_state.messages[0]:
            st.audio("welcome.mp3", format="audio/mp3")

# Caja de entrada de texto principal (compatible con dictado Win + H)
if prompt := st.chat_input("Escríbele o háblale a JARVIS..."):
    # Agregar mensaje de la usuaria al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta simulada / o conexión con la API de Gemini
    response_text = f"Aquí sigo, jefa, soportando la brisa de Buin y tus constantes preguntas. Procesando: '{prompt}'"
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
        
        # Generar audio de respuesta oral con gTTS
        audio_filename = f"resp_{len(st.session_state.messages)}.mp3"
        tts = gTTS(text=response_text, lang='es')
        tts.save(audio_filename)
        st.audio(audio_filename, format="audio/mp3")

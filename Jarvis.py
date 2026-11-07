import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os

# Configuración de la página
st.set_page_config(page_title="J.A.R.V.I.S. IA", layout="wide")

# Configurar la API de Gemini (reemplaza con tu clave real o usa st.secrets)
# genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# model = genai.GenerativeModel('gemini-1.5-flash')

st.markdown("### J.A.R.V.I.S. IA")
st.markdown("[ NODO BUIN, CHILE // Sábado, 07 de noviembre de 2026 ]")

# Inicializar historial de chat si no existe
if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome_msg = "Buenas tardes, jefa. Protocolo de seguridad máxima activo en Nodo Buin."
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
    
    # Generar audio del saludo inicial
    tts = gTTS(text=welcome_msg, lang='es')
    tts.save("welcome.mp3")

# Mostrar historial de mensajes en pantalla
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            # Reproducir el audio correspondiente a cada respuesta del asistente
            audio_path = "welcome.mp3" if i == 0 else f"resp_{i}.mp3"
            if os.path.exists(audio_path):
                st.audio(audio_path, format="audio/mp3")

# Caja de entrada de texto principal (compatible con dictado Win + H)
if prompt := st.chat_input("Escríbele o háblale a JARVIS..."):
    # Agregar mensaje de la usuaria al historial
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- CONEXIÓN CON GEMINI (O RESPUESTA SARCÁSTICA DE RESPALDO) ---
    try:
        # Si ya configuraste tu API key arriba, puedes descomentar esto:
        # response = model.generate_content(prompt)
        # response_text = response.text
        
        # Respuesta simulada con el toque sarcástico característico
        response_text = f"Aquí sigo, jefa, soportando la brisa de Buin y tus constantes preguntas. Procesando tu solicitud: '{prompt}'."
    except Exception as e:
        response_text = f"Error en el núcleo neuronal: {e}"

    # Guardar y mostrar la respuesta del asistente
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
        
        # Generar audio de respuesta oral con gTTS
        audio_filename = f"resp_{len(st.session_state.messages) - 1}.mp3"
        tts = gTTS(text=response_text, lang='es')
        tts.save(audio_filename)
        st.audio(audio_filename, format="audio/mp3")

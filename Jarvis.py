import streamlit as st
import threading
import speech_recognition as sr
import time

# ---------------------------------------------------------
# 1. ESTADO GLOBAL E INTERFAZ HUD
# ---------------------------------------------------------
st.set_page_config(page_title="Panel de Control J.A.R.V.I.S.", layout="wide")

if 'estado_jarvis' not in st.session_state:
    st.session_state.estado_jarvis = "Esperando palabra clave ('Jarvis')..."

st.title("⚡ J.A.R.V.I.S. V6.4 - Sistema Hands-Free")
st.markdown(f"### Estado del Sistema: `{st.session_state.estado_jarvis}`")

# ---------------------------------------------------------
# 2. MÓDULO DE ESCUCHA PASIVA EN SEGUNDO PLANO (THREADING)
# ---------------------------------------------------------
def listener_background():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    # Usamos el micrófono predeterminado de Windows 11
    with sr.Microphone() as source:
        print("Módulo Hands-Free J.A.R.V.I.S. Iniciado en segundo plano...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while True:
            try:
                # Escucha continua en bucle
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
                text = recognizer.recognize_google(audio, language="es-CL").lower()
                
                if "jarvis" in text:
                    print("¡Palabra de activación detectada! [JARVIS]")
                    st.session_state.estado_jarvis = "¡Escuchando comando activo"
            except Exception:
                time.sleep(1)

# ---------------------------------------------------------
# 3. INICIALIZACIÓN ÚNICA DEL HILO EN STREAMLIT
# ---------------------------------------------------------
if 'jarvis_listener_active' not in st.session_state:
    st.session_state.jarvis_listener_active = True
    threading.Thread(target=listener_background, daemon=True).start()

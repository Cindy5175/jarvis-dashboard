import streamlit as st
import threading
import speech_recognition as sr
import time

def listener_background():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    # Usamos el micrófono predeterminado de Windows
    with sr.Microphone() as source:
        print("Módulo Hands-Free J.A.R.V.I.S. Iniciado en segundo plano...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        while True:
            try:
                # Escucha continua en bucle (frases cortas)
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
                text = recognizer.recognize_google(audio, language="es-CL").lower()
                
                if "jarvis" in text:
                    print("¡Palabra de activación detectada! [JARVIS]")
                    # Aquí puedes disparar la lógica de respuesta o activar el chat
            except Exception:
                time.sleep(1)

# Aseguramos que el hilo de escucha corra UNA SOLA VEZ al arrancar la app
if 'jarvis_listener_active' not in st.session_state:
    st.session_state.jarvis_listener_active = True
    threading.Thread(target=listener_background, daemon=True).start()

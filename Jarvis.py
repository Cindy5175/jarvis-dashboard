import streamlit as st
import threading
import speech_recognition as sr
import time

# ---------------------------------------------------------
# 1. INICIALIZACIÓN DEL MOTOR DE VOZ EN SEGUNDO PLANO
# ---------------------------------------------------------
def listener_background():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        while True:
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
                text = recognizer.recognize_google(audio, language="es-CL").lower()
                
                if "jarvis" in text:
                    st.session_state.estado_jarvis = "¡Jarvis Escuchando!"
                    # Aquí podemos hacer que active el chat o responda automáticamente
            except Exception:
                time.sleep(1)

# Arrancar el hilo de escucha sin bloquear la pantalla
if 'jarvis_listener_active' not in st.session_state:
    st.session_state.jarvis_listener_active = True
    threading.Thread(target=listener_background, daemon=True).start()

# ---------------------------------------------------------
# 2. TU CENTRO DE MANDO COMPLETO (INTERFAZ ORIGINAL)
# ---------------------------------------------------------
st.set_page_config(page_title="J.A.R.V.I.S. // CENTRO DE MANDO", layout="wide")

# Estado de voz integrado silenciosamente
if 'estado_jarvis' not in st.session_state:
    st.session_state.estado_jarvis = "Sistema en línea, jefa."

# Aquí va todo tu diseño previo:
st.title("JARVIS // CENTRO DE MANDO CENTRAL")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔵 JARVIS IA")
    # Indicador dinámico de voz dentro de tu mensaje de bienvenida
    st.info(f"{st.session_state.estado_jarvis} Sobrevivimos a otro día más sin que el búnker colapse.")
    
    # Tu input de comando táctico
    comando = st.text_input("Instrucciones para JARVIS...", placeholder="Escribe un comando táctico...")

with col2:
    st.subheader("🌐 CENTRO TÁCTICO")
    # Tus pestañas de Control y Clima, Biometría, Finanzas, etc.
    st.metric(label="Clima en Buin", value="14,9 °C", delta="V 6,5 km/h")

import streamlit as st
import speech_recognition as sr
import pyttsx3
import threading

# Configuración de la página (Estética intacta)
st.set_page_config(
    page_title="J.A.R.V.I.S. - Nodo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Inicializar motor de voz (Voz varonil y tono sarcástico)
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Buscar una voz en español o la primera disponible de tipo masculino si está configurada
    for voice in voices:
        if "spanish" in voice.name.lower() or "male" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 160)
except Exception:
    pass

def hablar_jarvis(texto):
    """Función para que Jarvis hable en voz alta"""
    try:
        engine.say(texto)
        engine.runAndWait()
    except Exception:
        pass

# Interfaz visual táctica
st.title("⚡ J.A.R.V.I.S. IA // NÚCLEO TÁCTICO")
st.markdown("---")

st.sidebar.header("⚙️ Configuración del Sistema")
modo_voz = st.sidebar.toggle("🎙️ Escucha Continua (Hands-Free)", value=True)
sarcasmo_nivel = st.sidebar.slider("Nivel de Sarcasmo", 1, 10, 8)
camara_activa = st.sidebar.toggle("📷 Cámaras en Vivo (Ojo de Dios)", value=False)

if st.sidebar.button("➕ Registrar Tarea"):
    st.sidebar.success("Tarea registrada correctamente en el Nodo Buin.")

# Sección de estado táctico
st.markdown("### 🌐 NÚCLEO DE CONTROL")
with st.expander("🛡️ Opciones de Seguridad"):
    if st.button("🔒 Bloquear Búnker"):
        st.warning("Sistema de búnker bloqueado temporalmente por seguridad, jefa.")

st.markdown("---")
st.subheader("💬 Interacción con el Asistente")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Sistema operativo en línea, Nodo Buin sincronizado. ¿Qué milagro necesitas hoy, jefa?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada por texto tradicional
if prompt := st.chat_input("Escribe una orden para Jarvis..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    respuesta_jarvis = f"Procesando tu orden '{prompt}' con nivel de sarcasmo {sarcasmo_nivel}. Por supuesto, haré el trabajo pesado mientras tú descansas, jefa."
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta_jarvis})
    with st.chat_message("assistant"):
        st.markdown(respuesta_jarvis)
    
    # Jarvis habla
    hablar_jarvis(respuesta_jarvis)

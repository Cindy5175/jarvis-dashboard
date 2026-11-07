import streamlit as st
import google.generativeai as genai
from gtts import gTTS
import os
import sqlite3
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="J.A.R.V.I.S. IA - Nodo Buin", layout="wide")

# --- CONFIGURACIÓN DE LA API DE GEMINI ---
# Descomenta la siguiente línea y pon tu clave real o usa st.secrets
# genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
# model = genai.GenerativeModel('gemini-1.5-flash')

# --- DISEÑO DEL ENCABEZADO TÁCTICO ---
st.markdown("### J.A.R.V.I.S. IA")
st.markdown("[ NODO BUIN, CHILE // Sábado, 07 de noviembre de 2026 ]")
st.markdown("⚡ **NÚCLEO NEURONAL CYBER-GRID** ⚡")
st.markdown("Sistemas de procesamiento, ciberseguridad, clima en vivo y **mapa táctico satelital**.")

# --- INICIALIZACIÓN DE BASE DE DATOS SQLITE ---
def init_db():
    conn = sqlite3.connect('nodo_buin.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS registros (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, evento TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- PANEL LATERAL TÁCTICO COMPLETO ---
with st.sidebar:
    st.markdown("### 🛡️ NÚCLEO DE CONTROL TÁCTICO")
    pin_ingresado = st.text_input("PIN de Seguridad del Nodo", type="password")
    
    if pin_ingresado == "2805":
        st.success("Acceso Concedido: Mandos Desbloqueados")
        if st.button("🔒 Bloquear Sistema"):
            st.warning("Sistema asegurado.")
        if st.button("🔄 Reinicio Total de la App"):
            st.rerun()
    elif pin_ingresado:
        st.error("PIN incorrecto. Acceso restringido.")
    
    st.markdown("---")
    st.markdown("### ⚙️ Protocolos Tácticos")
    protocolo_activo = st.selectbox(
        "Seleccionar Protocolo",
        [
            "1. /HUMAN (Natural y cercano)",
            "2. ELI10 (Explicación simple)",
            "3. X10PIENSA (Análisis profundo)",
            "4. KILLCRITIC (Cuestionar riesgos)",
            "5. OODA (Plan de acción)"
        ]
    )
    
    st.markdown("---")
    st.markdown("### 🌤️ Clima en Vivo - Buin")
    st.info("Temperatura actual: 22°C // Viento moderado.")
    
    st.markdown("---")
    st.markdown("### 🗺️ Mapa Táctico Satelital")
    st.write("Estado de geolocalización del Nodo: Activo y sincronizado.")

# --- INICIALIZAR HISTORIAL DE CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = []
    welcome_msg = "Buenas tardes, jefa. Protocolo de seguridad máxima activo en Nodo Buin."
    st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
    
    # Generar audio del saludo inicial
    tts = gTTS(text=welcome_msg, lang='es')
    tts.save("welcome.mp3")

# --- MOSTRAR HISTORIAL DE MENSAJES ---
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            audio_path = "welcome.mp3" if i == 0 else f"resp_{i}.mp3"
            if os.path.exists(audio_path):
                st.audio(audio_path, format="audio/mp3")

# --- CAJA DE ENTRADA PRINCIPAL (Texto y Dictado Win + H) ---
if prompt := st.chat_input("Escríbele o háblale a JARVIS..."):
    # Registrar mensaje de la usuaria
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- PROCESAMIENTO SEGÚN EL PROTOCOLO ACTIVO ---
    try:
        # Aquí puedes adaptar el prompt con el protocolo seleccionado si usas Gemini:
        # prompt_con_protocolo = f"[{protocolo_activo}] {prompt}"
        # response = model.generate_content(prompt_con_protocolo)
        # response_text = response.text
        
        # Respuesta adaptada según el protocolo elegido en la izquierda
        if "HUMAN" in protocolo_activo:
            response_text = f"Entendido, jefa. Hablando de forma más natural y cercana sobre: '{prompt}'."
        elif "ELI10" in protocolo_activo:
            response_text = f"Explicación sencilla (modo ELI10) para '{prompt}': Imagina que esto funciona paso a paso..."
        elif "X10PIENSA" in protocolo_activo:
            response_text = f"Análisis profundo (X10PIENSA) activado para tu consulta: '{prompt}'. Evaluando variables estratégicas..."
        elif "KILLCRITIC" in protocolo_activo:
            response_text = f"Evaluación de riesgos (KILLCRITIC): Analizando fallas potenciales y vulnerabilidades en tu planteamiento sobre '{prompt}'."
        elif "OODA" in protocolo_activo:
            response_text = f"Estructurando plan de acción (OODA) para '{prompt}': 1. Observar, 2. Orientar, 3. Decidir, 4. Actuar."
        else:
            response_text = f"Aquí sigo, jefa, soportando la brisa de Buin. Procesando: '{prompt}'."
            
    except Exception as e:
        response_text = f"Error en el núcleo neuronal del Nodo: {e}"

    # Guardar en base de datos SQLite local
    try:
        conn = sqlite3.connect('nodo_buin.db')
        c = conn.cursor()
        c.execute("INSERT INTO registros (timestamp, evento) VALUES (?, ?)", (str(datetime.datetime.now()), f"[{protocolo_activo}] {prompt}"))
        conn.commit()
        conn.close()
    except Exception:
        pass

    # Guardar y mostrar respuesta del asistente
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    with st.chat_message("assistant"):
        st.markdown(response_text)
        
        # Generar audio de respuesta oral con gTTS para los parlantes
        audio_filename = f"resp_{len(st.session_state.messages) - 1}.mp3"
        tts = gTTS(text=response_text, lang='es')
        tts.save(audio_filename)
        st.audio(audio_filename, format="audio/mp3")

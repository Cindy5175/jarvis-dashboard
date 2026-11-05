import streamlit as st
from datetime import datetime
import base64
from gtts import gTTS
import io
import pandas as pd
from streamlit_autorefresh import st_autorefresh

# Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. - Nodo Táctico",
    page_icon="⚡",
    layout="centered"
)

# Auto-refresco del núcleo cada 1000ms para el segundero en vivo
st_autorefresh(interval=1000, key="reloj_tactico")

# Estilo visual: Fondo negro absoluto y letras en tono cyan/azul Stark
st.markdown(
    """
    <style>
    .stApp {
        background-color: #050505;
        color: #00e5ff;
    }
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #00e5ff !important;
    }
    .stButton>button {
        background-color: #0d1b2a;
        color: #00e5ff !important;
        border: 1px solid #00e5ff;
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def hablar_jarvis_web(texto):
    """Genera audio con tono fluido y natural para Jarvis."""
    try:
        tts = gTTS(text=texto, lang='es', tld='cl', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f"""
            <audio autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    except Exception:
        pass

# Reactor Arc Triangular idéntico con brillo LED cian
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 10px;">
        <svg width="90" height="90" viewBox="0 0 100 100" style="filter: drop-shadow(0 0 14px #00e5ff);">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#00e5ff" stroke-width="4" stroke-dasharray="10 5"/>
            <circle cx="50" cy="50" r="38" fill="#050505" stroke="#00e5ff" stroke-width="2"/>
            <polygon points="50,20 80,72 20,72" fill="none" stroke="#00e5ff" stroke-width="4"/>
            <polygon points="50,32 70,66 30,66" fill="#00e5ff" opacity="0.3"/>
            <polygon points="50,45 60,60 40,60" fill="#ffffff" filter="drop-shadow(0 0 8px #ffffff)"/>
        </svg>
    </div>
    """,
    unsafe_allow_html=True
)

# Cabecera táctica exacta
st.markdown("<h3 style='text-align: center; color: #00e5ff;'>_J.A.R.V.I.S IA // NODO BUIN</h3>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #00e5ff; margin-top: -15px;'>TACTICAL CORE</h3>", unsafe_allow_html=True)

# Línea de estado y fecha con segundero en tiempo real
fecha_actual = datetime.now().strftime("%A, %d de %B de %Y - %H:%M:%S")
st.markdown(
    f"""
    <div style='text-align: center; color: #00ffff; text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff; font-family: monospace; font-weight: bold;'>
        [ STARK INDUSTRIES // NODO BUIN, CHILE // {fecha_actual} ]
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Botón de seguridad principal en el cuerpo
if st.button("🔒 Bloquear Búnker", use_container_width=True):
    st.warning("Sistema de búnker bloqueado temporalmente por seguridad, jefa.")

st.markdown("---")

# --- BARRA LATERAL (IZQUIERDA): OJO DE DIOS DE OSIRIS Y MÓDULOS ACTIVOS ---
with st.sidebar:
    st.markdown("### 🌐 NÚCLEO DE CONTROL")
    st.markdown("---")

    with st.expander("👁️ Ojo de Dios (Sistema Osiris)"):
        st.markdown("📡 **Feed Satelital & Rastreo Global Activo**")
        # Integración real del visor de rastreo / streaming directo
        st.video("https://www.youtube.com/watch?v=4QJEibrt9B8")
        st.success("Ojo de Dios (Osiris) enlazado al Nodo Buin con telemetría en directo.")

    with st.expander("🗺️ Mapa Táctico Satelital"):
        st.markdown("Coordenadas Perimetrales Buin")
        map_data = pd.DataFrame([[-33.7300, -70.7200]], columns=['lat', 'lon'])
        st.map(map_data, zoom=10, use_container_width=True)

    with st.expander("🌍 Cámara en Vivo: Red Mundial (earthTV)"):
        st.video("https://www.youtube.com/watch?v=HfgIFGbdGJ0")

    with st.expander("🎥 Cámara en Vivo: Global (SkylineWebcams)"):
        st.video("https://www.youtube.com/watch?v=kUfuwa8mDrA")

    with st.expander("🌤️ Clima en Vivo (Buin)"):
        st.markdown("**Estación Meteorológica Local**")
        st.markdown(
            '<div style="background-color: #0b1d3a; padding: 10px; border-radius: 6px; border: 1px solid #00e5ff; color: #00e5ff; font-weight: bold; margin-bottom: 8px;">🌡️ Temperatura: 21°C | Estado: Óptimo</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div style="background-color: #1a237e; padding: 10px; border-radius: 6px; border: 1px solid #3f51b5; color: #9fa8da; font-weight: bold;">💧 Humedad: 45% | Viento: 12 km/h SE</div>',
            unsafe_allow_html=True
        )

    with st.expander("🎙️ Escucha Continua (Hands-Free)"):
        st.info("Control de audio local en tiempo real.")
        if st.button("🎙️ Iniciar Hands-Free", use_container_width=True):
            st.success("¡Escucha continua activada en el nodo local, jefa!")

    with st.expander("➕ Registro de Tareas"):
        st.text("Nodo Buin sincronizado.")
        nueva_tarea = st.text_input("Nueva Misión / Tarea:")
        if st.button("Registrar Tarea ➕", use_container_width=True):
            if nueva_tarea:
                st.success(f"Tarea registrada: '{nueva_tarea}'")
            else:
                st.warning("Escribe una tarea primero, jefa.")

# --- CUERPO PRINCIPAL: CHAT IA OPERATIVO ---
st.subheader("💬 Chat IA & Sistema Operativo")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Ojo de Dios de Osiris en línea, jefa. Enlaces de rastreo conectados y segundero sincronizado. ¿Qué ruta o zona vigilamos ahora?"}
    ]

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de chat abajo
if prompt := st.chat_input("Escribe tu orden o dicte al sistema, jefa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower()
    if "código azul" in prompt_lower or "codigo azul" in prompt_lower:
        respuesta = "⚠️ ¡ATENCIÓN! Código Azul activado en el Nodo Buin. Protocolo de máxima seguridad desplegado, perímetro blindado y sistemas en alerta roja, jefa. Respira hondo, nadie va a pasar."
    elif "hola" in prompt_lower:
        respuesta = "Hola de nuevo, jefa. ¿Te dignaste a saludar al sistema o necesitas que mueva medio Buin otra vez?"
    else:
        respuesta = f"Procesando tu orden '{prompt}' mediante el sistema Osiris en el Nodo Buin, jefa. De inmediato."
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)

    hablar_jarvis_web(respuesta)

import streamlit as st
from datetime import datetime
import base64
from gtts import gTTS
import io

# Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. - Nodo Táctico",
    page_icon="⚡",
    layout="centered"
)

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

# Cabecera con el Reactor Arc de Tony Stark y letras azules
st.image("https://i.ibb.co/6y1M15X/arc-reactor.jpg", width=120)  # O usa la imagen local de tu reactor
st.markdown("<h2 style='text-align: center; color: #00e5ff;'>J.A.R.V.I.S IA</h2>", unsafe_allow_html=True)
st.markdown("### _E.D.I.T.H. TACTICAL CORE_")

fecha_actual = datetime.now().strftime("%A, %d de %B de %Y - %H:%M:%S")
st.markdown(f"`[ STARK INDUSTRIES // NODO BUIN, CHILE // {fecha_actual} ]`")
st.markdown("---")

# --- BARRA LATERAL CON MÓDULOS OCULTOS ---
with st.sidebar:
    st.markdown("### 🌐 NÚCLEO DE CONTROL")
    st.markdown("---")

    with st.expander("📷 Cámaras en Vivo (Ojo de Dios)"):
        st.info("Conectando con la red de vigilancia satelital del Nodo Buin...")

    with st.expander("🌌 Transmisión Espacial en Vivo"):
        st.markdown("📡 **Señal Satelital en Directo (NASA/Espacio)**")
        st.video("https://www.youtube.com/watch?v=4QJEibrt9B8")

    with st.expander("🌤️ Clima en Vivo (Buin)"):
        st.markdown("**Estación Meteorológica Local**")
        st.markdown(
            """
            <div style="background-color: #0b1d3a; padding: 10px; border-radius: 6px; border: 1px solid #00e5ff; color: #00e5ff; font-weight: bold; margin-bottom: 8px;">
                🌡️ Temperatura: 21°C | Estado: Óptimo
            </div>
            <div style="background-color: #1a237e; padding: 10px; border-radius: 6px; border: 1px solid #3f51b5; color: #9fa8da; font-weight: bold;">
                💧 Humedad: 45% | Viento: 12 km/h SE
            </div>
            """,
            unsafe_allow_html=True
        )

    with st.expander("📍 Coordenadas Tácticas Buin"):
        st.success("Latitud: -33.73 | Longitud: -70.72 - Perímetro seguro.")

    with st.expander("🎙️ Escucha Continua (Hands-Free)"):
        st.info("Módulo de escucha automática integrado en el núcleo operativo.")

    with st.expander("➕ Registro de Tareas"):
        st.text("Nodo Buin sincronizado con el registro de misiones.")

    with st.expander("🛡️ Módulo E.D.I.T.H."):
        st.markdown("Control satelital de defensa y apoyo táctico activo.")

    st.markdown("---")
    if st.button("🔒 Bloquear Búnker", use_container_width=True):
        st.warning("Sistema de búnker bloqueado temporalmente por seguridad, jefa.")

# --- CUERPO PRINCIPAL: CHAT IA & PROTOCOLO E.D.I.T.H. ---
st.subheader("💬 Chat IA & Protocolo E.D.I.T.H.")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Buenos días, jefa. El nodo de Buin está estable, la temperatura es perfecta y, sorprendentemente, nadie ha intentado hackearnos hoy. ¿Qué milagro te trae por aquí?"}
    ]

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de chat abajo (flujo nativo)
if prompt := st.chat_input("Escribe tu orden o dicte a E.D.I.T.H., jefa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower()
    if "código azul" in prompt_lower or "codigo azul" in prompt_lower:
        respuesta = "⚠️ ¡ATENCIÓN! Código Azul activado en el Nodo Buin. Protocolo de máxima seguridad desplegado, perímetro blindado y sistemas en alerta roja, jefa. Respira hondo, nadie va a pasar."
    elif "hola" in prompt_lower:
        respuesta = "Hola de nuevo, jefa. ¿Te dignaste a saludar al sistema o necesitas que mueva medio Buin otra vez?"
    else:
        respuesta = f"Procesando tu orden '{prompt}' desde el Nodo Buin, jefa. Por supuesto, haré el trabajo duro mientras tú descansas."
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)

    hablar_jarvis_web(respuesta)

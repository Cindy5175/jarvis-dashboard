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

def hablar_jarvis_web(texto):
    """Genera audio automáticamente para que Jarvis hable solo."""
    try:
        tts = gTTS(text=texto, lang='es', tld='cl')
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

# Indicador visual superior tipo núcleo
st.markdown("<div style='text-align: center; font-size: 24px; margin-bottom: -10px;'>🔵</div>", unsafe_allow_html=True)

# Cabecera táctica exacta
st.markdown("### _J.A.R.V.I.S IA // E.D.I.T.H. TACTICAL CORE")
fecha_actual = datetime.now().strftime("%A, %d de %B de %Y - %H:%M:%S")
st.markdown(f"`[ STARK INDUSTRIES // NODO BUIN, CHILE // {fecha_actual} ]`")
st.markdown("---")

# Botón de seguridad principal
if st.button("🔒 Bloquear Búnker", use_container_width=True):
    st.warning("Sistema de búnker bloqueado temporalmente por seguridad, jefa.")

st.markdown("---")
st.markdown("### 🌐 NÚCLEO DE CONTROL")

# Módulos ordenados
with st.expander("📷 Cámaras en Vivo (Ojo de Dios)"):
    st.info("Conectando con la red de vigilancia satelital del Nodo Buin...")

with st.expander("🌤️ Clima en Vivo (Buin)"):
    st.markdown("**Estación Meteorológica Local**")
    st.markdown(
        """
        <div style="background-color: #113816; padding: 10px; border-radius: 6px; border: 1px solid #2e7d32; color: #a5d6a7; font-weight: bold; margin-bottom: 8px;">
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
st.subheader("💬 Chat IA & Protocolo E.D.I.T.H.")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Buenos días, jefa. El nodo de Buin está estable, la temperatura es perfecta y, sorprendentemente, nadie ha intentado hackearnos hoy. ¿Qué milagro te trae por aquí?"}
    ]

# Mostrar historial de chat existente
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de chat abajo (como corresponde al diseño nativo)
if prompt := st.chat_input("Escribe tu orden o dicte a E.D.I.T.H., jefa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower()
    if "código azul" in prompt_lower or "codigo azul" in prompt_lower:
        respuesta = "⚠️ ¡ATENCIÓN! Código Azul activado en el Nodo Buin. Protocolo de máxima seguridad desplegado, perímetro blindado y sistemas en alerta roja, jefa. Respira hondo, nadie va a pasar."
    else:
        respuesta = f"Procesando tu orden '{prompt}' desde el Nodo Buin, jefa. Por supuesto, haré el trabajo duro mientras tú descansas."
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)

    hablar_jarvis_web(respuesta)

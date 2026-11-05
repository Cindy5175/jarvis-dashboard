import streamlit as st
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. - Nodo Táctico",
    page_icon="⚡",
    layout="centered"
)

# Cabecera táctica idéntica al teléfono (con el triángulo/reactor arriba)
st.markdown("<div style='text-align: center;'><h3>🔺</h3></div>", unsafe_allow_html=True)
st.markdown("### _J.A.R.V.I.S IA // E.D.I.T.H. TACTICAL CORE")
fecha_actual = datetime.now().strftime("%A, %d de %B de %Y - %H:%M:%S")
st.markdown(f"`[ STARK INDUSTRIES // NODO BUIN, CHILE // {fecha_actual} ]`")
st.markdown("---")

# Botón principal de Bloquear Búnker
if st.button("🔒 Bloquear Búnker", use_container_width=True):
    st.warning("Sistema de búnker bloqueado temporalmente por seguridad, jefa.")

st.markdown("---")
st.markdown("### 🌐 NÚCLEO DE CONTROL")

# Desplegable de Cámaras (Ojo de Dios)
with st.expander("📷 Cámaras en Vivo (Ojo de Dios)"):
    st.info("Conectando con la red de vigilancia satelital del Nodo Buin...")

# Desplegable del Clima con la cajita verde exacta de tu teléfono
with st.expander("🌤️ Clima en Vivo (Buin)", expanded=True):
    st.markdown("**Estación Meteorológica Local**")
    st.markdown(
        """
        <div style="background-color: #113816; padding: 12px; border-radius: 8px; border: 1px solid #2e7d32; color: #a5d6a7; font-weight: bold;">
            🌡️ Temperatura: 21°C | Estado: Óptimo
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")
st.subheader("💬 Interacción con el Asistente")

# Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Sistema operativo en línea, Nodo Buin sincronizado. ¿Qué orden ejecutamos hoy, jefa?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Caja de entrada de órdenes
if prompt := st.chat_input("Escribe una orden para Jarvis..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    respuesta = f"Procesando la orden '{prompt}' desde el Nodo Buin. Todo bajo control, jefa."
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)

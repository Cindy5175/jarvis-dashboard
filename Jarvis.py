import streamlit as st

# Configuración inicial de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Estilo visual y cabecera
st.title("⚡ J.A.R.V.I.S. // NÚCLEO TÁCTICO")
st.markdown("---")

# Panel lateral de control operativo
st.sidebar.header("⚙️ Configuración del Sistema")
modo_voz = st.sidebar.toggle("🎙️ Escucha Continua (Hands-Free)", value=True)
sarcasmo_nivel = st.sidebar.slider("Nivel de Sarcasmo", 1, 10, 8)
camara_activa = st.sidebar.toggle("📷 Cámaras de Seguridad", value=False)

if st.sidebar.button("➕ Registrar Tarea"):
    st.sidebar.success("Tarea registrada correctamente en el núcleo local.")

# Sección central: Mapa táctico satelital
st.subheader("🗺️ Mapa Táctico Satelital")
st.map(latitude=-33.725, longitude=-70.702, zoom=11)

# Sección de diálogo con el sistema
st.markdown("---")
st.subheader("💬 Interacción con el Asistente")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Sistema operativo en línea. ¿Qué milagro necesitas hoy, jefa?"}
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe una orden para Jarvis..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    respuesta_jarvis = f"Procesando tu orden '{prompt}' con nivel de sarcasmo {sarcasmo_nivel}. Por supuesto, haré el trabajo pesado mientras tú descansas."
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta_jarvis})
    with st.chat_message("assistant"):
        st.markdown(respuesta_jarvis)

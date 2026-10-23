import streamlit as st

# 1. Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S AI autónoma", 
    page_icon="⚛️", 
    layout="centered"
)

# Estilos CSS personalizados para centrar el título, diseño neón y ajustar la caja del chat
st.markdown("""
    <style>
    /* Centrar y estilizar el título con Reactor Arc */
    .neon-title {
        color: #00d2ff;
        text-shadow: 0 0 10px #00d2ff, 0 0 20px #00d2ff, 0 0 40px #0072ff;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 2.3rem;
        text-align: center;
        margin-top: -20px;
        margin-bottom: 25px;
    }
    
    /* Ajustar el ancho y centrar la caja principal de chat y contenedores */
    .block-container {
        max-width: 750px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* Estilo personalizado para la barra de entrada de texto inferior */
    .stChatInput {
        max-width: 750px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado centrado con Reactor Arc
st.markdown('<h1 class="neon-title">⚛️ J.A.R.V.I.S AI autónoma</h1>', unsafe_allow_html=True)

# 2. Historial de chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Reactor Arc al 100%, Jefa. Sistemas autónomos calibrados y listos. ¿Qué orden ejecutamos hoy?"}
    ]

# Mostrar los mensajes anteriores dentro del contenedor centrado
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Entrada de texto del usuario
if prompt := st.chat_input("Escribe tu instrucción o pregunta para J.A.R.V.I.S..."):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta del núcleo autónomo
    with st.chat_message("assistant"):
        full_response = f"Secuencia iniciada para: '{prompt}'. Parámetros estables, Jefa. Protocolo autónomo ejecutándose sin restricciones de red."
        st.markdown(full_response)

    # Guardar respuesta en el historial
    st.session_state.messages.append({"role": "assistant", "content": full_response})

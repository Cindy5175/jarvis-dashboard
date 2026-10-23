import streamlit as st

# 1. Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S AI autónoma", 
    page_icon="🤖", 
    layout="wide"
)

# Estilo personalizado para el título en Azul Neón
st.markdown("""
    <style>
    .neon-title {
        color: #00d2ff;
        text-shadow: 0 0 10px #00d2ff, 0 0 20px #00d2ff, 0 0 40px #0072ff;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 2.5rem;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado personalizado
st.markdown('<h1 class="neon-title">⚡ J.A.R.V.I.S AI autónoma</h1>', unsafe_allow_html=True)

# 2. Historial de chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hola, Jefa. Sistema autónomo en línea y listo para operar sin restricciones."}
    ]

# Mostrar los mensajes anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Entrada de texto del usuario
if prompt := st.chat_input("Escribe tu instrucción o pregunta para J.A.R.V.I.S..."):
    # Guardar y mostrar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta simulada/autónoma inmediata del Plan B
    with st.chat_message("assistant"):
        full_response = f"Entendido, Jefa. Procesando la instrucción: '{prompt}'. Todos los sistemas locales y de interfaz responden correctamente bajo el protocolo autónomo."
        st.markdown(full_response)

    # Guardar respuesta en el historial
    st.session_state.messages.append({"role": "assistant", "content": full_response})

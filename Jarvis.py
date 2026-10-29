import streamlit as st

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

# Estilos CSS para el neón azul y la caja de chat
st.markdown(
    """
    <style>
    .stApp {
        background-color: #050505;
        color: #00f0ff;
    }
    /* Título principal en azul neón con brillo */
    .neon-header {
        color: #00f0ff;
        font-size: 2rem;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
        margin-bottom: 0px;
    }
    /* Estilo para la caja de chat y mensajes con fondo negro y texto neón */
    .stChatInput input {
        background-color: #000000 !important;
        color: #00f0ff !important;
        border: 1px solid #00f0ff !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Encabezado
st.markdown('<div class="neon-header">J.A.R.V.I.S IA</div>', unsafe_allow_html=True)

if st.button("🗑️ Purgar Chat"):
    st.toast("Historial purgado.", icon="🧹")

st.markdown("---")

# Caja de chat de prueba con la nueva directriz
chat_container = st.container(height=300)
with chat_container:
    st.chat_message("assistant").write(
        "Sistemas en línea, Cindy. Encabezado y núcleo de chat configurados."
    )

user_input = st.chat_input("Escriba su comando...")
if user_input:
    with chat_container:
        st.chat_message("user").write(user_input)
        st.chat_message("assistant").write(f"Procesando: {user_input}")

import streamlit as st

# Configuración de la página independiente para JARVIS
st.set_page_config(
    page_title="Stark Core - JARVIS Console", page_icon="🔵", layout="centered"
)

# Estilos CSS personalizados: Modo Sigilo y Neón Azul exclusivo para JARVIS
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    .chat-container {
        border: 1.5px solid #00f0ff;
        border-radius: 12px;
        padding: 15px 20px;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
        background-color: rgba(0, 10, 20, 0.6);
        display: flex;
        align-items: center;
        margin-top: 30px;
    }
    .console-title {
        color: #00f0ff;
        font-family: monospace;
        font-size: 16px;
        text-align: center;
        margin-bottom: 15px;
        letter-spacing: 1.5px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Título principal de la consola táctica de JARVIS
st.markdown(
    '<p class="console-title">J.A.R.V.I.S. — NÚCLEO INDEPENDIENTE ACTIVO</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# Interfaz limpia en Modo Sigilo con el Reactor ARC
st.markdown(
    """
    <div class="chat-container">
        <span style="font-size: 30px; margin-right: 15px;">🔵</span>
        <span style="color: #a0a0a0; font-family: sans-serif; font-size: 16px;">¿Qué directiva operativa o creativa ejecutamos hoy?</span>
    </div>
    """,
    unsafe_allow_html=True,
)

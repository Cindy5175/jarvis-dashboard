import json
import os
import re
import subprocess
import requests
import streamlit as st
import streamlit.components.v1 as components

# Configuración de página
st.set_page_config(
    page_title="JARVIS 4.0", page_icon="🤖", layout="wide"
)

# CSS Personalizado: Fondo negro puro y estilos neón cian uniformes
st.markdown(
    """
    <style>
    /* Fondo negro absoluto */
    .stApp {
        background-color: #000000 !important;
        color: #00f3ff !important;
    }

    /* Títulos y textos */
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #00f3ff !important;
        text-shadow: 0 0 5px rgba(0, 243, 255, 0.5);
    }

    /* Cajas de texto e inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #050505 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        box-shadow: 0 0 8px rgba(0, 243, 255, 0.3);
    }

    /* Botones Neón */
    .stButton>button {
        background-color: #000000 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.4);
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #00f3ff !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #00f3ff;
    }

    /* Ecualizador de Voz (Animación Neón) */
    .equalizer-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        height: 40px;
        gap: 6px;
        margin-bottom: 15px;
    }

    .eq-bar {
        width: 8px;
        background-color: #00f3ff;
        box-shadow: 0 0 10px #00f3ff;
        animation: equalize 1.2s infinite ease-in-out alternate;
    }

    .eq-bar:nth-child(1) { height: 30%; animation-delay: -0.4s; }
    .eq-bar:nth-child(2) { height: 70%; animation-delay: -0.2s; }
    .eq-bar:nth-child(3) { height: 100%; animation-delay: -0.7s; }
    .eq-bar:nth-child(4) { height: 50%; animation-delay: -0.1s; }
    .eq-bar:nth-child(5) { height: 85%; animation-delay: -0.5s; }

    @keyframes equalize {
        0% { height: 15%; }
        100% { height: 100%; }
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Encabezado Principal Centrado
st.markdown(
    "<h1 style='text-align: center;'>🤖 J.A.R.V.I.S. 4.0</h1>",
    unsafe_allow_html=True,
)

# Memoria Persistente
MEMORY_FILE = "jarvis_memory.json"


def cargar_memoria():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"historial": []}


def guardar_memoria(memoria):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memoria, f, indent=4)


if "messages" not in st.session_state:
    st.session_state.messages = []

# Layout en 2 columnas: Centro (Chat + Ecualizador) y Derecha (Música)
col_centro, col_derecha = st.columns([3, 1.2])

with col_centro:
    # 1. Ecualizador de voz justo arriba del Chat
    st.markdown(
        """
        <div class="equalizer-container">
            <div class="eq-bar"></div>
            <div class="eq-bar"></div>
            <div class="eq-bar"></div>
            <div class="eq-bar"></div>
            <div class="eq-bar"></div>
        </div>
        <p style='text-align: center; font-size: 12px;'>🎙️ SINTETIZADOR DE VOZ ACTIVO</p>
    """,
        unsafe_allow_html=True,
    )

    # 2. Caja de Chat
    st.markdown("### 💬 Centro de Mando / Chat")

    # Mostrar historial de mensajes
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Selector de Personalidad y Botón Purgar
    col_p1, col_p2 = st.columns([2, 1])
    with col_p1:
        protocolo = st.selectbox(
            "Protocolo de Personalidad", ["Tony Stark", "Chef Ejecutivo"]
        )
    with col_p2:
        if st.button("Purgar Chat 🗑️"):
            st.session_state.messages = []
            st.rerun()

    # Entrada de texto del Chat
    user_input = st.chat_input("Escriba su comando, Jefa...")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        # Respuesta simulada o conexión a Ollama
        prompt_sistema = (
            "Eres JARVIS, asistente de Cindy (Jefa) en Buin."
            if protocolo == "Tony Stark"
            else "Eres un Chef Ejecutivo experto asistiendo a Cindy (Jefa)."
        )

        try:
            res = requests.post(
                "http://127.0.0.1:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": f"{prompt_sistema}\nUsuario: {user_input}\nJARVIS:",
                    "stream": False,
                },
                timeout=10,
            )
            respuesta = res.json().get("response", "Sistemas operativos.")
        except Exception:
            respuesta = f"Entendido, Jefa. Ejecutando orden con protocolo {protocolo}."

        st.session_state.messages.append(
            {"role": "assistant", "content": respuesta}
        )

        # Reproducción de voz automática vía Web Speech API
        texto_limpio = re.sub(r"[^\w\s,.]", "", respuesta)
        components.html(
            f"""
            <script>
                var msg = new SpeechSynthesisUtterance("{texto_limpio}");
                msg.lang = 'es-ES';
                window.speechSynthesis.speak(msg);
            </script>
        """,
            height=0,
        )

        st.rerun()

with col_derecha:
    # 3. Módulo de Música a la derecha 👉
    st.markdown("### 🎵 Reproductor 👉")
    st.markdown("---")
    st.write("📻 **Canal:** Ambient Búnker")

    st.audio(
        "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
        format="audio/mp3",
    )

    st.markdown("---")
    st.button("Play Playlist 🎶", use_container_width=True)
    st.button("Siguiente Pista ⏭️", use_container_width=True)

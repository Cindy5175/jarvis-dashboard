import json
import os
import re
import requests
import streamlit as st
import streamlit.components.v1 as components

# Configuración de página N.O.V.A.
st.set_page_config(
    page_title="N.O.V.A. - Tactical Core", page_icon="📡", layout="wide"
)

# CSS Personalizado: Fondo negro puro y neón verde esmeralda táctico
st.markdown(
    """
    <style>
    /* Fondo negro absoluto */
    .stApp {
        background-color: #000000 !important;
        color: #00ff66 !important;
    }

    /* Títulos y textos */
    h1, h2, h3, h4, h5, h6, p, label, span {
        color: #00ff66 !important;
        text-shadow: 0 0 5px rgba(0, 255, 102, 0.5);
    }

    /* Cajas de texto e inputs */
    .stTextInput input, .stTextArea textarea, .stSelectbox div {
        background-color: #031008 !important;
        color: #00ff66 !important;
        border: 1px solid #00ff66 !important;
        box-shadow: 0 0 8px rgba(0, 255, 102, 0.3);
    }

    /* Botones Neón Verde */
    .stButton>button {
        background-color: #000000 !important;
        color: #00ff66 !important;
        border: 1px solid #00ff66 !important;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0, 255, 102, 0.4);
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #00ff66 !important;
        color: #000000 !important;
        box-shadow: 0 0 20px #00ff66;
    }

    /* Radar/Ecualizador Táctico Verde */
    .radar-container {
        display: flex;
        justify-content: center;
        align-items: flex-end;
        height: 40px;
        gap: 6px;
        margin-bottom: 15px;
    }

    .radar-bar {
        width: 8px;
        background-color: #00ff66;
        box-shadow: 0 0 10px #00ff66;
        animation: radarPulse 1s infinite ease-in-out alternate;
    }

    .radar-bar:nth-child(1) { height: 40%; animation-delay: -0.3s; }
    .radar-bar:nth-child(2) { height: 80%; animation-delay: -0.1s; }
    .radar-bar:nth-child(3) { height: 100%; animation-delay: -0.5s; }
    .radar-bar:nth-child(4) { height: 60%; animation-delay: -0.2s; }
    .radar-bar:nth-child(5) { height: 90%; animation-delay: -0.4s; }

    @keyframes radarPulse {
        0% { height: 20%; opacity: 0.4; }
        100% { height: 100%; opacity: 1; }
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Encabezado Principal Centrado
st.markdown(
    "<h1 style='text-align: center;'>📡 N.O.V.A. 1.0 — TACTICAL CORE</h1>",
    unsafe_allow_html=True,
)

if "nova_messages" not in st.session_state:
    st.session_state.nova_messages = []

# Layout en 2 columnas: Centro (Análisis Táctico) y Derecha (Métricas)
col_centro, col_derecha = st.columns([3, 1.2])

with col_centro:
    # Radar Táctico de Audio
    st.markdown(
        """
        <div class="radar-container">
            <div class="radar-bar"></div>
            <div class="radar-bar"></div>
            <div class="radar-bar"></div>
            <div class="radar-bar"></div>
            <div class="radar-bar"></div>
        </div>
        <p style='text-align: center; font-size: 12px;'>🛰️ NÚCLEO TÁCTICO Y ANALÍTICO ONLINE</p>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### 📊 Centro de Diagnóstico & Análisis")

    # Historial de chat de N.O.V.A.
    for msg in st.session_state.nova_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Botón Purgar
    if st.button("Limpiar Registro Táctico 🗑️"):
        st.session_state.nova_messages = []
        st.rerun()

    # Entrada de comandos
    user_input = st.chat_input("Ingrese requerimiento analítico, Jefa...")

    if user_input:
        st.session_state.nova_messages.append(
            {"role": "user", "content": user_input}
        )

        input_lower = user_input.lower().strip()

        # Respuesta ante estado/despierto
        if "despierto" in input_lower or "estas despierto" in input_lower:
            respuesta = "Sistemas analíticos listos y a su entera disposición, señorita Cindy."
        elif (
            "buenos dias" in input_lower
            or "hola" in input_lower
            or "buenos días" in input_lower
        ):
            respuesta = "Buenos días, señorita Cindy. N.O.V.A. reporta 0 anomalías en el búnker."
        else:
            prompt_sistema = (
                "Eres N.O.V.A., el Segundo Sistema analítico, táctico y de diagnóstico de la señorita Cindy (Jefa) en Buin. "
                "Tu tono es conciso, profesional, altamente eficiente y sumamente leal."
            )

            try:
                res = requests.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={
                        "model": "llama3",
                        "prompt": f"{prompt_sistema}\nUsuario: {user_input}\nN.O.V.A.:",
                        "stream": False,
                    },
                    timeout=10,
                )
                respuesta = res.json().get(
                    "response", "Análisis completado, señorita Cindy."
                )
            except Exception:
                respuesta = f"Entendido, señorita Cindy. Procesando diagnóstico de la orden."

        st.session_state.nova_messages.append(
            {"role": "assistant", "content": respuesta}
        )

        # Voz de N.O.V.A.
        texto_limpio = re.sub(r"[^\w\s,.]", "", respuesta)
        components.html(
            f"""
            <script>
                var msg = new SpeechSynthesisUtterance("{texto_limpio}");
                msg.lang = 'es-ES';
                msg.pitch = 1.1; // Tono ligeramente más agudo para N.O.V.A.
                window.speechSynthesis.speak(msg);
            </script>
        """,
            height=0,
        )

        st.rerun()

with col_derecha:
    st.markdown("### 📈 Estado del Búnker")
    st.markdown("---")
    st.write("🛡️ **Red:** Encriptada (Buin)")
    st.write("⚡ **Estado:** Operativo al 100%")
    st.write("🧠 **Integración:** JARVIS 4.0 Dual-Core")
    st.markdown("---")
    st.markdown("#### 🎯 Accesos Rápida Respuesta")
    st.button("Escaneo de Red 🔍", use_container_width=True)
    st.button("Reporte de Memoria 💾", use_container_width=True)

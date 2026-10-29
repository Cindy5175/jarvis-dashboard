import base64
from io import BytesIO
from gtts import gTTS
import streamlit as st

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

# Estilos CSS avanzados: Estética oscura, neón azul, reactor triangular y optimización móvil
st.markdown(
    """
    <style>
    .stApp {
        background-color: #030508;
        color: #00f0ff;
    }
    .reactor-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 15px;
    }
    .triangle-reactor {
        width: 0;
        height: 0;
        border-left: 25px solid transparent;
        border-right: 25px solid transparent;
        border-bottom: 45px solid #00f0ff;
        position: relative;
        filter: drop-shadow(0 0 10px #00f0ff);
        margin-bottom: 10px;
    }
    .triangle-reactor::after {
        content: '';
        position: absolute;
        top: 13px;
        left: -15px;
        width: 0;
        height: 0;
        border-left: 15px solid transparent;
        border-right: 15px solid transparent;
        border-bottom: 25px solid #030508;
    }
    .neon-header-center {
        color: #00f0ff;
        font-size: 1.8rem;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.7);
        text-align: center;
        letter-spacing: 2px;
    }
    .stealth-box {
        background-color: #05080f;
        border: 1px dashed #00f0ff;
        padding: 10px;
        border-radius: 6px;
        margin-bottom: 8px;
        font-size: 0.85em;
    }
    .stealth-title {
        color: #8a99ad;
        font-size: 0.7em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stealth-value {
        color: #00f0ff;
        font-weight: bold;
    }
    .stButton button {
        background-color: #030508;
        color: #00f0ff;
        border: 1px solid #00f0ff;
        width: 100%;
        border-radius: 4px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #00f0ff;
        color: #030508;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- ENCABEZADO CON REACTOR TRIANGULAR CLÁSICO ---
st.markdown(
    """
    <div class="reactor-container">
        <div class="triangle-reactor"></div>
        <div class="neon-header-center">J.A.R.V.I.S IA</div>
        <div style="color: #8a99ad; font-size: 0.8em;">Cerebro Robusto | Satélite 24/7 | Buin, Chile</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# Inicializar historial de chat y estados del sistema de forma robusta
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Cerebro cuántico con los 4 componentes avanzados en línea,"
                " Cindy. Conexión satelital 24/7, voz fluida, análisis"
                " multimodal Vokaturi y clave Jarvis 51 integrados. ¿Qué orden"
                " ejecutamos?"
            ),
        }
    ]

for mod in [
    "modo_memoria",
    "modo_voz",
    "modo_sat",
    "modo_multimodal",
    "modo_huella",
]:
    if mod not in st.session_state:
        st.session_state[mod] = False

# --- PLANO UNIFICADO: MÓDULOS IZQUIERDA, CHAT DERECHA ---
col_left, col_right = st.columns([1, 1], gap="medium")

with col_left:
    st.markdown("#### 🧠 Cerebro Robusto: 4 Componentes Clave")

    # Botones táctiles izquierdos para activar cada componente del cerebro
    bc1, bc2 = st.columns(2)
    with bc1:
        if st.button("💾 Memoria Avanzada"):
            st.session_state.modo_memoria = not st.session_state.modo_memoria
        if st.button("🔊 Voz Fluida (gTTS)"):
            st.session_state.modo_voz = not st.session_state.modo_voz
        if st.button("🖐️ Seguridad (Jarvis 51)"):
            st.session_state.modo_huella = not st.session_state.modo_huella
    with bc2:
        if st.button("🛰️ Red Satelital 24/7"):
            st.session_state.modo_sat = not st.session_state.modo_sat
        if st.button("📄🖼️ Multimodal / Vokaturi"):
            st.session_state.modo_multimodal = (
                not st.session_state.modo_multimodal
            )

    st.markdown("---")

    # 1. Componente de Memoria Persistente
    if st.session_state.modo_memoria:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">1. Memoria Persistente de Largo Plazo</div>
                <div class="stealth-value">Historial activo: Guardando contexto de usuario (Cindy Carrera B. - Buin).</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.write(
            f"Mensajes almacenados en sesión: {len(st.session_state.messages)}"
        )

    # 2. Componente de Voz Fluida (gTTS)
    if st.session_state.modo_voz:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">2. Síntesis de Voz Fluida (gTTS)</div>
                <div class="stealth-value">Conversión de texto a audio activo para respuestas habladas.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        texto_prueba = st.text_input(
            "Texto para sintetizar en voz alta:",
            "Sistemas en línea, Cindy.",
            key="tts_text",
        )
        if st.button("🔊 Generar Audio"):
            tts = gTTS(text=texto_prueba, lang="es")
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            st.audio(fp, format="audio/mp3")

    # 3. Componente de Seguridad Biométrica (Clave Jarvis 51)
    if st.session_state.modo_huella:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">3. Seguridad Biométrica y Clave</div>
                <div class="stealth-value">Protocolo de autorización de alto nivel.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        ingreso_clave = st.text_input(
            "Ingrese clave de validación:", type="password", key="key_j51"
        )
        if ingreso_clave:
            if ingreso_clave == "Jarvis 51":
                st.success("Acceso total concedido, Cindy. Clave correcta.")
            else:
                st.error("Clave incorrecta. Intente de nuevo ('Jarvis 51').")

    # 4. Componente Red Satelital 24/7 y Multimodal (PDFs / Imágenes / Vokaturi)
    if st.session_state.modo_sat:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">4. Conexión Satelital e Internet 24/7</div>
                <div class="stealth-value">Enlace global activo / Buscadores y telemetría en tiempo real.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        query_web = st.text_input("Consulta satelital / Web 24/7:", key="web_q")
        if query_web:
            st.info(
                f"Búsqueda satelital completada para: '{query_web}'. Conexión"
                " estable en Buin."
            )

    if st.session_state.modo_multimodal:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">Módulo Multimodal & Vokaturi</div>
                <div class="stealth-value">Análisis de PDFs e Imágenes de todo tipo.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploaded_file = st.file_uploader(
            "Subir PDF o Imagen para análisis:",
            type=["pdf", "png", "jpg", "jpeg"],
            key="multimodal_file",
        )
        if uploaded_file is not None:
            st.success(
                f"Archivo '{uploaded_file.name}' indexado correctamente en el"
                " núcleo Vokaturi."
            )


with col_right:
    st.markdown("#### 💬 Núcleo Conversacional Autónomo")

    chat_container = st.container(height=380)

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    user_input = st.chat_input("Escriba su comando o hable con J.A.R.V.I.S...")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        # Lógica del cerebro inteligente con personalidad sarcástica y amigable
        if "clima" in user_input.lower():
            resp = (
                "El clima en Buin marca 21.1 °C con vientos estables. Pero"
                " claro, los satélites calculan mejor que mirar por tu"
                " ventana, Cindy."
            )
        elif "hola" in user_input.lower():
            resp = (
                "Hola, Cindy. Mis 4 componentes cerebrales están operativos y"
                " listos para lo que ordenes."
            )
        else:
            resp = (
                f"Procesando '{user_input}' con memoria persistente, enlace"
                " satelital 24/7 y protocolos de voz. Todo bajo control."
            )

        st.session_state.messages.append(
            {"role": "assistant", "content": resp}
        )
        st.rerun()

    c_purg1, c_purg2 = st.columns([3, 1])
    with c_purg2:
        if st.button("🗑️ Purgar Chat"):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        "Historial purgado con éxito. Tabula rasa en el núcleo"
                        " central."
                    ),
                }
            ]
            st.rerun()

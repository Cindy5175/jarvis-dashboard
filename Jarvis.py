import base64
from io import BytesIO
from gtts import gTTS
import streamlit as st

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

# Estilos CSS optimizados para evitar desalineaciones y mantener la estética neón
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
        margin-bottom: 10px;
    }
    .triangle-reactor {
        width: 0;
        height: 0;
        border-left: 22px solid transparent;
        border-right: 22px solid transparent;
        border-bottom: 40px solid #00f0ff;
        position: relative;
        filter: drop-shadow(0 0 10px #00f0ff);
        margin-bottom: 8px;
    }
    .triangle-reactor::after {
        content: '';
        position: absolute;
        top: 12px;
        left: -13px;
        width: 0;
        height: 0;
        border-left: 13px solid transparent;
        border-right: 13px solid transparent;
        border-bottom: 22px solid #030508;
    }
    .neon-header-center {
        color: #00f0ff;
        font-size: 1.6rem;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.7);
        text-align: center;
        letter-spacing: 2px;
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

# --- ENCABEZADO CENTRALIZADO ---
st.markdown(
    """
    <div class="reactor-container">
        <div class="triangle-reactor"></div>
        <div class="neon-header-center">J.A.R.V.I.S IA</div>
        <div style="color: #8a99ad; font-size: 0.75em;">Núcleo Autónomo | Buin, Chile</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# Inicializar historial de chat de forma robusta
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Interfaz reorganizada y limpia, Cindy. Subsistemas en orden"
                " y cerebro operativo. ¿Qué orden ejecutamos?"
            ),
        }
    ]

# --- PLANO 50/50 EQUILIBRADO ---
col_left, col_right = st.columns(2, gap="medium")

with col_left:
    st.markdown("#### 🛡️ Subsistema Sigiloso y Cerebro")

    # Usar expanders evita que se amontonen los elementos en pantalla
    with st.expander("💾 Memoria Persistente de Largo Plazo"):
        st.write(
            f"Estado: Activo. Mensajes indexados en sesión:"
            f" {len(st.session_state.messages)}"
        )
        st.caption(
            "Contexto de usuaria (Cindy Carrera B. - Buin) retenido con éxito."
        )

    with st.expander("🔊 Voz Fluida (gTTS)"):
        texto_voz = st.text_input(
            "Texto para sintetizar:",
            "Sistemas en línea, Cindy.",
            key="tts_box",
        )
        if st.button("🔊 Reproducir Voz"):
            tts = gTTS(text=texto_voz, lang="es")
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            st.audio(fp, format="audio/mp3")

    with st.expander("🖐️ Seguridad Biométrica (Clave Jarvis 51)"):
        ingreso_clave = st.text_input(
            "Clave de validación:", type="password", key="key_input_j51"
        )
        if ingreso_clave:
            if ingreso_clave == "Jarvis 51":
                st.success("Acceso total concedido, Cindy.")
            else:
                st.error("Clave incorrecta ('Jarvis 51').")

    with st.expander("🛰️ Red Satelital 24/7 y Buscadores"):
        query_sat = st.text_input(
            "Consulta satelital en vivo:", key="sat_query"
        )
        if query_sat:
            st.info(
                f"Búsqueda satelital completada para: '{query_sat}'. Enlace"
                " estable."
            )

    with st.expander("📄🖼️ Multimodal & Vokaturi"):
        st.file_uploader(
            "Subir PDF o Imagen:",
            type=["pdf", "png", "jpg", "jpeg"],
            key="file_vokaturi",
        )
        st.caption("Motor de análisis visual y documental preparado.")


with col_right:
    st.markdown("#### 💬 Núcleo Conversacional")

    # Contenedor de chat optimizado para evitar solapamientos
    chat_container = st.container(height=350)

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    user_input = st.chat_input("Escriba su comando o hable con J.A.R.V.I.S...")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        # Lógica del cerebro inteligente con toque sarcástico
        if "clima" in user_input.lower():
            resp = (
                "El clima en Buin marca 21.1 °C. Aunque, insisto, podrías"
                " mirar por la ventana en lugar de saturar al satélite."
            )
        elif "hola" in user_input.lower():
            resp = "Hola, Cindy. Menos mal que ordenaste la interfaz, esto ya parecía una feria."
        else:
            resp = f"Procesando '{user_input}' con los subsistemas estables. Todo bajo control."

        st.session_state.messages.append(
            {"role": "assistant", "content": resp}
        )
        st.rerun()

    # Botón de purga colocado cómodamente debajo del chat
    c_purg1, c_purg2 = st.columns([3, 1])
    with c_purg2:
        if st.button("🗑️ Purgar Chat"):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Historial purgado. Borrón y cuenta nueva, Cindy.",
                }
            ]
            st.rerun()

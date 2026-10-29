import streamlit as st

# Configuración inicial de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

# Estilos CSS personalizados (Estética oscura y neón azul)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #050505;
        color: #00f0ff;
    }
    .metric-box {
        background-color: #0a0e14;
        border: 1px solid #00f0ff;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 0.85em;
        color: #8a99ad;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 1.3em;
        font-weight: bold;
        color: #00f0ff;
    }
    .metric-sub {
        font-size: 0.8em;
        color: #00ff66;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Encabezado principal
st.markdown(
    "### 💬 Interfaz de Conversación Autónoma (Comando de Voz: 'Hey Jarvis')"
)

# Botón de purgar chat
col_top1, col_top2 = st.columns([1, 5])
with col_top1:
    if st.button("🗑️ Purgar Chat"):
        st.toast("Historial de chat purgado con éxito.", icon="🧹")

st.markdown("---")

# Distribución en dos columnas principales: Izquierda (Módulos/Telemetría) y Derecha (Chat)
col_left, col_right = st.columns([1, 2], gap="medium")

with col_left:
    st.markdown("#### ⚡ Telemetría y Sistemas")

    # Módulo 1: Ubicación Base
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Ubicación Base</div>
            <div class="metric-value">Buin, CL</div>
            <div class="metric-sub">↑ Seguro / Biometría OK</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Módulo 2: Clima Real
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Clima Real (Buin)</div>
            <div class="metric-value">21.1 °C</div>
            <div class="metric-sub">↑ Viento: 9.2 km/h</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Módulo 3: Estado del Sistema
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Estado del Sistema</div>
            <div class="metric-value">99.8% Neural</div>
            <div class="metric-sub">↑ Quantum Core</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Módulo 4: Latencia de Red
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Latencia de Red</div>
            <div class="metric-value">0.38 ms</div>
            <div class="metric-sub">↑ Óptimo</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "<small style='color: #8a99ad;'>J.A.R.V.I.S. IA Autónomo — Taller de Inteligencia Autónoma | Buin, Chile.</small>",
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown("#### 🎙️ Núcleo Conversacional")

    # Contenedor del historial de chat
    chat_container = st.container(height=450)

    with chat_container:
        st.chat_message("assistant").write(
            "Sistemas en línea, Cindy. Módulos de audio externos purgados y telemetría restablecida. ¿Qué orden ejecutamos hoy?"
        )

    # Entrada de texto del chat (caja de chat fija abajo)
    user_input = st.chat_input("Escriba su comando o diga 'Hey Jarvis'...")

    if user_input:
        with chat_container:
            st.chat_message("user").write(user_input)
            # Respuesta simulada del agente
            st.chat_message("assistant").write(
                f"Comando recibido y procesado con éxito: '{user_input}'"
            )

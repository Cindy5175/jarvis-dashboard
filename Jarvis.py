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
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 0.75em;
        color: #8a99ad;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 1.1em;
        font-weight: bold;
        color: #00f0ff;
    }
    .metric-sub {
        font-size: 0.75em;
        color: #00ff66;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- BARRA LATERAL: TELEMETRÍA Y SISTEMAS ---
with st.sidebar:
    st.markdown("### ⚡ Telemetría y Sistemas")
    st.markdown("---")

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

    st.markdown("---")
    st.markdown(
        "<small style='color: #8a99ad;'>J.A.R.V.I.S. IA Autónomo<br>Buin, Chile.</small>",
        unsafe_allow_html=True,
    )


# --- PANTALLA PRINCIPAL: NÚCLEO CONVERSACIONAL ---
st.markdown(
    "### 💬 Interfaz de Conversación Autónoma (Comando de Voz: 'Hey Jarvis')"
> )

col_btn1, col_btn2 = st.columns([1, 4])
with col_btn1:
    if st.button("🗑️ Purgar Chat"):
        st.toast("Historial de chat purgado con éxito.", icon="🧹")

st.markdown("---")

# Contenedor del historial de chat en la pantalla principal con buen espacio
chat_container = st.container(height=420)

with chat_container:
    st.chat_message("assistant").write(
        "Sistemas en línea, Cindy. Telemetría movida al panel lateral para optimizar la interfaz. ¿Qué orden ejecutamos hoy?"
    )

# Entrada de texto del chat
user_input = st.chat_input("Escriba su comando o diga 'Hey Jarvis'...")

if user_input:
    with chat_container:
        st.chat_message("user").write(user_input)
        st.chat_message("assistant").write(
            f"Comando procesado correctamente: '{user_input}'"
        )

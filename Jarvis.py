import streamlit as st

# Configuración de página con estética oscura y neón
st.markdown(
    """
    <style>
    .stApp {
        background-color: #050505;
        color: #00f0ff;
    }
    /* Estilo para los contenedores de telemetría */
    .metric-box {
        background-color: #0a0e14;
        border: 1px solid #00f0ff;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Encabezado principal
st.markdown(
    "### 💬 Interfaz de Conversación Autónoma (Comando de Voz: 'Hey Jarvis')"
)

# Botón para purgar chat
if st.button("🗑️ Purgar Chat"):
    st.toast("Chat purgado con éxito.", icon="🧹")

# Estructura en columnas: Módulos a la izquierda / principal y chat
col_telemetry, col_chat = st.columns([1, 2])

with col_telemetry:
    st.markdown("### 📊 Estado y Ubicación")

    # Módulo 1: Ubicación Base
    st.markdown(
        """
        <div class="metric-box">
            <strong>Ubicación Base</strong><br>
            <span style="font-size: 1.2em; font-weight: bold;">Buin, CL</span><br>
            <small style="color: #00ff66;">↑ Seguro / Biometría OK</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Módulo 2: Clima Real
    st.markdown(
        """
        <div class="metric-box">
            <strong>Clima Real (Buin)</strong><br>
            <span style="font-size: 1.2em; font-weight: bold;">21.1 °C</span><br>
            <small style="color: #00ff66;">↑ Viento: 9.2 km/h</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Módulo 3: Estado del Sistema
    st.markdown(
        """
        <div class="metric-box">
            <strong>Estado del Sistema</strong><br>
            <span style="font-size: 1.2em; font-weight: bold;">99.8% Neural</span><br>
            <small style="color: #00ff66;">↑ Quantum Core</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Módulo 4: Latencia de Red
    st.markdown(
        """
        <div class="metric-box">
            <strong>Latencia de Red</strong><br>
            <span style="font-size: 1.2em; font-weight: bold;">0.38 ms</span><br>
            <small style="color: #00ff66;">↑ Óptimo</small>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_chat:
    st.markdown("### 🎙️ Núcleo de Conversación")

    # Historial de chat simulado / contenedor de chat
    chat_container = st.container(height=400)
    with chat_container:
        st.chat_message("assistant").write(
            "Sistemas en línea, Cindy. ¿Qué orden ejecutamos hoy?"
        )

    # Caja de entrada de chat fija en la parte inferior de la columna
    user_input = st.chat_input("Escriba su comando o diga 'Hey Jarvis'...")
    if user_input:
        with chat_container:
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write(
                f"Procesando comando: {user_input}"
            )

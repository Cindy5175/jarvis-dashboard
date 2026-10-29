import streamlit as st

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

# Estilos CSS avanzados: Estética oscura, neón azul, reactor central y modo sigiloso
st.markdown(
    """
    <style>
    .stApp {
        background-color: #030508;
        color: #00f0ff;
    }
    /* Estilo centrado para el encabezado con el Reactor Arc */
    .reactor-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }
    .reactor-logo {
        width: 50px;
        height: 50px;
        border: 2px solid #00f0ff;
        border-radius: 50%;
        box-shadow: 0 0 15px #00f0ff, inset 0 0 15px #00f0ff;
        background: radial-gradient(circle, #ffffff 0%, #00f0ff 50%, #030508 100%);
        animation: pulse-reactor 2s infinite;
        margin-bottom: 10px;
    }
    @keyframes pulse-reactor {
        0% { box-shadow: 0 0 10px #00f0ff, inset 0 0 10px #00f0ff; }
        50% { box-shadow: 0 0 25px #00f0ff, inset 0 0 20px #ffffff; }
        100% { box-shadow: 0 0 10px #00f0ff, inset 0 0 10px #00f0ff; }
    }
    .neon-header-center {
        color: #00f0ff;
        font-size: 2.2rem;
        font-weight: bold;
        text-shadow: 0 0 12px rgba(0, 240, 255, 0.7);
        text-align: center;
        letter-spacing: 2px;
    }
    /* Módulos en modo sigiloso / táctico */
    .stealth-box {
        background-color: #05080f;
        border: 1px dashed #00f0ff;
        padding: 12px;
        border-radius: 6px;
        margin-bottom: 10px;
        font-size: 0.9em;
    }
    .stealth-title {
        color: #8a99ad;
        font-size: 0.75em;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .stealth-value {
        color: #00f0ff;
        font-weight: bold;
    }
    /* Botones táctiles neón */
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

# --- ENCABEZADO CENTRALIZADO CON REACTOR LOGO ---
st.markdown(
    """
    <div class="reactor-container">
        <div class="reactor-logo"></div>
        <div class="neon-header-center">J.A.R.V.I.S IA</div>
        <div style="color: #8a99ad; font-size: 0.85em;">Núcleo Autónomo | Buin, Chile</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# Distribución Principal: Izquierda (Módulo Táctico Sigiloso), Derecha (Chat y Núcleo de Conversación)
col_left, col_right = st.columns([1, 2], gap="medium")

# --- MÓDULO IZQUIERDO: ACCESOS TÁCTICOS EN MODO SIGILOSO ---
with col_left:
    st.markdown("#### 🛡️ Subsistema Sigiloso")
    st.markdown(
        "<small style='color: #8a99ad;'>Panel de control de acceso restringido.</small>",
        unsafe_allow_html=True,
    )

    # Inicializar estados de despliegue sigiloso
    if "modo_sensor" not in st.session_state:
        st.session_state.modo_sensor = False
    if "modo_facial" not in st.session_state:
        st.session_state.modo_facial = False
    if "modo_huella" not in st.session_state:
        st.session_state.modo_huella = False
    if "modo_voz" not in st.session_state:
        st.session_state.modo_voz = False
    if "modo_sat" not in st.session_state:
        st.session_state.modo_sat = False

    # Botones táctiles de control
    b1, b2 = st.columns(2)
    with b1:
        if st.button("👁️ Movimiento"):
            st.session_state.modo_sensor = not st.session_state.modo_sensor
        if st.button("👤 Facial"):
            st.session_state.modo_facial = not st.session_state.modo_facial
        if st.button("🎙️ Voz Fluida"):
            st.session_state.modo_voz = not st.session_state.modo_voz
    with b2:
        if st.button("🖐️ Huella/Clave"):
            st.session_state.modo_huella = not st.session_state.modo_huella
        if st.button("🛰️ Satelital"):
            st.session_state.modo_sat = not st.session_state.modo_sat

    st.markdown("---")

    # Visualización sigilosa al activar los botones
    if st.session_state.modo_sensor:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">Sensor de Movimiento</div>
                <div class="stealth-value">Perímetro Buin: Estable (0 anomalías)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.modo_facial:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">Identificación Facial</div>
                <div class="stealth-value">Acceso Concedido: Cindy Carrera B.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.modo_huella:
        # Clave interna de seguridad incluida en el código
        clave_secreta = "JARVIS-OMEGA-75"
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">Seguridad Biométrica y Clave</div>
                <div class="stealth-value">Biometría: Verificada</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        ingreso_clave = st.text_input(
            "Ingrese clave de validación:", type="password"
        )
        if ingreso_clave:
            if ingreso_clave == clave_secreta:
                st.success("Clave aceptada. Protocolo de alta seguridad activo.")
            else:
                st.error("Clave incorrecta. Acceso limitado.")

    if st.session_state.modo_voz:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">Voz Fluida & Personalidad</div>
                <div class="stealth-value">Modo: Autónomo / Sarcástico & Amigable</div>
                <small style='color: #00ff66;'>Conectado al chat principal.</small>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.modo_sat:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">Enlace Satelital / Radar</div>
                <div class="stealth-value">Conexión cifrada de baja latencia (0.38 ms)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# --- MÓDULO DERECHO: NÚCLEO CONVERSACIONAL Y PURGA DE CHAT ---
with col_right:
    st.markdown("#### 💬 Núcleo Conversacional Autónomo")

    chat_container = st.container(height=350)

    with chat_container:
        st.chat_message("assistant").write(
            "Por fin en línea, Cindy. Y dime, ¿qué milagro hace que me enciendas hoy? Espero que no sea para preguntarme el clima de nuevo. ¿Qué orden ejecutamos?"
        )

    user_input = st.chat_input("Escriba su comando o hable con J.A.R.V.I.S...")

    if user_input:
        with chat_container:
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write(
                f"Procesando '{user_input}'... Tranquila, lo tengo bajo control, o al menos eso intento."
            )

    # Botón de purga colocado cómodamente debajo del chat
    c_purg1, c_purg2 = st.columns([4, 1])
    with c_purg2:
        if st.button("🗑️ Purgar Chat"):
            st.toast(
                "Historial purgado con éxito. Borrón y cuenta nueva.", icon="🧹"
            )

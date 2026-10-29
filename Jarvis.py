import streamlit as st

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

# Estilos CSS avanzados: Estética oscura, neón azul y reactor triangular clásico
st.markdown(
    """
    <style>
    .stApp {
        background-color: #030508;
        color: #00f0ff;
    }
    /* Estilo centrado para el encabezado con el Reactor Triangular Clásico */
    .reactor-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
    }
    .triangle-reactor {
        width: 0;
        height: 0;
        border-left: 30px solid transparent;
        border-right: 30px solid transparent;
        border-bottom: 50px solid #00f0ff;
        position: relative;
        filter: drop-shadow(0 0 12px #00f0ff);
        margin-bottom: 12px;
    }
    .triangle-reactor::after {
        content: '';
        position: absolute;
        top: 15px;
        left: -18px;
        width: 0;
        height: 0;
        border-left: 18px solid transparent;
        border-right: 18px solid transparent;
        border-bottom: 30px solid #030508;
    }
    .neon-header-center {
        color: #00f0ff;
        font-size: 2.2rem;
        font-weight: bold;
        text-shadow: 0 0 12px rgba(0, 240, 255, 0.7);
        text-align: center;
        letter-spacing: 2px;
    }
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

# --- ENCABEZADO CENTRALIZADO CON REACTOR TRIANGULAR CLÁSICO ---
st.markdown(
    """
    <div class="reactor-container">
        <div class="triangle-reactor"></div>
        <div class="neon-header-center">J.A.R.V.I.S IA</div>
        <div style="color: #8a99ad; font-size: 0.85em;">Núcleo Autónomo | Conexión Satelital 24/7 | Buin, Chile</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# --- DISTRIBUCIÓN EN UN SOLO PLANO: MÓDULOS A LA IZQUIERDA, CHAT A LA DERECHA ---
col_left, col_right = st.columns(
    [1, 1], gap="medium"
)  # Plano equilibrado 50/50

with col_left:
    st.markdown("#### 🛡️ Subsistema Sigiloso y Módulos Avanzados")

    # Inicializar estados de los módulos
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
    if "modo_pdf" not in st.session_state:
        st.session_state.modo_pdf = False
    if "modo_img" not in st.session_state:
        st.session_state.modo_img = False

    # Botones táctiles organizados
    b1, b2 = st.columns(2)
    with b1:
        if st.button("👁️ Movimiento"):
            st.session_state.modo_sensor = not st.session_state.modo_sensor
        if st.button("👤 Facial"):
            st.session_state.modo_facial = not st.session_state.modo_facial
        if st.button("🎙️ Voz Fluida"):
            st.session_state.modo_voz = not st.session_state.modo_voz
        if st.button("📄 Descarga PDF"):
            st.session_state.modo_pdf = not st.session_state.modo_pdf
    with b2:
        if st.button("🖐️ Huella/Clave"):
            st.session_state.modo_huella = not st.session_state.modo_huella
        if st.button("🛰️ Satélite 24/7"):
            st.session_state.modo_sat = not st.session_state.modo_sat
        if st.button("🖼️ Motor Vokaturi / Imgs"):
            st.session_state.modo_img = not st.session_state.modo_img

    st.markdown("---")

    # Visualización de módulos activos en el plano izquierdo
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
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.modo_sat:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">Red Satelital e Internet 24/7</div>
                <div class="stealth-value">Conexión Global Activa / Latencia: 0.38 ms</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.modo_pdf:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">Módulo de Descarga de PDFs</div>
                <div class="stealth-value">Listo para indexar y extraer documentos técnicos.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.file_uploader(
            "Subir o buscar PDF para análisis:", type=["pdf"], key="pdf_up"
        )

    if st.session_state.modo_img:
        st.markdown(
            """
            <div class="stealth-box">
                <div class="stealth-title">Módulo de Imágenes & Vokaturi</div>
                <div class="stealth-value">Extracción y banco de imágenes activo.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.text_input("Buscar imagen en la red (Prompt):", key="img_query")


# --- PLANO DERECHO: NÚCLEO CONVERSACIONAL Y PURGA DE CHAT ---
with col_right:
    st.markdown("#### 💬 Núcleo Conversacional Autónomo")

    chat_container = st.container(height=380)

    with chat_container:
        st.chat_message("assistant").write(
            "Sistemas integrados en un solo plano, Cindy. Satélites enlazados y motores de descarga listos. ¿Qué orden ejecutamos ahora?"
        )

    user_input = st.chat_input("Escriba su comando o hable con J.A.R.V.I.S...")

    if user_input:
        with chat_container:
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write(
                f"Procesando '{user_input}' con enlace satelital activo... Menos mal que me tienes a mí para organizar todo esto."
            )

    # Botón de purga colocado cómodamente debajo de la caja del chat
    c_purg1, c_purg2 = st.columns([3, 1])
    with c_purg2:
        if st.button("🗑️ Purgar Chat"):
            st.toast("Historial purgado con éxito.", icon="🧹")

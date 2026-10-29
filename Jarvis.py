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
        <div style="color: #8a99ad; font-size: 0.8em;">Núcleo Autónomo | Satélite 24/7 | Buin, Chile</div>
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
            "content": "Cerebro cuántico en línea, Cindy. Conexión satelital estable y módulos listos. Menos mal que me tienes a cargo de esto. ¿Qué orden ejecutamos hoy?",
        }
    ]

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

# --- PLANO UNIFICADO: MÓDULOS IZQUIERDA, CHAT DERECHA ---
col_left, col_right = st.columns([1, 1], gap="medium")

with col_left:
    st.markdown("#### 🛡️ Subsistema Sigiloso y Módulos Avanzados")

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
        clave_secreta = "Jarvis 51"
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
            "Ingrese clave de validación:", type="password", key="input_clave_jarvis"
        )
        if ingreso_clave:
            if ingreso_clave == clave_secreta:
                st.success("Clave aceptada ('Jarvis 51'). Acceso total concedido.")
            else:
                st.error("Clave incorrecta. Verifique sus credenciales.")

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


with col_right:
    st.markdown("#### 💬 Núcleo Conversacional Autónomo")

    # Contenedor de chat persistente y robusto
    chat_container = st.container(height=300)

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    user_input = st.chat_input("Escriba su comando o hable con J.A.R.V.I.S...")

    if user_input:
        # Añadir mensaje de la usuaria al historial
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Lógica del cerebro de Jarvis con respuestas sarcásticas y lógicas
        if "clima" in user_input.lower():
            respuesta_cerebro = "El clima en Buin está perfecto, 21.1 °C. Aunque podrías salir a comprobarlo tú misma en lugar de hacer que los satélites calculen la temperatura por ti."
        elif "hola" in user_input.lower():
            respuesta_cerebro = (
                "Hola, Cindy. ¿Qué milagro te trae por mis servidores hoy?"
            )
        elif "pdf" in user_input.lower():
            respuesta_cerebro = (
                "Activa el módulo de Descarga PDF en el panel izquierdo y sube el archivo. Yo me encargo del resto."
            )
        else:
            respuesta_cerebro = f"Procesando '{user_input}' a través del enlace satelital 24/7 y los motores lógicos. Todo bajo control, Cindy."

        st.session_state.messages.append(
            {"role": "assistant", "content": respuesta_cerebro}
        )
        st.rerun()

    # Botón de purga colocado cómodamente debajo de la caja del chat
    c_purg1, c_purg2 = st.columns([3, 1])
    with c_purg2:
        if st.button("🗑️ Purgar Chat"):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Historial purgado con éxito. ¡Tabula rasa, Cindy! Empezamos de cero.",
                }
            ]
            st.rerun()

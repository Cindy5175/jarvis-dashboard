from datetime import datetime
from io import BytesIO
from gtts import gTTS
import psutil
import pytz
import requests
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

TZ_LOCAL = pytz.timezone("America/Santiago")


def obtener_tiempo_actual():
    ahora = datetime.now(TZ_LOCAL)
    fecha_str = ahora.strftime("%d/%m/%Y")
    hora_str = ahora.strftime("%H:%M:%S")
    return ahora, fecha_str, hora_str


ahora_dt, fecha_hoy, hora_hoy = obtener_tiempo_actual()

# Estilos CSS neón azul, fondo oscuro y animación holográfica del reactor
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
        margin-bottom: 0px;
    }
    @keyframes pulse-reactor {
        0% { filter: drop-shadow(0 0 5px #00f0ff); transform: scale(1); }
        50% { filter: drop-shadow(0 0 18px #00f0ff); transform: scale(1.03); }
        100% { filter: drop-shadow(0 0 5px #00f0ff); transform: scale(1); }
    }
    .triangle-reactor {
        width: 0;
        height: 0;
        border-left: 22px solid transparent;
        border-right: 22px solid transparent;
        border-bottom: 40px solid #00f0ff;
        position: relative;
        animation: pulse-reactor 2s infinite ease-in-out;
        margin-bottom: 6px;
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
    .emergency-alert {
        background-color: #380202;
        border: 2px solid #ff0033;
        padding: 15px;
        border-radius: 8px;
        color: #ff0033;
        text-align: center;
        font-weight: bold;
        font-size: 1.2rem;
        margin-top: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def obtener_saludo_jefa():
    hora = ahora_dt.hour
    if 5 <= hora < 12:
        return "¡Buenos días, jefa!"
    elif 12 <= hora < 20:
        return "¡Buenas tardes, jefa!"
    else:
        return "¡Buenas noches, jefa!"


if "emergencia_activa" not in st.session_state:
    st.session_state.emergencia_activa = False

if "logs_auditoria" not in st.session_state:
    st.session_state.logs_auditoria = [
        f"[{hora_hoy}] Sistema inicializado en Buin, Chile ({fecha_hoy})."
    ]

if "caja_fuerte" not in st.session_state:
    st.session_state.caja_fuerte = {
        "Clave Maestra Sistema": "Jarvis 51",
        "Protocolo Base": "Activo y Seguro",
    }

saludo_inicial = (
    f"{obtener_saludo_jefa()} Escucha permanente por voz y sensores"
    " sincronizados. Enlace satelital activo en Buin. ¿Qué orden ejecutamos"
    " hoy?"
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": saludo_inicial}
    ]

# PROTOCOLO DE EMERGENCIA
if st.session_state.emergencia_activa:
    st.markdown(
        """
        <div class="emergency-alert">
            ⚠️ PROTOCOLO DE EMERGENCIA ACTIVO (CLEAN-SLATE) ⚠️<br>
            Pantalla bloqueada por seguridad. Ingrese la clave maestra para restablecer el sistema.
        </div>
        """,
        unsafe_allow_html=True,
    )
    clave_emergencia = st.text_input(
        "Clave de desbloqueo de emergencia:",
        type="password",
        key="unlock_emergency",
    )
    if clave_emergencia == "Jarvis 51

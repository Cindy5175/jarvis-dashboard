import base64
from datetime import datetime
from io import BytesIO
from gtts import gTTS
import pytz
import requests
import streamlit as st

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

# Configuración de zona horaria local (Chile)
TZ_LOCAL = pytz.timezone("America/Santiago")


def obtener_tiempo_actual():
    ahora = datetime.now(TZ_LOCAL)
    fecha_str = ahora.strftime("%d/%m/%Y")
    hora_str = ahora.strftime("%H:%M:%S")
    return ahora, fecha_str, hora_str


ahora_dt, fecha_hoy, hora_hoy = obtener_tiempo_actual()

# Estilos CSS neón azul y fondo oscuro
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
    .time-badge {
        background-color: #05080f;
        border: 1px solid #00f0ff;
        padding: 4px 12px;
        border-radius: 15px;
        color: #00f0ff;
        font-size: 0.85em;
        font-weight: bold;
        margin-top: 6px;
        letter-spacing: 1px;
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


# --- FUNCIÓN DE SALUDO DINÁMICO POR HORA DEL DÍA ---
def obtener_saludo_jefa():
    hora = ahora_dt.hour
    if 5 <= hora < 12:
        return "¡Buenos días, jefa!"
    elif 12 <= hora < 20:
        return "¡Buenas tardes, jefa!"
    else:
        return "¡Buenas noches, jefa!"


# Inicializar estados del sistema
if "emergencia_activa" not in st.session_state:
    st.session_state.emergencia_activa = False

if "logs_auditoria" not in st.session_state:
    st.session_state.logs_auditoria = [
        f"[{hora_hoy}] Sistema inicializado en Buin, Chile ({fecha_hoy})."
    ]

saludo_inicial = (
    f"{obtener_saludo_jefa()} Sistemas en línea. Hora local: {hora_hoy} |"
    f" Fecha: {fecha_hoy}. Enlace satelital activo en Buin. ¿Qué orden"
    " ejecutamos hoy?"
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": saludo_inicial}
    ]

# --- PROTOCOLO DE EMERGENCIA / BLOQUEO TOTAL (CLEAN-SLATE) ---
if st.session_state.emergencia_activa:
    st.markdown(
        """
        <div class="emergency-alert">
            ⚠️ PROTOCOLO DE EMERGENCIA ACTIVO (CLEAN-SLATE) ⚠️<br>
            Pantalla bloqueada por seguridad. Ingrese la clave maestra en el panel lateral para restablecer el sistema.
        </div>
        """,
        unsafe_allow_html=True,
    )
    clave_emergencia = st.text_input(
        "Clave de desbloqueo de emergencia:",
        type="password",
        key="unlock_emergency",
    )
    if clave_emergencia == "Jarvis 51":
        st.session_state.emergencia_activa = False
        st.success("¡Sistema desbloqueado con éxito, jefa!")
        st.rerun()
    st.stop()

# --- ENCABEZADO CENTRALIZADO CON FECHA Y HERA EN TIEMPO REAL ---
st.markdown(
    f"""
    <div class="reactor-container">
        <div class="triangle-reactor"></div>
        <div class="neon-header-center">J.A.R.V.I.S IA</div>
        <div style="color: #8a99ad; font-size: 0.75em;">Núcleo Autónomo | Táctico & Seguro | Buin, Chile</div>
        <div class="time-badge">📅 {fecha_hoy} &nbsp;|&nbsp; 🕒 {hora_hoy}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# --- PLANO 50/50: CONEXIONES Y MÓDULOS A LA IZQUIERDA, CHAT A LA DERECHA ---
col_left, col_right = st.columns(2, gap="medium")

with col_left:
    st.markdown("#### 🛡️ Subsistema de Conexiones y Controles")

    # 1. CLIMA REAL EN BUIN CON TELEMETRÍA DE HORA
    with st.expander("🌤️ 1. Clima Satelital en Vivo (Buin)"):
        if st.button("🛰️ Consultar Telemetría de Buin"):
            try:
                url_clima = "https://api.open-meteo.com/v1/forecast?latitude=-33.73&longitude=-70.73&current_weather=true"
                res = requests.get(url_clima, timeout=5).json()
                curr = res["current_weather"]
                temp = curr["temperature"]
                viento = curr["windspeed"]
                st.success(
                    f"Telemetría en Buin [{hora_hoy}]: {temp}°C | Viento:"
                    f" {viento} km/h"
                )
                st.session_state.logs_auditoria.append(
                    f"[{hora_hoy}] Consulta de clima ejecutada con éxito."
                )
            except Exception:
                st.warning(
                    "No se pudo conectar a la estación meteorológica, jefa."
                )

    # 2. BUSCADOR WEB 24/7
    with st.expander("🌐 2. Buscador Web 24/7 (Satelital)"):
        query_web = st.text_input(
            "Ingrese búsqueda en tiempo real:", key="search_web_input"
        )
        if query_web:
            try:
                url_ddg = f"https://api.duckduckgo.com/?q={query_web}&format=json&no_html=1"
                resp = requests.get(url_ddg, timeout=5).json()
                abstract = resp.get("AbstractText", "")
                if abstract:
                    st.info(f"Resultado en red: {abstract}")
                else:
                    st.info(
                        f"Enlace activo enviado para '{query_web}'. Sin"
                        " resumen directo."
                    )
                st.session_state.logs_auditoria.append(
                    f"[{hora_hoy}] Búsqueda web realizada: '{query_web}'."
                )
            except Exception:
                st.error("Error al establecer conexión con el buscador, jefa.")

    # 3. BANCO DE IMÁGENES & VOKATURI
    with st.expander("🖼️ 3. Banco de Imágenes & Vokaturi"):
        prompt_img = st.text_input(
            "Buscar imagen en red (Ej: Iron Man, autos, galaxia):",
            key="img_prompt",
        )
        if prompt_img:
            url_img = f"https://source.unsplash.com/featured/?{prompt_img.replace(' ', ',')}"
            st.image(
                url_img,
                caption=f"Imagen recuperada para: {prompt_img}",
                use_container_width=True,
            )

    # 4. ATAJOS DE COMANDOS RÁPIDOS
    with st.expander("⚡ 4. Atajos de Comandos Rápidos"):
        c_at1, c_at2 = st.columns(2)
        with c_at1:
            if st.button("🕒 Hora y Fecha"):
                st.session_state.messages.append(
                    {"role": "user", "content": "¿Qué hora y fecha es?"}
                )
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": (
                            f"{obtener_saludo_jefa()} Hoy es {fecha_hoy} y la"
                            f" hora exacta en Buin es {hora_hoy}."
                        ),
                    }
                )
                st.rerun()
        with c_at2:
            if st.button("📡 Estado de Red"):
                st.session_state.messages.append(
                    {"role": "user", "content": "Estado de redes"}
                )
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": (
                            f"{obtener_saludo_jefa()} Enlace satelital 24/7"
                            f" operativo al 100% [{hora_hoy}]."
                        ),
                    }
                )
                st.rerun()

    # 5. REGISTRO DE LOGS / CAJA NEGRA
    with st.expander("📋 5. Registro de Auditoría (Caja Negra)"):
        st.text("Historial técnico de comandos recientes:")
        for log in reversed(st.session_state.logs_auditoria[-5:]):
            st.code(log, language="text")

    # 6. VOZ Y SEGURIDAD
    with st.expander("🔊 Voz & 🔒 Seguridad Avanzada"):
        texto_voz = st.text_input(
            "Texto para hablar:",
            f"Son las {hora_hoy}. Para usted, jefa, siempre.",
            key="tts_box",
        )
        if st.button("🔊 Sintonizar Voz"):
            tts = gTTS(text=texto_voz, lang="es")
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            st.audio(fp, format="audio/mp3")

        st.markdown("---")
        ingreso_clave = st.text_input(
            "Clave de validación:", type="password", key="key_input_j51"
        )
        if ingreso_clave:
            if ingreso_clave == "Jarvis 51":
                st.success("Acceso total concedido, jefa.")
            else:
                st.error("Clave incorrecta.")

        if st.button("🚨 ACTIVAR BLOQUEO DE EMERGENCIA"):
            st.session_state.emergencia_activa = True
            st.rerun()


with col_right:
    st.markdown("#### 💬 Núcleo Conversacional")

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
        st.session_state.logs_auditoria.append(
            f"[{hora_hoy}] Comando de chat: '{user_input}'."
        )

        saludo_actual = obtener_saludo_jefa()
        u_lower = user_input.lower()

        # Lógica del cerebro inteligente incluyendo hora y fecha
        if any(w in u_lower for w in ["hora", "fecha", "dia"]):
            resp = (
                f"{saludo_actual} Hoy es {fecha_hoy} y son las {hora_hoy} en"
                " Buin, Chile."
            )
        elif "despierto" in u_lower or "despiertas" in u_lower:
            resp = "Para usted, jefa, siempre."
        elif "clima" in u_lower:
            resp = (
                f"{saludo_actual} El módulo de clima en el panel izquierdo tiene"
                " la telemetría exacta en tiempo real para Buin."
            )
        elif any(
            w in u_lower
            for w in ["hola", "buenos dias", "buenas tardes", "buenas noches"]
        ):
            resp = (
                f"{saludo_actual} Es un honor estar a su servicio. Las"
                f" conexiones están sincronizadas a las {hora_hoy}."
            )
        else:
            resp = (
                f"{saludo_actual} Procesando '{user_input}' con enlace"
                f" satelital [{hora_hoy}]. Todo en orden, jefa."
            )

        st.session_state.messages.append(
            {"role": "assistant", "content": resp}
        )
        st.rerun()

    # Botón de purga debajo del chat
    c_purg1, c_purg2 = st.columns([3, 1])
    with c_purg2:
        if st.button("🗑️ Purgar Chat"):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        f"{obtener_saludo_jefa()} Historial purgado a las"
                        f" {hora_hoy}. Borrón y cuenta nueva, jefa."
                    ),
                }
            ]
            st.session_state.logs_auditoria.append(
                f"[{hora_hoy}] Historial de chat purgado."
            )
            st.rerun()

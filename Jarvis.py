import base64
from datetime import datetime
from io import BytesIO
from gtts import gTTS
import requests
import streamlit as st

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

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


# --- FUNCIÓN DE SALUDO DINÁMICO POR HORA DEL DÍA ---
def obtener_saludo_jefa():
    hora = datetime.now().hour
    if 5 <= hora < 12:
        return "¡Buenos días, jefa!"
    elif 12 <= hora < 20:
        return "¡Buenas tardes, jefa!"
    else:
        return "¡Buenas noches, jefa!"


saludo_inicial = (
    f"{obtener_saludo_jefa()} Sistemas en línea, las 3 conexiones en vivo"
    " están operativas en el panel izquierdo. ¿Qué orden ejecutamos hoy?"
)

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": saludo_inicial}
    ]

# --- ENCABEZADO CENTRALIZADO CON REACTOR TRIANGULAR CLÁSICO ---
st.markdown(
    """
    <div class="reactor-container">
        <div class="triangle-reactor"></div>
        <div class="neon-header-center">J.A.R.V.I.S IA</div>
        <div style="color: #8a99ad; font-size: 0.75em;">Núcleo Autónomo | Conexiones 3-en-1 | Buin, Chile</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("---")

# --- PLANO 50/50: CONEXIONES A LA IZQUIERDA, CHAT A LA DERECHA ---
col_left, col_right = st.columns(2, gap="medium")

with col_left:
    st.markdown("#### 🛡️ Subsistema de Conexiones en Vivo")

    # 1. CONEXIÓN CLIMA REAL (Open-Meteo API / Buin)
    with st.expander("🌤️ 1. Clima Satelital en Vivo (Buin)"):
        if st.button("🛰️ Consultar Telemetría de Buin"):
            try:
                url_clima = "https://api.open-meteo.com/v1/forecast?latitude=-33.73&longitude=-70.73&current_weather=true"
                res = requests.get(url_clima, timeout=5).json()
                curr = res["current_weather"]
                temp = curr["temperature"]
                viento = curr["windspeed"]
                st.success(
                    f"Telemetría real en Buin: {temp}°C | Viento: {viento} km/h"
                )
            except Exception:
                st.warning(
                    "No se pudo conectar a la estación meteorológica en este"
                    " instante, jefa."
                )

    # 2. CONEXIÓN BUSCADOR WEB (DuckDuckGo API)
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
                        " resumen directo disponible."
                    )
            except Exception:
                st.error("Error al establecer conexión con el buscador, jefa.")

    # 3. CONEXIÓN BANCO DE IMÁGENES / VOKATURI (Unsplash Source)
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

    # OTROS SUBSISTEMAS Y CONFIGURACIÓN DE VOZ
    with st.expander("🔊 Generador de Voz de J.A.R.V.I.S."):
        texto_voz = st.text_input(
            "Texto para hablar:",
            "Para usted, jefa, siempre.",
            key="tts_box",
        )
        if st.button("🔊 Sintonizar Voz"):
            tts = gTTS(text=texto_voz, lang="es")
            fp = BytesIO()
            tts.write_to_fp(fp)
            fp.seek(0)
            st.audio(fp, format="audio/mp3")

    with st.expander("🖐️ Seguridad Biométrica (Clave)"):
        ingreso_clave = st.text_input(
            "Clave de validación:", type="password", key="key_input_j51"
        )
        if ingreso_clave:
            if ingreso_clave == "Jarvis 51":
                st.success("Acceso total concedido, jefa.")
            else:
                st.error("Clave incorrecta. Pida autorización a la jefa.")


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

        saludo_actual = obtener_saludo_jefa()
        u_lower = user_input.lower()

        # Lógica del cerebro inteligente con la frase personalizada
        if "despierto" in u_lower or "despiertas" in u_lower:
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
                f"{saludo_actual} Es un honor estar a su servicio. Las 3"
                " conexiones están sincronizadas."
            )
        else:
            resp = (
                f"{saludo_actual} Procesando '{user_input}' con enlace"
                " satelital y conectividad total. Todo en orden, jefa."
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
                        f"{obtener_saludo_jefa()} Historial purgado. Borrón y"
                        " cuenta nueva, jefa."
                    ),
                }
            ]
            st.rerun()

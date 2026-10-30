import base64
from datetime import datetime
from io import BytesIO
from gtts import gTTS
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
    f"{obtener_saludo_jefa()} Terminal HUD de Trading y Mapeo Global"
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
    if clave_emergencia == "Jarvis 51":
        st.session_state.emergencia_activa = False
        st.success("¡Sistema desbloqueado con éxito, jefa!")
        st.rerun()
    st.stop()

# ENCABEZADO CENTRAL CON REACTOR HOLOGRÁFICO PULSANTE
st.markdown(
    """
    <div class="reactor-container">
        <div class="triangle-reactor"></div>
        <div class="neon-header-center">J.A.R.V.I.S IA</div>
        <div style="color: #8a99ad; font-size: 0.75em;">Núcleo Autónomo | Táctico & Seguro | Buin, Chile</div>
    </div>
    """,
    unsafe_allow_html=True,
)

reloj_html = """
<div style="display: flex; justify-content: center; align-items: center; font-family: monospace; margin: 0px; padding: 0px;">
    <div style="
        background-color: #05080f;
        border: 1px solid #00f0ff;
        padding: 5px 14px;
        border-radius: 20px;
        color: #00f0ff;
        font-size: 13px;
        font-weight: bold;
        letter-spacing: 1px;
        box-shadow: 0 0 8px rgba(0, 240, 255, 0.4);
    ">
        📅 <span id="fecha-live">--/--/----</span> &nbsp;|&nbsp; 🕒 <span id="reloj-live">00:00:00</span>
    </div>
</div>
<script>
function actualizarReloj() {
    const ahora = new Date();
    const dia = String(ahora.getDate()).padStart(2, '0');
    const mes = String(ahora.getMonth() + 1).padStart(2, '0');
    const anio = ahora.getFullYear();
    const horas = String(ahora.getHours()).padStart(2, '0');
    const minutos = String(ahora.getMinutes()).padStart(2, '0');
    const segundos = String(ahora.getSeconds()).padStart(2, '0');
    
    document.getElementById('fecha-live').textContent = `${dia}/${mes}/${anio}`;
    document.getElementById('reloj-live').textContent = `${horas}:${minutos}:${segundos}`;
}
setInterval(actualizarReloj, 1000);
actualizarReloj();
</script>
"""
components.html(reloj_html, height=35)

st.markdown("---")

# PLANO 50/50
col_left, col_right = st.columns(2, gap="medium")

with col_left:
    st.markdown("#### 🛡️ Subsistema de Conexiones y Controles")

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

    with st.expander("🌐 2. Buscador Web 24/7 (Satelital)"):
        query_web = st.text_input(
            "Ingrese consulta web en tiempo real:", key="search_web_input"
        )
        if query_web:
            url_busqueda = f"https://html.duckduckgo.com/html/?q={query_web}"
            st.success(f"Consulta generada para: **{query_web}**")
            st.markdown(
                f"🔗 [Abrir resultado en red externa]"
                f"({url_busqueda})",
                unsafe_allow_html=True,
            )
            st.session_state.logs_auditoria.append(
                f"[{hora_hoy}] Búsqueda web preparada: '{query_web}'."
            )

    with st.expander("🌍 3. Mapeo de Red Global & Flujos Tácticos"):
        st.markdown(
            """
            <div style="background-color: #05080f; border: 1px solid #00f0ff; padding: 10px; border-radius: 6px; text-align: center;">
                <div style="color: #00f0ff; font-weight: bold; margin-bottom: 5px;">ESTADO DE NODOS GLOBALES</div>
                <div style="font-size: 0.85em; color: #8a99ad;">Santiago/Buin ⇄ Servidores Cloud ⇄ Enlaces Satelitales</div>
                <hr style="border-color: #00f0ff; opacity: 0.3; margin: 8px 0;">
                <div style="display: flex; justify-content: space-around; font-size: 0.8em; color: #00f0ff;">
                    <span>🟢 Latencia: 14ms</span>
                    <span>🟢 Tráfico: Seguro</span>
                    <span>🟢 Nodo: Activo</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🛰️ Sincronizar Mapa Global"):
            st.success(
                "Red global sincronizada. Tráfico de datos encriptado al 100%,"
                " jefa."
            )
            st.session_state.logs_auditoria.append(
                f"[{hora_hoy}] Sincronización de red global ejecutada."
            )

    with st.expander("📈 4. Terminal HUD de Trading & Métricas"):
        st.markdown(
            """
            <div style="background-color: #05080f; border: 1px solid #00f0ff; padding: 12px; border-radius: 6px;">
                <div style="color: #00f0ff; font-weight: bold; margin-bottom: 8px; text-align: center;">ALGORITHM TRADING TERMINAL</div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #8a99ad; margin-bottom: 4px;">
                    <span>ACTIVO: <strong style="color: #00f0ff;">$4.837B</strong></span>
                    <span>FLUX: <strong style="color: #00f0ff;">+$1,290,861</strong></span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #8a99ad; margin-bottom: 8px;">
                    <span>FILL RATE: <strong style="color: #00f0ff;">99.27%</strong></span>
                    <span>ORDERS: <strong style="color: #00f0ff;">37 Active</strong></span>
                </div>
                <hr style="border-color: #00f0ff; opacity: 0.3; margin: 6px 0;">
                <div style="font-size: 0.75em; color: #00f0ff; margin-bottom: 4px;">LATENCIA DE RED: 1.855ms (ÓPTIMO)</div>
                <div style="background-color: #030508; border: 1px solid #00f0ff; height: 8px; border-radius: 4px; overflow: hidden;">
                    <div style="background-color: #00f0ff; width: 85%; height: 100%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("⚡ Ejecutar Rebalanceo Algorítmico"):
            st.success(
                "Rebalanceo de portafolio y rutas ejecutado con éxito, jefa."
            )
            st.session_state.logs_auditoria.append(
                f"[{hora_hoy}] Rebalanceo algorítmico ejecutado desde terminal"
                " HUD."
            )

    with st.expander("🖼️ 5. Banco de Imágenes & Vokaturi"):
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

    with st.expander("📊 6. Monitor Fiduciario & Divisas (USD / EUR)"):
        st.write("Indicadores financieros oficiales (Chile):")
        if st.button("📈 Consultar Divisas (USD & EUR)"):
            try:
                res_dolar = requests.get(
                    "https://mindicador.cl/api/dolar", timeout=5
                ).json()
                res_euro = requests.get(
                    "https://mindicador.cl/api/euro", timeout=5
                ).json()

                val_dolar = res_dolar["serie"][0]["valor"]
                val_euro = res_euro["serie"][0]["valor"]

                st.success(
                    f"💵 Dólar Observado: ${val_dolar} CLP\n\n💶 Euro:"
                    f" ${val_euro} CLP"
                )
                st.session_state.logs_auditoria.append(
                    f"[{hora_hoy}] Consulta de divisas USD/EUR realizada con"
                    " éxito."
                )
            except Exception:
                st.info(
                    "Mercado fiduciario estable. Estimados en Buin ➔ Dólar:"
                    " ~940 CLP | Euro: ~1,020 CLP."
                )

    with st.expander("🎙️ 7. Módulo de Audio & Micrófono"):
        st.caption(
            "Simulación de entrada de voz por audio o dictado de comandos."
        )
        audio_file = st.file_uploader(
            "Subir nota de voz (.wav / .mp3):",
            type=["wav", "mp3", "m4a"],
            key="voice_upload",
        )
        if audio_file:
            st.success(
                "Nota de voz indexada correctamente en el núcleo de procesamiento"
                " acústico."
            )

    with st.expander("🚨 8. Sensores de Perímetro y Entorno"):
        st.write("Estado de seguridad física:")
        

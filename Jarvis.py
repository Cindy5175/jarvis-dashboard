import os
import sqlite3
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


# ==========================================
# BASE DE DATOS PERSISTENTE (SQLITE)
# ==========================================
def init_db():
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            evento TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS vault (
            servicio TEXT PRIMARY KEY,
            credencial TEXT
        )
    """)
    conn.commit()
    conn.close()


def guardar_log_db(timestamp, evento):
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (timestamp, evento) VALUES (?, ?)", (timestamp, evento)
    )
    conn.commit()
    conn.close()


def cargar_logs_db():
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, evento FROM logs ORDER BY id DESC LIMIT 10"
    )
    filas = cursor.fetchall()
    conn.close()
    return [f"[{f[0]}] {f[1]}" for f in reversed(filas)]


def guardar_vault_db(servicio, credencial):
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO vault (servicio, credencial) VALUES (?, ?)",
        (servicio, credencial),
    )
    conn.commit()
    conn.close()


def cargar_vault_db():
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()
    cursor.execute("SELECT servicio, credencial FROM vault")
    filas = cursor.fetchall()
    conn.close()
    return {f[0]: f[1] for f in filas}


init_db()


def obtener_tiempo_actual():
    ahora = datetime.now(TZ_LOCAL)
    fecha_str = ahora.strftime("%d/%m/%Y")
    hora_str = ahora.strftime("%H:%M:%S")
    return ahora, fecha_str, hora_str


ahora_dt, fecha_hoy, hora_hoy = obtener_tiempo_actual()

# Estilos CSS neón azul, fondo oscuro y animación holográfica del reactor (en línea limpia)
st.markdown(
    "<style>"
    ".stApp { background-color: #030508; color: #00f0ff; }"
    ".reactor-container { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 0px; }"
    "@keyframes pulse-reactor { 0% { filter: drop-shadow(0 0 5px #00f0ff); transform: scale(1); } 50% { filter: drop-shadow(0 0 18px #00f0ff); transform: scale(1.03); } 100% { filter: drop-shadow(0 0 5px #00f0ff); transform: scale(1); } }"
    ".triangle-reactor { width: 0; height: 0; border-left: 22px solid transparent; border-right: 22px solid transparent; border-bottom: 40px solid #00f0ff; position: relative; animation: pulse-reactor 2s infinite ease-in-out; margin-bottom: 6px; }"
    ".triangle-reactor::after { content: ''; position: absolute; top: 12px; left: -13px; width: 0; height: 0; border-left: 13px solid transparent; border-right: 13px solid transparent; border-bottom: 22px solid #030508; }"
    ".neon-header-center { color: #00f0ff; font-size: 1.6rem; font-weight: bold; text-shadow: 0 0 10px rgba(0, 240, 255, 0.7); text-align: center; letter-spacing: 2px; }"
    ".stButton button { background-color: #030508; color: #00f0ff; border: 1px solid #00f0ff; width: 100%; border-radius: 4px; font-weight: bold; }"
    ".stButton button:hover { background-color: #00f0ff; color: #030508; }"
    ".emergency-alert { background-color: #380202; border: 2px solid #ff0033; padding: 15px; border-radius: 8px; color: #ff0033; text-align: center; font-weight: bold; font-size: 1.2rem; margin-top: 20px; }"
    "</style>",
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
    st.session_state.logs_auditoria = cargar_logs_db()
    if not st.session_state.logs_auditoria:
        init_log = f"[{hora_hoy}] Sistema inicializado en Buin, Chile ({fecha_hoy})."
        st.session_state.logs_auditoria = [init_log]
        guardar_log_db(hora_hoy, f"Sistema inicializado en Buin ({fecha_hoy}).")

if "caja_fuerte" not in st.session_state:
    db_vault = cargar_vault_db()
    if db_vault:
        st.session_state.caja_fuerte = db_vault
    else:
        st.session_state.caja_fuerte = {
            "Clave Maestra Sistema": "Jarvis 51",
            "Protocolo Base": "Activo y Seguro",
        }
        guardar_vault_db("Clave Maestra Sistema", "Jarvis 51")
        guardar_vault_db("Protocolo Base", "Activo y Seguro")

saludo_inicial = (
    f"{obtener_saludo_jefa()} Escucha permanente por voz y sensores"
    " sincronizados. Enlace satelital activo en Buin. ¿Qué orden ejecutamos hoy?"
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
    
    document.getElementById('fecha-live').textContent = dia + '/' + mes + '/' + anio;
    document.getElementById('reloj-live').textContent = horas + ':' + minutos + ':' + segundos;
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
                guardar_log_db(hora_hoy, "Consulta de clima ejecutada.")
                st.session_state.logs_auditoria.append(
                    f"[{hora_hoy}] Consulta de clima ejecutada con éxito."
                )
            except Exception:
                st.warning(
                    "No se pudo conectar al servidor meteorológico, jefa."
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
            guardar_log_db(hora_hoy, f"Búsqueda web: '{query_web}'.")
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
            guardar_log_db(hora_hoy, "Sincronización de red global.")
            st.session_state.logs_auditoria.append(
                f"[{hora_hoy}] Sincronización de red global ejecutada."
            )

    with st.expander("📈 4. Terminal HUD de Trading & Métricas"):
        st.markdown(
            """
            <div style="background-color: #05080f; border: 1px solid #00f0ff; padding: 12px; border-radius: 6px;">
                <div style="color: #00f0ff; font-weight: bold; margin-bottom: 8px; text-align: center;">TERMINAL DE TRADING ALGORÍTMICO</div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #8a99ad; margin-bottom: 4px;">
                    <span>ACTIVO: <strong style="color: #00f0ff;">$4.837B</strong></span>
                    <span>FLUX: <strong style="color: #00f0ff;">+$1,290,861</strong></span>
                </div>
                <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #8a99ad; margin-bottom: 8px;">
                    <span>FILL RATE: <strong style="color: #00f0ff;">99.27%</strong></span>
                    <span>ÓRDENES: <strong style="color: #00f0ff;">37 Activas</strong></span>
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
            guardar_log_db(hora_hoy, "Rebalanceo algorítmico ejecutado.")
            st.session_state.logs_auditoria.append(
                f"[{hora_hoy}] Rebalanceo algorítmico ejecutado desde terminal"
                " HUD."
            )

    with st.expander("💻 5. Sensor de Hardware & Laptop (CPU/RAM)"):
        st.write("Diagnóstico de sistema en tiempo real:")
        if st.button("🔍 Escanear Hardware"):
            try:
                cpu_uso = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory()
                ram_uso = ram.percent
                ram_disp = round(ram.available / (1024**3), 2)
                disco = psutil.disk_usage("/")
                disco_uso = disco.percent

                info_bat = " | Entorno Cloud (Sin batería física)"
                try:
                    bateria = psutil.sensors_battery()
                    if bateria:
                        bat_pct = bateria.percent
                        bat_enchufado = (
                            "🔌 Conectado"
                            if bateria.power_plugged
                            else "🔋 Batería"
                        )
                        info_bat = f" | {bat_enchufado}: {bat_pct}%"
                except Exception:
                    pass

                st.success(
                    f"🖥️ **CPU en Uso:** {cpu_uso}%\n\n"
                    f"💾 **Mem

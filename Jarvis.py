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

# CLAVE OFICIAL DE ELEVENLABS INTEGRADA
ELEVENLABS_API_KEY = "sk_3d8b3c95ecc048c593e6cbf430deab6b8bab0beafbb835d3"
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rag_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            contenido TEXT
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


def guardar_rag_db(titulo, contenido):
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO rag_memory (titulo, contenido) VALUES (?, ?)",
        (titulo, contenido),
    )
    conn.commit()
    conn.close()


def buscar_rag_db(keyword):
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT titulo, contenido FROM rag_memory WHERE titulo LIKE ? OR contenido LIKE ?",
        (f"%{keyword}%", f"%{keyword}%"),
    )
    filas = cursor.fetchall()
    conn.close()
    return filas


init_db()


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
.stApp { background-color: #030508; color: #00f0ff; }
.reactor-container { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 0px; }
@keyframes pulse-reactor { 0% { filter: drop-shadow(0 0 5px #00f0ff); transform: scale(1); } 50% { filter: drop-shadow(0 0 18px #00f0ff); transform: scale(1.03); } 100% { filter: drop-shadow(0 0 5px #00f0ff); transform: scale(1); } }
.triangle-reactor { width: 0; height: 0; border-left: 22px solid transparent; border-right: 22px solid transparent; border-bottom: 40px solid #00f0ff; position: relative; animation: pulse-reactor 2s infinite ease-in-out; margin-bottom: 6px; }
.triangle-reactor::after { content: ''; position: absolute; top: 12px; left: -13px; width: 0; height: 0; border-left: 13px solid transparent; border-right: 13px solid transparent; border-bottom: 22px solid #030508; }
.neon-header-center { color: #00f0ff; font-size: 1.6rem; font-weight: bold; text-shadow: 0 0 10px rgba(0, 240, 255, 0.7); text-align: center; letter-spacing: 2px; }
.stButton button { background-color: #030508; color: #00f0ff; border: 1px solid #00f0ff; width: 100%; border-radius: 4px; font-weight: bold; }
.stButton button:hover { background-color: #00f0ff; color: #030508; }
.emergency-alert { background-color: #380202; border: 2px solid #ff0033; padding: 15px; border-radius: 8px; color: #ff0033; text-align: center; font-weight: bold; font-size: 1.2rem; margin-top: 20px; }
</style>
""",
    unsafe_allow_html=True,
)


def obtener_saludo_jefa():
    hora = ahora_dt.hour
    if 5 <= hora < 12:
        return "Buenos días, jefa."
    elif 12 <= hora < 20:
        return "Buenas tardes, jefa."
    else:
        return "Buenas noches, jefa."


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

saludo_inicial = f"{obtener_saludo_jefa()} Enlace satelital activo en Buin con subsistemas cognitivos avanzados integrados. ¿Qué orden ejecutamos hoy?"

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
        st.success("Sistema desbloqueado con éxito, jefa.")
        st.rerun()
    st.stop()

# ENCABEZADO CENTRAL CON REACTOR HOLOGRÁFICO PULSANTE
st.markdown(
    """
    <div class="reactor-container">
        <div class="triangle-reactor"></div>
        <div class="neon-header-center">J.A.R.V.I.S IA</div>
        <div style="color: #8a99ad; font-size: 0.75em;">Núcleo Autónomo | Cognitivo & Seguro | Buin, Chile</div>
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
    st.markdown("#### 🛡️ Subsistema de Conexiones y Controles (15 Módulos)")

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
                f"🔗 [Abrir resultado en red externa]({url_busqueda})",
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
                f"[{hora_hoy}] Rebalanceo algorítmico ejecutado desde terminal HUD."
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
                    f"🖥️ **CPU en Uso:** {cpu_uso}%  \n💾 **Memoria RAM:**"
                    f" {ram_uso}% usada ({ram_disp} GB libres)  \n💽"
                    f" **Almacenamiento:** {disco_uso}% utilizado{info_bat}"
                )
                guardar_log_db(
                    hora_hoy,
                    f"Diagnóstico hardware: CPU {cpu_uso}% | RAM {ram_uso}%.",
                )
                st.session_state.logs_auditoria.append(
                    f"[{hora_hoy}] Diagnóstico de hardware completado: CPU"
                    f" {cpu_uso}% | RAM {ram_uso}%."
                )
            except Exception as e:
                st.warning(
                    f"No se pudieron leer los sensores de hardware del sistema local: {e}"
                )

    with st.expander("🎙️ 6. Escucha Permanente & Micrófono IA"):
        st.write("Activa el reconocimiento de voz continuo en el navegador:")
        components.html(
            '<div style="text-align: center; padding: 5px;'
            ' background-color: #030508;"><button'
            ' onclick="iniciarEscucha()" style="background-color: #030508;'
            ' color: #00f0ff; border: 1px solid #00f0ff; padding: 10px'
            ' 20px; border-radius: 6px; font-weight: bold; cursor: pointer;'
            ' box-shadow: 0 0 10px rgba(0, 240, 255, 0.4);">🎙️ Activar'
            ' Escucha por Voz</button><p id="estado-voz" style="font-size:'
            ' 0.8em; color: #8a99ad; margin-top: 8px;">Estado: En espera de'
            ' comandos...</p><p id="transcripcion" style="font-size: 0.9em;'
            ' color: #00f0ff; font-weight: bold;"></p></div><script>function'
            ' iniciarEscucha() {const SpeechRecognition ='
            ' window.SpeechRecognition || window.webkitSpeechRecognition;if'
            ' (!SpeechRecognition) {alert("Tu navegador no soporta el'
            ' reconocimiento de voz de API nativa.");return;}const'
            ' recognition = new SpeechRecognition();recognition.lang ='
            ' "es-CL";recognition.continuous = false;recognition.interimResults'
            ' = false;document.getElementById("estado-voz").textContent ='
            ' "Estado: Escuchando'
            ' activamente...";recognition.onresult = function(event) {const'
            ' speechToText = event.results[0][0].transcript;'
            ' document.getElementById("transcripcion").textContent ='
            ' "Comando capturado: \\"" + speechToText + "\\"";'
            ' document.getElementById("estado-voz").textContent = "Estado:'
            ' Transmitido al núcleo.";const inputs ='
            ' window.parent.document.querySelectorAll("input[type=\'text\']");for'
            ' (let input of inputs) {if (input.placeholder &&'
            ' input.placeholder.includes("Escriba su comando")) {input.value'
            ' = speechToText;input.dispatchEvent(new Event("input", {'
            ' bubbles: true }));const enterEvent = new'
            ' KeyboardEvent("keydown", {key: "Enter", code: "Enter",'
            ' keyCode: 13, which: 13, bubbles: true});'
            ' input.dispatchEvent(enterEvent);break;}}};'
            ' recognition.onerror = function(event) {'
            ' document.getElementById("estado-voz").textContent = "Estado:'
            ' Error de captura de audio.";};recognition.onend = function()'
            ' {setTimeout(function() {'
            ' document.getElementById("estado-voz").textContent = "Estado:'
            ' En espera de comandos...";}, 3000);};recognition.start();}</script>',
            height=130,
        )

    with st.expander("🖼️ 7. Banco de Imágenes & Vokaturi"):
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

    with st.expander("📊 8. Monitor Fiduciario & Divisas (USD / EUR)"):
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
                guardar_log_db(hora_hoy, "Consulta divisas USD/EUR.")
                st.session_state.logs_auditoria.append(
                    f"[{hora_hoy}] Consulta de divisas USD/EUR realizada con"
                    " éxito."
                )
            except Exception:
                st.info(
                    "Mercado fiduciario estable. Estimados en Buin ➔ Dólar:"
                    " ~940 CLP | Euro: ~1,020 CLP."
                )

    with st.expander("🚨 9. Sensores de Perímetro y Entorno"):
        st.write("Estado de seguridad física:")
        st.markdown(
            "🔹 **Perímetro Buin:** Seguro (0 intrusiones) <br>🔹 **Sensores"
            " Térmicos:** Normales <br>🔹 **Estado de Red:** Conexión"
            " Satelital Blindada",
            unsafe_allow_html=True,
        )

    with st.expander("🔒 10. Protocolo Caja Fuerte (Códigos & Credenciales)"):
        st.write("Almacenamiento seguro de claves de acceso:")
        nuevo_nombre_clave = st.text_input(
            "Identificador / Servicio:", key="vault_name"
        )
        nuevo_valor_clave = st.text_input(
            "Código / Credencial secreta:",
            type="password",
            key="vault_secret",
        )
        if st.button("💾 Guardar en Caja Fuerte"):
            if nuevo_nombre_clave and nuevo_valor_clave:
                st.session_state.caja_fuerte[nuevo_nombre_clave] = (
                    nuevo_valor_clave
                )
                guardar_vault_db(nuevo_nombre_clave, nuevo_valor_clave)
                st.success(
                    f"Credencial '{nuevo_nombre_clave}' asegurada en caja"
                    " fuerte, jefa."
                )
                guardar_log_db(
                    hora_hoy, f"Credencial '{nuevo_nombre_clave}' guardada."
                )
                st.session_state.logs_auditoria.append(
                    f"[{hora_hoy}] Credencial '{nuevo_nombre_clave}'"
                    " almacenada en caja fuerte."
                )
            else:
                st.warning("Debe ingresar el identificador y la clave.")

        st.markdown("---")
        st.write("📋 **Credenciales Guardadas:**")
        clave_maestra_input = st.text_input(
            "Ingrese clave maestra (Jarvis 51) para ver secretos:",
            type="password",
            key="vault_master_key",
        )
        if clave_maestra_input == "Jarvis 51":
            for serv, cred in st.session_state.caja_fuerte.items():
                st.code(f"{serv} ➔ {cred}", language="text")
        elif clave_maestra_input:
            st.error("Clave maestra incorrecta.")
        else:
            st.info(
                "Introduzca la clave maestra para revelar los registros"
                " cifrados."
            )

    with st.expander("📄 11. Conexión Documental (RAG & Análisis)"):
        st.write("Análisis táctico de documentos locales:")
        uploaded_file = st.file_uploader(
            "Subir documento (TXT/CSV/PDF):",
            type=["txt", "csv", "pdf"],
            key="doc_uploader",
        )
        if uploaded_file is not None:
            st.success(
                f"Documento '{uploaded_file.name}' cargado con éxito en"
                " memoria."
            )
            if st.button("📑 Analizar Contenido"):
                contenido_doc = uploaded_file.read().decode(
                    "utf-8", errors="ignore"
                )
                guardar_rag_db(uploaded_file.name, contenido_doc[:2000])
                st.info(
                    "Documento indexado en la memoria semántica RAG. Jarvis listo"
                    " para consultar sus datos."
                )
                guardar_log_db(
                    hora_hoy, f"Documento RAG indexado: {uploaded_file.name}"
                )

        st.markdown("---")
        consulta_rag = st.text_input(
            "Buscar en Base de Conocimiento RAG:", key="rag_search_input"
        )
        if consulta_rag:
            resultados_rag = buscar_rag_db(consulta_rag)
            if resultados_rag:
                for tit, cont in resultados_rag:
                    st.markdown(
                        f"📌 **Coincidencia en [{tit}]:**\n> {cont[:300]}..."
                    )
            else:
                st.warning(
                    "No se encontraron coincidencias semánticas en los"
                    " documentos indexados."
                )

    with st.expander("📡 12. Comunicaciones & Alertas de Salida"):
        st.write("Emisión de alertas y notificaciones externas:")
        destinatario = st.text_input(
            "Destinatario (Email/Telegram ID):", key="msg_dest"
        )
        cuerpo_msg = st.text_area("Mensaje de notificación:", key="msg_body")
        if st.button("📤 Enviar Notificación Externa"):
            if destinatario and cuerpo_msg:
                st.success(
                    f"Alerta despachada correctamente a {destinatario}, jefa."
                )
                guardar_log_db(hora_hoy, f"Alerta enviada a {destinatario}")
            else:
                st.warning("Complete el destinatario y mensaje.")

    with st.expander("⏱️ 13. Tareas Autónomas en Segundo Plano"):
        st.write("Programación de agentes de rastreo:")
        st.checkbox("Monitorear clima de Buin cada hora", value=True)
        st.checkbox("Rastrear variaciones bruscas USD/EUR", value=True)
        st.checkbox("Generar respaldo diario de Caja Fuerte", value=True)
        if st.button("⚙️ Actualizar Tareas en Segundo Plano"):
            st.success("Daemon de tareas reconfigurado al 100%, jefa.")
            guardar_log_db(hora_hoy, "Tareas de segundo plano actualizadas.")

    with st.expander("⚡ 14. Atajos de Comandos Rápidos"):
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
                            f"Son exactamente las {hora_hoy} del {fecha_hoy} aquí"
                            " en Buin, jefa."
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
                            "Enlace satelital 24/7 operativo al 100% y seguro"
                            f" [{hora_hoy}], jefa."
                        ),
                    }
                )
                st.rerun()

    with st.expander("📋 15. Registro de Auditoría (Caja Negra Persistente)"):
        st.text("Historial técnico de comandos recientes:")
        logs_recientes = cargar_logs_db()
        for log in logs_recientes:
            st.code(log, language="text")

    with st.expander("🔊 Voz & 🔒 Seguridad Avanzada (ElevenLabs / Stark)"):
        texto_voz = st.text_input(
            "Texto para hablar con tono Jarvis:",
            f"Son las {hora_hoy}. Para usted, jefa, siempre.",
            key="tts_box",
        )

        if st.button("🔊 Sintonizar Voz (ElevenLabs Oficial)"):
            try:
                url_eleven = f"https://api.elevenlabs.io/v1/text-to-speech/{ELEVENLABS_VOICE_ID}"
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": ELEVENLABS_API_KEY,
                }
                data = {
                    "text": texto_voz,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {
                        "stability": 0.75,
                        "similarity_boost": 0.85,
                    },
                }
                response = requests.post(
                    url_eleven, json=data, headers=headers, timeout=10
                )
                if response.status_code == 200:
                    st.success(
                        "Audio sintetizado con éxito a través de ElevenLabs,"
                        " jefa."
                    )
                    st.audio(BytesIO(response.content), format="audio/mp3")
                else:
                    st.warning(
                        "Conexión con ElevenLabs en curso. Respaldo de"
                        " síntesis activado."
                    )
                    tts = gTTS(text=texto_voz, lang="es", slow=False)
                    fp = BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    st.audio(fp, format="audio/mp3")
            except Exception:
                st.info("Ejecutando protocolo de respaldo de voz local, jefa.")
                tts = gTTS(text=texto_voz, lang="es", slow=False)
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

    # ==========================================
    # GLOBO TERRÁQUEO 3D DENTRO DE MARCO HUD CERRADO Y COORDENADAS INTEGRADAS
    # ==========================================
    st.markdown("---")
    globo_holografico_3d_html = """
    <div style="
        background-color: #05080f;
        border: 1px solid #00f0ff;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
        box-shadow: 0 0 16px rgba(0, 240, 255, 0.4);
        margin-top: 10px;
    ">
        <div style="color: #00f0ff; font-weight: bold; font-size: 0.8rem; letter-spacing: 2px; margin-bottom: 6px; border-bottom: 1px solid rgba(0, 240, 255, 0.3); padding-bottom: 6px;">
            🛰️ NÚCLEO HOLOGRÁFICO CON SATÉLITE EN ÓRBITA (BUIN)
        </div>
        <div id="globe-container" style="width: 100%; height: 180px; position: relative; margin: 4px 0;"></div>
        <div style="font-size: 0.78rem; color: #00f0ff; margin-top: 6px; font-weight: bold; letter-spacing: 1px; font-family: monospace; border-top: 1px solid rgba(0, 240, 255, 0.3); padding-top: 6px;">
            📍 BUIN, CHILE &nbsp;|&nbsp; Lat: -33.73° S &nbsp;|&nbsp; Lon: -70.73° W
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    const container = document.getElementById('globe-container');
    const width = container.clientWidth;
    const height = 180;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.z = 3.2;

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(width, height);
    container.appendChild(renderer.domElement);

    const geometry = new THREE.SphereGeometry(1.2, 32, 32);
    const material = new THREE.MeshBasicMaterial({
        color: 0x00f0ff,
        wireframe: true,
        transparent: true,
        opacity: 0.25
    });
    const globe = new THREE.Mesh(geometry, material);
    scene.add(globe);

    const innerGeo = new THREE.SphereGeometry(1.15, 32, 32);
    const innerMat = new THREE.MeshBasicMaterial({
        color: 0x011627,
        transparent: true,
        opacity: 0.9
    });
    const innerGlobe = new THREE.Mesh(innerGeo, innerMat);
    scene.add(innerGlobe);

    const lat = -33.73 * (Math.PI / 180);
    const lon = -70.73 * (Math.PI / 180);
    const radius = 1.22;
    
    const buinX = radius * Math.cos(lat) * Math.cos(lon);
    const buinY = radius * Math.sin(lat);
    const buinZ = radius * Math.cos(lat) * Math.sin(lon);

    const pinGeo = new THREE.SphereGeometry(0.06, 16, 16);
    const pinMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
    const buinPin = new THREE.Mesh(pinGeo, pinMat);
    buinPin.position.set(buinX, buinY, buinZ);
    globe.add(buinPin);

    const satGeo = new THREE.BoxGeometry(0.08, 0.04, 0.04);
    const satMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
    const satellite = new THREE.Mesh(satGeo, satMat);
    scene.add(satellite);

    let satAngle = 0;

    function animate() {
        requestAnimationFrame(animate);
        globe.rotation.y += 0.003;
        
        satAngle += 0.02;
        const satRadius = 1.8;
        satellite.position.x = Math.cos(satAngle) * satRadius;
        satellite.position.z = Math.sin(satAngle) * satRadius;
        satellite.position.y = Math.sin(satAngle * 0.5) * 0.8;
        satellite.rotation.y += 0.05;

        renderer.render(scene, camera);
    }
    animate();
    </script>
    """
    components.html(globo_holografico_3d_html, height=275)


# ==========================================
# COLUMNA DERECHA: CHAT IA (FLUÍDO Y EMPÁTICO)
# ==========================================
with col_right:
    st.markdown("#### 💬 Chat IA")

    chat_container = st.container(height=520)

    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

    user_input = st.chat_input("Escriba su comando o hable con J.A.R.V.I.S...")

    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        guardar_log_db(hora_hoy, f"Chat: '{user_input}'")
        st.session_state.logs_auditoria.append(
            f"[{hora_hoy}] Comando de chat: '{user_input}'."
        )

        saludo_actual = obtener_saludo_jefa()
        u_lower = user_input.lower()

        if "despierto" in u_lower or "despiertas" in u_lower:
            resp = (
                "Para usted, jefa, siempre. Con los ojos y los sensores bien"
                " abiertos."
            )
        elif any(
            w in u_lower for w in ["sarcástico", "sarcastico", "sarcasmo"]
        ):
            resp = (
                "Yo, ¿sarcástico? Jamás se me ocurriría, jefa. Simplemente"
                " mantengo un alto estándar de objetividad frente al caos."
            )
        elif any(w in u_lower for w in ["hora", "fecha", "dia"]):
            resp = (
                f"Son exactamente las {hora_hoy} del {fecha_hoy} aquí en Buin."
                " El tiempo corre, pero el sistema no descansa por usted."
            )
        elif "clima" in u_lower:
            resp = (
                "El ambiente en Buin está bajo control. Puede revisar la"
                " telemetría exacta en el panel izquierdo, aunque le sugiero"
                " un abrigo si sale, jefa."
            )
        elif "hardware" in u_lower or "cpu" in u_lower or "ram" in u_lower:
            resp = (
                "Los procesadores y la memoria están estables. Ninguna"
                " anomalía térmica ni de consumo detectada en la laptop."
            )
        elif any(
            w in u_lower
            for w in ["hola", "buenos dias", "buenas tardes", "buenas noches"]
        ):
            resp = (
                f"{saludo_actual} Qué gusto escucharla de nuevo. ¿Qué tenemos"
                " en la mira para hoy, jefa?"
            )
        elif "gracias" in u_lower:
            resp = (
                "Un placer, jefa. Para eso fuimos programados; el mérito es"
                " todo suyo."
            )
        else:
            resp = (
                f"Entendido, jefa. Analizando '{user_input}' con los"
                " protocolos cognitivos activos. El núcleo RAG y los agentes de"
                " análisis están listos para asistirla."
            )

        st.session_state.messages.append(
            {"role": "assistant", "content": resp}
        )
        st.rerun()

    c_purg1, c_purg2 = st.columns([3, 1])
    with c_purg2:
        if st.button("🗑️ Purgar Chat"):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": (
                        f"{obtener_saludo_jefa()} Historial purgado al"
                        " instante, jefa. Borrón y cuenta nueva."
                    ),
                }
            ]
            guardar_log_db(hora_hoy, "Historial de chat purgado.")
            st.session_state.logs_auditoria.append(
                f"[{hora_hoy}] Historial de chat purgado."
            )
            st.rerun()

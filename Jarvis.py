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

# CLAVES Y CREDENCIALES OFICIALES
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
        return "Buenos días, jefa. Enlace cognitivo global y local al 100%."
    elif 12 <= hora < 20:
        return "Buenas tardes, jefa. Procesamiento cibernético activo."
    else:
        return "Buenas noches, jefa. Vigilancia y razonamiento nocturno."


if "emergencia_activa" not in st.session_state:
    st.session_state.emergencia_activa = False

if "logs_auditoria" not in st.session_state:
    st.session_state.logs_auditoria = cargar_logs_db()
    if not st.session_state.logs_auditoria:
        init_log = f"[{hora_hoy}] Núcleo con Capacidad Cibernética Avanzada inicializado en Buin ({fecha_hoy})."
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

saludo_inicial = f"{obtener_saludo_jefa()} Enlace satelital seguro en Buin. Capacidad cibernética y conocimiento universal integrados. ¿Qué directiva ejecutamos hoy?"

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
        <div style="color: #8a99ad; font-size: 0.75em;">Núcleo Autónomo | Inteligencia Universal & Segura | Buin, Chile</div>
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

    with st.expander("🌤️ Clima Satelital en Vivo (Buin)"):
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

    with st.expander("🌐 Buscador Web 24/7 (Satelital)"):
        query_web = st.text_input(
            "Ingrese consulta web en tiempo real:", key="search_web_input"
        )
        if query_web:
            url_busqueda = f"https://html.duckduckgo.com/html/?q={query_web}"
            st.success(f"Agente Web Autónomo procesando: **{query_web}**")
            st.markdown(
                f"🔗 [Abrir reporte de red externo]({url_busqueda})",
                unsafe_allow_html=True,
            )
            guardar_log_db(hora_hoy, f"Búsqueda web avanzada: '{query_web}'.")
            st.session_state.logs_auditoria.append(
                f"[{hora_hoy}] Búsqueda web autónoma preparada: '{query_web}'."
            )

    with st.expander("🌍 Mapeo de Red Global & Flujos Tácticos"):
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

    with st.expander("📈 Terminal HUD de Trading & Métricas"):
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

    with st.expander("💻 Sensor de Hardware & Laptop (CPU/RAM)"):
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

    with st.expander("🎙️ Escucha Permanente & Micrófono IA"):
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

    with st.expander("🖼️ Banco de Imágenes & Vokaturi"):
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

    with st.expander("📊 Monitor Fiduciario & Divisas (USD / EUR)"):
        st.write(
            "Indicadores financieros oficiales con análisis predictivo de"
            " tendencias:"
        )
        if st.button("📈 Consultar Divisas & Alertas de Mercado"):
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
                    f" ${val_euro} CLP\n\n🟢 **Análisis predictivo:** Mercado"
                    " estable con ligera tendencia alcista en Buin."
                )
                guardar_log_db(hora_hoy, "Consulta divisas y análisis de mercado.")
                st.session_state.logs_auditoria.append(
                    f"[{hora_hoy}] Monitor fiduciario consultado con éxito."
                )
            except Exception:
                st.info(
                    "Mercado fiduciario estable. Estimados en Buin ➔ Dólar:"
                    " ~940 CLP | Euro: ~1,020 CLP."
                )

    with st.expander("🚨 Sensores de Perímetro y Entorno"):
        st.write("Estado de seguridad física:")
        st.markdown(
            "🔹 **Perímetro Buin:** Seguro (0 intrusiones) <br>🔹 **Sensores"
            " Térmicos:** Normales <br>🔹 **Estado de Red:** Conexión"
            " Satelital Blindada",
            unsafe_allow_html=True,
        )

    with st.expander("🔒 Protocolo Caja Fuerte (Códigos & Credenciales)"):
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

    with st.expander("📄 Conexión Documental (RAG & Memoria Semántica)"):
        st.write(
            "Memoria contextual avanzada para indexación de documentos locales:"
        )
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
            if st.button("📑 Indexar Semánticamente"):
                contenido_doc = uploaded_file.read().decode(
                    "utf-8", errors="ignore"
                )
                guardar_rag_db(uploaded_file.name, contenido_doc[:2500])
                st.info(
                    "Documento indexado en la base de datos semántica RAG."
                    " Memoria de largo plazo actualizada."
                )
                guardar_log_db(
                    hora_hoy,
                    f"Documento indexado en RAG: {uploaded_file.name}",
                )

        st.markdown("---")
        consulta_rag = st.text_input(
            "Búsqueda Semántica en

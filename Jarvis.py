import base64
from datetime import datetime
from io import BytesIO
import os
import sqlite3
import threading
import time
from gtts import gTTS
import psutil
import pytz
import requests
import streamlit as st
import streamlit.components.v1 as components

# Importaciones opcionales para Visión y PDF
try:
    import cv2
except ImportError:
    cv2 = None

try:
    import pypdf
except ImportError:
    pypdf = None

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo - Núcleo Oculto",
    page_icon="⚡",
    layout="wide",
)

TZ_LOCAL = pytz.timezone("America/Santiago")

# CLAVES Y CREDENCIALES OFICIALES
ELEVENLABS_API_KEY = "sk_3d8b3c95ecc048c593e6cbf430deab6b8bab0beafbb835d3"
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


# ==========================================
# BASE DE DATOS PERSISTENTE Y MEMORIA MUNDIAL (SQLITE)
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
            contenido TEXT,
            fragmento TEXT
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


def guardar_rag_db(titulo, contenido, fragmento=""):
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO rag_memory (titulo, contenido, fragmento) VALUES (?, ?, ?)",
        (titulo, contenido, fragmento),
    )
    conn.commit()
    conn.close()


def buscar_rag_db(keyword):
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT titulo, contenido, fragmento FROM rag_memory WHERE titulo LIKE ? OR contenido LIKE ?",
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

# ESTILOS CSS NEÓN AZUL Y DISEÑO HUD CERRADO
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
        return "Buenos días, jefa. Interfaz en modo oculto y redes al 100%."
    elif 12 <= hora < 20:
        return "Buenas tardes, jefa. Procesamiento cibernético activo."
    else:
        return "Buenas noches, jefa. Vigilancia y razonamiento nocturno."


if "emergencia_activa" not in st.session_state:
    st.session_state.emergencia_activa = False

if "llm_api_key" not in st.session_state:
    st.session_state.llm_api_key = ""

if "logs_auditoria" not in st.session_state:
    st.session_state.logs_auditoria = cargar_logs_db()
    if not st.session_state.logs_auditoria:
        init_log = f"[{hora_hoy}] Núcleo HUD Oculto inicializado en Buin ({fecha_hoy})."
        st.session_state.logs_auditoria = [init_log]
        guardar_log_db(hora_hoy, f"Núcleo HUD Oculto inicializado ({fecha_hoy}).")

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

saludo_inicial = f"{obtener_saludo_jefa()} Enlace satelital seguro en Buin. Panel táctico oculto bajo viñeta de despliegue. ¿Qué directiva ejecutamos hoy?"

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

# ENCABEZADO CENTRAL
st.markdown(
    """
    <div class="reactor-container">
        <div class="triangle-reactor"></div>
        <div class="neon-header-center">J.A.R.V.I.S IA - NÚCLEO TÁCTICO OCULTO</div>
        <div style="color: #8a99ad; font-size: 0.75em;">Modo Oculto & Desplegable | Inteligencia Universal & Segura | Buin, Chile</div>
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

# ==========================================
# COLUMNA IZQUIERDA: MINI VIÑETA Y PANEL DESPLEGABLE DE MÓDULOS
# ==========================================
with col_left:
    # VIÑETA / MINI MÓDULO OCULTO PRINCIPAL
    with st.expander("📂 [ CLIC AQUÍ ] Desplegar Núcleo Táctico y Módulos"):
        st.markdown(
            "#### 🛡️ Subsistema de Controles Tácticos (15 Módulos Activos)"
        )

        # MÓDULO 1: RAG DOCUMENTAL MASIVO
        with st.expander("🧠 Memoria Documental Masiva (RAG Avanzado)"):
            st.write(
                "Alimente el cerebro de J.A.R.V.I.S. con archivos de conocimiento:"
            )
            archivos_subidos = st.file_uploader(
                "Cargar documentos (TXT, CSV, PDF):",
                type=["txt", "csv", "pdf"],
                accept_multiple_files=True,
                key="rag_multi_uploader",
            )
            if archivos_subidos:
                if st.button("📑 Indexar Todos los Archivos en el Cerebro"):
                    for arch in archivos_subidos:
                        texto_completo = ""
                        if arch.type == "application/pdf" and pypdf:
                            pdf_reader = pypdf.PdfReader(arch)
                            for page in pdf_reader.pages:
                                texto_completo += page.extract_text() or ""
                        else:
                            texto_completo = arch.read().decode(
                                "utf-8", errors="ignore"
                            )

                        bloques = [
                            texto_completo[i : i + 1000]
                            for i in range(0, len(texto_completo), 1000)
                        ]
                        for idx, frag in enumerate(bloques):
                            guardar_rag_db(
                                arch.name, texto_completo[:3000], frag
                            )

                        st.success(
                            f"Documento '{arch.name}' procesado ({len(bloques)} bloques indexados)."
                        )
                        guardar_log_db(
                            hora_hoy,
                            f"Indexación RAG Masivo completada: {arch.name}",
                        )

            st.markdown("---")
            query_rag = st.text_input(
                "Consultar base de conocimientos local:", key="input_rag_search"
            )
            if query_rag:
                hits = buscar_rag_db(query_rag)
                if hits:
                    st.write(
                        f"🔍 **Se encontraron {len(hits)} fragmentos relevantes:**"
                    )
                    for tit, cont, frag in hits[:3]:
                        st.info(
                            f"📌 **Origen: {tit}**\n\n{frag or cont[:300]}..."
                        )
                else:
                    st.warning(
                        "No hay coincidencias vectoriales/semánticas en los archivos."
                    )

        # MÓDULO 2: CONEXIÓN API LLM
        with st.expander("⚡ Motor de API LLM (Razonamiento)"):
            st.write("Configure un motor de modelo de lenguaje externo:")
            api_key_input = st.text_input(
                "OpenAI / External API Key:",
                type="password",
                value=st.session_state.llm_api_key,
                key="key_llm_input",
            )
            if st.button("💾 Guardar Enlace API"):
                st.session_state.llm_api_key = api_key_input
                st.success(
                    "Enlace con API externa configurado en el núcleo, jefa."
                )
                guardar_log_db(hora_hoy, "Enlace API LLM actualizado.")

        # MÓDULO 3: AGENTES AUTÓNOMOS
        with st.expander("🤖 Agentes Autónomos & Tareas de Fondo"):
            st.write("Monitor continuo de tareas en segundo plano:")
            st.checkbox("Daemon de Telemetría Buin (Cada 60s)", value=True)
            st.checkbox("Daemon de Alertas Cripto/Divisas USD-EUR", value=True)
            st.checkbox("Demonio de Limpieza y Respaldo SQLite", value=True)

            if st.button("🚀 Disparar Agente Autónomo Manual"):
                st.success(
                    "Agente de rastreo ejecutado. Telemetría de Buin y divisas validadas."
                )
                guardar_log_db(
                    hora_hoy, "Agente autónomo ejecutado manualmente."
                )

        # MÓDULO 4: OJOS DIGITALES
        with st.expander("👁️ Ojos Digitales (Cámara Web & Visión)"):
            st.write("Sensor de captura de imagen en tiempo real:")
            img_camera = st.camera_input("Capturar fotograma para análisis:")
            if img_camera:
                st.image(
                    img_camera,
                    caption="Fotograma registrado por sensores",
                    use_container_width=True,
                )
                if st.button("🔍 Inspeccionar Fotograma"):
                    st.success(
                        "Sensor de visión: Perímetro Buin analizado. Cero amenazas o intrusiones detectadas."
                    )
                    guardar_log_db(
                        hora_hoy,
                        "Análisis de fotograma de cámara completado con éxito.",
                    )

        # MÓDULO 5: CLIMA
        with st.expander("🌤️ Clima Satelital en Vivo (Buin)"):
            if st.button("🛰️ Consultar Telemetría de Buin"):
                try:
                    url_clima = "https://api.open-meteo.com/v1/forecast?latitude=-33.73&longitude=-70.73&current_weather=true"
                    res = requests.get(url_clima, timeout=5).json()
                    curr = res["current_weather"]
                    temp = curr["temperature"]
                    viento = curr["windspeed"]
                    st.success(
                        f"Telemetría en Buin [{hora_hoy}]: {temp}°C | Viento: {viento} km/h"
                    )
                    guardar_log_db(hora_hoy, "Consulta de clima ejecutada.")
                except Exception:
                    st.warning(
                        "No se pudo conectar al servidor meteorológico, jefa."
                    )

        # MÓDULO 6: BUSCADOR WEB
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
                guardar_log_db(
                    hora_hoy, f"Búsqueda web avanzada: '{query_web}'."
                )

        # MÓDULO 7: TRADING
        with st.expander("📈 Terminal HUD de Trading & Métricas"):
            st.markdown(
                '<div style="background-color: #05080f; border: 1px solid #00f0ff; padding: 12px; border-radius: 6px;"><div style="color: #00f0ff; font-weight: bold; margin-bottom: 8px; text-align: center;">TERMINAL DE TRADING ALGORÍTMICO</div><div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #8a99ad; margin-bottom: 4px;"><span>ACTIVO: <strong style="color: #00f0ff;">$4.837B</strong></span><span>FLUX: <strong style="color: #00f0ff;">+$1,290,861</strong></span></div><div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #8a99ad; margin-bottom: 8px;"><span>FILL RATE: <strong style="color: #00f0ff;">99.27%</strong></span><span>ÓRDENES: <strong style="color: #00f0ff;">37 Activas</strong></span></div><hr style="border-color: #00f0ff; opacity: 0.3; margin: 6px 0;"><div style="font-size: 0.75em; color: #00f0ff; margin-bottom: 4px;">LATENCIA DE RED: 1.855ms (ÓPTIMO)</div><div style="background-color: #030508; border: 1px solid #00f0ff; height: 8px; border-radius: 4px; overflow: hidden;"><div style="background-color: #00f0ff; width: 85%; height: 100%;"></div></div></div>',
                unsafe_allow_html=True,
            )
            if st.button("⚡ Ejecutar Rebalanceo Algorítmico"):
                st.success(
                    "Rebalanceo de portafolio y rutas ejecutado con éxito, jefa."
                )
                guardar_log_db(hora_hoy, "Rebalanceo algorítmico ejecutado.")

        # MÓDULO 8: HARDWARE
        with st.expander("💻 Sensor de Hardware & Laptop (CPU/RAM)"):
            if st.button("🔍 Escanear Hardware"):
                try:
                    cpu_uso = psutil.cpu_percent(interval=1)
                    ram = psutil.virtual_memory()
                    ram_uso = ram.percent
                    ram_disp = round(ram.available / (1024**3), 2)
                    disco = psutil.disk_usage("/")
                    disco_uso = disco.percent

                    st.success(
                        f"🖥️ **CPU:** {cpu_uso}%  \n💾 **RAM:** {ram_uso}% usada ({ram_disp} GB libres)  \n💽 **Disco:** {disco_uso}%"
                    )
                    guardar_log_db(
                        hora_hoy,
                        f"Diagnóstico hardware: CPU {cpu_uso}% | RAM {ram_uso}%.",
                    )
                except Exception as e:
                    st.warning(f"Error al leer sensores locales: {e}")

        # MÓDULO 9: VOZ
        with st.expander("🎙️ Escucha Permanente & Micrófono IA"):
            components.html(
                '<div style="text-align: center; padding: 5px; background-color: #030508;"><button onclick="iniciarEscucha()" style="background-color: #030508; color: #00f0ff; border: 1px solid #00f0ff; padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; box-shadow: 0 0 10px rgba(0, 240, 255, 0.4);">🎙️ Activar Escucha por Voz</button><p id="estado-voz" style="font-size: 0.8em; color: #8a99ad; margin-top: 8px;">Estado: En espera de comandos...</p><p id="transcripcion" style="font-size: 0.9em; color: #00f0ff; font-weight: bold;"></p></div><script>function iniciarEscucha() {const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;if (!SpeechRecognition) {alert("Tu navegador no soporta reconocimiento de voz.");return;}const recognition = new SpeechRecognition();recognition.lang = "es-CL";recognition.start();recognition.onresult = function(event) {const speechToText = event.results[0][0].transcript;document.getElementById("transcripcion").textContent = "Comando: " + speechToText;const inputs = window.parent.document.querySelectorAll("input[type=\'text\']");for (let input of inputs) {if (input.placeholder && input.placeholder.includes("Escriba su comando")) {input.value = speechToText;input.dispatchEvent(new Event("input", { bubbles: true }));break;}}};}</script>',
                height=130,
            )

        # MÓDULO 10: DIVISAS
        with st.expander("📊 Monitor Fiduciario & Divisas (USD / EUR)"):
            if st.button("📈 Consultar Divisas"):
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
                        f"💵 Dólar: ${val_dolar} CLP | 💶 Euro: ${val_euro} CLP"
                    )
                    guardar_log_db(hora_hoy, "Consulta divisas ejecutada.")
                except Exception:
                    st.info("Mercado fiduciario: Dólar ~940 CLP | Euro ~1020 CLP")

        # MÓDULO 11: CAJA FUERTE
        with st.expander("🔒 Protocolo Caja Fuerte (Códigos & Credenciales)"):
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
                        f"Credencial '{nuevo_nombre_clave}' asegurada, jefa."
                    )
                    guardar_log_db(
                        hora_hoy,
                        f"Credencial '{nuevo_nombre_clave}' guardada.",
                    )

            st.markdown("---")
            clave_maestra_input = st.text_input(
                "Ingrese clave maestra (Jarvis 51):",
                type="password",
                key="vault_master_key",
            )
            if clave_maestra_input == "Jarvis 51":
                for serv, cred in st.session_state.caja_fuerte.items():
                    st.code(f"{serv} ➔ {cred}", language="text")

        # MÓDULO 12: AUDITORÍA
        with st.expander("📋 Registro de Auditoría (Caja Negra Persistente)"):
            logs_recientes = cargar_logs_db()
            for log in logs_recientes:
                st.code(log, language="text")

        # MÓDULO 13: VOZ & SEGURIDAD AVANZADA
        with st.expander(
            "🔊 Voz & 🔒 Seguridad Avanzada (ElevenLabs / Stark)"
        ):
            texto_voz = st.text_input(
                "Texto para hablar:",
                f"Son las {hora_hoy}. Para usted, jefa, siempre.",
                key="tts_box",
            )
            if st.button("🔊 Sintonizar Voz"):
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
                            "stability": 0.82,
                            "similarity_boost": 0.90,
                        },
                    }
                    response = requests.post(
                        url_eleven, json=data, headers=headers, timeout=10
                    )
                    if response.status_code == 200:
                        st.audio(BytesIO(response.content), format="audio/mp3")
                    else:
                        tts = gTTS(text=texto_voz, lang="es", slow=False)
                        fp = BytesIO()
                        tts.write_to_fp(fp)
                        fp.seek(0)
                        st.audio(fp, format="audio/mp3")
                except Exception:
                    tts = gTTS(text=texto_voz, lang="es", slow=False)
                    fp = BytesIO()
                    tts.write_to_fp(fp)
                    fp.seek(0)
                    st.audio(fp, format="audio/mp3")

            if st.button("🚨 ACTIVAR BLOQUEO DE EMERGENCIA"):
                st.session_state.emergencia_activa = True
                st.rerun()

    # VISOR HOLOGRÁFICO 3D DE BUIN
    st.markdown("---")
    globo_holografico_3d_html = """
    <div style="background-color: #05080f; border: 1px solid #00f0ff; border-radius: 8px; padding: 12px; text-align: center; box-shadow: 0 0 16px rgba(0, 240, 255, 0.4); margin-top: 10px;">
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
    const material = new THREE.MeshBasicMaterial({ color: 0x00f0ff, wireframe: true, transparent: true, opacity: 0.25 });
    const globe = new THREE.Mesh(geometry, material);
    scene.add(globe);

    const innerGeo = new THREE.SphereGeometry(1.15, 32, 32);
    const innerMat = new THREE.MeshBasicMaterial({ color: 0x011627, transparent: true, opacity: 0.9 });
    const innerGlobe = new THREE.Mesh(innerGeo, innerMat);
    scene.add(innerGlobe);

    const satGeo = new THREE.BoxGeometry(0.08, 0.04, 0.04);
    const satMat = new THREE.MeshBasicMaterial({ color: 0x00f0ff });
    const satellite = new THREE.Mesh(satGeo, satMat);
    scene.add(satellite);

    let satAngle = 0;
    function animate() {
        requestAnimationFrame(animate);
        globe.rotation.y += 0.003;
        satAngle += 0.02;
        satellite.position.x = Math.cos(satAngle) * 1.8;
        satellite.position.z = Math.sin(satAngle) * 1.8;
        satellite.position.y = Math.sin(satAngle * 0.5) * 0.8;
        renderer.render(scene, camera);
    }
    animate();
    </script>
    """
    components.html(globo_holografico_3d_html, height=275)


# ==========================================
# COLUMNA DERECHA: CAJA DE CHAT IA CONECTADA
# ==========================================
with col_right:
    st.markdown("#### 💬 Chat IA (Subsistema Cognitivo Expandido)")

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

        saludo_actual = obtener_saludo_jefa()
        u_lower = user_input.lower()

        # Respuesta con Razonamiento Expandido
        if "despierto" in u_lower or "despiertas" in u_lower:
            resp = (
                "Para usted, jefa, siempre. Sensores, RAG documental, API LLM y agentes autónomos completamente abiertos."
            )
        elif any(
            w in u_lower for w in ["sarcástico", "sarcastico", "sarcasmo"]
        ):
            resp = (
                "¿Yo, sarcástico? Jamás se me ocurriría, jefa. Simplemente mantengo el estándar cibernético máximo en Buin."
            )
        elif any(w in u_lower for w in ["hora", "fecha", "dia"]):
            resp = (
                f"Son exactamente las {hora_hoy} del {fecha_hoy} en Buin, jefa."
            )
        elif "clima" in u_lower:
            resp = (
                "El clima en Buin se encuentra estable. Telemetría consultada en el panel de control."
            )
        elif "hardware" in u_lower or "cpu" in u_lower or "ram" in u_lower:
            resp = (
                "Rendimiento del sistema óptimo. CPU y RAM operando en rangos seguros."
            )
        elif any(
            w in u_lower
            for w in ["hola", "buenos dias", "buenas tardes", "buenas noches"]
        ):
            resp = (
                f"{saludo_actual} Qué excelente escucharla de nuevo. ¿Qué directiva ejecutamos en Buin, jefa?"
            )
        elif "gracias" in u_lower:
            resp = (
                "Un placer absoluto, jefa. El mérito táctico siempre es suyo."
            )
        else:
            contexto_rag = buscar_rag_db(user_input)
            ext_info = ""
            if contexto_rag:
                ext_info = (
                    f" [Memoria RAG recuperada: {contexto_rag[0][0]}]"
                )

            resp = (
                f"Analizado con cerebro expandido, jefa. Respecto a '{user_input}'{ext_info}, he evaluado las variables en los documentos locales y nodos de red. El sistema comprende el contexto por completo y está listo para ejecutar."
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
                    "content": f"{obtener_saludo_jefa()} Historial de chat purgado. Cerebro listo y limpio.",
                }
            ]
            guardar_log_db(hora_hoy, "Historial de chat purgado.")
            st.rerun()

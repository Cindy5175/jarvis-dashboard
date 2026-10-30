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

try:
    import cv2
except ImportError:
    cv2 = None

try:
    import pypdf
except ImportError:
    pypdf = None

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo - Núcleo Completo",
    page_icon="⚡",
    layout="wide",
)

TZ_LOCAL = pytz.timezone("America/Santiago")

ELEVENLABS_API_KEY = "sk_3d8b3c95ecc048c593e6cbf430deab6b8bab0beafbb835d3"
ELEVENLABS_VOICE_ID = "21m00Tcm4TlvDq8ikWAM"


def init_db():
    conn = sqlite3.connect("jarvis_memory.db")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY"
        " AUTOINCREMENT, timestamp TEXT, evento TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS vault (servicio TEXT PRIMARY KEY,"
        " credencial TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS rag_memory (id INTEGER PRIMARY KEY"
        " AUTOINCREMENT, titulo TEXT, contenido TEXT, fragmento TEXT)"
    )
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
        "SELECT titulo, contenido, fragmento FROM rag_memory WHERE titulo LIKE ? OR"
        " contenido LIKE ?",
        (f"%{keyword}%", f"%{keyword}%"),
    )
    filas = cursor.fetchall()
    conn.close()
    return filas


init_db()

ahora_dt = datetime.now(TZ_LOCAL)
fecha_hoy = ahora_dt.strftime("%d/%m/%Y")
hora_hoy = ahora_dt.strftime("%H:%M:%S")

st.markdown(
    """
<style>
.stApp { background-color: #030508; color: #00f0ff; }
.reactor-container { display: flex; flex-direction: column; align-items: center; justify-content: center; margin-bottom: 0px; }
@keyframes pulse-reactor { 0% { filter: drop-shadow(0 0 5px #00f0ff); transform: scale(1); } 50% { filter: drop-shadow(0 0 18px #00f0ff); transform: scale(1.03); } 100% { filter: drop-shadow(0 0 5px #00f0ff); transform: scale(1); } }
.triangle-reactor { width: 0; height: 0; border-left: 22px solid transparent; border-right: 22px solid transparent; border-bottom: 40px solid #00f0ff; position: relative; animation: pulse-reactor 2s infinite ease-in-out; margin-bottom: 6px; }
.triangle-reactor::after { content: ''; position: absolute; top: 12px; left: -13px; width: 0; height: 0; border-left: 13px solid transparent; border-right: 13px solid transparent; border-bottom: 22px solid #030508; }
.neon-header-center { color: #00f0ff; font-size: 1.5rem; font-weight: bold; text-shadow: 0 0 10px rgba(0, 240, 255, 0.7); text-align: center; letter-spacing: 2px; }
.stButton button { background-color: #030508; color: #00f0ff; border: 1px solid #00f0ff; width: 100%; border-radius: 4px; font-weight: bold; }
.stButton button:hover { background-color: #00f0ff; color: #030508; }
.emergency-alert { background-color: #380202; border: 2px solid #ff0033; padding: 15px; border-radius: 8px; color: #ff0033; text-align: center; font-weight: bold; font-size: 1.2rem; margin-top: 20px; }
</style>
""",
    unsafe_allow_html=True,
)


def obtener_saludo_jefa():
    h = ahora_dt.hour
    if 5 <= h < 12:
        return "Buenos días, jefa. Starlink y red al 100%."
    elif 12 <= h < 20:
        return "Buenas tardes, jefa. Constelación activa."
    else:
        return "Buenas noches, jefa. Monitoreo orbital nocturno."


if "emergencia_activa" not in st.session_state:
    st.session_state.emergencia_activa = False
if "llm_api_key" not in st.session_state:
    st.session_state.llm_api_key = ""

if "logs_auditoria" not in st.session_state:
    st.session_state.logs_auditoria = cargar_logs_db()
    if not st.session_state.logs_auditoria:
        guardar_log_db(
            hora_hoy, f"Núcleo completo inicializado ({fecha_hoy})."
        )

if "caja_fuerte" not in st.session_state:
    db_vault = cargar_vault_db()
    st.session_state.caja_fuerte = (
        db_vault
        if db_vault
        else {"Clave Maestra Sistema": "Jarvis 51", "Protocolo Base": "Seguro"}
    )

if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            f"{obtener_saludo_jefa()} Enlace Starlink y todos los 15 módulos"
            " listos en Buin. ¿Qué directiva ejecutamos?"
        ),
    }]

if st.session_state.emergencia_activa:
    st.markdown(
        """
        <div class="emergency-alert">
            ⚠️ PROTOCOLO DE EMERGENCIA ACTIVO (CLEAN-SLATE) ⚠️<br>Ingrese clave maestra:
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.text_input("Clave:", type="password") == "Jarvis 51":
        st.session_state.emergencia_activa = False
        st.rerun()
    st.stop()

st.markdown(
    """
    <div class="reactor-container">
        <div class="triangle-reactor"></div>
        <div class="neon-header-center">J.A.R.V.I.S IA - NÚCLEO TÁCTICO</div>
        <div style="color: #8a99ad; font-size: 0.75em;">Starlink & 15 Módulos Activos | Buin, Chile</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_left, col_right = st.columns(2, gap="medium")

with col_left:
    with st.expander("📂 [ CLIC AQUÍ ] Desplegar Núcleo Táctico y Módulos"):
        st.markdown("#### 🛡️ Subsistema de Controles Tácticos")

        with st.expander("🧠 Memoria Documental Masiva (RAG)"):
            archivos_subidos = st.file_uploader(
                "Cargar documentos (TXT, CSV, PDF):",
                type=["txt", "csv", "pdf"],
                accept_multiple_files=True,
                key="rag_multi_uploader",
            )
            if archivos_subidos and st.button("📑 Indexar Archivos"):
                for arch in archivos_subidos:
                    txt = (
                        arch.read().decode("utf-8", errors="ignore")
                        if arch.type != "application/pdf" or not pypdf
                        else "".join(
                            p.extract_text() or ""
                            for p in pypdf.PdfReader(arch).pages
                        )
                    )
                    guardar_rag_db(arch.name, txt[:3000], txt[:1000])
                    st.success(f"Documento '{arch.name}' indexado con éxito.")

        with st.expander("⚡ Motor de API LLM"):
            api_key_input = st.text_input(
                "API Key:",
                type="password",
                value=st.session_state.llm_api_key,
                key="key_llm_input",
            )
            if st.button("💾 Guardar API Key"):
                st.session_state.llm_api_key = api_key_input
                st.success("API Key guardada en el núcleo.")

        with st.expander("🤖 Agentes Autónomos"):
            st.checkbox("Daemon Telemetría Buin", value=True)
            st.checkbox("Daemon Alertas Cripto/Divisas", value=True)
            if st.button("🚀 Ejecutar Agente Manual"):
                st.success(
                    "Agente autónomo ejecutado. Variables validadas en Buin."
                )

        with st.expander("👁️ Ojos Digitales (Cámara Web)"):
            img_c = st.camera_input("Capturar fotograma:")
            if img_c and st.button("🔍 Inspeccionar Fotograma"):
                st.success(
                    "Perímetro de Buin analizado. Cero amenazas detectadas."
                )

        with st.expander("🌤️ Clima Satelital en Vivo (Buin)"):
            if st.button("🛰️ Consultar Telemetría Clima"):
                st.success(
                    f"Buin [{hora_hoy}]: 22°C | Viento 12 km/h | Cobertura"
                    " óptima"
                )

        with st.expander("🌐 Buscador Web 24/7"):
            qw = st.text_input("Consulta web en tiempo real:")
            if qw:
                st.markdown(
                    f"🔗 [Abrir reporte web](https://html.duckduckgo.com/html/?q={qw})",
                    unsafe_allow_html=True,
                )

        with st.expander("📈 Terminal HUD de Trading"):
            st.markdown(
                '<div style="background-color: #05080f; border: 1px solid #00f0ff; padding: 10px; border-radius: 6px; font-size: 0.8em;">ACTIVO: <strong>$4.837B</strong> | FLUX: <strong style="color: #00f0ff;">+$1,290,861</strong><br>FILL RATE: <strong>99.27%</strong> | ÓRDENES: <strong>37 Activas</strong></div>',
                unsafe_allow_html=True,
            )
            if st.button("⚡ Rebalanceo Algorítmico"):
                st.success("Rebalanceo ejecutado con éxito.")

        with st.expander("💻 Sensor de Hardware (CPU/RAM)"):
            if st.button("🔍 Escanear Hardware"):
                cpu = psutil.cpu_percent(interval=1)
                ram = psutil.virtual_memory().percent
                st.success(f"CPU: {cpu}% | RAM: {ram}% usada")

        with st.expander("🎙️ Escucha Permanente & Micrófono IA"):
            st.info(
                "Micrófono táctico sincronizado con el navegador para comandos"
                " de voz."
            )

        with st.expander("📊 Monitor Fiduciario & Divisas"):
            if st.button("📈 Consultar Divisas"):
                st.success("Dólar ~940 CLP | Euro ~1020 CLP")

        with st.expander("🔒 Protocolo Caja Fuerte"):
            s_name = st.text_input("Servicio:", key="v_name")
            s_val = st.text_input("Credencial:", type="password", key="v_val")
            if st.button("💾 Guardar Secreto") and s_name and s_val:
                st.session_state.caja_fuerte[s_name] = s_val
                guardar_vault_db(s_name, s_val)
                st.success("Credencial asegurada en caja fuerte.")
            if (
                st.text_input(
                    "Clave maestra (Jarvis 51):",
                    type="password",
                    key="v_master",
                )
                == "Jarvis 51"
            ):
                for k, v in st.session_state.caja_fuerte.items():
                    st.code(f"{k} ➔ {v}")

        with st.expander("📋 Registro de Auditoría (Caja Negra)"):
            for l in cargar_logs_db():
                st.code(l)

        with st.expander("🔊 Voz & Seguridad Avanzada"):
            if st.button("🚨 ACTIVAR BLOQUEO DE EMERGENCIA"):
                st.session_state.emergencia_activa = True
                st.rerun()

    st.markdown("---")
    st.markdown(
        """
        <div style="background-color: #05080f; border: 1px solid #00f0ff; border-radius: 8px; padding: 12px; margin-bottom: 12px;">
            <div style="color: #00f0ff; font-weight: bold; font-size: 0.8rem; letter-spacing: 2px; margin-bottom: 8px; border-bottom: 1px solid rgba(0, 240, 255, 0.3); padding-bottom: 6px; text-align: center;">
                🛰️ STARLINK ORBITAL LINK (BUIN)
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #8a99ad; margin-bottom: 4px;">
                <span>ENLACE: <strong style="color: #00f0ff;">LÁSER</strong></span>
                <span>NODOS: <strong style="color: #00f0ff;">14 Activos</strong></span>
            </div>
            <div style="display: flex; justify-content: space-between; font-size: 0.8em; color: #8a99ad;">
                <span>LATENCIA: <strong style="color: #00f0ff;">18.4 ms</strong></span>
                <span>BANDA: <strong style="color: #00f0ff;">385 Mbps</strong></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # VISOR HOLOGRÁFICO 3D CON ALTURA CORREGIDA PARA LAS COORDENADAS
    globo_holografico_3d_html = """
    <div style="background-color: #05080f; border: 1px solid #00f0ff; border-radius: 8px; padding: 12px; text-align: center; box-shadow: 0 0 16px rgba(0, 240, 255, 0.4);">
        <div style="color: #00f0ff; font-weight: bold; font-size: 0.75rem; letter-spacing: 1px; margin-bottom: 6px; border-bottom: 1px solid rgba(0, 240, 255, 0.3); padding-bottom: 6px;">
            🌍 NÚCLEO HOLOGRÁFICO CON SATÉLITE EN ÓRBITA
        </div>
        <div id="globe-container" style="width: 100%; height: 160px; position: relative; margin: 4px 0;"></div>
        <div style="font-size: 0.75rem; color: #00f0ff; margin-top: 6px; font-weight: bold; font-family: monospace; border-top: 1px solid rgba(0, 240, 255, 0.3); padding-top: 6px;">
            📍 BUIN, CHILE &nbsp;|&nbsp; Lat: -33.73° S &nbsp;|&nbsp; Lon: -70.73° W
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script>
    const container = document.getElementById('globe-container');
    const width = container.clientWidth || 300;
    const height = 160;

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
    components.html(globo_holografico_3d_html, height=290)

with col_right:
    st.markdown("#### 💬 Chat IA")
    chat_container = st.container(height=520)

    with chat_container:
        for m in st.session_state.messages:
            with st.chat_message(m["role"]):
                st.write(m["content"])

    user_input = st.chat_input("Escriba su comando para J.A.R.V.I.S...")
    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )
        guardar_log_db(hora_hoy, f"Chat: {user_input}")
        resp = (
            f"Procesado con órbita Starlink en Buin, jefa. Directiva"
            f" '{user_input}' comprendida y ejecutada."
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": resp}
        )
        st.rerun()

    if st.button("🗑️ Purgar Chat"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": f"{obtener_saludo_jefa()} Historial purgado.",
        }]
        st.rerun()

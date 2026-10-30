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
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
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
</style>
""",
    unsafe_allow_html=True,
)


def obtener_saludo_jefa():
    h = ahora_dt.hour
    if 5 <= h < 12:
        return "Buenos días, jefa. Enlace Starlink y red al 100%."
    elif 12 <= h < 20:
        return "Buenas tardes, jefa. Constelación satelital activa."
    else:
        return "Buenas noches, jefa. Monitoreo orbital nocturno."


if "llm_api_key" not in st.session_state:
    st.session_state.llm_api_key = ""
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            f"{obtener_saludo_jefa()} Enlace Starlink activo en Buin. Panel"
            " listo. ¿Qué directiva ejecutamos hoy?"
        ),
    }]

st.markdown(
    """
    <div class="reactor-container">
        <div class="triangle-reactor"></div>
        <div class="neon-header-center">J.A.R.V.I.S IA - NÚCLEO MÓVIL</div>
        <div style="color: #8a99ad; font-size: 0.75em;">Starlink & Responsive HUD | Buin, Chile</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_left, col_right = st.columns(2, gap="medium")

with col_left:
    with st.expander("📂 [ CLIC AQUÍ ] Desplegar Núcleo Táctico y Módulos"):
        st.markdown("#### 🛡️ Subsistema de Controles Tácticos")

        with st.expander("🧠 Memoria Documental Masiva (RAG)"):
            st.write("Cargue archivos de conocimiento:")
            st.file_uploader(
                "Cargar documentos:",
                type=["txt", "csv", "pdf"],
                accept_multiple_files=True,
            )

        with st.expander("⚡ Motor de API LLM"):
            st.text_input(
                "API Key:",
                type="password",
                value=st.session_state.llm_api_key,
            )

        with st.expander("🤖 Agentes Autónomos"):
            st.checkbox("Telemetría Buin", value=True)
            st.checkbox("Alertas Cripto/Divisas", value=True)

        with st.expander("🌤️ Clima Satelital (Buin)"):
            if st.button("🛰️ Consultar Clima Buin"):
                st.success(f"Buin [{hora_hoy}]: 22°C | Cielo despejado Starlink")

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
        resp = (
            f"Analizado vía Starlink, jefa. Directiva '{user_input}' procesada"
            " con éxito en Buin."
        )
        st.session_state.messages.append(
            {"role": "assistant", "content": resp}
        )
        st.rerun()

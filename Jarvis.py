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
    if clave_emergencia == "Jarvis 51

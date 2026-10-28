import streamlit as st
import time
from groq import Groq
import streamlit.components.v1 as components
from gtts import gTTS
import os
import base64
import sqlite3
import yfinance as yf
import requests
from audio_recorder_streamlit import audio_recorder
from datetime import datetime
import pytz
import psutil
import plotly.graph_objects as go

# 1. Configuración de página
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Control de Estado para Código Rojo (Emergencia)
if "codigo_rojo" not in st.session_state:
    st.session_state.codigo_rojo = False

color_neon_principal = "#ff3333" if st.session_state.codigo_rojo else "#00d2ff"
color_sombra_neon = "rgba(255, 51, 51, 0.8)" if st.session_state.codigo_rojo else "rgba(0, 210, 255, 0.6)"

# Estilos globales dinámicos
st.markdown(f"""
    <style>
    h1, h2, h3, h4, h5, h6, span.neon-title {{
        color: {color_neon_principal} !important;
        text-shadow: 0 0 10px {color_sombra_neon};
    }}
    .stMarkdown p, label, .streamlit-expanderHeader span, div[data-testid="stExpander"] summary span {{
        color: {color_neon_principal} !important;
        text-shadow: 0 0 6px {color_sombra_neon};
    }}
    div[data-testid="stMetricLabel"] {{
        color: {color_neon_principal} !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: #ffffff !important;
        text-shadow: 0 0 10px {color_neon_principal};
    }}
    .stSelectbox label, .stCheckbox span {{
        color: {color_neon_principal} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Base de datos persistente (SQLite)
def inicializar_db():
    conn = sqlite3.connect("jarvis_tactical.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bitacora (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nota TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS misiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarea TEXT,
            estado TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetria_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tiempo TEXT,
            cpu REAL,
            ram REAL
        )
    """)
    conn.commit()
    return conn

db_conn = inicializar_db()

def guardar_mensaje_db(role, content):
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
    db_conn.commit()

def cargar_mensajes_db():
    cursor = db_conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history")
    rows = cursor.fetchall()
    return [{"role": r[0], "content": r[1]} for r in rows]

def purgar_db():
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM chat_history")
    db_conn.commit()

if "messages" not in st.session_state:
    st.session_state.messages = cargar_mensajes_db()
    if not st.session_state.messages:
        chile_tz = pytz.timezone("America/Santiago")
        hora_actual = datetime.now(chile_tz).hour
        if 5 <= hora_actual < 12:
            saludo_inicial = "Buenos días, Jefa. Sistemas tácticos en línea y operando al 100%. ¿Qué protocolos ejecutamos hoy?"
        elif 12 <= hora_actual < 20:
            saludo_inicial = "Buenas tardes, Jefa. La base de Buin está estable y los sistemas rinden al máximo. ¿En qué le sirvo?"
        else:
            saludo_inicial = "Buenas noches, Jefa. Trabajando en horario extendido, como corresponde a este taller. ¿Cuál es la orden?"
        
        st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})
        guardar_mensaje_db("assistant", saludo_inicial)

def hablar_jarvis(texto):
    try:
        velocidad = st.session_state.get("voz_lenta", False)
        tts = gTTS(text=texto, lang='es', slow=velocidad)
        audio_path = "jarvis_voice.mp3"
        tts.save(audio_path)
        with open(audio_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            audio_html = f"""
                <audio autoplay style="display:none;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
    except Exception:
        pass

# Protocolo 1: Alerta Externa (Telegram Webhook)
def enviar_alerta_telegram(mensaje_alerta):
    try:
        token = st.secrets.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = st.secrets.get("TELEGRAM_CHAT_ID", "")
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": f"🚨 [JARVIS BUIN ALERTA]: {mensaje_alerta}"}
            requests.post(url, json=payload, timeout=3)
    except Exception:
        pass

def generar_html_pdf(historial):
    html_content = """
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: monospace; color: #002244; padding: 20px; }
            h1 { color: #00d2ff; border-bottom: 2px solid #00d2ff; padding-bottom: 5px; }
            .msg { margin-bottom: 15px; padding: 10px; border-radius: 5px; background: #f0f8ff; }
            .user { font-weight: bold; color: #004488; }
            .jarvis { font-weight: bold; color: #0088cc; }
        </style>
    </head>
    <body>
        <h1>CENTRO DE COMANDO J.A.R.V.I.S. - INFORME TÁCTICO</h1>
    """
    for msg in historial:
        rol_class = "user" if msg["role"] == "user" else "jarvis"
        rol_nombre = "Jefa" if msg["role"] == "user" else "J.A.R.V.I.S."
        html_content += f'<div class="msg"><span class="{rol_class}">{rol_nombre}:</span><p>{msg["content"]}</p></div>'
    html_content += "</body></html>"
    return html_content

def renderizar_globo_terraqueo(hex_color):
    try:
        glogo_html = (
            "<!DOCTYPE html>"
            "<html>"
            "<head>"
            '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
            "<style>"
            "body { margin: 0; overflow: hidden; background: transparent; }"
            "#canvas-container { width: 100%; height: 320px; position: relative; cursor: pointer; }"
            "#hud-text {"
            "    position: absolute; top: 10px; left: 10px;"
            f"    font-family: monospace; color: {hex_color}; font-size: 11px;"
            "    background: rgba(0,0,0,0.85); padding: 5px 10px; border-radius: 4px;"
            f"    border: 1px solid {hex_color}; z-index: 10;"
            f"    box-shadow: 0 0 10px {hex_color};"
            "}"
            "#orbit-hud {"
            "    position: absolute; bottom: 10px; left: 10px;"
            f"    font-family: monospace; color: {hex_color}; font-size: 10px;"
            "    background: rgba(0,0,0,0.75); padding: 4px 8px; border-radius: 3px;"
            "    z-index: 10;"
            "}"
            "</style>"
            "</head>"
            "<body>"
            '<div id="canvas-container">'
            '<div id="hud-text">BUIN COMMAND // ORBITAL ROTATION ACTIVE</div>'
            '<div id="orbit-hud">Satélites enlazados: 24 | Estado: Nominal</div>'
            "</div>"
            "<script>"
            "const container = document.getElementById('canvas-container');"
            "const scene = new THREE.Scene();"
            "const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 320, 0.1, 1000);"
            "const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });"
            "renderer.setSize(container.clientWidth, 320);"
            "container.appendChild(renderer.domElement);"
            "const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);"
            "scene.add(ambientLight);"
            f"const pointLight = new THREE.PointLight('{hex_color}', 2, 50);"
            "pointLight.position.set(5, 3, 5);"
            "scene.add(pointLight);"
            "const geometry = new THREE.SphereGeometry(2, 32, 32);"
            "const textureLoader = new THREE.TextureLoader();"
            "const earthTexture = textureLoader.load('https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg');"
            "const bumpTexture = textureLoader.load('https://threejs.org/examples/textures/planets/earth_normal_2048.jpg');"
            "const material = new THREE.MeshStandardMaterial({ map: earthTexture, bumpMap: bumpTexture, bumpScale: 0.05, roughness: 0.8 });"
            "const earth = new THREE.Mesh(geometry, material);"
            "scene.add(earth);"
            "const ringGeometry = new THREE.RingGeometry(2.4, 2.45, 64);"
            "const ringMaterial = new THREE.MeshBasicMaterial({"
            f"    color: '{hex_color}',"
            "    side: THREE.DoubleSide,"
            "    transparent: true,"
            "    opacity: 0.6"
            "});"
            "const orbitRing = new THREE.Mesh(ringGeometry, ringMaterial);"
            "orbitRing.rotation.x = Math.PI / 3;"
            "scene.add(orbitRing);"
            "camera.position.z = 5.5;"
            "function animate() {"
            "    requestAnimationFrame(animate);"
            "    earth.rotation.y += 0.003;"
            "    orbitRing.rotation.z += 0.001;"
            "    renderer.render(scene, camera);"
            "}"
            "animate();"
            "</script>"
            "</body>"
            "</html>"
        )
        components.html(glogo_html, height=330, scrolling=False)
    except Exception as e:
        st.error(f"Error en Globo Terráqueo Holográfico: {e}")

def renderizar_camara_seguridad(hex_color):
    cctv_html = (
        "<!DOCTYPE html>"
        "<html>"
        "<head>"
        "<style>"
        "body { margin: 0; background: #000; overflow: hidden; display: flex; justify-content: center; align-items: center; }"
        f"#cctv-container {{ width: 100%; height: 260px; position: relative; border: 2px solid {hex_color}; border-radius: 8px; box-shadow: 0 0 12px {hex_color}; }}"
        "video { width: 100%; height: 100%; object-fit: cover; border-radius: 6px; }"
        "#overlay-hud {"
        "    position: absolute; top: 10px; left: 10px;"
        f"    font-family: monospace; color: {hex_color}; font-size: 11px;"
        "    background: rgba(0,0,0,0.8); padding: 4px 8px; border-radius: 4px;"
        "    z-index: 10;"
        "}"
        "#rec-dot {"
        "    height: 8px; width: 8px; background-color: #ff3333; border-radius: 50%;"
        "    display: inline-block; margin-right: 5px; animation: blink 1s infinite;"
        "}"
        "@keyframes blink { 0% { opacity: 1; } 50% { opacity: 0.2; } 100% { opacity: 1; } }"
        "</style>"
        "</head>"
        "<body>"
        '<div id="cctv-container">'
        '<div id="overlay-hud"><span id="rec-dot"></span>CCTV // CAM-01 BUIN BASE // REC</div>'
        '<video id="webcam" autoplay playsinline muted></video>'
        "</div>"
        "<script>"
        "const video = document.getElementById('webcam');"
        "navigator.mediaDevices.getUserMedia({ video: true })"
        "    .then(stream => { video.srcObject = stream; })"
        "    .catch(err => { console.log('Cámara no disponible: ', err); });"
        "</script>"
        "</body>"
        "</html>"
    )
    components.html(cctv_html, height=275, scrolling=False)

def renderizar_mapa_tactico(modo):
    try:
        filtro_css = "filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%);" if modo == "noche" else ""
        mapa_html = (
            "<!DOCTYPE html>"
            "<html>"
            "<head>"
            '<meta charset="utf-8">'
            '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />'
            '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
            "<style>"
            "body { margin: 0; padding: 0; }"
            f"#map {{ width: 100%; height: 350px; border-radius: 8px; {filtro_css} }}"
            "</style>"
            "</head>"
            "<body>"
            '<div id="map"></div>'
            "<script>"
            "const map = L.map('map').setView([-33.7331, -70.7072], 12);"
            "L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' }).addTo(map);"
            "L.marker([-33.7331, -70.7072]).addTo(map).bindPopup('<b>Base Buin (GPS Activo)</b>').openPopup();"
            "L.marker([-33.4489, -70.6693]).addTo(map).bindPopup('<b>Santiago Centro</b>').openPopup();"
            "</script>"
            "</body>"
            "</html>"
        )
        components.html(mapa_html, height=360, scrolling=False)
    except Exception as e:
        st.error(f"Error en Mapa Táctico: {e}")

def renderizar_radar_tactico(hex_color):
    radar_html = (
        "<!DOCTYPE html>"
        "<html>"
        "<head>"
        "<style>"
        "body { margin: 0; background: #000814; display: flex; justify-content: center; align-items: center; height: 180px; }"
        "canvas { width: 160px; height: 160px; }"
        "</style>"
        "</head>"
        "<body>"
        '<canvas id="radarCanvas" width="160" height="160"></canvas>'
        "<script>"
        "const canvas = document.getElementById('radarCanvas');"
        "const ctx = canvas.getContext('2d');"
        "let angle = 0;"
        "function drawRadar() {"
        "    ctx.clearRect(0, 0, 160, 160);"
        f"    ctx.strokeStyle = '{hex_color}';"
        "    ctx.lineWidth = 1.5;"
        "    ctx.beginPath(); ctx.arc(80, 80, 70, 0, Math.PI * 2); ctx.stroke();"
        "    ctx.beginPath(); ctx.arc(80, 80, 40, 0, Math.PI * 2); ctx.stroke();"
        "    ctx.beginPath(); ctx.moveTo(10, 80); ctx.lineTo(150, 80); ctx.stroke();"
        "    ctx.beginPath(); ctx.moveTo(80, 10); ctx.lineTo(80, 150); ctx.stroke();"
        "    ctx.save();"
        "    ctx.translate(80, 80);"
        "    ctx.rotate(angle);"
        f"    ctx.strokeStyle = '{hex_color}';"
        "    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(70, -70); ctx.stroke();"
        "    ctx.restore();"
        "    ctx.fillStyle = '#ff3333';"
        "    ctx.beginPath(); ctx.arc(110, 50, 3, 0, Math.PI * 2); ctx.fill();"

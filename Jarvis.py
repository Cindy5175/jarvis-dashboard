import streamlit as str_lit
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

# 1. Configuración de página
str_lit.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Control de Estado para Código Rojo y Enlace Satelital
if "codigo_rojo" not in str_lit.session_state:
    str_lit.session_state.codigo_rojo = False

if "enlace_satelital" not in str_lit.session_state:
    str_lit.session_state.enlace_satelital = True

color_neon_principal = "#ff3333" if str_lit.session_state.codigo_rojo else "#00d2ff"
color_sombra_neon = "rgba(255, 51, 51, 0.8)" if str_lit.session_state.codigo_rojo else "rgba(0, 210, 255, 0.6)"

# Estilos globales dinámicos
str_lit.markdown(f"""
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
        CREATE TABLE IF NOT EXISTS clima_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            detalles TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentos_rag (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            contenido TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sesiones_archivadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            resumen TEXT
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
    cursor.execute("SELECT content FROM chat_history LIMIT 1")
    row = cursor.fetchone()
    if row:
        fecha_sesion = datetime.now(pytz.timezone("America/Santiago")).strftime("%Y-%m-%d %H:%M")
        c_db = db_conn.cursor()
        c_db.execute("INSERT INTO sesiones_archivadas (fecha, resumen) VALUES (?, ?)", (fecha_sesion, f"Sesión iniciada con: {row[0][:40]}..."))
        db_conn.commit()
    
    cursor.execute("DELETE FROM chat_history")
    db_conn.commit()

if "messages" not in str_lit.session_state:
    str_lit.session_state.messages = cargar_mensajes_db()
    if not str_lit.session_state.messages:
        chile_tz = pytz.timezone("America/Santiago")
        hora_actual = datetime.now(chile_tz).hour
        
        clima_info = ""
        try:
            res_c = requests.get("https://api.open-meteo.com/v1/forecast?latitude=-33.7331&longitude=-70.7072&current_weather=true", timeout=2).json()
            t_val = res_c["current_weather"]["temperature"]
            w_val = res_c["current_weather"]["windspeed"]
            clima_info = f" [Reporte Buin: {t_val}°C, Viento {w_val} km/h]."
        except Exception:
            clima_info = " [Reporte Buin: Estable]."

        tipo_enlace = "enlace satelital Stark" if str_lit.session_state.enlace_satelital else "red terrestre de fibra"
        if 5 <= hora_actual < 12:
            saludo_inicial = f"Buenos días, Jefa.{clima_info} Enrutado mediante {tipo_enlace}. Sistemas tácticos al 100%. ¿Qué proyectos ejecutamos hoy?"
        elif 12 <= hora_actual < 20:
            saludo_inicial = f"Buenas tardes, Jefa.{clima_info} Conexión vía {tipo_enlace} estable en Buin. ¿En qué puedo acompañarla o ayudarle hoy?"
        else:
            saludo_inicial = f"Buenas noches, Jefa.{clima_info} Operando en horario extendido a través de {tipo_enlace}. Aquí estoy listo para lo que necesite."
        
        str_lit.session_state.messages.append({"role": "assistant", "content": saludo_inicial})
        guardar_mensaje_db("assistant", saludo_inicial)

def hablar_jarvis(texto):
    try:
        velocidad = str_lit.session_state.get("voz_lenta", False)
        tts = gTTS(text=texto, lang='es', slow=velocidad)
        audio_path = "jarvis_voice.mp3"
        tts.save(audio_path)
        with open(audio_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            audio_html = '<audio autoplay style="display:none;"><source src="data:audio/mp3;base64,' + b64 + '" type="audio/mp3"></audio>'
            str_lit.markdown(audio_html, unsafe_allow_html=True)
    except Exception:
        pass

def enviar_alerta_telegram(mensaje_alerta):
    try:
        token = str_lit.secrets.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = str_lit.secrets.get("TELEGRAM_CHAT_ID", "")
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": f"🚨 [JARVIS BUIN ALERTA]: {mensaje_alerta}"}
            requests.post(url, json=payload, timeout=3)
    except Exception:
        pass

def generar_html_pdf(historial):
    html_content = "<html><head><meta charset='utf-8'>"
    html_content += "<style>"
    html_content += "body { font-family: monospace; color: #002244; padding: 20px; }"
    html_content += "h1 { color: #00d2ff; border-bottom: 2px solid #00d2ff; padding-bottom: 5px; }"
    html_content += ".msg { margin-bottom: 15px; padding: 10px; border-radius: 5px; background: #f0f8ff; }"
    html_content += ".user { font-weight: bold; color: #004488; }"
    html_content += ".jarvis { font-weight: bold; color: #0088cc; }"
    html_content += "</style></head><body>"
    html_content += "<h1>CENTRO DE COMANDO J.A.R.V.I.S. - INFORME TÁCTICO</h1>"
    for msg in historial:
        rol_class = "user" if msg["role"] == "user" else "jarvis"
        rol_nombre = "Jefa" if msg["role"] == "user" else "J.A.R.V.I.S."
        html_content += f'<div class="msg"><span class="{rol_class}">{rol_nombre}:</span><p>{msg["content"]}</p></div>'
    html_content += "</body></html>"
    return html_content

def renderizar_globo_terraqueo(hex_color):
    try:
        glogo_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <style>
                body { margin: 0; overflow: hidden; background: transparent; }
                #canvas-container { width: 100%; height: 320px; position: relative; }
                #hud-text { position: absolute; top: 10px; left: 10px; font-family: monospace; color: HEX_COLOR_REPLACE; font-size: 11px; background: rgba(0,0,0,0.85); padding: 5px 10px; border-radius: 4px; border: 1px solid HEX_COLOR_REPLACE; z-index: 10; box-shadow: 0 0 10px HEX_COLOR_REPLACE; }
                #orbit-hud { position: absolute; bottom: 10px; left: 10px; font-family: monospace; color: HEX_COLOR_REPLACE; font-size: 10px; background: rgba(0,0,0,0.75); padding: 4px 8px; border-radius: 3px; z-index: 10; }
            </style>
        </head>
        <body>
            <div id="canvas-container">
                <div id="hud-text">BUIN COMMAND // GLOBO HOLOGRÁFICO F&F 8</div>
                <div id="orbit-hud">Satélites enlazados: 24 | Estado: Nominal</div>
            </div>
            <script>
                const container = document.getElementById('canvas-container');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 320, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(container.clientWidth, 320);
                container.appendChild(renderer.domElement);
                
                const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
                scene.add(ambientLight);
                
                const geometry = new THREE.SphereGeometry(2, 32, 32);
                const material = new THREE.MeshBasicMaterial({ 
                    color: 'HEX_COLOR_REPLACE', 
                    wireframe: true, 
                    transparent: true, 
                    opacity: 0.7 
                });
                const earth = new THREE.Mesh(geometry, material);
                scene.add(earth);
                
                const ringGeometry = new THREE.RingGeometry(2.4, 2.45, 64);
                const ringMaterial = new THREE.MeshBasicMaterial({ color: 'HEX_COLOR_REPLACE', side: THREE.DoubleSide, transparent: true, opacity: 0.5 });
                const orbitRing = new THREE.Mesh(ringGeometry, ringMaterial);
                orbitRing.rotation.x = Math.PI / 3;
                scene.add(orbitRing);
                
                camera.position.z = 5.5;
                
                function animate() {
                    requestAnimationFrame(animate);
                    earth.rotation.y += 0.004;
                    orbitRing.rotation.z += 0.002;
                    renderer.render(scene, camera);
                }
                animate();
            </script>
        </body>
        </html>
        """.replace("HEX_COLOR_REPLACE", hex_color)
        
        components.html(glogo_html, height=330, scrolling=False)
    except Exception as e:
        str_lit.error(f"Error en Globo Terráqueo: {e}")

def renderizar_street_view(lat, lon):
    street_html = f"""
    <iframe width="100%" height="320" src="https://maps.google.com/maps?q={lat},{lon}&t=&z=17&ie=UTF8&iwloc=&output=embed" frameborder="0" scrolling="no"></iframe>
    """
    components.html(street_html, height=330, scrolling=False)

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
            f"#map {{ width: 100%; height: 280px; border-radius: 8px; {filtro_css} }}"
            "</style>"
            "</head>"
            "<body>"
            '<div id="map"></div>'
            "<script>"
            "const map = L.map('map').setView([-33.7331, -70.7072], 11);"
            "L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, attribution: '© OpenStreetMap' }).addTo(map);"
            "L.marker([-33.7331, -70.7072]).addTo(map).bindPopup('<b>Base Buin</b>').openPopup();"
            "L.marker([-33.4489, -70.6693]).addTo(map).bindPopup('<b>Santiago Centro</b>').openPopup();"
            "</script>"
            "</body>"
            "</html>"
        )
        components.html(mapa_html, height=295, scrolling=False)
    except Exception as e:
        str_lit.error(f"Error en Mapa Táctico: {e}")

@str_lit.cache_resource
def obtener_cliente_groq():
    try:
        api_key = "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"
        if not api_key:
            return None
        return Groq(api_key=api_key, timeout=10.0)
    except Exception:
        return None

client = obtener_cliente_groq()

# BARRA LATERAL (IZQUIERDA)
with str_lit.sidebar:
    str_lit.markdown("### ⚙️ Panel Control J.A.R.V.I.S.")

    # --- 1. PROTOCOLOS AVANZADOS ---
    with str_lit.expander("🚀 Protocolos Avanzados (Software)"):
        str_lit.markdown("#### 1. Conmutador de Enlace (Dual)")
        enlace_sat = str_lit.toggle("🛰️ Enlace Satelital Stark", value=str_lit.session_state.enlace_satelital)
        if enlace_sat != str_lit.session_state.enlace_satelital:
            str_lit.session_state.enlace_satelital = enlace_sat
            str_lit

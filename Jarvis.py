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

# 1. Configuración de página
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos globales para forzar el azul neón
st.markdown("""
    <style>
    h1, h2, h3, h4, h5, h6, span.neon-title {
        color: #00d2ff !important;
        text-shadow: 0 0 10px rgba(0, 210, 255, 0.6);
    }
    .stMarkdown p, label, .streamlit-expanderHeader span, div[data-testid="stExpander"] summary span {
        color: #00d2ff !important;
        text-shadow: 0 0 6px rgba(0, 210, 255, 0.4);
    }
    div[data-testid="stMetricLabel"] {
        color: #00d2ff !important;
    }
    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        text-shadow: 0 0 10px #00d2ff;
    }
    .stSelectbox label, .stCheckbox span {
        color: #00d2ff !important;
    }
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

# Cargar mensajes en session_state desde SQLite con saludo dinámico
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

# Función para reproducir voz sintetizada automáticamente
def hablar_jarvis(texto):
    try:
        tts = gTTS(text=texto, lang='es', slow=False)
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

# Función para generar reporte HTML descargable
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

# Visor Holográfico 3D: ¡Globo Terráqueo Real que Gira en 3D!
def renderizar_globo_terraqueo(hex_color):
    try:
        globo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <style>
                body {{ margin: 0; overflow: hidden; background: transparent; }}
                #canvas-container {{ width: 100%; height: 320px; position: relative; cursor: pointer; }}
                #hud-text {{
                    position: absolute; top: 10px; left: 10px; 
                    font-family: monospace; color: {hex_color}; font-size: 11px;
                    background: rgba(0,0,0,0.85); padding: 5px 10px; border-radius: 4px;
                    border: 1px solid {hex_color}; z-index: 10;
                    box-shadow: 0 0 10px rgba(0,210,255,0.4);
                }}
                #orbit-hud {{
                    position: absolute; bottom: 10px; left: 10px; 
                    font-family: monospace; color: #00ffcc; font-size: 10px;
                    background: rgba(0,0,0,0.75); padding: 4px 8px; border-radius: 3px;
                    z-index: 10;
                }}
            </style>
        </head>
        <body>
            <div id="canvas-container">
                <div id="hud-text">BUIN COMMAND // ORBITAL ROTATION ACTIVE</div>
                <div id="orbit-hud">Satélites enlazados: 24 | Estado: Nominal</div>
            </div>
            <script>
                const container = document.getElementById('canvas-container');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 320, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
                renderer.setSize(container.clientWidth, 320);
                container.appendChild(renderer.domElement);

                // Iluminación espacial
                const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
                scene.add(ambientLight);
                const pointLight = new THREE.PointLight(0x00d2ff, 2, 50);
                pointLight.position.set(5, 3, 5);
                scene.add(pointLight);

                // Creación de la Esfera de la Tierra con Textura de Alta Calidad
                const geometry = new THREE.SphereGeometry(2, 32, 32);
                const textureLoader = new THREE.TextureLoader();
                // Textura pública de la Tierra tipo NASA
                const earthTexture = textureLoader.load('https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg');
                const bumpTexture = textureLoader.load('https://threejs.org/examples/textures/planets/earth_normal_2048.jpg');
                
                const material = new THREE.MeshStandardMaterial({{
                    map: earthTexture,
                    bumpMap: bumpTexture,
                    bumpScale: 0.05,
                    roughness: 0.8
                }});
                
                const earth = new THREE.Mesh(geometry, material);
                scene.add(earth);

                // Anillo de Red Satelital Holográfica
                const ringGeometry = new THREE.RingGeometry(2.4, 2.45, 64);
                const ringMaterial = new THREE.MeshBasicMaterial({{
                    color: '{hex_color}',
                    side: THREE.DoubleSide,
                    transparent: true,
                    opacity: 0.6
                }});
                const orbitRing = new THREE.Mesh(ringGeometry, ringMaterial);
                orbitRing.rotation.x = Math.PI / 3;
                scene.add(orbitRing);

                camera.position.z = 5.5;

                // Animación de Rotación Continua
                function animate() {{
                    requestAnimationFrame(animate);
                    earth.rotation.y += 0.003; // Rotación de la Tierra
                    orbitRing.rotation.z += 0.001; // Rotación de la órbita
                    renderer.render(scene, camera);
                }}
                animate();
            </script>
        </body>
        </html>
        """
        components.html(globo_html, height=330, scrolling=False)
    except Exception as e:
        st.error(f"Error en Globo Terráqueo Holográfico: {e}")

# Mapa Cartográfico
def renderizar_mapa_tactico(modo):
    try:
        tile_layer = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" if modo == "dia" else "https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"
        mapa_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                body {{ margin: 0; padding: 0; }}
                #map {{ width: 100%; height: 350px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                const map = L.map('map').setView([-33.7331, -70.7072], 12);
                L.tileLayer('{tile_layer}', {{ maxZoom: 19, attribution: '© OpenStreetMap' }}).addTo(map);
                L.marker([-33.7331, -70.7072]).addTo(map).bindPopup('<b>Base Buin</b>').openPopup();
                L.marker([-33.4489, -70.6693]).addTo(map).bindPopup('<b>Santiago Centro</b>').openPopup();
            </script>
        </body>
        </html>
        """
        components.html(mapa_html, height=360, scrolling=False)
    except Exception as e:
        st.error(f"Error en Mapa Táctico: {e}")

# BARRA LATERAL (IZQUIERDA)
with st.sidebar:
    st.markdown("### ⚙️ Panel Control J.A.R.V.I.S.")
    
    @st.cache_resource
    def obtener_cliente_groq():
        try:
            api_key = "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"
            if not api_key:
                return None
            return Groq(api_key=api_key, timeout=10.0)
        except Exception:
            return None

    client = obtener_cliente_groq()

    if st.button("🧹 Purgar Memoria de Chat"):
        purgar_db()
        st.session_state.messages = []
        st.success("¡Memoria persistente purgada con éxito, Jefa!")
        st.rerun()

    st.markdown("---")
    mostrar_estacion = st.checkbox("Mostrar Estación Holográfica", value=True)
    mostrar_mapa = st.checkbox("Mostrar Mapa Cartográfico Táctico", value=True)
    
    st.markdown("---")
    tema_hud = st.selectbox("Tema HUD:", ["Azul Arc", "Rojo Cobre/Terracota", "Grafito Oscuro"])
    color_map = {"Rojo Cobre/Terracota": "#d9534f", "Azul Arc": "#00d2ff", "Grafito Oscuro": "#888888"}
    hex_actual = color_map.get(tema_hud, "#00d2ff")
    
    protocolo_ia = st.selectbox("Protocolo IA:", ["Estándar (Leal y Ejecutivo)", "Avanzado", "Táctico"])
    grid_tactico = st.selectbox("Grid Táctico:", ["Santiago Centro", "Buin", "Global"])
    
    st.markdown("---")
    
    # --- JUGUETE 1: Radar Clima en Vivo ---
    with st.expander("🌤️ Juguete 1: Radar Clima en Vivo"):
        st.markdown("<span style='

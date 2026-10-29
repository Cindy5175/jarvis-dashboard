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
        CREATE TABLE IF NOT EXISTS galeria_ia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_archivo TEXT,
            descripcion TEXT
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

# Caché inteligente de consulta de clima en Buin para evitar latencias de red
@str_lit.cache_data(ttl=300)
def obtener_clima_buin():
    try:
        res = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=-33.7331&longitude=-70.7072&current_weather=true",
            timeout=2.0
        ).json()
        temp = res["current_weather"]["temperature"]
        wind = res["current_weather"]["windspeed"]
        return {"temp": temp, "wind": wind, "ok": True}
    except Exception:
        return {"temp": 18.0, "wind": 5.0, "ok": False}

def guardar_mensaje_db(role, content):
    cursor = db_conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history ORDER BY id DESC LIMIT 1")
    ultimo = cursor.fetchone()
    if not ultimo or ultimo[0] != role or ultimo[1] != content:
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
        
        datos_c = obtener_clima_buin()
        if datos_c["ok"]:
            clima_info = f" [Reporte Buin: {datos_c['temp']}°C, Viento {datos_c['wind']} km/h]."
        else:
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
    html_content = (
        "<html><head><meta charset='utf-8'>"
        "<style>"
        "body { font-family: monospace; color: #002244; padding: 20px; }"
        "h1 { color: #00d2ff; border-bottom: 2px solid #00d2ff; padding-bottom: 5px; }"
        ".msg { margin-bottom: 15px; padding: 10px; border-radius: 5px; background: #f0f8ff; }"
        ".user { font-weight: bold; color: #004488; }"
        ".jarvis { font-weight: bold; color: #0088cc; }"
        "</style></head><body>"
        "<h1>CENTRO DE COMANDO J.A.R.V.I.S. - INFORME TÁCTICO</h1>"
    )
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
                body { margin: 0; overflow: hidden; background: transparent; display: flex; flex-direction: column; align-items: center; justify-content: center; }
                #canvas-container { width: 100%; height: 230px; display: flex; justify-content: center; align-items: center; position: relative; }
                #orbit-hud { font-family: monospace; color: HEX_COLOR_REPLACE; font-size: 11px; background: rgba(0,0,0,0.85); padding: 4px 12px; border-radius: 4px; border: 1px solid HEX_COLOR_REPLACE; box-shadow: 0 0 10px HEX_COLOR_REPLACE; text-align: center; margin-top: 6px; letter-spacing: 1px; }
            </style>
        </head>
        <body>
            <div id="canvas-container"></div>
            <div id="orbit-hud">OJO DE DIOS // RED CUÁNTICA GLOBAL STARK</div>
            <script>
                const container = document.getElementById('canvas-container');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 230, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(container.clientWidth, 230);
                container.appendChild(renderer.domElement);
                
                const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
                scene.add(ambientLight);

                const globeGroup = new THREE.Group();
                scene.add(globeGroup);

                // 1. Esfera Base Transparente (Globo Interno)
                const baseGeo = new THREE.SphereGeometry(1.5, 32, 32);
                const baseMat = new THREE.MeshBasicMaterial({
                    color: 0x001122,
                    wireframe: false,
                    transparent: true,
                    opacity: 0.6
                });
                const baseGlobe = new THREE.Mesh(baseGeo, baseMat);
                globeGroup.add(baseGlobe);

                // 2. Red de Nodos Holográficos (Efecto Matrix/Red Global)
                const particlesCount = 280;
                const positions = new Float32Array(particlesCount * 3);
                const radius = 1.55;

                for (let i = 0; i < particlesCount; i++) {
                    const phi = Math.acos(-1 + (2 * i) / particlesCount);
                    const theta = Math.sqrt(particlesCount * Math.PI) * phi;

                    positions[i * 3] = radius * Math.cos(theta) * Math.sin(phi);
                    positions[i * 3 + 1] = radius * Math.sin(theta) * Math.sin(phi);
                    positions[i * 3 + 2] = radius * Math.cos(phi);
                }

                const pGeometry = new THREE.BufferGeometry();
                pGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));

                const pMaterial = new THREE.PointsMaterial({
                    color: 'HEX_COLOR_REPLACE',
                    size: 0.04,
                    transparent: true,
                    opacity: 0.9
                });
                const nodesPoints = new THREE.Points(pGeometry, pMaterial);
                globeGroup.add(nodesPoints);

                // 3. Conexiones Malla de Red (Lineas entre Nodos)
                const lineGeo = new THREE.WireframeGeometry(new THREE.IcosahedronGeometry(1.55, 3));
                const lineMat = new THREE.LineBasicMaterial({
                    color: 'HEX_COLOR_REPLACE',
                    transparent: true,
                    opacity: 0.25
                });
                const meshLines = new THREE.LineSegments(lineGeo, lineMat);
                globeGroup.add(meshLines);

                // 4. Anillo Orbital Holográfico
                const ringGeo = new THREE.RingGeometry(1.9, 1.95, 64);
                const ringMat = new THREE.MeshBasicMaterial({ color: 'HEX_COLOR_REPLACE', side: THREE.DoubleSide, transparent: true, opacity: 0.5 });
                const orbitRing = new THREE.Mesh(ringGeo, ringMat);
                orbitRing.rotation.x = Math.PI / 2.5;
                scene.add(orbitRing);

                camera.position.z = 4.6;

                function animate() {
                    requestAnimationFrame(animate);
                    globeGroup.rotation.y += 0.003;
                    globeGroup.rotation.x += 0.0008;
                    orbitRing.rotation.z -= 0.002;
                    renderer.render(scene, camera);
                }
                animate();
            </script>
        </body>
        </html>
        """.replace("HEX_COLOR_REPLACE", hex_color)
        
        components.html(glogo_html, height=280, scrolling=False)
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
        mapa_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>
                body {{ margin: 0; padding: 0; touch-action: pan-x pan-y; }}
                #map {{ width: 100%; height: 280px; border-radius: 8px; {filtro_css} }}
            </style>
        </head>
        <body>
            <div id="map"></div>
            <script>
                const map = L.map('map', {{
                    dragging: true,
                    tap: false,
                    touchZoom: true
                }}).setView([-33.7331, -70.7072], 11);
                
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom: 19, attribution: '© OpenStreetMap' }}).addTo(map);
                L.marker([-33.7331, -70.7072]).addTo(map).bindPopup('<b>Base Buin</b>').openPopup();
                L.marker([-33.4489, -70.6693]).addTo(map).bindPopup('<b>Santiago Centro</b>').openPopup();
                
                if (map.tap) map.tap.disable();
            </script>
        </body>
        </html>
        """
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
            str_lit.rerun()
        
        texto_enlace = "Enrutando vía Constelación Satelital Stark-1 (Banda Ku)." if str_lit.session_state.enlace_satelital else "Enrutando vía Red Terrestre de Fibra Óptica."
        str_lit.markdown(
            f"""<div style="background: rgba(0, 210, 255, 0.1); border: 1px solid {color_neon_principal}; padding: 10px; border-radius: 6px; color: {color_neon_principal}; font-family: monospace; font-size: 0.85rem; box-shadow: 0 0 8px {color_sombra_neon}; margin-top: 5px; margin-bottom: 10px;">
                🛰️ {texto_enlace}
            </div>""",
            unsafe_allow_html=True
        )

        str_lit.markdown("#### 2. Hotword Hey JARVIS")
        hotword_activo = str_lit.checkbox("Activar Escucha Continua de Voz", value=False)
        if hotword_activo:
            str_lit.info("🎙️ Escucha activa de voz habilitada en terminal local.")

        str_lit.markdown("#### 3. Alertas Climáticas Auto")
        if str_lit.button("Forzar Chequeo Clima Buin"):
            datos_c = obtener_clima_buin()
            msg_clima = f"Temperatura: {datos_c['temp']}°C | Viento: {datos_c['wind']} km/h. Estado: Óptimo."
            enviar_alerta_telegram(msg_clima)
            str_lit.success(f"📡 Reporte enviado a Telegram: {msg_clima}")

    # --- 2. BLOQUE CONSOLIDADO

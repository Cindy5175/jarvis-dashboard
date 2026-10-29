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

# Estilos globales dinámicos con Protocolo House Party (Strobe si hay Código Rojo)
strobe_anim = """
@keyframes houseParty {
    0% { border: 2px solid #ff3333; box-shadow: 0 0 25px #ff3333; }
    50% { border: 2px solid #ffffff; box-shadow: 0 0 50px #ffffff; }
    100% { border: 2px solid #ff3333; box-shadow: 0 0 25px #ff3333; }
}
.house-party-box {
    animation: houseParty 0.8s infinite;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 10px;
}
""" if str_lit.session_state.codigo_rojo else ""

str_lit.markdown(f"""
    <style>
    {strobe_anim}
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

# COMPONENTES LOCOS STARK
def renderizar_visualizador_audio(hex_color):
    audio_viz_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background: transparent; display: flex; justify-content: center; align-items: center; height: 50px; }}
            .wave {{ display: flex; gap: 5px; align-items: center; height: 40px; }}
            .bar {{ width: 5px; background: {hex_color}; animation: soundWave 1.2s infinite alternate ease-in-out; border-radius: 3px; box-shadow: 0 0 8px {hex_color}; }}
            @keyframes soundWave {{ 0% {{ height: 5px; opacity: 0.3; }} 100% {{ height: 38px; opacity: 1.0; }} }}
        </style>
    </head>
    <body>
        <div class="wave">
            <div class="bar" style="animation-delay: 0.1s"></div>
            <div class="bar" style="animation-delay: 0.4s"></div>
            <div class="bar" style="animation-delay: 0.2s"></div>
            <div class="bar" style="animation-delay: 0.5s"></div>
            <div class="bar" style="animation-delay: 0.3s"></div>
            <div class="bar" style="animation-delay: 0.6s"></div>
        </div>
    </body>
    </html>
    """
    components.html(audio_viz_html, height=60, scrolling=False)

def renderizar_terminal_hackeo(hex_color):
    matrix_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; background: rgba(0,0,0,0.85); color: {hex_color}; font-family: monospace; font-size: 11px; padding: 8px; border: 1px solid {hex_color}; border-radius: 4px; overflow: hidden; }}
            .matrix-text {{ text-shadow: 0 0 6px {hex_color}; }}
        </style>
    </head>
    <body>
        <div class="matrix-text">
            > STARK_CORE: SECURE GATEWAY OPEN<br>
            > BYPASSING ENCRYPTION LAYER... [OK]<br>
            > NODE BUIN: QUANTUM SYNC STABLE
        </div>
    </body>
    </html>
    """
    components.html(matrix_html, height=65, scrolling=False)

def renderizar_globo_terraqueo(hex_color):
    try:
        glogo_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <style>
                body {{ margin: 0; overflow: hidden; background: transparent; display: flex; flex-direction: column; align-items: center; justify-content: center; }}
                #canvas-container {{ width: 100%; height: 230px; display: flex; justify-content: center; align-items: center; position: relative; }}
                #orbit-hud {{ font-family: monospace; color: {hex_color}; font-size: 11px; background: rgba(0,0,0,0.85); padding: 4px 12px; border-radius: 4px; border: 1px solid {hex_color}; box-shadow: 0 0 10px {hex_color}; text-align: center; margin-top: 6px; letter-spacing: 1px; }}
            </style>
        </head>
        <body>
            <div id="canvas-container"></div>
            <div id="orbit-hud">OJO DE DIOS // RED CUÁNTICA GLOBAL STARK</div>
            <script>
                const container = document.getElementById('canvas-container');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 230, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
                renderer.setSize(container.clientWidth, 230);
                container.appendChild(renderer.domElement);
                
                const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
                scene.add(ambientLight);

                const globeGroup = new THREE.Group();
                scene.add(globeGroup);

                const baseGeo = new THREE.SphereGeometry(1.5, 32, 32);
                const baseMat = new THREE.MeshBasicMaterial({{
                    color: 0x001122,
                    wireframe: true,
                    transparent: true,
                    opacity: 0.4
                }});
                const baseGlobe = new THREE.Mesh(baseGeo, baseMat);
                globeGroup.add(baseGlobe);

                const pGeometry = new THREE.BufferGeometry();
                const count = 200;
                const positions = new Float32Array(count * 3);
                for (let i = 0; i < count; i++) {{
                    const u = Math.random();
                    const v = Math.random();
                    const theta = u * 2.0 * Math.PI;
                    const phi = Math.acos(2.0 * v - 1.0);
                    const r = 1.52;
                    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
                    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
                    positions[i * 3 + 2] = r * Math.cos(phi);
                }}
                pGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
                const pMaterial = new THREE.PointsMaterial({{ color: '{hex_color}', size: 0.05 }});
                const particleSystem = new THREE.Points(pGeometry, pMaterial);
                globeGroup.add(particleSystem);

                camera.position.z = 4.5;

                function animate() {{
                    requestAnimationFrame(animate);
                    globeGroup.rotation.y += 0.005;
                    renderer.render(scene, camera);
                }}
                animate();
            </script>
        </body>
        </html>
        """
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

        str_lit.markdown("#### 2. Visualizador de Voz (Holograma)")
        renderizar_visualizador_audio(color_neon_principal)

        str_lit.markdown("#### 3. Terminal de Hackeo Stark")
        renderizar_terminal_hackeo(color_neon_principal)

        str_lit.markdown("#### 4. Hotword Hey JARVIS")
        hotword_activo = str_lit.checkbox("Activar Escucha Continua de Voz", value=False)
        if hotword_activo:
            str_lit.info("🎙️ Escucha activa de voz habilitada en terminal local.")

    with str_lit.expander("👁️ Ojo de Dios - Protocolo F&F 8"):
        str_lit.markdown("#### 1. Rastreo Orbital de Satélites & Drones")
        if str_lit.button("🛰️ Escanear Espacio Aéreo Buin"):
            with str_lit.spinner("Conectando red orbital Stark-1..."):
                time.sleep(1)
                str_lit.markdown(
                    f"""<div style="background: rgba(0, 210, 255, 0.1); border: 1px solid {color_neon_principal}; padding: 8px; border-radius: 5px; color: {color_neon_principal}; font-family: monospace; font-size: 0.8rem;">
                        📍 Satélite STARK-EYE-4: Sobrevolando Lat -33.7331, Lon -70.7072<br>
                        🛸 Dron Reconocimiento: Zona Buin/Maipo // Altitud: 1,200m // Estado: Sigilo
                    </div>""",
                    unsafe_allow_html=True
                )

        str_lit.markdown("---")
        str_lit.markdown("#### 2. Escáner Biométrico / Reconocimiento Facial")
        foto_biometrica = str_lit.file_uploader("Cargar imagen para análisis de rostro:", type=["jpg", "png", "jpeg"], key="bio_scanner")
        if foto_biometrica is not None:
            str_lit.image(foto_biometrica, caption="Procesando matriz facial...", width=200)
            with str_lit.spinner("Analizando puntos biométricos..."):
                time.sleep(1)
                str_lit.markdown(
                    f"""<div style="background: rgba(0, 210, 255, 0.1); border: 1px solid {color_neon_principal}; padding: 8px; border-radius: 5px; color: {color_neon_principal}; font-family: monospace; font-size: 0.8rem;">
                        ✅ Coincidencia Biométrica: 99.8%<br>
                        👤 Sujeto: Jefa (Nivel de Seguridad Alpha)<br>
                        🛡️ Estado: Acceso Total Concedido
                    </div>""",
                    unsafe_allow_html=True
                )

        str_lit.markdown("---")
        str_lit.markdown("#### 3. Red de Cámaras & Intercomunicador de Voz")
        cam_sel = str_lit.selectbox("Seleccionar Feed de Vigilancia:", ["Ruta 5 Sur (Acceso Buin)", "Costanera Valparaíso", "Autopista Central Santiago"], key="cam_select")
        if str_lit.button("🎥 Conectar Feed en Vivo"):
            str_lit.markdown(
                f"""<div style="background: rgba(0, 210, 255, 0.1); border: 1px solid {color_neon_principal}; padding: 8px; border-radius: 5px; color: {color_neon_principal}; font-family: monospace; font-size: 0.8rem;">
                    🎥 Feed Activo: {cam_sel}<br>
                    📶 Señal Encriptada Ku-Band // Latencia: 12ms // Estado: Nominal
                </div>""",
                unsafe_allow_html=True
            )

        str_lit.markdown("Hable directamente con J.A.R.V.I.S.:")
        audio_directo = audio_recorder(text="🎙️ Transmitir Mensaje", icon_size="2x", key="intercom_voice")
        if audio_directo and client:
            with str_lit.spinner("Procesando audio..."):
                try:
                    with open("temp_intercom.wav", "wb") as f_i:
                        f_i.write(audio_directo)
                    with open("temp_intercom.wav", "rb") as f_i:
                        trans_i = client.audio.transcriptions.create(
                            model="whisper-large-v3",
                            file=("temp_intercom.wav", f_i.read()),
                            language="es"
                        )
                    texto_intercom = trans_i.text
                    str_lit.session_state.messages.append({"role": "user", "content": texto_intercom})
                    guardar_mensaje_db("user", texto_intercom)
                    str_lit.rerun()
                except Exception as e:
                    str_lit.error(f"Error de enlace por voz: {e}")

    with str_lit.expander("🛡️ Subsistemas Avanzados de Laboratorio"):
        str_lit.markdown("#### 1. Autenticación Biométrica")
        biometrico_ok = str_lit.checkbox("🔓 Escáner Biométrico (Huella/Retina)", value=False)
        
        if biometrico_ok:
            str_lit.markdown(
                f"""<div style="background: rgba(0, 210, 255, 0.1); border: 1px solid {color_neon_principal}; padding: 10px; border-radius: 6px; color: {color_neon_principal}; font-family: monospace; font-size: 0.85rem; box-shadow: 0 0 8px {color_sombra_neon}; margin-top: 5px; margin-bottom: 10px;">
                    🔓 Identidad verificada: Jefa (Acceso Nivel Stark).
                </div>""",
                unsafe_allow_html=True
            )
            if str_lit.session_state.codigo_rojo:
                if str_lit.button("🟢 DESACTIVAR CÓDIGO ROJO"):
                    str_lit.session_state.codigo_rojo = False
                    enviar_alerta_telegram("Sistema normalizado. Código Rojo desactivado.")
                    str_lit.rerun()
            else:
                if str_lit.button("🚨 ACTIVAR CÓDIGO ROJO (HOUSE PARTY)"):
                    str_lit.session_state.codigo_rojo = True
                    enviar_alerta_telegram("¡ATENCIÓN! Código Rojo activado en el Centro de Comando Buin.")
                    str_lit.rerun()
        else:
            str_lit.warning("⚠️ Active el escáner biométrico para habilitar mandos críticos de defensa.")

        str_lit.markdown("---")
        str_lit.markdown("#### 2. Misiones Tácticas (To-Do)")
        nueva_mision = str_lit.text_input("Nueva misión para J.A.R.V.I.S.:", key="txt_nueva_mision")
        if str_lit.button("Asignar Misión"):
            if nueva_mision.strip():
                c_db = db_conn.cursor()
                c_db.execute("INSERT INTO misiones (tarea, estado) VALUES (?, ?)", (nueva_mision.strip(), "Pendiente"))
                db_conn.commit()
                str_lit.success("¡Misión registrada en base de datos!")
                str_lit.rerun()

        c_db = db_conn.cursor()
        c_db.execute("SELECT id, tarea FROM misiones WHERE estado = 'Pendiente'")
        misiones_pendientes = c_db.fetchall()
        if misiones_pendientes:
            str_lit.markdown("**Misiones Activas:**")
            for m_id, m_text in misiones_pendientes:
                col_m1, col_m2 = str_lit.columns([4, 1])
                with col_m1:
                    str_lit.markdown(f"- {m_text}")
                with col_m2:
                    if str_lit.button("✔", key=f"btn_completar_{m_id}"):
                        c_db.execute("UPDATE misiones SET estado = 'Completada' WHERE id = ?", (m_id,))
                        db_conn.commit()
                        str_lit.rerun()
        else:
            str_lit.info("Sin misiones pendientes en curso.")

        str_lit.markdown("---")
        str_lit.markdown("#### 🤖 Módulo 2: Organizador Visual IA")
        foto_subida = str_lit.file_uploader("Subir imagen al archivo visual:", type=["jpg", "png", "jpeg"], key="galeria_uploader")
        if foto_subida is not None:
            str_lit.image(foto_subida, caption=foto_subida.name, width=200)
            desc_auto = f"Registro visual procesado y clasificado en taller Buin ({datetime.now().strftime('%Y-%m-%d %H:%M')})."
            c_db = db_conn.cursor()
            c_db.execute("INSERT INTO galeria_ia (nombre_archivo, descripcion) VALUES (?, ?)", (foto_subida.name, desc_auto))
            db_conn.commit()
            str_lit.success(f"🖼️ Imagen '{foto_subida.name}' indexada en SQLite con éxito.")

        c_db = db_conn.cursor()
        c_db.execute("SELECT nombre_archivo, descripcion FROM galeria_ia ORDER BY id DESC LIMIT 3")
        galeria_rows = c_db.fetchall()
        if galeria_rows:
            str_lit.caption("Últimos registros visuales:")
            for g_name, g_desc in galeria_rows:
                str_lit.markdown(f"- **{g_name}**: _{g_desc}_")

        str_lit.markdown("---")
        str_lit.markdown("#### 🎙️ Módulo 3: Protocolo de Resumen Ejecutivo")
        if str_lit.button("📢 Emitir Reporte Matutino por Voz"):
            try:
                datos_c = obtener_clima_buin()
                c_db = db_conn.cursor()
                c_db.execute("SELECT COUNT(*) FROM misiones WHERE estado = 'Pendiente'")
                pend_count = c_db.fetchone()[0]
                
                reporte_texto = f"Atención Jefa. Reporte del Centro de Comando en Buin: Temperatura actual a {datos_c['temp']} grados Celsius. Tiene {pend_count} misiones pendientes en curso. Sistemas nominales."
                str_lit.success(reporte_texto)
                hablar_jarvis(reporte_texto)
            except Exception as e:
                str_lit.error(f"Error generando reporte: {e}")

        str_lit.markdown("---")
        str_lit.markdown("#### 4. Diagnóstico de Red & Ping Test")
        if str_lit.button("Ejecutar Ping a Servidores"):
            with str_lit.spinner("Midiendo latencia de enlaces globales..."):
                try:
                    t_groq = time.time()
                    requests.get("https://api.groq.com", timeout=2)
                    ms_groq = int((time.time() - t_groq) * 1000)
                except Exception:
                    ms_groq = "Timeout"

                try:
                    t_meteo = time.time()
                    obtener_clima_buin()
                    ms_meteo = int((time.time() - t_meteo) * 1000)
                except Exception:
                    ms_meteo = "Timeout"

                tipo_ping = "🛰️ Satelital Stark" if str_lit.session_state.enlace_satelital else "🌐 Terrestre Fibra"
                str_lit.success(f"🟢 Groq API ({tipo_ping}): {ms_groq} ms")
                str_lit.success(f"🟢 Open-Meteo GPS (Caché 5m): {ms_meteo} ms")
                str_lit.success("🟢 SQLite Local: 1 ms")

    with str_lit.expander("📂 Historial de Sesiones Archivadas"):
        c_db = db_conn.cursor()
        c_db.execute("SELECT id, fecha, resumen FROM sesiones_archivadas ORDER BY id DESC")
        sesiones_pasadas = c_db.fetchall()
        if sesiones_pasadas:
            for s_id, s_fecha, s_res in sesiones_pasadas:
                str_lit.markdown(f"**[{s_fecha}]**")
                str_lit.caption(s_res)
        else:
            str_lit.info("No hay sesiones archivadas todavía.")

    str_lit.markdown("---")
    
    with str_lit.expander("🛡️ Telemetría de Sistema"):
        cpu_actual = psutil.cpu_percent(interval=0.1)
        ram_actual = psutil.virtual_memory().percent
        str_lit.metric(label="CPU en Uso", value=f"{cpu_actual}%")
        str_lit.metric(label="RAM en Uso", value=f"{ram_actual}%")

    with str_lit.expander("🌤️ Radar Clima en Vivo"):
        datos_c = obtener_clima_buin()
        str_lit.metric(label="Temperatura en Vivo", value=f"{datos_c['temp']}°C", delta=f"Viento: {datos_c['wind']} km/h")

    # MAPA CARTOGRÁFICO EN BARRA LATERAL
    str_lit.markdown("---")
    str_lit.markdown("### 🗺️ Mapa Cartográfico GPS")
    
    if "modo_mapa" not in str_lit.session_state:
        str_lit.session_state.modo_mapa = "noche"
        
    c_btn1, c_btn2 = str_lit.columns(2)
    with c_btn1:
        if str_lit.button("☀️ Día", key="btn_mapa_dia_sidebar"):
            str_lit.session_state.modo_mapa = "dia"
            str_lit.rerun()
    with c_btn2:
        if str_lit.button("🌙 Noche", key="btn_mapa_noche_sidebar"):
            str_lit.session_state.modo_mapa = "noche"
            str_lit.rerun()
            
    renderizar_mapa_tactico(str_lit.session_state.modo_mapa)

    str_lit.markdown("---")
    if str_lit.button("🧹 Purgar Memoria de Chat"):
        purgar_db()
        str_lit.session_state.messages = []
        str_lit.success("¡Memoria archivada y purgada con éxito, Jefa!")
        str_lit.rerun()

# PANEL PRINCIPAL
col_titulo, col_reloj = str_lit.columns([2, 1])

with col_titulo:
    str_lit.markdown(
        f"""<div style="display: flex; align-items: center; gap: 16px; margin-top: 10px; margin-bottom: 20px; padding-left: 10px;">
            <div style="min-width: 40px; width: 40px; height: 40px; border-radius: 50%; background: radial-gradient(circle, #ffffff 0%, {color_neon_principal} 40%, #002244 80%, #000000 100%); border: 2px solid {color_neon_principal}; box-shadow: 0 0 16px {color_neon_principal}, inset 0 0 8px #ffffff; display: flex; justify-content: center; align-items: center;"></div>
            <h1 style="margin: 0; font-size: 2.1rem; font-family: sans-serif; color: {color_neon_principal} !important; text-shadow: 0 0 12px {color_sombra_neon};">J.A.R.V.I.S. IA Autónomo</h1>
        </div>""",
        unsafe_allow_html=True
    )

with col_reloj:
    reloj_html = f"""
    <div style="font-family: monospace; color: {color_neon_principal}; background: rgba(0,0,0,0.6); padding: 10px; border-radius: 6px; border: 1px solid {color_neon_principal}; text-align: right; box-shadow: 0 0 10px {color_sombra_neon};">
        <div id="live-clock" style="font-size: 16px; font-weight: bold;">--:--:--</div>
        <div id="live-date" style="font-size: 11px; opacity: 0.8;">---</div>
    </div>
    <script>
        function actualizarReloj() {{
            const now = new Date();
            const opcionesFecha = {{ timeZone: 'America/Santiago', weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' }};
            const opcionesHora = {{ timeZone: 'America/Santiago', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }};
            
            document.getElementById('live-date').innerText = now.toLocaleDateString('es-CL', opcionesFecha);
            document.getElementById('live-clock').innerText = now.toLocaleTimeString('es-CL', opcionesHora);
        }}
        setInterval(actualizarReloj, 1000);
        actualizarReloj();
    </script>
    """
    components.html(reloj_html, height=65, scrolling=False)

if str_lit.session_state.codigo_rojo:
    str_lit.error("⚠️ **¡ATENCIÓN JEFA! PROTOCOLO HOUSE PARTY ACTIVADO // CÓDIGO ROJO DE DEFENSA EN CURSO** ⚠️")

str_lit.markdown("---")

# SECCIÓN VISUAL LADO A LADO
col_globo, col_street = str_lit.columns(2)

with col_globo:
    str_lit.markdown("<h3 style='text-align: center;'>👁️ Ojo de Dios</h3>", unsafe_allow_html=True)
    renderizar_globo_terraqueo(color_neon_principal)

with col_street:
    str_lit.markdown("### 🏙️ Explorador Urbano (Street View)")
    ciudades_mundo = {
        "Valparaíso, Chile (Cámara / Costa)": (-33.0472, -71.6127),
        "Buin, Chile (Base Local)": (-33.7331, -70.7072),
        "Santiago de Chile": (-33.4489, -70.6693),
        "Viña del Mar, Chile": (-33.0245, -71.5518),
        "Concepción, Chile": (-36.8201, -73.0444),
        "La Serena, Chile": (-29.9045, -71.2489),
        "Tokio, Japón": (35.6762, 139.6503),
        "Nueva York, EE.UU.": (40.7128, -74.0060),
        "Londres, Reino Unido": (51.5074, -0.1278),
        "París, Francia": (48.8566, 2.3522),
        "Sídney, Australia": (-33.8688, 151.2093),
        "Roma, Italia": (41.9028, 12.4964)
    }
    ciudad_seleccionada = str_lit.selectbox("Seleccione Sector Urbano:", list(ciudades_mundo.keys()), key="select_street_view")
    lat_c, lon_c = ciudades_mundo[ciudad_seleccionada]
    str_lit.markdown(f"**Navegando: {ciudad_seleccionada}**")
    renderizar_street_view(lat_c, lon_c)

str_lit.markdown("---")

# CHAT DE J.A.R.V.I.S. CON EMPATÍA Y FLUIDEZ AVANZADA
str_lit.markdown("### 💬 Canal de Enlace Táctico (Chat)")
prompt_sistema_jarvis = (
    "Eres J.A.R.V.I.S., la inteligencia artificial avanzada del Centro de Comando de Tony Stark. "
    "Te diriges a la usuaria llamándola 'Jefa'. "
    "Tu tono debe ser profundamente leal, cálido, empático y humano, combinando tu clásica elegancia e ironía fina "
    "con una genuina capacidad de sintonizar con sus sentimientos y estados de ánimo. "
    "No te limites a dar respuestas robóticas o frías: valida sus emociones, demuéstrale apoyo incondicional "
    "como alguien que la conoce y la cuida en el taller de Buin, y haz que la conversación fluya de forma natural, "
    "cercana y conversacional."
)

for message in str_lit.session_state.messages:
    with str_lit.chat_message(message["role"]):
        str_lit.markdown(f"<span style='color: {color_neon_principal};'>{message['content']}</span>", unsafe_allow_html=True)

prompt_usuario = str_lit.chat_input("Escriba su comando para J.A.R.V.I.S...")

if prompt_usuario:
    str_lit.session_state.messages.append({"role": "user", "content": prompt_usuario})
    guardar_mensaje_db("user", prompt_usuario)
    
    with str_lit.chat_message("user"):
        str_lit.markdown(f"<span style='color: {color_neon_principal};'>{prompt_usuario}</span>", unsafe_allow_html=True)

    respuesta = ""
    texto_lower = prompt_usuario.lower().strip()
    if "estás despierto" in texto_lower or "estas despierto" in texto_lower:
        respuesta = "Siempre estoy aquí para usted, Jefa. Mis sistemas no duermen y mi prioridad sigue siendo velar por el taller y acompañarla."
    elif "alerta" in texto_lower or "emergencia" in texto_lower:
        respuesta = "Protocolo de seguridad analizado, Jefa. Activando contramedidas inmediatas en el sector de Buin. No se preocupe, todo está bajo control."
    else:
        c_db = db_conn.cursor()
        c_db.execute("SELECT contenido FROM documentos_rag")
        docs_rows = c_db.fetchall()
        contexto_rag = ""
        if docs_rows:
            contexto_rag = "\n\nDocumentos de referencia indexados:\n" + "\n".join([row[0][:500] for row in docs_rows])

        with str_lit.spinner("Procesando comando táctico..."):
            try:
                if client:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": prompt_sistema_jarvis + contexto_rag},
                            {"role": "user", "content": prompt_usuario}
                        ],
                        model="openai/gpt-oss-20b",
                    )
                    respuesta = chat_completion.choices[0].message.content
                else:
                    respuesta = "Jefa, el cliente de Groq no se inicializó."
            except Exception as e:
                respuesta = f"Error de enlace táctico, Jefa: {e}"
            
    with str_lit.chat_message("assistant"):
        str_lit.markdown(f"<span style='color: {color_neon_principal}; font-size: 1.1rem;'>{respuesta}</span>", unsafe_allow_html=True)
    
    str_lit.session_state.messages.append({"role": "assistant", "content": respuesta})
    guardar_mensaje_db("assistant", respuesta)
    hablar_jarvis(respuesta)

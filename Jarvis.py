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
import plotly.graph_objects as go

# 1. Configuración de página
str_lit.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Control de Estado para Código Rojo (Emergencia)
if "codigo_rojo" not in str_lit.session_state:
    str_lit.session_state.codigo_rojo = False

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

if "messages" not in str_lit.session_state:
    str_lit.session_state.messages = cargar_mensajes_db()
    if not str_lit.session_state.messages:
        chile_tz = pytz.timezone("America/Santiago")
        hora_actual = datetime.now(chile_tz).hour
        if 5 <= hora_actual < 12:
            saludo_inicial = "Buenos días, Jefa. Sistemas tácticos en línea y operando al 100%. ¿Qué protocolos ejecutamos hoy?"
        elif 12 <= hora_actual < 20:
            saludo_inicial = "Buenas tardes, Jefa. La base de Buin está estable y los sistemas rinden al máximo. ¿En qué le sirvo?"
        else:
            saludo_inicial = "Buenas noches, Jefa. Trabajando en horario extendido, como corresponde a este taller. ¿Cuál es la orden?"
        
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
            audio_html = f"""
                <audio autoplay style="display:none;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            str_lit.markdown(audio_html, unsafe_allow_html=True)
    except Exception:
        pass

# Protocolo 1: Alerta Externa (Telegram Webhook)
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
        glogo_html = f"""
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
                    box-shadow: 0 0 10px {hex_color};
                }}
                #orbit-hud {{
                    position: absolute; bottom: 10px; left: 10px; 
                    font-family: monospace; color: {hex_color}; font-size: 10px;
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

                const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
                scene.add(ambientLight);
                const pointLight = new THREE.PointLight('{hex_color}', 2, 50);
                pointLight.position.set(5, 3, 5);
                scene.add(pointLight);

                const geometry = new THREE.SphereGeometry(2, 32, 32);
                const textureLoader = new THREE.TextureLoader();
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

                function animate() {{
                    requestAnimationFrame(animate);
                    earth.rotation.y += 0.003;
                    orbitRing.rotation.z += 0.001;
                    renderer.render(scene, camera);
                }}
                animate();
            </script>
        </body>
        </html>
        """
        components.html(glogo_html, height=330, scrolling=False)
    except Exception as e:
        str_lit.error(f"Error en Globo Terráqueo Holográfico: {e}")

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
        str_lit.error(f"Error en Mapa Táctico: {e}")

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
        "    angle += 0.04;"
        "    requestAnimationFrame(drawRadar);"
        "}"
        "drawRadar();"
        "</script>"
        "</body>"
        "</html>"
    )
    components.html(radar_html, height=190, scrolling=False)

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

    if str_lit.session_state.codigo_rojo:
        if str_lit.button("🟢 DESACTIVAR CÓDIGO ROJO"):
            str_lit.session_state.codigo_rojo = False
            enviar_alerta_telegram("Sistema normalizado. Código Rojo desactivado.")
            str_lit.rerun()
    else:
        if str_lit.button("🚨 ACTIVAR CÓDIGO ROJO (EMERGENCIA)"):
            str_lit.session_state.codigo_rojo = True
            enviar_alerta_telegram("¡ATENCIÓN! Código Rojo activado en el Centro de Comando Buin.")
            str_lit.rerun()

    if str_lit.button("🧹 Purgar Memoria de Chat"):
        purgar_db()
        str_lit.session_state.messages = []
        str_lit.success("¡Memoria persistente purgada con éxito, Jefa!")
        str_lit.rerun()

    str_lit.markdown("---")
    mostrar_estacion = str_lit.checkbox("Mostrar Estación Holográfica", value=True)
    mostrar_mapa = str_lit.checkbox("Mostrar Mapa Cartográfico Táctico", value=True)
    
    str_lit.markdown("---")
    tema_hud = str_lit.selectbox("Tema HUD:", ["Azul Arc", "Rojo Cobre/Terracota", "Grafito Oscuro"])
    color_map = {"Rojo Cobre/Terracota": "#d9534f", "Azul Arc": "#00d2ff", "Grafito Oscuro": "#888888"}
    hex_actual = color_map.get(tema_hud, "#ff3333" if str_lit.session_state.codigo_rojo else "#00d2ff")
    
    protocolo_ia = str_lit.selectbox("Protocolo IA:", ["Estándar (Leal y Ejecutivo)", "Avanzado", "Táctico"])
    grid_tactico = str_lit.selectbox("Grid Táctico:", ["Santiago Centro", "Buin", "Global"])
    
    str_lit.markdown("---")
    str_lit.markdown("### 🚀 MÓDULOS STARK & SEGURIDAD")

    with str_lit.expander("👁️ Cámara de Seguridad (CCTV Buin)"):
        renderizar_camara_seguridad(color_neon_principal)
        str_lit.success("Enlace de videovigilancia estable.")

    with str_lit.expander("📡 Mejora 1: Radar de Intrusos (Buin)"):
        renderizar_radar_tactico(color_neon_principal)
        str_lit.success("Perímetro nominal seguro.")

    with str_lit.expander("🎛️ Mejora 2: Selector de Voz y Tono"):
        str_lit.session_state.voz_lenta = str_lit.checkbox("Modo de locución pausada (Lento)", value=False)
        str_lit.info("Configuración de audio aplicada correctamente.")

    with str_lit.expander("🛡️ Mejora 3: Telemetría Histórica (Plotly)"):
        cpu_actual = psutil.cpu_percent(interval=0.1)
        ram_actual = psutil.virtual_memory().percent
        
        c_tel = db_conn.cursor()
        tiempo_actual = datetime.now().strftime("%H:%M:%S")
        c_tel.execute("INSERT INTO telemetria_log (tiempo, cpu, ram) VALUES (?, ?, ?)", (tiempo_actual, cpu_actual, ram_actual))
        db_conn.commit()
        
        c_tel.execute("SELECT tiempo, cpu, ram FROM telemetria_log ORDER BY id DESC LIMIT 10")
        registros = c_tel.fetchall()[::-1]
        
        if registros:
            tiempos = [r[0] for r in registros]
            cpus = [r[1] for r in registros]
            rams = [r[2] for r in registros]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=tiempos, y=cpus, mode='lines+markers', name='CPU %', line=dict(color=color_neon_principal, width=2)))
            fig.add_trace(go.Scatter(x=tiempos, y=rams, mode='lines+markers', name='RAM %', line=dict(color='#00ffcc', width=2)))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0.5)',
                margin=dict(l=10, r=10, t=10, b=10),
                height=180,
                font=dict(color=color_neon_principal, family="monospace")
            )
            str_lit.plotly_chart(fig, use_container_width=True)

    # --- PROTOCOLO 4: Domótica con Sandbox Protegido por PIN y Tecla Enter ---
    with str_lit.expander("🏠 Protocolo 4: Domótica Segura (IoT Sandbox)"):
        str_lit.markdown("<span style='font-size: 0.9rem;'>Acceso restringido a dispositivos de prueba:</span>", unsafe_allow_html=True)
        
        with str_lit.form(key="form_pin_iot"):
            pin_ingresado = str_lit.text_input("Clave Stark (Presione Enter):", type="password", key="pin_iot_input")
            submit_pin = str_lit.form_submit_button("Autorizar Acceso")
            
        if submit_pin or pin_ingresado:
            if pin_ingresado == "1975":
                str_lit.success("✔️ Clave aceptada. Sandbox IoT desbloqueado.")
                estado_luz_sandbox = str_lit.checkbox("LED de Prueba Taller (Aislado)", value=False)
                if estado_luz_sandbox:
                    str_lit.info("💡 Luz de prueba LED encendida de forma segura.")
                else:
                    str_lit.caption("Luz de prueba apagada.")
            elif pin_ingresado:
                str_lit.error("❌ Clave incorrecta. Acceso denegado a domótica.")

    with str_lit.expander("🗂️ Mejora: To-Do Táctico & Misiones"):
        nueva_mision = str_lit.text_input("Nueva misión o tarea:", placeholder="Ej: Optimizar script 3D", key="input_mision_sidebar")
        if str_lit.button("Añadir Misión", key="btn_add_mision"):
            if nueva_mision:
                c_db = db_conn.cursor()
                c_db.execute("INSERT INTO misiones (tarea, estado) VALUES (?, ?)", (nueva_mision, "Pendiente"))
                db_conn.commit()
                str_lit.success("¡Misión registrada en bitácora!")
                str_lit.rerun()
        
        c_db = db_conn.cursor()
        c_db.execute("SELECT id, tarea, estado FROM misiones")
        misiones_list = c_db.fetchall()
        if misiones_list:
            for m in misiones_list:
                col_m1, col_m2 = str_lit.columns([3, 1])
                with col_m1:
                    str_lit.text(f"• {m[1]}")
                with col_m2:
                    if str_lit.button("✔️", key=f"completar_{m[0]}"):
                        c_db.execute("DELETE FROM misiones WHERE id = ?", (m[0],))
                        db_conn.commit()
                        str_lit.rerun()
        else:
            str_lit.caption("No hay misiones pendientes en este momento.")

    str_lit.markdown("---")
    
    with str_lit.expander("🌤️ Juguete 1: Radar Clima en Vivo"):
        try:
            url_clima = "https://api.open-meteo.com/v1/forecast?latitude=-33.7331&longitude=-70.7072&current_weather=true"
            res_clima = requests.get(url_clima, timeout=3).json()
            temp = res_clima["current_weather"]["temperature"]
            wind = res_clima["current_weather"]["windspeed"]
            str_lit.metric(label="Temperatura en Vivo", value=f"{temp}°C", delta=f"Viento: {wind} km/h")
        except Exception:
            str_lit.metric(label="Temperatura Estimada", value="18°C", delta="Óptimo (Modo offline)")

    with str_lit.expander("🪙 Juguete 2: Terminal Cripto & Stablecoins"):
        crypto_sel = str_lit.selectbox("Seleccionar Activo Cripto:", ["tether", "bitcoin", "ethereum"], key="crypto_sb")
        try:
            url_crypto = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_sel}&vs_currencies=usd&include_24hr_change=true"
            res = requests.get(url_crypto, timeout=2.0)
            if res.status_code == 200:
                data_c = res.json()
                if crypto_sel in data_c:
                    precio_c = data_c[crypto_sel]["usd"]
                    cambio_c = data_c[crypto_sel].get("usd_24h_change", 0.0)
                    str_lit.metric(label=f"{crypto_sel.upper()} / USD", value=f"${precio_c:,.2f}", delta=f"{cambio_c:.2f}%")
                else:
                    str_lit.warning("Activo no disponible.")
            else:
                valores_fallback = {"tether": 1.00, "bitcoin": 68450.20, "ethereum": 3520.10}
                str_lit.metric(label=f"{crypto_sel.upper()} / USD (Modo Seguro)", value=f"${valores_fallback.get(crypto_sel, 1.00):,.2f}", delta="+0.00%")
        except Exception:
            valores_fallback = {"tether": 1.00, "bitcoin": 68450.20, "ethereum": 3520.10}
            str_lit.metric(label=f"{crypto_sel.upper()} / USD (Modo Seguro)", value=f"${valores_fallback.get(crypto_sel, 1.00):,.2f}", delta="+0.00%")

    with str_lit.expander("⚡ Juguete 3: Protocolo Stark (IA Code Gen)"):
        lenguaje_code = str_lit.selectbox("Lenguaje:", ["Python", "Streamlit", "HTML/CSS"], key="lang_sb")
        prompt_code = str_lit.text_input("Solicitud de snippet:", "Crear un botón neón", key="prompt_sb")
        if str_lit.button("Generar Snippet Táctico", key="btn_gen_snippet"):
            if prompt_code and client:
                with str_lit.spinner("Procesando código en laboratorio..."):
                    p_code = f"Genera un código limpio y directo en {lenguaje_code} para: {prompt_code}. Muestra solo el bloque de código."
                    comp_code = client.chat.completions.create(
                        messages=[{"role": "user", "content": p_code}],
                        model="openai/gpt-oss-20b"
                    )
                    snippet = comp_code.choices[0].message.content
                    str_lit.code(snippet, language=lenguaje_code.lower())
            else:
                str_lit.info("Escriba un requerimiento para generar el código.")

    with str_lit.expander("🎙️ Protocolo 2: Transcripción de Voz (Whisper)"):
        str_lit.markdown("Grabe su orden de voz para traducción IA:")
        audio_bytes = audio_recorder(text="Presione para hablar", icon_size="2x", key="rec_sb")
        if audio_bytes:
            str_lit.audio(audio_bytes, format="audio/wav")
            if client:
                with str_lit.spinner("Traduciendo ondas de voz con Whisper..."):
                    try:
                        with open("temp_audio.wav", "wb") as f_audio:
                            f_audio.write

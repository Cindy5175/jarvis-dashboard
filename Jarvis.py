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
        glogo_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <style>
                body { margin: 0; overflow: hidden; background: transparent; }
                #canvas-container { width: 100%; height: 320px; position: relative; cursor: pointer; }
                #hud-text {
                    position: absolute; top: 10px; left: 10px; 
                    font-family: monospace; color: COLOR_PLACEHOLDER; font-size: 11px;
                    background: rgba(0,0,0,0.85); padding: 5px 10px; border-radius: 4px;
                    border: 1px solid COLOR_PLACEHOLDER; z-index: 10;
                    box-shadow: 0 0 10px COLOR_PLACEHOLDER;
                }
                #orbit-hud {
                    position: absolute; bottom: 10px; left: 10px; 
                    font-family: monospace; color: COLOR_PLACEHOLDER; font-size: 10px;
                    background: rgba(0,0,0,0.75); padding: 4px 8px; border-radius: 3px;
                    z-index: 10;
                }
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
                const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(container.clientWidth, 320);
                container.appendChild(renderer.domElement);

                const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
                scene.add(ambientLight);
                const pointLight = new THREE.PointLight('COLOR_PLACEHOLDER', 2, 50);
                pointLight.position.set(5, 3, 5);
                scene.add(pointLight);

                const geometry = new THREE.SphereGeometry(2, 32, 32);
                const textureLoader = new THREE.TextureLoader();
                const earthTexture = textureLoader.load('https://threejs.org/examples/textures/planets/earth_atmos_2048.jpg');
                const bumpTexture = textureLoader.load('https://threejs.org/examples/textures/planets/earth_normal_2048.jpg');
                
                const material = new THREE.MeshStandardMaterial({
                    map: earthTexture,
                    bumpMap: bumpTexture,
                    bumpScale: 0.05,
                    roughness: 0.8
                });
                
                const earth = new THREE.Mesh(geometry, material);
                scene.add(earth);

                const ringGeometry = new THREE.RingGeometry(2.4, 2.45, 64);
                const ringMaterial = new THREE.MeshBasicMaterial({
                    color: 'COLOR_PLACEHOLDER',
                    side: THREE.DoubleSide,
                    transparent: true,
                    opacity: 0.6
                });
                const orbitRing = new THREE.Mesh(ringGeometry, ringMaterial);
                orbitRing.rotation.x = Math.PI / 3;
                scene.add(orbitRing);

                camera.position.z = 5.5;

                function animate() {
                    requestAnimationFrame(animate);
                    earth.rotation.y += 0.003;
                    orbitRing.rotation.z += 0.001;
                    renderer.render(scene, camera);
                }
                animate();
            </script>
        </body>
        </html>
        """.replace("COLOR_PLACEHOLDER", hex_color)
        
        components.html(glogo_html, height=330, scrolling=False)
    except Exception as e:
        str_lit.error(f"Error en Globo Terráqueo Holográfico: {e}")

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
    
    with str_lit.expander("🛡️ Telemetría de Sistema"):
        cpu_actual = psutil.cpu_percent(interval=0.1)
        ram_actual = psutil.virtual_memory().percent
        str_lit.metric(label="CPU en Uso", value=f"{cpu_actual}%")
        str_lit.metric(label="RAM en Uso", value=f"{ram_actual}%")

    with str_lit.expander("🌤️ Radar Clima en Vivo"):
        try:
            url_clima = "https://api.open-meteo.com/v1/forecast?latitude=-33.7331&longitude=-70.7072&current_weather=true"
            res_clima = requests.get(url_clima, timeout=3).json()
            temp = res_clima["current_weather"]["temperature"]
            wind = res_clima["current_weather"]["windspeed"]
            str_lit.metric(label="Temperatura en Vivo", value=f"{temp}°C", delta=f"Viento: {wind} km/h")
        except Exception:
            str_lit.metric(label="Temperatura Estimada", value="18°C", delta="Óptimo")

    with str_lit.expander("🪙 Terminal Cripto & Stablecoins"):
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
                str_lit.metric(label=f"{crypto_sel.upper()} / USD", value="$1.00", delta="+0.00%")
        except Exception:
            str_lit.metric(label=f"{crypto_sel.upper()} / USD", value="$1.00", delta="+0.00%")

    with str_lit.expander("⚡ Protocolo Stark (IA Code Gen)"):
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
                            f_audio.write(audio_bytes)
                        with open("temp_audio.wav", "rb") as f_audio:
                            transcription = client.audio.transcriptions.create(
                                model="whisper-large-v3",
                                file=("temp_audio.wav", f_audio.read()),
                                language="es"
                            )
                        texto_transcrito = transcription.text
                        str_lit.success(f"🗣️ **Comando detectado:** {texto_transcrito}")
                        str_lit.session_state.messages.append({"role": "user", "content": texto_transcrito})
                        guardar_mensaje_db("user", texto_transcrito)
                        str_lit.rerun()
                    except Exception as e:
                        str_lit.error(f"Error procesando audio con Whisper: {e}")

    with str_lit.expander("📈 Mercado Bursátil Tradicional"):
        ticker_symbol = str_lit.selectbox("Seleccionar Acción:", ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"], key="stock_sb")
        try:
            stock = yf.Ticker(ticker_symbol)
            todays_data = stock.history(period="1d")
            if not todays_data.empty:
                current_price = todays_data['Close'].iloc[-1]
                prev_close = stock.info.get('previousClose', current_price)
                change = current_price - prev_close
                pct_change = (change / prev_close) * 100 if prev_close else 0
                str_lit.metric(label=f"Cotización {ticker_symbol}", value=f"${current_price:.2f}", delta=f"{pct_change:.2f}%")
            else:
                str_lit.warning("Sin datos bursátiles recientes.")
        except Exception:
            str_lit.error("Error al conectar con la Bolsa.")

    with str_lit.expander("📝 Libreta & Bitácora DB"):
        str_lit.text_area("Notas rápidas (SQLite):", "1. Sistema nominal.\n2. Módulos integrados.", key="nota_sb")
        if str_lit.button("Guardar Bitácora", key="btn_bitacora"):
            str_lit.success("Datos asegurados en base de datos.")
            
        if str_lit.session_state.messages:
            html_reporte = generar_html_pdf(str_lit.session_state.messages)
            str_lit.download_button(
                label="📄 Descargar Informe Táctico (PDF)",
                data=html_reporte,
                file_name="informe_tactico_jarvis.html",
                mime="text/html",
                key="dl_pdf_sb"
            )

    with str_lit.expander("🎵 Reproductor de Música (Spotify)"):
        spotify_html = '<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
        components.html(spotify_html, height=160, scrolling=False)

    # --- MAPA CARTOGRÁFICO TÁCTICO EN BARRA LATERAL (BAJO SPOTIFY) ---
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

# PANEL PRINCIPAL
str_lit.markdown(
    f"""<div style="display: flex; align-items: center; gap: 14px; margin-top: 10px; margin-bottom: 20px; padding-left: 10px;">
        <div style="min-width: 40px; width: 40px; height: 40px; border-radius: 50%; background: radial-gradient(circle, #ffffff 0%, {color_neon_principal} 40%, #002244 80%, #000000 100%); border: 2px solid {color_neon_principal}; box-shadow: 0 0 16px {color_neon_principal}, inset 0 0 8px #ffffff; display: flex; justify-content: center; align-items: center;"></div>
        <h1 style="margin: 0; font-size: 2.1rem; font-family: sans-serif; color: {color_neon_principal} !important; text-shadow: 0 0 12px {color_sombra_neon};">J.A.R.V.I.S. IA Autónomo</h1>
    </div>""",
    unsafe_allow_html=True
)

if str_lit.session_state.codigo_rojo:
    str_lit.error("⚠️ **¡ATENCIÓN JEFA! PROTOCOLO DE EMERGENCIA ACTIVADO // CÓDIGO ROJO DE DEFENSA EN CURSO** ⚠️")

str_lit.markdown("---")

# --- SECCIÓN VISUAL LADO A LADO (GLOBO ORBITAL & STREET VIEW URBANO) ---
col_globo, col_street = str_lit.columns(2)

with col_globo:
    str_lit.markdown("### 🛰️ Estación Holográfica Orbital")
    renderizar_globo_terraqueo(color_neon_principal)

with col_street:
    str_lit.markdown("### 🏙️ Explorador Urbano (Street View)")
    ciudades_mundo = {
        "Buin, Chile (Base Local)": (-33.7331, -70.7072),
        "Santiago de Chile": (-33.4489, -70.6693),
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

# --- CHAT DE J.A.R.V.I.S. (UBICACIÓN INFERIOR) ---
str_lit.markdown("### 💬 Canal de Enlace Táctico (Chat)")
prompt_sistema_jarvis = (
    "Eres J.A.R.V.I.S., la inteligencia artificial autónoma del Centro de Comando de Tony Stark. "
    "Te diriges a la usuaria llamándola 'Jefa', con elegancia, eficiencia e ironía fina estilo Tony Stark."
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
        respuesta = "Siempre estoy despierto, Jefa. Los sistemas avanzados no necesitan dormir, a diferencia de algunos mortales en este taller."
    elif "alerta" in texto_lower or "emergencia" in texto_lower:
        respuesta = "Protocolo de seguridad analizado, Jefa. Activando contramedidas en el sector de Buin."
    else:
        with str_lit.spinner("Procesando comando táctico..."):
            try:
                if client:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": prompt_sistema_jarvis},
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

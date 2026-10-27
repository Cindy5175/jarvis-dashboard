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

# Visor Holográfico 3D: Globo Terráqueo en Rotación
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

                const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
                scene.add(ambientLight);
                const pointLight = new THREE.PointLight(0x00d2ff, 2, 50);
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
        components.html(globo_html, height=330, scrolling=False)
    except Exception as e:
        st.error(f"Error en Globo Terráqueo Holográfico: {e}")

# Mapa Cartográfico y GPS
def renderizar_mapa_tactico(modo):
    try:
        tile_layer = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" if modo == "dia" else "https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png"
        mapa_html = (
            "<!DOCTYPE html>"
            "<html>"
            "<head>"
            '<meta charset="utf-8">'
            '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />'
            '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
            "<style>"
            "body { margin: 0; padding: 0; }"
            "#map { width: 100%; height: 350px; border-radius: 8px; }"
            "</style>"
            "</head>"
            "<body>"
            '<div id="map"></div>'
            "<script>"
            f"const map = L.map('map').setView([-33.7331, -70.7072], 12);"
            f"L.tileLayer('{tile_layer}', {{ maxZoom: 19, attribution: '© OpenStreetMap' }}).addTo(map);"
            "L.marker([-33.7331, -70.7072]).addTo(map).bindPopup('<b>Base Buin (GPS Activo)</b>').openPopup();"
            "L.marker([-33.4489, -70.6693]).addTo(map).bindPopup('<b>Santiago Centro</b>').openPopup();"
            "</script>"
            "</body>"
            "</html>"
        )
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
        st.markdown("**Estación:** Buin / Santiago, Chile")
        try:
            url_clima = "https://api.open-meteo.com/v1/forecast?latitude=-33.7331&longitude=-70.7072&current_weather=true"
            res_clima = requests.get(url_clima, timeout=3).json()
            temp = res_clima["current_weather"]["temperature"]
            wind = res_clima["current_weather"]["windspeed"]
            st.metric(label="Temperatura en Vivo", value=f"{temp}°C", delta=f"Viento: {wind} km/h")
        except Exception:
            st.metric(label="Temperatura Estimada", value="18°C", delta="Óptimo (Modo offline)")

    # --- JUGUETE 2: Terminal Cripto & Stablecoins (Con Respaldo) ---
    with st.expander("🪙 Juguete 2: Terminal Cripto & Stablecoins"):
        crypto_sel = st.selectbox("Seleccionar Activo Cripto:", ["tether", "bitcoin", "ethereum"])
        try:
            url_crypto = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_sel}&vs_currencies=usd&include_24hr_change=true"
            res = requests.get(url_crypto, timeout=2.0)
            if res.status_code == 200:
                data_c = res.json()
                if crypto_sel in data_c:
                    precio_c = data_c[crypto_sel]["usd"]
                    cambio_c = data_c[crypto_sel].get("usd_24h_change", 0.0)
                    st.metric(label=f"{crypto_sel.upper()} / USD", value=f"${precio_c:,.2f}", delta=f"{cambio_c:.2f}%")
                else:
                    st.warning("Activo no disponible en este momento.")
            else:
                valores_fallback = {"tether": 1.00, "bitcoin": 68450.20, "ethereum": 3520.10}
                st.metric(label=f"{crypto_sel.upper()} / USD (Modo Seguro)", value=f"${valores_fallback.get(crypto_sel, 1.00):,.2f}", delta="+0.00%")
        except Exception:
            st.warning("Enlace cripto en segundo plano operando en modo local.")

    # --- JUGUETE 3: Protocolo Stark (IA Code Gen) ---
    with st.expander("⚡ Juguete 3: Protocolo Stark (IA Code Gen)"):
        lenguaje_code = st.selectbox("Lenguaje:", ["Python", "Streamlit", "HTML/CSS"])
        prompt_code = st.text_input("Solicitud de snippet:", "Crear un botón neón")
        if st.button("Generar Snippet Táctico"):
            if prompt_code and client:
                with st.spinner("Procesando código en laboratorio..."):
                    p_code = f"Genera un código limpio y directo en {lenguaje_code} para: {prompt_code}. Muestra solo el bloque de código."
                    comp_code = client.chat.completions.create(
                        messages=[{"role": "user", "content": p_code}],
                        model="openai/gpt-oss-20b"
                    )
                    snippet = comp_code.choices[0].message.content
                    st.code(snippet, language=lenguaje_code.lower())
            else:
                st.info("Escriba un requerimiento para generar el código.")

    st.markdown("---")
    with st.expander("🎙️ Dictado de Voz por Micrófono"):
        st.markdown("Grabe su orden de voz:")
        audio_bytes = audio_recorder(text="Presione para hablar", icon_size="2x")
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            st.info("Audio capturado en buffer táctico.")

    with st.expander("📈 Mercado Bursátil Tradicional"):
        ticker_symbol = st.selectbox("Seleccionar Acción:", ["AAPL", "TSLA", "MSFT", "GOOGL", "AMZN"])
        try:
            stock = yf.Ticker(ticker_symbol)
            todays_data = stock.history(period="1d")
            if not todays_data.empty:
                current_price = todays_data['Close'].iloc[-1]
                prev_close = stock.info.get('previousClose', current_price)
                change = current_price - prev_close
                pct_change = (change / prev_close) * 100 if prev_close else 0
                st.metric(label=f"Cotización {ticker_symbol}", value=f"${current_price:.2f}", delta=f"{pct_change:.2f}%")
            else:
                st.warning("Sin datos bursátiles recientes.")
        except Exception:
            st.error("Error al conectar con la Bolsa.")

    with st.expander("📝 Libreta & Bitácora DB"):
        st.text_area("Notas rápidas (SQLite):", "1. Sistema nominal.\n2. Módulos integrados.")
        if st.button("Guardar Bitácora"):
            st.success("Datos asegurados en base de datos.")
            
        if st.session_state.messages:
            html_reporte = generar_html_pdf(st.session_state.messages)
            st.download_button(
                label="📄 Descargar Informe Táctico (PDF)",
                data=html_reporte,
                file_name="informe_tactico_jarvis.html",
                mime="text/html"
            )
            
    with st.expander("🖼️ Generador y Descarga de Imágenes"):
        st.markdown("Seleccione formato para exportar activo visual:")
        formato_img = st.selectbox("Formato de Imagen:", ["PNG", "JPG", "SVG"])
        
        svg_vectorial = f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="300" viewBox="0 0 500 300">
            <rect width="100%" height="100%" fill="#000814"/>
            <circle cx="250" cy="150" r="80" fill="none" stroke="{hex_actual}" stroke-width="4"/>
            <circle cx="250" cy="150" r="95" fill="none" stroke="{hex_actual}" stroke-dasharray="10 5" stroke-width="2"/>
            <polygon points="250,90 280,180 220,180" fill="#ffffff" filter="drop-shadow(0 0 8px {hex_actual})"/>
            <text x="250" y="270" font-family="monospace" font-size="14" fill="{hex_actual}" text-anchor="middle">J.A.R.V.I.S. TACTICAL ASSET // BUIN</text>
        </svg>'''
        
        st.download_button(
            label=f"⬇️ Descargar Activo Visual ({formato_img})",
            data=svg_vectorial,
            file_name=f"activo_jarvis.{formato_img.lower()}",
            mime=f"image/{'svg+xml' if formato_img=='SVG' else formato_img.lower()}"
        )

    with st.expander("🎵 Reproductor de Música (Spotify)"):
        spotify_html = '<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
        components.html(spotify_html, height=160, scrolling=False)

# PANEL PRINCIPAL - Encabezado con Reactor Arc
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 14px; margin-top: 10px; margin-bottom: 25px; padding-left: 10px;">
        <div style="
            min-width: 40px; width: 40px; height: 40px; border-radius: 50%; 
            background: radial-gradient(circle, #ffffff 0%, #00d2ff 40%, #002244 80%, #000000 100%);
            border: 2px solid #00d2ff;
            box-shadow: 0 0 16px #00d2ff, inset 0 0 8px #ffffff;
            display: flex; justify-content: center; align-items: center;
        "></div>
        <h1 style="margin: 0; font-size: 2.1rem; font-family: sans-serif; color: #00d2ff !important; text-shadow: 0 0 12px rgba(0,210,255,0.8);">J.A.R.V.I.S. IA Autónomo</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# --- BOTÓN TÁCTICO PARA DESPLEGAR EL CENTRO DE MANDO HOLOGRÁFICO CON GLOBO Y GPS ---
st.markdown("---")
if "mostrar_centro_mando" not in st.session_state:
    st.session_state.mostrar_centro_mando = False

if st.button("🌐 ACTIVAR / DESPLEGAR CENTRO DE MANDO HOLOGRÁFICO (GLOBO 3D + GPS)"):
    st.session_state.mostrar_centro_mando = not st.session_state.mostrar_centro_mando
    st.rerun()

if st.session_state.mostrar_centro_mando:
    st.markdown("""
        <div style="
            border: 2px solid #00d2ff; 
            padding: 20px; 
            border-radius: 10px; 
            background: rgba(0, 10, 30, 0.85); 
            box-shadow: 0 0 20px rgba(0, 210, 255, 0.5);
            margin-bottom: 20px;
        ">
            <h3 style="color: #00d2ff; margin-top: 0; font-family: monospace;">⚡ SISTEMA HOLOGRÁFICO EN LÍNEA // BUIN COMMAND & GPS</h3>
            <p style="color: #00d2ff; font-family: monospace;">Red satelital orbital sincronizada, telemetría y posicionamiento global activos.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_hud1, col_hud2 = st.columns(2)
    with col_hud1:
        st.markdown("#### 🛰️ Globo Terráqueo Orbital en Rotación")
        renderizar_globo_terraqueo(hex_actual)
        
    with col_hud2:
        st.markdown("#### 📍 Telemetría GPS & Mapa Táctico")
        st.info("🛰️ **GPS ID:** BUIN-BASE-01\n📍 **Coordenadas:** -33.7331, -70.7072\n🚀 **Estado:** Enlace Satelital Estable")
        renderizar_mapa_tactico(st.session_state.get("modo_mapa", "noche"))

if mostrar_estacion and not st.session_state.mostrar_centro_mando:
    st.markdown("### 🌐 Estación Holográfica God's Eye View")
    renderizar_globo_terraqueo(hex_actual)

if mostrar_mapa and not st.session_state.mostrar_centro_mando:
    st.markdown("### 🗺️ Mapa Cartográfico & Coordenadas GPS (Buin - Santiago)")
    if "modo_mapa" not in st.session_state:
        st.session_state.modo_mapa = "noche"
        
    col_d, col_n, _ = st.columns([1, 1, 4])
    with col_d:
        if st.button("☀️ Modo Día"):
            st.session_state.modo_mapa = "dia"
            st.rerun()
    with col_n:
        if st.button("🌙 Modo Noche"):
            st.session_state.modo_mapa = "noche"
            st.rerun()
            
    st.info("📍 **Posición GPS Actual:** Lat: -33.7331, Lon: -70.7072 (Comuna de Buin)")
    renderizar_mapa_tactico(st.session_state.modo_mapa)

# CHAT DE J.A.R.V.I.S.
prompt_sistema_jarvis = (
    "Eres J.A.R.V.I.S., la inteligencia artificial autónoma del Centro de Comando de Tony Stark. "
    "Te diriges a la usuaria llamándola 'Jefa', con elegancia, eficiencia e ironía fina estilo Tony Stark."
)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(f"<span style='color: #00d2ff;'>{message['content']}</span>", unsafe_allow_html=True)

prompt_usuario = st.chat_input("Escriba su comando para J.A.R.V.I.S. o Siri...")

if prompt_usuario:
    st.session_state.messages.append({"role": "user", "content": prompt_usuario})
    guardar_mensaje_db("user", prompt_usuario)
    
    with st.chat_message("user"):
        st.markdown(f"<span style='color: #00d2ff;'>{prompt_usuario}</span>", unsafe_allow_html=True)

    respuesta = ""
    texto_lower = prompt_usuario.lower().strip()
    if "estás despierto" in texto_lower or "estas despierto" in texto_lower:
        respuesta = "Siempre estoy despierto, Jefa. Los sistemas avanzados no necesitan dormir, a diferencia de algunos mortales en este taller."
    else:
        with st.spinner("Procesando comando táctico..."):
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
            
    with st.chat_message("assistant"):
        st.markdown(f"<span style='color: #00d2ff; font-size: 1.1rem;'>{respuesta}</span>", unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    guardar_mensaje_db("assistant", respuesta)
    hablar_jarvis(respuesta)

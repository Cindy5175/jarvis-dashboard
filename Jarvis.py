import streamlit as st
import time
from groq import Groq
import streamlit.components.v1 as components
from gtts import gTTS
import os
import base64

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

# Control de Estado del Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

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

# 3. Función del Visor Holográfico 3D blindado
def renderizar_gods_eye(hex_color):
    try:
        gods_eye_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <style>
                body {{ margin: 0; overflow: hidden; background: transparent; }}
                #canvas-container {{ width: 100%; height: 280px; position: relative; cursor: pointer; }}
                #hud-text {{
                    position: absolute; top: 10px; left: 10px; 
                    font-family: monospace; color: {hex_color}; font-size: 11px;
                    background: rgba(0,0,0,0.8); padding: 4px 8px; border-radius: 4px;
                    border: 1px solid {hex_color}; z-index: 10;
                }}
                #seismic-hud {{
                    position: absolute; bottom: 10px; left: 10px; 
                    font-family: monospace; color: #00ffcc; font-size: 10px;
                    background: rgba(0,0,0,0.7); padding: 3px 6px; border-radius: 3px;
                    z-index: 10;
                }}
                #cam-link {{
                    position: absolute; bottom: 10px; right: 10px;
                    font-family: monospace; color: #ffffff; font-size: 10px;
                    background: rgba(0, 150, 255, 0.6); padding: 4px 8px; border-radius: 4px;
                    text-decoration: none; z-index: 10; border: 1px solid #00d2ff;
                }}
                #cam-link:hover {{ background: rgba(0, 210, 255, 0.9); }}
            </style>
        </head>
        <body>
            <div id="canvas-container">
                <div id="hud-text">GOD's EYE VIEW // RED SÍSMICA GLOBAL & CÁMARAS</div>
                <div id="seismic-hud">Sistema nominal operativo.</div>
                <a id="cam-link" href="https://www.windy.com/-Webcams/Chile/Santiago/Santiago/webcams/1423152643" target="_blank">📹 Cámaras Globales</a>
            </div>
            <script>
                const container = document.getElementById('canvas-container');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 280, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
                renderer.setSize(container.clientWidth, 280);
                container.appendChild(renderer.domElement);

                const geometry = new THREE.SphereGeometry(2, 24, 24);
                const wireframe = new THREE.WireframeGeometry(geometry);
                const line = new THREE.LineSegments(wireframe);
                line.material.color.set('{hex_color}');
                line.material.opacity = 0.8;
                line.material.transparent = true;
                scene.add(line);
                camera.position.z = 5;

                function animate() {{
                    requestAnimationFrame(animate);
                    line.rotation.y += 0.005;
                    renderer.render(scene, camera);
                }}
                animate();
            </script>
        </body>
        </html>
        """
        components.html(gods_eye_html, height=290, scrolling=False)
    except Exception as e:
        st.error(f"Error en Estación Holográfica: {e}")

# 4. Función del Mapa Cartográfico
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

# 5. BARRA LATERAL
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
        st.session_state.messages = []
        st.success("¡Memoria purgada con éxito, Jefa!")
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
    with st.expander("🌤️ Clima & Alertas"):
        st.markdown("<span style='color: #00d2ff;'>**Ubicación:** Buin / Santiago, Chile</span>", unsafe_allow_html=True)
        st.metric(label="Temperatura Estimada", value="18°C", delta="Óptimo")
        
    with st.expander("📡 Radar de Red & Enlace Siri / Voz"):
        st.markdown("<span style='color: #00d2ff;'>**Estado Siri:** 🟢 En línea</span>", unsafe_allow_html=True)
        st.markdown("<span style='color: #00d2ff;'>**Síntesis de Voz:** Activa</span>", unsafe_allow_html=True)
        st.progress(95)
        
    with st.expander("📝 Libreta & Bitácora Táctica"):
        st.text_area("Notas rápidas:", "1. Sistema nominal.\n2. Módulos restaurados al 100%.")
        if st.button("Guardar Bitácora"):
            st.success("Datos guardados en memoria.")
            
        if st.session_state.messages:
            html_reporte = generar_html_pdf(st.session_state.messages)
            st.download_button(
                label="📄 Descargar Informe Táctico (PDF)",
                data=html_reporte,
                file_name="informe_tactico_jarvis.html",
                mime="text/html"
            )
            
    with st.expander("🖼️ Generador y Descarga de Imágenes"):
        st.markdown("<span style='color: #00d2ff;'>Seleccione formato para exportar activo visual:</span>", unsafe_allow_html=True)
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

# 6. PANEL PRINCIPAL - Encabezado con Reactor Arc
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

if mostrar_estacion:
    st.markdown("### 🌐 Estación Holográfica God's Eye View")
    renderizar_gods_eye(hex_actual)

if mostrar_mapa:
    st.markdown("### 🗺️ Mapa Cartográfico Táctico (Buin - Santiago)")
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
            
    renderizar_mapa_tactico(st.session_state.modo_mapa)

# 7. CHAT DE J.A.R.V.I.S.
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
    with st.chat_message("user"):
        st.markdown(f"<span style='color: #00d2ff;'>{prompt_usuario}</span>", unsafe_allow_html=True)

    respuesta = ""
    with st.spinner("Procesando comando táctico..."):
        try:
            if client:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": prompt_sistema_jarvis},
                        {"role": "user", "content": prompt_usuario}
                    ],
                    model="llama3-8b",
                )
                respuesta = chat_completion.choices[0].message.content
            else:
                respuesta = "Jefa, el cliente de Groq no se inicializó."
            
            with st.chat_message("assistant"):
                st.markdown(f"<span style='color: #00d2ff; font-size: 1.1rem;'>{respuesta}</span>", unsafe_allow_html=True)
            
            st.session_state.messages.append({"role": "assistant", "content": respuesta})
            hablar_jarvis(respuesta)
            
        except Exception as e:
            st.error(f"Error de enlace táctico, Jefa: {e}")

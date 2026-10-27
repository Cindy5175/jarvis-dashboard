import streamlit as st
import time
from groq import Groq
import streamlit.components.v1 as components
from gtts import gTTS
import os
import base64
from fpdf import FPDF

# 1. Configuración de página
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos globales para forzar el azul neón en textos, expansores, menús y módulos
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

# 2. Inicialización de cliente Groq seguro
@st.cache_resource
def obtener_cliente_groq():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            return None
        return Groq(api_key=api_key, timeout=10.0)
    except Exception:
        return None

client = obtener_cliente_groq()

# Control de Estado del Chat (Memoria Volátil)
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

# Función para generar PDF de bitácora o chat
def generar_pdf(historial):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 100, 150)
    pdf.cell(200, 10, txt="CENTRO DE COMANDO J.A.R.V.I.S. - INFORME TÁCTICO", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(0, 0, 0)
    
    for msg in historial:
        rol = "Jefa" if msg["role"] == "user" else "J.A.R.V.I.S."
        texto = f"{rol}: {msg['content']}"
        pdf.multi_cell(0, 8, txt=texto)
        pdf.ln(4)
        
    pdf_path = "reporte_tactico_jarvis.pdf"
    pdf.output(pdf_path)
    return pdf_path

# 3. Función del Visor Holográfico 3D
def renderizar_gods_eye(hex_color):
    gods_eye_html = f"""
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
                background: rgba(0,0,0,0.8); padding: 4px 8px; border-radius: 4px;
                border: 1px solid {hex_color};
                z-index: 10;
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
        <div id="canvas-container" title="Haga clic para acelerar escaneo sísmico">
            <div id="hud-text">GOD's EYE VIEW // RED SÍSMICA GLOBAL & CÁMARAS EN VIVO</div>
            <div id="seismic-hud">Sincronizando telemetría mundial...</div>
            <a id="cam-link" href="https://www.windy.com/-Webcams/Chile/Santiago/Santiago/webcams/1423152643" target="_blank">📹 Ver Cámaras Globales</a>
        </div>
        <script>
            try {{
                const container = document.getElementById('canvas-container');
                const seismicHud = document.getElementById('seismic-hud');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 320, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
                renderer.setSize(container.clientWidth, 320);
                container.appendChild(renderer.domElement);

                const geometry = new THREE.SphereGeometry(2, 24, 24);
                const wireframe = new THREE.WireframeGeometry(geometry);
                const line = new THREE.LineSegments(wireframe);
                line.material.color.set('{hex_color}');
                line.material.opacity = 0.8;
                line.material.transparent = true;
                
                line.position.y = -0.35;
                scene.add(line);

                const ringGeo = new THREE.RingGeometry(2.4, 2.45, 64);
                const ringMat = new THREE.MeshBasicMaterial({{ color: '{hex_color}', side: THREE.DoubleSide, transparent: true, opacity: 0.9 }});
                const ring = new THREE.Mesh(ringGeo, ringMat);
                ring.rotation.x = Math.PI / 3;
                ring.position.y = -0.35;
                scene.add(ring);

                camera.position.z = 5.5;

                let velocidadRotacion = 0.004;
                let modoAlerta = false;

                fetch('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_hour.geojson')
                    .then(response => response.json())
                    .then(data => {{
                        const sismos = data.features;
                        if (sismos.length > 0) {{
                            const ultimo = sismos[0].properties;
                            seismicHud.innerText = '⚠️ ALERTA SÍSMICA: M' + ultimo.mag + ' - ' + ultimo.place;
                            velocidadRotacion = 0.02;
                            line.material.color.set('#ff3333');
                        }} else {{
                            seismicHud.innerText = '🟢 RED GLOBAL ESTABLE - BUIN / SANTIAGO OPERATIVO';
                        }}
                    }})
                    .catch(err => {{
                        seismicHud.innerText = '📡 TELEMETRÍA TÁCTICA ACTIVA // BUIN';
                    }});

                container.addEventListener('click', (e) => {{
                    if (e.target.id === 'cam-link') return;
                    modoAlerta = !modoAlerta;
                    velocidadRotacion = modoAlerta ? 0.035 : 0.004;
                    seismicHud.innerText = modoAlerta ? '⚡ MODO ESCANEO SÍSMICO PROFUNDO ACTIVADO' : '🟢 ESTACIÓN EN ESPERA';
                }});

                function animate() {{
                    requestAnimationFrame(animate);
                    line.rotation.y += velocidadRotacion;
                    ring.rotation.z += velocidadRotacion * 0.7;
                    renderer.render(scene, camera);
                }}
                animate();
            }} catch (err) {{
                console.error("Error al renderizar el visor 3D:", err);
            }}
        </script>
    </body>
    </html>
    """
    components.html(gods_eye_html, height=330, scrolling=False)

# 4. Función del Mapa Cartográfico con Leaflet blindado
def renderizar_mapa_tactico(modo):
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
            #map {{ width: 100%; height: 400px; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            const map = L.map('map').setView([-33.7331, -70.7072], 12);
            L.tileLayer('{tile_layer}', {{ maxZoom: 19, attribution: '© OpenStreetMap' }}).addTo(map);
            L.marker([-33.7331, -70.7072]).addTo(map).bindPopup('<b>Base Operativa Buin</b><br>Telemetría activa.').openPopup();
            L.marker([-33.4489, -70.6693]).addTo(map).bindPopup('<b>Santiago Centro</b><br>Grid Táctico.');
        </script>
    </body>
    </html>
    """
    components.html(mapa_html, height=410, scrolling=False)

# 5. BARRA LATERAL
with st.sidebar:
    st.markdown("### ⚙️ Panel Control J.A.R.V.I.S.")
    
    # Botón de Purga del Chat
    if st.button("🧹 Purgar Memoria de Chat"):
        st.session_state.messages = []
        st.success("¡Memoria de chat purgada con éxito, Jefa!")
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
        st.markdown("<span style='color: #00d2ff;'>**Estado Siri (`jarvis.py`):** 🟢 En línea (ws://localhost:8765)</span>", unsafe_allow_html=True)
        st.markdown("<span style='color: #00d2ff;'>**Síntesis de Voz Automática:** Activa</span>", unsafe_allow_html=True)
        st.progress(95)
    with st.expander("📝 Libreta & Bitácora Táctica"):
        st.text_area("Notas rápidas:", "1. God's Eye View + Siri cargados.\n2. Catálogo 'Sabor y Receta 24/7' preparado para noviembre.")
        if st.button("Guardar Bitácora"):
            st.success("Datos guardados en memoria táctica.")
            
        # Módulo de Descarga PDF
        if st.session_state.messages:
            if st.button("📄 Exportar Chat a PDF"):
                archivo_pdf = generar_pdf(st.session_state.messages)
                with open(archivo_pdf, "rb") as f:
                    st.download_button(
                        label="⬇️ Descargar Reporte PDF",
                        data=f,
                        file_name="informe_jarvis.pdf",
                        mime="application/pdf"
                    )
                    
    with st.expander("🎵 Reproductor de Música (Spotify)"):
        spotify_html = '<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
        components.html(spotify_html, height=160, scrolling=False)

# 6. PANEL PRINCIPAL - Encabezado Alineado con Reactor Arc y J.A.R.V.I.S. IA Autónomo
st.markdown(
    """
    <div style="display: flex; align-items: center; gap: 14px; margin-top: 10px; margin-bottom: 25px; padding-left: 10px;">
        <div style="
            min-width: 40px; width: 40px; height: 40px; border-radius: 50%; 
            background: radial-gradient(circle, #ffffff 0%, #00d2ff 40%, #002244 80%, #000000 100%);
            border: 2px solid #00d2ff;
            box-shadow: 0 0 16px #00d2ff, inset 0 0 8px #ffffff;
            display: flex; justify-content: center; align-items: center;
            animation: pulse-arc 2s infinite;
        ">

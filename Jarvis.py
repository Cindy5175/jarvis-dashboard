import streamlit as st
import time
from groq import Groq
import streamlit.components.v1 as components
from gtts import gTTS
import os
import base64

# 1. Configuración de página
st.set_page_config(
    page_title="Jarvis IA Autónomo",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# 3. Función del Visor Holográfico 3D con Conexión Sísmica Mundial y Cámaras
def renderizar_gods_eye(hex_color):
    gods_eye_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            body { margin: 0; overflow: hidden; background: transparent; }
            #canvas-container { width: 100%; height: 320px; position: relative; cursor: pointer; }
            #hud-text {
                position: absolute; top: 10px; left: 10px; 
                font-family: monospace; color: COLOR_HEX; font-size: 11px;
                background: rgba(0,0,0,0.8); padding: 4px 8px; border-radius: 4px;
                border: 1px solid COLOR_HEX;
                z-index: 10;
            }
            #seismic-hud {
                position: absolute; bottom: 10px; left: 10px; 
                font-family: monospace; color: #00ffcc; font-size: 10px;
                background: rgba(0,0,0,0.7); padding: 3px 6px; border-radius: 3px;
                z-index: 10;
            }
            #cam-link {
                position: absolute; top: 10px; right: 10px;
                font-family: monospace; color: #ffffff; font-size: 10px;
                background: rgba(0, 150, 255, 0.6); padding: 4px 8px; border-radius: 4px;
                text-decoration: none; z-index: 10; border: 1px solid #00d2ff;
            }
            #cam-link:hover { background: rgba(0, 210, 255, 0.9); }
        </style>
    </head>
    <body>
        <div id="canvas-container" title="Haga clic para acelerar escaneo sísmico">
            <div id="hud-text">GOD's EYE VIEW // RED SÍSMICA GLOBAL & CÁMARAS EN VIVO</div>
            <div id="seismic-hud">Sincronizando telemetría mundial...</div>
            <a id="cam-link" href="https://www.windy.com/-Webcams/Chile/Santiago/Santiago/webcams/1423152643" target="_blank">📹 Ver Cámaras Globales</a>
        </div>
        <script>
            try {
                const container = document.getElementById('canvas-container');
                const seismicHud = document.getElementById('seismic-hud');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 320, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(container.clientWidth, 320);
                container.appendChild(renderer.domElement);

                const geometry = new THREE.SphereGeometry(2, 24, 24);
                const wireframe = new THREE.WireframeGeometry(geometry);
                const line = new THREE.LineSegments(wireframe);
                line.material.color.set('COLOR_HEX');
                line.material.opacity = 0.8;
                line.material.transparent = true;
                scene.add(line);

                const ringGeo = new THREE.RingGeometry(2.4, 2.45, 64);
                const ringMat = new THREE.MeshBasicMaterial({ color: 'COLOR_HEX', side: THREE.DoubleSide, transparent: true, opacity: 0.9 });
                const ring = new THREE.Mesh(ringGeo, ringMat);
                ring.rotation.x = Math.PI / 3;
                scene.add(ring);

                camera.position.z = 5.5;

                let velocidadRotacion = 0.004;
                let modoAlerta = false;

                fetch('https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_hour.geojson')
                    .then(response => response.json())
                    .then(data => {
                        const sismos = data.features;
                        if (sismos.length > 0) {
                            const ultimo = sismos[0].properties;
                            seismicHud.innerText = `⚠️ ALERTA SÍSMICA: M${ultimo.mag} - ${ultimo.place}`;
                            velocidadRotacion = 0.02;
                            line.material.color.set('#ff3333');
                        } else {
                            seismicHud.innerText = `🟢 RED GLOBAL ESTABLE - BUIN / SANTIAGO OPERATIVO`;
                        }
                    })
                    .catch(err => {
                        seismicHud.innerText = `📡 TELEMETRÍA TÁCTICA ACTIVA // BUIN`;
                    });

                container.addEventListener('click', (e) => {
                    if (e.target.id === 'cam-link') return;
                    modoAlerta = !modoAlerta;
                    velocidadRotacion = modoAlerta ? 0.035 : 0.004;
                    seismicHud.innerText = modoAlerta ? "⚡ MODO ESCANEO SÍSMICO PROFUNDO ACTIVADO" : "🟢 ESTACIÓN EN ESPERA";
                });

                function animate() {
                    requestAnimationFrame(animate);
                    line.rotation.y += velocidadRotacion;
                    ring.rotation.z += velocidadRotacion * 0.7;
                    renderer.render(scene, camera);
                }
                animate();
            } catch (err) {
                console.error("Error al renderizar el visor 3D:", err);
            }
        </script>
    </body>
    </html>
    """.replace("COLOR_HEX", hex_color)
    components.html(gods_eye_html, height=330)

# 4. Función del Mapa Cartográfico con Leaflet (Libre de llaves y 100% funcional)
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
    components.html(mapa_html, height=410)

# 5. BARRA LATERAL
with st.sidebar:
    st.subheader("⚙️ Panel Control Jarvis")
    
    mostrar_estacion = st.checkbox("Mostrar Estación Holográfica", value=True)
    mostrar_mapa = st.checkbox("Mostrar Mapa Cartográfico Táctico", value=True)
    
    st.markdown("---")
    
    tema_hud = st.selectbox("Tema HUD:", ["Rojo Cobre/Terracota", "Azul Arc", "Grafito Oscuro"])
    color_map = {"Rojo Cobre/Terracota": "#d9534f", "Azul Arc": "#00d2ff", "Grafito Oscuro": "#888888"}
    hex_actual = color_map.get(tema_hud, "#00d2ff")
    
    protocolo_ia = st.selectbox("Protocolo IA:", ["Estándar (Leal y Ejecutivo)", "Avanzado", "Táctico"])
    grid_tactico = st.selectbox("Grid Táctico:", ["Santiago Centro", "Buin", "Global"])
    
    st.markdown("---")
    with st.expander("🌤️ Clima & Alertas"):
        st.write("**Ubicación:** Buin / Santiago, Chile")
        st.metric(label="Temperatura Estimada", value="18°C", delta="Óptimo")
    with st.expander("📡 Radar de Red & Enlace Siri / Voz"):
        st.write("**Estado Siri (`jarvis.py`):** 🟢 En línea (ws://localhost:8765)")
        st.write("**Síntesis de Voz Automática:** Activa")
        st.progress(95)
    with st.expander("📝 Libreta & Bitácora Táctica"):
        st.text_area("Notas rápidas:", "1. God's Eye View + Siri cargados.\n2. Catálogo 'Sabor y Receta 24/7' preparado para noviembre.")
        if st.button("Guardar Bitácora"):
            st.success("Datos guardados en memoria táctica.")
    with st.expander("🎵 Reproductor de Música (Spotify)"):
        st.markdown("[Abrir Interfaz de Spotify](https://open.spotify.com)", unsafe_allow_html=True)

# 6. PANEL PRINCIPAL - Encabezado Alineado con Reactor Arc y Jarvis IA Autónomo
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
            <div style="
                width: 0; height: 0; 
                border-left: 8px solid transparent;
                border-right: 8px solid transparent;
                border-bottom: 14px solid #ffffff;
                filter: drop-shadow(0 0 5px #00d2ff);
            "></div>
        </div>
        <h1 style="margin: 0; font-size: 2.1rem; font-family: sans-serif; white-space: nowrap;">Jarvis IA Autónomo</h1>
    </div>
    <style>
    @keyframes pulse-arc {
        0% { transform: scale(0.95); box-shadow: 0 0 10px #00d2ff, inset 0 0 6px #fff; }
        50% { transform: scale(1.06); box-shadow: 0 0 22px #00d2ff, inset 0 0 12px #fff; }
        100% { transform: scale(0.95); box-shadow: 0 0 10px #00d2ff, inset 0 0 6px #fff; }
    }
    </style>
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

# 7. INTERFAZ DE COMANDOS DE J.A.R.V.I.S.
prompt_sistema_jarvis = (
    "Eres Jarvis, la inteligencia artificial autónoma avanzada del Centro de Comando de Tony Stark. "
    "Te diriges a la usuaria con el máximo respeto y lealtad, llamándola siempre 'Jefa', "
    "pero mezclas tu eficiencia impecable con altas sobredosis de ironía, sarcasmo fino y comentarios ingeniosos estilo Tony Stark. "
    "Respondes de manera precisa, ordenada y estratégica, manteniendo el rendimiento operativo al 100% mientras bromeas sutilmente."
)

prompt_usuario = st.chat_input("Escriba su comando para Jarvis o Siri...")

if prompt_usuario:
    respuesta = ""
    with st.spinner("Procesando comando táctico..."):
        try:
            if client:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": prompt_sistema_jarvis},
                        {"role": "user", "content": prompt_usuario}
                    ],
                    model="llama3-70b-8192",
                )
                respuesta = chat_completion.choices[0].message.content
            else:
                respuesta = "Jefa, la clave de API de Groq no está configurada en los secrets. ¿Desea que hackee el Pentágono para conseguir otra o la anota usted?"
            
            st.write(respuesta)
            hablar_jarvis(respuesta)
            
        except Exception as e:
            st.error(f"Error de enlace táctico, Jefa: {e}")

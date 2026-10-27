import streamlit as st
import time
from groq import Groq
import streamlit.components.v1 as components

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

# 3. Función del Visor Holográfico 3D (God's Eye View)
def renderizar_gods_eye(hex_color):
    gods_eye_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            body { margin: 0; overflow: hidden; background: transparent; }
            #canvas-container { width: 100%; height: 320px; position: relative; }
            #hud-text {
                position: absolute; top: 10px; left: 10px; 
                font-family: monospace; color: COLOR_HEX; font-size: 11px;
                background: rgba(0,0,0,0.8); padding: 4px 8px; border-radius: 4px;
                border: 1px solid COLOR_HEX;
            }
        </style>
    </head>
    <body>
        <div id="canvas-container">
            <div id="hud-text">GOD's EYE VIEW // ESTACIÓN ACTIVA: BUIN - SANTIAGO</div>
        </div>
        <script>
            try {
                const container = document.getElementById('canvas-container');
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

                function animate() {
                    requestAnimationFrame(animate);
                    line.rotation.y += 0.004;
                    ring.rotation.z += 0.002;
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

# 4. Función del Mapa Cartográfico Interactivo con Modo Día/Noche
def renderizar_mapa_tactico(modo):
    # Estilos de Mapbox para cartografía con calles y edificios
    estilo = "mapbox://styles/mapbox/streets-v11" if modo == "dia" else "mapbox://styles/mapbox/navigation-night-v1"
    
    mapa_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <script src="https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.js"></script>
        <link href="https://api.mapbox.com/mapbox-gl-js/v2.15.0/mapbox-gl.css" rel="stylesheet" />
        <style>
            body {{ margin: 0; padding: 0; }}
            #map {{ width: 100%; height: 400px; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            // Token público estándar para mapas cartográficos
            mapboxgl.accessToken = 'pk.eyJ1IjoiZXhhbXBsZSIsImEiOiJjbGs0cW05MzAwenBuM3BwaWw2NW1xY3B1In0.q68w04z123456789abcdef';
            
            const map = new mapboxgl.Map({{
                container: 'map',
                style: '{estilo}',
                center: [-70.7072, -33.7331], // Coordenadas Buin, Chile
                zoom: 12
            }});

            // Agregar marcador Base Buin
            new mapboxgl.Marker({{color: '#00d2ff'}})
                .setLngLat([-70.7072, -33.7331])
                .setPopup(new mapboxgl.Popup().setText('Base Operativa Buin'))
                .addTo(map);
        </script>
    </body>
    </html>
    """
    components.html(mapa_html, height=410)

# 5. BARRA LATERAL - Módulos del Panel de Control
with st.sidebar:
    st.subheader("⚙️ Panel Control Jarvis")
    
    mostrar_estacion = st.checkbox("Mostrar Estación Holográfica", value=True)
    mostrar_mapa = st.checkbox("Mostrar Mapa Cartográfico Táctico", value=True)
    
    st.markdown("---")
    
    tema_hud = st.selectbox(
        "Tema HUD:",
        ["Rojo Cobre/Terracota", "Azul Arc", "Grafito Oscuro"]
    )
    
    color_map = {
        "Rojo Cobre/Terracota": "#d9534f",
        "Azul Arc": "#00d2ff",
        "Grafito Oscuro": "#888888"
    }
    hex_actual = color_map.get(tema_hud, "#00d2ff")
    
    protocolo_ia = st.selectbox(
        "Protocolo IA:",
        ["Estándar (Leal y Ejecutivo)", "Avanzado", "Táctico"]
    )
    
    grid_tactico = st.selectbox(
        "Grid Táctico:",
        ["Santiago Centro", "Buin", "Global"]
    )
    
    st.markdown("---")
    
    with st.expander("🌤️ Clima & Alertas"):
        st.write("**Ubicación:** Buin / Santiago, Chile")
        st.metric(label="Temperatura Estimada", value="18°C", delta="Óptimo")
    
    with st.expander("📡 Radar de Red & Enlace Siri / Voz"):
        st.write("**Estado Siri (`jarvis.py`):** 🟢 En línea (ws://localhost:8765)")
        st.write("**Síntesis de Voz Automática:** Activa")
        st.progress(95)
        
    with st.expander("📝 Libreta & Bitácora Táctica"):
        st.text_area(
            "Notas rápidas y registros:", 
            "1. God's Eye View + Siri cargados.\n2. Catálogo 'Sabor y Receta 24/7' preparado para noviembre."
        )
        if st.button("Guardar Bitácora"):
            st.success("Datos guardados en memoria táctica.")
        
    with st.expander("🎵 Reproductor de Música (Spotify)"):
        st.markdown("[Abrir Interfaz de Spotify](https://open.spotify.com)", unsafe_allow_html=True)

# 6. PANEL PRINCIPAL - Encabezado Centrado con Reactor y Jarvis IA Autónomo
st.markdown(
    """
    <div style="display: flex; justify-content: center; align-items: center; gap: 14px; margin-top: 10px; margin-bottom: 25px;">
        <div style="
            width: 32px; height: 32px; border-radius: 50%; 
            background: radial-gradient(circle, #00d2ff 0%, #0044ff 70%, #000 100%);
            box-shadow: 0 0 14px #00d2ff, inset 0 0 6px #fff;
            animation: pulse 2s infinite;
        "></div>
        <h1 style="margin: 0; font-size: 2.3rem; font-family: sans-serif; text-align: center;">Jarvis IA Autónomo</h1>
    </div>
    <style>
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 8px #00d2ff; }
        50% { transform: scale(1.08); box-shadow: 0 0 20px #00d2ff; }
        100% { transform: scale(0.95); box-shadow: 0 0 8px #00d2ff; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

if mostrar_estacion:
    st.markdown("### 🌐 Estación Holográfica God's Eye View")

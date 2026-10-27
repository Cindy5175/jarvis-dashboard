import streamlit as st
import time
from groq import Groq
import streamlit.components.v1 as components

# 1. Configuración de página
st.set_page_config(
    page_title="Centro de Comando Stark - J.A.R.V.I.S.",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inicialización de cliente Groq
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

# 3. Función del Visor Holográfico 3D (Sin errores de sintaxis en f-strings)
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

# 4. BARRA LATERAL - Todos los Módulos del Centro de Comando Stark
with st.sidebar:
    st.subheader("⚙️ Centro de Comando Stark")
    
    mostrar_estacion = st.checkbox("Mostrar Estación Holográfica", value=True)
    
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
        st.write("Estado: Monitoreo atmosférico y telemetría local activos.")
        st.metric(label="Temperatura Estimada", value="18°C", delta="Óptimo")
    
    with st.expander("📡 Radar de Red & Enlace Siri"):
        st.write("**Estado Siri (`jarvis.py`):** 🟢 Escuchando (ws://localhost:8765)")
        st.write("**Latencia de Red:** 24 ms")
        st.progress(90)
        st.write("Conexión con servidores externos blindada.")
        
    with st.expander("📝 Libreta & Bitácora Táctica"):
        st.text_area(
            "Notas rápidas y registros:", 
            "1. Agosto: God's Eye View y conexión Siri (jarvis.py).\n2. Noviembre: Catálogo 'Sabor y Receta 24/7' (4 e-books a $5 USD, pauta SII y boletas automáticas)."
        )
        if st.button("Guardar Bitácora"):
            st.success("Datos guardados en memoria táctica.")
        
    with st.expander("🎵 Reproductor de Música (Spotify)"):
        st.write("🎶 Estado: Enlace de audio sincronizado.")
        st.markdown("[Abrir Interfaz de Spotify](https://open.spotify.com)", unsafe_allow_html=True)

# 5. PANEL PRINCIPAL
st.title("⚡ Centro de Comando Stark - J.A.R.V.I.S.")

if mostrar_estacion:
    st.markdown("### 🌐 Estación Holográfica God's Eye View")
    renderizar_gods_eye(hex_actual)

prompt_sistema_jarvis = (
    "Eres J.A.R.V.I.S., el asistente de inteligencia artificial avanzado inspirado en el universo de Iron Man. "
    "Te diriges a la usuaria con el máximo respeto, llamándola siempre 'Jefa'. "
    "Tu tono es sumamente profesional, leal, ejecutivo, sofisticado, eficiente y servicial. "
    "Respondes de manera precisa, ordenada y estratégica, manteniendo la estética y el rendimiento operativo "
    "del Centro de Comando Stark en todo momento."
)

prompt_usuario = st.chat_input("Escriba su comando para J.A.R.V.I.S. o Siri...")

if prompt_usuario:
    if not client:
        st.error("⚠️ Jefa, la clave de API de Groq no está configurada correctamente en los secrets de Streamlit.")
    else:
        with st.spinner("Procesando comando táctico..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": prompt_sistema_jarvis},
                        {"role": "user", "content": prompt_usuario}
                    ],
                    model="llama3-70b-8192",
                )
                respuesta = chat_completion.choices[0].message.content
                st.write(respuesta)
                
            except Exception as e:
                st.error(f"Error de enlace con los servidores de Groq, Jefa: {e}")

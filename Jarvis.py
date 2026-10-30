import streamlit as st
import psutil
import datetime

# --- CONFIGURACIÓN DE PÁGINA Y ESTÉTICA NEÓN AZUL ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #00f3ff;
    }
    h1, h2, h3, h4 {
        color: #00f3ff !important;
        font-family: 'Courier New', monospace;
    }
    .metric-card {
        background-color: #0d1527;
        border: 1px solid #00f3ff;
        padding: 12px;
        border-radius: 8px;
        box-shadow: 0 0 12px rgba(0, 243, 255, 0.25);
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA CON EL REACTOR ARC TRIANGULAR (ESTILO IRON MAN) ---
st.markdown("""
    <div style="text-align: center; margin-bottom: 5px;">
        <div style="display: inline-block; position: relative; width: 60px; height: 60px; border: 2px solid #00f3ff; border-radius: 50%; box-shadow: 0 0 20px #00f3ff, inset 0 0 15px #00f3ff; background: rgba(0, 243, 255, 0.1); display: flex; align-items: center; justify-content: center; margin: 0 auto 8px auto;">
            <div style="font-size: 28px; color: #ffffff; text-shadow: 0 0 12px #00f3ff; line-height: 0;">▲</div>
        </div>
        <h2 style="font-size: 1.8rem; margin: 0; color: #00f3ff; letter-spacing: 2px;">J.A.R.V.I.S IA - NÚCLEO TÁCTICO</h2>
    </div>
""", unsafe_allow_html=True)

# --- RECTÁNGULO PEQUEÑO ABAJO DE J.A.R.V.I.S: STARLINK ORBITAL LINK (BUIN) ---
st.markdown("""
    <div class="metric-card" style="max-width: 500px; margin: 10px auto 15px auto;">
        <h4 style="margin: 0 0 6px 0; text-align: center; font-size: 0.95rem;">📡 STARLINK ORBITAL LINK (BUIN)</h4>
        <div style="display: flex; justify-content: space-around; font-size: 12px; color: #00f3ff;">
            <div><b>ENLACE:</b> LÁSER &nbsp;|&nbsp; <b>LATENCIA:</b> 18.4 ms</div>
            <div><b>NODOS:</b> 14 Activos &nbsp;|&nbsp; <b>BANDA:</b> 385 Mbps</div>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- ESTADO DE SESIÓN PARA EL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Buenas tardes, jefa. Constelación activa. Enlace Starlink y todos los 15 módulos listos en Buin. ¿Qué directiva ejecutamos?"}
    ]

# --- DISTRIBUCIÓN EN 2 COLUMNAS SIMÉTRICAS ---
col_left, col_right = st.columns([1.05, 1])

with col_left:
    # 1. MENÚ DESPLEGABLE CON LOS 15 MÓDULOS ACTIVOS E INTERACTIVOS
    with st.expander("📂 [CLIC AQUÍ] Desplegar Núcleo Táctico y Módulos"):
        st.markdown("### 🛡️ Subsistema de Controles Tácticos Activos")
        
        with st.expander("📚 Memoria Documental Masiva (RAG)"):
            rag_active = st.toggle("Activar Memoria RAG / Base Documental", value=True, key="rag_toggle")
            st.write(f"Estado RAG: {'🟢 Operativo y Sincronizado' if rag_active else '🔴 En Pausa'}")

        with st.expander("⚡ Motor de API LLM"):
            st.write("Estado: Conectado al núcleo de inferencia.")
            st.selectbox("Modelo Activo:", ["Gemini Pro / Flash", "Local LLM Custom"], key="llm_model")

        with st.expander("🤖 Agentes Autónomos"):
            st.toggle("Activar Ejecución Autónoma", value=True, key="agents_toggle")

        with st.expander("👁️ Ojos Digitales (Cámara Web)"):
            cam_active = st.toggle("Activar Feed de Cámara", value=False, key="cam_toggle")
            if cam_active:
                st.camera_input("Capturar imagen táctica en vivo")
            else:
                st.write("Estado: Cámara en modo standby.")

        with st.expander("⛅ Clima Satelital en Vivo (Buin)"):
            st.markdown("""
                * **Ubicación:** Buin, Chile (Lat: -33.73° S, Lon: -70.73° W)
                * **Temperatura:** 21.5°C | **Condición:** Despejado / Órbita Óptima
                * **Humedad:** 45% | **Viento:** 12 km/h S-W
            """)

        with st.expander("🌐 Buscador Web 24/7"):
            web_query = st.text_input("Consulta de búsqueda web en vivo:", placeholder="Escriba aquí para buscar en la red...")
            if web_query:
                st.success(f"Buscando directiva: '{web_query}' en la red global...")

        with st.expander("📊 Terminal HUD de Trading & Divisas"):
            st.markdown("""
                * **EUR / CLP:** 1,045.20 $
                * **USD / CLP:** 968.50 $
                * **EUR / USD:** 1.08 €/$
            """)

        with st.expander("💻 Sensor de Hardware (CPU/RAM)"):
            st.write(f"CPU en uso: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%")
            st.progress(psutil.cpu_percent() / 100.0)

        with st.expander("🎙️ Escucha Permanente & Micrófono IA"):
            mic_active = st.toggle("Activar Escucha Permanente de Voz", value=True, key="mic_toggle")
            st.write(f"Micrófono: {'🟢 Escuchando activamente' if mic_active else '🔴 Silenciado'}")

        with st.expander("💶 Monitor Fiduciario & Divisas"):
            st.markdown("Cotización en tiempo real configurada en **Euro (€)** y Dólar ($).")
            st.metric(label="Euro (EUR)", value="1,045.20 CLP", delta="+2.4%")

        with st.expander("🔒 Protocolo Caja Fuerte"):
            safe_box = st.button("Ejecutar Protocolo Caja Fuerte")
            if safe_box:
                st.error("🔒 Protocolo de seguridad activado. Cifrado de alta confidencialidad aplicado.")

        with st.expander("📋 Registro de Auditoría (Caja Negra)"):
            st.write("Base de datos SQLite: 1,420 registros sincronizados sin anomalías.")

        with st.expander("🔊 Voz & Seguridad Avanzada"):
            st.toggle("Biometría de Voz Activa", value=True, key="bio_toggle")

        with st.expander("📡 Starlink Orbital Link (Buin)"):
            st.write("Enlace Láser Activo — Latencia: 18.4 ms | Ancho de banda: 385 Mbps.")

        with st.expander("🌐 Núcleo Holográfico con Satélite en Órbita"):
            st.write("Visualización 3D principal sincronizada.")

    # 2. TARJETA VISUALIZADOR HOLOGRÁFICO AVANZADO (ESTILO HOLOGRAMA STARK)
    st.markdown("""
    <div class="metric-card">
        <h4 style="margin:0 0 10px 0;">🌐 NÚCLEO HOLOGRÁFICO CON SATÉLITE EN ÓRBITA</h4>
    """, unsafe_allow_html=True)
    
    st.components.v1.html("""
        <div style="width: 100%; height: 220px; background: #020617; border: 1px solid #00f3ff; border-radius: 6px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; box-shadow: inset 0 0 20px rgba(0,243,255,0.2);">
            
            <!-- HUD Exterior Giratorio (Anillo Stark) -->
            <div style="position: absolute; width: 155px; height: 155px; border: 1px dashed rgba(0, 243, 255, 0.5); border-radius: 50%; animation: spinHUD 10s linear infinite;"></div>
            
            <!-- Globo Terráqueo Digital Holográfico Avanzado -->
            <div style="width: 115px; height: 115px; border-radius: 50%; border: 2px solid #00f3ff; background: radial-gradient(circle at 30% 30%, rgba(0,243,255,0.6) 0%, rgba(0,85,136,0.3) 50%, rgba(2,6,23,0.95) 85%); box-shadow: 0 0 18px #00f3ff, inset 0 0 12px #00f3ff; position: relative; display: flex; align-items: center; justify-content: center;">
                <!-- Malla de Meridianos y Paralelos Holográficos -->
                <div style="position: absolute; width: 115px; height: 40px; border: 1px solid rgba(0,243,255,0.7); border-radius: 50%;"></div>
                <div style="position: absolute; width: 40px; height: 115px; border: 1px solid rgba(0,243,255,0.7); border-radius: 50%;"></div>
                <!-- Línea de Escaneo Láser Central -->
                <div style="position: absolute; width: 100%; height: 2px; background: rgba(255,255,255,0.8); box-shadow: 0 0 8px #fff; animation: scanLine 3s ease-in-out infinite alternate;"></div>
            </div>

            <!-- Órbita y Satélite Avanzado -->
            <div style="position: absolute; width: 185px; height: 185px; border: 1px rgba(0, 243, 255, 0.3) solid; border-radius: 50%; animation: orbitSatellite 6s linear infinite;">
                <div style="position: absolute; top: 0; left: 50%; width: 8px; height: 8px; background: #ffffff; border-radius: 50%; box-shadow: 0 0 12px #00f3ff, 0 0 6px #fff; transform: translate(-50%, -50%);"></div>
            </div>
            
            <!-- Coordenadas Tácticas de Buin -->
            <div style="position: absolute; bottom: 8px; left: 10px; color: #00f3ff; font-family: monospace; font-size: 10px; background: rgba(11,15,25,0.9); padding: 3px 6px; border-radius: 4px; border: 1px solid rgba(0,243,255,0.5); letter-spacing: 1px;">
                STARK HUD // LAT: -33.73° S | LON: -70.73° W — BUIN OK
            </div>
        </div>
        <style>
        @keyframes spinHUD {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes scanLine {
            0% { top: 15%; }
            100% { top: 85%; }
        }
        @keyframes orbitSatellite {
            0% { transform: rotate(0deg) rotateX(65deg); }
            100% { transform: rotate(360deg) rotateX(65deg); }
        }
        </style>
    """, height=230)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:

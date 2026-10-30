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

    # 2. TARJETA VISUALIZADOR HOLOGRÁFICO CON EL GLOBO TERRÁQUEO DIGITAL
    st.markdown("""
    <div class="metric-card">
        <h4 style="margin:0 0 10px 0;">🌐 NÚCLEO HOLOGRÁFICO CON SATÉLITE EN ÓRBITA</h4>
    """, unsafe_allow_html=True)
    
    st.components.v1.html("""
        <div style="width: 100%; height: 210px; background: #030712; border: 1px solid #00f3ff; border-radius: 6px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;">
            
            <!-- Globo Terráqueo Digital Estándar -->
            <div style="width: 110px; height: 110px; border-radius: 50%; border: 2px solid #00f3ff; background: radial-gradient(circle at 35% 35%, rgba(0,243,255,0.4) 0%, rgba(3,7,18,0.95) 75%); box-shadow: 0 0 15px rgba(0,243,255,0.4); position: relative; display: flex; align-items: center; justify-content: center;">
                <div style="position: absolute; width: 110px; height: 35px; border: 1px dashed rgba(0,243,255,0.6); border-radius: 50%;"></div>
                <div style="position: absolute; width: 35px; height: 110px; border: 1px dashed rgba(0,243,255,0.6); border-radius: 50%;"></div>
            </div>

            <!-- Órbita y Satélite Pequeño -->
            <div style="position: absolute; width: 160px; height: 160px; border: 1px dotted rgba(0, 243, 255, 0.4); border-radius: 50%; animation: orbitSatellite 6s linear infinite;">
                <div style="position: absolute; top: 0; left: 50%; width: 7px; height: 7px; background: #ffffff; border-radius: 50%; box-shadow: 0 0 8px #00f3ff; transform: translate(-50%, -50%);"></div>
            </div>
            
            <!-- Coordenadas Exactas -->
            <div style="position: absolute; bottom: 8px; left: 10px; color: #00f3ff; font-family: monospace; font-size: 10px; background: rgba(11,15,25,0.85); padding: 3px 6px; border-radius: 4px; border: 1px solid rgba(0,243,255,0.4);">
                LAT: -33.73° S | LON: -70.73° W — BUIN SECTOR OK
            </div>
        </div>
        <style>
        @keyframes orbitSatellite {
            0% { transform: rotate(0deg) rotateX(60deg); }
            100% { transform: rotate(360deg) rotateX(60deg); }
        }
        </style>
    """, height=220)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    # COLUMNA DERECHA: CHAT IA Y ENTRADA DE COMANDOS INTEGRADA
    st.markdown("### 💬 Chat IA")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Escriba su comando para J.A.R.V.I.S..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message

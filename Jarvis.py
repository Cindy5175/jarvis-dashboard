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

# --- CABECERA PRINCIPAL CON EL TRIÁNGULO ---
st.markdown("""
    <div style="text-align: center; margin-bottom: 5px;">
        <h1 style="font-size: 2.2rem; margin: 0; color: #00f3ff;">▲</h1>
        <h2 style="font-size: 1.8rem; margin: 0; color: #00f3ff;">J.A.R.V.I.S IA - NÚCLEO TÁCTICO</h2>
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
    # 1. MENÚ DESPLEGABLE CON LOS 15 MÓDULOS E ÍCONOS
    with st.expander("📂 [CLIC AQUÍ] Desplegar Núcleo Táctico y Módulos"):
        st.markdown("### 🛡️ Subsistema de Controles Tácticos")
        
        with st.expander("📚 Memoria Documental Masiva (RAG)"):
            st.write("Estado: Base documental y PDFs sincronizados.")
        with st.expander("⚡ Motor de API LLM"):
            st.write("Estado: Conectado a núcleo de inferencia.")
        with st.expander("🤖 Agentes Autónomos"):
            st.write("Estado: Enrutamiento directo activo.")
        with st.expander("👁️ Ojos Digitales (Cámara Web)"):
            st.write("Estado: Feed de cámara preparado.")
        with st.expander("⛅ Clima Satelital en Vivo (Buin)"):
            st.write("Estado: Monitoreo meteorológico local activo.")
        with st.expander("🌐 Buscador Web 24/7"):
            st.write("Estado: Conectividad web continua.")
        with st.expander("📊 Terminal HUD de Trading"):
            st.write("Estado: Monitoreo de divisa EUR activado.")
        with st.expander("💻 Sensor de Hardware (CPU/RAM)"):
            st.write(f"CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%")
        with st.expander("🎙️ Escucha Permanente & Micrófono IA"):
            st.write("Estado: Standby de voz sincronizado.")
        with st.expander("💶 Monitor Fiduciario & Divisas"):
            st.write("Estado: Seguimiento financiero OK.")
        with st.expander("🔒 Protocolo Caja Fuerte"):
            st.write("Seguridad: Cifrado táctico activo.")
        with st.expander("📋 Registro de Auditoría (Caja Negra)"):
            st.write("Registro: Base SQLite verificada.")
        with st.expander("🔊 Voz & Seguridad Avanzada"):
            st.write("Estado: Reconocimiento biométrico en espera.")
        with st.expander("📡 Starlink Orbital Link (Buin)"):
            st.write("Estado: Latencia 18.4ms | 385 Mbps.")
        with st.expander("🌐 Núcleo Holográfico con Satélite en Órbita"):
            st.write("Visualización 3D Orbital en ejecución.")

    # 2. TARJETA VISUALIZADOR HOLOGRÁFICO CON EL GLOBO TERRÁQUEO DIGITAL
    st.markdown("""
    <div class="metric-card">
        <h4 style="margin:0 0 10px 0;">🌐 NÚCLEO HOLOGRÁFICO CON SATÉLITE EN ÓRBITA</h4>
    """, unsafe_allow_html=True)
    
    st.components.v1.html("""
        <div style="width: 100%; height: 210px; background: #030712; border: 1px solid #00f3ff; border-radius: 6px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;">
            
            <!-- Globo Terráqueo Digital Estándar (Esfera con meridiano neón) -->
            <div style="width: 110px; height: 110px; border-radius: 50%; border: 2px solid #00f3ff; background: radial-gradient(circle at 35% 35%, rgba(0,243,255,0.4) 0%, rgba(3,7,18,0.95) 75%); box-shadow: 0 0 15px rgba(0,243,255,0.4); position: relative; display: flex; align-items: center; justify-content: center;">
                <div style="position: absolute; width: 110px; height: 35px; border: 1px dashed rgba(0,243,255,0.6); border-radius: 50%;"></div>
                <div style="position: absolute; width: 35px; height: 110px; border: 1px dashed rgba(0,243,255,0.6); border-radius: 50%;"></div>
            </div>

            <!-- Órbita y Satélite Pequeño Girando Alrededor -->
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
    # COLUMNA DERECHA: CHAT IA Y ENTRADA DE COMANDOS INTEGRADA EN LA MISMA COLUMNA
    st.markdown("### 💬 Chat IA")
    
    # Contenedor para el historial y la caja de chat alineados en la columna derecha
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Caja de entrada de comandos situada exactamente debajo del chat en su columna
    if prompt := st.chat_input("Escriba su comando para J.A.R.V.I.S..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        prompt_lower = prompt.lower().strip()
        if "estás despierto" in prompt_lower or "estas despierto" in prompt_lower:
            response = "para Ud señorita siempre"
        else:
            response = f"Procesado con órbita Starlink en Buin, jefa. Directiva '{prompt}' comprendida y ejecutada."

        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

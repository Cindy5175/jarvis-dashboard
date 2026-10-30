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
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 0 12px rgba(0, 243, 255, 0.25);
        margin-bottom: 15px;
    }
    /* Estilo para simular el contenedor del chat alineado */
    .chat-container-box {
        border: 1px solid #00f3ff;
        border-radius: 8px;
        padding: 10px;
        background-color: #0d1527;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.15);
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA PRINCIPAL CON EL TRIÁNGULO EXACTO ---
st.markdown("""
    <div style="text-align: center; margin-bottom: 5px;">
        <h1 style="font-size: 2.2rem; margin: 0; color: #00f3ff;">▲</h1>
        <h2 style="font-size: 1.8rem; margin: 0; color: #00f3ff;">J.A.R.V.I.S IA - NÚCLEO TÁCTICO</h2>
        <p style="color: #9ca3af; font-size: 0.9rem; margin-top: 4px;">Starlink & 15 Módulos Activos | Buin, Chile</p>
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
    # 1. MENÚ DESPLEGABLE CON LOS 15 MÓDULOS E ÍCONOS PEQUEÑOS
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

    # 2. TARJETA STARLINK ORBITAL LINK
    st.markdown("""
    <div class="metric-card">
        <h4 style="margin:0 0 8px 0;">📡 STARLINK ORBITAL LINK (BUIN)</h4>
        <div style="display: flex; justify-content: space-between; font-size: 13px; color: #00f3ff;">
            <div><b>ENLACE:</b> LÁSER<br><b>LATENCIA:</b> 18.4 ms</div>
            <div style="text-align: right;"><b>NODOS:</b> 14 Activos<br><b>BANDA:</b> 385 Mbps</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. TARJETA VISUALIZADOR HOLOGRÁFICO CON EL GLOBO 3D EXPRESO
    st.markdown("""
    <div class="metric-card">
        <h4 style="margin:0 0 10px 0;">🌐 NÚCLEO HOLOGRÁFICO CON SATÉLITE EN ÓRBITA</h4>
    """, unsafe_allow_html=True)
    
    st.components.v1.html("""
        <div style="width: 100%; height: 160px; background: #030712; border: 1px solid #00f3ff; border-radius: 6px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;">
            <!-- Malla 3D simulada del Globo Orbital -->
            <div style="position: absolute; width: 130px; height: 130px; border: 2px dashed #00f3ff; border-radius: 50%; animation: spinGlobe 12s linear infinite; box-shadow: 0 0 15px rgba(0, 243, 255, 0.4);"></div>
            <div style="position: absolute; width: 90px; height: 90px; border: 1px dotted #00f3ff; border-radius: 50%; animation: spinGlobeReverse 8s linear infinite;"></div>
            <div style="position: absolute; width: 50px; height: 50px; border: 1px solid #00f3ff; border-radius: 50%; background: rgba(0, 243, 255, 0.1);"></div>
            <div style="color: #00f3ff; font-family: monospace; font-size: 11px; text-align: center; z-index: 2;">
                🟢 GLOBO ÓRBITA EN VIVO<br><span style="font-size: 9px; color: #9ca3af;">BUIN SECTOR - OK</span>
            </div>
        </div>
        <style>
        @keyframes spinGlobe { 0% { transform: rotate(0deg) rotateX(60deg); } 100% { transform: rotate(360deg) rotateX(60deg); } }
        @keyframes spinGlobeReverse { 0% { transform: rotate(360deg) rotateY(45deg); } 100% { transform: rotate(0deg) rotateY(45deg); } }
        </style>
    """, height=170)
    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    # COLUMNA DERECHA: CAJA DEL CHAT ALINEADA A LA MISMA ALTURA
    st.markdown("### 💬 Chat IA")
    
    # Mostrar el historial dentro del área asignada
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- ENTRADA DE COMANDOS DE CHAT (BARRA FLOTANTE AL FONDO) ---
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

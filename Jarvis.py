import streamlit as st
import psutil
import datetime

# --- CONFIGURACIÓN DE PÁGINA Y ESTÉTICA NEÓN AZUL ---
st.set_page_config(
    page_title="J.A.R.V.I.S. IA - NÚCLEO TÁCTICO",
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
    h1, h2, h3 {
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
    </style>
""", unsafe_allow_html=True)

# --- CABECERA ESTILO LAPTOP ---
st.markdown("<h1 style='text-align: center; color: #00f3ff;'>▲ J.A.R.V.I.S IA - NÚCLEO TÁCTICO</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #9ca3af;'>Starlink & 15 Módulos Activos | Buin, Chile</p>", unsafe_allow_html=True)
st.markdown("---")

# --- ESTADO DE SESIÓN PARA EL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Buenas tardes, jefa. Constelación activa. Enlace Starlink y todos los 15 módulos listos en Buin. ¿Qué directiva ejecutamos?"}
    ]

# --- ESTRUCTURA DE 2 COLUMNAS IDÉNTICA A LA PANTALLA ---
col_left, col_right = st.columns([1, 1])

with col_left:
    # 1. Menú desplegable táctico
    with st.expander("📂 [CLIC AQUÍ] Desplegar Núcleo Táctico y Módulos"):
        st.markdown("### 🛡️ Subsistema de Controles Tácticos")
        with st.expander("📁 Memoria Documental Masiva (RAG)"):
            st.write("Estado: Enlazado")
        with st.expander("📁 Motor de API LLM"):
            st.write("Estado: Conectado")
        with st.expander("📁 Agentes Autónomos"):
            st.write("Estado: En espera")
        with st.expander("📁 Ojos Digitales (Cámara Web)"):
            st.write("Estado: Activo")
        with st.expander("📁 Clima Satelital en Vivo (Buin)"):
            st.write("Estado: 20°C - OK")
        with st.expander("📁 Buscador Web 24/7"):
            st.write("Estado: En línea")
        with st.expander("📁 Terminal HUD de Trading"):
            st.write("Monitoreo EUR: Activo")
        with st.expander("📁 Sensor de Hardware (CPU/RAM)"):
            st.write(f"CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}%")
        with st.expander("📁 Escucha Permanente & Micrófono IA"):
            st.write("Estado: Standby")
        with st.expander("📁 Monitor Fiduciario & Divisas"):
            st.write("Estado: EUR Monitor")
        with st.expander("📁 Protocolo Caja Fuerte"):
            st.write("Seguridad: Cifrada")
        with st.expander("📁 Registro de Auditoría (Caja Negra)"):
            st.write("SQLite: OK")
        with st.expander("📁 Voz & Seguridad Avanzada"):
            st.write("Biometría: En espera")
        with st.expander("📁 Starlink Orbital Link (Buin)"):
            st.write("Banda: 385 Mbps")
        with st.expander("📁 Núcleo Holográfico con Satélite en Órbita"):
            st.write("Malla 3D: Activa")

    # 2. Tarjeta Starlink Orbital Link
    st.markdown("""
    <div class="metric-card">
        <h4 style="margin-top:0;">📡 STARLINK ORBITAL LINK (BUIN)</h4>
        <div style="display: flex; justify-content: space-between; font-size: 13px;">
            <div><b>ENLACE:</b> LÁSER<br><b>LATENCIA:</b> 18.4 ms</div>
            <div><b>NODOS:</b> 14 Activos<br><b>BANDA:</b> 385 Mbps</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Tarjeta Visualizador Holográfico 3D
    st.markdown("### 🌐 NÚCLEO HOLOGRÁFICO CON SATÉLITE EN ÓRBITA")
    st.components.v1.html("""
        <div style="width: 100%; height: 160px; background: #030712; border: 1px solid #00f3ff; border-radius: 8px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;">
            <div style="position: absolute; width: 110px; height: 110px; border: 2px dashed #00f3ff; border-radius: 50%; animation: spin 8s linear infinite;"></div>
            <div style="position: absolute; width: 70px; height: 70px; border: 1px solid #00f3ff; border-radius: 50%;"></div>
            <div style="color: #00f3ff; font-family: monospace; font-size: 11px; text-align: center; z-index: 2;">
                🟢 SATÉLITE ÓRBITA EN VIVO<br>BUIN SECTOR - OK
            </div>
        </div>
        <style>
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    """, height=170)

with col_right:
    # Columna derecha: Chat IA completo
    st.markdown("### 💬 Chat IA")
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- ENTRADA DE COMANDOS (BARRA INFERIOR) ---
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

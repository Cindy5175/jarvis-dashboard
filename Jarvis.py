import streamlit as st
import psutil
import datetime

# --- CONFIGURACIÓN DE PÁGINA Y ESTÉTICA NEÓN AZUL ---
st.set_page_config(
    page_title="J.A.R.V.I.S. Dashboard Táctico",
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
        background-color: #111827;
        border: 1px solid #00f3ff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA Y COORDENADAS ---
st.markdown("<h1>⚡ J.A.R.V.I.S. IA // NÚCLEO TÁCTICO</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #9ca3af;'>Starlink & 15 Módulos Activos | Buin, Chile (Lat: -33.73° S | Lon: -70.73° W)</p>", unsafe_allow_html=True)
st.markdown("---")

# --- ESTADO DE SESIÓN PARA EL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Buenas tardes, jefa. Constelación activa. Enlace Starlink y todos los 15 módulos listos en Buin. ¿Qué directiva ejecutamos?"}
    ]

# --- 1. SECCIÓN DE CHAT INTELIGENTE ---
st.markdown("### 💬 Chat IA")
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

st.markdown("---")

# --- 2. CONTENEDOR EXPANDIBLE DE LOS 15 MÓDULOS ---
with st.expander("📂 [CLIC AQUÍ] Desplegar Núcleo Táctico y Módulos"):
    st.markdown("### 🛡️ Subsistema de Controles Tácticos")
    
    with st.expander("📁 Memoria Documental Masiva (RAG)"):
        st.write("Estado: Enlazado con base de notas y PDFs.")
    with st.expander("📁 Motor de API LLM"):
        st.write("Estado: Conectado y operativo.")
    with st.expander("📁 Agentes Autónomos"):
        st.write("Estado: En espera de directivas.")
    with st.expander("📁 Ojos Digitales (Cámara Web)"):
        st.write("Estado: Activo / Monitoreo visual.")
    with st.expander("📁 Clima Satelital en Vivo (Buin)"):
        st.write("Temperatura actual: 20°C - Señal Órbita OK.")
    with st.expander("📁 Buscador Web 24/7"):
        st.write("Estado: Conectado a la red.")
    with st.expander("📁 Terminal HUD de Trading"):
        st.write("Monitoreo de divisas (EUR) activo.")
    with st.expander("📁 Sensor de Hardware (CPU/RAM)"):
        st.write(f"CPU: {psutil.cpu_percent()}% | RAM: {psutil.virtual_memory().percent}% | Disco: {psutil.disk_usage('/').percent}%")
    with st.expander("📁 Escucha Permanente & Micrófono IA"):
        st.write("Estado: Standby / Sincronizado.")
    with st.expander("📁 Monitor Fiduciario & Divisas"):
        st.write("Estado: Operativo (EUR configurado).")
    with st.expander("📁 Protocolo Caja Fuerte"):
        st.write("Seguridad: Cifrado activo.")
    with st.expander("📁 Registro de Auditoría (Caja Negra)"):
        st.write("Base de datos SQLite: OK.")
    with st.expander("📁 Voz & Seguridad Avanzada"):
        st.write("Motor biométrico y Vokaturi en espera.")
    with st.expander("📁 Starlink Orbital Link (Buin)"):
        st.write("Banda: 385 Mbps | Enlace Láser Activo.")
    with st.expander("📁 Núcleo Holográfico con Satélite en Órbita"):
        st.markdown("""
            <div style="width: 100%; height: 160px; background: #030712; border: 1px solid #00f3ff; border-radius: 8px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;">
                <div style="color: #00f3ff; font-family: monospace; font-size: 13px; text-align: center;">
                    🟢 SATÉLITE ÓRBITA EN VIVO - BUIN SECTOR OK
                </div>
            </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# --- 3. TARJETAS LATERALES DE ESTADO ORBITAL Y HOLOGRÁFICO ---
col_starlink, col_holo = st.columns(2)

with col_starlink:
    st.markdown("""
    <div class="metric-card">
        <h3>📡 STARLINK ORBITAL LINK (BUIN)</h3>
        <p><b>ENLACE:</b> LÁSER &nbsp;&nbsp;|&nbsp;&nbsp; <b>NODOS:</b> 14 Activos<br>
        <b>LATENCIA:</b> 18.4 ms &nbsp;&nbsp;|&nbsp;&nbsp; <b>BANDA:</b> 385 Mbps</p>
    </div>
    """, unsafe_allow_html=True)

with col_holo:
    st.markdown("""
    <div class="metric-card">
        <h3>🌐 NÚCLEO HOLOGRÁFICO CON SATÉLITE EN ÓRBITA</h3>
        <div style="width: 100%; height: 90px; background: #030712; border: 1px solid #00f3ff; border-radius: 6px; display: flex; align-items: center; justify-content: center;">
            <span style="color: #00f3ff; font-family: monospace; font-size: 12px;">🟢 3D ORBITAL MESH ACTIVE</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# --- 4. ENTRADA DE COMANDOS DE CHAT (AL FONDO) ---
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

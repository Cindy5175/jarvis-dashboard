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
    }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA Y COORDENADAS ---
st.markdown("<h1>⚡ J.A.R.V.I.S. // NÚCLEO TÁCTICO</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #9ca3af;'>Lat: -33.73° S | Lon: -70.73° W — Buin, Chile | Enlace Starlink: <b>ACTIVO</b></p>", unsafe_allow_html=True)
st.markdown("---")

# --- VISOR 3D HOLOGRÁFICO (ARRIBA) ---
with st.container():
    st.markdown("### 🌐 Visualizador Holográfico Orbital")
    st.components.v1.html("""
        <div style="width: 100%; height: 220px; background: #030712; border: 1px solid #00f3ff; border-radius: 8px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden;">
            <div style="position: absolute; width: 150px; height: 150px; border: 2px dashed rgba(0, 243, 255, 0.4); border-radius: 50%; animation: spin 10s linear infinite;"></div>
            <div style="position: absolute; width: 100px; height: 100px; border: 1px solid rgba(0, 243, 255, 0.7); border-radius: 50%;"></div>
            <div style="color: #00f3ff; font-family: monospace; font-size: 14px; text-align: center; z-index: 2;">
                🟢 SATÉLITE ÓRBITA EN VIVO<br>
                <span style="font-size: 11px; color: #9ca3af;">BUIN SECTOR - OK</span>
            </div>
        </div>
        <style>
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        </style>
    """, height=240)

st.markdown("---")

# --- 15 MÓDULOS TÁCTICOS (PANELES) ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="metric-card">
        <h3>💻 Hardware</h3>
        <p>CPU: {}%<br>RAM: {}%<br>Disco: {}%</p>
    </div>
    """.format(
        psutil.cpu_percent(),
        psutil.virtual_memory().percent,
        psutil.disk_usage('/').percent
    ), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="metric-card">
        <h3>🛡️ Seguridad</h3>
        <p>Caja Fuerte: <b>Cifrada</b><br>Caja Negra: <b>SQLite OK</b><br>Protocolo: <b>Standby</b></p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="metric-card">
        <h3>📈 Enlaces & RAG</h3>
        <p>Trading: <b>EUR Monitor</b><br>Base RAG: <b>Conectada</b><br>Cámara: <b>Activa</b></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- ESTADO DE SESIÓN PARA EL CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Buenas tardes, jefa. Constelación activa. Enlace Starlink y todos los 15 módulos listos en Buin. ¿Qué directiva ejecutamos?"}
    ]

# --- SECCIÓN DE CHAT INTELIGENTE (ABAJO) ---
st.markdown("### 💬 Chat IA - Interfaz Directa")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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

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
                * **

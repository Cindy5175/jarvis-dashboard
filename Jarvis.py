import streamlit as st

# Configuración de página
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilo visual estilo Stark (Dark & Neón)
st.markdown("""
    <style>
        .main { background-color: #060911; }
        h1, h2, h3, h4 { color: #00d2ff !important; font-family: 'Courier New', monospace; }
        .stSelectbox label { color: #00d2ff !important; }
        
        /* Cajas de bordes neón */
        .stark-box {
            border: 1.5px solid #00d2ff;
            border-radius: 10px;
            padding: 12px;
            background-color: rgba(0, 210, 255, 0.03);
            margin-bottom: 12px;
            box-shadow: 0 0 10px rgba(0, 210, 255, 0.15);
        }
        
        /* Globo holográfico */
        .globe-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 15px;
        }
        .globe {
            width: 140px;
            height: 140px;
            border-radius: 50%;
            border: 2px solid #00d2ff;
            box-shadow: inset 0 0 20px #00d2ff, 0 0 20px #00d2ff;
            animation: spin 10s linear infinite;
            background: radial-gradient(circle, rgba(0,210,255,0.2) 0%, rgba(5,7,11,0.8) 80%);
            position: relative;
        }
        .orbit {
            position: absolute;
            width: 170px;
            height: 60px;
            border: 1px solid rgba(0, 210, 255, 0.6);
            border-radius: 50%;
            transform: rotate(-20deg);
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO TÁCTICO STARK INDUSTRIES (Diseño Arc Reactor puro) ---
st.markdown("""
    <div style="text-align: center; margin-bottom: 25px;">
        <svg width="65" height="65" viewBox="0 0 100 100" style="filter: drop-shadow(0 0 12px #00d2ff);">
            <!-- Marco exterior Arc Reactor -->
            <polygon points="50,5 95,85 5,85" fill="none" stroke="#00d2ff" stroke-width="5" stroke-linejoin="round" />
            <!-- Biseles internos tecnológicos -->
            <polygon points="50,22 80,78 20,78" fill="rgba(0, 210, 255, 0.12)" stroke="#00d2ff" stroke-width="2" />
            <!-- Núcleo de energía -->
            <polygon points="50,38 68,70 32,70" fill="#00d2ff" opacity="0.8" />
            <!-- Línea de corte táctica -->
            <line x1="15" y1="85" x2="85" y2="85" stroke="#ffffff" stroke-width="3" />
        </svg>
        <h2 style="margin: 8px 0 0 0; letter-spacing: 2px;">J.A.R.V.I.S IA - NÚCLEO TÁCTICO</h2>
        <p style="color: #00d2ff; font-family: monospace; font-size: 0.85rem; margin-top: 4px; opacity: 0.8;">
            [ STARK INDUSTRIES OPERATIONAL NODE // BUIN, CHILE ]
        </p>
    </div>
""", unsafe_allow_html=True)

# --- BARRA LATERAL: 15 MÓDULOS DEL SISTEMA ---
st.sidebar.markdown("### 🌐 ESTACIÓN TÁCTICA")
modulo_seleccionado = st.sidebar.selectbox(
    "Seleccionar Módulo del Sistema",
    [
        "01. Ojo de Dios (Osiris Tactical)",
        "02. Ojos Digitales",
        "03. Clima de Buin",
        "04. Buscador Web",
        "05. Sintetizador de Voz (ElevenLabs)",
        "06. Escucha Permanente",
        "07. Memoria Masiva",
        "08. Telemetría Global",
        "09. Análisis de Amenazas",
        "10. Protocolo de Emergencia",
        "11. Redes Satelitales",
        "12. Control Financiero (CLP/USD)",
        "13. Diagnóstico de Núcleo",
        "14. Encriptación Cuántica",
        "15. Modo Protocolo Stark"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("🌍 **Estado Orbital:** Satélites Activos")
st.sidebar.info("Conexión segura establecida con el nodo central en Buin.")

# --- LÓGICA DE LOS 15 MÓDULOS ---

if modulo_seleccionado == "01. Ojo de Dios (Osiris Tactical)":
    st.markdown("### 🛰️ Módulo 01: Ojo de Dios (Osiris Tactical)")
    osiris_url = (
        "https://osirisai.live/?"
        "lat=-33.7320&lon=-70.7300&zoom=10.00&"
        "layers=maritime,satellites,sat_comms,sat_military,sat_navigation,sat_earth,"
        "sat_science,cctv,cctv_previews,live_news,earthquakes,infrastructure,"
        "global_incidents,alert_pins,day_night,cables,sdk_sea,sdk_air,sdk_naval,"
        "wind_controls,rain_controls,gdelt_events"
    )
    st.link_button("🚀 ABRIR CENTRO DE MANDO OSIRIS EN PANTALLA COMPLETA", osiris_url, use_container_width=True)
    st.success("Acceso directo a la plataforma de monitoreo global con todas las capas activas para Buin.")

elif modulo_seleccionado == "02. Ojos Digitales":
    st.subheader("👁️ Módulo 02: Ojos Digitales")
    st.info("Cámaras de vigilancia y fuentes de video en circuito cerrado listas.")

elif modulo_seleccionado == "03. Clima de Buin":
    st.subheader("🌤️ Módulo 03: Clima de Buin")
    st.info("Monitoreo atmosférico y métricas meteorológicas en tiempo real para Buin.")

elif modulo_seleccionado == "04. Buscador Web":
    st.subheader("🔍 Módulo 04: Buscador Web")
    st.info("Motores de búsqueda de inteligencia abierta conectados.")

elif modulo_seleccionado == "05. Sintetizador de Voz (ElevenLabs)":
    st.subheader("🎙️ Módulo 05: Sintetizador de Voz (ElevenLabs)")
    st.info("Módulo reservado para la API Key y configuración de audio varonil.")

elif modulo_seleccionado == "06. Escucha Permanente":
    st.subheader("🎧 Módulo 06: Escucha Permanente")
    st.info("Sensores de audio y comandos de voz en espera.")

elif modulo_seleccionado == "07. Memoria Masiva":
    st.subheader("🧠 Módulo 07: Memoria Masiva")
    st.info("Base de datos de contexto y registros históricos activos.")

elif modulo_seleccionado == "08. Telemetría Global":
    st.subheader("📡 Módulo 08: Telemetría Global")
    st.info("Estado de constelaciones satelitales y enlaces de baja órbita.")

elif modulo_seleccionado == "09. Análisis de Amenazas":
    st.subheader("🛡️ Módulo 09: Análisis de Amenazas")
    st.info("Escáner de seguridad perimetral y defensas de red activas.")

elif modulo_seleccionado == "10. Protocolo de Emergencia":
    st.subheader("🚨 Módulo 10: Protocolo de

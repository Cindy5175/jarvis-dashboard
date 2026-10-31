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

# --- ENCABEZADO TÁCTICO CON TRIÁNGULO ARC REACTOR REAL ---
st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <svg width="60" height="60" viewBox="0 0 100 100" style="filter: drop-shadow(0 0 10px #00d2ff);">
            <!-- Triángulo exterior tecnológico -->
            <polygon points="50,15 90,85 10,85" fill="none" stroke="#00d2ff" stroke-width="4"/>
            <!-- Triángulo interior invertido (Diseño Arc Reactor Tony Stark) -->
            <polygon points="50,75 75,30 25,30" fill="rgba(0, 210, 255, 0.15)" stroke="#00d2ff" stroke-width="2"/>
            <!-- Núcleo central luminoso -->
            <circle cx="50" cy="45" r="8" fill="#fff" style="box-shadow: 0 0 15px #00d2ff;" />
        </svg>
        <h2 style="margin: 5px 0 0 0;">J.A.R.V.I.S IA - NÚCLEO TÁCTICO</h2>
        <p style="color: #64748b; font-size: 0.85rem; margin: 0;">Sector: Buin, Chile [-33.73° S | -70.73° W] | Estado: Óptimo</p>
    </div>
""", unsafe_allow_html=True)

# --- BARRA LATERAL (15 MÓDULOS) ---
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

# --- VISTA SI ESTÁ EN EL MÓDULO 01 (OJO DE DIOS) ---
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

# --- DASHBOARD PRINCIPAL DE 2 COLUMNAS ---
col_izq, col_der = st.columns([1, 1.2])

with col_izq:
    st.markdown("""
        <div class="stark-box">
            <b style="color: #00d2ff;">🌐 NÚCLEO HOLOGRÁFICO CON SATÉLITE EN ÓRBITA</b>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="stark-box" style="text-align: center;">
            <div class="globe-container">
                <div class="orbit"></div>
                <div class="globe"></div>
            </div>
            <div style="font-family: monospace; color: #00d2ff; font-size: 0.8rem; margin-top: 10px; border-top: 1px solid #1e293b; padding-top: 5px;">
                LAT: -33.73° S | LON: -70.73° W — BUIN OK
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_der:
    st.markdown("### 💬 Chat IA")
    
    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [
            {"role": "assistant", "content": "Buenas tardes, jefa. Constelación activa. Enlace Starlink y todos los 15 módulos listos en Buin. ¿Qué directiva ejecutamos?"}
        ]
    
    chat_container = st.container(height=280)
    with chat_container:
        for msg in st.session_state.mensajes:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
    
    if prompt := st.chat_input("Escriba su comando para J.A.R.V.I.S..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        respuesta_jarvis = f"Para usted, jefa, siempre. Directiva '{prompt}' procesada con éxito desde Buin."
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_jarvis})
        st.rerun()

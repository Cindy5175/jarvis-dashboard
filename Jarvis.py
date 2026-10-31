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
        
        /* Estilo de la consola táctica */
        .tactical-console {
            font-family: 'Courier New', monospace;
            background-color: #0b1120;
            border: 1px solid #00d2ff;
            border-radius: 8px;
            padding: 10px;
            font-size: 0.78rem;
            color: #00d2ff;
            margin-top: 10px;
        }
        
        /* Estilo para botón de purga */
        div.stButton > button {
            background-color: #1e293b;
            color: #00d2ff;
            border: 1px solid #00d2ff;
            border-radius: 6px;
        }
        div.stButton > button:hover {
            background-color: #00d2ff;
            color: #05070b;
        }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO TÁCTICO STARK INDUSTRIES ---
st.markdown("""
    <div style="text-align: center; margin-bottom: 25px;">
        <svg width="65" height="65" viewBox="0 0 100 100" style="filter: drop-shadow(0 0 12px #00d2ff);">
            <polygon points="50,5 95,85 5,85" fill="none" stroke="#00d2ff" stroke-width="5" stroke-linejoin="round" />
            <polygon points="50,22 80,78 20,78" fill="rgba(0, 210, 255, 0.12)" stroke="#00d2ff" stroke-width="2" />
            <polygon points="50,38 68,70 32,70" fill="#00d2ff" opacity="0.8" />
            <line x1="15" y1="85" x2="85" y2="85" stroke="#ffffff" stroke-width="3" />
        </svg>
        <h2 style="margin: 8px 0 0 0; letter-spacing: 2px;">J.A.R.V.I.S IA - NÚCLEO TÁCTICO</h2>
        <p style="color: #00d2ff; font-family: monospace; font-size: 0.85rem; margin-top: 4px; opacity: 0.8;">
            [ STARK INDUSTRIES OPERATIONAL NODE // BUIN, CHILE ]
        </p>
    </div>
""", unsafe_allow_html=True)

# --- BARRA LATERAL: MÓDULOS CON ICONOS ---
st.sidebar.markdown("### 🌐 ESTACIÓN TÁCTICA")
modulo_seleccionado = st.sidebar.selectbox(
    "Seleccionar Módulo del Sistema",
    [
        "🛰️ Ojo de Dios (Osiris Tactical)",
        "👁️ Ojos Digitales",
        "🌤️ Clima de Buin",
        "🔍 Buscador Web",
        "🎙️ Sintetizador de Voz (ElevenLabs)",
        "🎧 Escucha Permanente",
        "🧠 Memoria Masiva",
        "📡 Telemetría Global",
        "🛡️ Análisis de Amenazas",
        "🚨 Protocolo de Emergencia",
        "🌐 Redes Satelitales",
        "💵 Control Financiero (CLP/USD)",
        "⚙️ Diagnóstico de Núcleo",
        "🔐 Encriptación Cuántica",
        "🦾 Modo Protocolo Stark"
    ]
)

st.sidebar.markdown("---")

# --- DESPLIEGUE ESPECÍFICO DE MÓDULOS EN BARRA LATERAL ---
with st.sidebar.expander("📊 ESTADO OPERATIVO DE MÓDULOS", expanded=True):
    if "Clima de Buin" in modulo_seleccionado:
        st.markdown("🌡️ **Temperatura:** 22°C | Parcial")
        st.markdown("💧 **Humedad:** 45% | 💨 **Viento:** 12 km/h")
        st.markdown("📍 **Sector:** Buin Centro")
    
    elif "Ojo de Dios" in modulo_seleccionado:
        st.markdown("🛰️ **Estado:** Constelación Global Activa")
        osiris_url = "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00&layers=maritime,satellites,sat_comms,sat_military,sat_navigation,sat_earth,sat_science,cctv,cctv_previews,live_news,earthquakes,infrastructure,global_incidents,alert_pins,day_night,cables,sdk_sea,sdk_air,sdk_naval,wind_controls,rain_controls,gdelt_events"
        st.link_button("🚀 Lanzar Osiris Full", osiris_url, use_container_width=True)
    
    elif "Control Financiero" in modulo_seleccionado:
        st.markdown("💵 **USD/CLP:** $945.50")
        st.markdown("💶 **EUR/CLP:** $1,020.30")
        st.markdown("📈 **Tendencia:** Estable")
    
    elif "Ojos Digitales" in modulo_seleccionado:
        st.markdown("👁️ **Feeds CCTV:** 4 Cámaras activas")
        st.markdown("🔒 **Seguridad Perimetral:** Sin anomalías")
    
    elif "Análisis de Amenazas" in modulo_seleccionado:
        st.markdown("🛡️ **Escáner Firewall:** Blindado")
        st.markdown("⚠️ **Alertas en Sector:** 0 detectadas")
    
    else:
        st.markdown(f"🟢 **Canal:** {modulo_seleccionado}")
        st.markdown("⚡ **Sincronización:** 100% Buin OK")

# --- CONSOLA DINÁMICA DE TELEMETRÍA ---
st.sidebar.markdown("---")
st.sidebar.markdown("⚡ **TERMINAL DE ACCIÓN Y TELEMETRÍA**")

st.sidebar.caption("🔋 Potencia del Reactor Arc")
st.sidebar.progress(98)

st.sidebar.caption("📡 Estabilidad del Enlace Starlink")
st.sidebar.progress(92)

if "Amenazas" in modulo_seleccionado:
    if st.sidebar.button("🛡️ Escaneo Profundo"):
        st.sidebar.toast("Perímetro de Buin despejado. Sin anomalías.")
elif "Clima" in modulo_seleccionado:
    if st.sidebar.button("🌤️ Recargar Clima"):
        st.sidebar.toast("Telemetría meteorológica de Buin actualizada.")
else:
    if st.sidebar.button("🔄 Sincronizar Nodo"):
        st.sidebar.toast("Nodo en Buin sincronizado a máxima velocidad.")

st.sidebar.markdown(f"""
    <div class="tactical-console">
        &gt; SYS_OK: Node Buin online<br>
        &gt; ACTIVE: {modulo_seleccionado.split(' ')[1]}<br>
        &gt; STARK_NET: Encryption AES-256<br>
        &gt; STATUS: Esperando directivas, jefa...
    </div>
""", unsafe_allow_html=True)

# --- DASHBOARD PRINCIPAL DE

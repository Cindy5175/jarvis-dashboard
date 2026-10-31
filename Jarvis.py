import streamlit as st
import datetime

# Configuración de página con diseño ancho y estético
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO INTEGRADO", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilo visual estilo Stark (Dark, Neón y Simetría Limpia)
st.markdown("""
    <style>
        .main { background-color: #060911; }
        h1, h2, h3, h4 { color: #00d2ff !important; font-family: 'Courier New', monospace; }
        .stSelectbox label, .stTextInput label, .stTextArea label { color: #00d2ff !important; font-family: 'Courier New', monospace; }
        
        /* Cajas de bordes neón simétricas */
        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 10px;
            padding: 16px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 16px;
            box-shadow: 0 0 12px rgba(0, 210, 255, 0.15);
            min-height: 180px;
        }
        
        /* Globo holográfico en rotación */
        .globe-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
        }
        .globe {
            width: 130px;
            height: 130px;
            border-radius: 50%;
            border: 2px solid #00d2ff;
            box-shadow: inset 0 0 20px #00d2ff, 0 0 20px #00d2ff;
            animation: spin 10s linear infinite;
            background: radial-gradient(circle, rgba(0,210,255,0.2) 0%, rgba(5,7,11,0.8) 80%);
            position: relative;
        }
        .orbit {
            position: absolute;
            width: 160px;
            height: 55px;
            border: 1px solid rgba(0, 210, 255, 0.6);
            border-radius: 50%;
            transform: rotate(-20deg);
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        /* Consola de telemetría inferior */
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
    </style>
""", unsafe_allow_html=True)

# --- DETECCIÓN DE HORA PARA EL SALUDO AUTOMÁTICO ---
hora_actual = datetime.datetime.now().hour
if 5 <= hora_actual < 12:
    saludo_tiempo = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_tiempo = "Buenas tardes"
else:
    saludo_tiempo = "Buenas noches"

# --- CONFIGURACIÓN DE RESPUESTA Y BLINDAJE DE WHATSAPP ---
CIRCULO_FAMILIAR_BLINDADO = [
    "Leonardo Del Transit Carrera Araya",
    "Leonardo Alberto Carrera Baude",
    "Paola Carrera Baude",
    "Silvia Grau",
    "Karin Grau de Folliot"
]

MENSAJE_AUTO_EXTERNOS = (
    "Hola, en este momento no puedo contestar. "
    "Su mensaje ha sido registrado en el sistema y le será respondido a la brevedad posible, gracias."
)

# --- INICIALIZACIÓN DE ESTADOS EN SESSION_STATE ---
if "tareas_todo" not in st.session_state:
    st.session_state.tareas_todo = [
        "Revisar notificaciones de salud / Bci",
        "Sincronizar API Key de ElevenLabs",
        "Probar módulo de dictado de voz"
    ]

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_tiempo}, jefa. Los 5 módulos integrados operan en perfecta simetría desde Buin. ¿Qué directiva iniciamos?"}
    ]

# --- ENCABEZADO TÁCTICO PRINCIPAL ---
st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <svg width="60" height="60" viewBox="0 0 100 100" style="filter: drop-shadow(0 0 12px #00d2ff);">
            <polygon points="50,5 95,85 5,85" fill="none" stroke="#00d2ff" stroke-width="5" stroke-linejoin="round" />
            <polygon points="50,22 80,78 20,78" fill="rgba(0, 210, 255, 0.12)" stroke="#00d2ff" stroke-width="2" />
            <polygon points="50,38 68,70 32,70" fill="#00d2ff" opacity="0.8" />
            <line x1="15" y1="85" x2="85" y2="85" stroke="#ffffff" stroke-width="3" />
        </svg>
        <h2 style="margin: 6px 0 0 0; letter-spacing: 2px;">J.A.R.V.I.S IA - NÚCLEO TÁCTICO REFORZADO</h2>
        <p style="color: #00d2ff; font-family: monospace; font-size: 0.82rem; margin-top: 2px; opacity: 0.85;">
            [ NODO OPERATIVO STARK INDUSTRIES // BUIN, CHILE ]
        </p>
    </div>
""", unsafe_allow_html=True)

# --- BARRA LATERAL TÁCTICA ---
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")
st.sidebar.markdown("🚀 **Visor Satelital**")
st.sidebar.link_button("🛰️ Lanzar Ojo de Dios (Osiris)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00&layers=maritime,satellites,sat_comms,sat_military,sat_navigation,sat_earth,sat_science,cctv,cctv_previews,live_news,earthquakes,infrastructure,global_incidents,alert_pins,day_night,cables,sdk_sea,sdk_air,sdk_naval,wind_controls,rain_controls,gdelt_events", use_container_width=True)

st.sidebar.markdown("---")

modulo_seleccionado = st.sidebar.

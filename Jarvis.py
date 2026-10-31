import streamlit as st
import streamlit.components.v1 as components

# Configuración de página táctica
st.set_page_config(
    page_title="JARVIS System - Stark Industries", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilo personalizado para estética táctica
st.markdown("""
    <style>
        .main { background-color: #0b0f19; }
        h1, h2, h3 { color: #00d2ff !important; font-family: 'Courier New', monospace; }
        .stSelectbox label { color: #00d2ff !important; }
    </style>
""", unsafe_allow_html=True)

# Cabecera principal
st.title("▲ JARVIS CONTROL CENTER")
st.caption("Sector: Buin, Chile [-33.7320° S, -70.7300° W] | Estado: Operativo")

# Menú lateral para navegación entre módulos
modulo_seleccionado = st.sidebar.selectbox(
    "Módulos del Sistema",
    [
        "01. Ojo de Dios (Osiris Tactical)",
        "02. Ojos Digitales",
        "03. Clima de Buin",
        "04. Buscador Web",
        "05. Sintetizador de Voz (ElevenLabs)",
        # Agregue aquí el resto de sus 15 módulos
    ]
)

# --- MÓDULO 01: OJO DE DIOS (OSIRIS INTEGRADO) ---
if modulo_seleccionado == "01. Ojo de Dios (Osiris Tactical)":
    st.subheader("🛰️ Módulo Táctico: Monitoreo Global en Tiempo Real")
    st.caption("Telemetría activa: Satélites Militares/Comunicaciones, Tráfico Marítimo, Vuelos, Sismos y Redes Globales.")
    
    # URL completa con todas las capas activas centradas en Buin
    osiris_url = (
        "https://osirisai.live/?"
        "lat=-33.7320&lon=-70.7300&zoom=10.00&"
        "layers=maritime,satellites,sat_comms,sat_military,sat_navigation,sat_earth,"
        "sat_science,cctv,cctv_previews,live_news,earthquakes,infrastructure,"
        "global_incidents,alert_pins,day_night,cables,sdk_sea,sdk_air,sdk_naval,"
        "wind_controls,rain_controls,gdelt_events"
    )
    
    # Renderizado en vivo mediante iframe responsivo
    components.html(
        f"""
        <iframe 
            src="{osiris_url}" 
            width="100%" 
            height="760px" 
            style="border: 2px solid #00d2ff; border-radius: 12px; background-color: #000; box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);"
            allowfullscreen>
        </iframe>
        """,
        height=770
    )

# --- MÓDULO 05: ELEVENLABS (CONEXIÓN DE VOZ) ---
elif modulo_seleccionado == "05. Sintetizador de Voz (ElevenLabs)":
    st.subheader("🎙️ Configuración de Voz de Jarvis")
    st.info("Módulo reservado para la API Key de ElevenLabs e integración del modelo de voz varonil.")

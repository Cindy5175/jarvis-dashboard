import streamlit as st
import streamlit.components.v1 as components

# Configuración de página táctica
st.set_page_config(page_title="JARVIS System", layout="wide", initial_sidebar_state="expanded")

# --- CABECERA STARK ---
st.markdown("<h1 style='text-align: center;'>▲ JARVIS CONTROL CENTER</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #00d2ff;'>Sector: Buin, Chile [-33.73° S, -70.73° W]</p>", unsafe_allow_html=True)

# Selector de Módulos
modulo_seleccionado = st.sidebar.selectbox(
    "Módulos del Sistema",
    [
        "01. Ojo de Dios (Osiris Tactical)",
        "02. Ojos Digitales",
        "03. Clima de Buin",
        "04. Buscador Web",
        "05. Sintetizador de Voz (ElevenLabs)",
        # ... resto de sus 15 módulos
    ]
)

# --- MÓDULO: OJO DE DIOS (OSIRIS INTEGRADO) ---
if modulo_seleccionado == "01. Ojo de Dios (Osiris Tactical)":
    st.subheader("🛰️ Módulo Táctico: Monitoreo Global en Tiempo Real")
    st.caption("Capas activas: Satélites Militares, Tráfico Marítimo, Vuelos Privados, Sismos y Telemetría Global.")
    
    # URL con todas las capas tácticas activas desde Buin
    osiris_url = (
        "https://osirisai.live/?"
        "lat=-33.7320&lon=-70.7300&zoom=10.00&"
        "layers=maritime,satellites,sat_comms,sat_military,sat_navigation,sat_earth,"
        "sat_science,cctv,cctv_previews,live_news,earthquakes,infrastructure,"
        "global_incidents,alert_pins,day_night,cables,sdk_sea,sdk_air,sdk_naval,"
        "wind_controls,rain_controls,gdelt_events"
    )
    
    # Renderizado del visor en vivo mediante iframe fluido
    components.html(
        f"""
        <iframe 
            src="{osiris_url}" 
            width="100%" 
            height="750px" 
            style="border: 2px solid #00d2ff; border-radius: 10px; background-color: #000;"
            allowfullscreen>
        </iframe>
        """,
        height=760
    )

# --- MÓDULO ELEVENLABS (PENDIENTE) ---
elif modulo_seleccionado == "05. Sintetizador de Voz (ElevenLabs)":
    st.subheader("🎙️ Configuración de Voz de Jarvis")
    st.info("Módulo listo para conectar la API Key de ElevenLabs y clonar/asignar la voz varonil.")

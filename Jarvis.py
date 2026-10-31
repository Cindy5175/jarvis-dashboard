import streamlit as st

# Configuración de página con diseño extendido
st.set_page_config(
    page_title="JARVIS Control Center", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilo visual estilo Stark Industries (Oscuro y Neón)
st.markdown("""
    <style>
        .main { background-color: #05070b; }
        h1, h2, h3 { color: #00d2ff !important; font-family: 'Courier New', monospace; }
        .stSelectbox label { color: #00d2ff !important; font-weight: bold; }
        div.stButton > button {
            background: linear-gradient(45deg, #0072ff, #00d2ff);
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
        }
        div.stButton > button:hover {
            background: linear-gradient(45deg, #00d2ff, #0072ff);
            box-shadow: 0 0 25px rgba(0, 210, 255, 0.8);
        }
    </style>
""", unsafe_allow_html=True)

# --- CABECERA PRINCIPAL ---
st.title("▲ JARVIS CONTROL CENTER")
st.caption("Sector: Buin, Chile [-33.7320° S, -70.7300° W] | Estado del Sistema: Óptimo")

# --- BARRA LATERAL: 15 MÓDULOS Y GLOBO TÁCTICO ---
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

# Indicador visual del globo giratorio en la barra lateral
st.sidebar.markdown("---")
st.sidebar.markdown("🌍 **Estado Orbital:** Satélites Activos en Órbita Baja")
st.sidebar.info("Conexión segura establecida con el nodo central en Buin.")

# --- LÓGICA DE MÓDULOS ---

if modulo_seleccionado == "01. Ojo de Dios (Osiris Tactical)":
    st.subheader("🛰️ Módulo 01: Ojo de Dios (Centro de Monitoreo Global)")
    st.write("El servidor externo de Osiris requiere apertura directa para evitar bloqueos de seguridad en contenedores internos.")
    
    # URL definitiva con todas las capas configuradas y centrada en Buin
    osiris_url = (
        "https://osirisai.live/?"
        "lat=-33.7320&lon=-70.7300&zoom=10.00&"
        "layers=maritime,satellites,sat_comms,sat_military,sat_navigation,sat_earth,"
        "sat_science,cctv,cctv_previews,live_news,earthquakes,infrastructure,"
        "global_incidents,alert_pins,day_night,cables,sdk_sea,sdk_air,sdk_naval,"
        "wind_controls,rain_controls,gdelt_events"
    )
    
    # Botón de lanzamiento táctico de alta visibilidad
    st.link_button("🚀 LANZAR CENTRO DE MANDO OSIRIS (Pantalla Completa)", osiris_url, use_container_width=True)
    st.success("Haga clic en el botón superior para desplegar el mapa global con todas las capas de telemetría militar, marítima y sísmica en una nueva pestaña.")

elif modulo_seleccionado == "02. Ojos Digitales":
    st.subheader("👁️ Módulo 02: Ojos Digitales")
    st.info("Cámaras de vigilancia y feeds de video activos.")

elif modulo_seleccionado == "03. Clima de Buin":
    st.subheader("🌤️ Módulo 03: Clima de Buin")
    st.info("Monitoreo atmosférico y métricas meteorológicas locales.")

elif modulo_seleccionado == "05. Sintetizador de Voz (ElevenLabs)":
    st.subheader("🎙️ Módulo 05: Sintetizador de Voz")
    st.info("Configuración de credenciales API para la voz varonil de Jarvis.")

else:
    st.subheader(f"⚙️ {modulo_seleccionado}")
    st.info("Módulo operativo en línea y listo para recibir comandos.")

# --- CAJA DE CHAT 💬 CON JARVIS ---
st.divider()
st.subheader("💬 Interfaz de Conversación Táctica")

# Historial de chat simple en Streamlit
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": "Para usted, jefa, siempre. ¿Qué comandos ejecutamos hoy desde el búnker?"}]

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Escriba una orden para Jarvis..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    respuesta_jarvis = f"Para usted, jefa, siempre. Analizando su solicitud sobre '{prompt}' con los sistemas al 100%."
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_jarvis})
    with st.chat_message("assistant"):
        st.markdown(respuesta_jarvis)

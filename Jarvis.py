import streamlit as st

# Configuración de página con diseño extendido
st.set_page_config(
    page_title="J.A.R.V.I.S IA - Stark Industries", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilo visual de alta tecnología (Arc Reactor & Neón)
st.markdown("""
    <style>
        .main { background-color: #05070b; }
        h1, h2, h3 { color: #00d2ff !important; font-family: 'Courier New', monospace; }
        .stSelectbox label { color: #00d2ff !important; font-weight: bold; }
        
        /* Botones de acción táctica */
        div.stButton > button {
            background: linear-gradient(45deg, #0072ff, #00d2ff);
            color: white;
            font-weight: bold;
            border: none;
            border-radius: 8px;
            padding: 0.6rem 1rem;
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
            width: 100%;
        }
        div.stButton > button:hover {
            background: linear-gradient(45deg, #00d2ff, #0072ff);
            box-shadow: 0 0 25px rgba(0, 210, 255, 0.8);
        }
        
        /* Contenedor estilo panel de chat */
        .chat-container {
            background-color: #0f1626;
            border: 1px solid #1e293b;
            border-radius: 12px;
            padding: 15px;
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# --- ENCABEZADO TÁCTICO CON LOGO TRIÁNGULO ARC REACTOR ---
col_logo, col_titulo = st.columns([1, 6])

with col_logo:
    # Representación visual del Arc Reactor triangular
    st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; height: 70px;">
            <svg width="60" height="60" viewBox="0 0 100 100">
              <polygon points="50,10 90,90 10,90" fill="none" stroke="#00d2ff" stroke-width="6" style="filter: drop-shadow(0 0 8px #00d2ff);" />
              <polygon points="50,30 75,80 25,80" fill="rgba(0, 210, 255, 0.2)" stroke="#00d2ff" stroke-width="2" />
              <circle cx="50" cy="60" r="10" fill="#00d2ff" style="filter: drop-shadow(0 id=0 0 10px #fff);" />
            </svg>
        </div>
    """, unsafe_allow_html=True)

with col_titulo:
    st.markdown("<h1 style='margin: 0; padding-top: 10px;'>J.A.R.V.I.S IA</h1>", unsafe_allow_html=True)
    st.caption("Sector: Buin, Chile [-33.7320° S, -70.7300° W] | Estado del Sistema: Óptimo")

st.divider()

# --- BARRA LATERAL: 15 MÓDULOS Y ESTACIÓN TÁCTICA ---
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

# --- LÓGICA DE MÓDULOS ---

if modulo_seleccionado == "01. Ojo de Dios (Osiris Tactical)":
    st.subheader("🛰️ Módulo 01: Ojo de Dios (Centro de Monitoreo Global)")
    st.write("Acceso directo a la plataforma táctica global con todas las capas de telemetría activas.")
    
    osiris_url = (
        "https://osirisai.live/?"
        "lat=-33.7320&lon=-70.7300&zoom=10.00&"
        "layers=maritime,satellites,sat_comms,sat_military,sat_navigation,sat_earth,"
        "sat_science,cctv,cctv_previews,live_news,earthquakes,infrastructure,"
        "global_incidents,alert_pins,day_night,cables,sdk_sea,sdk_air,sdk_naval,"
        "wind_controls,rain_controls,gdelt_events"
    )
    
    st.link_button("🚀 LANZAR CENTRO DE MANDO OSIRIS (Pantalla Completa)", osiris_url)
    st.success("Haga clic para desplegar el mapa global en una nueva pestaña sin restricciones de seguridad.")

elif modulo_seleccionado == "02. Ojos Digitales":
    st.subheader("👁️ Módulo 02: Ojos Digitales")
    st.info("Cámaras de vigilancia y feeds en línea.")

elif modulo_seleccionado == "03. Clima de Buin":
    st.subheader("🌤️ Módulo 03: Clima de Buin")
    st.info("Monitoreo atmosférico local activo.")

elif modulo_seleccionado == "05. Sintetizador de Voz (ElevenLabs)":
    st.subheader("🎙️ Módulo 05: Sintetizador de Voz")
    st.info("Configuración de credenciales API para la voz varonil.")

else:
    st.subheader(f"⚙️ {modulo_seleccionado}")
    st.info("Módulo operativo en línea.")

# --- CAJA DE CHAT TÁCTICA ---
st.divider()
st.markdown("### 💬 Chat IA")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "Para usted, jefa, siempre. Sistema de comunicaciones restablecido en Buin."}
    ]

# Contenedor visual del chat
with st.container():
    for msg in st.session_state.mensajes:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# Entrada de comandos optimizada con botones de control
with st.form(key="form_chat", clear_on_submit=True):
    user_input = st.text_input("Escriba su comando para J.A.R.V.I.S...", placeholder="Escriba aquí...")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        submit_chat = st.form_submit_button("⚡ Enviar Directiva")
    with col_btn2:
        purgar_chat = st.form_submit_button("🗑️ Purgar Chat")

if purgar_chat:
    st.session_state.mensajes = [{"role": "assistant", "content": "Memoria de chat purgada, jefa. Sistema de comunicaciones restablecido en Buin."}]
    st.rerun()

if submit_chat and user_input:
    st.session_state.mensajes.append({"role": "user", "content": user_input})
    respuesta_jarvis = f"Procesado con órbita Starlink en Buin, jefa. Directiva '{user_input}' comprendida y ejecutada."
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_jarvis})
    st.rerun()

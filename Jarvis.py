import streamlit as st
import datetime

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
            [ NODO OPERATIVO STARK INDUSTRIES // BUIN, CHILE ]
        </p>
    </div>
""", unsafe_allow_html=True)

# --- BARRA LATERAL: MÓDULOS CON ICONOS Y PILARES ---
st.sidebar.markdown("### 🌐 ESTACIÓN TÁCTICA")

st.sidebar.markdown("🚀 **Visor Satelital Activo**")
st.sidebar.link_button("🛰️ Lanzar Ojo de Dios (Osiris)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00&layers=maritime,satellites,sat_comms,sat_military,sat_navigation,sat_earth,sat_science,cctv,cctv_previews,live_news,earthquakes,infrastructure,global_incidents,alert_pins,day_night,cables,sdk_sea,sdk_air,sdk_naval,wind_controls,rain_controls,gdelt_events", use_container_width=True)
st.sidebar.markdown("---")

modulo_seleccionado = st.sidebar.selectbox(
    "Seleccionar Módulo del Sistema",
    [
        "🛡️ Blindaje WhatsApp",
        "🧠 Memoria Masiva",
        "🔍 Buscador Web",
        "📡 Telemetría Global",
        "🎙️ Sintetizador de Voz",
        "🌤️ Clima de Buin",
        "👁️ Ojos Digitales",
        "💵 Control Financiero",
        "⚙️ Diagnóstico de Núcleo"
    ]
)

st.sidebar.markdown("---")

# --- DESPLIEGUE DE LOS 4 PILARES Y MÓDULOS EN BARRA LATERAL ---
with st.sidebar.expander("📊 ESTADO OPERATIVO DE MÓDULOS", expanded=True):
    if "Blindaje WhatsApp" in modulo_seleccionado:
        st.markdown("🛡️ **Protocolo de Inmunidad:** Activo")
        st.markdown(f"👥 **Protegidos:** {len(CIRCULO_FAMILIAR_BLINDADO)} familiares")
        st.markdown("💬 **Respuesta Externa:** Actualizada con éxito")

    elif "Memoria Masiva" in modulo_seleccionado:
        st.markdown("🧠 **Base Vectorial:** Activa")
        st.markdown("📁 **Contexto Local:** Manuales y Logs OK")

    elif "Buscador Web" in modulo_seleccionado:
        st.markdown("🔍 **Motor de Consulta:** En línea")

    elif "Telemetría Global" in modulo_seleccionado:
        st.markdown("📡 **Red Starlink:** Órbita estable")
        st.markdown("⚡ **Reactor Arc:** 98% Potencia")

    elif "Sintetizador de Voz" in modulo_seleccionado:
        st.markdown("🎙️ **ElevenLabs:** Configuración de audio")
        api_key = st.secrets.get("ELEVENLABS_API_KEY", "sk_0ad6fd3611d02842c77732aa608a1b1b238a6ae8f900d5cf")
        voice_id = st.text_input("Voice ID:", value="21m00Tcm4TlvDq8ikWAM")
        texto_voz = st.text_area("Texto a sintetizar:", f"{saludo_tiempo}, jefa. Sistemas de voz en línea en Buin.")
        
        if st.button("🔊 Generar Audio"):
            try:
                from elevenlabs.client import ElevenLabs
                client = ElevenLabs(api_key=api_key)
                audio_stream = client.text_to_speech.convert(
                    text=texto_voz,
                    voice_id=voice_id,
                    model_id="eleven_multilingual_v2"
                )
                audio_bytes = b"".join(audio_stream)
                st.audio(audio_bytes, format="audio/mp3")
                st.success("Audio generado con éxito desde Buin.")
            except Exception as e:
                st.error(f"Error ElevenLabs: {str(e)}")

    elif "Clima de Buin" in modulo_seleccionado:
        st.markdown("🌡️ **Temperatura:** 22°C | Parcial")

    elif "Control Financiero" in modulo_seleccionado:
        st.markdown("💵 **USD/CLP:** $945.50")
    
    else:
        st.markdown(f"🟢 **Canal:** {modulo_seleccionado}")

# --- TERMINAL DE ACCIÓN Y TELEMETRÍA ---
st.sidebar.markdown("---")
st.sidebar.markdown("⚡ **TERMINAL DE ACCIÓN Y TELEMETRÍA**")
st.sidebar.caption("🔋 Potencia del Reactor Arc")
st.sidebar.progress(98)
st.sidebar.caption("📡 Estabilidad del Enlace Starlink")
st.sidebar.progress(92)

st.sidebar.markdown(f"""
    <div class="tactical-console">
        &gt; SISTEMA_OK: Nodo Buin en línea<br>
        &gt; INMUNIDAD_FA: 5 contactos inmunes<br>
        &gt; MENSAJE_EXT: Actualizado con agradecimiento<br>
        &gt; ESTADO: Esperando directivas, jefa...
    </div>
""", unsafe_allow_html=True)

# --- DASHBOARD PRINCIPAL ---
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
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.markdown("### 💬 Chat IA & Protocolos de Mensajería")
    with col_head2:
        if st.button("🗑️ Purgar"):
            st.session_state.mensajes = [
                {"role": "assistant", "content": f"Memoria de chat purgada, jefa. {saludo_tiempo}. Sistema de comunicaciones restablecido en Buin."}
            ]
            st.rerun()

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [
            {"role": "assistant", "content": f"{saludo_tiempo}, jefa. Mensaje automático para externos actualizado con éxito. Los 5 familiares continúan blindados."}
        ]
    
    chat_container = st.container(height=280)
    with chat_container:
        for msg in st.session_state.mensajes:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
    
    if prompt := st.chat_input("Escriba su comando para J.A.R.V.I.S..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        
        prompt_lower = prompt.lower()
        if "hola" in prompt_lower or "buenas" in prompt_lower:
            respuesta_jarvis = f"{saludo_tiempo}, jefa. Sistemas al 100% y listo para servirle."
        elif "despierto" in prompt_lower or "estás ahí" in prompt_lower:
            respuesta_jarvis = "Para usted, señorita, siempre."
        else:
            respuesta_jarvis = f"Para usted, jefa, siempre. Directiva '{prompt}' procesada correctamente."
        
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_jarvis})
        st.rerun()

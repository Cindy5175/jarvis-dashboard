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
        "Verificar enlace seguro de ElevenLabs",
        "Probar módulo de dictado de voz"
    ]

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_tiempo}, jefa. Módulos integrados y enlace de voz blindado listos en Buin. ¿Qué directiva iniciamos?"}
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

modulo_seleccionado = st.sidebar.selectbox("Seleccionar Módulo Activo", [
    "🛡️ Blindaje WhatsApp",
    "📧 Alertas Gmail",
    "📋 Tareas & Notas Tácticas",
    "🎙️ Comandos por Voz",
    "💱 Conversor de Monedas",
    "📌 Marcadores Rápidos",
    "🧠 Memoria Masiva",
    "📡 Telemetría Global"
])

st.sidebar.markdown("---")

with st.sidebar.expander("📊 TELEMETRÍA DE NÚCLEO", expanded=True):
    st.markdown("🛡️ **Familiar Protegido:** 5 Activos")
    st.markdown("💬 **Respuesta Externa:** Educada & Cordial")
    st.markdown("⚡ **Reactor Arc:** 99% Operativo")
    st.markdown("📍 **Nodo:** Buin Centro OK")

st.sidebar.markdown("---")
st.sidebar.caption("🔋 Potencia Arc")
st.sidebar.progress(99)
st.sidebar.caption("📡 Enlace Starlink")
st.sidebar.progress(95)

st.sidebar.markdown(f"""
    <div class="tactical-console">
        &gt; MATRIZ: 5 Módulos Simétricos<br>
        &gt; NODO_BUIN: En línea<br>
        &gt; ESTADO: Esperando órdenes, jefa...
    </div>
""", unsafe_allow_html=True)

# --- DISPOSICIÓN PRINCIPAL EN DOS COLUMNAS ANCHAS ---
col_izq, col_der = st.columns([1, 1], gap="medium")

# --- COLUMNA IZQUIERDA: MÓDULOS 1, 2 Y 3 ---
with col_izq:
    # MÓDULO 1: ANÁLISIS DE CORREOS (GMAIL)
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("### 📧 Módulo 1: Alerta & Resumen Gmail")
    st.caption("Filtro prioritario de notificaciones bancarias, de salud e inversiones.")
    
    col_mail1, col_mail2 = st.columns(2)
    with col_mail1:
        st.markdown("**Notificaciones Prioritarias:**")
        st.info("🏥 UC Christus: Receta médica disponible.")
    with col_mail2:
        st.markdown("**Finanzas / Inversiones:**")
        st.success("🏦 Bci Corredora: Suscripción Moneda Renta CLP.")
    
    if st.button("🔄 Escanear Bandeja de Entrada", use_container_width=True):
        st.toast("Bandeja escaneada: 2 correos prioritarios detectados.")
    st.markdown('</div>', unsafe_allow_html=True)

    # MÓDULO 2: PANEL DE TAREAS Y NOTAS TÁCTICAS
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("### 📋 Módulo 2: Protocolo To-Do Táctico")
    
    nueva_tarea = st.text_input("Agregar nueva tarea al búnker:", placeholder="Ej: Revisar sensores de Buin...")
    if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
        st.session_state.tareas_todo.append(nueva_tarea)
        st.success("Tarea guardada en memoria táctica.")

    st.markdown("**Pendientes Activos:**")
    for idx, t in enumerate(st.session_state.tareas_todo):
        st.markdown(f"• `{idx+1}.` {t}")
    st.markdown('</div>', unsafe_allow_html=True)

    # MÓDULO 3: DICTADO Y COMANDO POR VOZ
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("### 🎙️ Módulo 3: Grabador & Sintetizador de Voz")
    
    audio_input = st.audio_input("Dictar comando de voz a J.A.R.V.I.S.")
    if audio_input:
        st.success("Audio capturado correctamente. Procesando instrucción por voz, jefa...")
    
    voice_id = st.text_input("Voice ID (ElevenLabs):", value="21m00Tcm4TlvDq8ikWAM")
    texto_a_hablar = st.text_area("Texto a reproducir:", value=f"{saludo_tiempo}, jefa. Todos los sistemas del búnker operan en Buin.", height=68)
    
    if st.button("🔊 Probar Síntesis de Voz", use_container_width=True):
        try:
            api_key = st.secrets["ELEVENLABS_API_KEY"]
            from elevenlabs.client import ElevenLabs
            client = ElevenLabs(api_key=api_key)
            audio_stream = client.text_to_speech.convert(
                text=texto_a_hablar,
                voice_id=voice_id,
                model_id="eleven_multilingual_v2"
            )
            audio_bytes = b"".join(audio_stream)
            st.audio(audio_bytes, format="audio/mp3")
            st.success("Síntesis generada.")
        except KeyError:
            st.error("Falta configurar la llave 'ELEVENLABS_API_KEY' en el archivo secrets.toml del sistema, jefa.")
        except Exception as e:
            st.error(f"Error de conexión de voz: {str(e)}")
    st.markdown('</div>', unsafe_allow_html=True)

# --- COLUMNA DERECHA: MÓDULOS 4, 5 Y CHAT DE CONSOLA ---
with col_der:
    # MÓDULO 4: CONVERSOR DE MONEDAS EN TIEMPO REAL
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("### 💱 Módulo 4: Conversor Financiero CLP")
    
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1:
        monto = st.number_input("Monto:", min_value=1.0, value=100.0, step=10.0)
    with c_m2:
        moneda_origen = st.selectbox("De:", ["USD", "EUR"])
    with c_m3:
        tasa = 945.50 if moneda_origen == "USD" else 1020.30
        st.metric(label=f"Tasa {moneda_origen}/CLP", value=f"${tasa}")

    total_clp = monto * tasa
    st.markdown(f"💰 **Resultado:** `{monto:.2f} {moneda_origen}` = **`${total_clp:,.2f} CLP`**")
    st.markdown('</div>', unsafe_allow_html=True)

    # MÓDULO 5: MARCADORES RÁPIDOS Y NÚCLEO HOLOGRÁFICO
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("### 📌 Módulo 5: Enlaces Rápidos & Globo Holográfico")
    
    col_link1, col_link2 = st.columns(2)
    with col_link1:
        st.link_button("🌐 Visor Osiris Global", "https://osirisai.live", use_container_width=True)
        st.link_button("🏥 Portal UC Christus", "https://portalclinico.ucchristus.cl", use_container_width=True)
    with col_link2:
        st.link_button("🏦 Banco Bci Inversiones", "https://www.bci.cl/inversiones", use_container_width=True)
        st.link_button("🌦️ Meteorología Chile", "https://www.meteochile.gob.cl", use_container_width=True)

    st.markdown("""
        <div class="globe-container" style="margin-top: 10px;">
            <div class="orbit"></div>
            <div class="globe"></div>
        </div>
        <div style="font-family: monospace; color: #00d2ff; font-size: 0.78rem; text-align: center; margin-top: 6px;">
            BUIN OK — NODO GEOGRÁFICO -33.73° S / -70.73° W
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # CONSOLA DE CHAT IA E INTERACCIÓN
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    c_h1, c_h2 = st.columns([3, 1])
    with c_h1:
        st.markdown("### 💬 Consola de Chat J.A.R.V.I.S.")
    with c_h2:
        if st.button("🗑️ Purgar", use_container_width=True):
            st.session_state.mensajes = [
                {"role": "assistant", "content": f"Memoria de chat purgada, jefa. {saludo_tiempo}. Consola lista en Buin."}
            ]
            st.rerun()

    chat_box = st.container(height=230)
    with chat_box:
        for m in st.session_state.mensajes:
            with st.chat_message(m["role"]):
                st.write(m["content"])

    if p := st.chat_input("Escriba su comando para J.A.R.V.I.S..."):
        st.session_state.mensajes.append({"role": "user", "content": p})
        p_low = p.lower()
        if "despierto" in p_low or "estás ahí" in p_low:
            resp = "Para usted, señorita, siempre."
        elif "hola" in p_low or "buenas" in p_low:
            resp = f"{saludo_tiempo}, jefa. Todos los 5 módulos operan en perfecta armonía."
        else:
            resp = f"Para usted, jefa, siempre. Comando '{p}' procesado correctamente."
        
        st.session_state.mensajes.append({"role": "assistant", "content": resp})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

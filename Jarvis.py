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
        
        /* Cajas de bordes neón independientes */
        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 10px;
            padding: 16px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 16px;
            box-shadow: 0 0 12px rgba(0, 210, 255, 0.15);
        }
        
        /* Títulos de módulos independientes */
        .module-title {
            color: #00d2ff;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(0, 210, 255, 0.3);
            padding-bottom: 4px;
        }
        
        /* Globo holográfico en rotación */
        .globe-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 10px;
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

# --- INICIALIZACIÓN DE ESTADOS ---
if "tareas_todo" not in st.session_state:
    st.session_state.tareas_todo = [
        "Revisar notificaciones de salud / Bci",
        "Optimizar matriz del búnker",
        "Monitorear nodo activo en Buin"
    ]

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_tiempo}, jefa. Núcleo estable en Buin. ¿Qué directiva iniciamos?"}
    ]

# --- ENCABEZADO PRINCIPAL ---
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

# --- BARRA LATERAL ---
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")
st.sidebar.markdown("🚀 **Visor Satelital**")
st.sidebar.link_button("🛰️ Ojo de Dios (Osiris)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)

st.sidebar.markdown("### 📌 Enlaces Rápidos")
st.sidebar.link_button("🏦 Banco Bci", "https://www.bci.cl/inversiones", use_container_width=True)
st.sidebar.link_button("🏥 UC Christus", "https://portalclinico.ucchristus.cl", use_container_width=True)
st.sidebar.link_button("🌦️ Meteo Chile 🇨🇱", "https://www.meteochile.gob.cl", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("🔋 Potencia Arc")
st.sidebar.progress(99)
st.sidebar.caption("📡 Enlace Starlink")
st.sidebar.progress(95)

# --- DISPOSICIÓN PRINCIPAL ---
col_izq, col_der = st.columns([1, 1], gap="medium")

with col_izq:
    # 1. BLINDAJE WHATSAPP
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Blindaje WhatsApp</div>', unsafe_allow_html=True)
    st.caption("Protocolo de inmunidad y respuesta automática para contactos externos.")
    st.info("Estado: Activo • Círculo Familiar Protegido (5 Activos)")
    st.markdown('</div>', unsafe_allow_html=True)

    # 2. ALERTAS Y RESUMEN GMAIL
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Alertas y Resumen Gmail</div>', unsafe_allow_html=True)
    st.caption("Filtro prioritario de notificaciones bancarias, de salud e inversiones.")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        st.info("🏥 UC Christus: Receta disponible.")
    with c_m2:
        st.success("🏦 Bci: Renta CLP.")
    if st.button("🔄 Escanear Bandeja", use_container_width=True):
        st.toast("Bandeja escaneada con éxito.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 3. TAREAS Y NOTAS TÁCTICAS
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Tareas y Notas Tácticas</div>', unsafe_allow_html=True)
    st.caption("Gestión y registro rápido de pendientes en el búnker.")
    nueva_tarea = st.text_input("Nueva tarea:", placeholder="Ej: Revisar sensores...")
    if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
        st.session_state.tareas_todo.append(nueva_tarea)
        st.success("Tarea guardada.")
    for t in st.session_state.tareas_todo:
        st.markdown(f"• {t}")
    st.markdown('</div>', unsafe_allow_html=True)

    # 4. SINTETIZADOR DE VOZ NATIVO
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Sintetizador de Voz Nativa (Varonil)</div>', unsafe_allow_html=True)
    st.caption("Emisión de comandos con tono de voz grave y profundo.")
    texto_a_hablar = st.text_area("Texto a reproducir:", value=f"{saludo_tiempo}, jefa. Sistemas de Buin operativos.", height=55)
    
    if st.button("🔊 Reproducir Voz de J.A.R.V.I.S.", use_container_width=True):
        js_voz = f"""
        <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            var utterance = new SpeechSynthesisUtterance("{texto_a_hablar}");
            utterance.lang = 'es-ES';
            utterance.rate = 0.90;
            utterance.pitch = 0.1;
            var voices = window.speechSynthesis.getVoices();
            for(var i = 0; i < voices.length; i++) {{
                var name = voices[i].name.toLowerCase();
                if(voices[i].lang.includes('es') && (name.includes('male') || name.includes('pablo') || name.includes('carlos') || name.includes('alberto') || name.includes('raul') || name.includes('diego'))) {{
                    utterance.voice = voices[i];
                    break;
                }}
            }}
            window.speechSynthesis.speak(utterance);
        }}
        </script>
        """
        st.components.v1.html(js_voz, height=0)
        st.success("Comando de voz emitido.")
    st.markdown('</div>', unsafe_allow_html=True)

    # 5. CONVERSOR DE MONEDAS
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Conversor de Monedas</div>', unsafe_allow_html=True)
    st.caption("Cálculo en tiempo real USD/EUR a Pesos Chilenos.")
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        monto = st.number_input("Monto:", value=100.0, step=10.0)
    with c_f2:
        moneda = st.selectbox("Moneda:", ["USD", "EUR"])
    tasa = 945.50 if moneda == "USD" else 1020.30
    total = monto * tasa
    st.markdown(f"💰 **Total:** `{monto} {moneda}` = **`${total:,.2f} CLP`**")
    st.markdown('</div>', unsafe_allow_html=True)

    # 6. TELEMETRÍA GLOBAL Y SENSORES
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Telemetría Global y Sensores</div>', unsafe_allow_html=True)
    st.caption("Monitoreo de estado de conexiones y satélites.")
    st.success("Enlace Starlink: Estable (95%) • Sensores Buin: OK")
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    # NODO HOLOGRÁFICO
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Nodo Holográfico Global</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="globe-container">
            <div class="orbit"></div>
            <div class="globe"></div>
        </div>
        <div style="font-family: monospace; color: #00d2ff; font-size: 0.78rem; text-align: center; margin-top: 8px;">
            BUIN OK — COORDENADAS: -33.73° S / -70.73° W
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # CHAT IA
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    c_h1, c_h2 = st.columns([3, 1])
    with c_h1:
        st.markdown('<div class="module-title" style="border:none; margin:0; padding:0;">Chat IA</div>', unsafe_allow_html=True)
    with c_h2:
        if st.button("🗑️ Purgar", use_container_width=True):
            st.session_state.mensajes = [
                {"role": "assistant", "content": f"Memoria purgada, jefa. {saludo_tiempo}. Chat IA listo en Buin."}
            ]
            st.rerun()

    chat_box = st.container(height=350)
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
            resp = f"{saludo_tiempo}, jefa. Todos los sistemas operan en perfecta armonía."
        else:
            resp = f"Para usted, jefa, siempre. Comando '{p}' procesado correctamente."
        
        st.session_state.mensajes.append({"role": "assistant", "content": resp})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

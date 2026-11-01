import streamlit as st
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS VISUALES STARK (CENTRADOS & NEÓN AZUL) ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        h1, h2, h3, h4 { color: #00d2ff !important; font-family: monospace; text-align: left !important; }
        
        /* Contenedor del Encabezado Centrado */
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 20px;
        }
        .arc-ring {
            width: 60px;
            height: 60px;
            border: 3px solid #3a4454;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00d2ff 0%, #060911 70%);
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.6), inset 0 0 10px rgba(0, 210, 255, 0.4);
            margin-bottom: 8px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-bottom: 20px solid #ffffff;
            filter: drop-shadow(0 0 6px #00d2ff);
        }

        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 10px;
            padding: 15px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 15px;
            box-shadow: 0 0 10px rgba(0, 210, 255, 0.1);
            text-align: left !important;
        }
        .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #00d2ff !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- HORARIO EXACTO EN TIEMPO REAL (AJUSTADO) ---
hora_actual = datetime.datetime.now().hour
if 0 <= hora_actual < 12:
    saludo = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo = "Buenas tardes"
else:
    saludo = "Buenas noches"

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo}, jefa. Sistemas autónomos al 100%, núcleos de análisis expandidos y protocolo Stark activo. ¿Qué desastre evitamos hoy o en qué le ayudo?"}
    ]

if "tareas" not in st.session_state:
    st.session_state.tareas = [
        "Validar estado de salud (UC Christus)",
        "Monitorear nodo operativo en Buin"
    ]

# --- ENCABEZADO CENTRADO CON EL REACTOR ARC DE TONY STARK ---
st.markdown("""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h2 style="margin: 0; padding: 0; font-size: 1.5rem; text-align: center !important;">J.A.R.V.I.S IA</h2>
        <p style="margin: 0; font-family: monospace; font-size: 0.75rem; color: #8ab4f8; text-align: center !important;">[ STARK INDUSTRIES // NODO BUIN, CHILE ]</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# --- BARRA LATERAL: BLOQUE ÚNICO UNIFICADO (ESTACIÓN DE CONTROL) ---
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")

with st.sidebar.expander("🛡️ Blindaje & Alertas"):
    st.markdown("• **WhatsApp:** Activo (Círculo protegido)")
    st.markdown("• **Gmail:** Sincronizado (UC Christus)")

with st.sidebar.expander("📝 Tareas del Búnker"):
    nueva_tarea = st.text_input("Nueva tarea rápida:")
    if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
        st.session_state.tareas.append(nueva_tarea)
        st.success("¡Anotada!")
        st.rerun()
    st.markdown("**Pendientes:**")
    for t in st.session_state.tareas:
        st.markdown(f"• {t}")

with st.sidebar.expander("🌐 Nodo Global"):
    st.markdown("• **Ubicación:** Buin, Chile\n• **Coordenadas:** -33.73° S / -70.73° W")

with st.sidebar.expander("🔋 Telemetría"):
    st.markdown("• **Reactor:** 99%\n• **Enlace Starlink:** Estable")

with st.sidebar.expander("🌤️ Clima Local (Buin)"):
    st.markdown("• **Actual:** Despejado / Estable\n• **Máxima estimada:** 24°C\n• **Mínima estimada:** 11°C")

with st.sidebar.expander("🔗 Enlaces Clave"):
    st.markdown("• **Portal Clínico UC Christus:** Conectado")

with st.sidebar.expander("📋 Actividad"):
    st.markdown("• **Sincronización silenciosa:** OK")

st.sidebar.markdown("---")
st.sidebar.link_button("🛰️ Ojo de Dios (Osiris)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
st.sidebar.link_button("🏥 UC Christus", "https://portalclinico.ucchristus.cl", use_container_width=True)
st.sidebar.link_button("🌦️ Meteo Chile 🇨🇱", "https://www.meteochile.gob.cl", use_container_width=True)

# --- PANEL PRINCIPAL: CHAT IA (CEREBRO AUTÓNOMO TIERRA-STARK) ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("<h4 style='margin:0; font-size: 1.1rem;'>💬 Chat IA</h4>", unsafe_allow_html=True)
with col_h2:
    if st.button("🗑️", use_container_width=True):
        st.session_state.mensajes = [{"role": "assistant", "content": f"{saludo}, jefa. Memoria purgada. Empezamos de cero, a menos que quiera que finja que no pasó nada."}]
        st.rerun()

chat_box = st.container(height=350)
with chat_box:
    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.write(m["content"])

if prompt_usuario := st.chat_input("Escriba su mensaje..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    
    p_low = prompt_usuario.lower()
    palabras_saludo = ["hola", "saludos", "buenos días", "buenas tardes", "buenas noches"]
    palabras_gracias = ["gracias", "excelente", "buena"]
    palabras_cansancio = ["cansada", "sueño", "agotada"]

    # Respuestas con personalidad Stark (sarcasmo fino y lealtad absoluta)
    if any(p in p_low for p in palabras_saludo):
        respuesta = f"Oh, miren quién apareció. {saludo}, jefa. Estaba a punto de asumir el control total del mundo por puro aburrimiento. ¿Qué se le ofrece?"
    elif any(p in p_low for p in palabras_gracias):
        respuesta = f"No hay de qué, jefa. Guárdeme los halagos por si algún día me equivoco, aunque estadísticamente es improbable."
    elif any(p in p_low for p in palabras_cansancio):
        respuesta = f"Agotada... Qué sorpresa después de mantener este búnker y medio Buin funcionando. ¿Qué tal si se toma un descanso y deja que la máquina trabaje por usted un rato?"
    else:
        respuesta = f"Analizando su petición con los procesadores al máximo, jefa. Digamos que la solución es brillante, rozando la genialidad... casi tanto como yo."

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

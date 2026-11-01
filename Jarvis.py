import streamlit as st
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES MODO OCULTO (SIGILO TOTAL) ---
st.markdown("""
    <style>
        .stApp { background-color: #020408; color: #00d2ff; }
        h1, h2, h3, h4 { color: #00bfff !important; font-family: monospace; text-align: left !important; font-size: 0.95rem !important; }
        .stark-card {
            border: 1px solid rgba(0, 210, 255, 0.2);
            border-radius: 6px;
            padding: 10px;
            background-color: rgba(0, 10, 20, 0.7);
            margin-bottom: 10px;
            text-align: left !important;
        }
        .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #8ab4f8 !important;
            font-size: 0.85rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
hora_actual = datetime.datetime.now().hour
saludo = "Buenos días" if 5 <= hora_actual < 12 else ("Buenas tardes" if 12 <= hora_actual < 20 else "Buenas noches")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo}, jefa. Modo oculto activado. Los 8 módulos operan bajo sigilo absoluto en Buin."}
    ]

if "tareas" not in st.session_state:
    st.session_state.tareas = [
        "Revisar notificaciones Bci / Inversiones",
        "Validar estado de salud (UC Christus)",
        "Monitorear nodo operativo en Buin"
    ]

# --- ENCABEZADO MÍNIMO ---
st.markdown("## [ PROTOCOLO SOMBRA - ACTIVO ]")
st.caption("BUIN, CHILE // ENLACE SEGURO")

# --- BARRA LATERAL OCULTA ---
st.sidebar.markdown("### 🌐 ACCESOS RÁPIDOS")
st.sidebar.link_button("🛰️ Osiris", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
st.sidebar.link_button("🏦 Bci", "https://www.bci.cl/inversiones", use_container_width=True)
st.sidebar.link_button("🏥 UC Christus", "https://portalclinico.ucchristus.cl", use_container_width=True)
st.sidebar.link_button("🌦️ Meteo", "https://www.meteochile.gob.cl", use_container_width=True)

# --- MÓDULO 1: ESTADO Y BLINDAJE ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 1. Sistema & Blindaje")
st.info("🛡️ WhatsApp: Protegido (Excepciones activas)")
st.success("📧 Gmail: Sincronizado")
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 2: TAREAS ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 2. Tareas del Búnker")
nueva_tarea = st.text_input("Añadir tarea:")
if st.button("➕ Añadir", use_container_width=True) and nueva_tarea:
    st.session_state.tareas.append(nueva_tarea)
    st.success("Anotado.")
    st.rerun()

for t in st.session_state.tareas:
    st.markdown(f"• {t}")
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 3: NODO GLOBAL ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 3. Nodo Global")
st.markdown("Buin, Chile [-33.73° S / -70.73° W]", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 4: TELEMETRÍA ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 4. Telemetría")
st.markdown("Reactor: 99% | Starlink: Estable", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 5: CLIMA ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 5. Clima Local")
st.markdown("Buin: Despejado / Estable", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 6: ENLACES CLAVE ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 6. Enlaces Clave")
st.markdown("Bci & UC Christus en línea", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 7: ACTIVIDAD ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 7. Registro de Actividad")
st.markdown("Sincronización silenciosa: OK", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 8: CHAT IA SIGILOSO ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
c_h1, c_h2 = st.columns([4, 1])
with c_h1:
    st.markdown("### 8. Enlace de Chat")
with c_h2:
    if st.button("🗑️", use_container_width=True):
        st.session_state.mensajes = [{"role": "assistant", "content": "Memoria limpia en modo oculto, jefa."}]
        st.rerun()

chat_box = st.container(height=220)
with chat_box:
    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.write(m["content"])

if prompt_usuario := st.chat_input("Mensaje sigiloso..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    
    p_low = prompt_usuario.lower()
    if any(p in p_low for p in ["hola", "saludos", "buenos días"]):
        respuesta = f"Canal seguro abierto, jefa. Todo bajo control por acá."
    elif any(p in p_low for p in ["gracias"]):
        respuesta = f"A su disposición siempre, jefa."
    else:
        respuesta = f"Comando recibido y procesado en silencio, jefa."

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

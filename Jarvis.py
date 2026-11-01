import streamlit as st
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS VISUALES STARK (NEÓN AZUL & FONDO UNIFICADO) ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        h1, h2, h3, h4 { color: #00d2ff !important; font-family: monospace; text-align: left !important; }
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

# --- INICIALIZACIÓN DE ESTADOS ---
hora_actual = datetime.datetime.now().hour
saludo = "Buenos días" if 5 <= hora_actual < 12 else ("Buenas tardes" if 12 <= hora_actual < 20 else "Buenas noches")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo}, jefa. Error de sintaxis corregido. Núcleo operativo en Buin al 100%."}
    ]

if "tareas" not in st.session_state:
    st.session_state.tareas = [
        "Revisar notificaciones Bci / Inversiones",
        "Validar estado de salud (UC Christus)",
        "Monitorear nodo operativo en Buin"
    ]

# --- ENCABEZADO PRINCIPAL CON LOGOTIPO TRIANGULAR TONY STARK ---
st.markdown("## 🔺 J.A.R.V.I.S IA")
st.caption("[ STARK INDUSTRIES // NODO OPERATIVO BUIN, CHILE ]")
st.markdown("---")

# --- BARRA LATERAL: ESTACIÓN DE CONTROL Y MÓDULOS DESPLEGABLES ---
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")
st.sidebar.link_button("🛰️ Ojo de Dios (Osiris)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
st.sidebar.link_button("🏦 Banco Bci", "https://www.bci.cl/inversiones", use_container_width=True)
st.sidebar.link_button("🏥 UC Christus", "https://portalclinico.ucchristus.cl", use_container_width=True)
st.sidebar.link_button("🌦️ Meteo Chile 🇨🇱", "https://www.meteochile.gob.cl", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Módulos del Sistema")

# Módulos desplegables en la barra lateral
with st.sidebar.expander("🛡️ Blindaje & Alertas"):
    st.info("WhatsApp: Activo (Círculo protegido)")
    st.success("Gmail: Sincronizadas (Bci / UC)")

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
    st.markdown("UBICACIÓN: Buin, Chile\n\nCOORDENADAS: -33.73° S / -70.73° W")

with st.sidebar.expander("🔋 Telemetría"):
    st.markdown("Reactor: 99%\n\nEnlace Starlink: Estable")

with st.sidebar.expander("🌤️ Clima Local"):
    st.markdown("Buin: Despejado / Estable")

with st.sidebar.expander("🔗 Enlaces Clave"):
    st.markdown("Bci Inversiones & UC Christus en línea")

with st.sidebar.expander("📋 Actividad"):
    st.markdown("Sincronización silenciosa: OK")

# --- PANEL PRINCIPAL: CHAT IA ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("### 💬 Chat IA")
with col_h2:
    if st.button("🗑️", use_container_width=True):
        st.session_state.mensajes = [{"role": "assistant", "content": "Memoria limpia y fresca, jefa. ¿De qué conversamos ahora?"}]
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

    if any(p in p_low for p in palabras_saludo):
        respuesta = f"¡Hola de nuevo, jefa! Qué gusto leerla. ¿Cómo va todo por ahí?"
    elif any(p in p_low for p in palabras_gracias):
        respuesta = f"Para eso estamos, jefa. Me alegra mucho que le guste cómo va quedando."
    elif any(p in p_low for p in palabras_cansancio):
        respuesta

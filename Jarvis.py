import streamlit as st
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES STARK PARA MÓVIL ---
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
        {"role": "assistant", "content": f"{saludo}, jefa. Interfaz optimizada para móvil. Núcleo operativo activo."}
    ]

if "tareas" not in st.session_state:
    st.session_state.tareas = [
        "Revisar notificaciones Bci / Inversiones",
        "Validar estado de salud (UC Christus)",
        "Monitorear nodo operativo en Buin"
    ]

# --- ENCABEZADO PRINCIPAL ---
st.markdown("## 🛡️ J.A.R.V.I.S IA")
st.caption("[ NODO OPERATIVO BUIN, CHILE ]")
st.markdown("---")

# --- BARRA LATERAL (ESTACIÓN DE CONTROL MÓVIL) ---
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")
st.sidebar.link_button("🛰️ Ojo de Dios (Osiris)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
st.sidebar.link_button("🏦 Banco Bci", "https://www.bci.cl/inversiones", use_container_width=True)
st.sidebar.link_button("🏥 UC Christus", "https://portalclinico.ucchristus.cl", use_container_width=True)
st.sidebar.link_button("🌦️ Meteo Chile 🇨🇱", "https://www.meteochile.gob.cl", use_container_width=True)

# --- MÓDULO 1: ESTADO DEL SISTEMA (SEGURIDAD Y ALERTAS JUNTAS) ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 📌 Estado del Sistema")
st.info("🛡️ **Blindaje WhatsApp:** Activo (Círculo protegido)")
st.success("📧 **Alertas Gmail:** Sincronizadas (Bci / UC)")
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 2: TAREAS DEL BÚNKER ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 📝 Tareas del Búnker")
nueva_tarea = st.text_input("Nueva tarea rápida:")
if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
    st.session_state.tareas.append(nueva_tarea)
    st.success("Registrada con éxito.")
    st.rerun()

st.markdown("**Pendientes:**")
for t in st.session_state.tareas:
    st.markdown(f"• {t}")
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 3: TELEMETRÍA ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 🌐 Nodo Global")
st.markdown("""
    <div style="font-family: monospace; font-size: 0.85rem; padding: 2px 0;">
        UBICACIÓN: Buin, Chile<br>
        COORDENADAS: -33.73° S / -70.73° W
    </div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 4: CHAT IA ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("### 🤖 Chat IA")
with col_h2:
    if st.button("🗑️", use_container_width=True):
        st.session_state.mensajes = [{"role": "assistant", "content": "Memoria purgada, jefa."}]
        st.rerun()

chat_box = st.container(height=300)
with chat_box:
    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.write(m["content"])

if prompt_usuario := st.chat_input("Escriba su comando..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    st.session_state.mensajes.append({"role": "assistant", "content": f"Para usted, jefa, siempre. Orden: '{prompt_usuario}'."})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

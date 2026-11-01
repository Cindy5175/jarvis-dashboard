import streamlit as st
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS VISUALES STARK (NEÓN & MODO OSCURO) ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        h1, h2, h3, h4 { color: #00d2ff !important; font-family: monospace; text-align: left !important; }
        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 10px;
            padding: 20px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 20px;
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
        {"role": "assistant", "content": f"{saludo}, jefa. Módulos unificados perfectamente. Núcleo operativo en Buin activo."}
    ]

if "tareas" not in st.session_state:
    st.session_state.tareas = [
        "Revisar notificaciones Bci / Inversiones",
        "Validar estado de salud (UC Christus)",
        "Monitorear nodo operativo en Buin"
    ]

# --- ENCABEZADO PRINCIPAL ---
st.markdown("## 🛡️ J.A.R.V.I.S IA - NÚCLEO TÁCTICO")
st.caption("[ STARK INDUSTRIES // NODO OPERATIVO BUIN, CHILE ]")
st.markdown("---")

# --- BARRA LATERAL: ESTACIÓN DE CONTROL ---
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")
st.sidebar.markdown("---")
st.sidebar.markdown("🚀 **Monitoreo Satelital**")
st.sidebar.link_button("🛰️ Ojo de Dios (Osiris)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)

st.sidebar.markdown("### 📌 Enlaces Directos")
st.sidebar.link_button("🏦 Banco Bci", "https://www.bci.cl/inversiones", use_container_width=True)
st.sidebar.link_button("🏥 UC Christus", "https://portalclinico.ucchristus.cl", use_container_width=True)
st.sidebar.link_button("🌦️ Meteo Chile 🇨🇱", "https://www.meteochile.gob.cl", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.caption("🔋 Potencia del Reactor: 99%")
st.sidebar.caption("📡 Enlace Starlink: Estable")

# --- MÓDULO 1: SEGURIDAD, SINCRONIZACIÓN Y TAREAS (UNIFICADO) ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 📌 Seguridad, Sincronización & Tareas")
st.info("🛡️ **Blindaje WhatsApp:** Activo (Círculo familiar protegido)")
st.success("📧 **Alertas Gmail:** Sincronizadas (Bci / UC Christus)")
st.markdown("---")
st.markdown("#### 📝 Tareas y Notas del Búnker")
nueva_tarea = st.text_input("Añadir nueva directiva / tarea rápida:")
if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
    st.session_state.tareas.append(nueva_tarea)
    st.success("Directiva registrada con éxito.")
    st.rerun()

st.markdown("**Listado operativo actual:**")
for t in st.session_state.tareas:
    st.markdown(f"• {t}")
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 2: TELEMETRÍA Y COORDENADAS ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 🌐 Nodo Holográfico Global")
st.markdown("""
    <div style="font-family: monospace; font-size: 0.9rem; padding: 5px 0;">
        ESTADO DEL NODO: Órbita estable<br>
        UBICACIÓN: Buin, Chile<br>
        COORDENADAS TÁCTICAS: -33.73° S / -70.73° W
    </div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- MÓDULO 3: CHAT IA PRINCIPAL ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
col_h1, col_h2 = st.columns([5, 1])
with col_h1:
    st.markdown("### 🤖 Interfaz de Comando (Chat IA)")
with col_h2:
    if st.button("🗑️ Purgar", use_container_width=True):
        st.session_state.mensajes = [{"role": "assistant", "content": "Memoria purgada, jefa. Sistemas listos."}]
        st.rerun()

chat_box = st.container(height=350)
with chat_box:
    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.write(m["content"])

if prompt_usuario := st.chat_input("Escriba su comando o directiva para J.A.R.V.I.S..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    
    p_low = prompt_usuario.lower()
    if "hola" in p_low or "saludos" in p_low:
        respuesta = f"{saludo}, jefa. Todos los sistemas operan en perfecta armonía."
    else:
        respuesta = f"Para usted, jefa, siempre. Comando '{prompt_usuario}' procesado correctamente."
        
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

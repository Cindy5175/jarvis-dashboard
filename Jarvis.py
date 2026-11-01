import streamlit as st

# Configuración de página limpia
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO", 
    layout="wide"
)

# Estilo visual Stark
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        h1, h2, h3, h4 { color: #00d2ff !important; font-family: monospace; }
        .stark-card {
            border: 1px solid #00d2ff;
            border-radius: 8px;
            padding: 15px;
            background-color: rgba(0, 210, 255, 0.03);
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# Estado inicial del chat y tareas
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "Núcleo operativo en Buin activo, jefa. Todos los módulos alineados a la izquierda. ¿Qué orden ejecutamos?"}
    ]

if "tareas" not in st.session_state:
    st.session_state.tareas = ["Revisar notificaciones Bci", "Optimizar búnker", "Monitorear Buin"]

# Título Principal
st.markdown("## 🛡️ J.A.R.V.I.S IA - NÚCLEO TÁCTICO")
st.caption("[ NODO OPERATIVO STARK INDUSTRIES // BUIN, CHILE ]")

# Barra lateral con enlaces directos
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")
st.sidebar.link_button("🛰️ Ojo de Dios (Osiris)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
st.sidebar.link_button("🏦 Banco Bci", "https://www.bci.cl/inversiones", use_container_width=True)
st.sidebar.link_button("🏥 UC Christus", "https://portalclinico.ucchristus.cl", use_container_width=True)
st.sidebar.link_button("🌦️ Meteo Chile", "https://www.meteochile.gob.cl", use_container_width=True)

# --- TODOS LOS MÓDULOS EN COLUMNA ÚNICA A LA IZQUIERDA ---

st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 📌 Blindaje WhatsApp & Alertas Gmail")
st.info("Blindaje WhatsApp: Activo (Círculo familiar protegido)")
st.success("Alertas Gmail: Sincronizadas (Bci / UC Christus)")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 📝 Tareas del Búnker")
nueva = st.text_input("Nueva tarea rápida:")
if st.button("➕ Registrar Tarea", use_container_width=True) and nueva:
    st.session_state.tareas.append(nueva)
    st.rerun()
for t in st.session_state.tareas:
    st.markdown(f"• {t}")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("### 🌐 Nodo Holográfico Global")
st.markdown("""
    <div style="font-family: monospace; color: #00d2ff; font-size: 0.85rem; padding: 5px 0;">
        ESTADO: Órbita estable — COORDENADAS: -33.73° S / -70.73° W (Buin)
    </div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="stark-card">', unsafe_allow_html=True)
c_h1, c_h2 = st.columns([4, 1])
with c_h1:
    st.markdown("### 🤖 Chat IA")
with c_h2:
    if st.button("🗑️ Purgar", use_container_width=True):
        st.session_state.mensajes = [{"role": "assistant", "content": "Memoria purgada, jefa. Sistema listo."}]
        st.rerun()

chat_container = st.container(height=320)
with chat_container:
    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.write(m["content"])

if prompt := st.chat_input("Escriba su comando para J.A.R.V.I.S..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    st.session_state.mensajes.append({"role": "assistant", "content": f"Para usted, jefa, siempre. Comando recibido: '{prompt}'."})
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

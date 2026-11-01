import streamlit as st

# Configuración de página limpia
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO", 
    layout="wide"
)

# Estilo visual Stark básico y seguro
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        h1, h2, h3 { color: #00d2ff !important; font-family: monospace; }
        .stark-card {
            border: 1px solid #00d2ff;
            border-radius: 8px;
            padding: 15px;
            background-color: rgba(0, 210, 255, 0.03);
            margin-bottom: 15px;
        }
    </style>
""", unsafe_allow_html=True)

# Estado inicial del chat
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "Núcleo operativo en Buin activo, jefa. ¿Qué orden ejecutamos?"}
    ]

# Título Principal
st.markdown("## 🛡️ J.A.R.V.I.S IA - NÚCLEO TÁCTICO")
st.caption("[ NODO OPERATIVO STARK INDUSTRIES // BUIN, CHILE ]")

# Barra lateral con enlaces directos
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")
st.sidebar.link_button("🛰️ Ojo de Dios (Osiris)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
st.sidebar.link_button("🏦 Banco Bci", "https://www.bci.cl/inversiones", use_container_width=True)
st.sidebar.link_button("🏥 UC Christus", "https://portalclinico.ucchristus.cl", use_container_width=True)
st.sidebar.link_button("🌦️ Meteo Chile", "https://www.meteochile.gob.cl", use_container_width=True)

# Diseño en 2 columnas
col_izq, col_der = st.columns(2, gap="medium")

with col_izq:
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("### 📌 Módulos Independientes")
    st.info("Blindaje WhatsApp: Activo (Círculo protegido)")
    st.success("Alertas Gmail: Sincronizadas (Bci / UC Christus)")
    
    st.markdown("#### Tareas del Búnker")
    tarea = st.text_input("Nueva tarea rápida:")
    if st.button("Registrar Tarea", use_container_width=True) and tarea:
        st.success(f"Registrada: {tarea}")
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("### 🌐 Nodo Holográfico & Chat IA")
    
    # Historial de chat limpio
    chat_container = st.container(height=320)
    with chat_container:
        for m in st.session_state.mensajes:
            with st.chat_message(m["role"]):
                st.write(m["content"])

    # Entrada de chat
    if prompt := st.chat_input("Escriba su comando para J.A.R.V.I.S..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        st.session_state.mensajes.append({"role": "assistant", "content": f"Para usted, jefa, siempre. Comando recibido: '{prompt}'."})
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

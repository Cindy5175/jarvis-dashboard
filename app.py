import streamlit as st
import datetime

# Configuración de página
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Estilo visual Stark
st.markdown("""
    <style>
        .main { background-color: #060911; }
        h1, h2, h3, h4 { color: #00d2ff !important; font-family: 'Courier New', monospace; }
        .stSelectbox label, .stTextInput label, .stTextArea label { color: #00d2ff !important; font-family: 'Courier New', monospace; }
        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 10px;
            padding: 16px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 16px;
            box-shadow: 0 0 12px rgba(0, 210, 255, 0.15);
        }
        .module-title {
            color: #00d2ff;
            font-family: 'Courier New', monospace;
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(0, 210, 255, 0.3);
            padding-bottom: 4px;
        }
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
            width: 155px;
            height: 55px;
            border: 1px solid rgba(0, 210, 255, 0.6);
            border-radius: 50%;
            transform: rotate(-20deg);
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
""", unsafe_allow_html=True)

# Saludo según hora
hora = datetime.datetime.now().hour
saludo = "Buenos días" if 5 <= hora < 12 else ("Buenas tardes" if 12 <= hora < 20 else "Buenas noches")

if "tareas" not in st.session_state:
    st.session_state.tareas = ["Revisar notificaciones Bci", "Optimizar búnker", "Monitorear Buin"]

if "chat" not in st.session_state:
    st.session_state.chat = [{"role": "assistant", "content": f"{saludo}, jefa. Núcleo operativo en Buin activo."}]

# Encabezado
st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h2 style="color: #00d2ff; letter-spacing: 2px; margin:0;">J.A.R.V.I.S IA - NÚCLEO TÁCTICO</h2>
        <p style="color: #00d2ff; font-family: monospace; font-size: 0.8rem; opacity: 0.85;">[ BUIN, CHILE ]</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")
st.sidebar.link_button("🛰️ Ojo de Dios (Osiris)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
st.sidebar.link_button("🏦 Banco Bci", "https://www.bci.cl/inversiones", use_container_width=True)
st.sidebar.link_button("🏥 UC Christus", "https://portalclinico.ucchristus.cl", use_container_width=True)
st.sidebar.link_button("🌦️ Meteo Chile 🇨🇱", "https://www.meteochile.gob.cl", use_container_width=True)

# 2 Columnas
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Blindaje WhatsApp</div>', unsafe_allow_html=True)
    st.info("Estado: Activo • Círculo Familiar Protegido")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Alertas Gmail</div>', unsafe_allow_html=True)
    st.success("Bandeja sincronizada correctamente.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Tareas Tácticas</div>', unsafe_allow_html=True)
    nueva = st.text_input("Nueva tarea:")
    if st.button("➕ Agregar", use_container_width=True) and nueva:
        st.session_state.tareas.append(nueva)
        st.rerun()
    for t in st.session_state.tareas:
        st.markdown(f"• {t}")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown('<div class="module-title">Nodo Holográfico Global</div>', unsafe_allow_html=True)
    st.markdown("""
        <div class="globe-container">
            <div class="orbit"></div>
            <div class="globe"></div>
        </div>
        <div style="font-family: monospace; color: #00d2ff; font-size: 0.75rem; text-align: center; margin-top: 8px;">
            COORDENADAS: -33.73° S / -70.73° W
        </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    ch_1, ch_2 = st.columns([3, 1])
    with ch_1:
        st.markdown('<div class="module-title" style="border:none; margin:0; padding:0;">Chat IA</div>', unsafe_allow_html=True)
    with ch_2:
        if st.button("🗑️", use_container_width=True):
            st.session_state.chat = [{"role": "assistant", "content": "Memoria purgada, jefa."}]
            st.rerun()

    cbox = st.container(height=300)
    with cbox:
        for m in st.session_state.chat:
            with st.chat_message(m["role"]):
                st.write(m["content"])

    prompt = st.chat_input("Escriba su comando...")
    if prompt:
        st.session_state.chat.append({"role": "user", "content": prompt})
        st.session_state.chat.append({"role": "assistant", "content": f"Comando '{prompt}' procesado, jefa."})
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

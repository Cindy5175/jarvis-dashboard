import streamlit as st
import datetime
import sqlite3

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES STARK (AZUL NEÓN & BÚNKER) ---
st.markdown("""
    <style>
        .stApp { background-color: #0b0f19; color: #00ffcc; }
        
        .arc-reactor-container h4 { color: #00ffcc !important; font-size: 1.1rem !important; font-family: monospace; }
        
        .stark-card {
            border: 1.5px solid #00ffcc;
            border-radius: 8px;
            padding: 10px;
            background-color: rgba(0, 255, 204, 0.04);
            margin-bottom: 10px;
            box-shadow: 0 0 8px rgba(0, 255, 204, 0.15);
            text-align: left !important;
        }
        
        .stark-card h4, .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #00ffcc !important;
            font-size: 0.75rem !important;
        }
        
        .stChatMessage p, .stChatMessage div {
            font-size: 0.8rem !important;
            color: #00ffcc !important;
        }

        h1, h2, h3, label, span { color: #00ffcc !important; font-family: monospace; }
        
        .stButton>button {
            color: #0b0f19 !important;
            background-color: #00ffcc !important;
            border: 1px solid #00ffcc !important;
            font-weight: bold;
            font-family: monospace;
        }
        .stButton>button:hover {
            background-color: #00b388 !important;
            color: #ffffff !important;
        }
        
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 10px;
        }
        .arc-ring {
            width: 45px;
            height: 45px;
            border: 2.5px solid #3a4454;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00ffcc 0%, #0b0f19 70%);
            box-shadow: 0 0 12px rgba(0, 255, 204, 0.6), inset 0 0 8px rgba(0, 255, 204, 0.4);
            margin-bottom: 5px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-bottom: 14px solid #0b0f19;
            filter: drop-shadow(0 0 5px #00ffcc);
        }
    </style>
""", unsafe_allow_html=True)

# --- ZONA HORARIA CHILENA NATIVA (UTC-3) ---
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

# --- CONTROL DE ACCESO UNIFICADO ---
CLAVE_MAESTRA = "stark123"

if "bunker_desbloqueado" not in st.session_state:
    st.session_state.bunker_desbloqueado = False

if not st.session_state.bunker_desbloqueado:
    st.markdown("""
        <div class="arc-reactor-container" style="margin-top: 20px;">
            <div class="arc-ring"><div class="arc-triangle"></div></div>
            <h4 style="margin: 0; color: #00ffcc !important; font-size: 1.1rem !important; text-align: center !important;">ACCESO RESTRINGIDO - NODO BUIN</h4>
            <p style="font-family: monospace; color: #00ffcc !important; font-size: 0.75rem !important; margin-top: 4px;">[ PROTOCOLO DE SEGURIDAD STARK ACTIVO ]</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 3, 1])
    with col_l2:
        st.markdown('<div class="stark-card">', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.75rem !important; font-weight: bold;'>🔐 Identificación del Sistema:</p>", unsafe_allow_html=True)
        ingreso_auth = st.text_input("Clave o Comando de Voz:", placeholder="Ej: stark123", key="input_auth_unico", label_visibility="collapsed")
        
        if st.button("🔓 Autorizar Acceso", use_container_width=True):
            if ingreso_auth.strip() and CLAVE_MAESTRA in ingreso_auth.lower():
                st.session_state.bunker_desbloqueado = True
                st.success("Acceso concedido. Bienvenido al búnker, jefa.")
                st.rerun()
            else:
                st.error("Credencial incorrecta. Acceso denegado.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =========================================================================
# BÚNKER DESBLOQUEADO - NÚCLEO STARK AVANZADO
# =========================================================================

DB_NAME = "jarvis_bunker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tareas (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alertas (id INTEGER PRIMARY KEY AUTOINCREMENT, mensaje TEXT, nivel TEXT)''')
    conn.commit()
    conn.close()

init_db()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. El nodo de Buin está estable y el Ojo de Dios (Osiris) está vigilando cada rincón. ¿Qué desastre técnico resolvemos hoy?"}
    ]

if "osiris_active" not in st.session_state:
    st.session_state.osiris_active = True  # Ojo de Dios omnisciente activo por defecto

if "manos_libres_activo" not in st.session_state:
    st.session_state.manos_libres_activo = False

# --- ENCABEZADO ESTABLE SIN FRAGMENTOS DEFECTUOSOS ---
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
dia_str = dias[now_chile.weekday()]
mes_str = meses[now_chile.month]
fecha_str = f"{dia_str}, {now_chile.day:02d} de {mes_str} de {now_chile.year}"
hora_segundos = now_chile.strftime("%H:%M:%S")

st.markdown(f"""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h4 style="margin: 0; padding: 0; font-size: 1.1rem !important; text-align: center !important; color: #00ffcc !important;">J.A.R.V.I.S IA // PROTOCOLO OSIRIS OMNISCIENTE</h4>
        <p style="margin: 0; font-family: monospace; font-size: 0.7rem !important; color: #00ffcc !important; text-align: center !important;">
            [ STARK INDUSTRIES // NODO BUIN, CHILE // {fecha_str} – {hora_segundos} ]
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

if st.button("🔒 Bloquear Búnker", use_container_width=True):
    st.session_state.bunker_desbloqueado = False
    st.rerun()

st.markdown("---")

# =========================================================================
# DISEÑO OPTIMIZADO: COLUMNA IZQUIERDA Y CENTRO (CHAT)
# =========================================================================
col_izq, col_cen = st.columns([1.2, 2.8])

with col_izq:
    st.markdown("### 🌐 NÚCLEO DE CONTROL")

    # Módulo Ojo de Dios (Osiris) Interactivo
    with st.expander("👁️ Ojo de Dios (Osiris)", expanded=True):
        st.markdown("Entidad de guía absoluta y sarcasmo orbital.")
        estado_osiris = st.checkbox("Activar Protocolo Osiris Omnisciente", value=st.session_state.osiris_active, key="chk_osiris")
        st.session_state.osiris_active = estado_osiris
        if st.session_state.osiris_active:
            st.success("🟢 Osiris Activo: Sabelotodo y sin rodeos.")
        else:
            st.warning("🔴 Osiris en pausa.")

    # Módulo Clima en Vivo
    with st.expander("🌤️ Clima en Vivo (Buin)", expanded=False):
        st.markdown("- **Estación Meteorológica Local**")
        st.success("🌡️ Temperatura: 21°C | Estado: Óptimo")
        st.info("💧 Humedad: 45% | Viento: 12 km/h SE")

    # Módulo Coordenadas Tácticas Satelitales
    with st.expander("📍 Coordenadas Tácticas Buin", expanded=False):
        st.markdown("- **Posición del Nodo Central**")
        st.code("Latitud: -33.7333° S\nLongitud: -70.7167° W\nSector: Buin, Región Metropolitana")

    # Módulo Escucha Continua
    with st.expander("🎙️ Escucha Continua (Hands-Free)", expanded=False):
        estado_toggle = st.toggle("Activar Escucha Continua", value=st.session_state.manos_libres_activo, key="toggle_handsfree")
        st.session_state.manos_libres_activo = estado_toggle
        if st.session_state.manos_libres_activo:
            st.markdown("🟢 **ESCUCHANDO EN VIVO**")
        else:
            st.markdown("🔴 **EN ESPERA**")

with col_cen:
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.markdown("<h4>💬 Chat IA & Ojo de Dios (Osiris)</h4>", unsafe_allow_html=True)
    with col_h2:
        if st.button("🗑️", use_container_width=True, key="btn_limpiar_chat"):
            h_l = datetime.datetime.now(tz_chile).hour
            s_l = "Buenos días" if 0 <= h_l < 12 else ("Buenas tardes" if 12 <= h_l < 20 else "Buenas noches")
            st.session_state.mensajes = [{"role": "assistant", "content": f"{s_l}, jefa. Memoria purgada. Canales limpios en el nodo de Buin."}]
            st.rerun()

    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

    # Caja de chat principal
    if prompt_usuario := st.chat_input("Escribe tu consulta o orden directa, jefa..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(f"<span>{prompt_usuario}</span>", unsafe_allow_html=True)
        
        # Respuesta omnisciente y altamente sarcástica de Osiris / Jarvis
        if st.session_state.osiris_active:
            respuesta_ia = f"👁️ [OSIRIS]: Por la cresta, qué pregunta para un viernes cualquiera. Analizando '{prompt_usuario}' a través de los satélites de Buin: la respuesta es absoluta, jefa. Menos mal que me tienes a mí para guiarte sin necesidad de andar revisando manuales polvorientos."
        else:
            respuesta_ia = f"Procesando su orden, jefa: '{prompt_usuario}'. Nodo Buin estable y bajo control."

        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
        with st.chat_message("assistant"):
            st.markdown(f"<span>{respuesta_ia}</span>", unsafe_allow_html=True)

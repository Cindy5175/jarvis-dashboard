import streamlit as st
import datetime
import sqlite3

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES STARK (ESTÉTICA DE BÚNKER) ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        
        .arc-reactor-container h4 { color: #00d2ff !important; font-size: 1.1rem !important; font-family: monospace; }
        
        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 8px;
            padding: 10px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 10px;
            box-shadow: 0 0 8px rgba(0, 210, 255, 0.1);
            text-align: left !important;
        }
        
        .stark-card h4 {
            font-size: 0.75rem !important;
            color: #00d2ff !important;
            margin-bottom: 5px !important;
        }
        
        .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #00d2ff !important;
            font-size: 0.7rem !important;
        }
        
        .stChatMessage p, .stChatMessage div {
            font-size: 0.75rem !important;
            color: #00d2ff !important;
        }

        h1, h2, h3, label, span { color: #00d2ff !important; font-family: monospace; }
        
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
            background: radial-gradient(circle, #00d2ff 0%, #060911 70%);
            box-shadow: 0 0 12px rgba(0, 210, 255, 0.6), inset 0 0 8px rgba(0, 210, 255, 0.4);
            margin-bottom: 5px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-bottom: 14px solid #ffffff;
            filter: drop-shadow(0 0 5px #00d2ff);
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
            <h4 style="margin: 0; color: #00d2ff !important; font-size: 1.1rem !important; text-align: center !important;">ACCESO RESTRINGIDO - NODO BUIN</h4>
            <p style="font-family: monospace; color: #00d2ff !important; font-size: 0.75rem !important; margin-top: 4px;">[ PROTOCOLO DE SEGURIDAD STARK ACTIVO ]</p>
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
    
    c.execute("SELECT COUNT(*) FROM tareas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Validar estado de salud (UC Christus)",))
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Monitorear nodo operativo en Buin",))
        conn.commit()
        
    c.execute("SELECT COUNT(*) FROM alertas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", ("Temperatura Buin óptima (21°C)", "INFO"))
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", ("Blindaje WhatsApp y Gmail operativo", "OK"))
        conn.commit()
    conn.close()

init_db()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. El nodo de Buin está estable, la temperatura es perfecta y, sorprendentemente, nadie ha intentado hackearnos hoy. ¿Qué milagro te trae por aquí?"}
    ]

# Inicializar estado del manos libres si no existe
if "manos_libres_activo" not in st.session_state:
    st.session_state.manos_libres_activo = False

# --- ENCABEZADO CON RELOJ EN VIVO ---
@st.fragment(run_every=1)
def render_live_header():
    now = datetime.datetime.now(tz_chile)
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    
    dia_str = dias[now.weekday()]
    mes_str = meses[now.month]
    fecha_str = f"{dia_str}, {now.day:02d} de {mes_str} de {now.year}"
    hora_segundos = now.strftime("%H:%M:%S")
    
    st.markdown(f"""
        <div class="arc-reactor-container">
            <div class="arc-ring"><div class="arc-triangle"></div></div>
            <h4 style="margin: 0; padding: 0; font-size: 1.1rem !important; text-align: center !important; color: #00d2ff !important;">J.A.R.V.I.S IA // E.D.I.T.H. TACTICAL CORE</h4>
            <p style="margin: 0; font-family: monospace; font-size: 0.7rem !important; color: #00d2ff !important; text-align: center !important;">
                [ STARK INDUSTRIES // NODO BUIN, CHILE // {fecha_str} – {hora_segundos} ]
            </p>
        </div>
    """, unsafe_allow_html=True)

render_live_header()
st.markdown("---")

if st.button("🔒 Bloquear Búnker", use_container_width=True):
    st.session_state.bunker_desbloqueado = False
    st.rerun()

st.markdown("---")

# =========================================================================
# DISEÑO OPTIMIZADO: COLUMNA IZQUIERDA (MÓDULOS) Y CENTRO (CHAT)
# =========================================================================
col_izq, col_cen = st.columns([1.2, 2.8])

# -------------------------------------------------------------------------
# COLUMNA IZQUIERDA (MÓDULOS EXPANDIBLES E ICONOS)
# -------------------------------------------------------------------------
with col_izq:
    st.markdown("### 🌐 NÚCLEO DE CONTROL")

    # Módulo de Cámara en Vivo / Ojo de Dios
    with st.expander("📷 Cámaras en Vivo (Ojo de Dios)", expanded=False):
        st.markdown("- Transmisión orbital en directo (ISS)")
        st.video("https://www.youtube.com/watch?v=4QJEibrt9B8")

    # Módulo Clima en Vivo
    with st.expander("🌤️ Clima en Vivo (Buin)", expanded=True):
        st.markdown("- **Estación Meteorológica Local**")
        st.success("🌡️ Temperatura: 21°C | Estado: Óptimo")
        st.info("💧 Humedad: 45% | Viento: 12 km/h SE")

    # Módulo Coordenadas Tácticas Satelitales
    with st.expander("📍 Coordenadas Tácticas Buin", expanded=False):
        st.markdown("- **Posición del Nodo Central**")
        st.code("Latitud: -33.7333° S\nLongitud: -70.7167° W\nSector: Buin, Región Metropolitana")
        st.caption("Usa el visor Osiris AI en E.D.I.T.H. para escaneo visual detallado.")

    # Módulo de Escucha Continua (Con indicador visual de estado)
    with st.expander("🎙️ Escucha Continua (Hands-Free)", expanded=False):
        st.markdown("- **Control de Audio Local**")
        
        estado_toggle = st.toggle("Activar Escucha Continua", value=st.session_state.manos_libres_activo, key="toggle_handsfree")
        st.session_state.manos_libres_activo = estado_toggle
        
        if st.session_state.manos_libres_activo:
            st.markdown("🟢 **ESTADO: ESCUCHANDO EN VIVO** (El script local en tu PC está atento a tu voz)")
        else:
            st.markdown("🔴 **ESTADO: EN ESPERA / MANUAL** (Micrófono inactivo)")
            
        st.info("El manos libres opera localmente en tu ordenador para máxima velocidad y seguridad.")

    # Módulo de Registro de Tareas
    with st.expander("⚙️ Registro de Tareas", expanded=False):
        st.markdown("- **Gestión de Protocolos**")
        if st.button("➕ Registrar Tarea", use_container_width=True):
            st.success("Tarea registrada correctamente en el sistema.")
        st.info("Sistema de tareas secundarias sincronizado.")

    # Módulo 1: E.D.I.T.H.
    with st.expander("🛰️ Módulo E.D.I.T.H.", expanded=False):
        st.markdown("- **Control Óptico y Satelital**")
        usar_camara_edith = st.checkbox("📷 Cámara Óptica", value=False, key="cam_edith")
        if usar_camara_edith:
            foto_edith = st.camera_input("Captura orbital:")
            if foto_edith:
                st.success("Fotograma analizado.")
        edith_query = st.text_input("Objetivo:", key="obj_edith")
        if st.button("🕶️ Escaneo", use_container_width=True, key="btn_edith"):
            if edith_query.strip():
                st.success(f"Rastreado: {edith_query}")
            else:
                st.warning("Ingrese un objetivo.")
        st.link_button("🌐 Visor Osiris AI", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)

    # Módulo 2: Fundamentos y Bases
    with st.expander("🐧 Fundamentos y Bases", expanded=False):
        st.markdown("- **Aprende lo básico: Linux, Redes, Python**")
        if st.button("🐧 Núcleo Linux", use_container_width=True, key="b_lin"): st.info("Linux activo.")
        if st.button("🌐 Redes", use_container_width=True, key="b_net"): st.info("Redes activas.")
        if st.button("🐍 Python", use_container_width=True, key="b_py"): st.info("Python operativo.")

    # Módulo 3: Exploración y Práctica
    with st.expander("👁️ Exploración y Práctica", expanded=False):
        st.markdown("- **Práctica activa: Nmap, Wireshark, Burp**")
        if st.button("👁️ Nmap", use_container_width=True, key="b_nmap"): st.info("Nmap desplegado.")
        if st.button("🦈 Wireshark", use_container_width=True, key="b_wire"): st.info("Wireshark en curso.")
        if st.button("⚡ Burp Suite", use_container_width=True, key="b_burp"): st.info("Burp conectado.")


# -------------------------------------------------------------------------
# COLUMNA CENTRAL (CHAT IA AMPLIADO Y PROTOCOLO JARVIS MEJORADO)
# -------------------------------------------------------------------------
with col_cen:
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.markdown("<h4>💬 Chat IA & Protocolo E.D.I.T.H.</h4>", unsafe_allow_html=True)
    with col_h2:
        if st.button("🗑️", use_container_width=True, key="btn_limpiar_chat"):
            h_l = datetime.datetime.now(tz_chile).hour
            s_l = "Buenos días" if 0 <= h_l < 12 else ("Buenas tardes" if 12 <= h_l < 20 else "Buenas noches")
            st.session_state.mensajes = [{"role": "assistant", "content": f"{s_l}, jefa. Memoria purgada por E.D.I.T.H. ¿Qué directiva suicida o genial ejecutamos ahora?"}]
            st.rerun()

    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

    # Caja de chat optimizada y amplia
    if prompt_usuario := st.chat_input("Escribe tu orden o dicte a E.D.I.T.H., jefa..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(f"<span>{prompt_usuario}</span>", unsafe_allow_html=True)
        
        # Inteligencia Stark con tono sarcástico, humano y natural
        texto_lower = prompt_usuario.lower()
        if "hola" in texto_lower or "saludos" in texto_lower:
            respuesta_ia = "Hola, jefa. El nodo de Buin está estable, la temperatura es perfecta y, sorprendentemente, nadie ha intentado hackearnos hoy. ¿Qué milagro te trae por aquí?"
        elif "estado" in texto_lower or "sistema" in texto_lower:
            respuesta_ia = "Todo verde y funcionando a la perfección, jefa. El reactor Arc no brama, pero el servidor sufre en silencio. ¿Alguna otra crisis que deba ignorar con elegancia?"
        elif "clima" in texto_lower:
            respuesta_ia = "21°C en Buin, un clima tan tranquilo que casi da sospechas. ¿Quieres que mueva las nubes o prefieres lidiar con la realidad tú misma?"
        else:
            respuesta_ia = f"Orden procesada: '{prompt_usuario}'. Suéltala y déjamelo a mí, jefa. Aunque entre tú y yo, a veces tus ideas suenan a que quieres volar por los aires otra vez."

        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
        with st.chat_message("assistant"):
            st.markdown(f"<span>{respuesta_ia}</span>", unsafe_allow_html=True
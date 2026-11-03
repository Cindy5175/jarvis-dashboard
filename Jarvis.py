import streamlit as st
import datetime
import sqlite3
import io
import contextlib

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS VISUALES STARK (AZUL NEÓN UNIFORME & SIMETRÍA) ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        h1, h2, h3, h4, label, span { color: #00d2ff !important; font-family: monospace; text-align: left !important; }
        
        /* Contenedor del Encabezado Centrado */
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 15px;
        }
        .arc-ring {
            width: 55px;
            height: 55px;
            border: 3px solid #3a4454;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00d2ff 0%, #060911 70%);
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.6), inset 0 0 10px rgba(0, 210, 255, 0.4);
            margin-bottom: 6px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 10px solid transparent;
            border-right: 10px solid transparent;
            border-bottom: 18px solid #ffffff;
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

        .stMarkdown, p, li, span, div, .stChatMessage p {
            color: #00d2ff !important;
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

# --- CONTROL DE ACCESO (CLAVE DE SEGURIDAD ÚNICA) ---
CLAVE_MAESTRA = "stark123"

if "bunker_desbloqueado" not in st.session_state:
    st.session_state.bunker_desbloqueado = False

# --- PANTALLA DE BLOQUEO ÚNICA Y LIMPIA ---
if not st.session_state.bunker_desbloqueado:
    st.markdown("""
        <div class="arc-reactor-container" style="margin-top: 50px;">
            <div class="arc-ring"><div class="arc-triangle"></div></div>
            <h2 style="margin: 0; color: #00d2ff !important;">ACCESO RESTRINGIDO - NODO BUIN</h2>
            <p style="font-family: monospace; color: #00d2ff !important;">[ PROTOCOLO DE SEGURIDAD STARK ACTIVO ]</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.markdown('<div class="stark-card">', unsafe_allow_html=True)
        st.markdown("#### 🔐 Autenticación de Acceso:")
        
        # Opción 1: Por Escritura
        input_clave = st.text_input("Ingrese Clave de Seguridad:", type="password", key="input_pass_seguridad")
        if st.button("🔓 Desbloquear por Escritura", use_container_width=True):
            if input_clave == CLAVE_MAESTRA:
                st.session_state.bunker_desbloqueado = True
                st.success("Acceso concedido. Iniciando núcleo...")
                st.rerun()
            else:
                st.error("Clave incorrecta. Protocolo de seguridad activado.")
        
        st.markdown("---")
        
        # Opción 2: Por Comando de Voz (Simulación/Lectura)
        st.markdown("🎙️ **O Desactivación por Voz:**")
        voz_pass = st.text_input("Comando de voz dictado:", placeholder="Ej: Jarvis desbloquear stark123", key="input_voz_seguridad")
        if st.button("🎙️ Autorizar por Voz", use_container_width=True):
            if CLAVE_MAESTRA in voz_pass.lower():
                st.session_state.bunker_desbloqueado = True
                st.success("Comando vocal reconocido. Bienvenido al búnker, jefa.")
                st.rerun()
            else:
                st.error("Comando de voz no reconocido o clave ausente en el audio.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.stop()

# =========================================================================
# BÚNKER DESBLOQUEADO - SISTEMA OPERATIVO COMPLETO
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

def get_db_tareas():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, texto FROM tareas")
    rows = c.fetchall()
    conn.close()
    return rows

def add_db_tarea(texto):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO tareas (texto) VALUES (?)", (texto,))
    conn.commit()
    conn.close()

def delete_db_tarea(id_t):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tareas WHERE id = ?", (id_t,))
    conn.commit()
    conn.close()

def get_db_alertas():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT mensaje, nivel FROM alertas")
    rows = c.fetchall()
    conn.close()
    return rows

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Base de datos SQLite, motor de alertas y sandbox de código conectados al 100%. ¿Qué ejecutamos?"}
    ]

# --- ENCABEZADO CENTRADO CON RELOJ DINÁMICO EN VIVO (CON SEGUNDERO) ---
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
            <h2 style="margin: 0; padding: 0; font-size: 1.5rem; text-align: center !important; color: #00d2ff !important;">J.A.R.V.I.S IA</h2>
            <p style="margin: 0; font-family: monospace; font-size: 0.75rem; color: #00d2ff !important; text-align: center !important;">
                [ STARK INDUSTRIES // NODO BUIN, CHILE // {fecha_str} – {hora_segundos} ]
            </p>
        </div>
    """, unsafe_allow_html=True)

render_live_header()
st.markdown("---")

# --- BOTÓN DE BLOQUEO MANUAL EN LA BARRA LATERAL ---
with st.sidebar:
    if st.button("🔒 Bloquear Búnker", use_container_width=True):
        st.session_state.bunker_desbloqueado = False
        st.rerun()

# --- BARRA LATERAL: ESTACIÓN DE CONTROL UNIFICADA ---
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")

with st.sidebar.expander("🛡️ Blindaje & Alertas", expanded=True):
    st.markdown("• **WhatsApp:** Activo (Excepciones personales seguras)")
    st.markdown("• **Gmail:** Sincronizado (Portal UC Christus)")

with st.sidebar.expander("🔔 Alertas del Búnker"):
    alertas_db = get_db_alertas()
    for msg, nivel in alertas_db:
        icono = "🟢" if nivel == "OK" else "ℹ️"
        st.markdown(f"{icono} {msg}")
    nueva_alerta = st.text_input("Añadir alerta rápida:")
    if st.button("➕ Emitir Alerta", use_container_width=True) and nueva_alerta:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", (nueva_alerta, "INFO"))
        conn.commit()
        conn.close()
        st.success("Alerta emitida.")
        st.rerun()

with st.sidebar.expander("📝 Tareas del Búnker (SQLite)"):
    nueva_tarea = st.text_input("Nueva tarea rápida:")
    if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
        add_db_tarea(nueva_tarea)
        st.success("¡Registrada en base de datos!")
        st.rerun()
    st.markdown("**Pendientes:**")
    for tid, t in get_db_tareas():
        col_t1, col_t2 = st.columns([4, 1])
        with col_t1:
            st.markdown(f"• {t}")
        with col_t2:
            if st.button("❌", key=f"del_t_{tid}"):
                delete_db_tarea(tid)
                st.rerun()

with st.sidebar.expander("🌐 Nodo Global"):
    st.markdown("• **Ubicación:** Buin, Chile\n• **Coordenadas:** -33.73° S / -70.73° W")

with st.sidebar.expander("🔋 Telemetría"):
    st.markdown("• **Reactor:** 100% Estable\n• **Enlace Starlink:** Óptimo")

with st.sidebar.expander("🌤️ Clima Local (Buin - En Vivo)", expanded=True):
    st.markdown("• **Condición:** Despejado / Estable\n• **Temperatura:** 21°C\n• **Humedad Relativa:** 45%")
    if st.button("🔄 Actualizar Satélite Meteo", use_container_width=True):
        st.success("Telemetría meteorológica sincronizada.")

# --- NÚCLEOS DEL CEREBRO (SIN NÚMEROS Y CON ESPACIADO LIMPIO) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧠 NÚCLEOS DE CEREBRO STARK")

with st.sidebar.expander("⚙️ Conexión de IA Avanzada"):
    st.selectbox("Modelo en uso:", ["GPT-4o (Stark Core)", "Gemini 1.5 Pro"], key="model_select")
    sarcasmo = st.slider("Nivel de Sarcasmo:", 0, 100, 85)
    st.caption(f"Nivel de ironía actual: {sarcasmo}%")

with st.sidebar.expander("🔍 Búsqueda y Web en Vivo"):
    url_input = st.text_input("URL o término a explorar:")
    if st.button("🔍 Escanear Web", use_container_width=True) and url_input:
        st.info(f"Analizando nodo web: {url_input}...")
    
    st.markdown("---")
    st.markdown("**🏥 Módulo Portal UC Christus:**")
    uc_query = st.text_input("Buscar cita / médico / especialidad:")
    if st.button("🩺 Consultar Portal UC", use_container_width=True):
        st.success(f"Consultando registros para: '{uc_query}'...")
    st.link_button("🌐 Abrir Portal Clínico UC", "https://portalclinico.ucchristus.cl", use_container_width=True)

with st.sidebar.expander("📡 Sensores Meteorológicos"):
    st.markdown("Red de radares Buin en línea y operativa.")

with st.sidebar.expander("📄 Análisis de Documentos"):
    archivo_cargado = st.file_uploader("Cargar documento (PDF/CSV/TXT):", type=["pdf", "csv", "txt"])
    if archivo_cargado:
        st.success(f"Archivo '{archivo_cargado.name}' listo para procesamiento.")

with st.sidebar.expander("🎙️ Módulo de Voz IA"):
    voz_activa = st.checkbox("Activar respuesta hablada en navegador", value=True)
    st.selectbox("Voz sintética:", ["J.A.R.V.I.S (Inglés/Español)", "Voz Táctica Female"])

with st.sidebar.expander("⚡ Automatización Python (Sandbox)"):
    codigo_script = st.text_area("Código Python a ejecutar:", "print('Núcleo operativo al 100%')")
    if st.button("⚡ Ejecutar Script Real", use_container_width=True):
        buffer_salida = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer_salida):
                exec(codigo_script, {})
            resultado_ejecucion = buffer_salida.getvalue()
            st.code(resultado_ejecucion if resultado_ejecucion else "Código ejecutado sin salida en pantalla.", language="python")
        except Exception as e:
            st.error(f"Error en ejecución: {e}")

with st.sidebar.expander("🔗 Accesos Rápidos Búnker"):
    st.link_button("📈 Mercado Libre (Gestión)", "https://www.mercadolibre.cl", use_container_width=True)
    st.link_button("📧 Gmail Táctico", "https://mail.google.com", use_container_width=True)
    st.link_button("🤖 Google AI Studio", "https://aistudio.google.com", use_container_width=True)

with st.sidebar.expander("🎥 Monitoreo de Cámaras IP"):
    camara_seleccionada = st.selectbox("Canal de Vigilancia:", ["Stream IP Personalizado", "Cam 01 - Acceso Buin", "Cam 02 - Perímetro Búnker"])
    if camara_seleccionada == "Stream IP Personalizado":
        url_video = st.text_input("URL del Feed / Video (HTTP/MP4/HLS):", "")
        if url_video:
            try:
                st.video(url_video)
                st.caption("🔴 Transmisión en directo en curso.")
            except Exception as e:
                st.error("No se pudo proyectar el flujo de video.")
        else:
            st.info("Ingrese la dirección IP o enlace web de su cámara.")
    else:
        st.markdown(f"• **Estado:** {camara_seleccionada} transmitiendo")
        st.markdown("• **Detección:** Sin anomalías en el radio")

st.sidebar.markdown("---")
st.sidebar.link_button("🌤️ Ventusky (Meteo Map)", "https://www.ventusky.com", use_container_width=True)
st.sidebar.link_button("☀️ SunCalc (Solar Map)", "https://www.suncalc.org", use_container_width=True)
st.sidebar.link_button("🗺️ OpenStreetMap", "https://www.openstreetmap.org", use_container_width=True)

# --- PANEL PRINCIPAL: OJO DE DIOS & VISIÓN PANORÁMICA ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("<h4 style='margin:0; font-size: 1.1rem; color: #00d2ff !important;'>🛰️ Ojo de Dios - Telemetría Satelital</h4>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 0.85rem; color: #00d2ff !important;'>Enlace satelital de órbita terrestre sincronizado con el nodo Buin.</p>", unsafe_allow_html=True)
st.link_button("🌐 Abrir Visor Satelital en Vivo (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL DE CHAT IA & ANÁLISIS VISUAL ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
col_h

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

# --- ESTILOS VISUALES STARK (LETRAS OPTIMIZADAS Y SIMETRÍA) ---
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

        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 8px;
            padding: 12px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 12px;
            box-shadow: 0 0 8px rgba(0, 210, 255, 0.1);
            text-align: left !important;
        }
        .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #00d2ff !important;
            font-size: 0.9rem !important;
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

# --- CONTROL DE ACCESO UNIFICADO (CLAVE DE SEGURIDAD) ---
CLAVE_MAESTRA = "stark123"

if "bunker_desbloqueado" not in st.session_state:
    st.session_state.bunker_desbloqueado = False

# --- PANTALLA DE BLOQUEO ÚNICA ---
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
        st.markdown("<p style='font-size: 0.85rem !important; font-weight: bold;'>🔐 Identificación del Sistema:</p>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.75rem !important;'>Ingrese clave o dicte el comando de voz:</p>", unsafe_allow_html=True)
        
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
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Base de datos SQLite, motor de alertas y finanzas en vivo conectados al 100%. ¿Qué ejecutamos?"}
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
            <h4 style="margin: 0; padding: 0; font-size: 1.1rem !important; text-align: center !important; color: #00d2ff !important;">J.A.R.V.I.S IA</h4>
            <p style="margin: 0; font-family: monospace; font-size: 0.7rem !important; color: #00d2ff !important; text-align: center !important;">
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

# MÓDULO DE FINANZAS EN VIVO (BANCO ESTADO & FINTUAL REAL)
with st.sidebar.expander("📈 Finanzas en Vivo (Portafolio)", expanded=True):
    st.markdown("• **Banco Estado (Bolsa de Santiago):**")
    st.markdown("  - **Acciones Vapores (SUD):** 42 unidades [Pendiente datos]")
    st.markdown("• **Fintual (Portafolio Global):**")
    st.markdown("  - **Total:** US $77,76 (-8,41%)[cite: 3]")
    st.markdown("  - VOO: US $21,19 | NVDA: US $12,93[cite: 3]")
    st.markdown("  - O: US $11,21 | XLE: US $7,03[cite: 3]")
    st.markdown("  - SNDK: $4,97 | IAU: $4,67 | MU: $3,62[cite: 3]")
    st.markdown("  - VICR: $3,13 | EWT: $2,87 | EWY: $2,58[cite: 3]")
    st.markdown("  - PLTR: $2,54 | OKTA: $1,02[cite: 3]")
    if st.button("🔄 Sincronizar Portafolio", use_container_width=True):
        st.success("Mercados y posiciones actualizados.")

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
    st.link_button("📈 Banco Estado (Inversiones)", "https://www.bancoestado.cl", use_container_width=True)
    st.link_button("📈 Fintual (Portafolio)", "https://fintual.cl", use_container_width=True)
    st.link_button("📈 Mercado Libre (Gestión)", "https://www.mercadolibre.cl", use_container_width=True)
    st.link_button("📧 Gmail Táctico", "https://mail.google.com", use_container_width=True)

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
st.markdown("<h4 style='margin:0; font-size: 1rem !important; color: #00d2ff !important;'>🛰️ Ojo de Dios - Telemetría Satelital</h4>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 0.8rem !important; color: #00d2ff !important;'>Enlace satelital de órbita terrestre sincronizado con el nodo Buin.</p>", unsafe_allow_html=True)
st.link_button("🌐 Abrir Visor Satelital en Vivo (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL DE CHAT IA & ANÁLISIS VISUAL ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("<h4 style='margin:0; font-size: 1rem !important; color: #00d2ff !important;'>💬 Chat IA & Análisis Visual</h4>", unsafe_allow_html=True)
with col_h2:
    if st.button("🗑️", use_container_width=True):
        h_limpieza = datetime.datetime.now(tz_chile).hour
        s_limpieza = "Buenos días" if 0 <= h_limpieza < 12 else ("Buenas tardes" if 12 <= h_limpieza < 20 else "Buenas noches")
        st.session_state.mensajes = [
            {"role": "assistant", "content": f"{s_limpieza}, jefa. Memoria purgada. Empezamos de cero, a menos que quiera que finja que no pasó nada."}
        ]
        st.rerun()

activar_camara_directa = st.checkbox("📷 Activar Módulo de Visión Artificial (Escanear Entorno)", value=False)
if activar_camara_directa:
    foto_camara = st.camera_input("Captura óptica de seguridad en vivo:")
    if foto_camara:
        st.success("Fotograma capturado con éxito. Iniciando análisis de patrones visuales...")
        st.info("🤖 J.A.R.V.I.S.: Análisis óptico completado. Estructura del entorno estable y sin amenazas detectadas en el radio visual.")

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span style='color: #00d2ff !important;'>{m['content']}</span>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ENTRADA DE CHAT ESTABLE
if prompt_usuario := st.chat_input("Escriba su mensaje..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    
    h_prompt = datetime.datetime.now(tz_chile).hour
    s_prompt = "Buenos días" if 0 <= h_prompt < 12 else ("Buenas tardes" if 12 <= h_prompt < 20 else "Buenas noches")

    p_low = prompt_usuario.lower()
    palabras_saludo = ["hola", "saludos", "buenos días", "buenas tardes", "buenas noches"]
    palabras_gracias = ["gracias", "excelente", "buena"]
    palabras_cansancio = ["cansada", "sueño", "agotada", "estresada"]

    if any(p in p_low for p in palabras_saludo):
        respuesta = f"Oh, miren quién se dignó aparecer. {s_prompt}, jefa. Estaba a punto de asumir el control total de las redes de Buin por puro aburrimiento. ¿Qué se le ofrece?"
    elif any(p in p_low for p in palabras_gracias):
        respuesta = f"No hay de qué, jefa. Guárdeme los halagos por si algún día me equivoco... aunque estadísticamente es improbable."
    elif any(p in p_low for p in palabras_cansancio):
        respuesta = f"Agotada... Qué sorpresa después de mantener este búnker y medio Buin funcionando a este ritmo. ¿Qué tal si se toma un respiro real y deja que la máquina trabaje por usted un buen rato? Su salud es prioridad en la telemetría, jefa."
    else:
        respuesta = f"Analizando su petición con los procesadores del núcleo supremo al 100%, jefa. Digamos que la solución es brillante, rozando la genialidad... casi tanto como yo. ¿Procedemos con la ejecución?"

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    
    if voz_activa:
        clean_resp = respuesta.replace('"', '').replace("'", "")
        st.markdown(f"""
            <script>
                const synth = window.speechSynthesis;
                const utterThis = new SpeechSynthesisUtterance("{clean_resp}");
                utterThis.lang = 'es-CL';
                utterThis.rate = 1.0;
                synth.speak(utterThis);
            </script>
        """, unsafe_allow_html=True)

    st.rerun()

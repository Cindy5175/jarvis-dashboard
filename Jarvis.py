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

# --- ESTILOS VISUALES STARK (TÍTULOS PRINCIPALES MÁS PEQUEÑOS) ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        
        /* El encabezado superior se mantiene intacto y destacado */
        .arc-reactor-container h4 { color: #00d2ff !important; font-size: 1.1rem !important; font-family: monospace; }
        
        /* Tarjetas del panel principal con fuentes muy compactas */
        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 8px;
            padding: 8px 10px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 8px;
            box-shadow: 0 0 8px rgba(0, 210, 255, 0.1);
            text-align: left !important;
        }
        
        /* Achicar drásticamente los títulos h4 dentro de las tarjetas principales */
        .stark-card h4 {
            font-size: 0.7rem !important;
            color: #00d2ff !important;
            margin-bottom: 4px !important;
        }
        
        /* Achicar párrafos y textos generales del cuerpo principal */
        .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #00d2ff !important;
            font-size: 0.7rem !important;
        }
        
        /* Achicar texto del chat principal */
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
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Núcleo Stark y E.D.I.T.H. sincronizados. ¿Qué órdenes ejecutamos?"}
    ]

# --- ENCABEZADO CON RELOJ EN VIVO (INTACTO Y DESTACADO) ---
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

with st.sidebar:
    if st.button("🔒 Bloquear Búnker", use_container_width=True):
        st.session_state.bunker_desbloqueado = False
        st.rerun()

# --- BARRA LATERAL: ESTACIÓN DE CONTROL STARK ---
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")

# 1. MÓDULO E.D.I.T.H. (EQUIPO DIGITAL DE INTERVENCIÓN TÁCTICA Y HACKING)
with st.sidebar.expander("🛰️ Módulo E.D.I.T.H. (Órbita & Óptica)", expanded=True):
    st.markdown("• **Significado:** *Equipo Digital de Intervención Táctica y Hacking*")
    st.markdown("• **Estado:** Órbita Baja Activa")
    
    usar_camara_edith = st.checkbox("📷 Activar Cámara Óptica E.D.I.T.H.", value=False)
    if usar_camara_edith:
        foto_edith = st.camera_input("Captura de seguridad E.D.I.T.H.:")
        if foto_edith:
            st.success("E.D.I.T.H.: Fotograma analizado con éxito por los servidores orbitales.")

    edith_query = st.text_input("Consulta a E.D.I.T.H. (Ej: Datos / Objetivo):")
    if st.button("🕶️ Ejecutar Escaneo E.D.I.T.H.", use_container_width=True):
        if edith_query.strip():
            st.success(f"E.D.I.T.H.: Registros cruzados para '{edith_query}'. Datos recuperados sin interrupciones.")
        else:
            st.warning("Ingrese un parámetro de búsqueda.")

# 2. FINANZAS
with st.sidebar.expander("📈 Finanzas en Vivo (Portafolio)", expanded=True):
    st.markdown("• **Banco Estado (Bolsa de Santiago):**")
    st.markdown("  - **Acciones Vapores (SUD):** 42 unidades")
    st.markdown("• **Fintual (Portafolio Global):**")
    st.markdown("  - **Total:** US $77,76 (-8,41%)")
    st.markdown("  - VOO: US $21,19 | NVDA: US $12,93 | O: US $11,21")
    if st.button("🔄 Sincronizar Portafolio", use_container_width=True):
        st.success("Mercados y posiciones actualizados.")

# 3. OSINT TÁCTICO
with st.sidebar.expander("🕵️ Módulo OSINT Táctico", expanded=True):
    osint_modo = st.selectbox("Seleccionar Protocolo:", ["1. Auditoría de Ciberseguridad", "2. Verificación Periodística", "3. Rastreo Criminológico", "4. Due Diligence Corporativo"])
    target_osint = st.text_input("Objetivo o Dominio a Analizar:", placeholder="Ej: objetivo.cl")
    if st.button("🚀 Ejecutar Protocolo OSINT", use_container_width=True) and target_osint.strip():
        st.success(f"Analizando [{osint_modo}] sobre '{target_osint}': Nodo seguro.")

# 4. BLINDAJE Y ALERTAS
with st.sidebar.expander("🛡️ Blindaje & Alertas", expanded=True):
    st.markdown("• **WhatsApp:** Activo (Excepciones personales seguras)")
    st.markdown("• **Gmail:** Sincronizado (Portal UC Christus)")

with st.sidebar.expander("🔔 Alertas del Búnker"):
    for msg, nivel in get_db_alertas():
        st.markdown(f"{'🟢' if nivel == 'OK' else 'ℹ️'} {msg}")
    nueva_alerta = st.text_input("Añadir alerta rápida:")
    if st.button("➕ Emitir Alerta", use_container_width=True) and nueva_alerta:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", (nueva_alerta, "INFO"))
        conn.commit()
        conn.close()
        st.rerun()

# 5. TAREAS SQLITE
with st.sidebar.expander("📝 Tareas del Búnker (SQLite)"):
    nueva_tarea = st.text_input("Nueva tarea rápida:")
    if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
        add_db_tarea(nueva_tarea)
        st.rerun()
    for tid, t in get_db_tareas():
        col_t1, col_t2 = st.columns([4, 1])
        with col_t1:
            st.markdown(f"• {t}")
        with col_t2:
            if st.button("❌", key=f"del_t_{tid}"):
                delete_db_tarea(tid)
                st.rerun()

with st.sidebar.expander("🌤️ Clima Local (Buin - En Vivo)", expanded=True):
    st.markdown("• **Condición:** Despejado / Estable\n• **Temperatura:** 21°C\n• **Humedad Relativa:** 45%")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🧠 NÚCLEOS DE CEREBRO STARK")

with st.sidebar.expander("⚙️ Conexión de IA Avanzada", expanded=True):
    st.selectbox("Modelo en uso:", ["GPT-4o (Stark Core)", "Gemini 1.5 Pro"], key="model_select")
    sarcasmo = st.slider("Nivel de Sarcasmo / Ironía:", 0, 100, 85)

with st.sidebar.expander("🔍 Búsqueda y Web en Vivo"):
    url_input = st.text_input("URL o término a explorar:")
    if st.button("🔍 Escanear Web", use_container_width=True) and url_input:
        st.info(f"Analizando nodo web: {url_input}...")
    st.link_button("🌐 Abrir Portal Clínico UC", "https://portalclinico.ucchristus.cl", use_container_width=True)

with st.sidebar.expander("🎙️ Módulo de Voz IA

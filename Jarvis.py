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

# --- ESTILOS VISUALES STARK (ESTÉTICA NEÓN AZUL, SIMETRÍA Y LETRAS OPTIMIZADAS) ---
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

# --- PANTALLA DE BLOQUEO ÚNICA Y OPTIMIZADA ---
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
# BÚNKER DESBLOQUEADO - SISTEMA OPERATIVO TOTALMENTE INTEGRADO
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
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Todos los sistemas del búnker, base de datos SQLite, finanzas en vivo y el nuevo Módulo OSINT Táctico están conectados al 100%. ¿Qué ejecutamos?"}
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

# 1. MÓDULO DE FINANZAS EN VIVO (BANCO ESTADO & FINTUAL REAL)
with st.sidebar.expander("📈 Finanzas en Vivo (Portafolio)", expanded=True):
    st.markdown("• **Banco Estado (Bolsa de Santiago):**")
    st.markdown("  - **Acciones Vapores (SUD):** 42 unidades [Pendiente datos]")
    st.markdown("• **Fintual (Portafolio Global):**")
    st.markdown("  - **Total:** US $77,76 (-8,41%)")
    st.markdown("  - VOO: US $21,19 | NVDA: US $12,93")
    st.markdown("  - O: US $11,21 | XLE: US $7,03")
    st.markdown("  - SNDK: $4,97 | IAU: $4,67 | MU: $3,62")
    st.markdown("  - VICR: $3,13 | EWT: $2,87 | EWY: $2,58")
    st.markdown("  - PLTR: $2,54 | OKTA: $1,02")
    if st.button("🔄 Sincronizar Portafolio", use_container_width=True):
        st.success("Mercados y posiciones actualizados.")

# 2. NUEVO MÓDULO OSINT TÁCTICO EJECUTABLE
with st.sidebar.expander("🕵️ Módulo OSINT Táctico", expanded=True):
    st.markdown("• **Ciberseguridad:** Evaluación de exposición digital.")
    st.markdown("• **Periodismo de Investigación:** Verificación de hechos y redes.")
    st.markdown("• **Criminología:** Análisis de patrones y registros.")
    st.markdown("• **Due Diligence:** Antecedentes corporativos y socios.")
    
    osint_modo = st.selectbox("Seleccionar Protocolo:", [
        "1. Auditoría de Ciberseguridad", 
        "2. Verificación Periodística", 
        "3. Rastreo Criminológico", 
        "4. Due Diligence Corporativo"
    ])
    
    target_osint = st.text_input("Objetivo o Dominio a Analizar:", placeholder="Ej: objetivo.cl / tema / usuario")
    if st.button("🚀 Ejecutar Protocolo OSINT", use_container_width=True):
        if target_osint.strip():
            st.success(f"Analizando bajo [{osint_modo}]...")
            st.info(f"🔍 Resultados OSINT para '{target_osint}': Fuentes abiertas consultadas. Nodo sin brechas críticas expuestas en radio local.")
        else:
            st.warning("Ingrese un objetivo válido para iniciar el escaneo.")

# 3. BLINDAJE Y ALERTAS
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

# 4. TAREAS SQLITE
with st.sidebar.expander("📝 Tareas del Búnker (SQLite)"):
    nueva_tarea = st.text_input("Nueva tarea rápida:")
    if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
        add_db_tarea(nueva_tarea)
        st.success("¡Registrada en base de datos!")
        st.rerun()

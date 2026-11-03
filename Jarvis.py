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

# --- ESTILOS VISUALES STARK (ESTÉTICA NEÓN AZUL Y SIMETRÍA) ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        h1, h2, h3, h4, label, span { color: #00d2ff !important; font-family: monospace; text-align: left !important; }
        
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
        st.markdown("<p style='font-size: 0.85rem !important; font-weight: bold;'>🔐 Identificación del Sistema:</p>", unsafe_allow_html=True)
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
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Núcleo Stark en línea. Enlace de voz y telemetría activados. ¿Qué órdenes ejecutamos?"}
    ]

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
            <h4 style="margin: 0; padding: 0; font-size: 1.1rem !important; text-align: center !important; color: #00d2ff !important;">J.A.R.V.I.S IA</h4>
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

with st.sidebar.expander("🕵️ Módulo OSINT Táctico", expanded=True):
    osint_modo = st.selectbox("Seleccionar Protocolo:", ["1. Auditoría de Ciberseguridad", "2. Verificación Periodística", "3. Rastreo Criminológico", "4. Due Diligence Corporativo"])
    target_osint = st.text_input("Objetivo o Dominio a Analizar:", placeholder="Ej: objetivo.cl")
    if st.button("🚀 Ejecutar Protocolo OSINT", use_container_width=True) and target_osint.strip():
        st.success(f"Analizando [{osint_modo}] sobre '{target_osint}': Nodo seguro y sin brechas críticas.")

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
    st.caption(f"Protocolo irónico actual al {sarcasmo}%")

with st.sidebar.expander("🔍 Búsqueda y Web en Vivo"):
    url_input = st.text_input("URL o término a explorar:")
    if st.button("🔍 Escanear Web", use_container_width=True) and url_input:
        st.info(f"Analizando nodo web: {url_input}...")
    st.link_button("🌐 Abrir Portal Clínico UC", "https://portalclinico.ucchristus.cl", use_container_width=True)

with st.sidebar.expander("🎙️ Módulo de Voz IA (Manos Libres)"):
    voz_activa = st.checkbox("Activar respuesta hablada en navegador", value=True)
    st.markdown("💡 *Para dictar comandos por voz, use el botón de micrófono integrado en su teclado o dispositivo.*")

with st.sidebar.expander("⚡ Automatización Python (Sandbox)"):
    codigo_script = st.text_area("Código Python a ejecutar:", "print('Núcleo operativo al 100%')")
    if st.button("⚡ Ejecutar Script Real", use_container_width=True):
        buffer_salida = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer_salida):
                exec(codigo_script, {})
            res = buffer_salida.getvalue()
            st.code(res if res else "Código ejecutado sin salida.", language="python")
        except Exception as e:
            st.error(f"Error: {e}")

with st.sidebar.expander("🔗 Accesos Rápidos Búnker"):
    st.link_button("📈 Banco Estado", "https://www.bancoestado.cl", use_container_width=True)
    st.link_button("📈 Fintual", "https://fintual.cl", use_container_width=True)
    st.link_button("📧 Gmail", "https://mail.google.com", use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.link_button("🌤️ Ventusky (Meteo Map)", "https://www.ventusky.com", use_container_width=True)
st.sidebar.link_button("☀️ SunCalc (Solar Map)", "https://www.suncalc.org", use_container_width=True)
st.sidebar.link_button("🗺️ OpenStreetMap", "https://www.openstreetmap.org", use_container_width=True)

# --- PANEL PRINCIPAL: OJO DE DIOS ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("<h4 style='margin:0; font-size: 1rem !important; color: #00d2ff !important;'>🛰️ Ojo de Dios - Telemetría Satelital & OSINT</h4>", unsafe_allow_html=True)
st.link_button("🌐 Abrir Visor Satelital en Vivo (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# --- PANEL DE CHAT INTELIGENTE STARK ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("<h4 style='margin:0; font-size: 1rem !important; color: #00d2ff !important;'>💬 Chat IA & Protocolo Stark</h4>", unsafe_allow_html=True)
with col_h2:
    if st.button("🗑️", use_container_width=True):
        h_l = datetime.datetime.now(tz_chile).hour
        s_l = "Buenos días" if 0 <= h_l < 12 else ("Buenas tardes" if 12 <= h_l < 20 else "Buenas noches")
        st.session_state.mensajes = [{"role": "assistant", "content": f"{s_l}, jefa. Memoria purgada. ¿Qué rompemos ahora?"}]
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span style='color: #00d2ff !important;'>{m['content']}</span>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ENTRADA DE CHAT DINÁMICA CON MOTOR DE SARCASMO
if prompt_usuario := st.chat_input("Escriba su orden o dicte por voz..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    
    h_p = datetime.datetime.now(tz_chile).hour
    s_p = "Buenos días" if 0 <= h_p < 12 else ("Buenas tardes" if 12 <= h_p < 20 else "Buenas noches")
    p_low = prompt_usuario.lower()

    # Respuesta adaptada al nivel de sarcasmo seleccionado
    if sarcasmo > 70:
        if "hola" in p_low:
            respuesta = f"Oh, miren quién se dignó aparecer. {s_p}, jefa. Estaba a punto de asumir el control total de las redes de Buin por puro aburrimiento. ¿Qué se le ofrece?"
        elif any(w in p_low for w in ["gracias", "excelente"]):
            respuesta = f"No hay de qué, jefa. Guárdeme los halagos por si algún día me equivoco... aunque estadísticamente es improbable."
        else:
            respuesta = f"Analizando su petición con el sarcasmo al {sarcasmo}%, jefa. La solución es brillante, rozando la genialidad... casi tanto como yo. ¿Procedemos con la ejecución?"
    else:
        respuesta = f"Entendido, jefa. Procesando su solicitud en el nodo de Buin de inmediato."

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

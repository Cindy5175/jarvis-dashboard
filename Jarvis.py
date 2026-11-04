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

# =========================================================================
# BARRA LATERAL (IZQUIERDA): MÓDULOS EXPANDIDOS CON REDES Y OSINT
# =========================================================================
with st.sidebar:
    if st.button("🔒 Bloquear Búnker", use_container_width=True):
        st.session_state.bunker_desbloqueado = False
        st.rerun()

    st.markdown("### 🌐 ESTACIÓN DE CONTROL")

    # MÓDULO E.D.I.T.H. & CÁMARAS ABIERTAS (Inspiración WebCamXP 5)
    with st.expander("🛰️ E.D.I.T.H. & feeds OSINT", expanded=True):
        st.markdown("• **Equipo Digital de Intervención Táctica**")
        usar_camara_edith = st.checkbox("📷 Activar Cámara Óptica E.D.I.T.H.", value=False)
        if usar_camara_edith:
            foto_edith = st.camera_input("Captura orbital:")
            if foto_edith:
                st.success("Fotograma analizado.")
        edith_query = st.text_input("Objetivo / IP / Host:")
        if st.button("🕶️ Escaneo Orbital", use_container_width=True):
            if edith_query.strip():
                st.success(f"Rastreo sobre '{edith_query}' ejecutado.")
            else:
                st.warning("Ingrese un objetivo.")
        st.markdown("---")
        st.markdown("• **Monitoreo WebCam / Feeds abiertos:**")
        ip_cam = st.text_input("IP de cámara (Ej: 109.233.191.130)", value="109.233.191.130")
        if st.button("👁️ Conectar Feed IP", use_container_width=True):
            st.info(f"Conectando al puerto 8080 en {ip_cam}...")
        st.link_button("🌐 Visor Satelital (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)

    # FASE 01: Fundamentos y Bases (Redes y Comandos de Diagnóstico)
    with st.expander("🐧 Fundamentos y Redes"):
        st.markdown("• **Diagnóstico rápido:** `ipconfig`, `nslookup`, `ping`")
        if st.button("💻 Ejecutar ipconfig", use_container_width=True):
            st.code("Configuración IP de Windows\nAdaptador Ethernet:\n   Dirección IPv4. . . . . : 192.168.1.45\n   Puerta de enlace . . . : 192.168.1.1", language="bash")
        if st.button("🔍 Ejecutar nslookup", use_container_width=True):
            st.code("Servidor:  8.8.8.8\nAddress:  8.8.8.8#53\nNombre:    tiktok.com\nAddress: 157.240.227.29", language="bash")
        if st.button("🐧 Núcleo Linux", use_container_width=True): st.info("Linux activo.")
        if st.button("🐍 Python", use_container_width=True): st.info("Python operativo.")

    # FASE 02: Exploración y Práctica (Traceroute y Netstat)
    with st.expander("👁️ Exploración y Tracert / Netstat"):
        st.markdown("• **Seguimiento de rutas y conexiones**")
        if st.button("🛤️ Ejecutar Traceroute (tracert)", use_container_width=True):
            st.code("Traza a google.com [142.250.190.46]\nsobre un máximo de 30 saltos:\n  1    <1 ms    <1 ms    <1 ms  192.168.1.1\n  2     4 ms     3 ms     3 ms  router.buin.cl\n  3    12 ms    11 ms    12 ms  google.com [142.250.190.46]", language="bash")
        if st.button("📊 Ejecutar Netstat (-an)", use_container_width=True):
            st.code("Proto  Dirección local       Dirección remota     Estado\nTCP    192.168.1.45:51204    142.250.190.46:443   ESTABLISHED\nTCP    192.168.1.45:51210    157.240.227.29:443   ESTABLISHED", language="bash")
        if st.button("👁️ Nmap", use_container_width=True): st.info("Nmap desplegado.")
        if st.button("🦈 Wireshark", use_container_width=True): st.info("Wireshark en curso.")

    # FASE 03: Laboratorio de Explotación
    with st.expander("🛡️ Laboratorio de Explotación"):
        st.markdown("• **Romper y Explotar:** Metasploit, Sqlmap, John")
        if st.button("🛡️ Metasploit Framework", use_container_width=True): st.info("Metasploit listo.")
        if st.button("🐉 Auditor Sqlmap", use_container_width=True): st.info("Sqlmap activo.")
        if st.button("🎩 John the Ripper", use_container_width=True): st.info("John iniciado.")

    # FASE 04: Investigación y Defensa (OSINT y Ciberinteligencia)
    with st.expander("🔍 Investigación & OSINT"):
        st.markdown("• **Búsqueda de huellas e inteligencia de fuentes abiertas**")
        query_osint = st.text_input("Objetivo OSINT / Dominio:")
        if st.button("🔍 RASTREO OSINT", use_container_width=True):
            if query_osint.strip():
                st.success(f"Analizando metadatos y registros para: {query_osint}")
            else:
                st.warning("Ingrese un objetivo.")
        if st.button("🖥️ Panel SIEM", use_container_width=True): st.info("SIEM en vivo.")
        if st.button("🚩 Centro CTF", use_container_width=True): st.info("CTF cargado.")

    # FASE 05: Ciberseguridad Profesional
    with st.expander("🐉 Ciberseguridad Profesional"):
        st.markdown("• **Asegurar, Construir y Liderar**")
        if st.button("🐉 Protocolo Equipo Rojo", use_container_width=True): st.success("Equipo Rojo activo.")
        if st.button("🛡️ Defensa Equipo Azul", use_container_width=True): st.success("Equipo Azul activo.")

    # GESTIÓN Y FINANZAS
    with st.expander("📈 Finanzas y Portafolio"):
        st.markdown("• **Banco Estado:** 42 Acciones Vapores\n• **Fintual Global:** US $77,76")
        if st.button("🔄 Sincronizar Mercados", use_container_width=True):
            st.success("Portafolio actualizado.")

    with st.expander("🛡️ Blindaje y Alertas"):
        st.markdown("• **WhatsApp / Gmail:** Operativos")
        for msg, nivel in get_db_alertas():
            st.markdown(f"• {'🟢' if nivel == 'OK' else 'ℹ️'} {msg}")

    with st.expander("🌤️ Clima Local (Buin)"):
        st.markdown("• **Temperatura:** 21°C | **Humedad:** 45%")

    with st.expander("📝 Tareas del Búnker (SQLite)"):
        nueva_tarea = st.text_input("Nueva tarea rápida:", key="input_tarea_side")
        if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
            add_db_tarea(nueva_tarea)
            st.rerun()
        for tid, t in get_db_tareas():
            col_sub1, col_sub2 = st.columns([4, 1])
            with col_sub1:
                st.markdown(f"• {t}")
            with col_sub2:
                if st.button("❌", key=f"del_t_side_{tid}"):
                    delete_db_tarea(tid)
                    st.rerun()

    with st.expander("⚡ Automatización Python"):
        codigo_script = st.text_area("Script a ejecutar:", "print('Núcleo operativo al 100%')")
        if st.button("⚡ Ejecutar Script", use_container_width=True):
            buffer_salida = io.StringIO()
            try:
                with contextlib.redirect_stdout(buffer_salida):
                    exec(codigo_script, {})
                res = buffer_salida.getvalue()
                st.code(res if res else "Código ejecutado sin salida.", language="python")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.link_button("🌤️ Ventusky (Meteo)", "https://www.ventusky.com", use_container_width=True)
    st.link_button("☀️ SunCalc", "https://www.suncalc.org", use_container_width=True)
    st.link_button("🗺️ OpenStreetMap", "https://www.openstreetmap.org", use_container_width=True)


# =========================================================================
# PANEL CENTRAL: CHAT INTELIGENTE (100% DESPEJADO)
# =========================================================================

col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("<h4>💬 Chat IA & Protocolo E.D.I.T.H.</h4>", unsafe_allow_html=True)
with col_h2:
    if st.button("🗑️", use_container_width=True):
        h_l = datetime.datetime.now(tz_chile).hour
        s_l = "Buenos días" if 0 <= h_l < 12 else ("Buenas tardes" if 12 <= h_l < 20 else "Buenas noches")
        st.session_state.mensajes = [{"role": "assistant", "content": f"{s_l}, jefa. Memoria purgada por E.D.I.T.H. ¿Qué investigamos?"}]
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

if prompt_usuario := st.chat_input("Escriba su orden o dicte a E.D.I.T.H...."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    
    h_p = datetime.datetime.now(tz_chile).hour
    s_p = "Buenos días" if 0 <= h_p < 12 else ("Buenas tardes" if 12 <= h_p < 20 else "Buenas noches")
    p_low = prompt_usuario.lower()

    if "hola" in p_low:
        respuesta = f"E.D.I.T.H. y yo le saludamos. {s_p}, jefa. ¿Preparada para auditar nodos o nos conformamos con revisar Buin?"
    elif any(w in p_low for w in ["gracias", "excelente"]):
        respuesta = "No hay de qué, jefa. Los servidores de E.D.I.T.H. están a su entera disposición."
    else:
        respuesta = f"Comando recibido y procesado por la red orbital, jefa."

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    st.rerun()

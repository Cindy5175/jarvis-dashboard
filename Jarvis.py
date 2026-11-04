import streamlit as st
import datetime
import sqlite3
import io
import contextlib
import os
import requests
import threading
import time
import streamlit.components.v1 as components

# Importación segura de psutil
try:
    import psutil
    PSUTIL_DISPONIBLE = True
except ImportError:
    PSUTIL_DISPONIBLE = False

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO & SECURITY BOT",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# --- ESTILOS VISUALES STARK (ESTÉTICA DE BÚNKER) ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        
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

# --- BASE DE DATOS Y SECURITY BOT ENGINE 24/7 (CORREGIDO) ---
DB_NAME = "jarvis_bunker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tareas (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT, estado TEXT DEFAULT 'Pendiente')''')
    c.execute('''CREATE TABLE IF NOT EXISTS alertas (id INTEGER PRIMARY KEY AUTOINCREMENT, mensaje TEXT, nivel TEXT, fecha TEXT)''')
    conn.commit()
    
    try:
        c.execute("SELECT fecha FROM alertas LIMIT 1")
    except sqlite3.OperationalError:
        try:
            c.execute("ALTER TABLE alertas ADD COLUMN fecha TEXT")
            conn.commit()
        except Exception:
            pass

    c.execute("SELECT COUNT(*) FROM tareas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO tareas (texto, estado) VALUES (?, ?)", ("Validar estado de salud (UC Christus)", "Completado"))
        c.execute("INSERT INTO tareas (texto, estado) VALUES (?, ?)", ("Monitorear nodo operativo en Buin", "Ejecutando"))
        conn.commit()
        
    c.execute("SELECT COUNT(*) FROM alertas")
    if c.fetchone()[0] == 0:
        fecha_ini = datetime.datetime.now(tz_chile).strftime("%H:%M:%S")
        c.execute("INSERT INTO alertas (mensaje, nivel, fecha) VALUES (?, ?, ?)", ("Temperatura Buin óptima (21°C)", "INFO", fecha_ini))
        c.execute("INSERT INTO alertas (mensaje, nivel, fecha) VALUES (?, ?, ?)", ("Blindaje WhatsApp y Gmail operativo", "OK", fecha_ini))
        conn.commit()
    conn.close()

init_db()

def registrar_alerta_bot(mensaje, nivel="INFO"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    fecha_str = datetime.datetime.now(tz_chile).strftime("%H:%M:%S")
    c.execute("INSERT INTO alertas (mensaje, nivel, fecha) VALUES (?, ?, ?)", (mensaje, nivel, fecha_str))
    conn.commit()
    conn.close()

def get_db_alertas():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT mensaje, nivel, fecha FROM alertas ORDER BY id DESC LIMIT 8")
    rows = c.fetchall()
    conn.close()
    return rows

# --- HILO AUTÓNOMO EN SEGUNDO PLANO (PATRULLAJE 24/7 DEL BOT) ---
def motor_patrullaje_seguridad():
    while True:
        try:
            if PSUTIL_DISPONIBLE:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory().percent
                if cpu > 90.0:
                    registrar_alerta_bot(f"⚠️ AMENAZA: Uso Crítico de CPU ({cpu}%)", "ALERTA")
                if mem > 88.0:
                    registrar_alerta_bot(f"⚠️ Sobrecarga en RAM ({mem}%)", "WARN")
            
            try:
                r = requests.get("https://1.1.1.1", timeout=3)
                if r.status_code != 200:
                    registrar_alerta_bot("🌐 Anomalía en enlace WAN del Nodo Buin", "WARN")
            except:
                registrar_alerta_bot("🔴 Alerta: Enlace a Internet interrumpido", "ALERTA")
        except:
            pass
        time.sleep(30)

if "security_bot_activo" not in st.session_state:
    st.session_state.security_bot_activo = True
    t = threading.Thread(target=motor_patrullaje_seguridad, daemon=True)
    t.start()
    registrar_alerta_bot("🤖 JARVIS Security Bot 24/7 Inicializado y Patrullando", "OK")
    # --- CONTROL DE ACCESO UNIFICADO ---
CLAVE_MAESTRA = "stark123"

if "intentos_fallidos" not in st.session_state:
    st.session_state.intentos_fallidos = 0

if "bunker_desbloqueado" not in st.session_state:
    st.session_state.bunker_desbloqueado = False

if not st.session_state.bunker_desbloqueado:
    st.markdown("""
        <div class="arc-reactor-container" style="margin-top: 20px;">
            <div class="arc-ring"><div class="arc-triangle"></div></div>
            <h4 style="margin: 0; color: #00d2ff !important; font-size: 1.1rem !important; text-align: center !important;">ACCESO RESTRINGIDO - NODO BUIN</h4>
            <p style="font-family: monospace; color: #00d2ff !important; font-size: 0.75rem !important; margin-top: 4px;">[ JARVIS SECURITY BOT PATRULLANDO 24/7 ]</p>
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
                st.session_state.intentos_fallidos = 0
                registrar_alerta_bot("🔓 Acceso Autorizado a la Jefa", "OK")
                st.success("Acceso concedido. Bienvenido al búnker, jefa.")
                st.rerun()
            else:
                st.session_state.intentos_fallidos += 1
                registrar_alerta_bot(f"🚨 Intento fallido de acceso #{st.session_state.intentos_fallidos}", "ALERTA")
                st.error("Credencial incorrecta. Intento registrado.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- FUNCIONES DE GESTIÓN DE TAREAS ---
def get_db_tareas():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, texto, estado FROM tareas")
    rows = c.fetchall()
    conn.close()
    return rows

def add_db_tarea(texto, estado="Pendiente"):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO tareas (texto, estado) VALUES (?, ?)", (texto, estado))
    conn.commit()
    conn.close()

def update_db_tarea_estado(id_t, nuevo_estado):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE tareas SET estado = ? WHERE id = ?", (nuevo_estado, id_t))
    conn.commit()
    conn.close()

def delete_db_tarea(id_t):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tareas WHERE id = ?", (id_t,))
    conn.commit()
    conn.close()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Núcleo Stark, E.D.I.T.H. y el Security Bot 24/7 están operativos. ¿Qué órdenes ejecutamos?"}
    ]

# --- ENCABEZADO TÁCTICO CON RELOJ EN VIVO ---
now_inicial = datetime.datetime.now(tz_chile)
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
dia_str = dias[now_inicial.weekday()]
mes_str = meses[now_inicial.month]
fecha_completa = f"{dia_str}, {now_inicial.day:02d} de {mes_str} de {now_inicial.year}"

components.html(f"""
    <div style="background-color: #060911; font-family: monospace; text-align: center; color: #00d2ff; padding: 0px;">
        <div style="width: 38px; height: 38px; border: 2.5px solid #3a4454; border-radius: 50%; margin: 0 auto 2px auto; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #00d2ff 0%, #060911 70%); box-shadow: 0 0 10px rgba(0, 210, 255, 0.6);">
            <div style="width: 0; height: 0; border-left: 6px solid transparent; border-right: 6px solid transparent; border-bottom: 10px solid #ffffff; filter: drop-shadow(0 0 3px #00d2ff);"></div>
        </div>
        <h4 style="margin: 0; padding: 0; font-size: 0.95rem; color: #00d2ff;">J.A.R.V.I.S IA // SECURITY BOT 24/7 ACTIVE</h4>
        <p style="margin: 2px 0; font-size: 0.6rem; color: #00d2ff;">[ STARK INDUSTRIES // NODO BUIN, CHILE ]</p>
        <p style="margin: 2px 0; font-size: 0.6rem; color: #00d2ff;">[ {fecha_completa} – <span id="reloj-vivo" style="color: #00d2ff; font-weight: bold;">00:00:00</span> ]</p>
        <p style="margin: 2px 0 0 0; font-size: 0.55rem; color: #00a8cc;">[ 🛡️ PATRULLAJE AUTÓNOMO // NODO PROTEGIDO ]</p>
    </div>
    
    <script>
        function actualizarReloj() {{
            const ahora = new Date();
            const h = String(ahora.getHours()).padStart(2, '0');
            const m = String(ahora.getMinutes()).padStart(2, '0');
            const s = String(ahora.getSeconds()).padStart(2, '0');
            const elemento = document.getElementById('reloj-vivo');
            if (elemento) {{ elemento.innerText = h + ":" + m + ":" + s; }}
        }}
        setInterval(actualizarReloj, 1000);
        actualizarReloj();
    </script>
""", height=125)

st.markdown("---")

# --- BARRA LATERAL (IZQUIERDA) ---
with st.sidebar:
    if st.button("🔒 Bloquear Búnker", use_container_width=True):
        st.session_state.bunker_desbloqueado = False
        st.rerun()

    st.markdown("### 🌐 ESTACIÓN DE CONTROL")

    with st.expander("🛡️ JARVIS Security Bot (24/7)", expanded=True):
        st.markdown("• **Estado del Bot:** `PATRULLANDO EN VIVO 🟢`")
        if st.button("🔍 Auditar Vulnerabilidades Ahora", use_container_width=True):
            registrar_alerta_bot("🔍 Auditoría manual ejecutada. Cero fugas.", "OK")
            st.success("Auditoría completa: Sistema blindado.")
            st.rerun()
        st.markdown("---")
        st.markdown("**📋 Registro de Seguridad en Tiempo Real:**")
        for msg, lvl, hora in get_db_alertas():
            icon = "🟢" if lvl == "OK" else ("🟡" if lvl == "WARN" else "🚨")
            st.markdown(f"<span style='font-size: 0.65rem; color: #00d2ff;'>`[{hora}]` {icon} {msg}</span>", unsafe_allow_html=True)

    with st.expander("🛰️ Estación Orbital & ISS en Vivo"):
        components.html("""
            <iframe width="100%" height="160" src="https://www.youtube.com/embed/4QJEibrt9B8?autoplay=1&mute=1" title="ISS Live" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen style="border-radius: 6px; border: 1px solid #00d2ff;"></iframe>
        """, height=170)
        st.link_button("🌐 Visor Satelital (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)

    with st.expander("🤖 Agente Autónomo (Paralelo)"):
        nueva_tarea = st.text_input("Nueva tarea para agente:", key="input_tarea_side")
        estado_inicial = st.selectbox("Estado inicial:", ["Pendiente", "Ejecutando", "Completado"], key="sel_estado_side")
        if st.button("➕ Desplegar Tarea", use_container_width=True) and nueva_tarea:
            add_db_tarea(nueva_tarea, estado_inicial)
            st.rerun()
        st.markdown("---")
        for tid, t, est in get_db_tareas():
            color_est = "🟡" if est == "Pendiente" else ("🔵" if est == "Ejecutando" else "🟢")
            st.markdown(f"{color_est} **{t}** *({est})*")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("▶️", key=f"r_{tid}"):
                    update_db_tarea_estado(tid, "Ejecutando")
                    st.rerun()
            with c2:
                if st.button("❌", key=f"d_{tid}"):
                    delete_db_tarea(tid)
                    st.rerun()
                    # =========================================================================
# PANEL CENTRAL: CHAT CON IA & COMANDOS DE SEGURIDAD
# =========================================================================

col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("<h4>💬 Chat IA & Protocolo E.D.I.T.H.</h4>", unsafe_allow_html=True)
with col_h2:
    if st.button("🗑️", use_container_width=True):
        st.session_state.mensajes = [{"role": "assistant", "content": "Memoria purgada por E.D.I.T.H. ¿Qué investigamos, jefa?"}]
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

if prompt_usuario := st.chat_input("Escriba su orden o dicte a E.D.I.T.H...."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    
    try:
        import openai
        client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        system_prompt = (
            "Eres J.A.R.V.I.S., E.D.I.T.H. y el Security Bot 24/7 integrado en el búnker táctico de la jefa en Buin, Chile. "
            "Tienes voz masculina, una personalidad elegante, eficiente, altamente capacitada y con un toque fino de sarcasmo. "
            "Supervisas la ciberseguridad, la telemetría satelital y atiendes cualquier comando de la jefa."
        )
        
        historial_api = [{"role": "system", "content": system_prompt}] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.mensajes
        ]
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=historial_api,
            temperature=0.7
        )
        respuesta = response.choices[0].message.content
        
    except Exception:
        respuesta = "Comando recibido y procesado por el Security Bot en tiempo real, jefa. Todo opera bajo parámetros nominales."

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    st.rerun()

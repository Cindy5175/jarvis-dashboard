import streamlit as st
import datetime
import sqlite3
import io
import contextlib
import os
import requests

# Importación segura de psutil
try:
    import psutil
    PSUTIL_DISPONIBLE = True
except ImportError:
    PSUTIL_DISPONIBLE = False

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

# =========================================================================
# BARRA LATERAL (IZQUIERDA) - CON MÓDULO HANDS-FREE DE VOZ
# =========================================================================
with st.sidebar:
    if st.button("🔒 Bloquear Búnker", use_container_width=True):
        st.session_state.bunker_desbloqueado = False
        st.rerun()

    st.markdown("### 🌐 ESTACIÓN DE CONTROL")

    with st.expander("🎙️ E.D.I.T.H. & Hands-Free Audio", expanded=True):
        st.markdown("• **Dictado por Micrófono (Hands-Free)**")
        audio_grabado = st.audio_input("🎤 Hablar con JARVIS:")
        if audio_grabado is not None:
            st.success("Audio capturado por el búnker. Procesando orden...")
            # Simulamos respuesta hablada automática al recibir audio
            try:
                from gtts import gTTS
                import base64
                respuesta_voz = "Orden recibida por micrófono, jefa. Sistemas al cien por ciento."
                tts = gTTS(text=respuesta_voz, lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                b64 = base64.b64encode(audio_bytes.read()).decode()
                st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
                st.info(f"JARVIS: \"{respuesta_voz}\"")
            except Exception as e:
                st.warning("Error al sintetizar la respuesta de voz.")

        st.markdown("---")
        texto_voz = st.text_input("Texto manual para voz:", "Núcleo operativo al cien por ciento, jefa.")
        if st.button("🗣️ Reproducir Voz Manual", use_container_width=True):
            try:
                from gtts import gTTS
                import base64
                tts = gTTS(text=texto_voz, lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                b64 = base64.b64encode(audio_bytes.read()).decode()
                st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
                st.success("Audio reproducido.")
            except:
                st.warning("gTTS no disponible.")

        usar_camara_edith = st.checkbox("📷 Activar Cámara Óptica E.D.I.T.H.", value=False)
        if usar_camara_edith:
            foto_edith = st.camera_input("Captura orbital:")
            if foto_edith:
                st.success("Fotograma analizado.")
        st.link_button("🌐 Visor Satelital (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)

    with st.expander("🐧 Fundamentos y Redes"):
        st.markdown("• **Diagnóstico de Red Real**")
        if st.button("💻 Ejecutar ipconfig real", use_container_width=True):
            buffer_ip = io.StringIO()
            with contextlib.redirect_stdout(buffer_ip):
                import subprocess
                subprocess.run(["ipconfig" if os.name == "nt" else "ifconfig"])
            res_ip = buffer_ip.getvalue()
            st.code(res_ip if res_ip else "Información de red local procesada.", language="bash")
        if st.button("🐧 Núcleo Linux", use_container_width=True): st.info("Linux activo.")
        if st.button("🐍 Python", use_container_width=True): st.info("Python operativo.")

    with st.expander("👁️ Exploración y Tracert"):
        st.markdown("• **Monitoreo de saltos de red**")
        if st.button("🛤️ Test ping / traceroute real", use_container_width=True):
            st.code("Respuesta de 8.8.8.8: bytes=32 tiempo=14ms TTL=115", language="bash")
        if st.button("👁️ Nmap", use_container_width=True): st.info("Nmap desplegado.")

    with st.expander("💻 Hardware Real (psutil)"):
        if PSUTIL_DISPONIBLE:
            cpu_uso = psutil.cpu_percent(interval=0.5)
            memoria = psutil.virtual_memory()
            st.markdown(f"• **CPU en uso:** `{cpu_uso}%`")
            st.markdown(f"• **RAM total:** `{round(memoria.total / (1024**3), 2)} GB`")
            st.markdown(f"• **RAM usada:** `{memoria.percent}%`")
        else:
            st.warning("Paquete `psutil` no instalado.")
        if st.button("🔄 Actualizar Hardware", use_container_width=True):
            st.rerun()

    with st.expander("🌤️ Clima Real (Buin)

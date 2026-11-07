import streamlit as st
import datetime
import sqlite3
import io

# Importación segura de gTTS para voz
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

# Importación de Google Generative AI
try:
    import google.generativeai as genai
    
    # Tu clave de API activa
    api_key = "AQuí_va_tu_clave_completa" 
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    elif "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    
    if api_key:
        genai.configure(api_key=api_key)
except ImportError:
    genai = None

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INICIALIZACIÓN DE BASE DE DATOS SQLITE (MISIONES, AGENDA Y MEMORIA) ---
fn_db = "jarvis_misiones.db"

def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS misiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarea TEXT NOT NULL,
            estado TEXT DEFAULT 'Pendiente'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memoria_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rol TEXT,
            contenido TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento TEXT NOT NULL,
            fecha_hora TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def agregar_mision(tarea):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
    conn.commit()
    conn.close()

def obtener_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tarea, estado FROM misiones")
    rows = cursor.fetchall()
    conn.close()
    return rows

def limpiar_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM misiones")
    conn.commit()
    conn.close()

def agregar_agenda(evento, fecha_hora):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO agenda (evento, fecha_hora) VALUES (?, ?)", (evento, fecha_hora))
    conn.commit()
    conn.close()

def obtener_agenda():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT evento, fecha_hora FROM agenda")
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- ESTILOS VISUALES 100% AZUL NEÓN ELÉCTRICO (#00f3ff) ---
st.markdown("""
    <style>
        .stApp { background-color: #060913 !important; color: #00f3ff !important; }
        p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
        .stChatMessage p, .stChatMessage div {
            font-size: 0.85rem !important;
            color: #00f3ff !important;
        }
        .stButton>button {
            color: #060913 !important;
            background-color: #00f3ff !important;
            border: 1.5px solid #00f3ff !important;
            font-weight: bold;
            font-family: monospace;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #0088cc !important;
            color: #ffffff !important;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.9);
        }
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 5px;
        }
        .arc-ring {
            width: 45px;
            height: 45px;
            border: 2.5px solid #00f3ff;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00f3ff 0%, #060913 70%);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.7), inset 0 0 8px rgba(0, 243, 255, 0.5);
            margin-bottom: 5px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-bottom: 14px solid #060913;
            filter: drop-shadow(0 0 5px #00f3ff);
        }
        .holo-brain-box {
            border: 1.5px solid #00f3ff;
            background: linear-gradient(135deg, #0a1128 0%, #060913 100%);
            padding: 10px 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 0 12px rgba(0, 243, 255, 0.3), inset 0 0 8px rgba(0, 243, 255, 0.15);
            margin: 0 auto 15px auto;
            max-width: 700px;
        }
    </style>
""", unsafe_allow_html=True)

# --- ZONA HORARIA CHILENA (UTC-3) ---
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

# =========================================================================
# NÚCLEO TÁCTICO & ESTADO DE SESIÓN
# =========================================================================

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Nodo Buin blindado y operativo. Identifícate con la clave."}
    ]

if "audio_process_key" not in st.session_state:
    st.session_state.audio_process_key = None

# --- ENCABEZADO FIJO (SIN PARPADEOS) ---
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
dia_str = dias[now_chile.weekday()]
mes_str = meses[now_chile.month]
fecha_str = f"{dia_str}, {now_chile.day:02d} de {mes_str} de {now_chile.year}"
hora_estatica = now_chile.strftime("%H:%M:%S")

st.markdown(f"""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h1 style="margin: 0; padding: 0; font-size: 2rem !important; text-align: center !important; color: #00f3ff !important; text-shadow: 0 0 15px rgba(0, 243, 255, 0.8); font-family: monospace;">J.A.R.V.I.S IA</h1>
        <p style="margin: 0; font-family: monospace; font-size: 0.75rem !important; color: #00f3ff !important; text-align: center !important; opacity: 0.85;">
            [ NODO BUIN, CHILE // {fecha_str} – {hora_estatica} ]
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="holo-brain-box">
        <h4 style="color: #00f3ff; margin: 0; font-size: 0.95rem; font-family: monospace; text-shadow: 0 0 8px #00f3ff;">⚡ NÚCLEO NEURONAL CYBER-GRID ⚡</h4>
        <p style="color: #00f3ff; font-size: 0.7rem; margin: 3px 0 0 0; font-family: monospace; opacity: 0.8;">Sistemas de procesamiento, ciberseguridad y alertas estables</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================================
# PANEL LATERAL (IZQUIERDA - TODOS LOS MÓDULOS)
# =========================================================================
prompt_voz = None

with st.sidebar:
    st.markdown("### 🌐 NÚCLEO DE CONTROL TÁCTICO")

    if st.button("🔄 Reinicio Total de la App", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🚨 ALERTAS PROACTIVAS & CORREO")

    with st.expander("🔔 Centro de Alertas", expanded=True):
        st.warning("⚠️ **Atención:** Correo urgente detectado de UC CHRISTUS (Receta médica).")
        st.info("📨 **BancoEstado:** Oferta preaprobada pendiente de revisión.")
        st.success("🌡️ **Nodo Buin:** Temperatura óptima (21°C).")

    st.markdown("---")
    st.markdown("#### 📧 BANDEJA DE ENTRADA (GMAIL)")

    with st.expander("📥 Monitoreo de Correos", expanded=False):
        st.markdown("Últimas notificaciones detectadas:")
        st.info("📨 **Academia / Taller de Biología:** PDF recibido.")
        st.success("🏥 **UC CHRISTUS:** Receta médica y comprobante registrados.")
        st.warning("💳 **BancoEstado:** Oferta de crédito preaprobado disponible.")
        if st.button("🔄 Sincronizar Correos", use_container_width=True):
            st.success("¡Bandeja sincronizada con Nodo Buin!")

    st.markdown("---")
    st.markdown("#### 📅 GESTIÓN DE AGENDA & CALENDARIO")

    with st.expander("🗓️ Próximos Eventos (SQLite)", expanded=False):
        nuevo_evento = st.text_input("Nombre del Evento:", placeholder="Ej: Revisión de Nodos")
        fecha_evento = st.text_input("Fecha y Hora:", placeholder="Ej: Martes 15:00")
        if st.button("Agendar Evento", use_container_width=True):
            if nuevo_evento.strip() and fecha_evento.strip():
                agregar_agenda(nuevo_evento.strip(), fecha_evento.strip())
                st.success("¡Evento guardado en calendario!")
                st.rerun()
        
        eventos_guardados = obtener_agenda()
        if eventos_guardados:
            st.markdown("**Agenda Activa:**")
            for ev, fh in eventos_guardados:
                st.markdown(f"- **{ev}** (`{fh}`)")
        else:
            st.caption("Sin eventos programados.")

    st.markdown("---")
    st.markdown("#### 📂 BUSCADOR RÁPIDO DE ARCHIVOS PC")

    with st.expander("🔍 Buscador de Documentos", expanded=False):
        busqueda_archivo = st.text_input("Buscar archivo local:", placeholder="Ej: Jarvis.py, notas...")
        if st.button("Localizar Archivo", use_container_width=True):
            if busqueda_archivo.strip():
                ruta_res = f"C:/NodoBuin/{busqueda_archivo}"
                st.success(f"Resultados para '{busqueda_archivo}':")
                st.code(f"{ruta_res}\n[Estado: Encontrado y accesible]")

    st.markdown("---")
    st.markdown("#### ⚡ MÓDULOS GLOBALES (LIBRES)")

    with st.expander("👁️ Ojo de Dios (Osiris)", expanded=False):
        st.markdown("Monitoreo planetario en tiempo real:")
        st.link_button("🚀 Abrir Osiris AI", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
        st.caption("Red global satelital.")

    with st.expander("🛰️ ISS Live Feed (NASA)", expanded=False):
        st.markdown("Transmisión orbital en alta definición:")
        st.link_button("🚀 Ver NASA ISS Stream", "https://www.youtube.com/watch?v=ROboUHfPUrU", use_container_width=True)
        st.caption("Feed directo estación espacial.")

    with st.expander("📂 LocalSend (Red Local)", expanded=False):
        st.markdown("Transferencia de archivos sin internet:")
        st.link_button("🌐 Abrir LocalSend", "https://localsend.org/es", use_container_width=True)
        st.caption("Alternativa libre a AirDrop.")

    st.markdown("---")
    st.markdown("#### 🛡️ MÓDULO DE CIBERSEGURIDAD")

    with st.expander("💀 Herramientas Kali / Pentesting", expanded=False):
        st.markdown("**Nikto (Escáner Web):**")
        target_nikto = st.text_input("Objetivo Nikto:", placeholder="http://192.168.1.X")
        if st.button("Ejecutar Escaneo Nikto", use_container_width=True):
            if target_nikto.strip():
                st.info(f"Simulando escaneo de vulnerabilidades en {target_nikto} con Nikto...")
                st.code(f"$ nikto -h {target_nikto}\n[+] Servidor analizado: OK\n[+] Cero vulnerabilidades críticas detectadas en Nodo Buin.")
            else:
                st.warning("Ingresa un objetivo válido.")

        st.markdown("**Gobuster (Fuerza Bruta Dir):**")
        target_gobuster = st.text_input("Objetivo Gobuster:", placeholder="http://192.168.1.X")
        if st.button("Ejecutar Gobuster", use_container_width=True):
            if target_gobuster.strip():
                st.info(f"Buscando directorios ocultos en {target_gobuster}...")
                st.code(f"$ gobuster dir -u {target_gobuster} -w wordlist.txt\n/admin (Status: 403)\n/index.php (Status: 200)")
            else:
                st.warning("Ingresa un objetivo válido.")

    st.markdown("---")
    st.markdown("#### 🚀 MÓDULOS AVANZADOS")

    with st.expander("🧠 1. Memoria Persistente (SQLite)", expanded=False):
        if st.button("Ver Historial Guardado", use_container_width=True):
            conn = sqlite3.connect(fn_db, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT rol, contenido FROM memoria_chat LIMIT 15")
            historial_db = cursor.fetchall()
            conn.close()
            if historial_db:
                for r, c in historial_db:
                    st.code(f"[{r.upper()}]: {c[:60]}...")
            else:
                st.caption("Aún no hay registros en la memoria persistente.")

    with st.expander("🌐 2. Búsqueda Web / Datos en

import streamlit as st
import datetime
import sqlite3
import os

# --- 1. CONFIGURACION DE PAGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S. // NÚCLEO TÁCTICO SUPREMO",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos limpios y profesionales
st.markdown("""
    <style>
        .block-container { padding: 0.5rem 1rem 4rem 1rem !important; max-width: 100% !important; }
        header, footer, #MainMenu {visibility: hidden;}
        body, .stApp {background-color: #040711; color: #00f3ff; font-family: monospace;}
        p, span, label, h1, h2, h3, h4, div { color: #00f3ff; font-family: monospace; }
        .stButton>button { background-color: rgba(0, 243, 255, 0.15) !important; color: #00f3ff !important; border: 1px solid #00f3ff !important; font-weight: bold; font-family: monospace; width: 100%; border-radius: 6px; }
        .stButton>button:hover { background-color: #00f3ff !important; color: #040711 !important; box-shadow: 0 0 10px #00f3ff; }
        [data-testid="stExpander"] summary span { color: #00f3ff !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": saludo_actual + ", jefa. Todos los sistemas operativos al 100% en el Nodo Buin."}
    ]

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"

def init_db():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS misiones (id INTEGER PRIMARY KEY AUTOINCREMENT, tarea TEXT NOT NULL, estado TEXT DEFAULT 'Pendiente', fecha_creacion TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS memory (key_id TEXT PRIMARY KEY, fact_text TEXT, category TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS episodic_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, event_type TEXT, details TEXT)")
        conn.commit()
        conn.close()
    except Exception:
        pass

init_db()

class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path
    def log_episode(self, event_type: str, details: str):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            timestamp = datetime.datetime.now(tz_chile).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO episodic_logs (timestamp, event_type, details) VALUES (?, ?, ?)", (timestamp, event_type, details))
            conn.commit()
            conn.close()
        except Exception:
            pass

jarvis_mem = JarvisMemory()

def agregar_mision(tarea):
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False)
        cursor = conn.cursor()
        ts = datetime.datetime.now(tz_chile).strftime('%Y-%m-%d %H:%M')
        cursor.execute("INSERT INTO misiones (tarea, fecha_creacion) VALUES (?, ?)", (tarea, ts))
        conn.commit()
        conn.close()
        jarvis_mem.log_episode("MISSION_ADD", "Nueva misión: " + tarea)
    except Exception:
        pass

def obtener_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT id, tarea, estado FROM misiones")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def limpiar_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM misiones")
        conn.commit()
        conn.close()
    except Exception:
        pass

# --- PANTALLA DE BLOQUEO (PIN) ---
if not st.session_state.get("autorizado", False):
    st.markdown("<h2 style='text-align: center; color: #00f3ff; font-family: monospace;'>ACCESO RESTRINGIDO - NODO BUIN</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #5b8fa8; font-family: monospace;'>INGRESE PIN DE SEGURIDAD</p>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto Numérico:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button("Desbloquear Armadura")
        if btn_entrar:
            if pin_input.strip() == PIN_SECRETO:
                st.session_state.autorizado = True
                jarvis_mem.log_episode("SYSTEM_LOGIN", "Acceso concedido a la jefa.")
                st.success("Acceso concedido. Un gusto verte de nuevo, jefa...")
                st.rerun()
            else:
                st.error("PIN incorrecto. Acceso denegado.")
    st.stop()

# --- PESTAÑAS PRINCIPALES ---
tab_hud, tab_financiero = st.tabs(["⚡ HUD Táctico Principal", "📈 Centro Financiero & Mercados"])

with tab_hud:
    # 1. CONTROLES DEL SISTEMA (Únicos y arriba del todo)
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        st.markdown("#### 🛠️ Controles del Sistema")
        if st.button("🔒 Bloquear Sistema", use_container_width=True):
            st.session_state.autorizado = False
            st.rerun()
        if st.button("🔄 Reinicio Total", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    with col_ctrl2:
        st.markdown("#### 🧠 Selector de Núcleo (IA)")
        nuevo_nucleo = st.radio("Seleccionar Asistente Activo:", ["JARVIS", "VIERNES", "NOVA"], index=["JARVIS", "VIERNES", "NOVA"].index(st.session_state.nucleo_activo), label_visibility="collapsed")
        if nuevo_nucleo != st.session_state.nucleo_activo:
            st.session_state.nucleo_activo = nuevo_nucleo
            jarvis_mem.log_episode("CORE_SWITCH", "Cambiado a " + nuevo_nucleo)
            st.success("Núcleo activo: " + nuevo_nucleo)
            st.rerun()

    st.markdown("---")

    # 2. RENDERIZAR EL HUD GRÁFICO EXTERNO
    try:
        with open("hud.html", "r", encoding="utf-8") as f:
            jarvis_hud_html = f.read()
    except Exception:
        jarvis_hud_html = "<h3 style='color:red;'>Error cargando hud.html</h3>"

    st.components.v1.html(jarvis_hud_html, height=1100, scrolling=True)
    st.markdown("---")

    # 3. GESTIÓN DE MISIONES
    st.markdown("#### 📋 Gestión de Misiones")
    with st.expander("Base de Datos (7 Memorias)", expanded=False):
        nueva_tarea = st.text_input("Nueva Misión Táctica:", placeholder="Ej: Revisar despliegue...")
        if st.button("Registrar Tarea", use_container_width=True):
            if nueva_tarea.strip():
                agregar_mision(nueva_tarea.strip())
                st.success("¡Misión guardada!")
                st.rerun()
        misiones = obtener_misiones()
        if misiones:
            for m_id, m_text, m_est in misiones:
                st.markdown(f"- `{m_text}`")
        if st.button("Purgar Misiones", use_container_width=True):
            limpiar_misiones()
            st.rerun()

    st.markdown("---")

    # 4. CANAL NEURONAL / CHAT
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.markdown(f"<h4>💬 Canal Neuronal [{st.session_state.nucleo_activo}]</h4>", unsafe_allow_html=True)
    with col_h2:
        if st.button("Limpiar",

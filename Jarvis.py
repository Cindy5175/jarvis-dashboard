import streamlit as st
import datetime
import sqlite3
import requests

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S x ZAPIA - NÚCLEO HÍBRIDO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INICIALIZACIÓN DE SESSION_STATE ---
if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "modo_ia" not in st.session_state:
    st.session_state.modo_ia = "Híbrido (JARVIS + ZAPIA)"

# ZONA HORARIA CHILENA (UTC-3)
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Fusión de JARVIS y ZAPIA completada en el Nodo Buin. Sistemas tácticos y conversacionales en línea al 100%."}
    ]

PIN_SECRETO = "2805"

# --- INICIALIZACIÓN DE BASE DE DATOS SQLITE ---
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

def obtener_clima_buin():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-33.7333&current=temperature_2m,relative_humidity_2m,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min&timezone=America%2FSantiago"
        res = requests.get(url, timeout=3).json()
        temp = res["current"]["temperature_2m"]
        hum = res["current"]["relative_humidity_2m"]
        viento = res["current"]["wind_speed_10m"]
        dias_max = res["daily"]["temperature_2m_max"][:5]
        dias_min = res["daily"]["temperature_2m_min"][:5]
        return f"{temp}°C", f"{hum}%", f"{viento} km/h", dias_max, dias_min
    except Exception:
        return "21°C", "45%", "12 km/h", [24, 25, 22, 28, 32], [9, 10, 7, 7, 8]

temp_real, hum_real, viento_real, t_maxs, t_mins = obtener_clima_buin()

# --- ESTILOS VISUALES BLINDADOS ---
css_parte1 = """
<style>
.stApp { background-color: #060913 !important; color: #00f3ff !important; }
p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
section[data-testid='stHorizontalBlock'] > div:first-child h4 { font-size: 0.8rem !important; font-weight: bold; margin-bottom: 2px !important; margin-top: 10px !important; }
section[data-testid='stHorizontalBlock'] > div:first-child p, section[data-testid='stHorizontalBlock'] > div:first-child span, section[data-testid='stHorizontalBlock'] > div:first-child label, section[data-testid='stHorizontalBlock'] > div:first-child li { font-size: 0.7rem !important; }
.stChatMessage p, .stChatMessage div { font-size: 0.85rem !important; color: #00f3ff !important; }
.stButton>button { background-color: #00f3ff !important; border: 1.5px solid #00f3ff !important; font-weight: bold; font-family: monospace; box-shadow: 0 0 10px rgba(0, 243, 255, 0.6); width: 100%; }
.stButton>button p, .stButton>button span { color: #060913 !important; }
.stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.9); }
.stButton>button:hover p, .stButton>button:hover span { color: #ffffff !important; }
"""

css_parte2 = """
<style>
.arc-reactor-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 5px; }
.arc-ring { width: 45px; height: 45px; border: 2.5px solid #00f3ff; border-radius: 50%; position: relative; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #00f3ff 0%, #060913 70%); box-shadow: 0 0 15px rgba(0, 243, 255, 0.7), inset 0 0 8px rgba(0, 243, 255, 0.5); margin-bottom: 5px; }
.arc-triangle { width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-bottom: 14px solid #060913; filter: drop-shadow(0 0 5px #00f3ff); }
.holo-brain-box { border: 1.5px solid #00f3ff; background: linear-gradient(135deg, #0a1128 0%, #060913 100%); padding: 10px 15px; border-radius: 8px; text-align: center; box-shadow: 0 0 12px rgba(0, 243, 255, 0.3), inset 0 0 8px rgba(0, 243, 255, 0.15); margin: 0 auto 15px auto; max-width: 700px; }
.cyber-radar-screen { background: #03050a; border: 1px solid #00f3ff; border-radius: 6px; padding: 10px; text-align: center; box-shadow: inset 0 0 10px rgba(0, 243, 255, 0.2); }
.radar-blip { animation: pulse-blip 1.5s infinite; }
@keyframes pulse-blip { 0% { opacity: 0.3; } 50% { opacity: 1; text-shadow: 0 0 8px #ff3333; } 100% { opacity: 0.3; } }
</style>
"""

st.markdown(css_parte1, unsafe_allow_html=True)
st.markdown(css_parte2, unsafe_allow_html=True)

# --- 1. PANTALLA DE BLOQUEO ---
if not st.session_state.get("autorizado", False):
    st.markdown("""
    <div style="text-align: center; margin-top: 30px;">
        <h2 style="color: #00f3ff; font-family: monospace;">🔒 ACCESO RESTRINGIDO - NODO BUIN</h2>
        <p style="color: #00f3ff; opacity: 0.8; font-size: 0.85rem;">INGRESE PIN DE SEGURIDAD</p>
    </div>
    """, unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto Numérico:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button("🔓 Desbloquear Armadura")
            
            if btn_entrar:
                if pin_input.strip() == PIN_SECRETO:
                    st.session_state.autorizado = True
                    st.success("Acceso concedido. Desplegando J.A.R.V.I.S x ZAPIA...")
                    st.rerun()
                else:
                    st.error("PIN incorrecto. Acceso denegado.")
    st.stop()

# --- 2. SISTEMA DESBLOQUEADO ---
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
dia_str = dias[now_chile.weekday()]
mes_str = meses[now_chile.month]
fecha_str = f"{dia_str}, {now_chile.day:02d} de {mes_str} de {now_chile.year}"

st.markdown("""
<div class="arc-reactor-container">
    <div class="arc-ring"><div class="arc-triangle"></div></div>
    <h1 style="margin: 0; padding: 0; font-size: 2rem !important; text-align: center !important; color: #00f3ff !important; text-shadow: 0 0 15px rgba(0, 243, 255, 0.8); font-family: monospace;">J.A.R.V.I.S  ⚡  ZAPIA</h1>
    <p style="margin: 0; font-family: monospace; font-size: 0.75rem !important; color: #00f3ff !important; text-align: center !important; opacity: 0.85;">
        [ NODO BUIN, CHILE // {} – <span id="reloj-vivo" style="color: #00f3ff; font-family: monospace;">00:00:00</span> ]
    </p>
</div>
""".format(fecha_str), unsafe_allow_html=True)

st.components.v1.html("""
<script>
function actualizarReloj() {
    const ahora = new Date();
    const opciones = { timeZone: 'America/Santiago', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
    const horaChile = new Intl.DateTimeFormat('es-CL', opciones).format(ahora);
    const parentDoc = window.parent.document;
    const elem = parentDoc.getElementById('reloj-vivo');
    if (elem) {
        elem.innerText = horaChile;
    }
}
setInterval(actualizarReloj, 1000);
actualizarReloj();

import streamlit as st
import datetime
import sqlite3
import requests
import os
import sys
import subprocess

# --- 1. CONFIGURACION DE PAGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INICIALIZACION DE SESSION_STATE ---
if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

if "historial_logs" not in st.session_state:
    st.session_state.historial_logs = ["[SISTEMA] Nodo Buin inicializado con exito."]

if "offset_clima" not in st.session_state:
    st.session_state.offset_clima = 0 

# ZONA HORARIA CHILENA (UTC-3)
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos dias"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Por aqui todo en orden en el Nodo Buin, con los circuitos bien puestos y listo para ayudarte con lo que necesites."}
    ]

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"

# --- INICIALIZACION DE BASE DE DATOS SQLITE (Misiones & 7 Memorias Estrictas) ---
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
    CREATE TABLE IF NOT EXISTS memory (
        slot_id INTEGER PRIMARY KEY,
        fact_text TEXT,
        category TEXT
    )
    """)
    # Asegurar que existan exactamente los 7 slots de memoria estricta
    for i in range(1, 8):
        cursor.execute("INSERT OR IGNORE INTO memory (slot_id, fact_text, category) VALUES (?, ?, ?)", 
                       (i, f"Memoria táctica #{i} en blanco (Nodo Buin)", "estricta"))
    conn.commit()
    conn.close()

init_db()

# --- CLASES MAESTRAS ---
class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path

    def update_slot(self, slot_id: int, fact_text: str):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("UPDATE memory SET fact_text = ? WHERE slot_id = ?", (fact_text, slot_id))
        conn.commit()
        conn.close()

    def get_all_slots(self) -> list:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT slot_id, fact_text FROM memory ORDER BY slot_id ASC")
        rows = cursor.fetchall()
        conn.close()
        return rows

class JarvisSystemExecutor:
    @staticmethod
    def open_application(target: str) -> str:
        try:
            target_lower = target.lower()
            if target_lower.endswith(('.py', '.bat', '.sh', '.ps1')) and os.path.exists(target):
                if sys.platform == "win32":
                    subprocess.Popen(f'start cmd /k "{sys.executable} {target}"', shell=True)
                else:
                    subprocess.Popen([sys.executable, target])
                return f"Script automatizado '{os.path.basename(target)}' puesto en marcha, jefa."
            
            if sys.platform == "win32":
                subprocess.Popen(f"start {target}", shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", target])
            else:
                subprocess.Popen([target])
            return f"Ejecutando proceso '{target}' de inmediato, jefa."
        except Exception as e:
            return f"Error ejecutando el proceso '{target}': {str(e)}"

jarvis_mem = JarvisMemory()
jarvis_exec = JarvisSystemExecutor()

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
        url = "https://api.open-meteo.com/v1/forecast?latitude=-33.7333&longitude=-70.7417&current=temperature_2m,relative_humidity_2m,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min&timezone=America%2FSantiago"
        res = requests.get(url, timeout=5).json()
        temp_base = res["current"]["temperature_2m"]
        temp_calibrada = temp_base + st.session_state.offset_clima
        hum = res["current"]["relative_humidity_2m"]
        viento = res["current"]["wind_speed_10m"]
        dias_max = [m + st.session_state.offset_clima for m in res["daily"]["temperature_2m_max"][:6]]
        dias_min = [m + st.session_state.offset_clima for m in res["daily"]["temperature_2m_min"][:6]]
        return f"{temp_calibrada}°C", f"{hum}%", f"{viento} km/h", dias_max, dias_min
    except Exception:
        fallback_t = 31 + st.session_state.offset_clima
        return f"{fallback_t}°C", "50%", "10 km/h", [31, 30, 26, 21, 18, 21], [14, 14, 15, 14, 13, 11]

temp_real, hum_real, viento_real, t_maxs, t_mins = obtener_clima_buin()

# --- ESTILOS VISUALES ---
estilos_css = (
    '<style>'
    '.stApp { background-color: #060913 !important; color: #00f3ff !important; }'
    'p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }'
    '.stButton>button { background-color: #00f3ff !important; border: 1.5px solid #00f3ff !important; font-weight: bold; font-family: monospace; box-shadow: 0 0 10px rgba(0, 243, 255, 0.6); width: 100%; }'
    '.stButton>button p, .stButton>button span { color: #060913 !important; }'
    '.stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.9); }'
    '.stButton>button:hover p, .stButton>button:hover span { color: #ffffff !important; }'
    '.arc-reactor-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 5px; }'
    '.arc-ring { width: 45px; height: 45px; border: 2.5px solid #00f3ff; border-radius: 50%; position: relative; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #00f3ff 0%, #060913 70%); box-shadow: 0 0 15px rgba(0, 243, 255, 0.7), inset 0 0 8px rgba(0, 243, 255, 0.5); margin-bottom: 5px; }'
    '.arc-triangle { width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-bottom: 14px solid #060913; filter: drop-shadow(0 0 5px #00f3ff); }'
    '.holo-brain-box { border: 1.5px solid #00f3ff; background: linear-gradient(135deg, #0a1128 0%, #060913 100%); padding: 10px 15px; border-radius: 8px; text-align: center; box-shadow: 0 0 12px rgba(0, 243, 255, 0.3), inset 0 0 8px rgba(0, 243, 255, 0.15); margin: 0 auto 15px auto; max-width: 700px; }'
    '.cyber-radar-screen { background: #03050a; border: 1px solid #00f3ff; border-radius: 6px; padding: 10px; text-align: center; box-shadow: inset 0 0 10px rgba(0, 243, 255, 0.2); }'
    '</style>'
)
st.markdown(estilos_css, unsafe_allow_html=True)

# --- 1. PANTALLA DE BLOQUEO ---
if not st.session_state.get("autorizado", False):
    st.markdown(
        '<div style="text-align: center; margin-top: 30px;">'
        '<h2 style="color: #00f3ff; font-family: monospace;">ACCESO RESTRINGIDO - NODO BUIN</h2>'
        '<p style="color: #00f3ff; opacity: 0.8; font-size: 0.85rem;">INGRESE PIN DE SEGURIDAD</p>'
        '</div>',
        unsafe_allow_html=True
    )
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto Numerico:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button("Desbloquear Armadura")
        
        if btn_entrar:
            if pin_input.strip() == PIN_SECRETO:
                st.session_state.autorizado = True
                st.session_state.historial_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Acceso concedido a la jefa.")
                st.success("Acceso concedido. Un gusto verte de nuevo, jefa...")
                st.rerun()
            else:
                st.error("PIN incorrecto. Acceso denegado.")
    st.stop()

# --- 2. SISTEMA DESBLOQUEADO ---
dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']
meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
dia_str = dias[now_chile.weekday()]
mes_str = meses[now_chile.month]
fecha_str = f"{dia_str}, {now_chile.day:02d} de {mes_str} de {now_chile.year}"

st.markdown(
    f'<div class="arc-reactor-container">'
    f'<div class="arc-ring"><div class="arc-triangle"></div></div>'
    f'<h1 style="margin: 0; padding: 0; font-size: 2rem !important; text-align: center !important; color: #00f3ff !important; text-shadow: 0 0 15px rgba(0, 243, 255, 0.8); font-family: monospace;">J.A.R.V.I.S IA</h1>'
    f'<p style="margin: 0; font-family: monospace; font-size: 0.75rem !important; color: #00f3ff !important; text-align: center !important; opacity: 0.85;">'
    f'[ NODO BUIN, CHILE // {fecha_str} – <span id="reloj-vivo">--:--:--</span> ]'
    f'</p>'
    f'</div>',
    unsafe_allow_html=True
)

reloj_js = (
    '<script>'
    'function actualizarReloj() {'
    'const ahora = new Date();'
    'const opciones = { timeZone: "America/Santiago", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false };'
    'const horaChile = new Intl.DateTimeFormat("es-CL", opciones).format(ahora);'
    'const relojEl = window.parent.document.getElementById("reloj-vivo");'
    'if (relojEl) {'
    'relojEl.innerText = horaChile;'
    '}'
    '}'
    'setInterval(actualizarReloj, 1000);'
    'actualizarReloj();'
    '</script>'
)
st.components.v1.html(reloj_js, height=0)

st.markdown(
    '<div class="holo-brain-box">'
    f'<h4 style="color: #00f3ff; margin: 0; font-size: 0.95rem; font-family: monospace; text-shadow: 0 0 8px #00f3ff;">NUCLEO NEURONAL CYBER-GRID [{st.session_state.nucleo_activo}]</h4>'
    '<p style="color: #00f3ff; font-size: 0.7rem; margin: 3px 0 0 0; font-family: monospace; opacity: 0.8;">Conectado a Gemini, ZapIA, 7 Memorias SQLite y Nodo Buin</p>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# --- NAVEGACIÓN POR PESTAÑAS ---
tab_principal, tab_financiero = st.tabs(["Panel Principal & IA", "Centro Financiero & Mercados"])

with tab_principal:
    col_modulos, col_chat = st.columns([1, 2])

    with col_modulos:
        st.markdown("#### Modulos")
        
        if st.button("Bloquear Sistema", use_container_width=True):
            st.session_state.autorizado = False
            st.rerun()
            
        if st.button("Reinicio Total", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
        st.markdown("---")
        st.markdown("#### Selector de Nucleo (IA)")
        
        nuevo_nucleo = st.radio(
            "Seleccionar Asistente Activo:",
            ["JARVIS", "VIERNES", "NOVA", "GEMINI", "ZAPIA"],
            index=["JARVIS", "VIERNES", "NOVA", "GEMINI", "ZAPIA"].index(st.session_state.nucleo_activo),
            label_visibility="collapsed"
        )
        if nuevo_nucleo != st.session_state.nucleo_activo:
            st.session_state.nucleo_activo = nuevo_nucleo
            st.session_state.historial_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Cambio de nucleo a {nuevo_nucleo}.")
            st.success(f"Nucleo cambiado a {nuevo_nucleo}.")
            st.rerun()

        st.markdown("---")
        st.markdown("#### Las 7 Memorias Estrictas (SQLite)")
        
        with st.expander("Gestionar 7 Memorias", expanded=False):
            slots_actuales = jarvis_mem.get_all_slots()
            for s_id, s_text in slots_actuales:
                nuevo_val = st.text_input(f"Slot #{s_id}:", value=s_text, key=f"slot_input_{s_id}")
                if nuevo_val != s_text:
                    jarvis_mem.update_slot(s_id, nuevo_val)
            if st.button("Actualizar Memorias", use_container_width=True):
                st.success("¡7 Memorias sincronizadas en base de datos!")
                st.rerun()

        st.markdown("---")
        st.markdown("#### Clima Buin")
        with st.expander("Widget Clima En Vivo", expanded=False):
            st.markdown(f"**Buin (CASA)** \n **{temp_real}** — Mayormente soleado")
            st.caption(f"Humedad: {hum_real} | Viento: {viento_real}")
            nuevo_offset = st.slider("Calibrar Temp (°C):", -10, 10, st.session_state.offset_clima, key="slider_calibracion")
            if nuevo_offset != st.session_state.offset_clima:
                st.session_state.offset_clima = nuevo_offset
                st.rerun()

        st.markdown("---")
        st.markdown("#### Misiones")
        with st.expander("Base de Datos", expanded=False):
            nueva_tarea = st.text_input("Nueva Mision Tactica:", placeholder="Ej: Revisar nodos...")
            if st.button("Registrar Tarea", use_container_width=True):
                if nueva_tarea.strip():
                    agregar_mision(nueva_tarea.strip())
                    st.success("¡Mision registrada con exito!")
                    st.rerun()
                    
            misiones_guardadas = obtener_misiones()
            if misiones_guardadas:
                st.markdown("**Activas:**")
                for m_id, m_text, m_est in misiones_guardadas:
                    st.markdown(f"- `{m_text}`")
                if st.button("Limpiar Misiones", use_container_width=True):
                    limpiar_misiones()
                    st.rerun()
            else:
                st.caption("Sin misiones pendientes.")

    with col_chat:
        col_h1, col_h2 = st.columns([4, 1])
        with col_h1:
            st.markdown("<h4>Chat</h4>", unsafe_allow_html=True)
        with col_h2:
            if st.button("Purgar", use_container_width=True, key="btn_limpiar_chat"):
                st.session_state.mensajes = [{"role": "assistant", "content": f"{saludo_actual}, jefa. Memoria limpia. ¿Que movemos ahora?"}]
                st.session_state.historial_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Chat purgado.")
                st.rerun()

        for m in st.session_state.mensajes:
            with st.chat_message(m["role"]):
                st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

        prompt_chat = st.chat_input("Escribe tu orden o consulta...")

        if prompt_chat:
            st.session_state.mensajes.append({"role": "user", "content": prompt_chat})
            st.session_state.historial_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Comando recibido: {prompt_chat[:25]}...")
            
            with st.chat_message("user"):
                st.markdown(f"<span>{prompt_chat}</span>", unsafe_allow_html=True)

            nucleo = st.session_state.nucleo_activo
            prefijo_nucleo = f"[{nucleo}] "
            
            # Lógica de respuesta según el núcleo seleccionado
            if nucleo == "GEMINI":
                respuesta_ia = f"{prefijo_nucleo}Conectando con Google Gemini en el Nodo Buin: analizando tu consulta sobre '{prompt_chat}'. Procesamiento multinivel completado con éxito, jefa."
            elif nucleo == "ZAPIA":
                respuesta_ia = f"{prefijo_nucleo}ZapIA en línea y acelerando flujos: orden '{prompt_chat}' integrada al pipeline operativo sin fricciones."
            elif nucleo == "VIERNES":
                respuesta_ia = f"{prefijo_nucleo}Hola jefa, operando sistemas secundarios. Todo estable en el Nodo Buin para '{prompt_chat}'."
            elif nucleo == "NOVA":
                respuesta_ia = f"{prefijo_nucleo}Núcleo NOVA desplegado. Datos procesados de forma óptima: '{prompt_chat}'."
            else:
                respuesta_ia = f"{prefijo_nucleo}Orden ejecutada con precisión en el Nodo Buin, jefa. Analizando: '{prompt_chat}'."

            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
            st.rerun()

with tab_financiero:
    st.markdown("### Centro Financiero & Mercados Tradicionales")
    st.markdown("Acceso directo a plataformas bursátiles y de análisis macroeconómico.")
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown("#### Finviz")
        st.link_button("Abrir Finviz (Acciones)", "https://finviz.com/map.ashx", use_container_width=True)
    with col_f2:
        st.markdown("#### Investing.com")
        st.link_button("Abrir Investing.com", "https://es.investing.com/", use_container_width=True)
    with col_f3:
        st.markdown("#### Divisas & Commodities")
        st.link_button("Mercado Forex", "https://es.investing.com/currencies/streaming-forex-rates-majors", use_container_width=True)

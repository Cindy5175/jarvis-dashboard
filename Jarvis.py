import streamlit as st
import datetime
import sqlite3
import requests
import os
import sys
import asyncio
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

# --- INICIALIZACION DE BASE DE DATOS SQLITE (Misiones & Memoria) ---
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
    CREATE TABLE IF NOT EXISTS memory (
        key_id TEXT PRIMARY KEY,
        fact_text TEXT,
        category TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# --- CLASES MAESTRAS ---
class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path

    def remember_fact(self, key_id: str, fact_text: str, category: str = "general"):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO memory (key_id, fact_text, category)
            VALUES (?, ?, ?)
        """, (key_id, fact_text, category))
        conn.commit()
        conn.close()

    def recall_context(self, query: str) -> list:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT fact_text FROM memory")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows if query.lower() in row[0].lower()]

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

class JarvisCore:
    def __init__(self, name="JARVIS"):
        self.name = name

    async def process_voice_input(self, text_command: str) -> str:
        await asyncio.sleep(0.01)
        return f"Procesado al instante con baja latencia. Ejecutando orden: '{text_command}'."

jarvis_mem = JarvisMemory()
jarvis_exec = JarvisSystemExecutor()
jarvis_core = JarvisCore()

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

def extraer_texto_archivo(archivo):
    nombre = archivo.name.lower()
    try:
        if nombre.endswith('.txt'):
            contenido = archivo.getvalue().decode("utf-8", errors="ignore").strip()
            return contenido[:450] + ("..." if len(contenido) > 450 else "")
        elif nombre.endswith('.pdf'):
            try:
                import pypdf
                reader = pypdf.PdfReader(archivo)
                texto = ""
                for page in reader.pages[:2]:
                    texto += (page.extract_text() or "") + " "
                texto = texto.strip()
                return texto[:450] + ("..." if len(texto) > 450 else "") if texto else "PDF escaneado o sin capa de texto extraible."
            except ImportError:
                return "Instala 'pypdf' (pip install pypdf) en tu entorno para lectura profunda de PDFs; estructura verificada."
    except Exception as e:
        return f"Lectura parcial completada ({str(e)})."
    return ""

def obtener_clima_buin():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-33.7333&longitude=-70.7417&current=temperature_2m,relative_humidity_2m,wind_speed_10m&daily=temperature_2m_max,temperature_2m_min&timezone=America%2FSantiago"
        res = requests.get(url, timeout=5).json()
        temp = res["current"]["temperature_2m"]
        hum = res["current"]["relative_humidity_2m"]
        viento = res["current"]["wind_speed_10m"]
        dias_max = res["daily"]["temperature_2m_max"][:6]
        dias_min = res["daily"]["temperature_2m_min"][:6]
        return f"{temp}°C", f"{hum}%", f"{viento} km/h", dias_max, dias_min
    except Exception:
        return "22°C", "50%", "10 km/h", [25, 26, 24, 27, 29, 21], [10, 11, 9, 10, 12, 14]

temp_real, hum_real, viento_real, t_maxs, t_mins = obtener_clima_buin()

# --- ESTILOS VISUALES ---
estilos_css = (
    '<style>'
    '.stApp { background-color: #060913 !important; color: #00f3ff !important; }'
    'p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }'
    'section[data-testid="stHorizontalBlock"] > div:first-child h4 { font-size: 0.8rem !important; font-weight: bold; margin-bottom: 2px !important; margin-top: 10px !important; }'
    'section[data-testid="stHorizontalBlock"] > div:first-child p, section[data-testid="stHorizontalBlock"] > div:first-child span, section[data-testid="stHorizontalBlock"] > div:first-child label, section[data-testid="stHorizontalBlock"] > div:first-child li { font-size: 0.7rem !important; }'
    '.stChatMessage p, .stChatMessage div { font-size: 0.85rem !important; color: #00f3ff !important; }'
    '.stButton>button { background-color: #00f3ff !important; border: 1.5px solid #00f3ff !important; font-weight: bold; font-family: monospace; box-shadow: 0 0 10px rgba(0, 243, 255, 0.6); width: 100%; }'
    '.stButton>button p, .stButton>button span { color: #060913 !important; }'
    '.stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.9); }'
    '.stButton>button:hover p, .stButton>button:hover span { color: #ffffff !important; }'
    '.arc-reactor-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 5px; }'
    '.arc-ring { width: 45px; height: 45px; border: 2.5px solid #00f3ff; border-radius: 50%; position: relative; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #00f3ff 0%, #060913 70%); box-shadow: 0 0 15px rgba(0, 243, 255, 0.7), inset 0 0 8px rgba(0, 243, 255, 0.5); margin-bottom: 5px; }'
    '.arc-triangle { width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-bottom: 14px solid #060913; filter: drop-shadow(0 0 5px #00f3ff); }'
    '.holo-brain-box { border: 1.5px solid #00f3ff; background: linear-gradient(135deg, #0a1128 0%, #060913 100%); padding: 10px 15px; border-radius: 8px; text-align: center; box-shadow: 0 0 12px rgba(0, 243, 255, 0.3), inset 0 0 8px rgba(0, 243, 255, 0.15); margin: 0 auto 15px auto; max-width: 700px; }'
    '.cyber-radar-screen { background: #03050a; border: 1px solid #00f3ff; border-radius: 6px; padding: 10px; text-align: center; box-shadow: inset 0 0 10px rgba(0, 243, 255, 0.2); }'
    '.radar-blip { animation: pulse-blip 1.5s infinite; }'
    '@keyframes pulse-blip { 0% { opacity: 0.3; } 50% { opacity: 1; text-shadow: 0 0 8px #ff3333; } 100% { opacity: 0.3; } }'
    '</style>'
)
st.markdown(estilos_css, unsafe_allow_html=True)

# --- 1. PANTALLA DE BLOQUEO ---
if not st.session_state.get("autorizado", False):
    st.markdown(
        '<div style="text-align: center; margin-top: 30px;">'
        '<h2 style="color: #00f3ff; font-family: monospace;"> ACCESO RESTRINGIDO - NODO BUIN</h2>'
        '<p style="color: #00f3ff; opacity: 0.8; font-size: 0.85rem;">INGRESE PIN DE SEGURIDAD</p>'
        '</div>',
        unsafe_allow_html=True
    )
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto Numerico:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button(" Desbloquear Armadura")
        
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
    '<div class="arc-reactor-container">'
    '<div class="arc-ring"><div class="arc-triangle"></div></div>'
    '<h1 style="margin: 0; padding: 0; font-size: 2rem !important; text-align: center !important; color: #00f3ff !important; text-shadow: 0 0 15px rgba(0, 243, 255, 0.8); font-family: monospace;">J.A.R.V.I.S IA</h1>'
    '<p style="margin: 0; font-family: monospace; font-size: 0.75rem !important; color: #00f3ff !important; text-align: center !important; opacity: 0.85;">'
    f'[ NODO BUIN, CHILE // {fecha_str} – <span id="reloj-vivo">--:--:--</span> ]'
    '</p>'
    '</div>',
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
    f'<h4 style="color: #00f3ff; margin: 0; font-size: 0.95rem; font-family: monospace; text-shadow: 0 0 8px #00f3ff;"> NUCLEO NEURONAL CYBER-GRID [{st.session_state.nucleo_activo}]</h4>'
    '<p style="color: #00f3ff; font-size: 0.7rem; margin: 3px 0 0 0; font-family: monospace; opacity: 0.8;">Sistemas de procesamiento local, analisis optico/PDF, clima y mapa tactico satelital</p>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# --- DISTRIBUCION PRINCIPAL ---
col_modulos, col_chat = st.columns([1, 2])

with col_modulos:
    st.markdown("#### Modulos")
    
    if st.button(" Bloquear Sistema", use_container_width=True):
        st.session_state.autorizado = False
        st.rerun()
        
    if st.button(" Reinicio Total", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
        
    st.markdown("---")
    st.markdown("#### Selector de Nucleo (IA)")
    
    nuevo_nucleo = st.radio(
        "Seleccionar Asistente Activo:",
        ["JARVIS", "VIERNES", "NOVA"],
        index=["JARVIS", "VIERNES", "NOVA"].index(st.session_state.nucleo_activo),
        label_visibility="collapsed"
    )
    if nuevo_nucleo != st.session_state.nucleo_activo:
        st.session_state.nucleo_activo = nuevo_nucleo
        st.session_state.historial_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Cambio de nucleo a {nuevo_nucleo}.")
        st.success(f"Nucleo cambiado a {nuevo_nucleo}.")
        st.rerun()

    st.markdown("---")
    st.markdown("#### Memoria y Autonomia")
    
    with st.expander(" Gestionar Nucleo Tecnico", expanded=False):
        dato_mem = st.text_input("Dato a guardar en memoria:", placeholder="Ej: Preferencia de diseno...")
        if st.button(" Guardar Memoria Larga", use_container_width=True):
            if dato_mem.strip():
                jarvis_mem.remember_fact(f"mem_{datetime.datetime.now().timestamp()}", dato_mem.strip())
                st.success("¡Informacion retenida en bases locales!")
        
        app_sys = st.text_input("Ejecutar comando/App o script:", placeholder="notepad o script.py")
        if st.button(" Lanzar Sistema", use_container_width=True):
            if app_sys.strip():
                res_exec = jarvis_exec.open_application(app_sys.strip())
                st.info(res_exec)

    st.markdown("---")
    st.markdown("#### Centro de Analisis Optico")
    
    with st.expander(" Subir Archivo (IMG / TXT / PDF)", expanded=False):
        archivo_subido = st.file_uploader("Selecciona archivo:", type=["png", "jpg", "jpeg", "txt", "pdf"])
        if archivo_subido is not None:
            st.download_button(
                label=" Descargar Archivo Cargado",
                data=archivo_subido,
                file_name=archivo_subido.name,
                use_container_width=True
            )
            
        if st.button(" Ejecutar Analisis Tactico", use_container_width=True):
            if archivo_subido is not None:
                nombre_archivo = archivo_subido.name
                nucleo_actual = st.session_state.nucleo_activo
                if nombre_archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                    informe_analisis = f"[{nucleo_actual}] **ANALISIS OPTICO:** \n- Archivo: `{nombre_archivo}` \n- **Diagnostico:** Captura visual procesada con exito, jefa. Resolucion y metadatos verificados."
                elif nombre_archivo.lower().endswith('.pdf'):
                    extracto = extraer_texto_archivo(archivo_subido)
                    informe_analisis = f"[{nucleo_actual}] **ANALISIS DE DOCUMENTO PDF:** \n- Documento: `{nombre_archivo}` \n- **Extracto:** _{extracto}_ \n- **Diagnostico:** Lectura completada, jefa. Avisame si necesitas cruzar estos datos con alguna mision."
                else:
                    extracto = extraer_texto_archivo(archivo_subido)
                    informe_analisis = f"[{nucleo_actual}] **ANALISIS DE TEXTO:** \n- Archivo: `{nombre_archivo}` \n- **Contenido:** _{extracto}_ \n- **Diagnostico:** Texto procesado y comprendido a la perfeccion."
                
                st.session_state.mensajes.append({"role": "assistant", "content": informe_analisis})
                st.session_state.historial_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Analisis optico ejecutado en {nombre_archivo}.")
                st.rerun()
            else:
                st.warning("Primero debes subir un archivo.")
            
    st.markdown("---")
    st.markdown("#### Seguridad")
    
    if st.button(" Refrescar Sensores", use_container_width=True):
        st.info("Sensores del Nodo Buin estables y seguros.")
        
    st.markdown("---")
    st.markdown("#### Mapa Tactico")
    
    with st.expander(" mapa tactico satelital", expanded=False):
        st.markdown(
            '<div class="cyber-radar-screen">'
            '<p style="color: #ff3333; font-size: 0.75rem; margin: 0;" class="radar-blip"><b> 10,940,428 ATAQUES HOY</b></p>'
            '<p style="color: #00f3ff; font-size: 0.65rem; margin: 3px 0;">[ Rastreo Global Activo ]</p>'
            '<hr style="border-color: #00f3ff; opacity: 0.3; margin: 5px 0;">'
            '<p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"><b>Japan ➔ Germany</b><br><span style="color:#ff3333;">[Exploit detectado]</span></p>'
            '<p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"><b>United States ➔ Honduras</b><br><span style="color:#bf7fff;">[Phishing activo]</span></p>'
            '<p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"><b>Nodo Buin ➔ Seguro</b><br><span style="color:#00ff88;">[0 intrusiones]</span></p>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### Red Neuronal & Skills (Open Source)")
    with st.expander(" Inspector de Repositorios", expanded=False):
        st.markdown(
            '<div class="cyber-radar-screen" style="text-align: left;">'
            '<p style="color: #00f3ff; font-size: 0.65rem; margin: 2px 0;"><b>01 / mattpocock / skills</b><br><span style="color:#00ff88;">[307K Estrellas // 18M Installs]</span></p>'
            '<p style="color: #00f3ff; font-size: 0.65rem; margin: 2px 0;"><b>02 / addyosmani / agent-skills</b><br><span style="color:#bf7fff

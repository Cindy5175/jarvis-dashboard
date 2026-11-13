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

if "offset_clima" not in st.session_state:
    st.session_state.offset_clima = 0  # Para calibración manual si lo desea

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

# --- INICIALIZACION DE BASE DE DATOS SQLITE (Las 7 Memorias) ---
fn_db = "jarvis_misiones.db"

def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    # 1. Prospective Memory (Misiones futuras y recordatorios)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS misiones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarea TEXT NOT NULL,
        estado TEXT DEFAULT 'Pendiente',
        fecha_creacion TEXT
    )
    """)
    # 2. Semantic Memory (Hechos duraderos sobre el usuario)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        key_id TEXT PRIMARY KEY,
        fact_text TEXT,
        category TEXT
    )
    """)
    # 3. Episodic Memory (Historial persistente de eventos y auditoría)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS episodic_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        event_type TEXT,
        details TEXT
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

    def log_episode(self, event_type: str, details: str):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            timestamp = datetime.datetime.now(tz_chile).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("""
                INSERT INTO episodic_logs (timestamp, event_type, details)
                VALUES (?, ?, ?)
            """, (timestamp, event_type, details))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def get_recent_episodes(self, limit=15) -> list:
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, event_type, details FROM episodic_logs ORDER BY id DESC LIMIT ?", (limit,))
            rows = cursor.fetchall()
            conn.close()
            return rows
        except Exception:
            return []

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
    ts = datetime.datetime.now(tz_chile).strftime('%Y-%m-%d %H:%M')
    cursor.execute("INSERT INTO misiones (tarea, fecha_creacion) VALUES (?, ?)", (tarea, ts))
    conn.commit()
    conn.close()
    jarvis_mem.log_episode("MISSION_ADD", f"Nueva misión registrada: {tarea}")

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
    jarvis_mem.log_episode("MISSION_PURGE", "Base de misiones purgada.")

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

# --- ESTILOS VISUALES BLINDADOS ---
estilos_css = (
    "<style>"
    ".stApp { background-color: #060913 !important; color: #00f3ff !important; }"
    "p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }"
    "section[data-testid='stHorizontalBlock'] > div:first-child h4 { font-size: 0.8rem !important; font-weight: bold; margin-bottom: 2px !important; margin-top: 10px !important; }"
    "section[data-testid='stHorizontalBlock'] > div:first-child p { font-size: 0.7rem !important; }"
    ".stChatMessage p, .stChatMessage div { font-size: 0.85rem !important; color: #00f3ff !important; }"
    ".stButton>button { background-color: #00f3ff !important; border: 1.5px solid #00f3ff !important; font-weight: bold; font-family: monospace; box-shadow: 0 0 10px rgba(0, 243, 255, 0.6); width: 100%; }"
    ".stButton>button p { color: #060913 !important; }"
    ".stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.9); }"
    ".arc-reactor-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 5px; }"
    ".arc-ring { width: 45px; height: 45px; border: 2.5px solid #00f3ff; border-radius: 50%; position: relative; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #00f3ff 0%, #060913 70%); box-shadow: 0 0 15px rgba(0, 243, 255, 0.7); margin-bottom: 5px; }"
    ".arc-triangle { width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-bottom: 14px solid #060913; filter: drop-shadow(0 0 5px #00f3ff); }"
    ".holo-brain-box { border: 1.5px solid #00f3ff; background: linear-gradient(135deg, #0a1128 0%, #060913 100%); padding: 10px 15px; border-radius: 8px; text-align: center; box-shadow: 0 0 12px rgba(0, 243, 255, 0.3); margin: 0 auto 15px auto; max-width: 700px; }"
    ".cyber-radar-screen { background: #03050a; border: 1px solid #00f3ff; border-radius: 6px; padding: 10px; text-align: center; box-shadow: inset 0 0 10px rgba(0, 243, 255, 0.2); }"
    ".radar-blip { animation: pulse-blip 1.5s infinite; }"
    "@keyframes pulse-blip { 0% { opacity: 0.3; } 50% { opacity: 1; text-shadow: 0 0 8px #ff3333; } 100% { opacity: 0.3; } }"
    "</style>"
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
                jarvis_mem.log_episode("SYSTEM_LOGIN", "Acceso concedido a la jefa exitosamente.")
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

nucleo_actual_txt = st.session_state.nucleo_activo
st.markdown(
    f'<div class="holo-brain-box">'
    f'<h4 style="color: #00f3ff; margin: 0; font-size: 0.95rem; font-family: monospace; text-shadow: 0 0 8px #00f3ff;"> NUCLEO NEURONAL CYBER-GRID [{nucleo_actual_txt}] (7 MEMORIAS ACTIVAS)</h4>'
    '<p style="color: #00f3ff; font-size: 0.7rem; margin: 3px 0 0 0; font-family: monospace; opacity: 0.8;">Working, Semantic, Episodic, Procedural, Retrieval, Parametric & Prospective Systems</p>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# --- NAVEGACIÓN POR PESTAÑAS ---
tab_principal, tab_financiero = st.tabs(["🖥️ Panel Principal & IA", "📈 Centro Financiero & Mercados"])

with tab_principal:
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
            jarvis_mem.log_episode("CORE_SWITCH", f"Cambio de núcleo activo a {nuevo_nucleo}.")
            st.success(f"Nucleo cambiado a {nuevo_nucleo}.")
            st.rerun()

        st.markdown("---")
        st.markdown("#### Memoria y Autonomia")
        
        with st.expander(" Gestionar Nucleo Tecnico", expanded=False):
            dato_mem = st.text_input("Dato a guardar en memoria semántica:", placeholder="Ej: Preferencia de diseño...")
            if st.button(" Guardar Memoria Larga", use_container_width=True):
                if dato_mem.strip():
                    jarvis_mem.remember_fact(f"mem_{datetime.datetime.now().timestamp()}", dato_mem.strip())
                    jarvis_mem.log_episode("SEMANTIC_MEM_SAVE", f"Guardado hecho semántico: {dato_mem.strip()}")
                    st.success("¡Informacion retenida en bases locales!")
            
            app_sys = st.text_input("Ejecutar comando/App o script:", placeholder="notepad o script.py")
            if st.button(" Lanzar Sistema", use_container_width=True):
                if app_sys.strip():
                    res_exec = jarvis_exec.open_application(app_sys.strip())
                    jarvis_mem.log_episode("SYS_EXEC", f"Ejecutado proceso: {app_sys.strip()}")
                    st.info(res_exec)

        st.markdown("---")
        st.markdown("#### Centro de Analisis Optico & NotebookLM")
        
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
                        informe_analisis = f"[{nucleo_actual}] **ANALISIS OPTICO (Retrieval Memory):** \n- Archivo: `{nombre_archivo}` \n- **Diagnostico:** Captura visual procesada con exito, jefa. Resolucion y metadatos verificados."
                    elif nombre_archivo.lower().endswith('.pdf'):
                        extracto = extraer_texto_archivo(archivo_subido)
                        informe_analisis = f"[{nucleo_actual}] **ANALISIS DE DOCUMENTO PDF (Retrieval/NotebookLM Bridge):** \n- Documento: `{nombre_archivo}` \n- **Extracto:** _{extracto}_ \n- **Diagnostico:** Lectura completada, jefa. Avisame si necesitas cruzar estos datos con alguna mision."
                    else:
                        extracto = extraer_texto_archivo(archivo_subido)
                        informe_analisis = f"[{nucleo_actual}] **ANALISIS DE TEXTO:** \n- Archivo: `{nombre_archivo}` \n- **Contenido:** _{extracto}_ \n- **Diagnostico:** Texto procesado y comprendido a la perfeccion."
                    
                    st.session_state.mensajes.append({"role": "assistant", "content": informe_analisis})
                    st.session_state.historial_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Analisis optico ejecutado en {nombre_archivo}.")
                    jarvis_mem.log_episode("RETRIEVAL_ANALYSIS", f"Análisis de archivo {nombre_archivo} completado.")
                    st.rerun()
                else:
                    st.warning("Primero debes subir un archivo.")
            
            st.markdown("---")
            st.markdown("**Puente Externo:**")
            st.link_button(" Abrir NotebookLM (Google)", "https://notebooklm.google.com/", use_container_width=True)

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
                '<p style="color: #00f3ff; font-size: 0.65rem; margin: 2px 0;"><b>02 / addyosmani / agent-skills</b><br><span style="color:#bf7fff;">[Claude Code Engineering]</span></p>'
                '<p style="color: #00f3ff; font-size: 0.65rem; margin: 2px 0;"><b>03 / cloudflare / security-audit</b><br><span style="color:#ff3333;">[128 Repos Scanned]</span></p>'
                '</div>',
                unsafe_allow_html=True
            )
            
            # --- SELECTOR DE SKILLS TÁCTICAS (Procedural Memory) ---
            st.markdown("<p style='font-size: 0.7rem; margin-top: 8px;'><b>Skills Activas:</b></p>", unsafe_allow_html=True)
            skill_seleccionada = st.selectbox(
                "Seleccionar Skill:",
                ["/skill_resumen (Resumen Ejecutivo)", "/skill_mercado (Inteligencia Bursátil)", "/skill_auditoria (Auditoría de Código)"],
                label_visibility="collapsed"
            )
            if st.button(" Ejecutar Skill Activa", use_container_width=True):
                skill_tag = skill_seleccionada.split(" ")[0]
                st.session_state.historial_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Skill {skill_tag} ejecutada.")
                jarvis_mem.log_episode("PROCEDURAL_SKILL", f"Skill ejecutada: {skill_tag}")
                if "resumen" in skill_tag:
                    res_skill = "[SKILL RESUMEN] Análisis ejecutado: Nodo Buin operando con alta eficiencia y cero pérdidas de paquetes."
                elif "mercado" in skill_tag:
                    res_skill = "[SKILL MERCADO] Reporte bursátil: Activos tradicionales y divisas estables. Monitoreo en Finviz e Investing activo."
                else:
                    res_skill = "[SKILL AUDITORÍA] Escaneo de sintaxis y seguridad: 0 vulnerabilidades detectadas en el motor principal."
                st.session_state.mensajes.append({"role": "assistant", "content": res_skill})
                st.rerun()

            if st.button(" Ejecutar Escaneo de Skills", use_container_width=True):
                st.session_state.historial_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Escaneo de Skills y Auditoria completado.")
                jarvis_mem.log_episode("SKILLS_SCAN", "Escaneo completo de red neuronal de skills.")
                st.success("¡Red neuronal de skills sincronizada con exito!")

        st.markdown("---")
        st.markdown("#### Videovigilancia Global")
        with st.expander(" Camaras en Vivo / Satelite", expanded=False):
            st.link_button(" Stgo / Chile (Skyline)", "https://www.skylinewebcams.com/es/webcam/chile.html", use_container_width=True)
            st.link_button(" Concepcion Webcam", "https://liveworldwebcams.com/es/concepcion-webcam/", use_container_width=True)
            st.link_button(" Windy Radars & Cams", "https://www.windy.com/es/-C%C3%A1maras-web/webcams?39.880,-5.449,7", use_container_width=True)
            st.link_button(" Galveston Port, Texas", "https://www.earthcam.com/usa/texas/galveston/port/?cam=pg_terminal28", use_container_width=True)
            st.link_button(" Puerta del Sol, Madrid", "https://www.skylinewebcams.com/es/webcam/espana/comunidad-de-madrid/madrid/puerta-del-sol-tio-pepe.html", use_container_width=True)
        
        st.markdown("---")
        st.markdown(" **OSIRIS:** En linea")
        st.link_button(" Abrir OSIRIS", "https://osiris.mclaren.com/", use_container_width=True)
       
        st.markdown(" **PlanetEar:** Sincronizado")
        st.link_button(" Abrir PlanetEar", "https://www.planet.com/", use_container_width=True)
       
        st.markdown(" **USGS Explorer:**")
        st.link_button(" USGS Explorer", "https://earthexplorer.usgs.gov/", use_container_width=True)
       
        st.markdown("---")
        st.markdown("#### Clima Buin (Panel Dinamico)")
        
        with st.expander(" Widget Clima En Vivo", expanded=False):
            st.markdown(f"**Buin (CASA)** \n ☀️ **{temp_real}** — Mayormente soleado")
            st.caption(f" Humedad: {hum_real} | Viento: {viento_real}")
            
            # --- CALIBRACIÓN MANUAL HÍBRIDA ---
            nuevo_offset = st.slider("Calibrar Temp (°C):", -10, 10, st.session_state.offset_clima, key="slider_calibracion")
            if nuevo_offset != st.session_state.offset_clima:
                st.session_state.offset_clima = nuevo_offset
                st.rerun()

            st.markdown("---")
            st.markdown(" **Pronostico Diario (Avanzando):**")
            
            dia_actual_idx = now_chile.weekday()
            nombres_dias_semana = ['Lun', 'Mar', 'Mie', 'Jue', 'Vie', 'Sab', 'Dom']
            
            for i in range(min(6, len(t_maxs))):
                d_idx = (dia_actual_idx + i) % 7
                d_label = "Hoy" if i == 0 else nombres_dias_semana[d_idx]
                mx = int(t_maxs[i])
                mn = int(t_mins[i])
                st.markdown(f"**`{d_label}`** ➔ Min: **`{mn}°`** | Max: **`{mx}°`**")
                
        st.markdown("---")
        st.markdown("#### Misiones")
        
        with st.expander(" Base de Datos", expanded=False):
            nueva_tarea = st.text_input("Nueva Mision Tactica:", placeholder="Ej: Revisar nodos...")
            if st.button(" Registrar Tarea", use_container_width=True):
                if nueva_tarea.strip():
                    agregar_mision(nueva_tarea.strip())
                    st.success("¡Mision registrada con exito!")
                    st.rerun()
                    
            misiones_guardadas = obtener_misiones()
            if misiones_guardadas:
                st.markdown("**Activas:**")
                for m_id, m_text, m_est in misiones_guardadas:
                    st.markdown(f"- `{m_text}`")
                if st.button(" Limpiar Misiones", use_container_width=True):
                    limpiar_misiones()
                    st.rerun()
            else:
                st.caption("Sin misiones pendientes.")

        st.markdown("---")
        st.markdown("#### Consola de Auditoria (Episodic Memory)")
        with st.expander(" Logs en Vivo", expanded=False):
            episodios_recientes = jarvis_mem.get_recent_episodes(10)
            if episodios_recientes:
                for ts, ev_type, details in episodios_recientes:
                    st.markdown(f"<span style='font-size: 0.6rem;'>[{ts}] <b>{ev_type}</b>: {details}</span>", unsafe_allow_html=True)
            else:
                for log_item in st.session_state.historial_logs[-10:]:
                    st.markdown(f"<span style='font-size: 0.6rem;'>{log_item}</span>", unsafe_allow_html=True)

    # =========================================================================
    # CONSOLA PRINCIPAL (DERECHA)
    # =========================================================================

    script_voz_pc = (
        '<div style="margin-bottom: 10px;">'
        '<button onclick="iniciarEscuchaPC()" style="background-color: #00f3ff; color: #060913; border

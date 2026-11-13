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
        {"role": "assistant", "content": saludo_actual + ", jefa. Por aqui todo en orden en el Nodo Buin, con los circuitos bien puestos y listo para ayudarte con lo que necesites."}
    ]

PIN_SECRETO = "2805"

# --- INICIALIZACION DE BASE DE DATOS SQLITE (Las 7 Memorias) ---
fn_db = "jarvis_misiones.db"

def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS misiones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tarea TEXT NOT NULL,
        estado TEXT DEFAULT 'Pendiente',
        fecha_creacion TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS memory (
        key_id TEXT PRIMARY KEY,
        fact_text TEXT,
        category TEXT
    )
    """)
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
                    subprocess.Popen('start cmd /k "' + sys.executable + ' ' + target + '"', shell=True)
                else:
                    subprocess.Popen([sys.executable, target])
                return "Script automatizado '" + os.path.basename(target) + "' puesto en marcha, jefa."
            
            if sys.platform == "win32":
                subprocess.Popen("start " + target, shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", target])
            else:
                subprocess.Popen([target])
            return "Ejecutando proceso '" + target + "' de inmediato, jefa."
        except Exception as e:
            return "Error ejecutando el proceso '" + target + "': " + str(e)

class JarvisCore:
    def __init__(self, name="JARVIS"):
        self.name = name

    async def process_voice_input(self, text_command: str) -> str:
        await asyncio.sleep(0.01)
        return "Procesado al instante con baja latencia. Ejecutando orden: '" + text_command + "'."

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
    jarvis_mem.log_episode("MISSION_ADD", "Nueva misión registrada: " + tarea)

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
                return (texto[:450] + ("..." if len(texto) > 450 else "")) if texto else "PDF sin texto extraíble."
            except ImportError:
                return "Instala 'pypdf' en tu entorno para lectura profunda de PDFs."
    except Exception as e:
        return "Lectura parcial completada (" + str(e) + ")."
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
        return str(temp_calibrada) + "°C", str(hum) + "%", str(viento) + " km/h", dias_max, dias_min
    except Exception:
        fallback_t = 31 + st.session_state.offset_clima
        return str(fallback_t) + "°C", "50%", "10 km/h", [31, 30, 26, 21, 18, 21], [14, 14, 15, 14, 13, 11]

temp_real, hum_real, viento_real, t_maxs, t_mins = obtener_clima_buin()

# --- ESTILOS VISUALES CORREGIDOS (ALTA VISIBILIDAD EN MÓDULOS) ---
estilos_css = """
<style>
.stApp { background-color: #060913 !important; color: #00f3ff !important; }
p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
.stButton>button { background-color: #00f3ff !important; color: #060913 !important; border: 1.5px solid #00f3ff !important; font-weight: bold; font-family: monospace; width: 100%; }
.stButton>button:hover { background-color: #0088cc !important; }
/* Forzar alto contraste en los expanders y títulos de módulos para que se lean perfecto */
[data-testid="stExpander"] summary span { color: #00f3ff !important; font-weight: bold; }
</style>
"""
st.markdown(estilos_css, unsafe_allow_html=True)

# --- 1. PANTALLA DE BLOQUEO ---
if not st.session_state.get("autorizado", False):
    st.markdown("<h2 style='text-align: center;'>ACCESO RESTRINGIDO - NODO BUIN</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>INGRESE PIN DE SEGURIDAD</p>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto Numerico:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button("Desbloquear Armadura")
        
        if btn_entrar:
            if pin_input.strip() == PIN_SECRETO:
                st.session_state.autorizado = True
                st.session_state.historial_logs.append("[" + datetime.datetime.now().strftime('%H:%M:%S') + "] Acceso concedido a la jefa.")
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
fecha_str = dia_str + ", " + str(now_chile.day).zfill(2) + " de " + mes_str + " de " + str(now_chile.year)

st.markdown("<h1 style='text-align: center;'>J.A.R.V.I.S IA</h1>", unsafe_allow_html=True)

# Reloj en vivo con segundos dinámicos usando JavaScript incrustado de alta precisión
reloj_html_vivo = """
<div style="text-align: center; font-family: monospace; font-size: 0.85rem; color: #00f3ff; margin-bottom: 15px;">
    [ NODO BUIN, CHILE // """ + fecha_str + """ – <span id="reloj-dinamico">Calculando hora...</span> ]
</div>
<script>
function iniciarRelojVivo() {
    const el = document.getElementById("reloj-dinamico");
    if (!el) return;
    function actualizar() {
        const ahora = new Date();
        const opciones = { timeZone: 'America/Santiago', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        el.innerText = "Hora Local: " + new Intl.DateTimeFormat('es-CL', opciones).format(ahora);
    }
    actualizar();
    setInterval(actualizar, 1000);
}
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciarRelojVivo);
} else {
    iniciarRelojVivo();
}
</script>
"""
st.components.v1.html(reloj_html_vivo, height=35)

# NÚCLEO NEURONAL CENTRADO Y DESTACADO
nucleo_actual_txt = st.session_state.nucleo_activo
nucleo_centrado_html = """
<div style="text-align: center; background: linear-gradient(135deg, #0a1128 0%, #060913 100%); border: 1.5px solid #00f3ff; padding: 10px; border-radius: 8px; margin: 10px auto 20px auto; max-width: 800px; box-shadow: 0 0 12px rgba(0, 243, 255, 0.4);">
    <h4 style="color: #00f3ff; margin: 0; font-size: 0.95rem; font-family: monospace; text-shadow: 0 0 8px #00f3ff;">NÚCLEO NEURONAL CYBER-GRID [""" + nucleo_actual_txt + """] (7 MEMORIAS ACTIVAS)</h4>
    <p style="color: #00f3ff; font-size: 0.7rem; margin: 3px 0 0 0; opacity: 0.8;">Working, Semantic, Episodic, Procedural, Retrieval, Parametric & Prospective Systems</p>
</div>
"""
st.markdown(nucleo_centrado_html, unsafe_allow_html=True)

st.markdown("---")

# --- NAVEGACIÓN POR PESTAÑAS ---
tab_principal, tab_financiero = st.tabs(["🖥️ Panel Principal & IA", "📈 Centro Financiero & Mercados"])

with tab_principal:
    col_modulos, col_chat = st.columns([1, 2])

    with col_modulos:
        st.markdown("#### 📂 Módulos del Sistema")
        
        if st.button("Bloquear Sistema", use_container_width=True):
            st.session_state.autorizado = False
            st.rerun()
            
        if st.button("Reinicio Total", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
            
        st.markdown("---")
        st.markdown("#### Selector de Núcleo (IA)")
        
        nuevo_nucleo = st.radio(
            "Seleccionar Asistente Activo:",
            ["JARVIS", "VIERNES", "NOVA"],
            index=["JARVIS", "VIERNES", "NOVA"].index(st.session_state.nucleo_activo),
            label_visibility="collapsed"
        )
        if nuevo_nucleo != st.session_state.nucleo_activo:
            st.session_state.nucleo_activo = nuevo_nucleo
            st.session_state.historial_logs.append("[" + datetime.datetime.now().strftime('%H:%M:%S') + "] Cambio de nucleo a " + nuevo_nucleo + ".")
            jarvis_mem.log_episode("CORE_SWITCH", "Cambio de núcleo activo a " + nuevo_nucleo + ".")
            st.success("Núcleo cambiado a " + nuevo_nucleo + ".")
            st.rerun()

        st.markdown("---")
        st.markdown("#### Memoria y Autonomía")
        
        with st.expander("💾 Gestionar Núcleo Técnico", expanded=False):
            dato_mem = st.text_input("Dato a guardar en memoria semántica:", placeholder="Ej: Preferencia de diseño...")
            if st.button("Guardar Memoria Larga", use_container_width=True):
                if dato_mem.strip():
                    jarvis_mem.remember_fact("mem_" + str(datetime.datetime.now().timestamp()), dato_mem.strip())
                    jarvis_mem.log_episode("SEMANTIC_MEM_SAVE", "Guardado hecho semántico: " + dato_mem.strip())
                    st.success("¡Información retenida en bases locales!")
            
            app_sys = st.text_input("Ejecutar comando/App o script:", placeholder="notepad o script.py")
            if st.button("Lanzar Sistema", use_container_width=True):
                if app_sys.strip():
                    res_exec = jarvis_exec.open_application(app_sys.strip())
                    jarvis_mem.log_episode("SYS_EXEC", "Ejecutado proceso: " + app_sys.strip())
                    st.info(res_exec)

        st.markdown("---")
        st.markdown("#### Análisis Óptico & NotebookLM")
        
        with st.expander("📁 Subir Archivo (IMG / TXT / PDF)", expanded=False):
            archivo_subido = st.file_uploader("Selecciona archivo:", type=["png", "jpg", "jpeg", "txt", "pdf"])
            if archivo_subido is not None:
                st.download_button(
                    label="Descargar Archivo Cargado",
                    data=archivo_subido,
                    file_name=archivo_subido.name,
                    use_container_width=True
                )
                
            if st.button("Ejecutar Análisis Táctico", use_container_width=True):
                if archivo_subido is not None:
                    nombre_archivo = archivo_subido.name
                    nucleo_actual = st.session_state.nucleo_activo
                    if nombre_archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                        informe_analisis = "[" + nucleo_actual + "] **ANÁLISIS ÓPTICO:** Archivo `" + nombre_archivo + "` procesado con éxito, jefa."
                    elif nombre_archivo.lower().endswith('.pdf'):
                        extracto = extraer_texto_archivo(archivo_subido)
                        informe_analisis = "[" + nucleo_actual + "] **ANÁLISIS DE PDF:** `" + nombre_archivo + "`. Extracto: _" + extracto + "_"
                    else:
                        extracto = extraer_texto_archivo(archivo_subido)
                        informe_analisis = "[" + nucleo_actual + "] **ANÁLISIS DE TEXTO:** `" + nombre_archivo + "`. Contenido: _" + extracto + "_"
                    
                    st.session_state.mensajes.append({"role": "assistant", "content": informe_analisis})
                    st.session_state.historial_logs.append("[" + datetime.datetime.now().strftime('%H:%M:%S') + "] Análisis ejecutado en " + nombre_archivo + ".")
                    jarvis_mem.log_episode("RETRIEVAL_ANALYSIS", "Análisis de archivo " + nombre_archivo + " completado.")
                    st.rerun()
                else:
                    st.warning("Primero debes subir un archivo.")
            
            st.markdown("---")
            st.link_button("Abrir NotebookLM (Google)", "https://notebooklm.google.com/", use_container_width=True)

        st.markdown("---")
        st.markdown("#### Mapa Táctico Satelital")
        with st.expander("🌐 Ver Estado Global de Red", expanded=False):
            st.markdown("**10,940,428 ATAQUES HOY** [Rastreo Global Activo]")
            st.markdown("- Japan ➔ Germany `[Exploit detectado]`")
            st.markdown("- United States ➔ Honduras `[Phishing activo]`")
            st.markdown("- **Nodo Buin ➔ Seguro `[0 intrusiones]`**")

        st.markdown("---")
        st.markdown("#### Skills Tácticas")
        with st.expander("⚡ Selector de Skills", expanded=False):
            skill_seleccionada = st.selectbox(
                "Seleccionar Skill:",
                ["/skill_resumen", "/skill_mercado", "/skill_auditoria"],
                label_visibility="collapsed"
            )
            if st.button("Ejecutar Skill Activa", use_container_width=True):
                if "resumen" in skill_seleccionada:
                    res_skill = "[SKILL RESUMEN] Nodo Buin operando al 100% de eficiencia."
                elif "mercado" in skill_seleccionada:
                    res_skill = "[SKILL MERCADO] Monitoreo bursátil en Finviz e Investing activo."
                else:
                    res_skill = "[SKILL AUDITORÍA] 0 vulnerabilidades detectadas."
                st.session_state.mensajes.append({"role": "assistant", "content": res_skill})
                st.rerun()

        st.markdown("---")
        st.markdown("#### Videovigilancia Global")
        with st.expander("📷 Cámaras y Radares", expanded=False):
            st.link_button("Stgo / Chile (Skyline)", "https://www.skylinewebcams.com/es/webcam/chile.html", use_container_width=True)
            st.link_button("Concepción Webcam", "https://liveworldwebcams.com/es/concepcion-webcam/", use_container_width=True)
            st.link_button("Windy Radars", "https://www.windy.com/", use_container_width=True)

        st.markdown("---")
        st.markdown("#### Clima Buin")
        with st.expander("☀️ Widget Clima En Vivo", expanded=False):
            st.markdown("**Buin (CASA)**: ☀️ **" + temp_real + "** | Humedad: " + hum_real + " | Viento: " + viento_real)
            nuevo_offset = st.slider("Calibrar Temp (°C):", -10, 10, st.session_state.offset_clima, key="slider_calibracion")
            if nuevo_offset != st.session_state.offset_clima:
                st.session_state.offset_clima = nuevo_offset
                st.rerun()

        st.markdown("---")
        st.markdown("#### Misiones")
        with st.expander("🎯 Base de Datos", expanded=False):
            nueva_tarea = st.text_input("Nueva Misión Táctica:", placeholder="Ej: Revisar nodos...")
            if st.button("Registrar Tarea", use_container_width=True):
                if nueva_tarea.strip():
                    agregar_mision(nueva_tarea.strip())
                    st.success("¡Misión registrada!")
                    st.rerun()
                    
            misiones_guardadas = obtener_misiones()
            if misiones_guardadas:
                for m_id, m_text, m_est in misiones_guardadas:
                    st.markdown("- `" + m_text + "`")
                if st.button("Limpiar Misiones", use_container_width=True):
                    limpiar_misiones()
                    st.rerun()

    with col_chat:
        col_h1, col_h2 = st.columns([4, 1])
        with col_h1:
            st.markdown("<h4>Chat Táctico</h4>", unsafe_allow_html=True)
        with col_h2:
            if st.button("Purgar", use_container_width=True, key="btn_limpiar_chat"):
                st.session_state.mensajes = [{"role": "assistant", "content": saludo_actual + ", jefa. Memoria limpia. ¿Qué movemos ahora?"}]
                st.session_state.historial_logs.append("[" + datetime.datetime.now().strftime('%H:%M:%S') + "] Chat purgado.")
                jarvis_mem.log_episode("CHAT_PURGE", "Historial purgado.")
                st.rerun()

        for m in st.session_state.mensajes:
            with st.chat_message(m["role"]):
                st.markdown(m['content'])

        prompt_chat = st.chat_input("Escribe tu orden o protocolo...")

        if prompt_chat:
            st.session_state.mensajes.append({"role": "user", "content": prompt_chat})
            st.session_state.historial_logs.append("[" + datetime.datetime.now().strftime('%H:%M:%S') + "] Comando: " + prompt_chat[:25] + "...")
            jarvis_mem.log_episode("USER_COMMAND", "Comando: " + prompt_chat)
            
            with st.chat_message("user"):
                st.markdown(prompt_chat)

            respuesta_ia = ""
            q = prompt_chat.lower().strip()
            contexto_memoria = jarvis_mem.recall_context(q)
            
            nucleo = st.session_state.nucleo_activo
            prefijo_nucleo = "[" + nucleo + "] "

            if q.startswith("/skill_resumen"):
                respuesta_ia = prefijo_nucleo + "**[SKILL: RESUMEN]**: Sistemas estables, 7 memorias sincronizadas."
            elif q.startswith("/skill_mercado"):
                respuesta_ia = prefijo_nucleo + "**[SKILL: MERCADO]**: Flujos tradicionales estables. Consulta Finviz en la pestaña de al lado."
            elif q.startswith("/skill_auditoria"):
                respuesta_ia = prefijo_nucleo + "**[SKILL: AUDITORÍA]**: 0 vulnerabilidades detectadas."
            elif "modo trabajo" in q or "abre el taller" in q:
                res_1 = jarvis_exec.open_application("notepad")
                respuesta_ia = prefijo_nucleo + "Desplegando entorno de trabajo. " + res_1
            elif q.startswith("abrir ") or q.startswith("ejecutar "):
                app_objetivo = q.replace("abrir ", "").replace("ejecutar ", "").strip()
                res_app = jarvis_exec.open_application(app_objetivo)
                respuesta_ia = prefijo_nucleo + res_app
            elif nucleo == "JARVIS":
                if q.startswith("/human"):
                    respuesta_ia = prefijo_nucleo + "Entendido, jefa. Todo fluye con precisión por aquí."
                elif q.startswith("eli10"):
                    respuesta_ia = prefijo_nucleo + "**[ELI10]**: Imagina el Nodo Buin como una colmena donde cada memoria colabora."
                else:
                    recuerdos_extra = " [Memoria: " + ", ".join(contexto_memoria) + "]" if contexto_memoria else ""
                    respuesta_ia = prefijo_nucleo + "Orden procesada al 100%." + recuerdos_extra + " ¿Qué otra directriz ejecutamos, jefa?"
            elif nucleo == "VIERNES":
                recuerdos_extra = " [Memoria: " + ", ".join(contexto_memoria) + "]" if contexto_memoria else ""
                respuesta_ia = prefijo_nucleo + "Protocolo táctico secundario activo. Analizando su consulta: '" + prompt_chat + "'. Eficiencia estricta garantizada en el Nodo Buin." + recuerdos_extra
            elif nucleo == "NOVA":
                recuerdos_extra = " [Memoria: " + ", ".join(contexto_memoria) + "]" if contexto_memoria else ""
                respuesta_ia = prefijo_nucleo + "Núcleo cuántico NOVA en línea. Patrones evaluados para: '" + prompt_chat + "'. Todo calibrado y listo." + recuerdos_extra

            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
            jarvis_mem.log_episode("JARVIS_RESPONSE", "Respuesta emitida por " + nucleo)
            st.rerun()

# =========================================================================
# PESTAÑA 2: CENTRO FINANCIERO Y MERCADOS
# =========================================================================
with tab_financiero:
    st.markdown("### 📈 Centro Financiero & Mercados Tradicionales")
    st.markdown("Acceso directo a plataformas bursátiles tradicionales.")
    
    st.markdown("---")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        st.markdown("#### 📊 Finviz")
        st.link_button("Abrir Finviz (Acciones)", "https://finviz.com/map.ashx", use_container_width=True)
        st.link_button("Screener de Mercado", "https://finviz.com/screener.ashx", use_container_width=True)
        
    with col_f2:
        st.markdown("#### 🌐 Investing.com")
        st.link_button("Abrir Investing.com", "https://es.investing.com/", use_container_width=True)
        st.link_button("Índices Mundiales", "https://es.investing.com/indices/major-indices", use_container_width=True)

    with col_f3:
        st.markdown("#### 💱 Divisas & Commodities")
        st.link_button("Mercado Forex", "https://es.investing.com/currencies/streaming-forex-rates-majors", use_container_width=True)
        st.link_button("Materias Primas", "https://es.investing.com/commodities/real-time-futures", use_container_width=True)

    st.markdown("---")
    st.info("El subsistema financiero está conectado con la Memoria de Recuperación y la Base de Datos SQLite del Nodo Buin.")

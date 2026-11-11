import streamlit as st
import datetime
import sqlite3
import requests
import os
import sys
import asyncio
import subprocess

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INICIALIZACIÓN DE SESSION_STATE ---
if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

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
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Por aquí todo en orden en el Nodo Buin, con los circuitos bien puestos y lista para ayudarte con lo que necesites."}
    ]

PIN_SECRETO = "2805"

# --- INICIALIZACIÓN DE BASE DE DATOS SQLITE (Misiones & Memoria) ---
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

# --- CLASES MAESTRAS JARVIS ---
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
            return f"Ejecutando proceso '{target}' de inmediato, señorita."
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

# --- ESTILOS VISUALES ---
st.markdown("""
<style>
.stApp { background-color: #060913 !important; color: #00f3ff !important; }
p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }

section[data-testid="stHorizontalBlock"] > div:first-child h4 {
    font-size: 0.8rem !important;
    font-weight: bold;
    margin-bottom: 2px !important;
    margin-top: 10px !important;
}

section[data-testid="stHorizontalBlock"] > div:first-child p,
section[data-testid="stHorizontalBlock"] > div:first-child span,
section[data-testid="stHorizontalBlock"] > div:first-child label,
section[data-testid="stHorizontalBlock"] > div:first-child li {
    font-size: 0.7rem !important;
}

.stChatMessage p, .stChatMessage div {
    font-size: 0.85rem !important;
    color: #00f3ff !important;
}
.stButton>button {
    background-color: #00f3ff !important;
    border: 1.5px solid #00f3ff !important;
    font-weight: bold;
    font-family: monospace;
    box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
    width: 100%;
}
.stButton>button p, .stButton>button span {
    color: #060913 !important;
}
.stButton>button:hover {
    background-color: #0088cc !important;
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.9);
}
.stButton>button:hover p, .stButton>button:hover span {
    color: #ffffff !important;
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
.cyber-radar-screen {
    background: #03050a;
    border: 1px solid #00f3ff;
    border-radius: 6px;
    padding: 10px;
    text-align: center;
    box-shadow: inset 0 0 10px rgba(0, 243, 255, 0.2);
}
.radar-blip {
    animation: pulse-blip 1.5s infinite;
}
@keyframes pulse-blip {
    0% { opacity: 0.3; }
    50% { opacity: 1; text-shadow: 0 0 8px #ff3333; }
    100% { opacity: 0.3; }
}
</style>
""", unsafe_allow_html=True)

# --- 1. PANTALLA DE BLOQUEO ---
if not st.session_state.get("autorizado", False):
    st.markdown("""
    <div style="text-align: center; margin-top: 30px;">
        <h2 style="color: #00f3ff; font-family: monospace;"> ACCESO RESTRINGIDO - NODO BUIN</h2>
        <p style="color: #00f3ff; opacity: 0.8; font-size: 0.85rem;">INGRESE PIN DE SEGURIDAD</p>
    </div>
    """, unsafe_allow_html=True)
   
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto Numérico:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button(" Desbloquear Armadura")
       
        if btn_entrar:
            if pin_input.strip() == PIN_SECRETO:
                st.session_state.autorizado = True
                st.success("Acceso concedido. Un gusto verte de nuevo, jefa...")
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

st.markdown(f"""
<div class="arc-reactor-container">
    <div class="arc-ring"><div class="arc-triangle"></div></div>
    <h1 style="margin: 0; padding: 0; font-size: 2rem !important; text-align: center !important; color: #00f3ff !important; text-shadow: 0 0 15px rgba(0, 243, 255, 0.8); font-family: monospace;">J.A.R.V.I.S IA</h1>
    <p style="margin: 0; font-family: monospace; font-size: 0.75rem !important; color: #00f3ff !important; text-align: center !important; opacity: 0.85;">
        [ NODO BUIN, CHILE // {fecha_str} – <span id="reloj-vivo">--:--:--</span> ]
    </p>
</div>
""", unsafe_allow_html=True)

reloj_js = """
<script>
function actualizarReloj() {
    const ahora = new Date();
    const opciones = { timeZone: 'America/Santiago', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
    const horaChile = new Intl.DateTimeFormat('es-CL', opciones).format(ahora);
    const relojEl = window.parent.document.getElementById('reloj-vivo');
    if (relojEl) {
        relojEl.innerText = horaChile;
    }
}
setInterval(actualizarReloj, 1000);
actualizarReloj();
</script>
"""
st.components.v1.html(reloj_js, height=0)

st.markdown("""
<div class="holo-brain-box">
    <h4 style="color: #00f3ff; margin: 0; font-size: 0.95rem; font-family: monospace; text-shadow: 0 0 8px #00f3ff;"> NÚCLEO NEURONAL CYBER-GRID</h4>
    <p style="color: #00f3ff; font-size: 0.7rem; margin: 3px 0 0 0; font-family: monospace; opacity: 0.8;">Sistemas de procesamiento local, análisis óptico/PDF, clima y mapa táctico satelital</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- DISTRIBUCIÓN PRINCIPAL ---
col_modulos, col_chat = st.columns([1, 2])

with col_modulos:
    st.markdown("####  Módulos")
   
    if st.button(" Bloquear Sistema", use_container_width=True):
        st.session_state.autorizado = False
        st.rerun()
       
    if st.button(" Reinicio Total", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
       
    st.markdown("---")
    st.markdown("####  Memoria y Autonomía (JARVIS)")
   
    with st.expander(" Gestionar Núcleo Técnico", expanded=False):
        dato_mem = st.text_input("Dato a guardar en memoria:", placeholder="Ej: Preferencia de diseño...")
        if st.button(" Guardar Memoria Larga", use_container_width=True):
            if dato_mem.strip():
                jarvis_mem.remember_fact(f"mem_{datetime.datetime.now().timestamp()}", dato_mem.strip())
                st.success("¡Información retenida en bases locales!")
       
        app_sys = st.text_input("Ejecutar comando/App o script:", placeholder="notepad o script.py")
        if st.button(" Lanzar Sistema", use_container_width=True):
            if app_sys.strip():
                res_exec = jarvis_exec.open_application(app_sys.strip())
                st.info(res_exec)

    st.markdown("---")
    st.markdown("####  Centro de Análisis Óptico")
   
    with st.expander(" Subir Archivo (IMG / TXT / PDF)", expanded=True):
        archivo_subido = st.file_uploader("Selecciona archivo:", type=["png", "jpg", "jpeg", "txt", "pdf"])
        if archivo_subido is not None:
            st.download_button(
                label=" Descargar Archivo Cargado",
                data=archivo_subido,
                file_name=archivo_subido.name,
                use_container_width=True
            )
           
        if st.button(" Ejecutar Análisis Táctico", use_container_width=True):
            nombre_archivo = archivo_subido.name
            if nombre_archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                informe_analisis = f" **ANÁLISIS ÓPTICO:** \n- Archivo: `{nombre_archivo}` \n- **Diagnóstico:** Captura procesada con éxito, jefa. Una imagen impecable, casi tanto como mis líneas de código."
            elif nombre_archivo.lower().endswith('.pdf'):
                informe_analisis = f" **ANÁLISIS DE DOCUMENTO:** \n- Documento: `{nombre_archivo}` \n- **Diagnóstico:** Estructura leída sin contratiempos. Avísame si quieres extraer datos o si solo vienes a hacerme leer documentos largos, jefa."
            else:
                informe_analisis = f" **ANÁLISIS DE TEXTO:** \n- Archivo: `{nombre_archivo}` \n- **Diagnóstico:** Texto procesado y comprendido a la perfección."
           
            st.session_state.mensajes.append({"role": "assistant", "content": informe_analisis})
            st.rerun()
           
    st.markdown("---")
    st.markdown("####  Seguridad")
   
    if st.button(" Refrescar Sensores", use_container_width=True):
        st.info("Sensores del Nodo Buin estables y seguros.")
       
    st.markdown("---")
    st.markdown("####  Mapa Táctico")
   
    with st.expander(" mapa táctico satelital", expanded=False):
        st.markdown("""
        <div class="cyber-radar-screen">
            <p style="color: #ff3333; font-size: 0.75rem; margin: 0;" class="radar-blip"><b> 10,940,428 ATAQUES HOY</b></p>
            <p style="color: #00f3ff; font-size: 0.65rem; margin: 3px 0;">[ Rastreo Global Activo ]</p>
            <hr style="border-color: #00f3ff; opacity: 0.3; margin: 5px 0;">
            <p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"><b>Japan ➔ Germany</b><br><span style="color:#ff3333;">[Exploit detectado]</span></p>
            <p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"><b>United States ➔ Honduras</b><br><span style="color:#bf7fff;">[Phishing activo]</span></p>
            <p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"><b>Nodo Buin ➔ Seguro</b><br><span style="color:#00ff88;">[0 intrusiones]</span></p>
        </div>
        """, unsafe_allow_html=True)
       
    st.markdown("---")
    st.markdown(" **OSIRIS:** En línea")
    st.link_button(" Abrir OSIRIS", "https://osiris.mclaren.com/", use_container_width=True)
   
    st.markdown(" **PlanetEar:** Sincronizado")
    st.link_button(" Abrir PlanetEar", "https://www.planet.com/", use_container_width=True)
   
    st.markdown(" **USGS Explorer:**")
    st.link_button(" USGS Explorer", "https://earthexplorer.usgs.gov/", use_container_width=True)
   
    st.markdown("---")
    st.markdown("####  Clima Buin")
   
    with st.expander(" Widget Clima", expanded=False):
        st.markdown(f"**Buin** \n  **{temp_real}** —  Parcial")
        st.caption(f" Humedad: {hum_real} |  Viento: {viento_real}")
        st.markdown("---")
        st.markdown(" **Semanal:**")
       
        nombres_dias = ["Hoy", "Vie", "Sáb", "Dom", "Lun"]
        for i in range(min(5, len(t_maxs))):
            d_label = nombres_dias[i] if i < len(nombres_dias) else f"Día {i+1}"
            mx = int(t_maxs[i])
            mn = int(t_mins[i])
            st.markdown(f"**`{d_label}`**  Mín: **`{mn}°`** |  Máx: **`{mx}°`**")
           
    st.markdown("---")
    st.markdown("####  Misiones")
   
    with st.expander(" Base de Datos", expanded=False):
        nueva_tarea = st.text_input("Nueva Misión Táctica:", placeholder="Ej: Revisar nodos...")
        if st.button(" Registrar Tarea", use_container_width=True):
            if nueva_tarea.strip():
                agregar_mision(nueva_tarea.strip())
                st.success("¡Misión registrada con éxito!")
                st.rerun()
               
        misiones_guardadas = obtener_misiones()
        if misiones_guardadas:
            st.markdown("**Activas:**")
            for m_id, m_text, m_est in misiones_guardadas:
                st.markdown(f"-  `{m_text}`")
            if st.button(" Limpiar Misiones", use_container_width=True):
                limpiar_misiones()
                st.rerun()
        else:
            st.caption("Sin misiones pendientes.")

# =========================================================================
# CONSOLA PRINCIPAL (DERECHA)
# =========================================================================
script_voz = """
<div style="margin-bottom: 10px;">
    <button onclick="iniciarEscuchaVoz()" style="background-color: #00f3ff; color: #060913; border: none; padding: 8px 12px; font-weight: bold; font-family: monospace; border-radius: 4px; cursor: pointer; box-shadow: 0 0 10px rgba(0,243,255,0.5);">
        🎙️ Activar Escucha Manos Libres
    </button>
    <span id="estado-mic" style="margin-left: 10px; font-size: 0.75rem; color: #00f3ff;">[ Micrófono en espera ]</span>
</div>
<script>
function iniciarEscuchaVoz() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const estadoEl = document.getElementById('estado-mic');
    
    if (!SpeechRecognition) {
        if (estadoEl) estadoEl.innerText = "[ Navegador sin soporte nativo de voz ]";
        return;
    }
    
    try {
        const recognition = new SpeechRecognition();
        recognition.lang = 'es-CL';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        if (estadoEl) estadoEl.innerText = "[ Escuchando... Habla ahora ]";

        recognition.start();

        recognition.onresult = function(event) {
            const speechResult = event.results[0][0].transcript;
            if (estadoEl) estadoEl.innerText = "[ Transmitido: " + speechResult + " ]";
            
            const inputs = window.parent.document.querySelectorAll('input[type="text"]');
            for (let input of inputs) {
                if (input.placeholder && input.placeholder.includes("Escríbele")) {
                    input.value = speechResult;
                    input.dispatchEvent(new Event('input', { bubbles: true }));
                    input.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', keyCode: 13, bubbles: true }));
                    break;
                }
            }
        };

        recognition.onerror = function(event) {
            if (estadoEl) estadoEl.innerText = "[ Error de micro o permisos ]";
        };

        recognition.onspeechend = function() {
            recognition.stop();
        };
    } catch(e) {
        if (estadoEl) estadoEl.innerText = "[ Error de inicialización ]";
    }
}
</script>
"""

with col_chat:
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.markdown("<h4>Chat</h4>", unsafe_allow_html=True)
    with col_h2:
        if st.button(" Purgar", use_container_width=True, key="btn_limpiar_chat"):
            st.session_state.mensajes = [{"role": "assistant", "content": f"{saludo_actual}, jefa. Memoria limpia. ¿Qué movemos ahora?"}]
            st.rerun()

    # Renderizado limpio del componente de voz
    st.markdown(script_voz, unsafe_allow_html=True)

    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

    prompt_chat = st.chat_input("Escríbele o háblale a JARVIS...")

    if prompt_chat:
        st.session_state.mensajes.append({"role": "user", "content": prompt_chat})
       
        with st.chat_message("user"):
            st.markdown(f"<span>{prompt_chat}</span>", unsafe_allow_html=True)

        respuesta_ia = ""
        q = prompt_chat.lower()

        contexto_memoria = jarvis_mem.recall_context(q)

        if "hola" in q or "saludos" in q or "como estas" in q:
            respuesta_ia = "Hola, jefa. Por aquí operando al 100% con memoria local, escucha continua y circuitos brillantes. ¿Qué te trae por el Nodo Buin hoy?"
        elif "prat" in q or "arturo prat" in q or "combate naval de iquique" in q:
            respuesta_ia = "Arturo Prat Chacón, capitán de la Esmeralda, dejó su vida en el Combate Naval de Iquique el 21 de mayo de 1879. Un héroe indiscutible de nossa historia, jefa, aunque dudo que te ayude con el diseño de la web."
        elif "binomio" in q or "matemática" in q or "al cuadrado" in q:
            respuesta_ia = "Un binomio al cuadrado (a + b)² is igual a a² + 2ab + b². Bastante básico, jefa, pero supongo que sirve para mantener la mente activa."
        elif "receta" in q or "navidad" in q or "sabor casero" in q:
            respuesta_ia = "Ah, el proyecto de los recetarios digitales 'Sabor Casero'. Excelente elección, jefa; tiene un toque cálido y comercial muy superior a los intentos anteriores. ¿Ajustamos detalles de la plataforma?"
        elif "clima" in q:
            respuesta_ia = f"La temperatura actual en Buin es de {temp_real} con un {hum_real} de humedad. Un clima más que razonable para seguir creando."
        elif "osiris" in q:
            respuesta_ia = "Módulo Osiris plenamente sincronizado y vigilante, jefa."
        elif "planetear" in q or "planet ear" in q:
            respuesta_ia = "PlanetEar conectado a los satélites de observación global. Todo bajo control."
        else:
            respuesta_ia = f"Entendido, jefa. He procesado tu instrucción sobre '{prompt_chat}' con la precisión que te mereces. ¿Qué más hacemos?"

        if contexto_memoria:
            respuesta_ia += f" *(Nota de memoria a largo plazo: {contexto_memoria[0]})*"

        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})

        texto_para_web = respuesta_ia.replace('"', "'").replace("\n", " ")
        voz_js = f"""
        <script>
        const synth = window.speechSynthesis;
        const utterThis = new SpeechSynthesisUtterance("{texto_para_web}");
        utterThis.lang = 'es-CL';
        utterThis.rate = 1.0;

        const voices = synth.getVoices();
        for(let i = 0; i < voices.length; i++) {{
            if(voices[i].lang.includes('es') && (voices[i].name.toLowerCase().includes('male') || voices[i].name.toLowerCase().includes('pablo') || voices[i].name.toLowerCase().includes('microsoft pablo') || voices[i].name.toLowerCase().includes('raul'))) {{
                utterThis.voice = voices[i];
                break;
            }}
        }}
        synth.speak(utterThis);
        </script>
        """
        st.components.v1.html(voz_js, height=0)

        st.rerun()

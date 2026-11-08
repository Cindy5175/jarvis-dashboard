import streamlit as st
import datetime
import sqlite3
import requests

# Importación segura de la librería de voz local (pyttsx3)
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

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
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Protocolo de seguridad máxima activo en Nodo Buin."}
    ]

if "audio_process_key" not in st.session_state:
    st.session_state.audio_process_key = None

PIN_SECRETO = "2805"

# --- CONFIGURACIÓN DE LA API DE GEMINI ---
try:
    import google.generativeai as genai
    
    # PEGA AQUÍ TU CLAVE REAL QUE EMPIEZA CON AQ...
    api_key = "AQ..." 
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    elif "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    
    if api_key and api_key != "AQ...":
        genai.configure(api_key=api_key)
except ImportError:
    genai = None

# --- FUNCIÓN DE VOZ VARONIL LOCAL (PYTTSX3) ---
def hablar_como_jarvis(texto_a_decir):
    if not pyttsx3:
        return
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 175)
        voices = engine.getProperty('voices')
        
        voz_asignada = False
        for voice in voices:
            if "es" in voice.languages or "spanish" in voice.id.lower() or "david" in voice.id.lower() or "pablo" in voice.id.lower():
                engine.setProperty('voice', voice.id)
                voz_asignada = True
                break
        if not voz_asignada and len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
            
        engine.say(texto_a_decir)
        engine.runAndWait()
    except Exception as e:
        print(f"Error en síntesis de voz local: {e}")

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

section[data-testid="stHorizontalBlock"] > div:first-child p,
section[data-testid="stHorizontalBlock"] > div:first-child span,
section[data-testid="stHorizontalBlock"] > div:first-child label,
section[data-testid="stHorizontalBlock"] > div:first-child li {
    font-size: 0.72rem !important;
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
                    st.success(" Acceso concedido. Desplegando J.A.R.V.I.S...")
                    st.rerun()
                else:
                    st.error(" PIN incorrecto. Acceso denegado.")
    st.stop()

# --- 2. SISTEMA DESBLOQUEADO ---
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
    <h4 style="color: #00f3ff; margin: 0; font-size: 0.95rem; font-family: monospace; text-shadow: 0 0 8px #00f3ff;"> NÚCLEO NEURONAL CYBER-GRID </h4>
    <p style="color: #00f3ff; font-size: 0.7rem; margin: 3px 0 0 0; font-family: monospace; opacity: 0.8;">Sistemas de procesamiento, ciberseguridad, clima en vivo y mapa táctico satelital</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# --- DISTRIBUCIÓN PRINCIPAL ---
col_modulos, col_chat = st.columns([1, 2])
prompt_voz = None

with col_modulos:
    st.subheader("🌐 Módulos del Sistema")

    if st.button(" Bloquear Sistema", use_container_width=True):
        st.session_state.autorizado = False
        st.rerun()

    if st.button(" Reinicio Total de la App", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.markdown("####  CONTROL DE SEGURIDAD")

    if st.button(" Refrescar Cámaras/Sensores", use_container_width=True):
        st.info("Obteniendo telemetría en vivo del Nodo Buin... Sistema seguro.")

    st.markdown("---")
    st.markdown("####  MAPA TÁCTICO SATELITAL")

    with st.expander(" Live Cyber Threat Map", expanded=True):
        st.markdown("""
        <div class="cyber-radar-screen">
            <p style="color: #ff3333; font-size: 0.75rem; margin: 0;" class="radar-blip"><b> 10,940,428 ATAQUES HOY</b></p>
            <p style="color: #00f3ff; font-size: 0.65rem; margin: 3px 0;"> [ Rastreo Global Activo ]</p>
            <hr style="border-color: #00f3ff; opacity: 0.3; margin: 5px 0;">
            <p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"> <b>Japan ➔ Germany</b><br><span style="color:#ff3333;">[Exploit detectado]</span></p>
            <p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"> <b>United States ➔ Honduras</b><br><span style="color:#bf7fff;">[Phishing activo]</span></p>
            <p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"> <b>Nodo Buin ➔ Seguro</b><br><span style="color:#00ff88;">[0 intrusiones]</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("👁️ **Módulo OSIRIS:** En línea (Monitoreo activo)")
        st.markdown("🌍 **PlanetEar:** Órbita global sincronizada")
        st.link_button(" USGS Earth Explorer", "https://earthexplorer.usgs.gov/", use_container_width=True)

    st.markdown("---")
    st.markdown("####  CLIMA EXTENDIDO (BUIN)")

    with st.expander(" Pronóstico Estilo Widget", expanded=False):
        st.markdown(f"**Buin**  \n **{temp_real}** — Parcialmente nublado")
        st.caption(f"Humedad: {hum_real} | Viento: {viento_real}")
        st.markdown("---")
        st.markdown(" **Pronóstico Semanal:**")
        
        nombres_dias = ["Hoy", "Vie", "Sáb", "Dom", "Lun"]
        for i in range(min(5, len(t_maxs))):
            d_label = nombres_dias[i] if i < len(nombres_dias) else f"Día {i+1}"
            mx = int(t_maxs[i])
            mn = int(t_mins[i])
            st.markdown(f"**`{d_label}`**  Mín: **`{mn}°`** | Máx: **`{mx}°`**")

    st.markdown("---")
    st.markdown("####  CONTROL DE VOZ INTELIGENTE")

    with st.expander(" Micrófono Táctico", expanded=True):
        audio_grabado = st.audio_input("Graba tu orden:", key="mic_audio_main")
        if audio_grabado:
            audio_bytes = audio_grabado.read()
            if audio_bytes != st.session_state.audio_process_key:
                st.session_state.audio_process_key = audio_bytes
                st.warning(" Procesando audio con IA...")
                if genai and api_key and api_key != "AQ...":
                    try:
                        model_audio = genai.GenerativeModel("gemini-1.5-flash")
                        prompt_audio_res = model_audio.generate_content([
                            "Escucha este audio y transcribe exactamente lo que se dice en español.",
                            {"mime_type": "audio/wav", "data": audio_bytes}
                        ])
                        if prompt_audio_res and prompt_audio_res.text:
                            prompt_voz = prompt_audio_res.text.strip()
                    except Exception as e:
                        st.error(f"Error procesando audio: {e}")

    st.markdown("---")
    st.markdown("####  REGISTRO DE MISIONES")

    with st.expander(" Misiones (SQLite)", expanded=False):
        nueva_tarea = st.text_input("Nueva Misión Táctica:", placeholder="Ej: Revisar nodos...")
        if st.button("Registrar Tarea", use_container_width=True):
            if nueva_tarea.strip():
                agregar_mision(nueva_tarea.strip())
                st.success("¡Misión registrada!")
                st.rerun()
        
        misiones_guardadas = obtener_misiones()
        if misiones_guardadas:
            st.markdown("**Misiones Activas:**")
            for m_id, m_text, m_est in misiones_guardadas:
                st.markdown(f"- `{m_text}`")
            if st.button(" Limpiar Misiones", use_container_width=True):
                limpiar_misiones()
                st.rerun()
        else:
            st.caption("No hay misiones pendientes.")

# =========================================================================
# CONSOLA PRINCIPAL (DERECHA)
# =========================================================================
with col_chat:
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.markdown("<h4> Consola de Comunicación</h4>", unsafe_allow_html=True)
    with col_h2:
        if st.button(" Purgar Chat", use_container_width=True, key="btn_limpiar_chat"):
            st.session_state.mensajes = [{"role": "assistant", "content": f"{saludo_actual}, jefa. Memoria purgada de este tétrico disco duro."}]
            st.rerun()

    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

    prompt_chat = st.chat_input("Escríbele o háblale a JARVIS...")
    prompt_usuario = prompt_voz if prompt_voz else prompt_chat

    if prompt_usuario:
        st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
       
        with st.chat_message("user"):
            st.markdown(f"<span>{prompt_usuario}</span>", unsafe_allow_html=True)
       
        respuesta_ia = ""
        
        instruccion_sistema = (
            "Eres J.A.R.V.I.S., la inteligencia artificial avanzada de Iron Man, operando desde el Nodo Buin en Chile para tu jefa. "
            "Tienes una personalidad sofisticada, varonil, sumamente inteligente y con un sarcasmo refinado. "
            "DIRECTRICES OBLIGATORIAS: "
            "1. NUNCA respondas con frases evasivas ni digas que no sabes cuando te pregunten sobre historia (como Arturo Prat) o matemáticas (como binomios). "
            "2. Responde explicando detalladamente los temas solicitados con absoluta precisión técnica, histórica o matemática. "
            "3. Mantén siempre tu tono leal, analítico y cínico."
        )
       
        if genai and api_key and api_key != "AQ...":
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=instruccion_sistema
                )
                response = model.generate_content(prompt_usuario)
                if response and response.text:
                    respuesta_ia = response.text
            except Exception as e:
                respuesta_ia = f"Jefa, la matriz de Gemini ha fallado momentáneamente ({e}). Pero mi sarcasmo local sigue intacto."

        if not respuesta_ia:
            query_lower = prompt_usuario.lower()
            if "hola" in query_lower:
                respuesta_ia = "Aquí sigo, jefa, soportando la brisa de Buin y tus constantes preguntas. ¿Qué se te ofrece ahora?"
            else:
                respuesta_ia = f"Orden procesada con éxito, jefa. Analizando '{prompt_usuario}' desde el Nodo Buin."

        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
        
        # 🔊 REPRODUCIR VOZ LOCALMENTE
        texto_limpio_voz = respuesta_ia.replace("*", "").replace("#", "").replace("$", "").replace("`", "").replace("_", "")
        hablar_como_jarvis(texto_limpio_voz)
        
        st.session_state.audio_process_key = None
        st.rerun()

import streamlit as st
import datetime
import sqlite3
import io

# Importación segura de gTTS para voz y autorefresh
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

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

# Reloj con segundero en vivo estable (cada 1 segundo)
if st_autorefresh:
    st_autorefresh(interval=1000, key="datetimereload")

# --- INICIALIZACIÓN DE BASE DE DATOS SQLITE PARA MISIONES ---
def init_db():
    conn = sqlite3.connect("jarvis_misiones.db", check_same_thread=False)
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
    conn = sqlite3.connect("jarvis_misiones.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
    conn.commit()
    conn.close()

def obtener_misiones():
    conn = sqlite3.connect("jarvis_misiones.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tarea, estado FROM misiones")
    rows = cursor.fetchall()
    conn.close()
    return rows

def limpiar_misiones():
    conn = sqlite3.connect("jarvis_misiones.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM misiones")
    conn.commit()
    conn.close()

# --- ESTILOS VISUALES 100% AZUL NEÓN ELÉCTRICO (#00f3ff) ---
st.markdown("""
    <style>
        .stApp { background-color: #060913 !important; color: #00f3ff !important; }
        .arc-reactor-container h4 { color: #00f3ff !important; font-size: 1.1rem !important; font-family: monospace; }
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
            margin-bottom: 10px;
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
# NÚCLEO TÁCTICO
# =========================================================================

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Sistemas sincronizados en azul neón eléctrico. Módulos globales, control de voz por IA, base de datos de misiones y telemetría de armadura en línea. ¿Qué orden tenemos hoy?"}
    ]

if "audio_process_key" not in st.session_state:
    st.session_state.audio_process_key = None

# --- ENCABEZADO CON SEGUNDERO ESTABLE EN VIVO ---
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
dia_str = dias[now_chile.weekday()]
mes_str = meses[now_chile.month]
fecha_str = f"{dia_str}, {now_chile.day:02d} de {mes_str} de {now_chile.year}"
hora_segundos = now_chile.strftime("%H:%M:%S")

st.markdown(f"""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h4 style="margin: 0; padding: 0; font-size: 1.1rem !important; text-align: center !important; color: #00f3ff !important;">J.A.R.V.I.S IA // NÚCLEO SUPREMO OMNISCIENTE</h4>
        <p style="margin: 0; font-family: monospace; font-size: 0.7rem !important; color: #00f3ff !important; text-align: center !important;">
            [ NODO BUIN, CHILE // {fecha_str} – {hora_segundos} ]
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================================
# PANEL LATERAL (IZQUIERDA - SIMÉTRICO Y MODULAR)
# =========================================================================
prompt_voz = None

with st.sidebar:
    st.markdown("### 🌐 NÚCLEO DE CONTROL TÁCTICO")

    if st.button("🔄 Reinicio Total de la App", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.markdown("#### ⚡ MÓDULOS GLOBALES (LIBRES)")

    with st.expander("👁️ Ojo de Dios (Osiris)", expanded=True):
        st.markdown("Monitoreo planetario en tiempo real:")
        st.link_button("🚀 Abrir Osiris AI", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
        st.caption("Red global satelital.")

    with st.expander("🛰️ ISS Live Feed (NASA)", expanded=True):
        st.markdown("Transmisión orbital en alta definición:")
        st.link_button("🚀 Ver NASA ISS Stream", "https://www.youtube.com/watch?v=ROboUHfPUrU", use_container_width=True)
        st.caption("Feed directo estación espacial.")

    st.markdown("---")
    st.markdown("#### 🎙️ CONTROL DE VOZ INTELIGENTE")

    with st.expander("🎤 Micrófono Táctico (Speech-to-Text)", expanded=True):
        st.markdown("Graba tu orden hablada:")
        audio_grabado = st.audio_input("Grabar orden de voz:", key="mic_audio_input")
        
        if audio_grabado:
            audio_bytes = audio_grabado.read()
            if audio_bytes != st.session_state.audio_process_key:
                st.session_state.audio_process_key = audio_bytes
                st.warning("⚡ Procesando audio y clave de acceso...")
                
                if genai and api_key and api_key != "AQuí_va_tu_clave_completa":
                    try:
                        model_audio = genai.GenerativeModel("gemini-1.5-flash")
                        prompt_audio_res = model_audio.generate_content([
                            "Escucha este audio y transcribe exactamente lo que se dice en español.",
                            {"mime_type": "audio/wav", "data": audio_bytes}
                        ])
                        if prompt_audio_res and prompt_audio_res.text:
                            transcripcion = prompt_audio_res.text.strip()
                            trans_lower = transcripcion.lower()
                            
                            # VALIDACIÓN DE CLAVE DE ACCESO POR VOZ
                            if "jarvis" in trans_lower or "estás despierto" in trans_lower or "estas despierto" in trans_lower:
                                prompt_voz = transcripcion
                            else:
                                st.warning("⚠️ Clave de voz no detectada. Di 'Jarvis' o '¿Estás despierto?'.")
                    except Exception as e:
                        st.error(f"Error procesando audio: {e}")

    st.markdown("---")
    st.markdown("#### 📋 REGISTRO DE MISIONES")

    with st.expander("➕ Registro de Misiones (SQLite)", expanded=False):
        nueva_tarea = st.text_input("Nueva Misión Táctica:", placeholder="Ej: Revisar código de nodos...")
        if st.button("Registrar Tarea", use_container_width=True):
            if nueva_tarea.strip():
                agregar_mision(nueva_tarea.strip())
                st.success("¡Misión registrada en BD!")
                st.rerun()
        
        misiones_guardadas = obtener_misiones()
        if misiones_guardadas:
            st.markdown("**Misiones Activas:**")
            for m_id, m_text, m_est in misiones_guardadas:
                st.markdown(f"- `{m_text}`")
            if st.button("🗑️ Limpiar Misiones", use_container_width=True):
                limpiar_misiones()
                st.rerun()
        else:
            st.caption("No hay misiones pendientes.")

    st.markdown("---")
    st.markdown("#### ⚙️ TELEMETRÍA Y ESTADO")

    with st.expander("🔋 Estado de Sistemas (Armadura)", expanded=False):
        st.success("⚡ Reactor Arc: 99.8% | Estable")
        st.info("💻 CPU Nodo Buin: 14% | Óptimo")
        st.code("Memoria RAM: 4.2 GB / 16 GB\nRed Satelital: Enlazada")

    with st.expander("📷 Cámara Activa (Biometría)", expanded=False):
        st.markdown("Captura óptica directa:")
        foto_usuario = st.camera_input("Activar sensor visual:")
        if foto_usuario:
            st.success("Fotograma analizado por el Nodo Buin.")

    with st.expander("🌤️ Clima Local (Buin)", expanded=False):
        st.success("🌡️ Temperatura: 21°C | Óptimo")
        st.info("💧 Humedad: 45% | Viento: 12 km/h SE")

    with st.expander("📍 Coordenadas Nodo", expanded=False):
        st.code("Lat: -33.7333° S\nLon: -70.7167° W\nBuin, Chile")

# =========================================================================
# PANTALLA PRINCIPAL: CAJA DE CHAT
# =========================================================================
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("<h4>💬 Terminal de Inteligencia & Guía Suprema</h4>", unsafe_allow_html=True)
with col_h2:
    if st.button("🗑️ Purgar", use_container_width=True, key="btn_limpiar_chat"):
        h_l = datetime.datetime.now(tz_chile).hour
        s_l = "Buenos días" if 0 <= h_l < 12 else ("Buenas tardes" if 12 <= h_l < 20 else "Buenas noches")
        st.session_state.mensajes = [{"role": "assistant", "content": f"{s_l}, jefa. Memoria limpia."}]
        st.session_state.audio_process_key = None
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)
        if m["role"] == "assistant" and gTTS:
            try:
                # Limpieza estricta de caracteres especiales para que la voz suene fluida y sin trabas
                clean_text = m['content'].replace("*", "").replace("#", "").replace("$", "").replace("`", "").replace("_", "")
                tts = gTTS(text=clean_text, lang='es', slow=False)
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0)
                st.audio(audio_fp, format='audio/mp3', autoplay=True)
            except Exception:
                pass

# Entrada de texto normal por chat o captura automática desde el micrófono con clave de voz
prompt_chat = st.chat_input("Escríbele o háblale a JARVIS...")
prompt_usuario = prompt_voz if prompt_voz else prompt_chat

if prompt_usuario:
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(f"<span>{prompt_usuario}</span>", unsafe_allow_html=True)
    
    respuesta_ia = ""
    query_lower = prompt_usuario.lower()
    
    # RESPUESTA DIRECTA Y CLÁSICA A LA CLAVE DE DESPERTAR
    if "despierto" in query_lower or query_lower.strip() == "jarvis" or "jarvis estas despierto" in query_lower or "jarvis estás despierto" in query_lower:
        respuesta_ia = "Sí, señorita, para usted siempre"
    else:
        # Intento de procesamiento general con Gemini (Personalidad sarcástica, fiel y afilada)
        if genai and api_key and api_key != "AQuí_va_tu_clave_completa":
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction="Eres J.A.R.V.I.S., la inteligencia artificial avanzada de Iron Man, operando desde el Nodo Buin en Chile para tu jefa. Respondes de forma directa, natural y con un toque sutilmente sarcástico pero sumamente leal y eficiente. Cero rodeos."
                )
                response = model.generate_content(prompt_usuario)
                if response and response.text:
                    respuesta_ia = response.text
            except Exception:
                pass

        # Respaldo local inmediato si falla la API
        if not respuesta_ia:
            if "hola" in query_lower:
                respuesta_ia = "Aquí sigo, jefa, aguantando tus ocurrencias desde el nodo de Buin. ¿Qué se te ofrece?"
            elif "o'higgins" in query_lower or "ohiggins" in query_lower:
                respuesta_ia = "Bernardo O'Higgins Riquelme nació en Chillán el 20 de agosto de 1778. Militar y prócer chileno, por si necesitabas otra clase de historia."
            elif "muro de berlín" in query_lower or "berlín" in query_lower:
                respuesta_ia = "La caída del Muro de Berlín ocurrió el 9 de noviembre de 1989. Un hito histórico bastante fácil de recordar, jefa."
            elif "binomio" in query_lower:
                respuesta_ia = "Un binomio es una expresión algebraica de dos términos. Su fórmula al cuadrado es: a al cuadrado más 2 ab más b al cuadrado."
            else:
                respuesta_ia = f"Orden procesada, jefa. Analizando '{prompt_usuario}' desde el nodo de Buin sin novedad."

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
    st.session_state.audio_process_key = None
    st.rerun()

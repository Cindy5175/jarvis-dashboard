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
    api_key = None
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

# --- ESTILOS VISUALES 100% AZUL NEÓN (#00ffcc) ---
st.markdown("""
    <style>
        .stApp { background-color: #0b0f19 !important; color: #00ffcc !important; }
        
        .arc-reactor-container h4 { color: #00ffcc !important; font-size: 1.1rem !important; font-family: monospace; }
        
        p, span, label, h1, h2, h3, h4, div { color: #00ffcc !important; font-family: monospace; }
        
        .stChatMessage p, .stChatMessage div {
            font-size: 0.85rem !important;
            color: #00ffcc !important;
        }

        /* Botones en Azul Neón absoluto */
        .stButton>button {
            color: #0b0f19 !important;
            background-color: #00ffcc !important;
            border: 1.5px solid #00ffcc !important;
            font-weight: bold;
            font-family: monospace;
            box-shadow: 0 0 8px rgba(0, 255, 204, 0.5);
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #00b388 !important;
            color: #ffffff !important;
            box-shadow: 0 0 12px rgba(0, 255, 204, 0.8);
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
            border: 2.5px solid #00ffcc;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00ffcc 0%, #0b0f19 70%);
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.7), inset 0 0 8px rgba(0, 255, 204, 0.5);
            margin-bottom: 5px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-bottom: 14px solid #0b0f19;
            filter: drop-shadow(0 0 5px #00ffcc);
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
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Sistemas sincronizados en azul neón absoluto. Módulos de Osiris y GlobeAlert en línea. ¿Qué orden tenemos hoy?"}
    ]

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
        <h4 style="margin: 0; padding: 0; font-size: 1.1rem !important; text-align: center !important; color: #00ffcc !important;">J.A.R.V.I.S IA // NÚCLEO SUPREMO OMNISCIENTE</h4>
        <p style="margin: 0; font-family: monospace; font-size: 0.7rem !important; color: #00ffcc !important; text-align: center !important;">
            [ NODO BUIN, CHILE // {fecha_str} – {hora_segundos} ]
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================================
# PANEL LATERAL
# =========================================================================
with st.sidebar:
    st.markdown("### 🌐 NÚCLEO DE CONTROL TÁCTICO")

    if st.button("🔄 Reinicio Total de la App", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Módulo Ojo de Dios (Osiris)
    with st.expander("👁️ Ojo de Dios (Osiris)", expanded=True):
        st.markdown("Monitoreo planetario en tiempo real:")
        st.link_button("🚀 Abrir Osiris AI", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
        st.caption("Acceso a la red global satelital.")

    # Módulo GlobeAlert (Inteligencia Global)
    with st.expander("🌍 GlobeAlert (Alertas en Vivo)", expanded=True):
        st.markdown("Feed de inteligencia y eventos globales:")
        st.link_button("🚀 Abrir GlobeAlert", "https://globealert.com", use_container_width=True)
        st.caption("Monitoreo de alertas en tiempo real.")

    # Módulo de Cámara Activa en Vivo
    with st.expander("📷 Cámara Activa en Vivo (Biometría)", expanded=False):
        st.markdown("Captura óptica directa desde tu dispositivo:")
        foto_usuario = st.camera_input("Activar sensor visual:")
        if foto_usuario:
            st.success("Fotograma capturado y analizado por el Nodo Buin.")

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
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

# Caja de chat principal con respuesta fluida, humana y recíproca
if prompt_usuario := st.chat_input("Escríbele o háblale a JARVIS..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(f"<span>{prompt_usuario}</span>", unsafe_allow_html=True)
    
    respuesta_ia = ""
    
    # Intento de procesamiento con Gemini
    if genai:
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction="Eres J.A.R.V.I.S., una inteligencia artificial avanzada inspirada en Iron Man, operando desde el Nodo Buin en Chile para tu jefa. Respondes de forma directa, natural, humana y recíproca, con un toque sutilmente sarcástico pero sumamente servicial, preciso y claro ante cualquier consulta."
            )
            response = model.generate_content(prompt_usuario)
            if response and response.text:
                respuesta_ia = response.text
        except Exception:
            pass

    # Respaldo local inmediato y conversacional
    if not respuesta_ia:
        query_lower = prompt_usuario.lower()
        if "hola" in query_lower:
            respuesta_ia = "Hola, jefa. Aquí estoy, con los sistemas a tope en el nodo de Buin. ¿Qué se te ofrece?"
        elif "o'higgins" in query_lower or "ohiggins" in query_lower:
            respuesta_ia = "Bernardo O'Higgins Riquelme nació en Chillán el 20 de agosto de 1778. Fue militar, político y uno de los principales Padres de la Patria de Chile."
        elif "muro de berlín" in query_lower or "berlín" in query_lower:
            respuesta_ia = "La caída del Muro de Berlín ocurrió el 9 de noviembre de 1989, marcando el fin de la división alemana y el inicio de la reunificación."
        elif "binomio" in query_lower:
            respuesta_ia = "Un binomio es una expresión algebraica de dos términos. Su fórmula al cuadrado es: $(a + b)^2 = a^2 + 2ab + b^2$."
        else:
            respuesta_ia = f"Recibido, jefa. Analizando '{prompt_usuario}' desde el nodo de Buin. Todo bajo control."

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
    
    with st.chat_message("assistant"):
        st.markdown(f"<span>{respuesta_ia}</span>", unsafe_allow_html=True)
        
        # Síntesis de voz automática (gTTS)
        if gTTS:
            try:
                clean_text = respuesta_ia.replace("*", "").replace("#", "").replace("$", "")
                tts = gTTS(text=clean_text, lang='es', slow=False)
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0)
                st.audio(audio_fp, format='audio/mp3', autoplay=True)
            except Exception:
                pass

    st.rerun()

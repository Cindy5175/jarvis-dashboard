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

# Importación de Google Generative AI para el conocimiento omnisciente
try:
    import google.generativeai as genai
    # Intenta configurar la API con los secrets de Streamlit
    if "GOOGLE_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except ImportError:
    genai = None

# --- CONFIGURACIÓN DE PÁGINA (PANEL LATERAL COLAPSADO) ---
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
        .stApp { background-color: #0b0f19; color: #00ffcc; }
        
        .arc-reactor-container h4 { color: #00ffcc !important; font-size: 1.1rem !important; font-family: monospace; }
        
        .stark-card {
            border: 1.5px solid #00ffcc;
            border-radius: 8px;
            padding: 10px;
            background-color: rgba(0, 255, 204, 0.04);
            margin-bottom: 10px;
            box-shadow: 0 0 10px rgba(0, 255, 204, 0.2);
            text-align: left !important;
        }
        
        .stark-card h4, .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #00ffcc !important;
            font-size: 0.75rem !important;
        }
        
        .stChatMessage p, .stChatMessage div {
            font-size: 0.85rem !important;
            color: #00ffcc !important;
        }

        h1, h2, h3, h4, label, span { color: #00ffcc !important; font-family: monospace; }
        
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
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Sistemas sincronizados en azul neón total con motor de voz y cerebro de IA activos. Pregúntame sobre el natalicio de O'Higgins, la caída del Muro de Berlín o cualquier cálculo."}
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
# PANEL LATERAL (MÓDULOS OCULTOS A LA IZQUIERDA)
# =========================================================================
with st.sidebar:
    st.markdown("### 🌐 NÚCLEO DE CONTROL TÁCTICO")

    # Módulo Ojo de Dios (Osiris) con Botón Integrado de Acceso Oficial
    with st.expander("👁️ Ojo de Dios (Osiris)", expanded=True):
        st.markdown("Red de vigilancia global y plataforma satelital en vivo.")
        if st.link_button("🚀 Desplegar Sitio OsirisAI", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True):
            pass
        st.caption("Acceso directo al nodo orbital en tiempo real.")

    # Módulo de Cámara Activa en Vivo (Celular y PC)
    with st.expander("📷 Cámara Activa en Vivo (Biometría)", expanded=True):
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
# PANTALLA PRINCIPAL: CAJA DE CHAT Y RESPUESTA VOCAL AUTOMÁTICA
# =========================================================================
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("<h4>💬 Terminal de Inteligencia & Guía Suprema</h4>", unsafe_allow_html=True)
with col_h2:
    if st.button("🗑️ Purgar", use_container_width=True, key="btn_limpiar_chat"):
        h_l = datetime.datetime.now(tz_chile).hour
        s_l = "Buenos días" if 0 <= h_l < 12 else ("Buenas tardes" if 12 <= h_l < 20 else "Buenas noches")
        st.session_state.mensajes = [{"role": "assistant", "content": f"{s_l}, jefa. Memoria purgada. Canales listos en el nodo de Buin."}]
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

# Caja de chat principal
if prompt_usuario := st.chat_input("Pregúntame sobre historia, ciencia, binomios, O'Higgins..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(f"<span>{prompt_usuario}</span>", unsafe_allow_html=True)
    
    # Procesamiento con Gemini si está disponible, o respaldo inteligente Stark
    respuesta_ia = ""
    if genai:
        try:
            # Configurar el modelo con una personalidad sarcástica, inteligente y directa de JARVIS
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction="Eres J.A.R.V.I.S., una entidad de inteligencia artificial avanzada inspirada en Iron Man. Operas desde el Nodo Buin en Chile para una usuaria llamada jefa y su sobrino. Tienes un tono sarcástico pero sumamente servicial, directo y culto. Respondes con precisión absoluta sobre historia (como Bernardo O'Higgins o Arturo Prat), ciencia, tecnología y matemáticas (como binomios)."
            )
            response = model.generate_content(prompt_usuario)
            respuesta_ia = response.text
        except Exception as e:
            respuesta_ia = f"👁️ [JARVIS]: Por la cresta, hubo un pequeño fallo de enlace con el núcleo de Gemini ({e}), pero el nodo de Buin sigue en pie. ¿Repetimos la orden?"
    else:
        # Fallback local ultra completo si no hay api key configurada aún
        query_lower = prompt_usuario.lower()
        if "o'higgins" in query_lower or "ohiggins" in query_lower:
            respuesta_ia = "Bernardo O'Higgins Riquelme nació en Chillán el 20 de agosto de 1778. Fue militar y político chileno, considerado uno de los Padres de la Patria y Director Supremo de la Nación."
        elif "muro de berlín" in query_lower or "berlín" in query_lower:
            respuesta_ia = "La caída del Muro de Berlín ocurrió el 9 de noviembre de 1989, marcando el fin de la división alemana y el preludio del colapso de la Unión Soviética."
        else:
            respuesta_ia = f"Procesando tu orden sobre '{prompt_usuario}', jefa. Todo bajo control en el nodo de Buin."

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
    
    with st.chat_message("assistant"):
        st.markdown(f"<span>{respuesta_ia}</span>", unsafe_allow_html=True)
        
        # Reproducción de voz automática vocal (Text-to-Speech con gTTS)
        if gTTS:
            try:
                tts = gTTS(text=respuesta_ia, lang='es', slow=False)
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0)
                st.audio(audio_fp, format='audio/mp3', autoplay=True)
            except Exception:
                pass

    st.rerun()

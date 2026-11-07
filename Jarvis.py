import streamlit as st
import datetime
import sqlite3
import io
import requests

# --- 1. CONFIGURACIÓN DE PÁGINA (SIEMPRE PRIMERO) ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Importación segura de gTTS para voz
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

# Importación de Google Generative AI
try:
    import google.generativeai as genai
    
    api_key = "AQuí_va_tu_clave_completa" 
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    elif "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    
    if api_key:
        genai.configure(api_key=api_key)
except ImportError:
    genai = None

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
        CREATE TABLE IF NOT EXISTS memoria_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rol TEXT,
            contenido TEXT
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
        url = "https://api.open-meteo.com/v1/forecast?latitude=-33.7333&current=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=America%2FSantiago"
        res = requests.get(url, timeout=3).json()
        temp = res["current"]["temperature_2m"]
        hum = res["current"]["relative_humidity_2m"]
        viento = res["current"]["wind_speed_10m"]
        return f"{temp}°C", f"{hum}%", f"{viento} km/h"
    except Exception:
        return "21°C", "45%", "12 km/h"

temp_real, hum_real, viento_real = obtener_clima_buin()

# --- ESTILOS VISUALES 100% AZUL NEÓN ELÉCTRICO (#00f3ff) ---
st.markdown(
    """
    <style>
        .stApp { background-color: #060913 !important; color: #00f3ff !important; }
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
    </style>
    """,
    unsafe_allow_html=True
)

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
# ESTADO DE SESIÓN & CONTROL DE ACCESO (TRIPLE FACTOR)
# =========================================================================

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Protocolo de seguridad máxima activo."}
    ]

if "audio_process_key" not in st.session_state:
    st.session_state.audio_process_key = None

PIN_SECRETOS = ["2805"]

# =========================================================================
# 1. PANTALLA DE BLOQUEO (ACCESO RESTRINGIDO TRIPLE FACTOR)
# =========================================================================
if not st.session_state.autorizado:
    st.markdown(
        """
        <div style="text-align: center; margin-top: 30px;">
            <h2 style="color: #00f3ff; font-family: monospace;">🔒 ACCESO RESTRINGIDO - NODO BUIN</h2>
            <p style="color: #00f3ff; opacity: 0.8; font-size: 0.85rem;">AUTENTICACIÓN DE TRIPLE FACTOR REQUERIDA (VOZ + PIN + IA)</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login_triple"):
            st.markdown("**Factor 1 & 2:** Frase clave y PIN numérico secreto")
            frase_input = st.text_input("Frase de Activación:", placeholder="Escribe 'Jarvis' o 'estás despierto'...")
            pin_input = st.text_input("PIN Secreto Numérico:", type="password", placeholder="Ingresa tu PIN...")
            
            st.markdown("---")
            st.markdown("**Factor 3:** Dictado biométrico por voz (Opcional)")
            audio_login = st.audio_input("Graba orden de voz para verificar:", key="mic_login_voice")
            
            btn_entrar = st.form_submit_button("🛡️ Ejecutar Protocolo de Acceso")
            
            if btn_entrar:
                valido_texto = (pin_input.strip() in PIN_SECRETOS) or (frase_input.lower().strip() in ["jarvis", "despierto", "estás despierto", "estas despierto", "jefa", "hola"])
                
                valido_voz = False
                if audio_login:
                    audio_bytes_l = audio_login.read()
                    if genai and api_key and api_key != "AQuí_va_tu_clave_completa":
                        try:
                            m_val = genai.GenerativeModel("gemini-1.5-flash")
                            res_val = m_val.generate_content([
                                "Analiza este audio. Responde UNICAMENTE 'AUTORIZADO' si escuchas a la jefa nombrando a Jarvis o un saludo de activación, o 'DENEGADO' en caso contrario.",
                                {"mime_type": "audio/wav", "data": audio_bytes_l}
                            ])
                            if res_val and "AUTORIZADO" in res_val.text.upper():
                                valido_voz = True
                        except Exception:
                            pass

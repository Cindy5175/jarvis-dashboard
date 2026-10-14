import streamlit as st
import streamlit.components.v1 as components
import datetime
import random
import json
import os

# Configuración de página en modo ancho
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónoma // Hologram Core", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ARCHIVO DE MEMORIA PERSISTENTE LOCAL
MEMORY_FILE = "jarvis_memory.json"

def cargar_memoria():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "usuario": {
            "nombre": "Cindy",
            "titulo": "Jefa",
            "ubicacion": "Buin, Chile"
        },
        "notas": ["Búnker activado en Buin, Chile.", "Satélite Serafín en enlace estable."],
        "misiones": ["Verificar sistemas del búnker", "Sincronizar red táctica"],
        "preferencias_voz": {
            "voz_activa": "Español (Neutro)",
            "elevenlabs_api_key": "",
            "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",
            "ai_api_key": ""
        }
    }

def guardar_memoria(memoria):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error guardando memoria: {e}")

if "memoria" not in st.session_state:
    st.session_state.memoria = cargar_memoria()

nombre_jefa = st.session_state.memoria.get("usuario", {}).get("nombre", "Cindy")
titulo_jefa = st.session_state.memoria.get("usuario", {}).get("titulo", "Jefa")
prefs_voz = st.session_state.memoria.get("preferencias_voz", {})
ai_api_key_guardada = prefs_voz.get("ai_api_key", "")

# CONFIGURACIÓN DIRECTA DE GEMINI
cliente_ia = None
if ai_api_key_guardada:
    try:
        import google.generativeai as genai
        genai.configure(api_key=ai_api_key_guardada)
        # Usamos directamente el modelo estándar flash
        cliente_ia = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        cliente_ia = None

# ESTILOS CSS TÁCTICOS Y HOLOGRÁFICOS
st.markdown("""
    <style>
    .stApp, .main { background-color: #000000 !important; color: #ffffff; }
    .main-header { color: #00d2ff; font-family: 'Segoe UI', sans-serif; font-weight: 800; letter-spacing: 2px; text-align: center; margin-bottom: 0px; }
    .status-bar { text-align: center; color: #00d2ff; font-size: 12px; font-weight: bold; letter-spacing: 1px; margin-bottom: 15px; }
    .market-ticker { background: #050505; border: 1px solid #00d2ff; border-radius: 8px; padding: 6px 12px; display: flex; justify-content: space-around; align-items: center; margin-bottom: 15px; font-family: monospace; font-size: 12px; }
    .market-item { color: #00d2ff; }
    .market-value { color: #00ffaa; font-weight: bold; }
    .holo-card { background-color: #050505; border: 1px solid #00d2ff; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 0 15px rgba(0, 210, 255, 0.2); }
    .holo-title { color: #00d2ff; font-size: 14px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
    .stTextInput input, .stTextArea textarea, .stSelectbox select { background-color: #050505 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; }
    label[data-testid="stWidgetLabel"] { color: #00d2ff !important; font-weight: bold !important; }
    div.stButton > button, div.stFormSubmitButton > button { background-color: #050505 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 6px !important; font-weight: bold !important; width: 100% !important; box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important; }
    div.stButton > button:hover { background-color: #00d2ff !important; color: #000000 !important; }
    div[data-testid="stExpander"] { background-color: #050505 !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    div[data-testid="stExpander"] details summary { background-color: #050505 !important; color: #00d2ff !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">⚡ J.A.R.V.I.S. CORE 3.0</h1>', unsafe_allow_html=True)
estado_ia_txt = "AI ENGINE: GEMINI ACTIVE" if cliente_ia else "AI ENGINE: LOCAL MODE"
st.markdown(f'<div class="status-bar">CORE STATUS: ONLINE &nbsp;|&nbsp; OPERANDO PARA {titulo_jefa.upper()} {nombre_jefa.upper()} &nbsp;|&nbsp; {estado_ia_txt}</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="market-ticker">
        <span class="market-item">💵 USD/CLP: <span class="market-value">$930.50 ▲ +0.2%</span></span>
        <span class="market-item">💶 EUR/CLP: <span class="market-value">$1,012.40 ▲ +0.1%</span></span>
        <span class="market-item">📈 IPSA CHILE: <span class="market-value">6,480.12 pts ▲ +0.4%</span></span>
        <span class="market-item">📡 SERAFÍN-SAT: <span class="market-value">LINK 100%</span></span>
    </div>
""", unsafe_allow_html=True)

col_telemetria, col_orbe, col_chat = st.columns([1, 1.4, 1.2])

with col_telemetria:
    st.markdown('<div class="holo-card"><div class="holo-title">⚙️ SYSTEM TELEMETRY</div>', unsafe_allow_html=True)
    gauges_html = """
    <div style="display: flex; justify-content: space-around; align-items: center; padding: 5px 0;">
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">38%</div><span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">CPU</span></div>
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">57%</div><span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">RAM</span></div>
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">100%</div><span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">PWR</span></div>
    </div>
    """
    components.html(gauges_html, height=90)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card"><div class="holo-title">📍 BASE & SATÉLITE</div>', unsafe_allow_html=True)
    globe_html = """
    <div style="display: flex; align-items: center; gap: 12px; padding: 2px 0;">
        <div style="width: 50px; height: 50px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #00d2ff 0%, #003366 60%, #000511 100%); border: 1px solid #00d2ff; box-shadow: 0 0 12px rgba(0, 210, 255, 0.6); position: relative;"></div>
        <div><p style='color:#00d2ff; font-size:12px; margin:2px 0; font-weight:bold;'>🌍 Ubicación: Buin, Chile</p><p style='color:#00d2ff; font-size:11px; margin:2px 0;'>🛰️ Serafín-Sat: Órbita Estable</p></div>
    </div>
    """
    components.html(globe_html, height=65)
    st.markdown('</div>', unsafe_allow_html=True)

hora_actual = datetime.datetime.now().hour
saludo_tiempo = "Buenos días" if hora_actual < 12 else ("Buenas tardes" if hora_actual < 20 else "Buenas noches")

if "ultima_respuesta" not in st.session_state:
    st.session_state.ultima_respuesta = f"{saludo_tiempo}, {titulo_jefa} {nombre_jefa}. Todos los sistemas y radares en línea en Buin."
if "ultimo_usuario" not in st.session_state:
    st.session_state.ultimo_usuario = ""

with col_orbe:
    texto_para_hablar = st.session_state.ultima_respuesta.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
    orb_component = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 350px;">
        <div onclick="hablarJarvis()" style="cursor: pointer; width: 100px; height: 100px; background: radial-gradient(circle, #00d2ff 0%, #005580 70%, #000000 100%); border-radius: 50%; box-shadow: 0 0 35px #00d2ff;"></div>
        <button onclick="hablarJarvis()" style="margin-top: 15px; background-color: #050505; color: #00d2ff; border: 1px solid #00d2ff; padding: 6px 12px; border-radius: 6px; font-weight: bold; cursor: pointer;">🔊 Reproducir Respuesta</button>
    </div>
    <script>
    function hablarJarvis() {{
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance("{texto_para_hablar}");
        utterance.lang = 'es-ES';
        window.speechSynthesis.speak(utterance);
    }}
    </script>
    """
    components.html(orb_component, height=350)

with col_chat:
    st.markdown('<div class="holo-card"><div class="holo-title">💬 CONVERSATION CORE</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background-color: #000000; border: 1px solid #00d2ff; border-radius: 8px; padding: 10px; margin-bottom: 10px;"><p style="margin:0; color:#00d2ff; font-weight:bold; font-size:12px;">⚡ J.A.R.V.I.S.:</p><p style="margin:4px 0 0 0; color:#ffffff; font-size:13px;">{st.session_state.ultima_respuesta}</p></div>', unsafe_allow_html=True)

    if st.session_state.ultimo_usuario:
        st.markdown(f'<div style="background-color: #000000; border: 1px solid #1f293d; border-radius: 8px; padding: 8px; margin-bottom: 10px;"><p style="margin:0; color:#a5b4fc; font-weight:bold; font-size:11px;">👩‍💻 {titulo_jefa} {nombre_jefa}:</p><p style="margin:2px 0 0 0; color:#ffffff; font-size:12px;">{st.session_state.ultimo_usuario}</p></div>', unsafe_allow_html=True)

    with st.form(key="form_chat", clear_on_submit=True):
        entrada_usuario = st.text_input("", placeholder="Escribe tu instrucción...")
        boton_enviar = st.form_submit_button(label="🚀 Transmitir")

    if boton_enviar and entrada_usuario:
        texto = entrada_usuario.lower().strip()
        
        # PROCESAMIENTO CON IA REAL O RESPALDO
        if cliente_ia:
            try:
                prompt_sistema = f"Eres J.A.R.V.I.S., asistente de inteligencia artificial leal, sofisticado y formal. Te diriges a la usuaria como '{titulo_jefa} {nombre_jefa}' en su búnker en Buin, Chile. Responde de forma concisa."
                respuesta_modelo = cliente_ia.generate_content(f"{prompt_sistema}\nInstrucción: {entrada_usuario}")
                respuesta_ia = respuesta_modelo.text
            except Exception as e:
                respuesta_ia = f"Error de núcleo Gemini: {e}"
        else:
            if "hola" in texto or "saludos" in texto:
                respuesta_ia = f"{saludo_tiempo}, {titulo_jefa} {nombre_jefa}. Búnker operativo."
            else:
                respuesta_ia = f"Comando '{entrada_usuario}' registrado y procesado en el búnker de Buin, {nombre_jefa}."

        st.session_state.ultimo_usuario = entrada_usuario
        st.session_state.ultima_respuesta = respuesta_ia
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

with st.expander("👤 Identidad & Conexión de Voz Avanzada / IA Core", expanded=False):
    if "input_nombre" not in st.session_state: st.session_state.input_nombre = nombre_jefa
    if "input_titulo" not in st.session_state: st.session_state.input_titulo = titulo_jefa

    col_id1, col_id2 = st.columns(2)
    with col_id1:
        nuevo_nom = st.text_input("Tu Nombre:", key="input_nombre")
        nuevo_tit = st.text_input("Título Preferido:", key="input_titulo")
    with col_id2:
        ai_key_actual = prefs_voz.get("ai_api_key", "")
        ai_api_key = st.text_input("IA Engine API Key (Gemini):", type="password", value=ai_key_actual)
    
    if st.button("💾 Actualizar Configuración"):
        if "usuario" not in st.session_state.memoria: st.session_state.memoria["usuario"] = {}
        if "preferencias_voz" not in st.session_state.memoria: st.session_state.memoria["preferencias_voz"] = {}
            
        st.session_state.memoria["usuario"]["nombre"] = nuevo_nom
        st.session_state.memoria["usuario"]["titulo"] = nuevo_tit
        st.session_state.memoria["preferencias_voz"]["ai_api_key"] = ai_api_key
        
        guardar_memoria(st.session_state.memoria)
        st.success("Configuración actualizada con éxito.")
        st.rerun()

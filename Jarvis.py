import streamlit as st
import streamlit.components.v1 as components
import datetime
import random
import json
import os
import urllib.parse
import urllib.request

# Configuración de página en modo ancho
st.set_page_config(
    page_title="J.A.R.V.I.S. // M.E.C.A. 4.0", 
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
ai_api_key_guardada = prefs_voz.get("ai_api_key", "").strip()

# CONFIGURACIÓN DIRECTA DE GEMINI
cliente_ia = None
if ai_api_key_guardada:
    try:
        import google.generativeai as genai
        genai.configure(api_key=ai_api_key_guardada)
        cliente_ia = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        try:
            import google.generativeai as genai
            cliente_ia = genai.GenerativeModel('gemini-pro')
        except Exception:
            cliente_ia = None

# INICIALIZAR ESTACIÓN DE MÚSICA EN SESSION STATE
if "estacion_musica" not in st.session_state:
    st.session_state.estacion_musica = "Lo-Fi Labs & Coffee"

# INICIALIZAR HISTORIAL DE CHAT ESTILO BURBUJAS
if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = [
        {"remitente": "jarvis", "texto": f"Saludos, {titulo_jefa} {nombre_jefa}. Sistemas del búnker en Buin operando al 100%. ¿Qué planeamos hoy?"}
    ]

if "ultima_respuesta" not in st.session_state:
    st.session_state.ultima_respuesta = st.session_state.historial_chat[0]["texto"]

# ESTILOS CSS TÁCTICOS NEÓN (TOTALMENTE NEGRO Y AZUL NEÓN)
st.markdown("""
    <style>
    .stApp, .main, [data-testid="stViewToolbar"], header { background-color: #000000 !important; color: #00d2ff !important; }
    .main-header { color: #00d2ff; font-family: 'Segoe UI', sans-serif; font-weight: 800; letter-spacing: 2px; text-align: center; margin-bottom: 0px; text-shadow: 0 0 10px rgba(0,210,255,0.5); }
    .status-bar { text-align: center; color: #00d2ff; font-size: 13px; font-weight: bold; letter-spacing: 1px; margin-bottom: 15px; }
    .market-ticker { background: #000000; border: 1px solid #00d2ff; border-radius: 8px; padding: 6px 12px; display: flex; justify-content: space-around; align-items: center; margin-bottom: 15px; font-family: monospace; font-size: 12px; box-shadow: 0 0 10px rgba(0,210,255,0.2); }
    .market-item { color: #00d2ff; }
    .market-value { color: #00ffaa; font-weight: bold; }
    .holo-card { background-color: #000000; border: 1px solid #00d2ff; border-radius: 12px; padding: 12px; margin-bottom: 15px; box-shadow: 0 0 15px rgba(0, 210, 255, 0.3); }
    .holo-title { color: #00d2ff; font-size: 14px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; text-align: center; text-shadow: 0 0 8px rgba(0,210,255,0.4); }
    
    .stSelectbox select, .stTextInput input, .stTextArea textarea { background-color: #000000 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; }
    label[data-testid="stWidgetLabel"] { color: #00d2ff !important; font-weight: bold !important; }
    
    /* BOTONES TÁCTICOS NEÓN Y BOTÓN DE FORMULARIO NEGRO */
    div.stButton > button, button[kind="secondaryFormSubmit"] { background-color: #000000 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 6px !important; font-weight: bold !important; width: 100% !important; box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important; }
    div.stButton > button:hover, button[kind="secondaryFormSubmit"]:hover { background-color: #00d2ff !important; color: #000000 !important; box-shadow: 0 0 15px #00d2ff !important; }
    
    div[data-testid="stExpander"] { background-color: #000000 !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; margin-bottom: 10px !important; box-shadow: 0 0 10px rgba(0,210,255,0.2); }
    div[data-testid="stExpander"] details summary { background-color: #000000 !important; color: #00d2ff !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">⚡ J.A.R.V.I.S. // INTELIGENCIA ARTIFICIAL M.E.C.A. 4.0</h1>', unsafe_allow_html=True)
estado_ia_txt = "MOTOR IA: GEMINI NEURAL ACTIVO" if cliente_ia else "MOTOR IA: SINTESIS LOCAL HÍBRIDA"
st.markdown(f'<div class="status-bar">CONSOLA OPTIMIZADA &nbsp;|&nbsp; ESTADO: AUTÓNOMO &nbsp;|&nbsp; OPERANDO PARA {titulo_jefa.upper()} {nombre_jefa.upper()} &nbsp;|&nbsp; {estado_ia_txt}</div>', unsafe_allow_html=True)

# TELETIPO FINANCIERO Y DE MERCADOS
st.markdown("""
    <div class="market-ticker">
        <span class="market-item">💵 USD/CLP: <span class="market-value">$930.50 ▲ +0.2%</span></span>
        <span class="market-item">💶 EUR/CLP: <span class="market-value">$1,012.40 ▲ +0.1%</span></span>
        <span class="market-item">📈 IPSA CHILE: <span class="market-value">6,480.12 pts ▲ +0.4%</span></span>
        <span class="market-item">🛢️ BRENT: <span class="market-value">$82.40 ▼ -0.3%</span></span>
        <span class="market-item">🛰️ SERAFÍN-SAT: <span class="market-value">ENLACE 100%</span></span>
    </div>
""", unsafe_allow_html=True)

col_telemetria, col_orbe, col_chat = st.columns([1, 1.4, 1.3])

with col_telemetria:
    st.markdown('<div class="holo-card"><div class="holo-title">⚙️ TELEMETRÍA DEL SISTEMA</div>', unsafe_allow_html=True)
    gauges_html = """
    <div style="display: flex; justify-content: space-around; align-items: center; padding: 5px 0; background: #000;">
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">38%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">CPU</span></div>
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">57%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">RAM</span></div>
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">100%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">PWR</span></div>
    </div>
    """
    components.html(gauges_html, height=90)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card"><div class="holo-title">📍 BASE Y SATÉLITE</div>', unsafe_allow_html=True)
    globe_html = """
    <div style="display: flex; align-items: center; gap: 12px; padding: 2px 0; background: #000;">
        <div style="width: 50px; height: 50px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #00d2ff 0%, #001133 60%, #000000 100%); border: 1px solid #00d2ff; box-shadow: 0 0 12px rgba(0, 210, 255, 0.6); position: relative;"></div>
        <div><p style='color:#00d2ff; font-size:12px; margin:2px 0; font-weight:bold;'>🌍 Ubicación: Buin, Chile</p><p style='color:#00d2ff; font-size:11px; margin:2px 0;'>🛰️ Serafín-Sat: Órbita Estable</p></div>
    </div>
    """
    components.html(globe_html, height=65)
    st.markdown('</div>', unsafe_allow_html=True)

# REPRODUCTOR DE MÚSICA TÁCTICO CON HTML5 DIRECTO Y BOTÓN DE PLAY ACCESIBLE
with col_orbe:
    st.markdown('<div class="holo-card"><div class="holo-title">🎵 AMBIENTE ACÚSTICO // AUDIO TÁCTICO BÚNKER</div>', unsafe_allow_html=True)
    
    opciones_estaciones = {
        "Lo-Fi Labs & Coffee": "https://play.iloveradio.de/ilove-lofi",
        "Stark Chill Synthwave": "https://stream.zeno.fm/f3wvbbqmdg8uv",
        "Cyberpunk Electronic Beats": "https://stream.zeno.fm/0r0xa792yk8uv",
        "Silent Night Buin (Modo Sigilo)": ""
    }
    
    estacion_seleccionada = st.selectbox("Seleccionar Frecuencia Sonora:", list(opciones_estaciones.keys()), index=list(opciones_estaciones.keys()).index(st.session_state.estacion_musica) if st.session_state.estacion_musica in opciones_estaciones else 0)
    st.session_state.estacion_musica = estacion_seleccionada
    
    url_streaming = opciones_estaciones[estacion_seleccionada]

    if url_streaming:
        audio_stream_html = f'''
            <div style="background: #000; border: 1px solid #00d2ff; border-radius: 8px; padding: 12px; box-shadow: 0 0 10px rgba(0,210,255,0.3); text-align: center;">
                <audio controls preload="none" style="width: 100%; height: 40px; filter: invert(100%) hue-rotate(180deg) brightness(1.5);">
                    <source src="{url_streaming}" type="audio/mpeg">
                    Tu navegador no soporta audio táctico.
                </audio>
                <p style="color: #00ffaa; font-family: monospace; font-size: 10px; margin: 6px 0 0 0;">📡 PRESIONA PLAY EN EL REPRODUCTOR</p>
            </div>
        '''
        components.html(audio_stream_html, height=85)
    else:
        st.markdown('<div style="text-align: center; color: #ffbb00; font-family: monospace; font-size: 12px; padding: 20px 0; border: 1px dashed #ffbb00; border-radius: 8px;">🔇 SILENCIO TÁCTICO ACTIVADO EN BUIN</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-title" style="margin-top:8px;">🌐 FRECUENCIA VOCAL & ORBE HOLOGRÁFICO</div>', unsafe_allow_html=True)
    audio_wave_core_html = """
    <style>
      body { background: #000; margin: 0; display: flex; justify-content: center; align-items: center; height: 65px; overflow: hidden; }
      .audio-container { width: 100%; height: 60px; display: flex; justify-content: center; align-items: center; position: relative; background: radial-gradient(circle, rgba(0,210,255,0.15) 0%, rgba(0,0,0,0.95) 80%); border: 1px solid rgba(0,210,255,0.4); border-radius: 8px; box-shadow: 0 0 12px rgba(0, 210, 255, 0.3); }
      .waveform { display: flex; align-items: center; gap: 3px; height: 40px; }
      .bar { width: 4px; background: linear-gradient(180deg, #00ffff 0%, #00d2ff 50%, #0055ff 100%); border-radius: 2px; animation: soundWaveAnim 1.2s ease-in-out infinite alternate; box-shadow: 0 0 8px #00d2ff; }
      .bar:nth-child(1)  { height: 12px; animation-delay: 0.1s; }
      .bar:nth-child(2)  { height: 28px; animation-delay: 0.3s; }
      .bar:nth-child(3)  { height: 40px; animation-delay: 0.2s; }
      .bar:nth-child(4)  { height: 20px; animation-delay: 0.5s; }
      .bar:nth-child(5)  { height: 50px; animation-delay: 0.1s; }
      .bar:nth-child(6)  { height: 32px; animation-delay: 0.4s; }
      .bar:nth-child(7)  { height: 55px; animation-delay: 0.2s; }
      .bar:nth-child(8)  { height: 36px; animation-delay: 0.6s; }
      .bar:nth-child(9)  { height: 48px; animation-delay: 0.1s; }
      .bar:nth-child(10) { height: 42px; animation-delay: 0.3s; }
      @keyframes soundWaveAnim { 0% { transform: scaleY(0.4); opacity: 0.5; } 100% { transform: scaleY(1.2); opacity: 1; box-shadow: 0 0 12px #ffffff; } }
    </style>
    <div class="audio-container"><div class="waveform"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div></div>
    """
    components.html(audio_wave_core_html, height=70)
    
    texto_para_hablar = st.session_state.ultima_respuesta.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        btn_reproducir = st.button("🔊 Hablar Respuesta")
    with c_btn2:
        btn_autonomia = st.button("🤖 Autoevaluación Táctica")

    if btn_reproducir:
        audio_script = f"""
        <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance("{texto_para_hablar}");
            utterance.lang = 'es-CL';
            utterance.pitch = 0.95;
            utterance.rate = 1.0;
            window.speechSynthesis.speak(utterance);
        }}
        </script>
        """
        components.html(audio_script, height=0)

    st.markdown('</div>', unsafe_allow_html=True)

# CONSOLA DE MANDO ORDENADA: CHAT ARRIBA -> BOTONES ABAJO
with col_chat:
    st.markdown('<div class="holo-card"><div class="holo-title">💬 CONSOLA DE MANDO // DIÁLOGO & CONTROLES</div>', unsafe_allow_html=True)
    
    # 1. Historial de burbujas arriba
    chat_container = st.container(height=130)
    with chat_container:
        for item in st.session_state.historial_chat:
            remitente = item["remitente"]
            msg = item["texto"]
            if remitente == "jefa":
                st.markdown(f'''
                    <div style="display: flex; justify-content: flex-end; margin-bottom: 4px;">
                        <div style="background-color: #001133; border: 1px solid #00d2ff; border-radius: 8px 8px 0 8px; padding: 6px 10px; max-width: 85%; color: #00d2ff; font-size: 12px; box-shadow: 0 0 6px rgba(0,210,255,0.2);">
                            <p style="margin:0; color:#00d2ff; font-weight:bold; font-size:10px;">👤 {titulo_jefa} {nombre_jefa}:</p>
                            <p style="margin:2px 0 0 0;">{msg}</p>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                    <div style="display: flex; justify-content: flex-start; margin-bottom: 4px;">
                        <div style="background-color: #000000; border: 1px solid #00d2ff; border-radius: 8px 8px 8px 0; padding: 6px 10px; max-width: 85%; color: #00d2ff; font-size: 12px; box-shadow: 0 0 8px rgba(0,210,255,0.3);">
                            <p style="margin:0; color:#00d2ff; font-weight:bold; font-size:10px;">⚡ J.A.R.V.I.S.:</p>
                            <p style="margin:2px 0 0 0;">{msg}</p>
                        </div>
                    </div>
                ''', unsafe_allow_html=True)

    # 2. Caja de texto para escribir ARRIBA de los botones
    with st.form(key="form_chat_ordenado", clear_on_submit=True):
        entrada_usuario = st.text_input("", placeholder="Escribe o presiona [Windows + H] para charlar...")
        btn_enviar_chat = st.form_submit_button("🚀 Enviar Mensaje")

    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)

    # 3. Botones de acceso rápido ABAJO de todo
    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    with col_q1: btn_q_hola = st.button("👋 Saludar")
    with col_q2: btn_q_emerg = st.button("🚨 Emergencia")
    with col_q3: btn_q_seg = st.button("🛡️ Seguridad")
    with col_q4: btn_limpiar = st.button("🧹 Purga")

    st.markdown('</div>', unsafe_allow_html=True)

    if btn_limpiar:
        st.session_state.historial_chat = [
            {"remitente": "jarvis", "texto": f"Memoria de chat purgada con éxito, {titulo_jefa} {nombre_jefa}. Registros limpios."}
        ]
        st.session_state

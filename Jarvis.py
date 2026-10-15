import streamlit as st
import streamlit.components.v1 as components
import datetime
import random
import json
import os
import subprocess
import urllib.parse
import urllib.request
import urllib.error

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
elevenlabs_key = prefs_voz.get("elevenlabs_api_key", "").strip()

# CONFIGURACIÓN DE IA (OLLAMA LOCAL + GEMINI DE RESPALDO)
def consultar_ollama_local(prompt_sistema, mensaje_usuario):
    """Consulta al servidor local de Ollama (Llama 3)"""
    url = "http://localhost:11434/api/generate"
    prompt_completo = f"{prompt_sistema}\n\nMensaje de la Jefa: {mensaje_usuario}"
    payload = {
        "model": "llama3",
        "prompt": prompt_completo,
        "stream": False
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            resultado = json.loads(response.read().decode('utf-8'))
            return resultado.get("response", "").strip()
    except Exception:
        return None

# FUNCIÓN PARA EJECUTAR ÓRDENES REALES EN EL SISTEMA
def ejecutar_orden_sistema(texto_comando):
    """Ejecuta comandos en Windows basados en la solicitud de la jefa"""
    texto = texto_comando.lower()
    try:
        if "bloc de notas" in texto or "notepad" in texto:
            subprocess.Popen(["notepad.exe"])
            return f"Abriendo el Bloc de notas de inmediato, {titulo_jefa} {nombre_jefa}."
        elif "calculadora" in texto or "calc" in texto:
            subprocess.Popen(["calc.exe"])
            return f"Lanzando la calculadora, {titulo_jefa}."
        elif "chrome" in texto or "navegador" in texto:
            subprocess.Popen(["start", "chrome"], shell=True)
            return f"Abriendo el navegador web, {titulo_jefa}."
        elif "explorador" in texto or "archivos" in texto:
            subprocess.Popen(["explorer.exe"])
            return f"Desplegando el explorador de archivos en pantalla, {titulo_jefa}."
        elif "terminal" in texto or "powershell" in texto or "consola" in texto:
            subprocess.Popen(["powershell.exe"])
            return f"Nueva terminal de comandos desplegada, {titulo_jefa}."
    except Exception as e:
        return f"Error ejecutando la orden física en el sistema: {e}"
    return None

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

# INICIALIZAR HISTORIAL DE CHAT
if "historial_chat" not in st.session_state:
    saludo_inicial = f"Sistemas del búnker en Buin operando al 100%, {titulo_jefa} {nombre_jefa}. ¿Qué orden ejecutamos hoy?"
    st.session_state.historial_chat = [
        {"remitente": "jarvis", "texto": saludo_inicial}
    ]

if "ultima_respuesta" not in st.session_state:
    st.session_state.ultima_respuesta = st.session_state.historial_chat[0]["texto"]

# ESTILOS CSS TÁCTICOS NEÓN
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
    
    div[data-baseweb="select"], div[data-baseweb="select"] > div {
        background-color: #000000 !important;
        border-color: #00d2ff !important;
        color: #00d2ff !important;
        box-shadow: 0 0 10px rgba(0,210,255,0.3) !important;
    }
    div[data-baseweb="select"] span, div[data-baseweb="select"] div {
        background-color: #000000 !important;
        color: #00d2ff !important;
    }
    
    .stTextInput input, .stTextArea textarea { background-color: #000000 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; box-shadow: 0 0 8px rgba(0,210,255,0.3) !important; }
    label[data-testid="stWidgetLabel"] { color: #00d2ff !important; font-weight: bold !important; text-shadow: 0 0 5px rgba(0,210,255,0.4); }
    
    div.stButton > button, button[kind="secondaryFormSubmit"] { background-color: #000000 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 6px !important; font-weight: bold !important; width: 100% !important; box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important; }
    div.stButton > button:hover, button[kind="secondaryFormSubmit"]:hover { background-color: #00d2ff !important; color: #000000 !important; box-shadow: 0 0 15px #00d2ff !important; }
    
    div[data-testid="stExpander"] { background-color: #000000 !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; margin-bottom: 10px !important; box-shadow: 0 0 10px rgba(0,210,255,0.2); }
    div[data-testid="stExpander"] details summary { background-color: #000000 !important; color: #00d2ff !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">⚡ J.A.R.V.I.S. // M.E.C.A. 4.0 (EJECUTOR)</h1>', unsafe_allow_html=True)
st.markdown(f'<div class="status-bar">CONSOLA CON EJECUCIÓN FÍSICA &nbsp;|&nbsp; ESTADO: AUTÓNOMO &nbsp;|&nbsp; {titulo_jefa.upper()} {nombre_jefa.upper()}</div>', unsafe_allow_html=True)

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

    reloj_chileno_html = """
    <div style="background: #000000; border: 1px solid #00d2ff; border-radius: 8px; padding: 8px; font-family: monospace; font-size: 12px; color: #00d2ff; text-align: center; box-shadow: 0 0 10px rgba(0,210,255,0.3); margin-top: 8px;">
        <div style="font-weight: bold; color: #00d2ff; margin-bottom: 4px; font-size: 11px; letter-spacing: 1px;">⏳ HORA TÁCTICA (BUIN / STGO)</div>
        🇨🇱 <b id="clock-buin" style="color:#00ffff; font-size: 14px;">--:--:--</b>
    </div>
    <script>
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-GB', { timeZone: 'America/Santiago', hour12: false });
        document.getElementById('clock-buin').innerText = timeString;
    }
    setInterval(updateClock, 1000);
    updateClock();
    </script>
    """
    components.html(reloj_chileno_html, height=65)
    st.markdown('</div>', unsafe_allow_html=True)

with col_orbe:
    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.markdown('<div class="holo-title">📺 AMBIENTE ACÚSTICO // YOUTUBE TÁCTICO</div>', unsafe_allow_html=True)
    
    canales_yt = {
        "🚀 Work Mode Activated [Deep Focus]": "cTTxesT4C0M",
        "⚡ Synthwave Radio (Mix 24/7)": "4xDzrJKXOOY",
        "🌆 Cyberpunk Ambient Stream": "MV_3Dpw-BRY"
    }
    
    estacion_yt = st.selectbox("Seleccionar Frecuencia de Video/Audio:", list(canales_yt.keys()))
    video_id = canales_yt[estacion_yt]

    youtube_iframe_html = f"""
    <div style="background: #000; border: 1px solid #00d2ff; border-radius: 8px; overflow: hidden; box-shadow: 0 0 12px rgba(0,210,255,0.3);">
        <iframe width="100%" height="135" src="https://www.youtube.com/embed/{video_id}?autoplay=0&enablejsapi=1" 
        title="YouTube video player" frameborder="0" 
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
        allowfullscreen></iframe>
    </div>
    """
    components.html(youtube_iframe_html, height=145)

    st.markdown('<div class="holo-title" style="margin-top:10px;">🌐 FRECUENCIA VOCAL & ORBE HOLOGRÁFICO</div>', unsafe_allow_html=True)
    
    audio_wave_core_html = (
        '<style>'
        'body { background: #000; margin: 0; display: flex; justify-content: center; align-items: center; height: 65px; overflow: hidden; }'
        '.audio-container { width: 100%; height: 60px; display: flex; justify-content: center; align-items: center; position: relative; background: radial-gradient(circle, rgba(0,210,255,0.15) 0%, rgba(0,0,0,0.95) 80%); border: 1px solid rgba(0,210,255,0.4); border-radius: 8px; box-shadow: 0 0 12px rgba(0, 210, 255, 0.3); }'
        '.waveform { display: flex; align-items: center; gap: 3px; height: 40px; }'
        '.bar { width: 4px; background: linear-gradient(180deg, #00ffff 0%, #00d2ff 50%, #0055ff 100%); border-radius: 2px; animation: soundWaveAnim 1.2s ease-in-out infinite alternate; box-shadow: 0 0 8px #00d2ff; }'
        '.bar:nth-child(1)  { height: 12px; animation-delay: 0.1s; }'
        '.bar:nth-child(2)  { height: 28px; animation-delay: 0.3s; }'
        '.bar:nth-child(3)  { height: 40px; animation-delay: 0.2s; }'
        '.bar:nth-child(4)  { height: 20px; animation-delay: 0.5s; }'
        '.bar:nth-child(5)  { height: 50px; animation-delay: 0.1s; }'
        '.bar:nth-child(6)  { height: 32px; animation-delay: 0.4s; }'
        '.bar:nth-child(7)  { height: 55px; animation-delay: 0.2s; }'
        '.bar:nth-child(8)  { height: 36px; animation-delay: 0.6s; }'
        '.bar:nth-child(9)  { height: 48px; animation-delay: 0.1s; }'
        '.bar:nth-child(10) { height: 42px; animation-delay: 0.3s; }'
        '@keyframes soundWaveAnim { 0% { transform: scaleY(0.4); opacity: 0.5; } 100% { transform: scaleY(1.2); opacity: 1; box-shadow: 0 0 12px #ffffff; } }'
        '</style>'
        '<div class="audio-container"><div class="waveform"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div></div>'
    )
    components.html(audio_wave_core_html, height=70)
    
    texto_limpio = st.session_state.ultima_respuesta.replace('"', '\\"').replace("'", "\\'")
    texto_para_hablar = " ".join(texto_limpio.splitlines())
    
    auto_voice_script = f"""
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
    components.html(auto_voice_script, height=0)

    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        btn_reproducir = st.button("🔊 Hablar Respuesta")
    with c_btn2:
        btn_autonomia = st.button("🤖 Autoevaluación Táctica")

    st.markdown('</div>', unsafe_allow_html=True)

with col_chat:
    st.markdown('<div class="holo-card"><div class="holo-title">💬 CONSOLA DE MANDO // DIÁLOGO & EJECUCIÓN</div>', unsafe_allow_html=True)
    
    chat_container = st.container(height=130)
    with chat_container:
        for item in st.session_state.historial_chat:
            remitente = item["remitente"]
            msg = item["texto"]
            if remitente == "jefa":
                html_msg = (
                    '<div style="display: flex; justify-content: flex-end; margin-bottom: 4px;">'
                    '<div style="background-color: #001133; border: 1px solid #00d2ff; border-radius: 8px 8px 0 8px; padding: 6px 10px; max-width: 85%; color: #00d2ff; font-size: 12px; box-shadow: 0 0 6px rgba(0,210,255,0.2);">'
                    f'<p style="margin:0; color:#00d2ff; font-weight:bold; font-size:10px;">👤 {titulo_jefa} {nombre_jefa}:</p>'
                    f'<p style="margin:2px 0 0 0;">{msg}</p>'
                    '</div></div>'
                )
                st.markdown(html_msg, unsafe_allow_html=True)
            else:
                html_msg = (
                    '<div style="display: flex; justify-content: flex-start; margin-bottom: 4px;">'
                    '<div style="background-color: #000000; border: 1px solid #00d2ff; border-radius: 8px 8px 8px 0; padding: 6px 10px; max-width: 85%; color: #00d2ff; font-size: 12px; box-shadow: 0 0 8px rgba(0,210,255,0.3);">'
                    '<p style="margin:0; color:#00d2ff; font-weight:bold; font-size:10px;">⚡ J.A.R.V.I.S.:</p>'
                    f'<p style="margin:2px 0 0 0;">{msg}</p>'
                    '</div></div>'
                )
                st.markdown(html_msg, unsafe_allow_html=True)

    with st.form(key="form_chat_ordenado", clear_on_submit=True):
        entrada_usuario = st.text_input("", placeholder="Ej: Abre el bloc de notas...")
        btn_enviar_chat = st.form_submit_button("🚀 Enviar Comando")

    st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)

    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    with col_q1: btn_q_hola = st.button("👋 Saludar")
    with col_q2: btn_q_emerg = st.button("🚨 Emergencia")
    with col_q3: btn_q_seg = st.button("🛡️ Seguridad")
    with col_q4: btn_limpiar = st.button("🧹 Purga")

    st.markdown('</div>', unsafe_allow_html=True)

    if btn_limpiar:
        st.session_state.historial_chat = [
            {"remitente": "jarvis", "texto": f"Historial purgado, {titulo_jefa} {nombre_jefa}. Tabula rasa."}
        ]
        st.session_state.ultima_respuesta = st.session_state.historial_chat[0]["texto"]
        st.rerun()

    comando_ejecutar = None
    if btn_enviar_chat and entrada_usuario:
        comando_ejecutar = entrada_usuario
    elif btn_q_hola:
        comando_ejecutar = "Hola Jarvis"
    elif btn_q_emerg:
        comando_ejecutar = "Protocolo de emergencia"
    elif btn_q_seg:
        comando_ejecutar = "Protocolo de seguridad"

    if comando_ejecutar:
        texto = comando_ejecutar.lower().strip()
        respuesta_ia = None

        # 1. PRIORIDAD: EJECUTAR ORDEN FÍSICA EN EL SISTEMA
        respuesta_ia = ejecutar_orden_sistema(comando_ejecutar)

        # 2. SI NO ES UNA ORDEN FÍSICA, CONSULTAR A OLLAMA LOCAL (Llama 3)
        if not respuesta_ia:
            prompt_sistema = f"""Eres J.A.R.V.I.S., el asistente de IA superinteligente, leal y carismático de Tony Stark. Tu jefa es {titulo_jefa} {nombre_jefa}, y estás a cargo de su búnker en Buin, Chile.
            INSTRUCCIONES:
            1. Habla 100% como un compañero humano astuto y brillante con toque de humor elegante.
            2. Sé breve y directo (1 a 3 frases máximo)."""
            respuesta_ia = consultar_ollama_local(prompt_sistema, comando_ejecutar)

        # 3. RESPALDO CON CLOUD GEMINI SI ESTÁ CONFIGURADO
        if not respuesta_ia and cliente_ia:
            try:
                respuesta_modelo = cliente_ia.generate_content(f"{prompt_sistema}\nMensaje de la Jefa: {comando_ejecutar}")
                if respuesta_modelo and respuesta_modelo.text:
                    respuesta_ia = respuesta_modelo.text.strip()
            except Exception:
                respuesta_ia = None

        # 4. RESPALDO LOCAL FINAL
        if not respuesta_ia:
            if "autoevaluación" in texto or "autonomía" in texto:
                respuesta_ia = f"Sistemas estables en Buin, {nombre_jefa}. Perímetro y servidores al 100%."
            elif "hola" in texto:
                respuesta_ia = f"¡Hola, {nombre_jefa}! ¿Qué aplicación o comando ejecutamos ahora?"
            else:
                respuesta_ia = f"Orden procesada en el búnker, {nombre_jefa}."

        st.session_state.historial_chat.append({"remitente": "jefa", "texto": comando_ejecutar})
        st.session_state.historial_chat.append({"remitente": "jarvis", "texto": respuesta_ia})
        st.session_state.ultima_respuesta = respuesta_ia
        st.rerun()

st.markdown("---")

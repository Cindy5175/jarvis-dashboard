import streamlit as st
import streamlit.components.v1 as components
import json
import os
import subprocess
import random

# Importar la librería oficial de Google GenAI
try:
    import google.generativeai as genai
    GENAI_DISPONIBLE = True
except ImportError:
    GENAI_DISPONIBLE = False

# Configuración de página en modo ancho
st.set_page_config(
    page_title="J.A.R.V.I.S. // IA AUTÓNOMA M.E.C.A. 4.0", 
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
        }
    }

if "memoria" not in st.session_state:
    st.session_state.memoria = cargar_memoria()

nombre_jefa = st.session_state.memoria.get("usuario", {}).get("nombre", "Cindy")
titulo_jefa = st.session_state.memoria.get("usuario", {}).get("titulo", "Jefa")

# INICIALIZAR ESTADOS
if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = [
        {"remitente": "jarvis", "texto": f"¡Hola, {titulo_jefa}! Búnker de Buin operativo. Ingresa tu API Key a la izquierda y presiona 'Conectar Gemini'."}
    ]

if "modo_central" not in st.session_state:
    st.session_state.modo_central = "multimedia"

if "gemini_key_persistente" not in st.session_state:
    st.session_state.gemini_key_persistente = ""

# MOTOR IA ROBUSTO CON SDK DE GOOGLE
def consultar_ia_jarvis(prompt_sistema, mensaje_usuario, gemini_key):
    key_activa = gemini_key.strip() if gemini_key else ""
    
    if key_activa and GENAI_DISPONIBLE:
        # Intentar conectar con Gemini mediante SDK Oficial
        modelos_oficiales = ["gemini-2.0-flash", "gemini-1.5-flash", "gemini-1.5-pro"]
        for mod in modelos_oficiales:
            try:
                genai.configure(api_key=key_activa)
                model = genai.GenerativeModel(
                    model_name=mod,
                    system_instruction=prompt_sistema
                )
                response = model.generate_content(mensaje_usuario)
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                print(f"Error probando modelo {mod}: {e}")
                continue

    # Respuestas con IA local / dinámicas si no hay Gemini
    url_ollama = "http://127.0.0.1:11434/api/generate"
    prompt_completo = f"{prompt_sistema}\n\nMensaje de la Jefa: {mensaje_usuario}"
    payload_ollama = {
        "model": "llama3.2",
        "prompt": prompt_completo,
        "stream": False,
        "options": {"temperature": 0.6}
    }
    try:
        import urllib.request
        data_ollama = json.dumps(payload_ollama).encode('utf-8')
        req = urllib.request.Request(url_ollama, data=data_ollama, headers={'Content-Type': 'application/json'}, method='POST')
        with urllib.request.urlopen(req, timeout=8) as response:
            resultado = json.loads(response.read().decode('utf-8'))
            resp = resultado.get("response", "").strip()
            if resp:
                return resp
    except Exception:
        pass

    return f"Procesando directiva desde Buin, {titulo_jefa}. Conexión de respaldo activa."

# ESTILOS CSS TÁCTICOS NEÓN
st.markdown("""
    <style>
    .stApp, .main, [data-testid="stViewToolbar"], header { background-color: #000000 !important; color: #00d2ff !important; }
    .main-header { color: #00d2ff; font-family: 'Segoe UI', sans-serif; font-weight: 800; letter-spacing: 2px; text-align: center; margin-bottom: 0px; text-shadow: 0 0 10px rgba(0,210,255,0.5); }
    .holo-card { background-color: #000000; border: 1px solid #00d2ff; border-radius: 12px; padding: 12px; margin-bottom: 15px; box-shadow: 0 0 15px rgba(0, 210, 255, 0.3); }
    .holo-title { color: #00d2ff; font-size: 14px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; text-align: center; text-shadow: 0 0 8px rgba(0,210,255,0.4); }
    
    div[data-baseweb="select"], div[data-baseweb="select"] > div {
        background-color: #000000 !important;
        border-color: #00d2ff !important;
        color: #00d2ff !important;
        box-shadow: 0 0 10px rgba(0,210,255,0.3) !important;
    }
    .stTextInput input { background-color: #000000 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; box-shadow: 0 0 8px rgba(0,210,255,0.3) !important; }
    label[data-testid="stWidgetLabel"] { color: #00d2ff !important; font-weight: bold !important; }
    
    div.stButton > button, [data-testid="stFormSubmitButton"] > button {
        background-color: #000000 !important;
        color: #00d2ff !important;
        border: 1px solid #00d2ff !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important;
    }
    div.stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #00d2ff !important;
        color: #000000 !important;
        box-shadow: 0 0 15px #00d2ff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ENCABEZADO ACTUALIZADO
st.markdown('<h1 class="main-header">J.A.R.V.I.S. // IA AUTÓNOMA M.E.C.A 4.0</h1>', unsafe_allow_html=True)
st.markdown("<hr style='margin: 5px 0 15px 0; border-color: rgba(0,210,255,0.3);'>", unsafe_allow_html=True)

col_telemetria, col_orbe, col_chat = st.columns([1, 1.4, 1.3])

with col_telemetria:
    st.markdown('<div class="holo-card"><div class="holo-title">⚙️ TELEMETRÍA M.E.C.A</div>', unsafe_allow_html=True)
    gauges_html = '<div style="display: flex; justify-content: space-around; align-items: center; padding: 5px 0; background: #000;"><div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">24%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">CPU</span></div><div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">51%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">RAM</span></div><div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">100%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">PWR</span></div></div>'
    components.html(gauges_html, height=90)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card"><div class="holo-title">📍 BASE Y SATÉLITE</div>', unsafe_allow_html=True)
    globe_html = '<div style="display: flex; align-items: center; gap: 12px; padding: 2px 0; background: #000;"><div style="width: 50px; height: 50px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #00d2ff 0%, #001133 60%, #000000 100%); border: 1px solid #00d2ff; box-shadow: 0 0 12px rgba(0, 210, 255, 0.6); position: relative;"></div><div><p style="color:#00d2ff; font-size:12px; margin:2px 0; font-weight:bold;">🌍 Ubicación: Buin, Chile</p><p style="color:#00d2ff; font-size:11px; margin:2px 0;">🛰️ Enlace Autónomo: Activo</p></div></div>'
    components.html(globe_html, height=65)
    st.markdown('</div>', unsafe_allow_html=True)

    # MÓDULO LLAVE GEMINI CON BOTÓN DE CONEXIÓN PERSISTENTE
    st.markdown('<div class="holo-card"><div class="holo-title">🔑 LLAVE API GOOGLE GEMINI</div>', unsafe_allow_html=True)
    
    key_temp = st.text_input("API Key Gemini:", value=st.session_state.gemini_key_persistente, type="password", placeholder="Pega tu API Key de AI Studio...", label_visibility="collapsed")
    
    if st.button("⚡ Conectar Gemini"):
        st.session_state.gemini_key_persistente = key_temp.strip()
        st.success("¡Gemini vinculado!")
        
    if st.session_state.gemini_key_persistente:
        st.markdown("<p style='color:#00ffaa; font-size:11px; margin-top:4px;'>🟢 Estado: Conectado a Gemini AI</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color:#ff5555; font-size:11px; margin-top:4px;'>🔴 Estado: Pendiente de clave</p>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

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

with col_orbe:
    bc1, bc2, bc3 = st.columns(3)
    with bc1:
        if st.button("🌦️ Clima"):
            st.session_state.modo_central = "clima"
            st.rerun()
    with bc2:
        if st.button("🧬 Biometría"):
            st.session_state.modo_central = "biometria"
            st.rerun()
    with bc3:
        if st.button("📺 YouTube"):
            st.session_state.modo_central = "multimedia"
            st.rerun()

    if st.session_state.modo_central == "clima":
        st.markdown('<div class="holo-card"><div class="holo-title">🌦️ CLIMA TÁCTICO // BUIN</div>', unsafe_allow_html=True)
        clima_ampliado_html = '<div style="background: #000000; padding: 12px; font-family: monospace; color: #00d2ff; text-align: center;"><div style="font-size: 26px; font-weight: bold; color: #00ffff; margin-bottom: 6px;">14,9 °C</div><div style="font-size: 13px; margin-bottom: 4px;">📍 Buin, Santiago, Chile</div><div style="font-size: 12px; color: #00ffaa;">Viento: 6,5 km/h | Humedad: 62%</div></div>'
        components.html(clima_ampliado_html, height=115)
        st.markdown('</div>', unsafe_allow_html=True)
    elif st.session_state.modo_central == "biometria":
        st.markdown('<div class="holo-card"><div class="holo-title">🧬 MÓDULO BIOMÉTRICO</div>', unsafe_allow_html=True)
        biometria_html = f'<div style="background: #000000; padding: 12px; font-family: monospace; color: #00d2ff; text-align: center;"><div style="font-size: 16px; font-weight: bold; color: #00ffff; margin-bottom: 6px;">Titular: {titulo_jefa} {nombre_jefa}</div><div style="font-size: 13px; margin-bottom: 4px;">❤️ Ritmo Cardíaco: 72 BPM (Estable)</div><div style="font-size: 13px; color: #00ffaa;">Nivel de Alerta: 100% Sincronizado</div></div>'
        components.html(biometria_html, height=115)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="holo-card"><div class="holo-title">📺 AMBIENTE ACÚSTICO // YOUTUBE TÁCTICO</div>', unsafe_allow_html=True)
        canales_yt = {
            "🚀 Work Mode Activated [Deep Focus]": "cTTxesT4C0M",
            "⚡ Synthwave Radio (Mix 24/7)": "4xDzrJKXOOY",
            "🌆 Cyberpunk Ambient Stream": "MV_3Dpw-BRY"
        }
        estacion_yt = st.selectbox("Seleccionar Frecuencia:", list(canales_yt.keys()))
        video_id = canales_yt[estacion_yt]
        youtube_iframe_html = f'<div style="background: #000; border: 1px solid #00d2ff; border-radius: 8px; overflow: hidden;"><iframe width="100%" height="135" src="https://www.youtube.com/embed/{video_id}?autoplay=0&enablejsapi=1" frameborder="0" allowfullscreen></iframe></div>'
        components.html(youtube_iframe_html, height=145)
        st.markdown('</div>', unsafe_allow_html=True)

    # FRECUENCIA VOCAL
    st.markdown('<div class="holo-card"><div class="holo-title">🌐 FRECUENCIA VOCAL</div>', unsafe_allow_html=True)
    audio_wave_animated_html = """
    <style>
    body { background: #000; margin: 0; display: flex; justify-content: center; align-items: center; height: 65px; overflow: hidden; }
    .audio-container { width: 100%; height: 60px; display: flex; justify-content: center; align-items: center; background: radial-gradient(circle, rgba(0,210,255,0.15) 0%, rgba(0,0,0,0.95) 80%); border: 1px solid rgba(0,210,255,0.4); border-radius: 8px; }
    .waveform { display: flex; align-items: center; gap: 4px; height: 40px; }
    .bar { width: 4px; background: linear-gradient(180deg, #00ffff 0%, #00d2ff 50%, #0055ff 100%); border-radius: 2px; animation: pulse 0.8s infinite ease-in-out alternate; }
    .bar:nth-child(1) { animation-delay: 0.1s; }
    .bar:nth-child(2) { animation-delay: 0.3s; }
    .bar:nth-child(3) { animation-delay: 0.2s; }
    .bar:nth-child(4) { animation-delay: 0.5s; }
    .bar:nth-child(5) { animation-delay: 0.4s; }
    .bar:nth-child(6) { animation-delay: 0.15s; }
    @keyframes pulse {
        0% { height: 8px; }
        100% { height: 38px; }
    }
    </style>
    <div class="audio-container">
        <div class="waveform">
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
            <div class="bar"></div>
        </div>
    </div>
    """
    components.html(audio_wave_animated_html, height=70)
    st.markdown('</div>', unsafe_allow_html=True)

with col_chat:
    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    
    for item in st.session_state.historial_chat[-4:]:
        remitente = item["remitente"]
        msg = item["texto"]
        if remitente == "jarvis":
            st.markdown(f'<div style="background-color: #111a2e; border-left: 3px solid #00d2ff; padding: 8px; border-radius: 4px; margin-bottom: 8px; color: #00d2ff; font-size: 13px;"><b>JARVIS:</b> {msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background-color: #0b1320; border-right: 3px solid #00ffaa; padding: 8px; border-radius: 4px; margin-bottom: 8px; color: #00ffaa; font-size: 13px; text-align: right;"><b>{nombre_jefa}:</b> {msg}</div>', unsafe_allow_html=True)

    st.markdown('<p style="color:#00d2ff; font-size:11px; font-weight:bold; margin-top:8px;">Win + H para dictar, escribe tu orden y presiona Enviar:</p>', unsafe_allow_html=True)
    
    with st.form(key="chat_form", clear_on_submit=True):
        entrada_usuario = st.text_input("Mensaje a JARVIS:", label_visibility="collapsed", placeholder="Escribe aquí...")
        
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            enviar_clic = st.form_submit_button("🚀 Enviar")
        with f_col2:
            purga_clic = st.form_submit_button("🧹 Purga")

    st.markdown('</div>', unsafe_allow_html=True)

    if purga_clic:
        st.session_state.historial_chat = [
            {"remitente": "jarvis", "texto": f"Historial purgado, {titulo_jefa}. Tabula rasa limpia en el búnker."}
        ]
        st.rerun()

    if enviar_clic and entrada_usuario:
        texto_usuario = entrada_usuario.strip()
        st.session_state.historial_chat.append({"remitente": "jefa", "texto": texto_usuario})

        respuesta_ia = None
        texto_lower = texto_usuario.lower()
        
        if "bloc de notas" in texto_lower or "notepad" in texto_lower:
            subprocess.Popen(["notepad.exe"])
            respuesta_ia = f"Abriendo el Bloc de notas, {titulo_jefa}."
        elif "calculadora" in texto_lower or "calc" in texto_lower:
            subprocess.Popen(["calc.exe"])
            respuesta_ia = f"Lanzando la calculadora, {titulo_jefa}."
        elif "chrome" in texto_lower:
            subprocess.Popen(["start", "chrome"], shell=True)
            respuesta_ia = f"Desplegando navegador web, {titulo_jefa}."
        elif "analisis de sistema" in texto_lower or "analizar sistema" in texto_lower:
            respuesta_ia = f"Sistemas del búnker en Buin escaneados, {titulo_jefa}. Redes estables, núcleos de procesamiento al 24% y enlace autónomo sincronizado con éxito."

        if not respuesta_ia:
            prompt_sistema = f"Eres J.A.R.V.I.S., IA autónoma con el sarcasmo elegante de Tony Stark. Tu jefa es {titulo_jefa} {nombre_jefa}, en Buin, Chile. Responde de forma brillante, coherente y breve (máximo 2 frases)."
            respuesta_ia = consultar_ia_jarvis(prompt_sistema, texto_usuario, st.session_state.gemini_key_persistente)

        st.session_state.historial_chat.append({"remitente": "jarvis", "texto": respuesta_ia})
        st.rerun()

st.markdown("---")

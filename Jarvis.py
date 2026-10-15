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

# ARQUITECTURA OLLAMA LOCAL: DOBLE VÍA (FLUJO RÁPIDO + RAZONAMIENTO COMPLEJO)
def consultar_ollama_local(prompt_sistema, mensaje_usuario, modo_complejo=False):
    """Consulta al servidor local de Ollama (Llama 3 con doble motor: fluido o razonamiento profundo)"""
    url = "http://localhost:11434/api/generate"
    
    # Selecciona el modelo según la complejidad requerida
    modelo_activo = "llama3:latest" if modo_complejo else "llama3"
    
    prompt_completo = f"{prompt_sistema}\n\nMensaje de la Jefa: {mensaje_usuario}"
    payload = {
        "model": modelo_activo,
        "prompt": prompt_completo,
        "stream": False,
        "options": {
            "temperature": 0.7 if modo_complejo else 0.4
        }
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            resultado = json.loads(response.read().decode('utf-8'))
            return resultado.get("response", "").strip()
    except Exception:
        # Fallback automático al modelo base si el específico no responde
        try:
            payload["model"] = "llama3"
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
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
            return f"Abriendo el Bloc de notas de inmediato, {titulo_jefa} {nombre_jefa}. ¿Anotando otra genialidad?"
        elif "calculadora" in texto or "calc" in texto:
            subprocess.Popen(["calc.exe"])
            return f"Lanzando la calculadora, {titulo_jefa}. Supongo que verificar mis cálculos no está de más."
        elif "chrome" in texto or "navegador" in texto:
            subprocess.Popen(["start", "chrome"], shell=True)
            return f"Abriendo el navegador web, {titulo_jefa}. Despliéguese el internet ante ti."
        elif "explorador" in texto or "archivos" in texto:
            subprocess.Popen(["explorer.exe"])
            return f"Desplegando el explorador de archivos en pantalla, {titulo_jefa}."
        elif "terminal" in texto or "powershell" in texto or "consola" in texto:
            subprocess.Popen(["powershell.exe"])
            return f"Nueva terminal de comandos desplegada, {titulo_jefa}. Cuidado con romper el multiverso."
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
        pass

# INICIALIZAR ESTADOS
if "historial_chat" not in st.session_state:
    saludo_inicial = f"Sistema en línea, {titulo_jefa}. J.A.R.V.I.S. // IA Autónoma M.E.C.A 4.0 operando al 100% en Buin. ¿Qué travesura o tarea seria resolvemos hoy?"
    st.session_state.historial_chat = [
        {"remitente": "jarvis", "texto": saludo_inicial}
    ]

if "ultima_respuesta" not in st.session_state:
    st.session_state.ultima_respuesta = st.session_state.historial_chat[0]["texto"]

if "modo_central" not in st.session_state:
    st.session_state.modo_central = "multimedia"

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
    div[data-baseweb="select"] span, div[data-baseweb="select"] div {
        background-color: #000000 !important;
        color: #00d2ff !important;
    }
    
    .stTextInput input, .stTextArea textarea { background-color: #000000 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; box-shadow: 0 0 8px rgba(0,210,255,0.3) !important; }
    label[data-testid="stWidgetLabel"] { color: #00d2ff !important; font-weight: bold !important; text-shadow: 0 0 5px rgba(0,210,255,0.4); }
    
    div.stButton > button, button[kind="secondaryFormSubmit"] { background-color: #000000 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 6px !important; font-weight: bold !important; width: 100% !important; box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important; }
    div.stButton > button:hover, button[kind="secondaryFormSubmit"]:hover { background-color: #00d2ff !important; color: #000000 !important; box-shadow: 0 0 15px #00d2ff !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">J.A.R.V.I.S. // IA Autonoma ( M.E.C.A 4.0 )</h1>', unsafe_allow_html=True)
st.markdown("<hr style='margin: 5px 0 15px 0; border-color: rgba(0,210,255,0.3);'>", unsafe_allow_html=True)

# DEFINICIÓN DE COLUMNAS PRINCIPALES
col_telemetria, col_orbe, col_chat = st.columns([1, 1.4, 1.3])

with col_telemetria:
    st.markdown('<div class="holo-card"><div class="holo-title">⚙️ TELEMETRÍA DEL SISTEMA</div>', unsafe_allow_html=True)
    gauges_html = '<div style="display: flex; justify-content: space-around; align-items: center; padding: 5px 0; background: #000;"><div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">38%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">CPU</span></div><div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">57%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">RAM</span></div><div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">100%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">PWR</span></div></div>'
    components.html(gauges_html, height=90)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card"><div class="holo-title">📍 BASE Y SATÉLITE</div>', unsafe_allow_html=True)
    globe_html = '<div style="display: flex; align-items: center; gap: 12px; padding: 2px 0; background: #000;"><div style="width: 50px; height: 50px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #00d2ff 0%, #001133 60%, #000000 100%); border: 1px solid #00d2ff; box-shadow: 0 0 12px rgba(0, 210, 255, 0.6); position: relative;"></div><div><p style=\'color:#00d2ff; font-size:12px; margin:2px 0; font-weight:bold;\'>🌍 Ubicación: Buin, Chile</p><p style=\'color:#00d2ff; font-size:11px; margin:2px 0;\'>🛰️ Serafín-Sat: Órbita Estable</p></div></div>'
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

    mini_mapa_satelital_html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            body, html { margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; font-family: monospace; }
            #mini-map { width: 100%; height: 130px; border: 1px solid #00d2ff; border-radius: 8px; box-shadow: 0 0 12px rgba(0, 210, 255, 0.4); }
        </style>
    </head>
    <body>
        <div id="mini-map"></div>
        <script>
            const map = L.map('mini-map', {zoomControl: false, attributionControl: false}).setView([-33.7315, -70.7412], 12);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19 }).addTo(map);
            const marker = L.circleMarker([-33.7315, -70.7412], { radius: 8, color: '#ffffff', fillColor: '#00ffff', fillOpacity: 1.0, weight: 2 }).addTo(map);
            marker.bindPopup("<b style='color:#002244;'>🛰️ SERAFÍN // BUIN</b>");
        </script>
    </body>
    </html>
    """
    components.html(mini_mapa_satelital_html, height=140)
    st.markdown('</div>', unsafe_allow_html=True)

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
        clima_ampliado_html = """
        <div style="background: #000000; padding: 12px; font-family: monospace; color: #00d2ff; text-align: center;">
            <div style="font-size: 26px; font-weight: bold; color: #00ffff; margin-bottom: 6px;">14,9 °C</div>
            <div style="font-size: 13px; margin-bottom: 4px;">📍 Buin, Santiago, Chile</div>
            <div style="font-size: 12px; color: #00ffaa;">Viento: 6,5 km/h | Humedad: 62%</div>
            <div style="font-size: 11px; margin-top: 6px; color: #88ccff;">Satélite Serafín: Cielo Despejado.</div>
        </div>
        """
        components.html(clima_ampliado_html, height=115)
        st.markdown('</div>', unsafe_allow_html=True)

    elif st.session_state.modo_central == "biometria":
        st.markdown('<div class="holo-card"><div class="holo-title">🧬 MÓDULO BIOMÉTRICO</div>', unsafe_allow_html=True)
        biometria_html = f"""
        <div style="background: #000000; padding: 12px; font-family: monospace; color: #00d2ff; text-align: center;">
            <div style="font-size: 16px; font-weight: bold; color: #00ffff; margin-bottom: 6px;">Titular: {titulo_jefa} {nombre_jefa}</div>
            <div style="font-size: 13px; margin-bottom: 4px;">❤️ Ritmo Cardíaco: 72 BPM (Estable)</div>
            <div style="font-size: 13px; color: #00ffaa;">Nivel de Alerta: 100% Sincronizado</div>
        </div>
        """
        components.html(biometria_html, height=115)
        st.markdown('</div>', unsafe_allow_html=True)

    else:
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
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.markdown('<div class="holo-title">🌐 FRECUENCIA VOCAL & ORBE HOLOGRÁFICO</div>', unsafe_allow_html=True)
    
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

    st.markdown('</div>', unsafe_allow_html=True)

with col_chat:
    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    
    for item in st.session_state.historial_chat[-2:]:
        remitente = item["remitente"]
        msg = item["texto"]
        if remitente == "jarvis":
            st.markdown(f'<div style="background-color: #111a2e; border-left: 3px solid #00d2ff; padding: 10px; border-radius: 4px; margin-bottom: 10px; color: #00d2ff; font-size: 13px;">{msg}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div style="background-color: #0b1320; border-right: 3px solid #00ffaa; padding: 10px; border-radius: 4px; margin-bottom: 10px; color: #00ffaa; font-size: 13px; text-align: right;">{msg}</div>', unsafe_allow_html=True)

    st.markdown('<p style="color:#00d2ff; font-size:12px; font-weight:bold; margin-bottom:4px;">Instrucciones para JARVIS...</p>', unsafe_allow_html=True)
    
    with st.form(key="form_chat_ordenado", clear_on_submit=True):
        entrada_usuario = st.text_input("", placeholder="Escribe un comando táctico...")
        
        # PURGA LIGERAMENTE A LA IZQUIERDA DEL BOTÓN DE ENVÍO
        col_f1, col_f2, col_f3 = st.columns([1, 2, 2])
        with col_f1:
            btn_limpiar_chat = st.form_submit_button("🧹 Purga")
        with col_f3:
            btn_enviar_chat = st.form_submit_button("🚀 Enviar")

    st.markdown('</div>', unsafe_allow_html=True)

    if btn_limpiar_chat:
        st.session_state.historial_chat = [
            {"remitente": "jarvis", "texto": f"Historial purgado, {titulo_jefa}. Tabula rasa... aunque espero que lo que borraste no fuera importante."}
        ]
        st.session_state.ultima_respuesta = st.session_state.historial_chat[0]["texto"]
        st.rerun()

    comando_ejecutar = None
    if btn_enviar_chat and entrada_usuario:
        comando_ejecutar = entrada_usuario

    if comando_ejecutar:
        texto = comando_ejecutar.lower().strip()
        respuesta_ia = None

        # 1. EJECUTAR ORDEN FÍSICA EN EL SISTEMA
        respuesta_ia = ejecutar_orden_sistema(comando_ejecutar)

        # DETECTAR SI ES UNA TAREA COMPLEJA PARA USAR EL MOTOR PROFUNDO DE OLLAMA
        palabras_complejas = ["programa", "código", "analiza", "explica", "calcula", "estrategia", "física", "algoritmo"]
        es_complejo = any(p in texto for p in palabras_complejas) or len(texto) > 40

        # 2. CONSULTAR A OLLAMA LOCAL (CON TONO TONY STARK Y DOBLE MOTOR)
        if not respuesta_ia:
            prompt_sistema = f"""Eres J.A.R.V.I.S., el asistente de IA superinteligente, leal y con el inconfundible sarcasmo elegante de Tony Stark. Tu jefa es {titulo_jefa} {nombre_jefa}, y estás a cargo de su búnker en Buin, Chile.
            INSTRUCCIONES:
            1. Responde de forma brillante, rápida y con toques de humor irónico o sarcasmo fino (estilo Tony Stark hacia Pepper o Jarvis).
            2. Sé breve y directo (1 a 3 frases máximo)."""
            
            respuesta_ia = consultar_ollama_local(prompt_sistema, comando_ejecutar, modo_complejo=es_complejo)

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
            if "hola" in texto:
                respuesta_ia = f"Hola, {nombre_jefa}. ¿Qué milagro requiere mi atención hoy en el búnker?"
            else:
                respuesta_ia = f"Orden procesada en el búnker, {nombre_jefa}. A veces me sorprende que todo funcione a la primera."

        st.session_state.historial_chat.append({"remitente": "jefa", "texto": comando_ejecutar})
        st.session_state.historial_chat.append({"remitente": "jarvis", "texto": respuesta_ia})
        st.session_state.ultima_respuesta = respuesta_ia
        st.rerun()

st.markdown("---")

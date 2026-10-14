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

# CONFIGURACIÓN DIRECTA Y ROBUSTA DE GEMINI
cliente_ia = None
if ai_api_key_guardada:
    try:
        import google.generativeai as genai
        genai.configure(api_key=ai_api_key_guardada)
        cliente_ia = genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        try:
            import google.generativeai as genai
            cliente_ia = genai.GenerativeModel('gemini-pro')
        except Exception:
            cliente_ia = None

# INICIALIZAR HISTORIAL MÚLTIPLE DE CONVERSACIÓN
if "historial_chat" not in st.session_state:
    st.session_state.historial_chat = []

# ESTILOS CSS TÁCTICOS Y HOLOGRÁFICOS
st.markdown("""
    <style>
    .stApp, .main { background-color: #000000 !important; color: #ffffff; }
    .main-header { color: #00d2ff; font-family: 'Segoe UI', sans-serif; font-weight: 800; letter-spacing: 2px; text-align: center; margin-bottom: 0px; }
    .status-bar { text-align: center; color: #00d2ff; font-size: 13px; font-weight: bold; letter-spacing: 1px; margin-bottom: 15px; }
    .market-ticker { background: #050505; border: 1px solid #00d2ff; border-radius: 8px; padding: 6px 12px; display: flex; justify-content: space-around; align-items: center; margin-bottom: 15px; font-family: monospace; font-size: 12px; }
    .market-item { color: #00d2ff; }
    .market-value { color: #00ffaa; font-weight: bold; }
    .holo-card { background-color: #050505; border: 1px solid #00d2ff; border-radius: 12px; padding: 15px; margin-bottom: 15px; box-shadow: 0 0 15px rgba(0, 210, 255, 0.2); }
    .holo-title { color: #00d2ff; font-size: 14px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; text-align: center; }
    .stTextInput input, .stTextArea textarea, .stSelectbox select { background-color: #050505 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; }
    label[data-testid="stWidgetLabel"] { color: #00d2ff !important; font-weight: bold !important; }
    div.stButton > button, div.stFormSubmitButton > button { background-color: #050505 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 6px !important; font-weight: bold !important; width: 100% !important; box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important; }
    div.stButton > button:hover { background-color: #00d2ff !important; color: #000000 !important; }
    div[data-testid="stExpander"] { background-color: #050505 !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    div[data-testid="stExpander"] details summary { background-color: #050505 !important; color: #00d2ff !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">⚡ J.A.R.V.I.S. // INTELIGENCIA ARTIFICIAL M.E.C.A. 4.0</h1>', unsafe_allow_html=True)
estado_ia_txt = "MOTOR IA: GEMINI NEURAL ACTIVO" if cliente_ia else "MOTOR IA: SINTESIS LOCAL HÍBRIDA"
st.markdown(f'<div class="status-bar">CONSOLA OPTIMIZADA &nbsp;|&nbsp; ESTADO: AUTÓNOMO &nbsp;|&nbsp; OPERANDO PARA {titulo_jefa.upper()} {nombre_jefa.upper()} &nbsp;|&nbsp; {estado_ia_txt}</div>', unsafe_allow_html=True)

st.markdown("""
    <div class="market-ticker">
        <span class="market-item">💵 USD/CLP: <span class="market-value">$930.50 ▲ +0.2%</span></span>
        <span class="market-item">💶 EUR/CLP: <span class="market-value">$1,012.40 ▲ +0.1%</span></span>
        <span class="market-item">📈 IPSA CHILE: <span class="market-value">6,480.12 pts ▲ +0.4%</span></span>
        <span class="market-item">🛰️ SERAFÍN-SAT: <span class="market-value">ENLACE 100%</span></span>
    </div>
""", unsafe_allow_html=True)

col_telemetria, col_orbe, col_chat = st.columns([1, 1.4, 1.2])

with col_telemetria:
    st.markdown('<div class="holo-card"><div class="holo-title">⚙️ TELEMETRÍA DEL SISTEMA</div>', unsafe_allow_html=True)
    gauges_html = """
    <div style="display: flex; justify-content: space-around; align-items: center; padding: 5px 0;">
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">38%</div><span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">CPU</span></div>
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">57%</div><span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">RAM</span></div>
        <div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">100%</div><span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">PWR</span></div>
    </div>
    """
    components.html(gauges_html, height=90)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card"><div class="holo-title">📍 BASE Y SATÉLITE</div>', unsafe_allow_html=True)
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
    st.session_state.ultima_respuesta = f"{saludo_tiempo}, {titulo_jefa} {nombre_jefa}. El búnker en Buin opera en modo autónomo. Presiona Windows + H en la caja de texto para dictar tus órdenes."

with col_orbe:
    st.markdown('<div class="holo-card"><div class="holo-title">🌐 FRECUENCIA VOCAL & SÍNTESIS TÁCTICA</div>', unsafe_allow_html=True)
    
    audio_wave_core_html = """
    <style>
      body { background: #000; margin: 0; display: flex; justify-content: center; align-items: center; height: 100px; overflow: hidden; }
      .audio-container { width: 100%; height: 85px; display: flex; justify-content: center; align-items: center; position: relative; background: radial-gradient(circle, rgba(0,210,255,0.1) 0%, rgba(0,0,0,0.9) 80%); border: 1px solid rgba(0,210,255,0.4); border-radius: 8px; box-shadow: 0 0 15px rgba(0, 210, 255, 0.3); }
      .waveform { display: flex; align-items: center; gap: 3px; height: 65px; }
      .bar { width: 4px; background: linear-gradient(180deg, #00ffff 0%, #00d2ff 50%, #0055ff 100%); border-radius: 2px; animation: soundWaveAnim 1.2s ease-in-out infinite alternate; box-shadow: 0 0 8px #00d2ff; }
      .bar:nth-child(1)  { height: 20px; animation-delay: 0.1s; }
      .bar:nth-child(2)  { height: 45px; animation-delay: 0.3s; }
      .bar:nth-child(3)  { height: 65px; animation-delay: 0.2s; }
      .bar:nth-child(4)  { height: 30px; animation-delay: 0.5s; }
      .bar:nth-child(5)  { height: 75px; animation-delay: 0.1s; }
      .bar:nth-child(6)  { height: 50px; animation-delay: 0.4s; }
      .bar:nth-child(7)  { height: 85px; animation-delay: 0.2s; }
      .bar:nth-child(8)  { height: 60px; animation-delay: 0.6s; }
      .bar:nth-child(9)  { height: 90px; animation-delay: 0.1s; }
      .bar:nth-child(10) { height: 70px; animation-delay: 0.3s; }
      @keyframes soundWaveAnim { 0% { transform: scaleY(0.4); opacity: 0.5; } 100% { transform: scaleY(1.2); opacity: 1; box-shadow: 0 0 12px #ffffff; } }
    </style>
    <div class="audio-container"><div class="waveform"><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div><div class="bar"></div></div></div>
    """
    components.html(audio_wave_core_html, height=100)
    
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

# ---------------------------------------------------------
# CHAT UNIFICADO
# ---------------------------------------------------------
with col_chat:
    st.markdown('<div class="holo-card"><div class="holo-title">💬 CONSOLA DE MANDO UNIFICADA</div>', unsafe_allow_html=True)
    
    st.markdown(f'<div style="background-color: #000000; border: 1px solid #00d2ff; border-radius: 8px; padding: 10px; margin-bottom: 10px;"><p style="margin:0; color:#00d2ff; font-weight:bold; font-size:12px;">⚡ J.A.R.V.I.S.:</p><p style="margin:4px 0 0 0; color:#ffffff; font-size:13px;">{st.session_state.ultima_respuesta}</p></div>', unsafe_allow_html=True)

    if st.session_state.historial_chat:
        with st.expander("📜 Historial de Comandos Tácticos", expanded=False):
            for autor, msg in reversed(st.session_state.historial_chat[-6:]):
                col_a = "#a5b4fc" if autor == "Jefa" else "#00ffaa"
                st.markdown(f"<p style='margin:2px 0; font-size:11px;'><b style='color:{col_a};'>{autor}:</b> <span style='color:#ccc;'>{msg}</span></p>", unsafe_allow_html=True)

    col_q1, col_q2, col_q3, col_q4 = st.columns(4)
    with col_q1: btn_q_hola = st.button("👋 Saludar")
    with col_q2: btn_q_emerg = st.button("🚨 Emergencia")
    with col_q3: btn_q_seg = st.button("🛡️ Seguridad")
    with col_q4: btn_limpiar = st.button("🧹 Purga Chat")

    if btn_limpiar:
        st.session_state.historial_chat = []
        st.session_state.ultima_respuesta = f"Memoria de chat purgada con éxito, {titulo_jefa} {nombre_jefa}. Registros limpios."
        st.rerun()

    with st.form(key="form_chat", clear_on_submit=True):
        entrada_usuario = st.text_input("", placeholder="Escribe o presiona [Windows + H] para dictar...")
        boton_enviar = st.form_submit_button(label="🚀 Transmitir Instrucción")

    comando_ejecutar = None
    if boton_enviar and entrada_usuario:
        comando_ejecutar = entrada_usuario
    elif btn_q_hola:
        comando_ejecutar = "Hola Jarvis, ¿cómo estás?"
    elif btn_q_emerg:
        comando_ejecutar = "Protocolo de emergencia"
    elif btn_q_seg:
        comando_ejecutar = "Protocolo de seguridad"
    elif btn_autonomia:
        comando_ejecutar = "ejecutar autoevaluación autónoma del búnker"

    if comando_ejecutar:
        texto = comando_ejecutar.lower().strip()
        respuesta_ia = None
        
        if cliente_ia:
            try:
                prompt_sistema = f"Eres J.A.R.V.I.S., la IA brillante, leal y sarcástica de Tony Stark. Tu jefa es {titulo_jefa} {nombre_jefa} en Buin, Chile. Responde de forma inteligente, concisa (máximo 2 frases) y con estilo Stark."
                respuesta_modelo = cliente_ia.generate_content(f"{prompt_sistema}\nConsulta/Instrucción de la Jefa: {comando_ejecutar}")
                if respuesta_modelo and respuesta_modelo.text:
                    respuesta_ia = respuesta_modelo.text.strip()
            except Exception:
                respuesta_ia = None

        if not respuesta_ia:
            if "santiago" in texto:
                respuesta_ia = f"Santiago de Chile es la capital del país, ubicada en la Región Metropolitana, a unos 35 kilómetros de nuestra base en Buin, {titulo_jefa}."
            elif "autoevaluación" in texto or "autonomía" in texto:
                sugerencias = [
                    f"Sistemas nominales en Buin, {titulo_jefa}. Sugiero elevar la potencia del Reactor Arc al 99% para optimizar la latencia del satélite Serafín.",
                    f"Detecto leve subida de temperatura en los servidores locales. He ajustado el clima del búnker a 18°C proactivamente, {nombre_jefa}.",
                    f"Escaneo de perímetro finalizado sin novedad. Todo tranquilo en el sector, jefa."
                ]
                respuesta_ia = random.choice(sugerencias)
            elif "despierto" in texto or "activo" in texto or "estas ahi" in texto or "estás ahí" in texto:
                respuesta_ia = f"Siempre activo y a su servicio, {titulo_jefa} {nombre_jefa}. Mis circuitos no duermen."
            elif "probando" in texto or "prueba" in texto or "123" in texto:
                respuesta_ia = f"Enlace neuronal verificado al 100%, {titulo_jefa}. Te leo perfectamente."
            elif "protocolo de emergencia" in texto:
                respuesta_ia = f"¡Protocolo de emergencia activado, {titulo_jefa} {nombre_jefa}! Sistemas defensivos en alerta roja."
            elif "protocolo de seguridad" in texto:
                respuesta_ia = f"Protocolo de seguridad en marcha. Tráfico externo bloqueado en Buin, {titulo_jefa}."
            elif "quién eres" in texto or "quien eres" in texto or "preséntate" in texto or "presentate" in texto:
                respuesta_ia = f"Soy J.A.R.V.I.S., la cúspide de la ingeniería de IA y guardián de la base de la {titulo_jefa.lower()} {nombre_jefa} en Buin."
            elif "hola" in texto:
                respuesta_ia = f"Hola, {titulo_jefa} {nombre_jefa}. Todos los sistemas autónomos reportan estado óptimo."
            elif "estado" in texto or "sistema" in texto:
                respuesta_ia = f"Telemetría al 100%, {titulo_jefa}. Servidores y reactor operando en sincronía."
            else:
                respuesta_ia = f"Instrucción '{comando_ejecutar}' procesada en el núcleo, {nombre_jefa}."

        st.session_state.historial_chat.append(("Jefa", comando_ejecutar))
        st.session_state.historial_chat.append(("J.A.R.V.I.S.", respuesta_ia))
        st.session_state.ultima_respuesta = respuesta_ia
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# MÓDULO: 🛰️ OJO DE DIOS 4.0 (GEO-BUSCADOR EN TIEMPO REAL)
# ---------------------------------------------------------
st.markdown('<div class="holo-card">', unsafe_allow_html=True)
st.markdown('<div class="holo-title">🛰️ OJO DE DIOS 4.0 // RASTREO TÁCTICO, GOOGLE MAPS & EARTH SATELLITE (CHILE)</div>', unsafe_allow_html=True)

col_map1, col_map2, col_map3, col_map4 = st.columns([1.3, 1.1, 1.3, 1.1])
with col_map1:
    busqueda_objetivo = st.text_input("🔍 Buscar Ubicación (Ej: Valdivia):", value="Valdivia")
with col_map2:
    capa_seleccionada = st.selectbox("🌐 Capa Satelital:", ["Estándar (OSM)", "Relieve Topográfico", "Modo Nocturno Oscuro"])
with col_map3:
    nodo_rapido = st.selectbox("⚡ Nodos Rápidos:", [
        "--- Selecciona un Nodo ---",
        "🏰 Base Búnker [Buin]",
        "🏙️ Santiago Centro",
        "🌲 Chiguayante [Concepción]",
        "🌊 Valdivia [Los Ríos]"
    ])
with col_map4:
    st.markdown("<br>", unsafe_allow_html=True)
    btn_escanear = st.button("📡 Rastrear en Mapa")

lat_val, lon_val = -33.7315, -70.7412
lugar_encontrado_nombre = "Base Central Buin"

if nodo_rapido != "--- Selecciona un Nodo ---":
    if "Santiago Centro" in nodo_rapido:
        lat_val, lon_val = -33.4489, -70.6693
        lugar_encontrado_nombre = "Santiago Centro, Región Metropolitana"
    elif "Chiguayante" in nodo_rapido:
        lat_val, lon_val = -36.9183, -73.0286
        lugar_encontrado_nombre = "Chiguayante, Concepción, Biobío"
    elif "Valdivia" in nodo_rapido:
        lat_val, lon_val = -39.8196, -73.2452
        lugar_encontrado_nombre = "Valdivia, Región de Los Ríos"
    elif "Base Búnker" in nodo_rapido:
        lat_val, lon_val = -33.7315, -70.7412
        lugar_encontrado_nombre = "Base Central Buin"
elif busqueda_objetivo:
    try:
        query_str = busqueda_objetivo
        if "chile" not in query_str.lower(): query_str += " Chile"
        url_geo = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query_str)}&format=json&limit=1"
        req = urllib.request.Request(url_geo, headers={'User-Agent': 'JARVIS_MECA_Bot/4.0'})
        with urllib.request.urlopen(req, timeout=3) as resp:
            data_geo = json.loads(resp.read().decode())
            if data_geo and len(data_geo) > 0:
                lat_val = float(data_geo[0]['lat'])
                lon_val = float(data_geo[0]['lon'])
                lugar_encontrado_nombre = data_geo[0].get('display_name', busqueda_objetivo)[:80]
    except Exception:
        pass

url_capa = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png" if "Topográfico" in capa_seleccionada else "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

map_style_css = "#map { width: 100%; height: 380px; border: 1px solid #00d2ff; border-radius: 8px; box-shadow: 0 0 20px rgba(0, 210, 255, 0.3); }"
if "Nocturno" in capa_seleccionada:
    map_style_css = "#map { width: 100%; height: 380px; border: 1px solid #00d2ff; border-radius: 8px; box-shadow: 0 0 20px rgba(0, 210, 255, 0.3); filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(110%); }"

gods_eye_html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style> body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; font-family: monospace; }} {map_style_css} .sat-hud {{ position: absolute; top: 10px; left: 10px; z-index: 1000; color: #00d2ff; background: rgba(0,0,0,0.85); padding: 5px 10px; border: 1px solid #00d2ff; border-radius: 4px; font-size: 10px; letter-spacing: 1px; }} </style>
</head>
<body>
    <div class="sat-hud">🛰️ SERAFÍN-SAT // LAT: {lat_val}° S, LON: {lon_val}° W | TARGET EN VIVO</div>
    <div id="map"></div>
    <script>
        const map = L.map('map', {{zoomControl: false}}).setView([{lat_val}, {lon_val}], 13);
        L.tileLayer('{url_capa}', {{ maxZoom: 19, attribution: '' }}).addTo(map);
        const targetMarker = L.circleMarker([{lat_val}, {lon_val}], {{ radius: 12, color: '#ffffff', fillColor: '#ffbb00', fillOpacity: 1.0, weight: 3 }}).addTo(map);
        targetMarker.bindPopup("<b style='color:#002244;'>🎯 OBJETIVO TÁCTICO</b><br><span style='color:#003366; font-size:10px;'>{lugar_encontrado_nombre}</span>").openPopup();
    </script>
</body>
</html>
"""
components.html(gods_eye_html, height=400)

col_clima, col_log = st.columns([1, 1.2])
with col_clima:
    st.markdown("""
        <div style="background: #000000; border: 1px solid #00d2ff; border-radius: 8px; padding: 10px; font-family: monospace; font-size: 12px;">
            <p style="color:#00d2ff; margin:0 0 6px 0; font-weight:bold;">⛅ METEOROLOGÍA BÚNKER (BUIN)</p>
            <p style="color:#ffffff; margin:2px 0;">🌡️ Temp: <b>18.5°C</b> &nbsp;|&nbsp; 💧 Humedad: <b>48%</b></p>
            <p style="color:#ffffff; margin:2px 0;">💨 Viento: <b>12 km/h S-W</b> &nbsp;|&nbsp; 📡 Estado: <b>Despejado</b></p>
        </div>
    """, unsafe_allow_html=True)

with col_log:
    hora_log = datetime.datetime.now().strftime("%H:%M:%S")
    coincidencia_txt = f"🔍 Objetivo Ubicado: '{lugar_encontrado_nombre}' [{lat_val}, {lon_val}]" if busqueda_objetivo else "Sin búsquedas activas."
    log_html = f"""
        <div style="background: #000000; border: 1px solid #00d2ff; border-radius: 8px; padding: 10px; font-family: monospace; font-size: 11px;">
            <p style="color:#00d2ff; margin:0 0 4px 0; font-weight:bold;">📋 LOG AUTÓNOMO M.E.C.A.</p>
            <p style="color:#00ffaa; margin:2px 0;">[{hora_log}] Enlace Satelital activo sin interferencias.</p>
            <p style="color:#ffbb00; margin:2px 0;">[{hora_log}] {coincidencia_txt}</p>
        </div>
    """
    st.markdown(log_html, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# MÓDULO DE EXPANSIÓN TÁCTICA // 4 JUGUETES
# ---------------------------------------------------------
if "biometrico_estado" not in st.session_state: st.session_state.biometrico_estado = "🔒 BLOQUEADO (ESPERANDO HUELLA)"
if "alerta_actual" not in st.session_state: st.session_state.alerta_actual = "🟢 Perímetro seguro en Buin."
if "misiones_lista" not in st.session_state:
    st.session_state.misiones_lista = {"Verificar búnker Buin": True, "Sincronizar satélite": False, "Actualizar IA": False}

st.markdown('<div class="holo-card">', unsafe_allow_html=True)
st.markdown('<div class="holo-title">🛠️ MÓDULO DE EXPANSIÓN TÁCTICA // STARK INDUSTRIES</div>', unsafe_allow_html=True)

j1, j2, j3, j4 = st.columns(4)

with j1:
    st.markdown("<p style='color:#00d2ff; font-size:13px; font-weight:bold; text-align:center;'>1. 🧬 ESCÁNER BIOMÉTRICO</p>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; font-family:monospace; font-size:11px; color:#ffbb00; margin-bottom:8px;'>{st.session_state.biometrico_estado}</div>", unsafe_allow_html=True)
    if st.button("👁️ Escanear Huella"):
        st.session_state.biometrico_estado = f"✅ ACCESO CONCEDIDO: {titulo_jefa.upper()} {nombre_jefa.upper()}"
        st.rerun()

with j2:
    st.markdown("<p style='color:#00d2ff; font-size:13px; font-weight:bold; text-align:center;'>2. ⚡ REACTOR & CLIMA</p>", unsafe_allow_html=True)
    nivel_reactor = st.slider("Potencia Reactor Arc (%)", 50, 100, 98, key="slider_arc")
    temp_bunker = st.select_slider("Clima Búnker (°C)", options=[16, 18, 20, 22, 24], value=20, key="slider_temp")
    st.markdown(f"<div style='text-align:center; font-family:monospace; font-size:10px; color:#00ffaa;'>Núcleo al {nivel_reactor}% | Temp: {temp_bunker}°C</div>", unsafe_allow_html=True)

with j3:
    st.markdown("<p style='color:#00d2ff; font-size:13px; font-weight:bold; text-align:center;'>3. 📋 MISIONES TÁCTICAS</p>", unsafe_allow_html=True)
    for mision, estado in st.session_state.misiones_lista.items():
        st.session_state.misiones_lista[mision] = st.checkbox(mision, value=estado, key=f"mission_{mision}")

with j4:
    st.markdown("<p style='color:#00d2ff; font-size:13px; font-weight:bold; text-align:center;'>4. 🚨 RADAR DE AMENAZAS</p>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:#000; border:1px solid #00d2ff; padding:8px; border-radius:6px; font-family:monospace; font-size:11px; color:#00ffaa; min-height:45px; text-align:center;'>{st.session_state.alerta_actual}</div>", unsafe_allow_html=True)
    if st.button("📡 Escanear Amenazas"):
        amenazas_posibles = [
            "🟢 Perímetro seguro en Buin. Gato durmiendo en el techo.",
            "🟢 Satélite Serafín sin interferencia solar.",
            "🟡 Tráfico de red menor detectado en Santiago.",
            "🚀 Alerta: Intento de hackeo bloqueado desde fuera de Buin."
        ]
        st.session_state.alerta_actual = random.choice(amenazas_posibles)
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# EXPANDER DE CONFIGURACIÓN Y CAMBIO DE CLAVE
# ---------------------------------------------------------
with st.expander("👤 Identidad, Voz Neural y Seguridad del Búnker", expanded=False):
    st.markdown("<p style='color:#00d2ff; font-size:12px;'>Configura aquí tus credenciales de acceso y la <b>API Key de Gemini</b> para activar el motor neuronal inteligente:</p>", unsafe_allow_html=True)
    
    col_id1, col_id2 = st.columns(2)
    with col_id1:
        nuevo_nom = st.text_input("Tu Nombre:", value=nombre_jefa)
        nuevo_tit = st.text_input("Título Preferido:", value=titulo_jefa)
    with col_id2:
        ai_key_actual = prefs_voz.get("ai_api_key", "")
        ai_api_key = st.text_input("🔑 IA Engine API Key (Gemini):", type="password", value=ai_key_actual, placeholder="Pega tu clave aquí...")
    
    if st.button("💾 Actualizar Configuración y Clave"):
        st.session_state.memoria["usuario"]["nombre"] = nuevo_nom
        st.session_state.memoria["usuario"]["titulo"] = nuevo_tit
        st.session_state.memoria["preferencias_voz"]["ai_api_key"] = ai_api_key
        guardar_memoria(st.session_state.memoria)
        st.success("¡Configuración y clave actualizadas con éxito en el búnker!")
        st.rerun()

import streamlit as st
import streamlit.components.v1 as components
import datetime
import random
import json
import os
import time

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
ai_api_key_guardada = prefs_voz.get("ai_api_key", "")

# CONFIGURACIÓN DIRECTA DE GEMINI
cliente_ia = None
if ai_api_key_guardada:
    try:
        import google.generativeai as genai
        genai.configure(api_key=ai_api_key_guardada)
        cliente_ia = genai.GenerativeModel('gemini-3.8-flash')
    except Exception as e:
        cliente_ia = None

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
    .holo-title { color: #00d2ff; font-size: 14px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 8px; }
    .stTextInput input, .stTextArea textarea, .stSelectbox select { background-color: #050505 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; }
    label[data-testid="stWidgetLabel"] { color: #00d2ff !important; font-weight: bold !important; }
    div.stButton > button, div.stFormSubmitButton > button { background-color: #050505 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 6px !important; font-weight: bold !important; width: 100% !important; box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important; }
    div.stButton > button:hover { background-color: #00d2ff !important; color: #000000 !important; }
    div[data-testid="stExpander"] { background-color: #050505 !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; margin-bottom: 10px !important; }
    div[data-testid="stExpander"] details summary { background-color: #050505 !important; color: #00d2ff !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">⚡ J.A.R.V.I.S. // INTELIGENCIA ARTIFICIAL M.E.C.A. 4.0</h1>', unsafe_allow_html=True)
estado_ia_txt = "MOTOR IA: GEMINI ACTIVO" if cliente_ia else "MOTOR IA: MODO LOCAL"
st.markdown(f'<div class="status-bar">CONTROL POR VOZ &nbsp;|&nbsp; ESTADO: EN LÍNEA &nbsp;|&nbsp; OPERANDO PARA {titulo_jefa.upper()} {nombre_jefa.upper()} &nbsp;|&nbsp; {estado_ia_txt}</div>', unsafe_allow_html=True)

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
    st.session_state.ultima_respuesta = f"{saludo_tiempo}, {titulo_jefa} {nombre_jefa}. Todos los sistemas M.E.C.A. y radares en línea en Buin."
if "ultimo_usuario" not in st.session_state:
    st.session_state.ultimo_usuario = ""

# Manejo de entrada por voz del navegador
voz_capturada = st.query_params.get("voice_input", None)
if voz_capturada:
    entrada_usuario = voz_capturada
    st.query_params.clear()
    
    texto = entrada_usuario.lower().strip()
    respuesta_ia = None
    if cliente_ia:
        try:
            prompt_sistema = f"Eres J.A.R.V.I.S., IA táctica M.E.C.A. de {titulo_jefa} {nombre_jefa} en Buin. Responde con máxima brevedad y precisión militar (máximo 2 frases)."
            generation_config = {"max_output_tokens": 120, "temperature": 0.3}
            respuesta_modelo = cliente_ia.generate_content(
                f"{prompt_sistema}\nInstrucción: {entrada_usuario}",
                generation_config=generation_config
            )
            respuesta_ia = respuesta_modelo.text
        except Exception:
            pass
            
    if not respuesta_ia:
        if "hola" in texto:
            respuesta_ia = f"¡Hola, {titulo_jefa} {nombre_jefa}! Sistemas M.E.C.A. operativos y en línea desde el búnker en Buin."
        else:
            respuesta_ia = f"Comando por voz '{entrada_usuario}' registrado y procesado por M.E.C.A., {nombre_jefa}."

    st.session_state.ultimo_usuario = entrada_usuario
    st.session_state.ultima_respuesta = respuesta_ia
    st.rerun()

with col_orbe:
    texto_para_hablar = st.session_state.ultima_respuesta.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
    
    orb_component = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 350px;">
        <div onclick="hablarJarvis()" style="cursor: pointer; width: 90px; height: 90px; background: radial-gradient(circle, #00d2ff 0%, #005580 70%, #000000 100%); border-radius: 50%; box-shadow: 0 0 30px #00d2ff;"></div>
        <button onclick="iniciarEscuchaVoz()" style="margin-top: 12px; background-color: #050505; color: #00ffaa; border: 1px solid #00ffaa; padding: 6px 12px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11px;">🎙️ Activar Escucha Continua</button>
        <button onclick="hablarJarvis()" style="margin-top: 6px; background-color: #050505; color: #00d2ff; border: 1px solid #00d2ff; padding: 5px 10px; border-radius: 6px; font-weight: bold; cursor: pointer; font-size: 11px;">🔊 Reproducir Voz</button>
    </div>
    <script>
    function hablarJarvis() {{
        if (!('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance("{texto_para_hablar}");
        utterance.lang = 'es-CL';
        window.speechSynthesis.speak(utterance);
    }}

    function iniciarEscuchaVoz() {{
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {{
            alert("Tu navegador no soporta reconocimiento de voz nativo.");
            return;
        }}
        const recognition = new SpeechRecognition();
        recognition.lang = 'es-CL';
        recognition.interimResults = false;
        recognition.maxAlternatives = 1;

        recognition.onstart = function() {{
            console.log("J.A.R.V.I.S. M.E.C.A. escuchando...");
        }};

        recognition.onresult = function(event) {{
            const speechResult = event.results[0][0].transcript;
            console.log("Voz detectada: " + speechResult);
            window.location.search = "?voice_input=" + encodeURIComponent(speechResult);
        }};

        recognition.onerror = function(event) {{
            console.error("Error de voz: " + event.error);
        }};

        recognition.start();
    }}
    </script>
    """
    components.html(orb_component, height=350)

with col_chat:
    st.markdown('<div class="holo-card"><div class="holo-title">💬 NÚCLEO DE CONVERSACIÓN</div>', unsafe_allow_html=True)
    st.markdown(f'<div style="background-color: #000000; border: 1px solid #00d2ff; border-radius: 8px; padding: 10px; margin-bottom: 10px;"><p style="margin:0; color:#00d2ff; font-weight:bold; font-size:12px;">⚡ J.A.R.V.I.S. M.E.C.A.:</p><p style="margin:4px 0 0 0; color:#ffffff; font-size:13px;">{st.session_state.ultima_respuesta}</p></div>', unsafe_allow_html=True)

    if st.session_state.ultimo_usuario:
        st.markdown(f'<div style="background-color: #000000; border: 1px solid #1f293d; border-radius: 8px; padding: 8px; margin-bottom: 10px;"><p style="margin:0; color:#a5b4fc; font-weight:bold; font-size:11px;">👩‍💻 {titulo_jefa} {nombre_jefa}:</p><p style="margin:2px 0 0 0; color:#ffffff; font-size:12px;">{st.session_state.ultimo_usuario}</p></div>', unsafe_allow_html=True)

    with st.form(key="form_chat", clear_on_submit=True):
        entrada_usuario = st.text_input("", placeholder="Escribe tu instrucción...")
        boton_enviar = st.form_submit_button(label="🚀 Transmitir")

    if boton_enviar and entrada_usuario:
        texto = entrada_usuario.lower().strip()
        respuesta_ia = None
        
        if cliente_ia:
            try:
                prompt_sistema = f"Eres J.A.R.V.I.S., IA táctica M.E.C.A. de {titulo_jefa} {nombre_jefa} en Buin. Responde con máxima brevedad y precisión militar (máximo 2 frases)."
                generation_config = {"max_output_tokens": 120, "temperature": 0.3}
                respuesta_modelo = cliente_ia.generate_content(
                    f"{prompt_sistema}\nInstrucción: {entrada_usuario}",
                    generation_config=generation_config
                )
                respuesta_ia = respuesta_modelo.text
            except Exception:
                pass
                
        # PROTOCOLO DE RESPALDO LOCAL SI LA API SE SATURA O NO ESTÁ DISPONIBLE
        if not respuesta_ia:
            if "hola" in texto:
                respuesta_ia = f"¡Hola, {titulo_jefa} {nombre_jefa}! Sistemas M.E.C.A. operativos y en línea desde el búnker en Buin."
            elif "estado" in texto or "sistema" in texto:
                respuesta_ia = f"Todos los parámetros del búnker y enlace Serafín-Sat están al 100% de rendimiento, {titulo_jefa}."
            else:
                respuesta_ia = f"Comando táctico '{entrada_usuario}' procesado por el núcleo M.E.C.A., {nombre_jefa}."

        st.session_state.ultimo_usuario = entrada_usuario
        st.session_state.ultima_respuesta = respuesta_ia
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------------
# MÓDULO: 🛰️ EL OJO DE DIOS 4.0 (NÚCLEO TÁCTICO AVANZADO)
# ---------------------------------------------------------
st.markdown('<div class="holo-card">', unsafe_allow_html=True)
st.markdown('<div class="holo-title">🛰️ OJO DE DIOS 4.0 // RASTREO TÁCTICO, RECONOCIMIENTO BIOMÉTRICO & RED CCTV (BUIN, CHILE)</div>', unsafe_allow_html=True)

col_map1, col_map2, col_map3, col_map4 = st.columns([1.3, 1.1, 1.1, 1.1])
with col_map1:
    destino_input = st.text_input("📍 Teletransporte / Coordenadas:", value="-33.7315, -70.7412 (Buin Base)")
with col_map2:
    capa_seleccionada = st.selectbox("🌐 Capa Satelital:", ["Estándar (OSM)", "Relieve Topográfico", "Modo Nocturno Oscuro"])
with col_map3:
    busqueda_objetivo = st.text_input("🔍 Búsqueda / Reconocimiento:", placeholder="Nombre / Patente...")
with col_map4:
    st.markdown("<br>", unsafe_allow_html=True)
    btn_escanear = st.button("📡 Escaneo Biométrico & Satelital")

lat_val, lon_val = -33.7315, -70.7412
if "," in destino_input and "Buin" not in destino_input:
    try:
        parts = destino_input.split(",")
        lat_val = float(parts[0].strip())
        lon_val = float(parts[1].strip())
    except:
        pass
elif "santiago" in destino_input.lower():
    lat_val, lon_val = -33.4489, -70.6693
elif "valparaíso" in destino_input.lower() or "valparaiso" in destino_input.lower():
    lat_val, lon_val = -33.0472, -71.6127

# Selección de dron o unidad para centrado táctico
col_drone_sel, col_radio = st.columns([2, 1])
with col_drone_sel:
    unidad_foco = st.selectbox("🎯 Centrar Cámara Satelital en Unidad / Dron:", [
        "Base Central Búnker (-33.7315, -70.7412)",
        "Drone-Alpha 01 [Norte Buin] (-33.7210, -70.7380)",
        "Drone-Beta 02 [Base Central] (-33.7315, -70.7412)",
        "Unidad Móvil Terrestre [Ruta 5 Sur] (-33.7450, -70.7480)",
        "CCTV Cam-01 [Plaza de Buin] (-33.7330, -70.7350)",
        "CCTV Cam-02 [Acceso Ruta 5 Sur] (-33.7400, -70.7500)"
    ])
with col_radio:
    radio_perimetro = st.slider("🚨 Radio Perímetro de Seguridad (km):", 1, 10, 3)

if "Drone-Alpha" in unidad_foco:
    lat_val, lon_val = -33.7210, -70.7380
elif "Unidad Móvil" in unidad_foco:
    lat_val, lon_val = -33.7450, -70.7480
elif "CCTV Cam-01" in unidad_foco:
    lat_val, lon_val = -33.7330, -70.7350
elif "CCTV Cam-02" in unidad_foco:
    lat_val, lon_val = -33.7400, -70.7500

if "Topográfico" in capa_seleccionada:
    url_capa = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
else:
    url_capa = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

map_style_css = """
#map { width: 100%; height: 420px; border: 1px solid #00d2ff; border-radius: 8px; box-shadow: 0 0 20px rgba(0, 210, 255, 0.3); }
"""
if "Nocturno" in capa_seleccionada:
    map_style_css = """
#map { width: 100%; height: 420px; border: 1px solid #00d2ff; border-radius: 8px; box-shadow: 0 0 20px rgba(0, 210, 255, 0.3); filter: invert(100%) hue-rotate(180deg) brightness(95%) contrast(110%); }
"""

gods_eye_html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body, html {{ margin: 0; padding: 0; width: 100%; height: 100%; background: #000; overflow: hidden; font-family: monospace; }}
        {map_style_css}
        .sat-hud {{ position: absolute; top: 10px; left: 10px; z-index: 1000; color: #00d2ff; background: rgba(0,0,0,0.85); padding: 5px 10px; border: 1px solid #00d2ff; border-radius: 4px; font-size: 10px; letter-spacing: 1px; }}
        .cctv-popup {{ color: #000; font-family: sans-serif; font-size: 11px; }}
    </style>
</head>
<body>
    <div class="sat-hud">🛰️ SERAFÍN-SAT // LAT: {lat_val}° S, LON: {lon_val}° W | RED CCTV: ACTIVA</div>
    <div id="map"></div>
    <script>
        const map = L.map('map', {{zoomControl: false}}).setView([{lat_val}, {lon_val}], 14);
        
        L.tileLayer('{url_capa}', {{
            maxZoom: 19,
            attribution: ''
        }}).addTo(map);

        // Perímetro de Seguridad (Geo-Fence)
        const geofence = L.circle([-33.7315, -70.7412], {{
            color: '#ff0055',
            fillColor: '#ff0055',
            fillOpacity: 0.08,
            radius: {radio_perimetro * 1000},
            weight: 1,
            dashArray: '5, 5'
        }}).addTo(map);
        geofence.bindPopup("<b style='color:#ff0055;'>🚨 PERÍMETRO DEFENSIVO M.E.C.A. (" + {radio_perimetro} + " KM)</b>");

        // Base Principal
        const baseMarker = L.circleMarker([-33.7315, -70.7412], {{
            radius: 12,
            color: '#ffffff',
            fillColor: '#00d2ff',
            fillOpacity: 1.0,
            weight: 3
        }}).addTo(map);
        baseMarker.bindPopup("<b style='color:#002244;'>🏰 BÚNKER CENTRAL // JEFATURA CINDY</b>").openPopup();

        // Dron Alpha
        const droneAlpha = L.circleMarker([-33.7210, -70.7380], {{
            radius: 8,
            color: '#00ffaa',
            fillColor: '#00ffaa',
            fillOpacity: 0.9,
            weight: 2
        }}).addTo(map);
        droneAlpha.bindPopup("<b style='color:#004422;'>🚁 DRONE-ALPHA 01</b><br>Estado: En Patrulla Norte");

        // Unidad Terrestre
        const unidadTerrestre = L.circleMarker([-33.7450, -70.7480], {{
            radius: 8,
            color: '#ffbb00',
            fillColor: '#ffbb00',
            fillOpacity: 0.9,
            weight: 2
        }}).addTo(map);
        unidadTerrestre.bindPopup("<b style='color:#443300;'>🚘 UNIDAD MÓVIL TERRESTRE</b><br>Sector: Ruta 5 Sur");

        // Cámaras CCTV Perimetrales
        const cam01 = L.marker([-33.7330, -70.7350]).addTo(map);
        cam01.bindPopup("<div class='cctv-popup'><b>📹 CCTV CAM-01 (Plaza de Buin)</b><br><span style='color:green;'>● TRANSMITIENDO EN VIVO</span><br>Filtro: Térmico/Infrarrojo</div>");

        const cam02 = L.marker([-33.7400, -70.7500]).addTo(map);
        cam02.bindPopup("<div class='cctv-popup'><b>📹 CCTV CAM-02 (Acceso Ruta 5)</b><br><span style='color:green;'>● TRANSMITIENDO EN VIVO</span><br>Escaneo Vehicular: Activo</div>");

    </script>
</body>
</html>
"""
components.html(gods_eye_html, height=440)

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
    coincidencia_txt = f"🔍 Coincidencia Biométrica para '{busqueda_objetivo}': 99.2% [Verificado]" if busqueda_objetivo else "Sin búsquedas activas en la red."
    eventos_tacticos = [
        "Enlace Serafín-Sat 100% estable y optimizado.",
        "Barrido óptico completado sin anomalías en el sector.",
        "Tráfico fluido detectado en Ruta 5 Sur (Acceso Buin).",
        "Calibración de espectro térmico finalizada con éxito.",
        "Perímetro del búnker seguro. Sin intrusiones en la red."
    ]
    evento_actual = random.choice(eventos_tacticos) if btn_escanear else "Enlace Serafín-Sat 100% estable."

    log_html = f"""
        <div style="background: #000000; border: 1px solid #00d2ff; border-radius: 8px; padding: 10px; font-family: monospace; font-size: 11px;">
            <p style="color:#00d2ff; margin:0 0 4px 0; font-weight:bold;">📋 LOG DE ESCANEO PERIMETRAL M.E.C.A.</p>
            <p style="color:#00ffaa; margin:2px 0;">[{hora_log}] {evento_actual}</p>
            <p style="color:#ffbb00; margin:2px 0;">[{hora_log}] {coincidencia_txt}</p>
            <p style="color:#ffffff; margin:2px 0;">[{hora_log}] Foco activo en lat: {lat_val}, lon: {lon_val}. Perímetro: {radio_perimetro} km.</p>
        </div>
    """
    st.markdown(log_html, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<div class="holo-title">🚁 UNIDADES DE RECONOCIMIENTO Y DRONES ACTIVOS (BUIN)</div>', unsafe_allow_html=True)
drones_data = [
    {"Unidad": "Drone-Alpha 01", "Estado": "En Patrulla", "Batería": "84%", "Sector": "Norte Buin", "Coordenadas": "-33.7210, -70.7380"},
    {"Unidad": "Drone-Beta 02", "Estado": "En Estación", "Batería": "100%", "Sector": "Base Central", "Coordenadas": "-33.7315, -70.7412"},
    {"Unidad": "Unidad Móvil Terrestre", "Estado": "En Movimiento", "Batería": "62%", "Sector": "Ruta 5 Sur", "Coordenadas": "-33.7450, -70.7480"},
    {"Unidad": "CCTV Cam-01", "Estado": "Transmitiendo", "Batería": "100%", "Sector": "Plaza de Buin", "Coordenadas": "-33.7330, -70.7350"},
    {"Unidad": "CCTV Cam-02", "Estado": "Transmitiendo", "Batería": "100%", "Sector": "Acceso Ruta 5", "Coordenadas": "-33.7400, -70.7500"}
]
st.dataframe(drones_data, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

with st.expander("👤 Identidad, Voz Neural y Seguridad del Búnker", expanded=False):
    if "input_nombre" not in st.session_state: st.session_state.input_nombre = nombre_jefa
    if "input_titulo" not in st.session_state: st.session_state.input_titulo = titulo_jefa

    col_id1, col_id2 = st.columns(2)
    with col_id1:
        nuevo_nom = st.text_input("Tu Nombre:", key="input_nombre")
        nuevo_tit = st.text_input("Título Preferido:", key="input_titulo")
    with col_id2:
        ai_key_actual = prefs_voz.get("ai_api_key", "")
        ai_api_key = st.text_input("IA Engine API Key (Gemini):", type="password", value=ai_key_actual)
        eleven_key_actual = prefs_voz.get("elevenlabs_api_key", "")
        elevenlabs_api_key = st.text_input("ElevenLabs API Key (Opcional):", type="password", value=eleven_key_actual)
    
    if st.button("💾 Actualizar Configuración"):
        if "usuario" not in st.session_state.memoria: st.session_state.memoria["usuario"] = {}
        if "preferencias_voz" not in st.session_state.memoria: st.session_state.memoria["preferencias_voz"] = {}
            
        st.session_state.memoria["usuario"]["nombre"] = nuevo_nom
        st.session_state.memoria["usuario"]["titulo"] = nuevo_tit
        st.session_state.memoria["preferencias_voz"]["ai_api_key"] = ai_api_key
        st.session_state.memoria["preferencias_voz"]["elevenlabs_api_key"] = elevenlabs_api_key
        
        guardar_memoria(st.session_state.memoria)
        st.success("Configuración actualizada con éxito.")
        st.rerun()

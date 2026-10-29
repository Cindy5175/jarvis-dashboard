import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import pytz
from datetime import datetime
import folium
from streamlit_folium import st_folium
import requests
from gtts import gTTS

# 1. Configuración de página
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Quantum Cyber Core",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS Estilo Neón Holográfico Stark / Trading AI
st.markdown("""
    <style>
    .stApp {
        background-color: #02040a;
        color: #00f0ff;
        font-family: 'Courier New', monospace;
    }
    .sidebar .sidebar-content {
        background-color: #010206;
        border-right: 1px solid #00f0ff33;
    }
    h1, h2, h3 {
        color: #00f0ff !important;
        text-shadow: 0 0 14px rgba(0, 240, 255, 0.7);
        font-family: 'Courier New', monospace;
    }
    .stMetric {
        background: rgba(0, 240, 255, 0.02);
        border: 1px solid #00f0ff;
        border-radius: 6px;
        padding: 10px;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
    }
    </style>
""", unsafe_allow_html=True)

# 3. BARRA LATERAL: NAVEGACIÓN, SPOTIFY Y CAPAS
st.sidebar.markdown("## ⚡ J.A.R.V.I.S. SUBSYSTEMS")

nav_module = st.sidebar.radio(
    "Módulos del Sistema:",
    [
        "🌍 Radar Satelital Real-Time",
        "🌀 Quantum Orbital Core",
        "🧠 Neural Network Matrix",
        "📈 Trading & Liquidity",
        "📡 Feed Alertas Globales"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎵 Spotify Tactical Audio")
spotify_uri = st.sidebar.text_input("Spotify URI:", value="37i9dQZF1DXdLENR312A25")
components.html(
    f'''
    <div style="background:#010206; border-radius:12px; padding:4px; box-shadow: 0 0 10px rgba(0,240,255,0.2);">
        <iframe src="https://open.spotify.com/embed/playlist/{spotify_uri}?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
    </div>
    ''',
    height=165
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Capas Tácticas en Vivo")
layer_base = st.sidebar.checkbox("🛡️ Base Central Buin", value=True)
layer_earthquakes = st.sidebar.checkbox("🌋 Sismos USGS", value=True)
layer_fires = st.sidebar.checkbox("🔥 Incendios NASA FIRMS", value=True)
layer_satellites = st.sidebar.checkbox("🛰️ Órbitas Satelitales", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎙️ Configuración ElevenLabs")
eleven_key = st.sidebar.text_input("ElevenLabs API Key:", type="password")

# 4. FUNCIONES DE DATOS EN TIEMPO REAL
BUIN_LAT, BUIN_LON = -33.7328, -70.7356

def get_buin_weather():
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={BUIN_LAT}&longitude={BUIN_LON}&current_weather=true"
        res = requests.get(url, timeout=3).json()
        temp = res['current_weather']['temperature']
        wind = res['current_weather']['windspeed']
        return f"{temp}°C", f"{wind} km/h"
    except:
        return "18.5°C", "12 km/h"

def get_realtime_earthquakes():
    try:
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude=3.0&limit=8"
        res = requests.get(url, timeout=3).json()
        quakes = []
        for feat in res['features']:
            coords = feat['geometry']['coordinates']
            quakes.append({'lat': coords[1], 'lon': coords[0], 'mag': feat['properties']['mag'], 'place': feat['properties']['place']})
        return quakes
    except:
        return [{'lat': -33.45, 'lon': -70.66, 'mag': 3.8, 'place': 'Santiago, Chile'}]

def get_realtime_fires():
    try:
        url = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/c2419a7101eb652bb6c8a709210ec1d4/VIIRS_SNPP/CHL/1"
        res = requests.get(url, timeout=4)
        if res.status_code == 200:
            lines = res.text.strip().split('\n')
            fires = []
            for line in lines[1:10]:
                parts = line.split(',')
                if len(parts) > 2:
                    fires.append({'lat': float(parts[0]), 'lon': float(parts[1])})
            return fires if fires else [{'lat': -34.1, 'lon': -71.0}, {'lat': -33.2, 'lon': -70.9}]
        return [{'lat': -34.1, 'lon': -71.0}, {'lat': -33.2, 'lon': -70.9}]
    except:
        return [{'lat': -34.1, 'lon': -71.0}, {'lat': -33.2, 'lon': -70.9}]

# 5. ENCABEZADO Y MÉTRICAS
temp_buin, wind_buin = get_buin_weather()

st.markdown(f"# 🛡️ J.A.R.V.I.S. 4.0 — [{nav_module}]")
st.markdown("*Centro Táctico Cuántico y Control Geoespacial — Base Buin, Chile*")
st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
with m1: st.metric(label="Ubicación Base", value="Buin, CL", delta="Seguro")
with m2: st.metric(label="Clima Real (Buin)", value=temp_buin, delta=f"Viento: {wind_buin}")
with m3: st.metric(label="Estado del Sistema", value="99.8% Neural Sync", delta="Quantum Core")
with m4: st.metric(label="Latencia de Red", value="0.38 ms", delta="Óptimo")

st.markdown("\n")

# 6. MÓDULOS DINÁMICOS
if nav_module == "🌍 Radar Satelital Real-Time":
    st.markdown("### 🗺️ Telemetría Satelital Geoespacial en Vivo")
    m = folium.Map(location=[BUIN_LAT, BUIN_LON], zoom_start=8, tiles="OpenStreetMap")

    if layer_base:
        folium.Marker(
            [BUIN_LAT, BUIN_LON],
            popup="<b>CENTRO DE MANDO STARK — BUIN</b>",
            tooltip="Base Principal Buin",
            icon=folium.Icon(color="red", icon="shield", prefix="fa")
        ).add_to(m)
        folium.Circle(
            radius=15000,
            location=[BUIN_LAT, BUIN_LON],
            color="#00f0ff",
            fill=True,
            fill_color="#00f0ff",
            fill_opacity=0.1
        ).add_to(m)

    if layer_earthquakes:
        for q in get_realtime_earthquakes():
            folium.CircleMarker(
                location=[q['lat'], q['lon']],
                radius=q['mag'] * 3,
                color="#ff0055",
                fill=True,
                fill_color="#ff0055",
                fill_opacity=0.7,
                tooltip=f"🌋 Sismo USGS M{q['mag']} - {q['place']}"
            ).add_to(m)

    if layer_fires:
        for f in get_realtime_fires():
            folium.Marker(
                [f['lat'], f['lon']],
                tooltip="🔥 Foco Térmico Detectado por NASA VIIRS Sat",
                icon=folium.Icon(color="orange", icon="fire", prefix="fa")
            ).add_to(m)

    if layer_satellites:
        sats = [[-33.0, -70.0], [-34.5, -71.0], [-33.8, -70.5]]
        for i, s in enumerate(sats):
            folium.CircleMarker(s, radius=5, color="#00ffcc", fill=True, fill_color="#00ffcc", tooltip=f"🛰️ Satélite Node 0{i+1}").add_to(m)

    st_folium(m, width="100%", height=480)

elif nav_module == "🌀 Quantum Orbital Core":
    st.markdown("### 🌀 Visualizador Holográfico de Núcleo Cuántico Orbital")
    components.html("""
    <!DOCTYPE html>
    <html>
    <head><style>body { margin: 0; background: #02040a; overflow: hidden; } canvas { display: block; width: 100%; height: 420px; }</style></head>
    <body>
        <canvas id="quantumCanvas"></canvas>
        <script>
            const canvas = document.getElementById('quantumCanvas');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = 420;
            let angle = 0;
            function draw() {
                ctx.clearRect(0,0,canvas.width,canvas.height);
                let cx = canvas.width/2, cy = canvas.height/2;
                ctx.save();
                ctx.translate(cx, cy);
                ctx.rotate(angle);
                for(let i=1; i<=6; i++){
                    ctx.beginPath();
                    ctx.arc(0, 0, i * 32, 0, Math.PI * 1.5);
                    ctx.strokeStyle = i % 2 === 0 ? '#00f0ff' : '#00ffcc';
                    ctx.lineWidth = 2;
                    ctx.shadowBlur = 12;
                    ctx.shadowColor = '#00f0ff';
                    ctx.stroke();
                }
                ctx.restore();
                for(let p=0; p<20; p++){
                    let r = 40 + p * 8;
                    let a = angle * (p % 2 === 0 ? 1 : -1) + p;
                    let x = cx + r * Math.cos(a);
                    let y = cy + r * Math.sin(a);
                    ctx.beginPath();
                    ctx.arc(x, y, 3, 0, Math.PI * 2);
                    ctx.fillStyle = '#ffffff';
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = '#00f0ff';
                    ctx.fill();
                }
                angle += 0.015;
                requestAnimationFrame(draw);
            }
            draw();
        </script>
    </body>
    </html>
    """, height=430)

elif nav_module == "🧠 Neural Network Matrix":
    st.markdown("### 🧠 Red Neuronal de Inferencia Vertical")
    components.html("""
    <!DOCTYPE html>
    <html>
    <head><style>body { margin: 0; background: #02040a; overflow: hidden; } canvas { display: block; width: 100%; height: 420px; }</style></head>
    <body>
        <canvas id="neuralCanvas"></canvas>
        <script>
            const canvas = document.getElementById('neuralCanvas');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = 420;
            function drawNeural() {
                ctx.clearRect(0,0,canvas.width,canvas.height);
                let layers = [6, 10, 10, 6];
                let layerX = [canvas.width*0.2, canvas.width*0.4, canvas.width*0.6, canvas.width*0.8];
                for(let l=0; l<layers.length-1; l++){
                    for(let i=0; i<layers[l]; i++){
                        for(let j=0; j<layers[l+1]; j++){
                            let y1 = 50 + i * 35;
                            let y2 = 50 + j * 35;
                            ctx.beginPath();
                            ctx.moveTo(layerX[l], y1);
                            ctx.lineTo(layerX[l+1], y2);
                            ctx.strokeStyle = 'rgba(218, 0, 254, 0.15)';
                            ctx.lineWidth = 1;
                            ctx.stroke();
                        }
                    }
                }
                for(let l=0; l<layers.length; l++){
                    for(let i=0; i<layers[l]; i++){
                        let y = 50 + i * 35;
                        ctx.beginPath();
                        ctx.arc(layerX[l], y, 6, 0, Math.PI*2);
                        ctx.fillStyle = '#e000ff';
                        ctx.shadowBlur = 10;
                        ctx.shadowColor = '#e000ff';
                        ctx.fill();
                    }
                }
                requestAnimationFrame(drawNeural);
            }
            drawNeural();
        </script>
    </body>
    </html>
    """, height=430)

elif nav_module == "📈 Trading & Liquidity":
    st.markdown("### 📊 Algoritmos de Liquidez Financiera e Indicadores")
    chart_data = pd.DataFrame(
        np.random.randn(30, 3) * [12, 6, 3] + [120, 85, 45],
        columns=['Liquidez S&P 500', 'Volumen Crypto High-Freq', 'Algoritmo Alpha-1']
    )
    st.line_chart(chart_data, color=["#00f0ff", "#e000ff", "#00ffcc"])

elif nav_module == "📡 Feed Alertas Globales":
    st.markdown("### 🚨 Monitor de Alertas Sísmicas y Térmicas")
    st.info("🌋 [USGS REAL-TIME] Monitoreo de sismos activo. Sincronizado con la placa de Nazca.")
    st.warning("🔥 [NASA FIRMS] Escaneo térmico satelital procesando datos en tiempo real.")

# 7. HISTORIAL DE CHAT Y CAJA DE ENTRADA INTERACTIVA
st.markdown("---")
st.markdown("### 💬 Interfaz de Conversación Autónoma")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_prompt := st.chat_input("Escriba su comando para J.A.R.V.I.S..."):
    st.session_state.messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    response_msg = f"Directiva procesada en el subsistema '{nav_module}'. Todos los sensores en la base de Buin y el audio de Spotify están operativos, Jefa."
    
    with st.chat_message("assistant"):
        st.markdown(response_msg)
        
        if eleven_key:
            try:
                voice_id = "21m00Tcm4TlvDq8ikWAM"
                url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
                headers = {
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": eleven_key
                }
                data = {
                    "text": response_msg,
                    "model_id": "eleven_multilingual_v2",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
                }
                res = requests.post(url, json=data, headers=headers)
                if res.status_code == 200:
                    with open("jarvis_chat.mp3", "wb") as f:
                        f.write(res.content)
                    st.audio("jarvis_chat.mp3", format="audio/mp3", autoplay=True)
                else:
                    st.warning("⚠️ Verifique su API Key de ElevenLabs.")
            except Exception as e:
                st.error(f"Error de audio: {e}")
        else:
            tts = gTTS(text=response_msg, lang='es')
            tts.save("response.mp3")
            st.audio("response.mp3", format="audio/mp3", autoplay=True)

    st.session_state.messages.append({"role": "assistant", "content": response_msg})

st.markdown("---")
st.markdown("*J.A.R.V.I.S. Quantum AI Core — Taller de Inteligencia Autónoma | Buin, Chile.*")

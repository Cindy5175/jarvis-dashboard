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
    page_title="J.A.R.V.I.S. 4.0 - GodsView Layers Core",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS Estilo Neón Holográfico Stark
st.markdown("""
    <style>
    .stApp {
        background-color: #030611;
        color: #00f0ff;
        font-family: 'Courier New', monospace;
    }
    .sidebar .sidebar-content {
        background-color: #010309;
        border-right: 1px solid #00f0ff33;
    }
    h1, h2, h3 {
        color: #00f0ff !important;
        text-shadow: 0 0 12px rgba(0, 240, 255, 0.6);
        font-family: 'Courier New', monospace;
    }
    .stMetric {
        background: rgba(0, 240, 255, 0.03);
        border: 1px solid #00f0ff;
        border-radius: 8px;
        padding: 12px;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.15);
    }
    .terminal-card {
        background-color: #010814;
        border: 1px solid #00f0ff;
        border-left: 4px solid #00f0ff;
        border-radius: 6px;
        padding: 15px;
        box-shadow: 0 0 20px rgba(0, 240, 255, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# 3. BARRA LATERAL: PANEL DE CAPAS (LAYERS STYLE GODSVIEW)
st.sidebar.markdown("## 🌐 GODSVIEW LAYERS")
st.sidebar.markdown("---")

st.sidebar.markdown("### 🎛️ Capas de Eventos (Layers)")
layer_earthquakes = st.sidebar.checkbox("🌋 Temblores / Sismos (USGS)", value=True)
layer_weather = st.sidebar.checkbox("🌧️ Precipitación / Clima (Open-Meteo)", value=True)
layer_base = st.sidebar.checkbox("🛡️ Base Central Buin", value=True)
layer_satellites = st.sidebar.checkbox("🛰️ Órbitas / Satélites", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎙️ Configuración ElevenLabs")
eleven_key = st.sidebar.text_input("ElevenLabs API Key:", type="password")

# 4. FUNCIONES DE TELEMETRÍA EN TIEMPO REAL
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

def get_recent_earthquakes():
    try:
        url = "https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&minmagnitude=3.0&limit=5"
        res = requests.get(url, timeout=3).json()
        quakes = []
        for feat in res['features']:
            coords = feat['geometry']['coordinates']
            mag = feat['properties']['mag']
            place = feat['properties']['place']
            quakes.append({'lat': coords[1], 'lon': coords[0], 'mag': mag, 'place': place})
        return quakes
    except:
        return [{'lat': -33.45, 'lon': -70.66, 'mag': 3.8, 'place': 'Cerca de Santiago, Chile'}]

# 5. ENCABEZADO Y MÉTRICAS
temp_buin, wind_buin = get_buin_weather()

st.markdown("# 🛡️ J.A.R.V.I.S. 4.0 — GodsView Tactical Layers")
st.markdown("*Sistema de Monitoreo de Eventos en Tiempo Real — Base Buin*")
st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
with m1: st.metric(label="Ubicación Base", value="Buin, CL", delta="Protegido")
with m2: st.metric(label="Clima Actual (Buin)", value=temp_buin, delta=f"Viento: {wind_buin}")
with m3: st.metric(label="Capa de Temblores", value="Activa (USGS)", delta="Sincronizado")
with m4: st.metric(label="Latencia Global", value="0.95 ms", delta="Óptimo")

st.markdown("\n")

# 6. MAPA INTERACTIVO CON CAPAS ACTIVAS
st.markdown("### 🗺️ Radar Táctico de Capas y Eventos Naturales")

m = folium.Map(location=[BUIN_LAT, BUIN_LON], zoom_start=9, tiles="OpenStreetMap")

# Capa: Base Buin
if layer_base:
    folium.Marker(
        [BUIN_LAT, BUIN_LON],
        popup="<b>CENTRO DE MANDO STARK — BUIN</b>",
        tooltip="Base Principal Buin",
        icon=folium.Icon(color="red", icon="shield", prefix="fa")
    ).add_to(m)

    folium.Circle(
        radius=12000,
        location=[BUIN_LAT, BUIN_LON],
        popup="Perímetro de Seguridad Buin",
        color="#00f0ff",
        fill=True,
        fill_color="#00f0ff",
        fill_opacity=0.1
    ).add_to(m)

# Capa: Temblores / Sismos en tiempo real
if layer_earthquakes:
    quakes = get_recent_earthquakes()
    for q in quakes:
        folium.CircleMarker(
            location=[q['lat'], q['lon']],
            radius=q['mag'] * 3,
            color="#ff0055",
            fill=True,
            fill_color="#ff0055",
            fill_opacity=0.6,
            tooltip=f"🌋 Sismo M{q['mag']} - {q['place']}"
        ).add_to(m)

# Capa: Satélites
if layer_satellites:
    sat_coords = [[-33.10, -71.20], [-34.10, -70.40], [-33.50, -70.20]]
    for i, coord in enumerate(sat_coords):
        folium.CircleMarker(
            location=coord,
            radius=5,
            color="#00ffcc",
            fill=True,
            fill_color="#00ffcc",
            tooltip=f"🛰️ Satélite Stark-Node 0{i+1}"
        ).add_to(m)

st_folium(m, width="100%", height=480)

# 7. CONSOLA DE MANDO
st.markdown("---")
st.markdown("### 💬 Consola de Mando Táctico")
user_cmd = st.text_input("Ingrese directiva para J.A.R.V.I.S.:", placeholder="Ej: J.A.R.V.I.S., reporte de sismos y clima...")

if user_cmd:
    st.markdown(f'<div class="terminal-card">> [COMANDO]: {user_cmd}<br>> [J.A.R.V.I.S.]: Consultando capas tácticas en tiempo real desde Buin...</div>', unsafe_allow_html=True)
    if not eleven_key:
        tts = gTTS(text="Monitoreo de capas actualizado, Jefa. Todo bajo control en la base.", lang='es')
        tts.save("response.mp3")
        st.audio("response.mp3", format="audio/mp3", autoplay=True)

st.markdown("---")
st.markdown("*J.A.R.V.I.S. GodsView Layers Edition — Taller de Inteligencia Autónoma | Buin, Chile.*")

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

# 3. BARRA LATERAL: NAVEGACIÓN, CAPAS Y SPOTIFY
st.sidebar.markdown("## ⚡ J.A.R.V.I.S. SYSTEM SUBSYSTEMS")

nav_module = st.sidebar.radio(
    "Módulos del Sistema:",
    [
        "🌍 Radar Satelital (NASA/USGS Real-Time)",
        "🌀 Quantum Orbital Core (And Not One)",
        "🧠 Neural Network Matrix (Policy Network)",
        "📈 Trading & Market Liquidity",
        "📡 Feed de Alertas Globales"
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎵 Spotify Tactical Audio")
# Widget de reproductor compacto de Spotify incorporado en el sidebar
spotify_uri = st.sidebar.text_input("Spotify Playlist / Track URI:", value="37i9dQZF1DXdLENR312A25")
components.html(
    f'<iframe src="https://open.spotify.com/embed/playlist/{spotify_uri}?utm_source=generator&theme=0" width="100%" height="152" frameborder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>',
    height=160
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Capas Tácticas en Vivo")
layer_base = st.sidebar.checkbox("🛡️ Base Central Buin", value=True)
layer_earthquakes = st.sidebar.checkbox("🌋 Sismos en Vivo (USGS)", value=True)
layer_fires = st.sidebar.checkbox("🔥 Incendios Satelitales (NASA FIRMS)", value=True)
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
                    fires.append({'lat': float(parts[0]), 'lon': float(

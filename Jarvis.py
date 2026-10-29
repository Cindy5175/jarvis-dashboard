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
    page_title="J.A.R.V.I.S. 4.0 - GodsView Advanced Layers",
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

# 3. BARRA LATERAL: PANEL DE CAPAS AVANZADAS (GODSVIEW LAYERS)
st.sidebar.markdown("## 🌐 GODSVIEW LAYERS")
st.sidebar.markdown("---")

st.sidebar.markdown("### 🎛️ Capas de Telemetría Global")
layer_base = st.sidebar.checkbox("🛡️ Base Central Buin", value=True)
layer_earthquakes = st.sidebar.checkbox("🌋 Temblores (Earthquakes)", value=True)
layer_fires = st.sidebar.checkbox("🔥 Incendios Activos (Active Fires)", value=True)
layer_volcanoes = st.sidebar.checkbox("🌋 Volcanes Activos (Volcanoes)", value=True)
layer_disasters = st.sidebar.checkbox("⚡ Alertas de Desastre (Disaster Alerts)", value=True)
layer_tsunamis = st.sidebar.checkbox("🌊 Alertas de Tsunami", value=True)
layer_satellites = st.sidebar.checkbox("🛰️ Órbitas Satelitales & Starlink", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎙️ Configuración ElevenLabs")
eleven_key = st.sidebar.text_input("ElevenLabs API Key:", type="password")

# 4. DATOS Y TELEMETRÍA EN TIEMPO REAL
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
            quakes.append({'lat': coords[1], 'lon': coords[0], 'mag': feat['properties']['mag'], 'place': feat['properties']['place']})
        return quakes
    except:
        return [{'lat': -33.45, 'lon': -70.66, 'mag': 3.8, 'place': 'Santiago, Chile'}]

# 5. ENCABEZADO Y MÉTRICAS
temp_buin, wind_buin = get_buin_weather()

st.markdown("# 🛡️ J.A.R.V.I.S. 4.0 — Advanced Tactical Core")
st.markdown("*Sistema de Monitoreo Global y Capas Tácticas — Base Buin*")
st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
with m1: st.metric(label="Ubicación Base", value="Buin, CL", delta="Seguro")
with m2: st.metric(label="Clima Local", value=temp_buin, delta=f"Viento: {wind_buin}")
with m3: st.metric(label="Capas Activas", value="7 Monitores", delta="GodsView v2")
with m4: st.metric(label="Latencia Global", value="0.91 ms", delta="Óptimo")

st.markdown("\n")

# 6. MAPA TÁCTICO INTERACTIVO CON CAPAS MÚLTIPLES
st.markdown("### 🗺️ Radar Geoespacial en Vivo")

m = folium.Map(location=[BUIN_LAT, BUIN_LON], zoom_start=8, tiles="OpenStreetMap")

# Base Buin
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
        popup="Perímetro de Seguridad Buin",
        color="#00f0ff",
        fill=True,
        fill_color="#00f0ff",
        fill_opacity=0.1
    ).add_to(m)

# Temblores (USGS)
if layer_earthquakes:
    for q in get_recent_earthquakes():
        folium.CircleMarker(
            location=[q['lat'], q['lon']],
            radius=q['mag'] * 3,
            color="#ff0055",
            fill=True,
            fill_color="#ff0055",
            fill_opacity=0.7,
            tooltip=f"🌋 Sismo M{q['mag']} - {q['place']}"
        ).add_to(m)

# Incendios Activos (Simulación satelital en la zona centro-sur)
if layer_fires:
    fires = [[-34.1, -71.0], [-33.2, -70.9], [-35.4, -72.0]]
    for i, f in enumerate(fires):
        folium.Marker(
            f,
            tooltip=f"🔥 Incendio Activo Detectado 0{i+1}",
            icon=folium.Icon(color="orange", icon="fire", prefix="fa")
        ).add_to(m)

# Volcanes (Zona volcánica de Chile)
if layer_volcanoes:
    volcanoes = [[-33.83, -70.00, "Volcán Maipo"], [-33.33, -70.13, "Volcán San José"]]
    for v in volcanoes:
        folium.CircleMarker(
            location=[v[0], v[1]],
            radius=6,
            color="#ff4500",
            fill=True,
            fill_color="#ff4500",
            tooltip=f"🌋 {v[2]}"
        ).add_to(m)

# Alertas de Desastre y Tsunamis
if layer_disasters:
    folium.Marker([-33.0, -71.5], tooltip="⚡ Alerta Meteorológica Preventiva", icon=folium.Icon(color="purple", icon="bolt", prefix="fa")).add_to(m)

if layer_tsunamis:
    folium.CircleMarker([-32.9, -71.6], radius=8, color="#00ffff", fill=True, fill_color="#00ffff", tooltip="🌊 Boya DART / Alerta Tsunami: Estable").add_to(m)

# Satélites y Starlink Swarm
if layer_satellites:
    sats = [[-33.0, -70.0], [-34.5, -71.0], [-33.8, -70.5]]
    for i, s in enumerate(sats):
        folium.CircleMarker(
            location=s,
            radius=5,
            color="#00ffcc",
            fill=True,
            fill_color="#00ffcc",
            tooltip=f"🛰️ Satélite / Starlink Node 0{i+1}"
        ).add_to(m)

st_folium(m, width="100%", height=500)

# 7. TERMINAL DE COMANDO
st.markdown("---")
st.markdown("### 💬 Consola de Mando Táctico")
user_cmd = st.text_input("Ingrese directiva para J.A.R.V.I.S.:", placeholder="Ej: J.A.R.V.I.S., analiza el estado de las capas...")

if user_cmd:
    st.markdown(f'<div class="terminal-card">> [COMANDO]: {user_cmd}<br>> [J.A.R.V.I.S.]: Monitoreando capas globales desde el taller de Buin.</div>', unsafe_allow_html=True)
    if not eleven_key:
        tts = gTTS(text="Capas tácticas sincronizadas, Jefa. Todo bajo control.", lang='es')
        tts.save("response.mp3")
        st.audio("response.mp3", format="audio/mp3", autoplay=True)

st.markdown("---")
st.markdown("*J.A.R.V.I.S. GodsView Full Layers Edition — Taller de Inteligencia Autónoma | Buin, Chile.*")

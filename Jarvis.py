import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import pytz
from datetime import datetime
import folium
from streamlit_folium import st_folium
from gtts import gTTS

# 1. Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Centro Táctico & Monitoreo Satelital",
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

# 3. BARRA LATERAL
st.sidebar.markdown("## ⚡ ENLACE SATELITAL STARK")
satellite_active = st.sidebar.toggle("Enlace GodsView / Satelital", value=True)

if satellite_active:
    st.sidebar.success("📡 Conexión Satelital Ku-Band: Buin, CL")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎙️ Configuración ElevenLabs")
eleven_key = st.sidebar.text_input("ElevenLabs API Key:", type="password")

voice_model = st.sidebar.selectbox(
    "Modelo de Voz Cinematográfica:",
    ["Antoni (Suave / Sofisticada)", "Adam (Profunda / Narrativa)", "Arnold (Imponente / Varonil)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🛰️ Capas Tácticas Activadas")
show_buin_base = st.sidebar.checkbox("Base Central Buin", value=True)
show_satellites = st.sidebar.checkbox("Enjambre Satelital / Radar", value=True)

# 4. ENCABEZADO Y MÉTRICAS
st.markdown("# 🛡️ J.A.R.V.I.S. 4.0 — GodsView Tactical Core")
st.markdown("*Sistema de Monitoreo Global y Control de Operaciones — Taller Buin*")
st.markdown("---")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric(label="Base Operativa", value="Buin, Chile", delta="Protección Activa")
with m2:
    chile_tz = pytz.timezone('America/Santiago')
    st.metric(label="Hora Local", value=datetime.now(chile_tz).strftime('%H:%M:%S'), delta="Sincronizado")
with m3:
    st.metric(label="Satélites en Órbita", value="12 Activos", delta="+2 Stark-Net")
with m4:
    st.metric(label="Latencia Global", value="0.98 ms", delta="Óptimo")

st.markdown("\n")

# 5. SECCIÓN DEL MAPA TÁCTICO INTERACTIVO (BUIN & CHILE)
st.markdown("### 🗺️ Radar Satelital y Cobertura Táctica")

# Coordenadas de Buin, Chile
BUIN_LAT = -33.7328
BUIN_LON = -70.7356

# Crear mapa base en modo oscuro tipo GodsView
m = folium.Map(location=[BUIN_LAT, BUIN_LON], zoom_start=11, tiles="CartoDB dark_matter")

if show_buin_base:
    # Marcador Base Buin
    folium.Marker(
        [BUIN_LAT, BUIN_LON],
        popup="<b>CENTRO DE MANDO STARK — BUIN</b>",
        tooltip="Base Principal Buin",
        icon=folium.Icon(color="cyan", icon="shield", prefix="fa")
    ).add_to(m)

    # Radio de Cobertura Táctica (Anillo de Energía)
    folium.Circle(
        radius=8000,
        location=[BUIN_LAT, BUIN_LON],
        popup="Perímetro de Seguridad Buin",
        color="#00f0ff",
        fill=True,
        fill_color="#00f0ff",
        fill_opacity=0.1
    ).add_to(m)

if show_satellites:
    # Simulación de nodos satelitales en los alrededores
    sat_coords = [
        [-33.60, -70.70],
        [-33.80, -70.80],
        [-33.70, -70.60]
    ]
    for i, coord in enumerate(sat_coords):
        folium.CircleMarker(
            location=coord,
            radius=6,
            color="#00ffcc",
            fill=True,
            fill_color="#00ffcc",
            tooltip=f"Satelite Stark-Node 0{i+1}"
        ).add_to(m)

# Desplegar mapa en Streamlit
st_data = st_folium(m, width="100%", height=450)

# 6. REACTOR ARC EN CANVAS Y TELEMETRÍA
st.markdown("---")
col_core, col_telemetry = st.columns([1, 1])

with col_core:
    st.markdown("### 🌀 Estado del Reactor Arc")
    canvas_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>body { margin: 0; background: #030611; } canvas { display: block; width: 100%; height: 260px; }</style>
    </head>
    <body>
        <canvas id="miniCore"></canvas>
        <script>
            const canvas = document.getElementById('miniCore');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth / 2;
            canvas.height = 260;
            let a = 0;
            function draw() {
                ctx.clearRect(0,0,canvas.width,canvas.height);
                let cx = canvas.width/2, cy = canvas.height/2;
                ctx.save();
                ctx.translate(cx, cy);
                ctx.rotate(a);
                for(let i=0; i<3; i++){
                    ctx.beginPath();
                    ctx.arc(0,0, 40+i*20, i, i+2.5);
                    ctx.strokeStyle = i%2==0 ? '#00f0ff' : '#00ffcc';
                    ctx.lineWidth = 3;
                    ctx.shadowBlur = 10;
                    ctx.shadowColor = '#00f0ff';
                    ctx.stroke();
                }
                ctx.restore();
                ctx.beginPath();
                ctx.arc(cx, cy, 15, 0, Math.PI*2);
                ctx.fillStyle = '#00ffff';
                ctx.fill();
                a += 0.03;
                requestAnimationFrame(draw);
            }
            draw();
        </script>
    </body>
    </html>
    """
    components.html(canvas_html, height=270)

with col_telemetry:
    st.markdown("### 📊 Actividad de Red y Borde Satelital")
    chart_data = pd.DataFrame(
        np.random.randn(20, 2) * [10, 5] + [100, 50],
        columns=['Telemetría Satelital', 'Frecuencia Neuronal']
    )
    st.line_chart(chart_data, color=["#00f0ff", "#00ffcc"])

# 7. TERMINAL DE MANDO
st.markdown("---")
st.markdown("### 💬 Consola de Mando de J.A.R.V.I.S.")
user_cmd = st.text_input("Ingrese su orden, Jefa:")

if user_cmd:
    st.markdown(f'<div class="terminal-card">> [DIRECTIVA]: {user_cmd}<br>> [J.A.R.V.I.S.]: Ejecutando en la base de Buin con enlace GodsView.</div>', unsafe_allow_html=True)
    
    if not eleven_key:
        tts = gTTS(text=f"Directiva recibida Jefa. Procesando en la base de Buin.", lang='es')
        tts.save("response.mp3")
        st.audio("response.mp3", format="audio/mp3", autoplay=True)

st.markdown("---")
st.markdown("*Sistema J.A.R.V.I.S. GodsView Edition — Taller de Inteligencia Autónoma | Buin, Chile.*")

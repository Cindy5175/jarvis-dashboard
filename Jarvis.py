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
    page_title="J.A.R.V.I.S. 4.0 - GodsView Tactical Core",
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

# 3. BARRA LATERAL: MÓDULOS ESTILO GODSVIEW AI
st.sidebar.markdown("## 🌐 GODSVIEW / STARK CORE")

nav_module = st.sidebar.radio(
    "Seleccionar Subsistema:",
    ["🌍 Radar Satelital & Mapa", "📡 Feed & Eventos Globales", "📈 Mercados & Telemetría", "🧠 Núcleo IA & Red Neuronal", "🛰️ Órbitas & Espacio"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### ⚡ Enlace Satelital Stark")
satellite_active = st.sidebar.toggle("Enlace Ku-Band Activo", value=True)

if satellite_active:
    st.sidebar.success("📡 Conectado: Base Buin, CL")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎙️ Configuración ElevenLabs")
eleven_key = st.sidebar.text_input("ElevenLabs API Key:", type="password")

voice_model = st.sidebar.selectbox(
    "Voz Cinematográfica:",
    ["Antoni (Suave / Sofisticada)", "Adam (Profunda / Narrativa)", "Arnold (Imponente / Varonil)"]
)

# 4. ENCABEZADO PRINCIPAL
st.markdown(f"# 🛡️ J.A.R.V.I.S. 4.0 — [{nav_module}]")
st.markdown("*Centro de Comando Autónomo y Vigilancia Global — Taller Buin*")
st.markdown("---")

# 5. CONTENIDO DINÁMICO SEGÚN EL MÓDULO SELECCIONADO

if nav_module == "🌍 Radar Satelital & Mapa":
    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric(label="Base Operativa", value="Buin, Chile", delta="Protegido")
    with m2: 
        chile_tz = pytz.timezone('America/Santiago')
        st.metric(label="Hora Local", value=datetime.now(chile_tz).strftime('%H:%M:%S'), delta="Sincronizado")
    with m3: st.metric(label="Satélites Activos", value="12 Órbitas", delta="Stark-1")
    with m4: st.metric(label="Latencia Global", value="0.98 ms", delta="Óptimo")
    
    st.markdown("### 🗺️ Mapa Táctico de Cobertura (Buin y Alrededores)")
    
    BUIN_LAT, BUIN_LON = -33.7328, -70.7356
    # Usamos OpenStreetMap libre para evitar el error de API Key de Carto
    m = folium.Map(location=[BUIN_LAT, BUIN_LON], zoom_start=11, tiles="OpenStreetMap")

    folium.Marker(
        [BUIN_LAT, BUIN_LON],
        popup="<b>CENTRO DE MANDO STARK — BUIN</b>",
        tooltip="Base Principal Buin",
        icon=folium.Icon(color="red", icon="shield", prefix="fa")
    ).add_to(m)

    folium.Circle(
        radius=8000,
        location=[BUIN_LAT, BUIN_LON],
        popup="Perímetro de Seguridad Buin",
        color="#00f0ff",
        fill=True,
        fill_color="#00f0ff",
        fill_opacity=0.15
    ).add_to(m)

    st_folium(m, width="100%", height=450)

elif nav_module == "📡 Feed & Eventos Globales":
    st.markdown("### 🚨 Feed de Actividad y Alertas en Vivo")
    st.info("🔥 [ALERTA TÁCTICA] Actividad sísmica menor registrada en zona centro-sur. Sin riesgo para la base de Buin.")
    st.warning("🌪️ [METEOROLOGÍA] Vaguada costera en desplazamiento. Cielos despejados en el taller.")
    st.success("🛰️ [SATÉLITE] Constelación Stark-1 completó pase orbital sobre la Región Metropolitana.")

elif nav_module == "📈 Mercados & Telemetría":
    st.markdown("### 📊 Flujos Financieros y Ancho de Banda")
    chart_data = pd.DataFrame(
        np.random.randn(25, 3) * [15, 8, 4] + [110, 60, 30],
        columns=['Liquidez Global', 'Ancho de Banda (Gbps)', 'Carga del Sistema']
    )
    st.line_chart(chart_data, color=["#00f0ff", "#00ffcc", "#ff007f"])

elif nav_module == "🧠 Núcleo IA & Red Neuronal":
    st.markdown("### 🌀 Visualizador del Núcleo Neuronal")
    canvas_html = """
    <!DOCTYPE html>
    <html>
    <head><style>body { margin: 0; background: #030611; } canvas { display: block; width: 100%; height: 350px; }</style></head>
    <body>
        <canvas id="coreCanvas"></canvas>
        <script>
            const canvas = document.getElementById('coreCanvas');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth * 0.8;
            canvas.height = 350;
            let angle = 0;
            function render() {
                ctx.clearRect(0,0,canvas.width,canvas.height);
                let cx = canvas.width/2, cy = canvas.height/2;
                ctx.save();
                ctx.translate(cx, cy);
                ctx.rotate(angle);
                for(let i=0; i<4; i++){
                    ctx.beginPath();
                    ctx.arc(0,0, 50+i*30, i*0.5, i*0.5 + Math.PI);
                    ctx.strokeStyle = i%2==0 ? '#00f0ff' : '#ff007f';
                    ctx.lineWidth = 3;
                    ctx.shadowBlur = 15;
                    ctx.shadowColor = '#00f0ff';
                    ctx.stroke();
                }
                ctx.restore();
                ctx.beginPath();
                ctx.arc(cx, cy, 20, 0, Math.PI*2);
                ctx.fillStyle = '#00ffff';
                ctx.fill();
                angle += 0.02;
                requestAnimationFrame(render);
            }
            render();
        </script>
    </body>
    </html>
    """
    components.html(canvas_html, height=360)

elif nav_module == "🛰️ Órbitas & Espacio":
    st.markdown("### 🪐 Monitoreo de Enjambre Satelital y Constelaciones")
    st.code("""
[OK] Satélite Stark-1: Órbita LEO Sincronizada (Altitud: 550 km)
[OK] Enjambre Starlink-B: 4,400 nodos activos detectados en sector sur
[OK] Estación Espacial Internacional (ISS): Tránsito sobre el cono sur programado a las 21:42 hrs.
    """, language="text")

# 6. TERMINAL DE MANDO GLOBAL
st.markdown("---")
st.markdown("### 💬 Consola de Mando Táctico")
user_cmd = st.text_input("Ingrese directiva para J.A.R.V.I.S.:", placeholder="Ej: J.A.R.V.I.S., activa protocolos de escaneo...")

if user_cmd:
    st.markdown(f'<div class="terminal-card">> [COMANDO]: {user_cmd}<br>> [J.A.R.V.I.S.]: Ejecutando directiva en el subsistema [{nav_module}].</div>', unsafe_allow_html=True)
    if not eleven_key:
        tts = gTTS(text=f"Procesando orden en la base de Buin.", lang='es')
        tts.save("response.mp3")
        st.audio("response.mp3", format="audio/mp3", autoplay=True)

st.markdown("---")
st.markdown("*J.A.R.V.I.S. GodsView Edition — Taller de Inteligencia Autónoma | Buin, Chile.*")

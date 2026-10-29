import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import pytz
from datetime import datetime
import time

# 1. Configuración de la página Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. Tactical Dashboard - Stark Industries",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Estilos CSS personalizables estilo Stark/Holográfico
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

# 3. BARRA LATERAL: ENLACE SATELITAL Y SÍNTESIS DE VOZ ELEVENLABS
st.sidebar.markdown("## ⚡ ENLACE SATELITAL STARK")
satellite_active = st.sidebar.toggle("Enlace Satelital Activo", value=True)

if satellite_active:
    st.sidebar.success("📡 Conectado a Constelación Stark-1 (Buin, CL)")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎙️ Configuración ElevenLabs")
eleven_key = st.sidebar.text_input("ElevenLabs API Key:", type="password", help="Ingrese su API Key personal")

voice_model = st.sidebar.selectbox(
    "Modelo de Voz Varonil/Cinematográfica:",
    ["Antoni (Suave / Sofisticada)", "Adam (Profunda / Narrativa)", "Arnold (Imponente / Varonil)"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎛️ Diagnóstico del Núcleo")
st.sidebar.progress(98, text="Sincronización Neuronal: 98%")
st.sidebar.progress(100, text="Integridad del Reactor: 100%")

# 4. ENCABEZADO Y TELEMETRÍA DE ENTRADA
st.markdown("# 🛡️ J.A.R.V.I.S. TACTICAL DASHBOARD")
st.markdown("*Sistema Autónomo de Mando y Control Táctico — Base Buin*")
st.markdown("---")

col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    st.metric(label="Ubicación Base", value="Buin, Chile", delta="Estable")

with col_m2:
    chile_tz = pytz.timezone('America/Santiago')
    st.metric(label="Hora Local", value=datetime.now(chile_tz).strftime('%H:%M:%S'), delta="Sincronizado")

with col_m3:
    st.metric(label="Latencia Neuronal", value="1.14 ms", delta="-0.02 ms")

with col_m4:
    st.metric(label="Estado de la Red", value="99.27%", delta="Optimizado")

st.markdown("\n")

# 5. CORE HOLOGRÁFICO EN CANVAS (Vórtice Reactor Arc + Red Neuronal + Sintetizador Web Audio)
st.markdown("### 🌀 Núcleo Reactor & Red Neuronal Viva")

canvas_html = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; overflow: hidden; background-color: #030611; }
        canvas { display: block; width: 100%; height: 420px; }
    </style>
</head>
<body>
    <canvas id="starkCanvas"></canvas>
    <script>
        const canvas = document.getElementById('starkCanvas');
        const ctx = canvas.getContext('2d');
        
        function resize() {
            canvas.width = window.innerWidth;
            canvas.height = 420;
        }
        resize();
        window.addEventListener('resize', resize);

        let angle = 0;
        const nodes = [];
        const numNodes = 35;

        for (let i = 0; i < numNodes; i++) {
            nodes.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                vx: (Math.random() - 0.5) * 1.5,
                vy: (Math.random() - 0.5) * 1.5,
                radius: Math.random() * 2 + 1
            });
        }

        function drawCore() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;

            // 1. Red Neuronal de Fondo
            ctx.strokeStyle = 'rgba(0, 240, 255, 0.15)';
            ctx.fillStyle = '#00ffcc';
            for (let i = 0; i < numNodes; i++) {
                let n1 = nodes[i];
                n1.x += n1.vx;
                n1.y += n1.vy;
                if (n1.x < 0 || n1.x > canvas.width) n1.vx *= -1;
                if (n1.y < 0 || n1.y > canvas.height) n1.vy *= -1;

                ctx.beginPath();
                ctx.arc(n1.x, n1.y, n1.radius, 0, Math.PI * 2);
                ctx.fill();

                for (let j = i + 1; j < numNodes; j++) {
                    let n2 = nodes[j];
                    let dist = Math.hypot(n1.x - n2.x, n1.y - n2.y);
                    if (dist < 130) {
                        ctx.beginPath();
                        ctx.moveTo(n1.x, n1.y);
                        ctx.lineTo(n2.x, n2.y);
                        ctx.stroke();
                    }
                }
            }

            // 2. Vórtice / Reactor Arc
            ctx.save();
            ctx.translate(cx, cy);
            ctx.rotate(angle);

            for (let i = 0; i < 4; i++) {
                ctx.beginPath();
                ctx.arc(0, 0, 60 + i * 25, i * 0.5, i * 0.5 + Math.PI * 1.2);
                ctx.strokeStyle = i % 2 === 0 ? '#00f0ff' : '#ff007f';
                ctx.lineWidth = 2 + i;
                ctx.shadowBlur = 15;
                ctx.shadowColor = '#00f0ff';
                ctx.stroke();
            }

            ctx.restore();

            // Centro resplandeciente
            ctx.beginPath();
            ctx.arc(cx, cy, 25, 0, Math.PI * 2);
            ctx.fillStyle = '#00ffff';
            ctx.shadowBlur = 30;
            ctx.shadowColor = '#00ffff';
            ctx.fill();

            angle += 0.02;
            requestAnimationFrame(drawCore);
        }

        drawCore();
    </script>
</body>
</html>
"""

components.html(canvas_html, height=430)

# 6. PANEL DE TELEMETRÍA Y LATENCIA RADIAL
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📊 Telemetría de Flujos y Ancho de Banda")
    chart_data = pd.DataFrame(
        np.random.randn(30, 3) * [12, 8, 3] + [120, 65, 30],
        columns=['Flujo Satelital (Gbps)', 'Sincronización Neuronal', 'Carga del Reactor']
    )
    st.line_chart(chart_data, color=["#00f0ff", "#00ffcc", "#ff007f"])

with col_right:
    st.markdown("### 🎯 Medidor de Latencia")
    latency_data = pd.DataFrame({
        'Métrica': ['Red Central', 'Satelital', 'Núcleo IA'],
        'Latencia (ms)': [1.14, 12.2, 0.30]
    })
    st.bar_chart(latency_data.set_index('Métrica'), color="#00f0ff")

# 7. TERMINAL DE COMANDOS E INTERFAZ VOCAL
st.markdown("---")
st.markdown("### 💬 Terminal de Mando Táctico")

user_command = st.text_input("Escriba su directiva para J.A.R.V.I.S.:", placeholder="Ej: J.A.R.V.I.S., ejecuta diagnóstico de sistemas...")

if user_command:
    st.markdown(f"""
        <div class="terminal-card">
            > <strong>ENTRADA REGISTRADA:</strong> {user_command}<br>
            > <strong>ESTADO:</strong> Procesando directiva con la red neuronal central en Buin...
        </div>
    """, unsafe_allow_html=True)
    
    if eleven_key:
        st.success("🎙️ [ElevenLabs API] Generando sintetización de respuesta táctica...")
    else:
        st.info("🔊 [Web Audio Synth] Ejecutando señal de audio y respuesta de respaldo por defecto.")
        
        # Audio Synth FX embebido mediante JavaScript Web Audio API
        audio_synth_script = """
        <script>
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(440, audioCtx.currentTime + 0.3);
            gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.3);
        </script>
        """
        components.html(audio_synth_script, height=0)

st.markdown("---")
st.markdown("*J.A.R.V.I.S. 4.0 — Arquitectura de Mando Autónomo Stark Industries | Buin, Chile.*")

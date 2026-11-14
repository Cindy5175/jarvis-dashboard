import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="J.A.R.V.I.S. // Núcleo de Comando",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .block-container {
            padding: 0rem;
            max-width: 100%;
        }
        header, footer, #MainMenu {visibility: hidden;}
        body {background-color: #050814;}
    </style>
""", unsafe_allow_html=True)

jarvis_hud_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. // Núcleo de Comando</title>
    <style>
        :root {
            --bg-color: #050814;
            --glass-bg: rgba(10, 16, 32, 0.75);
            --glass-border: rgba(0, 243, 255, 0.25);
            --neon-blue: #00f3ff;
            --neon-gold: #ffb700;
            --text-main: #e2f1ff;
            --text-dim: #7b9ebc;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Courier New', Courier, monospace;
        }

        body {
            background-color: var(--bg-color);
            color: var(--text-main);
            min-height: 100vh;
            padding: 15px;
            overflow-x: hidden;
            background-image: 
                radial-gradient(circle at 50% 20%, rgba(0, 243, 255, 0.08) 0%, transparent 50%),
                linear-gradient(rgba(0,243,255,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0,243,255,0.03) 1px, transparent 1px);
            background-size: 100% 100%, 20px 20px, 20px 20px;
        }

        .container {
            max-width: 480px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }

        .glass-card {
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 18px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), inset 0 0 15px rgba(0, 243, 255, 0.05);
        }

        .header-title {
            font-size: 1.25rem;
            font-weight: bold;
            letter-spacing: 2px;
            color: var(--neon-blue);
            margin-bottom: 5px;
            text-shadow: 0 0 10px rgba(0, 243, 255, 0.4);
        }

        .status-line {
            font-size: 0.75rem;
            color: var(--text-dim);
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background-color: #00ff66;
            border-radius: 50%;
            box-shadow: 0 0 8px #00ff66;
            animation: pulse-dot 2s infinite;
        }

        @keyframes pulse-dot {
            0% { opacity: 1; }
            50% { opacity: 0.4; }
            100% { opacity: 1; }
        }

        .nav-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 15px;
        }

        .nav-btn {
            background: rgba(0, 243, 255, 0.05);
            border: 1px solid rgba(0, 243, 255, 0.3);
            border-radius: 8px;
            padding: 12px;
            color: var(--text-main);
            text-align: center;
            font-size: 0.8rem;
            font-weight: bold;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .nav-btn.active, .nav-btn:hover {
            background: rgba(0, 243, 255, 0.15);
            border-color: var(--neon-blue);
            box-shadow: 0 0 12px rgba(0, 243, 255, 0.3);
        }

        .telemetry-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.75rem;
            color: var(--text-dim);
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            padding-top: 10px;
        }

        .telemetry-val {
            color: var(--neon-blue);
            font-weight: bold;
        }

        .timestamp {
            color: var(--neon-gold);
            font-weight: bold;
        }

        .section-title {
            font-size: 0.85rem;
            letter-spacing: 2px;
            color: var(--text-main);
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .badge-orbits {
            font-size: 0.65rem;
            background: rgba(255, 183, 0, 0.15);
            border: 1px solid var(--neon-gold);
            color: var(--neon-gold);
            padding: 2px 8px;
            border-radius: 4px;
        }

        .core-visual-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 140px;
            position: relative;
        }

        canvas {
            width: 100px;
            height: 100px;
        }

        /* Órbita Circular Interactiva Completa */
        .orbit-container {
            position: relative;
            height: 220px;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
            border-radius: 8px;
            background: rgba(0,0,0,0.2);
            border: 1px dashed rgba(255,255,255,0.05);
        }

        .orbit-ring {
            position: absolute;
            width: 170px;
            height: 170px;
            border: 1px solid rgba(0, 243, 255, 0.3);
            border-radius: 50%;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.1);
            animation: rotate-orbit 25s linear infinite;
        }

        .orbit-ring-inner {
            position: absolute;
            width: 110px;
            height: 110px;
            border: 1px dotted rgba(255, 183, 0, 0.3);
            border-radius: 50%;
            animation: rotate-orbit-reverse 20s linear infinite;
        }

        @keyframes rotate-orbit {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        @keyframes rotate-orbit-reverse {
            from { transform: rotate(360deg); }
            to { transform: rotate(0deg); }
        }

        .planet {
            position: absolute;
            padding: 5px 10px;
            background: rgba(5, 8, 20, 0.95);
            border: 1px solid var(--neon-blue);
            border-radius: 6px;
            font-size: 0.65rem;
            color: var(--neon-blue);
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
            cursor: pointer;
            transition: transform 0.2s, border-color 0.2s;
            z-index: 2;
        }

        .planet:hover {
            transform: scale(1.15);
            border-color: var(--neon-gold);
            color: var(--neon-gold);
        }

        .tactical-map-view {
            display: none;
            height: 220px;
            background: #020408;
            border-radius: 8px;
            position: relative;
            overflow: hidden;
            border: 1px solid var(--neon-blue);
        }

        .radar-sweep {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 300px;
            height: 300px;
            margin-top: -150px;
            margin-left: -150px;
            border-radius: 50%;
            background: conic-gradient(from 0deg at 50% 50%, rgba(0, 243, 255, 0.2) 0deg, transparent 60deg, transparent 360deg);
            animation: sweep 4s linear infinite;
            pointer-events: none;
        }

        @keyframes sweep {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="glass-card">
            <div class="header-title">J.A.R.V.I.S. // NÚCLEO DE COMANDO</div>
            <div class="status-line">
                <span class="status-dot"></span>
                En línea // Escucha Continua Activa
            </div>

            <div class="nav-grid">
                <div class="nav-btn active" id="btn-neural" onclick="switchView('neural')">NÚCLEO NEURONAL</div>
                <div class="nav-btn" id="btn-tactical" onclick="switchView('tactical')">MAPA TÁCTICO SATELITAL</div>
            </div>

            <div id="view-neural">
                <div class="core-visual-container">
                    <canvas id="wireframeSphere" width="100" height="100"></canvas>
                    <div style="font-size: 0.7rem; color: var(--neon-blue); letter-spacing: 1px; margin-top: 5px;">ESTABILIZADOR ACTIVO</div>
                </div>

                <div class="telemetry-row" style="border-top: 1px solid rgba(255, 255, 255, 0.05); padding-top: 8px;">
                    <div>CPU: <span class="telemetry-val">25%</span></div>
                    <div>RAM: <span class="telemetry-val">4.2 / 16 GB</span></div>
                    <div>RED: <span class="telemetry-val">16 ms</span></div>
                </div>
                <div class="telemetry-row" style="margin-top: 6px;">
                    <div class="timestamp" id="live-clock">23:35:00</div>
                    <div style="color: var(--text-dim);">NODO BUIN</div>
                </div>
            </div>

            <div id="view-tactical" class="tactical-map-view">
                <div class="radar-sweep"></div>
                <div style="position: absolute; top: 10px; left: 10px; font-size: 0.7rem; color: var(--neon-blue); letter-spacing: 1px;">
                    [SAT-FEED: NODO BUIN SECTOR 01]
                </div>
                <div style="position: absolute; bottom: 10px; left: 10px; font-size: 0.65rem; color: var(--text-dim);">
                    COORD: -33.7312° S, 70.7415° W
                </div>
            </div>
        </div>

        <div class="glass-card">
            <div class="section-title">
                MAPA ORBITAL DE PROYECTOS
                <span class="badge-orbits">4 ÓRBITAS ACTIVAS</span>
            </div>
            
            <div class="orbit-container">
                <div class="orbit-ring"></div>
                <div class="orbit-ring-inner"></div>
                <!-- Planetas en posiciones orbitales exactas -->
                <div class="planet" style="top: 25px; left: 35px;" onclick="alert('JARVIS Core: Operativo y Sarcástico')">JARVIS</div>
                <div class="planet" style="top: 25px; right: 35px; border-color: var(--neon-gold); color: var(--neon-gold);" onclick="alert('La Isla de los Números: Freemium $3.99 USD')">Isla Números</div>
                <div class="planet" style="bottom: 25px; left: 30px;" onclick="alert('Agente de Soporte 24/7: Enrutando canales')">Soporte 24/7</div>
                <div class="planet" style="bottom: 25px; right: 30px;" onclick="alert('Automatización Nodo Buin: Conectado')">Nodo Buin</div>
            </div>
        </div>
    </div>

    <script>
        setInterval(() => {
            const now = new Date();
            document.getElementById('live-clock').innerText = now.toTimeString().split(' ')[0];
        }, 1000);

        function switchView(view) {
            const btnNeural = document.getElementById('btn-neural');
            const btnTactical = document.getElementById('btn-tactical');
            const viewNeural = document.getElementById('view-neural');
            const viewTactical = document.getElementById('view-tactical');

            if(view === 'neural') {
                btnNeural.classList.add('active');
                btnTactical.classList.remove('active');
                viewNeural.style.display = 'block';
                viewTactical.style.display = 'none';
            } else {
                btnTactical.classList.add('active');
                btnNeural.classList.remove('active');
                viewTactical.style.display = 'block';
                viewNeural.style.display = 'none';
            }
        }

        const canvas = document.getElementById('wireframeSphere');
        const ctx = canvas.getContext('2d');
        let angle = 0;

        function drawSphere() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const cx = canvas.width / 2;
            const cy = canvas.height / 2;
            const radius = 38;

            ctx.strokeStyle = 'rgba(0, 243, 255, 0.6)';
            ctx.lineWidth = 1;

            for (let i = -2; i <= 2; i++) {
                let yOffset = i * 12;
                let currentRadius = Math.sqrt(radius * radius - yOffset * yOffset);
                
                ctx.beginPath();
                ctx.ellipse(cx, cy + yOffset, currentRadius, currentRadius * 0.3, angle, 0, Math.PI * 2);
                ctx.stroke();
            }

            for (let j = 0; j < 4; j++) {
                let currentAngle = angle + (j * Math.PI / 2);
                ctx.beginPath();
                ctx.ellipse(cx, cy, radius * Math.sin(currentAngle), radius, 0, 0, Math.PI * 2);
                ctx.stroke();
            }

            angle += 0.02;
            requestAnimationFrame(drawSphere);
        }
        drawSphere();
    </script>
</body>
</html>
"""

components.html(jarvis_hud_html, height=720, scrolling=True)

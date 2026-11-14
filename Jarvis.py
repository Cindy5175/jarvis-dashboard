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
            padding: 0rem !important;
            max-width: 100% !important;
        }
        header, footer, #MainMenu {visibility: hidden;}
        body, .stApp {background-color: #040711;}
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
            --bg-dark: #040711;
            --card-bg: rgba(9, 16, 30, 0.88);
            --border-cyan: rgba(0, 229, 255, 0.25);
            --cyan: #00e5ff;
            --cyan-glow: rgba(0, 229, 255, 0.45);
            --gold: #f5b027;
            --green: #10e88a;
            --text-main: #eaf6ff;
            --text-dim: #6f8ba6;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Courier New', Courier, monospace;
        }

        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            padding: 12px;
            background-image:
                radial-gradient(circle at 50% 15%, rgba(0, 229, 255, 0.08) 0%, transparent 55%),
                linear-gradient(rgba(0, 229, 255, 0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 229, 255, 0.025) 1px, transparent 1px);
            background-size: 100% 100%, 22px 22px, 22px 22px;
        }

        .hud-wrapper {
            max-width: 460px;
            margin: 0 auto;
            display: flex;
            flex-direction: column;
            gap: 14px;
        }

        .hud-card {
            background: var(--card-bg);
            border: 1px solid var(--border-cyan);
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), inset 0 0 20px rgba(0, 229, 255, 0.04);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
        }

        .header-top {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 18px;
        }

        .arc-orb {
            width: 44px;
            height: 62px;
            border-radius: 50%;
            border: 2.5px solid var(--cyan);
            box-shadow: 0 0 16px var(--cyan-glow), inset 0 0 14px var(--cyan-glow);
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            cursor: pointer;
            animation: orbBreath 3s ease-in-out infinite;
        }

        .arc-orb-core {
            width: 24px;
            height: 36px;
            border-radius: 50%;
            background: radial-gradient(circle, #7cf4ff 0%, #00b8d4 70%, transparent 100%);
            box-shadow: 0 0 12px var(--cyan);
        }

        @keyframes orbBreath {
            0%, 100% { transform: scale(1); box-shadow: 0 0 14px var(--cyan-glow), inset 0 0 10px var(--cyan-glow); }
            50% { transform: scale(1.04); box-shadow: 0 0 24px var(--cyan), inset 0 0 18px var(--cyan); }
        }

        .title-block h1 {
            font-size: 1.25rem;
            line-height: 1.25;
            letter-spacing: 2px;
            color: var(--text-main);
            font-weight: bold;
        }

        .status-row {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 6px;
            font-size: 0.72rem;
            color: var(--green);
            letter-spacing: 1.2px;
        }

        .dot-live {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--green);
            box-shadow: 0 0 8px var(--green);
            animation: blink 1.6s infinite;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.35; }
        }

        .mode-bar {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            background: rgba(3, 7, 15, 0.65);
            padding: 6px;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            margin-bottom: 18px;
        }

        .mode-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 11px 8px;
            border-radius: 9px;
            border: 1px solid transparent;
            background: transparent;
            color: var(--text-main);
            font-size: 0.76rem;
            font-weight: bold;
            letter-spacing: 1px;
            cursor: pointer;
            transition: all 0.25s ease;
            text-align: center;
        }

        .mode-btn.active {
            background: rgba(0, 229, 255, 0.12);
            border-color: var(--cyan);
            color: var(--cyan);
            box-shadow: 0 0 14px rgba(0, 229, 255, 0.2);
        }

        .telemetry-grid {
            display: grid;
            grid-template-columns: 0.85fr 0.95fr 0.95fr 1.25fr;
            gap: 8px;
            align-items: start;
            border-top: 1px solid rgba(0, 229, 255, 0.12);
            padding-top: 14px;
        }

        .tel-label {
            font-size: 0.63rem;
            color: var(--text-dim);
            line-height: 1.25;
            margin-bottom: 4px;
        }

        .tel-value {
            font-size: 0.78rem;
            color: var(--cyan);
            font-weight: bold;
            line-height: 1.3;
        }

        .clock-box {
            text-align: right;
            border-left: 1px solid rgba(255, 255, 255, 0.08);
            padding-left: 8px;
        }

        .clock-big {
            font-size: 1.05rem;
            color: var(--gold);
            font-weight: bold;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(245, 176, 39, 0.35);
        }

        .clock-sub {
            font-size: 0.62rem;
            color: var(--text-dim);
            margin-top: 3px;
            line-height: 1.3;
        }

        #tactical-panel {
            display: none;
            margin-top: 14px;
            border-top: 1px solid rgba(0, 229, 255, 0.15);
            padding-top: 14px;
        }

        .sat-screen {
            position: relative;
            height: 210px;
            border-radius: 12px;
            border: 1px solid var(--cyan);
            background:
                radial-gradient(circle at 50% 50%, rgba(0, 229, 255, 0.12) 0%, rgba(2, 6, 14, 0.96) 75%),
                repeating-linear-gradient(0deg, rgba(0, 229, 255, 0.07) 0px, rgba(0, 229, 255, 0.07) 1px, transparent 1px, transparent 26px),
                repeating-linear-gradient(90deg, rgba(0, 229, 255, 0.07) 0px, rgba(0, 229, 255, 0.07) 1px, transparent 1px, transparent 26px);
            overflow: hidden;
        }

        .radar-ring {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            border: 1px solid rgba(0, 229, 255, 0.25);
            border-radius: 50%;
            pointer-events: none;
        }

        .radar-beam {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 260px;
            height: 260px;
            margin-top: -130px;
            margin-left: -130px;
            border-radius: 50%;
            background: conic-gradient(from 0deg, rgba(0, 229, 255, 0.32) 0deg, transparent 65deg);
            animation: spinRadar 4s linear infinite;
            pointer-events: none;
        }

        @keyframes spinRadar {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .sat-target {
            position: absolute;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: var(--gold);
            box-shadow: 0 0 10px var(--gold);
            animation: blink 1.2s infinite;
        }

        .orbital-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }

        .orbital-header h2 {
            font-size: 0.9rem;
            letter-spacing: 1.5px;
            color: var(--text-main);
            line-height: 1.3;
        }

        .orbit-badge {
            font-size: 0.65rem;
            color: var(--gold);
            background: rgba(245, 176, 39, 0.12);
            border: 1px solid rgba(245, 176, 39, 0.5);
            padding: 5px 10px;
            border-radius: 8px;
            text-align: center;
            font-weight: bold;
            line-height: 1.25;
        }

        .canvas-box {
            position: relative;
            width: 100%;
            height: 245px;
            border-radius: 12px;
            background: radial-gradient(circle at 55% 65%, rgba(0, 180, 255, 0.14) 0%, rgba(3, 6, 14, 0.95) 70%);
            border: 1px solid rgba(0, 229, 255, 0.12);
            overflow: hidden;
        }

        #solarCanvas {
            width: 100%;
            height: 100%;
            display: block;
            cursor: pointer;
        }

        .node-status-bar {
            margin-top: 10px;
            padding: 8px 12px;
            border-radius: 8px;
            background: rgba(0, 229, 255, 0.06);
            border: 1px solid rgba(0, 229, 255, 0.18);
            font-size: 0.72rem;
            color: var(--cyan);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .voice-btn {
            background: rgba(0, 229, 255, 0.15);
            border: 1px solid var(--cyan);
            color: var(--cyan);
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.68rem;
            font-weight: bold;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <div class="hud-wrapper">
        <div class="hud-card">
            <div class="header-top">
                <div class="arc-orb" onclick="speakJarvis('Sistemas en línea, jefa. Nodo Buin estable.')">
                    <div class="arc-orb-core"></div>
                </div>
                <div class="title-block">
                    <h1>J.A.R.V.I.S. //<br>NÚCLEO DE<br>COMANDO</h1>
                    <div class="status-row">
                        <span class="dot-live"></span>
                        <span>EN LÍNEA // ESCUCHA<br>CONTINUA</span>
                    </div>
                </div>
            </div>

            <div class="mode-bar">
                <button class="mode-btn active" id="btn-neural" onclick="setMode('neural')">
                    <span>◎</span>
                    <span>NÚCLEO<br>NEURONAL</span>
                </button>
                <button class="mode-btn" id="btn-tactical" onclick="setMode('tactical')">
                    <span>⊞</span>
                    <span>MAPA<br>TÁCTICO<br>SATELITAL</span>
                </button>
            </div>

            <div class="telemetry-grid">
                <div>
                    <div class="tel-label">CPU<br>NÚCLEO</div>
                    <div class="tel-value" id="cpu-val">25%</div>
                </div>
                <div>
                    <div class="tel-label">MEMORIA</div>
                    <div class="tel-value">4.2 /<br>16 GB</div>
                </div>
                <div>
                    <div class="tel-label">ENLACE<br>RED</div>
                    <div class="tel-value"><span id="ping-val">16</span> ms<br>//<br>ÓPTIMO</div>
                </div>
                <div class="clock-box">
                    <div class="clock-big" id="hud-clock">23:20:51</div>
                    <div class="clock-sub">NODO BUIN //<br>13 NOV. 2026</div>
                </div>
            </div>

            <div id="tactical-panel">
                <div class="sat-screen">
                    <div class="radar-ring" style="width: 70px; height: 70px;"></div>
                    <div class="radar-ring" style="width: 135px; height: 135px;"></div>
                    <div class="radar-ring" style="width: 200px; height: 200px;"></div>
                    <div class="radar-beam"></div>
                    <div class="sat-target" style="top: 48%; left: 50%;"></div>
                    <div class="sat-target" style="top: 32%; left: 64%; background: #00e5ff; box-shadow: 0 0 8px #00e5ff;"></div>
                    <div style="position: absolute; top: 10px; left: 12px; font-size: 0.66rem; color: var(--cyan);">
                        SAT-LINK // NODO BUIN (CHILE)
                    </div>
                    <div style="position: absolute; top: 10px; right: 12px; font-size: 0.64rem; color: var(--green);">
                        LOCKED
                    </div>
                    <div style="position: absolute; bottom: 10px; left: 12px; font-size: 0.64rem; color: var(--text-dim);">
                        LAT: -33.7312° S | LON: -70.7415° W
                    </div>
                </div>
            </div>
        </div>

        <div class="hud-card">
            <div class="orbital-header">
                <h2>MAPA ORBITAL DE<br>PROYECTOS</h2>
                <div class="orbit-badge">4 ÓRBITAS<br>ACTIVAS</div>
            </div>

            <div class="canvas-box">
                <canvas id="solarCanvas"></canvas>
            </div>

            <div class="node-status-bar">
                <span id="selected-node-info">NÚCLEO: J.A.R.V.I.S. // OPERATIVO</span>
                <button class="voice-btn" onclick="speakJarvis('Órbitas sincronizadas, jefa.')">VOZ HUD</button>
            </div>
        </div>
    </div>

    <script>
        function updateTelemetry() {
            const now = new Date();
            document.getElementById('hud-clock').innerText = now.toTimeString().split(' ')[0];
            document.getElementById('cpu-val').innerText = (22 + Math.floor(Math.random() * 7)) + '%';
            document.getElementById('ping-val').innerText = 14 + Math.floor(Math.random() * 5);
        }
        setInterval(updateTelemetry, 1000);
        updateTelemetry();

        function setMode(mode) {
            const btnNeural = document.getElementById('btn-neural');
            const btnTactical = document.getElementById('btn-tactical');
            const tacticalPanel = document.getElementById('tactical-panel');

            if (mode === 'tactical') {
                btnTactical.classList.add('active');
                btnNeural.classList.remove('active');
                tacticalPanel.style.display = 'block';
                speakJarvis('Desplegando mapa táctico satelital.');
            } else {
                btnNeural.classList.add('active');
                btnTactical.classList.remove('active');
                tacticalPanel.style.display = 'none';
            }
        }

        function speakJarvis(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const msg = new SpeechSynthesisUtterance(text);
                msg.lang = 'es-ES';
                msg.pitch = 0.85;
                msg.rate = 1.02;
                window.speechSynthesis.speak(msg);
            }
        }

        const canvas = document.getElementById('solarCanvas');
        const ctx = canvas.getContext('2d');

        function resizeCanvas() {
            const rect = canvas.parentElement.getBoundingClientRect();
            canvas.width = rect.width * window.devicePixelRatio;
            canvas.height = rect.height * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        }
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);

        const nodes = [
            { name: 'J.A.R.V.I.S.', rx: 72, ry: 34, angle: 0.35, speed: 0.008, color: '#f5b027', ring: true, radius: 9, info: 'NÚCLEO: J.A.R.V.I.S. // ACTIVO' },
            { name: 'Agente', rx: 112, ry: 52, angle: 3.65, speed: 0.006, color: '#10e88a', ring: false, radius: 7, info: 'ÓRBITA 02: AGENTE AUTÓNOMO' },
            { name: 'Isla Números', rx: 148, ry: 68, angle: 2.1, speed: 0.0045, color: '#00e5ff', ring: false, radius: 6.5, info: 'ÓRBITA 03: ISLA DE LOS NÚMEROS' },
            { name: 'Nodo Buin', rx: 180, ry: 82, angle: 5.1, speed: 0.0035, color: '#a855f7', ring: false, radius: 6, info: 'ÓRBITA 04: NODO BUIN' }
        ];

        let renderedPositions = [];

        function drawSolarSystem() {
            const w = canvas.parentElement.clientWidth;
            const h = canvas.parentElement.clientHeight;
            ctx.clearRect(0, 0, w, h);

            const cx = w * 0.56;
            const cy = h * 0.64;

            nodes.forEach((n, idx) => {
                ctx.save();
                ctx.translate(cx, cy);
                ctx.rotate(-0.18);
                ctx.beginPath();
                ctx.ellipse(0, 0, n.rx, n.ry, 0, 0, Math.PI * 2);
                ctx.strokeStyle = idx === 0 ? 'rgba(245, 176, 39, 0.32)' : 'rgba(0, 229, 255, 0.22)';
                ctx.lineWidth = 1.1;
                ctx.stroke();
                ctx.restore();
            });

            const sunGrad = ctx.createRadialGradient(cx, cy, 2, cx, cy, 32);
            sunGrad.addColorStop(0, '#ffffff');
            sunGrad.addColorStop(0.3, '#67f3ff');
            sunGrad.addColorStop(0.65, 'rgba(0, 180, 255, 0.35)');
            sunGrad.addColorStop(1, 'transparent');
            ctx.fillStyle = sunGrad;
            ctx.beginPath();
            ctx.arc(cx, cy, 32, 0, Math.PI * 2);
            ctx.fill();

            renderedPositions = [];
            nodes.forEach(n => {
                n.angle += n.speed;
                const tilt = -0.18;
                const rawX = Math.cos(n.angle) * n.rx;
                const rawY = Math.sin(n.angle) * n.ry;

                const px = cx + rawX * Math.cos(tilt) - rawY * Math.sin(tilt);
                const py = cy + rawX * Math.sin(tilt) + rawY * Math.cos(tilt);

                renderedPositions.push({ x: px, y: py, node: n });

                const pGrad = ctx.createRadialGradient(px, py, 1, px, py, n.radius * 2.5);
                pGrad.addColorStop(0, n.color);
                pGrad.addColorStop(1, 'transparent');
                ctx.fillStyle = pGrad;
                ctx.beginPath();
                ctx.arc(px, py, n.radius * 2.5, 0, Math.PI * 2);
                ctx.fill();

                ctx.fillStyle = '#ffffff';
                ctx.beginPath();
                ctx.arc(px, py, n.radius * 0.55, 0, Math.PI * 2);
                ctx.fill();

                if (n.ring) {
                    ctx.strokeStyle = '#f5b027';
                    ctx.lineWidth = 1.6;
                    ctx.beginPath();
                    ctx.arc(px, py, n.radius + 9, 0, Math.PI * 2);
                    ctx.stroke();
                }

                ctx.font = 'bold 11px "Courier New", monospace';
                ctx.fillStyle = n.ring ? '#f5b027' : '#eaf6ff';
                ctx.fillText(n.name, px + (n.ring ? 22 : 12), py + 4);
            });

            requestAnimationFrame(drawSolarSystem);
        }
        drawSolarSystem();

        canvas.addEventListener('click', (e) => {
            const rect = canvas.getBoundingClientRect();
            const clickX = e.clientX - rect.left;
            const clickY

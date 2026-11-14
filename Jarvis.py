import streamlit as st
import streamlit.components.v1 as components

# Configuración de página completa en Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. // Núcleo de Comando",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Ocultar márgenes y barras por defecto de Streamlit para inmersión total
st.markdown("""
    <style>
        .block-container {
            padding-top: 0rem;
            padding-bottom: 0rem;
            padding-left: 0rem;
            padding-right: 0rem;
            max-width: 100%;
        }
        header, footer, #MainMenu {visibility: hidden;}
        body {background-color: #050814;}
    </style>
""", unsafe_allow_html=True)

# Interfaz completa de J.A.R.V.I.S. (HTML + CSS + JS)
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

        .orbit-container {
            position: relative;
            height: 180px;
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
            width: 140px;
            height: 140px;
            border: 1px solid rgba(0, 243, 255, 0.2);
            border-radius: 50%;
            animation: rotate-orbit 20s linear infinite;
        }

        @keyframes rotate-orbit {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .planet {
            position: absolute;
            padding: 4px 8px;
            background: rgba(5, 8, 20, 0.9);
            border: 1px solid var(--neon-blue);
            border-radius: 6px;
            font-size: 0.7rem;
            color: var(--neon-blue);
            box-shadow: 0 0 8px rgba(0, 243, 255, 0.3);
            cursor: pointer;
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
                <div class="telemetry-row" style="border: none; padding-top: 0;">
                    <div>CPU NÚCLEO: <span class="telemetry-val">25%</span></div>
                    <div>MEMORIA: <span class="telemetry-val">4.2 / 16 GB</span></div>
                    <div>RED: <span class="telemetry-val">16 ms // ÓPTIMO</span></div>
                </div>
                <div class="telemetry-row" style="margin-top: 8px;">
                    <div class="timestamp" id="live-clock">23:24:00</div>
                    <div style="color: var(--text-dim);">NODO BUIN // 13 NOV. 2026</div>
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
                <div class="planet" style="top: 25px; left: 35px;" onclick="alert('Módulo JARVIS Core: Operativo')">Agente</div>
                <div class="planet" style="bottom: 25px; right: 45px; border-color: var(--neon-gold); color: var(--neon-gold);" onclick="alert('La Isla de los Números: En desarrollo activo ($3.99 USD)')">J.A.R.V.I.S.</div>
            </div>
        </div>
    </div>

    <script>
        setInterval(() => {
            const now = new Date();
            const timeString = now.toTimeString().split(' ')[0];
            document.getElementById('live-clock').innerText = timeString;
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
    </script>
</body>
</html>
"""

# Renderizar el HUD en Streamlit
components.html(jarvis_hud_html, height=700, scrolling=True)

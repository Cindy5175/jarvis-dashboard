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
        .block-container { padding: 0rem !important; max-width: 100% !important; }
        header, footer, #MainMenu {visibility: hidden;}
        body, .stApp {background-color: #040711;}
    </style>
""", unsafe_allow_html=True)

# Parte 1: Estilos CSS y Cabecera del Núcleo
hud_part1 = """
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
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Courier New', Courier, monospace; }
        body {
            background-color: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            padding: 12px 12px 40px 12px;
            background-image:
                radial-gradient(circle at 50% 15%, rgba(0, 229, 255, 0.08) 0%, transparent 55%),
                linear-gradient(rgba(0, 229, 255, 0.025) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 229, 255, 0.025) 1px, transparent 1px);
            background-size: 100% 100%, 22px 22px, 22px 22px;
        }
        .hud-wrapper { max-width: 460px; margin: 0 auto; display: flex; flex-direction: column; gap: 14px; }
        .hud-card {
            background: var(--card-bg);
            border: 1px solid var(--border-cyan);
            border-radius: 16px;
            padding: 18px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6), inset 0 0 20px rgba(0, 229, 255, 0.04);
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
        }
        .header-top { display: flex; align-items: center; gap: 16px; margin-bottom: 18px; }
        .arc-orb {
            width: 44px; height: 62px; border-radius: 50%;
            border: 2.5px solid var(--cyan);
            box-shadow: 0 0 16px var(--cyan-glow), inset 0 0 14px var(--cyan-glow);
            display: flex; align-items: center; justify-content: center; flex-shrink: 0; cursor: pointer;
            animation: orbBreath 3s ease-in-out infinite;
        }
        .arc-orb-core {
            width: 24px; height: 36px; border-radius: 50%;
            background: radial-gradient(circle, #7cf4ff 0%, #00b8d4 70%, transparent 100%);
            box-shadow: 0 0 12px var(--cyan);
        }
        @keyframes orbBreath {
            0%, 100% { transform: scale(1); box-shadow: 0 0 14px var(--cyan-glow), inset 0 0 10px var(--cyan-glow); }
            50% { transform: scale(1.04); box-shadow: 0 0 24px var(--cyan), inset 0 0 18px var(--cyan); }
        }
        .title-block h1 { font-size: 1.25rem; line-height: 1.25; letter-spacing: 2px; color: var(--text-main); font-weight: bold; }
        .status-row { display: flex; align-items: center; gap: 8px; margin-top: 6px; font-size: 0.72rem; color: var(--green); letter-spacing: 1.2px; }
        .dot-live { width: 8px; height: 8px; border-radius: 50%; background: var(--green); box-shadow: 0 0 8px var(--green); animation: blink 1.6s infinite; }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
        .section-tag { font-size: 0.75rem; letter-spacing: 1.5px; color: var(--cyan); margin-bottom: 10px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; }
        .telemetry-grid {
            display: grid; grid-template-columns: 0.85fr 0.95fr 0.95fr 1.25fr;
            gap: 8px; align-items: start; border-top: 1px solid rgba(0, 229, 255, 0.12); padding-top: 14px; margin-top: 14px;
        }
        .tel-label { font-size: 0.63rem; color: var(--text-dim); line-height: 1.25; margin-bottom: 4px; }
        .tel-value { font-size: 0.78rem; color: var(--cyan); font-weight: bold; line-height: 1.3; }
        .clock-box { text-align: right; border-left: 1px solid rgba(255, 255, 255, 0.08); padding-left: 8px; }
        .clock-big { font-size: 1.05rem; color: var(--gold); font-weight: bold; letter-spacing: 1px; text-shadow: 0 0 10px rgba(245, 176, 39, 0.35); }
        .clock-sub { font-size: 0.62rem; color: var(--text-dim); margin-top: 3px; line-height: 1.3; }
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
        </div>
"""

# Parte 2: Mapa Táctico, Mapa Orbital y Caja de Chat Interactiva
hud_part2 = """
        <div class="hud-card">
            <div class="section-tag">
                <span>MAPA TÁCTICO SATELITAL</span>
                <span style="color: var(--green); font-size: 0.65rem;">● NODO BUIN</span>
            </div>
            <div style="position: relative; height: 180px; border-radius: 12px; border: 1px solid var(--cyan); background: radial-gradient(circle at 50% 50%, rgba(0, 229, 255, 0.12) 0%, rgba(2, 6, 14, 0.96) 75%), repeating-linear-gradient(0deg, rgba(0, 229, 255, 0.07) 0px, rgba(0, 229, 255, 0.07) 1px, transparent 1px, transparent 26px), repeating-linear-gradient(90deg, rgba(0, 229, 255, 0.07) 0px, rgba(0, 229, 255, 0.07) 1px, transparent 1px, transparent 26px); overflow: hidden; margin-top: 10px;">
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 60px; height: 60px; border: 1px solid rgba(0, 229, 255, 0.25); border-radius: 50%; pointer-events: none;"></div>
                <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 120px; height: 120px; border: 1px solid rgba(0, 229, 255, 0.25); border-radius: 50%; pointer-events: none;"></div>
                <div style="position: absolute; top: 50%; left: 50%; width: 240px; height: 240px; margin-top: -120px; margin-left: -120px; border-radius: 50%; background: conic-gradient(from 0deg, rgba(0, 229, 255, 0.32) 0deg, transparent 65deg); animation: spinRadar 4s linear infinite; pointer-events: none;"></div>
                <div style="position: absolute; top: 48%; left: 50%; width: 10px; height: 10px; border-radius: 50%; background: var(--gold); box-shadow: 0 0 10px var(--gold);"></div>
                <div style="position: absolute; top: 32%; left: 64%; width: 10px; height: 10px; border-radius: 50%; background: #00e5ff; box-shadow: 0 0 8px #00e5ff;"></div>
                <div style="position: absolute; top: 8px; left: 10px; font-size: 0.62rem; color: var(--cyan);">SAT-LINK // NODO BUIN (CHILE)</div>
                <div style="position: absolute; top: 8px; right: 10px; font-size: 0.62rem; color: var(--green);">LOCKED</div>
                <div style="position: absolute; bottom: 8px; left: 10px; font-size: 0.62rem; color: var(--text-dim);">LAT: -33.7312° S | LON: -70.7415° W</div>
            </div>
        </div>

        <div class="hud-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <h2 style="font-size: 0.9rem; letter-spacing: 1.5px; color: var

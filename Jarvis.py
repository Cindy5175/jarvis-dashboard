# ==========================================
# J.A.R.V.I.S. IA - NÚCLEO CONSOLIDADO CON EFECTOS Y AUDIO
# ==========================================

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="J.A.R.V.I.S. // IA",
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

jarvis_hud_html = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. HUD</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #040711;
            --panel-bg: rgba(8, 17, 36, 0.88);
            --cyan: #00f3ff;
            --cyan-glow: rgba(0, 243, 255, 0.45);
            --cyan-dim: rgba(0, 243, 255, 0.18);
            --text-main: #d8f8ff;
            --text-muted: #5b8fa8;
            --green-ok: #00ff9d;
            --amber: #ffae00;
            --red-alert: #ff3b5c;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg-dark);
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(0, 243, 255, 0.08) 0%, transparent 60%),
                linear-gradient(rgba(0, 243, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 30px 30px, 30px 30px;
            color: var(--text-main);
            font-family: 'Share Tech Mono', monospace;
            padding: 16px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .hud-container {
            width: 100%;
            max-width: 720px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .panel {
            background: var(--panel-bg);
            border: 1px solid var(--cyan);
            border-radius: 14px;
            padding: 18px;
            box-shadow: 0 0 18px rgba(0, 243, 255, 0.12), inset 0 0 12px rgba(0, 243, 255, 0.06);
            position: relative;
            transition: border-color 0.3s, box-shadow 0.3s;
        }

        body.combat-mode {
            --cyan: #ff3b5c;
            --cyan-glow: rgba(255, 59, 92, 0.5);
            --cyan-dim: rgba(255, 59, 92, 0.2);
        }

        .header-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--cyan-dim);
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 18px;
        }

        .stark-reactor-box {
            width: 70px;
            height: 66px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            cursor: pointer;
            filter: drop-shadow(0 0 12px var(--cyan-glow));
            animation: reactorPulse 2.8s ease-in-out infinite;
        }

        @keyframes reactorPulse {
            0%, 100% { filter: drop-shadow(0 0 8px var(--cyan-glow)); transform: scale(1); }
            50% { filter: drop-shadow(0 0 20px var(--cyan)); transform: scale(1.05); }
        }

        .title-block h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.4rem;
            font-weight: 900;
            letter-spacing: 2px;
            color: #ffffff;
            text-shadow: 0 0 10px var(--cyan-glow);
            line-height: 1.25;
        }

        .status-line {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-top: 6px;
            font-size: 0.85rem;
            color: var(--green-ok);
            letter-spacing: 1px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--green-ok);
            box-shadow: 0 0 8px var(--green-ok);
            animation: blink 1.5s infinite;
        }

        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

        .telemetry-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            padding-top: 14px;
            font-size: 0.8rem;
        }

        .tele-item span.label {
            display: block;
            color: var(--text-muted);
            font-size: 0.7rem;
            margin-bottom: 4px;
        }

        .tele-item span.val {
            color: var(--cyan);
            font-weight: bold;
            font-size: 0.95rem;
        }

        .tele-clock { text-align: right; }
        .tele-clock .time {
            font-family: 'Orbitron', sans-serif;
            color: var(--amber);
            font-size: 1.05rem;
            font-weight: bold;
            text-shadow: 0 0 8px rgba(255, 174, 0, 0.4);
        }
        .tele-clock .loc {
            color: var(--text-muted);
            font-size: 0.7rem;
            margin-top: 2px;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.85rem;
            letter-spacing: 1.5px;
            color: var(--cyan);
        }

        .badge {
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.75rem;
            padding: 2px 8px;
            border: 1px solid var(--cyan);
            border-radius: 4px;
            background: rgba(0, 243, 255, 0.1);
            color: var(--green-ok);
        }

        .radar-box {
            height: 205px;
            background: radial-gradient(circle, rgba(0, 45, 70, 0.6) 0%, rgba(3, 9, 20, 0.95) 80%);
            border: 1px solid var(--cyan-dim);
            border-radius: 10px;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .radar-grid {
            position: absolute;
            inset: 0;
            background-image: 
                linear-gradient(rgba(0, 243, 255, 0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 243, 255, 0.08) 1px, transparent 1px);
            background-size: 25px 25px;
        }

        .radar-circle {
            position: absolute;
            border: 1px solid rgba(0, 243, 255, 0.2

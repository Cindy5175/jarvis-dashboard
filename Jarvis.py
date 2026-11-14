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

# Interfaz completa de J.A.R.V.I.S. con Esfera 3D y 4 Órbitas
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

        /* Contenedor del Núcleo Neuronal con Esfera 3D */
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

        /* Mapa Orbital de Proyectos (4 Órbitas) */
        .orbit-container {
            position: relative;
            height: 200px;
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
            width: 160px;
            height: 160px;
            border: 1px solid rgba(0, 243, 255, 0.2);
            border-radius: 50%;
            animation: rotate-orbit 20s linear infinite;
        }


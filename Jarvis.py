import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import random
import json
import os
import requests

try:
    import psutil
except ImportError:
    psutil = None

st.set_page_config(
    page_title="Centro de Mando - J.A.R.V.I.S. Autónomo",
    page_icon="⚡",
    layout="wide"
)

MEMORIA_JARVIS = "memoria_jarvis.json"

def cargar_memoria():
    if os.path.exists(MEMORIA_JARVIS):
        try:
            with open(MEMORIA_JARVIS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "bitacora": [{"Hora": datetime.now().strftime("%H:%M:%S"), "Evento": "JARVIS Inicializado", "Estado": "ÓPTIMO"}],
        "nota_rapida": "Ideas de proyectos y notas del taller.",
        "iot_luces": True,
        "iot_monitores": True,
        "iot_temp": 21
    }

def guardar_memoria(datos):
    try:
        with open(MEMORIA_JARVIS, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
    except:
        pass

memoria_actual = cargar_memoria()

# Barra lateral: Idioma, Sarcasmo y Stark Sound System
st.sidebar.markdown("### 🌐 Configuración Neural")
idioma = st.sidebar.selectbox("Idioma del Sistema:", ["Español 🇨🇱", "English 🇺🇸", "Français 🇫🇷", "Português 🇧🇷"])
modo_sarcasmo = st.sidebar.toggle("⚡ Activar Modo Sarcasmo (Tony Stark)", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎵 Stark Sound System")
canal_musica = st.sidebar.selectbox(
    "Ambiente de Trabajo:",
    ["Synthwave / Cyberpunk 🌆", "Lo-Fi Beats / Focus ☕", "Iron Man Soundtrack 🦾", "Desactivado 🔇"]
)

urls_musica = {
    "Synthwave / Cyberpunk 🌆": "https://www.youtube.com/embed/4xDzrJKXOOY?autoplay=0",
    "Lo-Fi Beats / Focus ☕": "https://www.youtube.com/embed/5qap5aO4i9A?autoplay=0",
    "Iron Man Soundtrack 🦾": "https://www.youtube.com/embed/C6MZXNOubwk?autoplay=0"
}

if canal_musica != "Desactivado 🔇":
    st.components.v1.html(
        f'<div style="background:#000a12; padding:5px; border-radius:8px; border:1px solid #00f3ff;"><iframe width="100%" height="160" src="{urls_musica[canal_musica]}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>',
        height=180
    )

textos_ui = {
    "Español 🇨🇱": {
        "titulo": "⚡ J.A.R.V.I.S. AI AUTÓNOMO ⚡",
        "sub": "[ NÚCLEO NEURAL AUTÓNOMO & CONTROL CREATIVO ]",
        "presentacion": "¡Hola, Jefa! Soy J.A.R.V.I.S., tu IA autónoma en español. ¿Qué directiva creativa ejecutamos hoy?",
        "input": "Escribe una idea o consulta para J.A.R.V.I.S....",
        "tiempo": "📅 Sincronización Temporal",
        "hora": "⏱️ Hora (Chile):",
        "rendimiento": "💻 Rendimiento CPU/RAM",
        "clima": "🌤️ Clima Buin (En Vivo)",
        "ping": "⚡ Conectividad y Ping",
        "proyectos": "🚀 Proyectos del Taller",
        "mapa": "🛰️ Radar GPS & Telemetría Móvil",
        "iot": "🤖 Domótica del Taller (IoT)",
        "cronometro": "⏱️ Cuenta Regresiva Stark"
    },
    "English 🇺🇸": {
        "titulo": "⚡ J.A.R.V.I.S. AUTONOMOUS AI ⚡",
        "sub": "[ AUTONOMOUS NEURAL CORE & CREATIVE CONTROL ]",
        "presentacion": "Hello, Boss! I am J.A.R.V.I.S., your autonomous English-ready AI. What creative directive shall we execute today?",
        "input": "Type an idea or query for J.A.R.V.I.S....",
        "tiempo": "📅 Temporal Synchronization",
        "hora": "⏱️ Time (Chile):",
        "rendimiento": "💻 CPU/RAM Performance",
        "clima": "🌤️ Buin Weather (Live)",
        "ping": "⚡ Connectivity & Ping",
        "proyectos": "🚀 Workshop Projects",
        "mapa": "🛰️ GPS Radar & Mobile Telemetry",
        "iot": "🤖 Workshop Smart Control (IoT)",
        "cronometro": "⏱️ Stark Countdown"
    },
    "Français 🇫🇷": {
        "titulo": "⚡ J.A.R.V.I.S. IA AUTONOME ⚡",
        "sub": "[ NOYAU NEURAL AUTONOME & CONTRÔLE CRÉATIF ]",
        "presentacion": "Bonjour, Chef ! Je suis J.A.R.V.I.S., votre IA autonome. Quelle directive créative exécutons-nous aujourd'hui ?",
        "input": "Écrivez une idée ou une requête pour J.A.R.V.I.S....",
        "tiempo": "📅 Synchronisation Temporelle",
        "hora": "⏱️ Heure (Chili) :",
        "rendimiento": "💻 Performance CPU/RAM",
        "clima": "🌤️ Météo Buin (En Direct)",
        "ping": "⚡ Connectivité & Ping",
        "proyectos": "🚀 Projets d'Atelier",
        "mapa": "🛰️ Radar GPS & Télémétrie Mobile",
        "iot": "🤖 Domotique d'Atelier (IoT)",
        "cronometro": "⏱️ Compte à rebours Stark"
    },
    "Português 🇧🇷": {
        "titulo": "⚡ J.A.R.V.I.S. IA AUTÔNOMA ⚡",
        "sub": "[ NÚCLEO NEURAL AUTÔNOMO & CONTROLE CRIATIVO ]",
        "presentacion": "Olá, Chefe! Sou o J.A.R.V.I.S., sua IA autônoma em português. Qual diretriz criativa executamos hoje?",
        "input": "Digite uma ideia ou consulta para o J.A.R.V.I.S....",
        "tiempo": "📅 Sincronização Temporal",
        "hora": "⏱️ Hora (Chile):",
        "rendimiento": "💻 Desempenho CPU/RAM",
        "clima": "🌤️ Clima Buin (Ao Vivo)",
        "ping": "⚡ Conectividade e Ping",
        "proyectos": "🚀 Projetos da Oficina",
        "mapa": "🛰️ Radar GPS e Telemetria Móvel",
        "iot": "🤖 Domótica da Oficina (IoT)",
        "cronometro": "⏱️ Contagem Regressiva Stark"
    }
}

t = textos_ui[idioma]

css_estilo = """
    .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000 !important;
    }
    h1 {
        text-align: center !important;
        color: #00f3ff !important;
        text-shadow: 0px 0px 12px rgba(0, 243, 255, 0.8);
        font-size: 28px !important;
        width: 100% !important;
        display: block !important;
    }
    h3 {
        color: #00f3ff !important;
        text-shadow: 0px 0px 8px rgba(0, 243, 255, 0.6);
        margin-top: 0px !important;
    }
    p, span, label, div, markdown, .stMarkdown {
        color: #80f9ff !important;
    }
    .card-tactica {
        background-color: #000a12 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 10px !important;
        padding: 16px !important;
        margin-bottom: 20px !important;
        box-shadow: 0px 0px 10px rgba(0, 243, 255, 0.3) !important;
    }
    .reloj-digital {
        background-color: #000000 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px !important;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.4) !important;
        font-size: 20px !important;
        padding: 4px 10px !important;
        font-family: monospace;
        display: inline-block;
    }
    div[data-testid="stChatMessage"] {
        background-color: #000a12 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 8px !important;
        box-shadow: 0px 0px 6px rgba(0, 243, 255, 0.3);
        margin-bottom: 10px;
    }
    div[data-testid="stChatMessage"] * {
        color: #00f3ff !important;
    }
    .banner-ondas {
        width: 100%;
        height: 60px;
        background: linear-gradient(90deg, #000000 0%, #031525 50%, #000000 100%);
        border: 1px solid #00f3ff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0px 0px 15px rgba(0, 243, 255, 0.4);
        margin-bottom: 20px;
        text-align: center;
    }
    .stButton>button {
        background-color: #000a12 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px;
        box-shadow: 0px 0px 6px rgba(0, 243, 255, 0.4);
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #00f3ff !important;
        color: #000000 !important;
    }
"""
st.markdown(f"<style>{css_estilo}</style>", unsafe_allow_html=True)

def emitir_voz(texto, lang_code):
    lang_map = {"Español 🇨🇱": "es-ES", "English 🇺🇸": "en-US", "Français 🇫🇷": "fr-

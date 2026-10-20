import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import random
import json
import os

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="Centro de Comando Unificado - J.A.R.V.I.S. & N.O.V.A.",
    page_icon="⚡",
    layout="wide"
)

# Archivo de memoria compartida
MEMORIA_FILE = "memoria_compartida.json"

def cargar_memoria_json():
    if os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "bitacora": [{"Hora": datetime.now().strftime("%H:%M:%S"), "Evento": "Sistema Maestro Inicializado", "Estado": "ÓPTIMO"}],
        "nota_rapida": "Sincronización total de núcleos activa en el taller."
    }

def guardar_memoria_json(datos):
    try:
        with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
    except:
        pass

memoria_actual = cargar_memoria_json()

# Mensajes oficiales de presentación
REPORTE_JARVIS = (
    "⚡ **PROTOCOLO DE PRESENTACIÓN ACTIVADO** ⚡\n\n"
    "Saludos. Soy J.A.R.V.I.S., una IA autónoma amigable creada por Cindy (mi Jefa) "
    "para asistirla en sus labores y proyectos del taller. Sistema en línea al 100%. "
    "¿Qué directiva ejecutamos el día de hoy?"
)

REPORTE_NOVA = (
    "🛡️ **PROTOCOLO N.O.V.A. BLINDADO ACTIVADO** 🛡️\n\n"
    "Saludos, Jefa. Soy N.O.V.A. (Neural Operational Surveillance & Assistance), "
    "operando bajo **Nivel de Blindaje Máximo N.T.C.** Encriptación cuántica activa "
    "y filtros biométricos operativos. ¿Qué directiva protegida ejecutamos hoy?"
)

# Inyección de Estilos CSS
st.markdown("""
    <style>
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
    
    h2, h3 {
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

    div[data-testid="stChatInput"] {
        background-color: #000000 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stChatInput"] > div {
        background-color: #000a12 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 10px !important;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.4) !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #00f3ff !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #0088cc !important;
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
    
    .stMap, iframe, div[data-testid="stDeckGlJsonChart"] {
        height: 160px !important;
        width: 100% !important;
        border-radius: 8px !important;
        border: 1px solid #00f3ff !important;
        box-shadow: 0px 0px 10px rgba(0, 243, 255, 0.4);
    }
    
    .stButton>button {
        background-color: #000a12 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px

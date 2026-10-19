import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import random

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Inyección de Estilos CSS precisos (Fondo negro, neón azul, caja del chat y mapa compacto)
st.markdown("""
    <style>
    /* Fondo negro profundo general */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Centrar el encabezado principal y darle azul neón brillante */
    h1 {
        text-align: center;
        color: #00f3ff !important;
        text-shadow: 0px 0px 10px rgba(0, 243, 255, 0.7);
    }
    
    /* Demás títulos en azul neón */
    h2, h3 {
        color: #00f3ff !important;
        text-shadow: 0px 0px 8px rgba(0, 243, 255, 0.6);
    }
    
    /* Textos generales en azul neón */
    p, span, label, div, markdown, .stMarkdown {
        color: #80f9ff !important;
    }
    
    /* Estilo táctico para la caja de la hora (Reloj negro con azul neón) */
    code, .stCodeBlock {
        background-color: #000000 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px !important;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.4) !important;
        font-size: 20px !important;
        padding: 4px 10px !important;
    }
    
    /* Estilo del historial de mensajes del chat */
    div[data-testid="stChatMessage"] {
        background-color: #000000 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 8px !important;
        box-shadow: 0px 0px 6px rgba(0, 243, 255, 0.3);
        margin-bottom: 8px;
    }
    div[data-testid="stChatMessage"] * {
        color: #00f3ff !important;
    }

    /* FORZAR LA CAJA DE TEXTO DEL CHAT A FONDO NEGRO Y LETRAS AZUL NEÓN */
    div[data-testid="stChatInput"] {
        background-color: #000000 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stChatInput"] > div {
        background-color: #000000 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 10px !important;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.3) !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: #000000 !important;
        color: #00f3ff !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #0088cc !important;
    }
    div[data-testid="stChatInput"] button {
        background-color: #000a12 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
    }
    
    /* Banner de ondas de IA táctico */
    .banner-ondas {
        width: 100%;
        height: 90px;
        background: linear-gradient(90deg, #000000 0%, #031525 50%, #000000 100%);
        border: 1px solid #00f3ff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0px 0px 15px rgba(0,

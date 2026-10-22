from datetime import datetime, timedelta
import json
import os
import random
import pandas as pd
import pytz
import requests
import streamlit as st

try:
  import psutil
except ImportError:
  psutil = None

# Configuración de la página en modo ancho y estética Stark
st.set_page_config(
    page_title="Stark Core - Dual Interface", page_icon="⚡", layout="wide"
)

# Estilos CSS personalizados: Modo Sigilo, Neón Azul y Diseño Minimalista
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    .chat-container {
        border: 1.5px solid #00f0ff;
        border-radius: 12px;
        padding: 12px 18px;
        box-shadow: 0 0 15px rgba(0, 240, 255, 0.3);
        background-color: rgba(0, 10, 20, 0.6);
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .console-title {
        color: #00f0ff;
        font-family: monospace;
        font-size: 14px;
        text-align: center;
        margin-bottom: 8px;
        letter-spacing: 1px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Título principal del centro de mando
st.markdown(
    "<h2 style='text-align: center; color: #00f0ff; font-family: monospace;"
    " font-size: 20px;'>CENTRO DE MANDO STARK — NÚCLEOS DUALES EN ESPERA</h2>",
    unsafe_allow_html=True,
)
st.markdown("---")

# Layout de dos columnas para JARVIS y NOVA en Modo Sigilo
col1, col2 = st.columns(2)

with col1:
  st.markdown(
      '<p class="console-title">J.A.R.V.I.S. — MODO SIGILO ACTIVO</p>',
      unsafe_allow_html=True,
  )
  # Caja de chat con el Reactor ARC de JARVIS
  st.markdown(
      """
        <div class="chat-container">
            <span style="font-size: 26px; margin-right: 14px;">🔵</span>
            <span style="color: #a0a0a0; font-family: sans-serif; font-size: 15px;">¿Qué directiva operativa o creativa ejecutamos hoy?</span>
        </div>
        """,
      unsafe_allow_html=True,
  )

with col2:
  st.markdown(
      '<p class="console-title">N.O.V.A. — UNIDAD TÁCTICA ACTIVA</p>',
      unsafe_allow_html=True,
  )
  # Caja de chat con la Estrella NOVA
  st.markdown(
      """
        <div class="chat-container">
            <span style="font-size: 26px; margin-right: 14px;">🌟</span>
            <span style="color: #a0a0a0; font-family: sans-serif; font-size: 15px;">¿Qué directiva operativa o creativa ejecutamos hoy?</span>
        </div>
        """,
      unsafe_allow_html=True,
  )

# Lógica complementaria del sistema base (si deseas agregar más funciones o métricas abajo)
if psutil:
  # Opcional: métricas de sistema en segundo plano si se requieren
  pass

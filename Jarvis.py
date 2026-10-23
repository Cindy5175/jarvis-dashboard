import os
import streamlit as st
from openai import OpenAI

# Configuración de página de Streamlit
st.set_page_config(page_title="JARVIS AI", page_icon="⚡", layout="wide")

# 1. Obtener la clave desde los Secrets de Streamlit
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la OPENAI_API_KEY en los Secrets.")
    st.stop()

# 2. Inicializar cliente de OpenAI
client = OpenAI(api_key=api_key)

st.title("⚡ Panel de Control - JARVIS")
st.success("¡Motor conectado y listo, Jefa!")

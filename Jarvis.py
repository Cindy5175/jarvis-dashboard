import streamlit as st
import time
from groq import Groq

# 1. Configuración visual inicial (esto debe ser lo primero para que pinte la pantalla)
st.set_page_config(page_title="Centro de Comando Stark", layout="wide")

st.title("⚡ Centro de Comando Stark - N.O.V.A.")

# 2. Inicialización segura del cliente (usando st.cache_resource para que no bloquee)
@st.cache_resource
def obtener_cliente_groq():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            return None
        return Groq(api_key=api_key, timeout=10.0)
    except Exception:
        return None

client = obtener_cliente_groq()

# 3. Entrada de usuario controlada por interfaz (evita bloqueos automáticos)
prompt_usuario = st.chat_input("Escriba su comando para N.O.V.A. o Siri...")

if prompt_usuario:
    if not client:
        st.error("⚠️ Falta configurar la API Key de Groq en los secrets.")
    else:
        with st.spinner("Procesando comando táctico..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt_usuario}],
                    model="llama3-70b-8192",
                )
                respuesta = chat_completion.choices[0].message.content
                st.write(respuesta)
            except Exception as e:
                st.error(f"Error de enlace con los servidores de Groq, Jefa: {e}")

import time
from groq import Groq
import streamlit as st

# Inicializar cliente de Groq con un timeout de seguridad (10 segundos)
# Esto evita que la app se quede bloqueada indefinidamente esperando una respuesta de red.
try:
    api_key = st.secrets.get("GROQ_API_KEY", "tu_api_key")
    client = Groq(api_key=api_key, timeout=10.0)
except Exception as e:
    client = None

def consultar_groq_seguro(prompt_usuario, modelo="llama3-70b-8192"):
    """
    Envía una consulta a Groq con control de errores y timeout para proteger 
    el Centro de Comando Stark de pantallas en blanco.
    """
    if not client:
        st.error("⚠️ La clave de API de Groq no está configurada correctamente en los secrets.")
        return "Error de configuración."

    try:
        # Llamada protegida a la API de Groq
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt_usuario,
                }
            ],
            model=modelo,
        )
        return chat_completion.choices[0].message.content
        
    except Exception as e:
        # Capturamos cualquier error de red, timeout o fallo del servidor y lo mostramos limpiamente
        st.error(f"Error de enlace con los servidores de Groq, Jefa: {e}")
        return None

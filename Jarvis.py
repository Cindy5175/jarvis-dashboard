import time
from groq import Groq
import streamlit as st

# Inicializar cliente de Groq (asegúrese de tener su API key configurada)
client = Groq(api_key=st.secrets.get("GROQ_API_KEY", "tu_api_key"))

def consultar_groq_con_respaldo(prompt_usuario, modelo="llama3-70b-8192", reintentos=3):
    """
    Envía una consulta a Groq con reintentos automáticos y manejo de errores
    para evitar caídas en el Centro de Comando Stark.
    """
    intento = 0
    while intento < reintentos:
        try:
            # Llamada a la API de Groq
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
            intento += 1
            time.sleep(1) # Espera un segundo antes de reintentar
            if intento == reintentos:
                # Si falla tras los reintentos, lanzamos una alerta amigable
                st.warning(f"⚠️ Servidores de Groq ocupados temporalmente. Reintentando enlace...")
                return None

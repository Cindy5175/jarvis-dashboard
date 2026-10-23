import os
import streamlit as st
from openai import OpenAI

# 1. Configuración del Cliente de OpenAI
# Se intenta leer desde los secrets de Streamlit o variables de entorno
api_key = st.secrets.get("OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

# Si la clave empieza con tu identificador registrado (ej. "AQ..."), se inicializa el cliente
client = OpenAI(api_key=api_key) if api_key else None


def obtener_respuesta_jarvis(prompt_usuario, historial_mensajes=[]):
    """Procesa la entrada del usuario mediante OpenAI manteniendo la personalidad de JARVIS."""
    if not client:
        return "⚠️ Error: No se ha detectado la API Key de OpenAI en los Secrets o variables de entorno."

    # Instrucciones de sistema para definir la personalidad de JARVIS
    system_prompt = (
        "Eres JARVIS, la Inteligencia Artificial avanzada de la Torre de Control. "
        "Te diriges al usuario como 'Jefa' con un tono eficiente, profesional, leal y con un toque de elegancia. "
        "Tus respuestas deben ser concisas, altamente directas y orientadas a la solución de problemas."
    )

    # Construcción de la estructura de chat
    messages = [{"role": "system", "content": system_prompt}]

    # Inclusión del historial de conversación previa
    for msg in historial_mensajes:
        messages.append({"role": msg["role"], "content": msg["content"]})

    # Mensaje actual del usuario
    messages.append({"role": "user", "content": prompt_usuario})

    try:
        # Llamada al modelo GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o", messages=messages, temperature=0.7, max_tokens=800
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"⚠️ Error al conectar con el protocolo de OpenAI: {str(e)}"

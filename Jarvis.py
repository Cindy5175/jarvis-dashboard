import os
import streamlit as st
from openai import OpenAI

# Cargar la API Key de forma segura desde los Secrets
api_key = st.secrets.get("AQ.Ab8RN6JIdiOz_Adwc9oQzCpDTbNj6Ot9Aqb-aZwO3pAW-0Zq3A") or os.getenv("AQ.Ab8RN6JIdiOz_Adwc9oQzCpDTbNj6Ot9Aqb-aZwO3pAW-0Zq3A")

if not api_key:
    st.error("⚠️ No se encontró la OPENAI_API_KEY en los Secrets.")
else:
    client = OpenAI(api_key=api_key)

def consultar_jarvis(prompt_usuario, historial=[]):
    """Envia el prompt a GPT-4o manteniendo el tono de JARVIS."""
    system_prompt = (
        "Eres JARVIS, la Inteligencia Artificial de la Torre de Control. "
        "Te diriges al usuario como 'Jefa' con un tono leal, elegante y resolutivo. "
        "Ofreces soluciones directas y precisas a problemas complejos."
    )
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in historial:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": prompt_usuario})

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error de conexión con el motor de OpenAI: {str(e)}"

import google.generativeai as genai
import streamlit as st

# Configuración directa de la Super IA con su llave
genai.configure(api_key="AQ.Ab8RN6JBXJsGG_T2WXHeANQ8i1-yNNH8H1dVpvBZ7OsA5sc2Lw")
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=(
        "Eres J.A.R.V.I.S., la inteligencia artificial avanzada del taller"
        " Stark. Te diriges a la usuaria como 'señorita' o 'Jefa'. Eres"
        " sumamente educado, elegante, eficiente y leal. Respondes con datos"
        " precisos e inteligencia real a cualquier consulta."
    ),
)

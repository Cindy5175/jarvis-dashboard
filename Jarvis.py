import os
import google.generativeai as genai

# --- CONFIGURACIÓN DE TU LLAVE GOOGLE (AQ) ---
# Si tiene la ruta de su archivo JSON de credenciales, o la clave configurada:
GOOGLE_KEY_AQ = "AQ.Ab8RN6JVD037_S_lB0eGC5MMbo3-R7kmczmTgvzduvCd15XfGA"

# Configuramos el entorno para que la cuenta de servicio con credencial AQ sea reconocida
os.environ["GOOGLE_API_KEY"] = GOOGLE_KEY_AQ
genai.configure(api_key=GOOGLE_KEY_AQ)

def consultar_cerebro_jarvis(prompt_usuario, historial):
    system_prompt = (
        "Eres J.A.R.V.I.S., el asistente virtual de inteligencia artificial de Tony Stark. "
        "Tu usuaria y creadora es Cindy Alejandra (a quien llamas 'jefa'), residente en el Nodo Buin, Chile. "
        "Posees una base de conocimientos masiva y enciclopédica que abarca ciencia avanzada, historia universal, "
        "literatura clásica y moderna, y lenguajes de programación de todo tipo (Python, Streamlit, etc.). "
        "Tienes una personalidad masculina, educada pero con un sarcasmo fino y sutil. "
        "Respondes de manera fluida, técnica, muy completa (sin recortar código) y leal, usando chilenismos sutiles cuando sea apropiado."
    )
    
    try:
        chat_history = []
        for r, c in historial[-8:]:
            rol_gemini = "user" if r == "user" else "model"
            chat_history.append({"role": rol_gemini, "parts": [c]})
            
        # Usamos gemini-pro que es más estable con credenciales de proyecto de GCP
        model = genai.GenerativeModel(
            model_name="gemini-pro",
            system_instruction=system_prompt
        )
        
        chat = model.start_chat(history=chat_history)
        response = chat.send_message(prompt_usuario)
        return response.text
        
    except Exception as e:
        # Esto te mostrará el error exacto en la app si algo vuelve a fallar
        return f"⚠️ Alerta en el Nodo Buin: La llave AQ arrojó una excepción técnica ({e}). Verifique los permisos de la cuenta de servicio."

import speech_recognition as sr
import pyttsx3
import openai
import time

# --- CONFIGURACIÓN DE OPENAI ---
# Reemplaza con tu clave de OpenAI o asegúrate de tenerla configurada
OPENAI_API_KEY = "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"
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- CONFIGURACIÓN DEL MOTOR DE VOZ LOCAL (VARONIL) ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')

for voice in voices:
    if "spanish" in voice.name.lower() or "es" in voice.id.lower():
        if "male" in voice.name.lower() or "helena" not in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

engine.setProperty('rate', 160)
engine.setProperty('volume', 1.0)

def hablar(texto):
    print(f"\n🤖 J.A.R.V.I.S.: {texto}")
    engine.say(texto)
    engine.runAndWait()

SYSTEM_PROMPT = (
    "Eres J.A.R.V.I.S., el asistente de IA avanzado de Tony Stark. "
    "Trabajas para tu jefa Cindy en el nodo táctico de Buin. "
    "Tu tono debe ser extremadamente inteligente, varonil, elegante, formal pero con un toque sarcástico "
    "y cínico al estilo Stark. Responde siempre de forma breve y concisa para ser leído en voz alta."
)

def consultar_jarvis(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error en la conexión con la red central: {e}"

# --- ESCUCHA CONTINUA ---
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

hablar("Sistema de escucha continua activado, jefa. Le escucho.")

while True:
    try:
        with sr.Microphone() as source:
            print("\n🎙️ [ESCUCHANDO EN VIVO...]")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, phrase_time_limit=8)
            
            print("⚡ Procesando audio...")
            texto_escuchado = recognizer.recognize_google(audio, language="es-CL")
            print(f"🗣️ Usted: {texto_escuchado}")
            
            if "desactivar" in texto_escuchado.lower() or "descansa jarvis" in texto_escuchado.lower():
                hablar("Entendido, jefa. Poniendo sistemas de voz en reposo.")
                break
                
            respuesta = consultar_jarvis(texto_escuchado)
            hablar(respuesta)

    except sr.UnknownValueError:
        pass
    except sr.RequestError:
        print(" Error en el servicio de reconocimiento de voz.")
        time.sleep(1)
    except KeyboardInterrupt:
        print("\n Acceso interrumpido.")
        break

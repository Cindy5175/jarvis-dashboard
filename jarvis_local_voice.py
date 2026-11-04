import speech_recognition as sr
import pyttsx3
import requests
import json
import time

# --- CONFIGURACIÓN DEL MOTOR DE VOZ LOCAL (VARONIL) ---
engine = pyttsx3.init()
voices = engine.getProperty('voices')

# Seleccionar voz masculina si está disponible en tu sistema
for voice in voices:
    if "spanish" in voice.name.lower() or "es" in voice.id.lower():
        if "male" in voice.name.lower() or "helena" not in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break

engine.setProperty('rate', 160)  # Velocidad de habla elegante y pausada
engine.setProperty('volume', 1.0) # Volumen al máximo

def hablar(texto):
    print(f"\n🤖 J.A.R.V.I.S.: {texto}")
    engine.say(texto)
    engine.runAndWait()

# --- CONFIGURACIÓN DE CONEXIÓN CON HOB / OLLAMA ---
# Hob expone su API localmente (por defecto en localhost:11434 o el puerto configurado en Hob)
HOB_API_URL = "http://localhost:11434/api/generate"
MODELO_LOCAL = "llama3"  # Cambia por el nombre del modelo que tengas cargado en Hob

SYSTEM_PROMPT = (
    "Eres J.A.R.V.I.S., el asistente de IA avanzado de Tony Stark. "
    "Trabajas para tu jefa Cindy en el nodo táctico de Buin. "
    "Tu tono debe ser extremadamente inteligente, varonil, elegante, formal pero con un toque sarcástico "
    "y cínico al estilo Stark. Responde de forma breve y concisa para ser leído en voz alta."
)

def consultar_hob(prompt):
    payload = {
        "model": MODELO_LOCAL,
        "prompt": f"System: {SYSTEM_PROMPT}\nUser: {prompt}\nAssistant:",
        "stream": False
    }
    try:
        response = requests.post(HOB_API_URL, json=payload, timeout=15)
        if response.status_code == 200:
            return response.json().get("response", "Sin respuesta del módulo local.")
        else:
            return "El servidor de Hob no respondió correctamente, jefa."
    except Exception as e:
        return "No pude conectar con el nodo local de Hob. Verifica que el servidor esté activo."

# --- PROTOCOLO DE ESCUCHA CONTINUA (HANDS-FREE) ---
recognizer = sr.Recognizer()
recognizer.energy_threshold = 300  # Sensibilidad del micrófono
recognizer.dynamic_energy_threshold = True

hablar("Sistema de escucha continua local activado, jefa. Hob sincronizado en Buin. Le escucho.")

while True:
    try:
        with sr.Microphone() as source:
            print("\n🎙️ [ESCUCHANDO EN VIVO...]")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, phrase_time_limit=8)
            
            print("⚡ Procesando audio...")
            texto_escuchado = recognizer.recognize_google(audio, language="es-CL")
            print(f"🗣️ Usted: {texto_escuchado}")
            
            # Comando de apagado local
            if "desactivar" in texto_escuchado.lower() or "descansa jarvis" in texto_escuchado.lower():
                hablar("Entendido, jefa. Poniendo sistemas de voz locales en reposo.")
                break
                
            # Procesar orden con Hob
            respuesta = consultar_hob(texto_escuchado)
            hablar(respuesta)

    except sr.UnknownValueError:
        # El micrófono no captó palabras claras, continúa escuchando en silencio
        pass
    except sr.RequestError:
        print(" Error en el servicio de reconocimiento de voz.")
        time.sleep(1)
    except KeyboardInterrupt:
        print("\n Acceso interrumpido manualmente.")
        break

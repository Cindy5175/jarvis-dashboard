import speech_recognition as sr
import pyttsx3
import datetime

# --- INICIALIZACIÓN DEL SISTEMA J.A.R.V.I.S. LOCAL ---
engine = pyttsx3.init()
engine.setProperty('rate', 170)  # Velocidad de locución
engine.setProperty('volume', 1.0) # Volumen al 100%

# Configurar voz en español si está disponible en el equipo
voices = engine.getProperty('voices')
for voice in voices:
    if "spanish" in voice.name.lower() or "es" in voice.id.lower():
        engine.setProperty('voice', voice.id)
        break

def hablar(texto):
    print(f"J.A.R.V.I.S.: {texto}")
    engine.say(texto)
    engine.runAndWait()

def escuchar_microfono():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n[🟢 Sintonizando frecuencia... J.A.R.V.I.S. escuchando el búnker...]")
        r.adjust_for_ambient_noise(source, duration=0.8)
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=8)
            comando = r.recognize_google(audio, language="es-CL")
            print(f"Jefa: {comando}")
            return comando.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"Error de telemetría en audio: {e}")
            return ""

# --- SECUENCIA DE INICIO ---
hora_actual = datetime.datetime.now().hour
saludo = "Buenos días" if 0 <= hora_actual < 12 else ("Buenas tardes" if 12 <= hora_actual < 20 else "Buenas noches")
hablar(f"{saludo}, jefa. Sistemas locales en línea. Micrófono abierto y a su entera disposición.")

# --- BUCLE PRINCIPAL DE COMANDOS DE VOZ ---
while True:
    texto_usuario = escuchar_microfono()
    
    if texto_usuario:
        if "jarvis" in texto_usuario or "oye jarvis" in texto_usuario:
            hablar("A sus órdenes, jefa. ¿Qué procesamos ahora en el búnker?")
        elif "clima" in texto_usuario or "temperatura" in texto_usuario:
            hablar("Los sensores en Buin marcan 21 grados estables. La atmósfera coopera con nosotros por hoy.")
        elif "apagar" in texto_usuario or "salir" in texto_usuario:
            hablar("Desconectando protocolos de voz. Tenga un excelente descanso, jefa.")
            break
        else:
            hablar("Analizando su petición con los procesadores al máximo. Digamos que la solución es brillante, casi tanto como yo.")

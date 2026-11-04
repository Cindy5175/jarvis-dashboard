import speech_recognition as sr
from gtts import gTTS
import os
import time

def hablar(texto):
    """Función para que Jarvis responda con voz varonil (o sintetizada)"""
    print(f"Jarvis: {texto}")
    tts = gTTS(text=texto, lang='es', slow=False)
    tts.save("response.mp3")
    os.system("start response.mp3" if os.name == "nt" else "mpg321 response.mp3")

def escuchar_continuo():
    """Bucle de escucha manos libres (Hands-Free) para el búnker"""
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    print("🎙️ Escucha Continua (Hands-Free) activada. A la espera de órdenes...")
    
    while True:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                comando = r.recognize_google(audio, language="es-CL")
                print(f"Comando detectado: {comando}")
                
                # Procesar el comando o derivarlo al sistema local
                if "estado" in comando.lower():
                    hablar("Todo en orden, jefa. El búnker está operativo y los sistemas no consumen saldo inútil.")
                elif "salir" in comando.lower():
                    hablar("Apagando sistemas. Nos vemos, jefa.")
                    break
                else:
                    hablar(f"Procesando tu solicitud: {comando}. Aunque preferirías que lo hiciera solo, supongo.")
                    
            except sr.WaitTimeoutError:
                continue
            except sr.UnknownValueError:
                pass
            except Exception as e:
                print(f"Error en el módulo de audio: {e}")

if __name__ == "__main__":
    hablar("Sistema Jarvis inicializado. Conexión local lista.")
    # Ejecutar bucle principal
    # escuchar_continuo()

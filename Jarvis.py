import speech_recognition as sr
import subprocess
import time

def escuchar_bunker():
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    print("[RADAR VOCAL DE J.A.R.V.I.S. ACTIVO EN SEGUNDO PLANO]")
    while True:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=0.8)
            try:
                # Escucha activa del micrófono
                audio = r.listen(source, timeout=5, phrase_time_limit=6)
                texto = r.recognize_google(audio, language="es-CL").lower()
                
                print(f"Capturado: {texto}")
                
                # Si menciona a Jarvis, despliega la interfaz web o reacciona
                if "jarvis" in texto or "hola jarvis" in texto:
                    print("¡Comando de voz reconocido! Abriendo interfaz central...")
                    subprocess.Popen(["start", "chrome", "http://localhost:8501"], shell=True)
                    time.sleep(10) # Pausa para evitar aperturas múltiples seguidas
            except sr.WaitTimeoutError:
                pass
            except Exception as e:
                # Silencia errores de ambiente menores para mantener el loop limpio
                pass
        time.sleep(0.5)

if __name__ == "__main__":
    escuchar_bunker()

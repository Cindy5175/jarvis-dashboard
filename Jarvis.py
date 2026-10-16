import speech_recognition as sr
import subprocess
import time

def escuchar_bunker():
    r = sr.Recognizer()
    mic = sr.Microphone()
    
    print("[OÍDO TÁCTICO DE J.A.R.V.I.S. ACTIVADO]")
    while True:
        with mic as source:
            r.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = r.listen(source, timeout=5, phrase_time_limit=5)
                texto = r.recognize_google(audio, language="es-CL").lower()
                
                print(f"Detectado: {texto}")
                if "jarvis" in texto or "hola jarvis" in texto:
                    print("¡Palabra de activación detectada! Despertando sistemas...")
                    # Aquí puede hacer que abra el navegador o ejecute una acción
                    subprocess.Popen(["start", "chrome", "http://localhost:8501"], shell=True)
            except Exception:
                pass
        time.sleep(0.5)

if __name__ == "__main__":
    escuchar_bunker()

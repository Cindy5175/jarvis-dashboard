import speech_recognition as sr
from gtts import gTTS
import os

r = sr.Recognizer()
mic = sr.Microphone()

print("🎙️ Escucha Continua (Hands-Free) activada...")
with mic as source:
    r.adjust_for_ambient_noise(source, duration=0.5)

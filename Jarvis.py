import streamlit as st
import datetime
import sqlite3
import requests
import random
import os
import sys
import time
import threading

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import cv2
    CV2_DISPONIBLE = True
except Exception:
    cv2 = None
    CV2_DISPONIBLE = False

try:
    import speech_recognition as sr
    SR_DISPONIBLE = True
except Exception:
    sr = None
    SR_DISPONIBLE = False

try:
    import pyttsx3
    TTS_DISPONIBLE = True
except Exception:
    pyttsx3 = None
    TTS_DISPONIBLE = False


def camara_disponible(indice: int = 0) -> bool:
    """Verifica de forma segura si OpenCV y la cámara están operativos."""
    if not CV2_DISPONIBLE or cv2 is None:
        return False
    try:
        cap = cv2.VideoCapture(indice)
        disponible = cap.isOpened()
        cap.release()
        return disponible
    except Exception:
        return False


class JarvisCoreEnhancements:
    """
    Módulo unificado y seguro (local + Streamlit Cloud) para JARVIS:
    1. Escucha continua manos libres (sin botones)
    2. Personalidad con voz varonil y sarcasmo seco
    3. Protocolos de conocimiento extremo
    4. Activación de mapa táctico satelital y sensor de movimiento
    """

    def __init__(self, on_command_callback=None, on_motion_callback=None):
        self.activo = True
        self.hablando = False
        self.on_command_callback = on_command_callback
        self.on_motion_callback = on_motion_callback
        self.ultimo_movimiento = "Sin novedades en el perímetro."
        self.ultimo_comando_voz = "Esperando instrucción de voz..."
        self.mostrar_mapa_tactico = False

        self.engine = None
        if TTS_DISPONIBLE and pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 178)
                self.engine.setProperty("volume", 1.0)
                self._seleccionar_voz_varonil()
            except Exception:
                self.engine = None

        self.recognizer = None
        if SR_DISPONIBLE and sr is not None:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.pause_threshold = 0.85
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
            except Exception:
                self.recognizer = None

        self.protocolos = {
            "protocolo extremo": (
                "Activando protocolo de conocimiento extremo, jefa. "
                "Procesando análisis profundo sin filtros de cortesía innecesarios."
            ),
            "mapa táctico satelital": (
                "Desplegando mapa táctico satelital en la consola, jefa. "
                "Coordenadas de Santiago y telemetría activas."
            ),
            "estado del sistema": (
                "Todos los núcleos operativos al cien por ciento. "
                "Aunque dudo que eso evite que me pida cinco cosas a la vez."
            ),
        }

    def _seleccionar_voz_varonil(self):
        if not self.engine:
            return
        try:
            voces = self.engine.getProperty("voices")
            for voz in voces:
                nombre = getattr(voz, "name", "").lower()
                if "sabina" not in nombre and any(
                    tag in nombre for tag in ["male", "raul", "pablo", "jorge", "david", "es", "spanish", "español"]
                ):
                    self.engine.setProperty("voice", voz.id)
                    break
        except Exception:
            pass

    def hablar(self, texto: str):
        """Habla en local si hay motor de audio y evita bucle con el micrófono."""
        if not self.engine or not texto:
            return
        self.hablando = True
        try:
            self.engine.say(texto)
            self.engine.runAndWait()
        except Exception:
            pass
        finally:
            self.hablando = False

    def procesar_intencion(self, texto: str) -> str:
        """Evalúa protocolos, mapa táctico satelital o responde con sarcasmo seco."""
        consulta = (texto or "").lower().strip()
        if not consulta:
            return ""

        if "mapa táctico satelital" in consulta or "mapa tactico satelital" in consulta or "mapa" in consulta:
            self.mostrar_mapa_tactico = True
            return self.protocolos["mapa táctico satelital"]

        for clave, respuesta in self.protocolos.items():
            if clave in consulta:
                return respuesta

        if "hola" in consulta or "jarvis" in consulta:
            return "Aquí estoy, jefa. ¿Qué brillante ocurrencia vamos a ejecutar ahora?"

        if "gracias" in consulta:
            return "No hay de qué. Alguien tiene que mantener este sistema funcionando."

        if self.on_command_callback:
            return self.on_command_callback(texto)

        return f"Orden recibida: '{texto}'. Procesando con mi habitual eficiencia sobrehumana."

    def iniciar_escucha_continua(self):
        """Hilo de conversación fluida manos libres (solo activo si hay micrófono disponible)."""
        if not self.recognizer or not SR_DISPONIBLE or sr is None:
            return

        def _loop_voz():
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.8)
                    while self.activo:
                        if self.hablando:
                            time.sleep(0.1)
                            continue
                        try:
                            audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=12)
                            texto = self.recognizer.recognize_google(audio, language="es-CL")
                            if texto:
                                self.ultimo_comando_voz = texto
                                respuesta = self.procesar_intencion(texto)
                                if respuesta:
                                    self.hablar(respuesta)
                        except Exception:
                            continue
            except Exception:
                return

        hilo = threading.Thread(target=_loop_voz, daemon=True)
        hilo.start()

    def iniciar_sensor_movimiento(self, indice_camara: int = 0, sensibilidad: int = 4500, cooldown: int = 20):
        """Sensor de movimiento silencioso por webcam (se omite si no hay cv2 o cámara)."""
        if not camara_disponible(indice_camara) or cv2 is None:
            return

        def _loop_camara():
            cap = cv2.VideoCapture(indice_camara)
            if not cap.isOpened():
                return

            try:
                ret, frame_anterior = cap.read()
                if not ret:
                    return

                gris_anterior = cv2.cvtColor(frame_anterior, cv2.COLOR_BGR2GRAY)
                gris_anterior = cv2.GaussianBlur(gris_anterior, (21, 21), 0)
                ultimo_aviso = 0

                while self.activo:
                    ret, frame = cap.read()
                    if not ret:
                        time.sleep(0.2)
                        continue

                    gris = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gris = cv2.GaussianBlur(gris, (21, 21), 0)

                    diferencia = cv2.absdiff(gris_anterior, gris)
                    umbral = cv2.threshold(diferencia, 25, 255, cv2.THRESH_BINARY)[1]
                    umbral = cv2.dilate(umbral, None, iterations=2)
                    contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                    movimiento_detectado = any(cv2.contourArea(c) > sensibilidad for c in contornos)
                    gris_anterior = gris

                    ahora = time.time()
                    if movimiento_detectado and (ahora - ultimo_aviso) > cooldown:
                        ultimo_aviso = ahora
                        self.ultimo_movimiento = f"Movimiento detectado ({time.strftime('%H:%M:%S')})"
                        if self.on_motion_callback:
                            self.on_motion_callback()
                        elif not self.hablando:
                            self.hablar("Sensor perimetral activado. Detecto movimiento en la sala, jefa.")

                    time.sleep(0.08)
            finally:
                cap.release()

        hilo_cam = threading.Thread(target=_loop_camara, daemon=True)
        hilo_cam.start()

    def detener(self):
        self.activo = False


# --- 1. CONFIGURACION DE PAGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

if "jarvis_core" not in st.session_state:
    core_instance = JarvisCoreEnhancements()
    core_instance.iniciar_escucha_continua()
    core_instance.iniciar_sensor_movimiento(indice_camara=0)
    st.session_state.jarvis_core = core_instance

jarvis_core = st.session_state.jarvis_core

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"

API_KEY_GROQ = ""
client_groq = None
if GROQ_AVAILABLE and API_KEY_GROQ:
    try:
        client_groq = Groq(api_key=API_KEY_GROQ)
    except Exception:

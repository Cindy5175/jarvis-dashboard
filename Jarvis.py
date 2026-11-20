import time
import threading

try:
    import cv2
    CV2_DISPONIBLE = True
except ModuleNotFoundError:
    cv2 = None
    CV2_DISPONIBLE = False

try:
    import speech_recognition as sr
    SR_DISPONIBLE = True
except ModuleNotFoundError:
    sr = None
    SR_DISPONIBLE = False

try:
    import pyttsx3
    TTS_DISPONIBLE = True
except ModuleNotFoundError:
    pyttsx3 = None
    TTS_DISPONIBLE = False


def camara_disponible(indice: int = 0) -> bool:
    """Verifica de forma segura si OpenCV y la cámara están operativos."""
    if not CV2_DISPONIBLE or cv2 is None:
        return False
    cap = cv2.VideoCapture(indice)
    disponible = cap.isOpened()
    cap.release()
    return disponible


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

        # 1. Inicialización segura de voz varonil
        self.engine = None
        if TTS_DISPONIBLE and pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 178)
                self.engine.setProperty("volume", 1.0)
                self._seleccionar_voz_varonil()
            except Exception:
                self.engine = None

        # 2. Inicialización segura de escucha continua
        self.recognizer = None
        if SR_DISPONIBLE and sr is not None:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.pause_threshold = 0.85
                self.recognizer.energy_threshold = 300
                self.recognizer.dynamic_energy_threshold = True
            except Exception:
                self.recognizer = None

        # 3. Protocolos de conocimiento extremo y comandos clave
        self.protocolos = {
            "protocolo extremo": (
                "Activando protocolo de conocimiento extremo, jefa. "
                "Procesando análisis profundo sin filtros de cortesía innecesarios."
            ),
            "mapa táctico satelital": (
                "Desplegando mapa táctico satelital en interfaz principal. "
                "Coordenadas y telemetría listas."
            ),
            "estado del sistema": (
                "Todos los núcleos operativos al cien por ciento. "
                "Aunque dudo que eso evite que me pida cinco cosas a la vez."
            ),
        }

    def _seleccionar_voz_varonil(self):
        if not self.engine:
            return
        voces = self.engine.getProperty("voices")
        for voz in voces:
            nombre = voz.name.lower()
            if "spanish" in nombre or "español" in nombre or "sabina" not in nombre:
                if any(tag in nombre for tag in ["male", "raul", "pablo", "jorge", "david", "es"]):
                    self.engine.setProperty("voice", voz.id)
                    break

    def hablar(self, texto: str):
        """Habla en local si hay motor de audio y evita bucle con el micrófono."""
        if not self.engine:
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
        consulta = texto.lower().strip()

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
                                respuesta = self.procesar_intencion(texto)
                                if respuesta:
                                    self.hablar(respuesta)
                        except (sr.WaitTimeoutError, sr.UnknownValueError):
                            continue
                        except Exception:
                            time.sleep(0.3)
            except Exception:
                # En entornos cloud sin micrófono físico sale silenciosamente sin romper la app
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

            ret, frame_anterior = cap.read()
            if not ret:
                cap.release()
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

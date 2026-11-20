import cv2
import time
import threading
import speech_recognition as sr
import pyttsx3


class JarvisCoreEnhancements:
    """
    Módulo unificado para JARVIS:
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

        # 1. Configuración de voz varonil y rápida
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 178)
        self.engine.setProperty("volume", 1.0)
        self._seleccionar_voz_varonil()

        # 2. Configuración de escucha continua
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 0.85
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

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
        voces = self.engine.getProperty("voices")
        for voz in voces:
            nombre = voz.name.lower()
            if "spanish" in nombre or "español" in nombre or "sabina" not in nombre:
                if any(tag in nombre for tag in ["male", "raul", "pablo", "jorge", "david", "es"]):
                    self.engine.setProperty("voice", voz.id)
                    break

    def hablar(self, texto: str):
        """Habla de forma fluida pausando temporalmente la autoescucha."""
        self.hablando = True
        try:
            self.engine.say(texto)
            self.engine.runAndWait()
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

        # Respuesta base para delegar al modelo conversacional con tono sarcástico
        if self.on_command_callback:
            return self.on_command_callback(texto)

        return f"Orden recibida: '{texto}'. Procesando con mi habitual eficiencia sobrehumana."

    def iniciar_escucha_continua(self):
        """Hilo de conversación fluida manos libres sin pulsar botones."""
        def _loop_voz():
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

        hilo = threading.Thread(target=_loop_voz, daemon=True)
        hilo.start()

    def iniciar_sensor_movimiento(self, indice_camara: int = 0, sensibilidad: int = 4500, cooldown: int = 20):
        """Sensor de movimiento silencioso por webcam sin alterar la estética de la UI."""
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
                    if self.on_motion_callback:
                        self.on_motion_callback()
                    elif not self.hablando:
                        self.hablar("Sensor perimetral activado. Detecto movimiento en la sala, jefa.")

                time.sleep(0.08)

            cap.release()

        hilo_cam = threading.Thread(target=_loop_camara, daemon=True)
        hilo_cam.start()

    def detener(self):
        self.activo = False


# Ejemplo de conexión limpia desde su jarvis.py o server.py:
if __name__ == "__main__":
    jarvis = JarvisCoreEnhancements()
    jarvis.iniciar_escucha_continua()
    jarvis.iniciar_sensor_movimiento(indice_camara=0)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        jarvis.detener()

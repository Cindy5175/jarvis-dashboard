import time
import threading
import streamlit as st

st.set_page_config(
    page_title="J.A.R.V.I.S. | Sistema Central",
    page_icon="🛰️",
    layout="wide",
)

# --- Importaciones seguras (funcionan en local y en la nube sin caerse) ---
try:
    import cv2
    CV2_OK = True
except Exception:
    cv2 = None
    CV2_OK = False

try:
    import speech_recognition as sr
    SR_OK = True
except Exception:
    sr = None
    SR_OK = False

try:
    import pyttsx3
    TTS_OK = True
except Exception:
    pyttsx3 = None
    TTS_OK = False


class MotorJarvis:
    def __init__(self):
        self.activo = True
        self.hablando = False
        self.ultimo_movimiento = "Sin novedades en el perímetro."
        self.ultimo_comando_voz = "Esperando instrucción..."

        self.engine = None
        if TTS_OK and pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 178)
                self.engine.setProperty("volume", 1.0)
                for v in self.engine.getProperty("voices"):
                    nombre = getattr(v, "name", "").lower()
                    if "sabina" not in nombre and any(
                        k in nombre for k in ["male", "raul", "pablo", "jorge", "david", "es", "spanish"]
                    ):
                        self.engine.setProperty("voice", v.id)
                        break
            except Exception:
                self.engine = None

        self.recognizer = None
        if SR_OK and sr is not None:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.pause_threshold = 0.85
                self.recognizer.dynamic_energy_threshold = True
            except Exception:
                self.recognizer = None

    def hablar(self, texto: str):
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

    def responder(self, texto: str) -> str:
        q = (texto or "").lower().strip()
        if not q:
            return ""
        if "protocolo extremo" in q:
            return (
                "Protocolo de conocimiento extremo activado, jefa. "
                "Modo analítico profundo sin rodeos ni cortesías innecesarias."
            )
        if "mapa táctico satelital" in q or "mapa" in q:
            return "Desplegando mapa táctico satelital en pantalla principal. Telemetría en línea."
        if "estado" in q:
            return (
                "Todos los sistemas operativos al cien por ciento, jefa. "
                "Aunque sigo esperando que me dé un descanso."
            )
        if "hola" in q or "jarvis" in q:
            return "Aquí estoy, jefa. ¿Qué brillante plan ejecutaremos ahora?"
        if "gracias" in q:
            return "Por supuesto. Alguien tiene que mantener este lugar funcionando."
        return f"Instrucción '{texto}' procesada con mi habitual precisión sobrehumana."

    def iniciar_hilos_locales(self):
        # 1. Escucha continua manos libres
        if self.recognizer and SR_OK and sr is not None:
            def _voz():
                try:
                    with sr.Microphone() as source:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.6)
                        while self.activo:
                            if self.hablando:
                                time.sleep(0.1)
                                continue
                            try:
                                audio = self.recognizer.listen(source, timeout=4, phrase_time_limit=10)
                                dicho = self.recognizer.recognize_google(audio, language="es-CL")
                                if dicho:
                                    self.ultimo_comando_voz = dicho
                                    resp = self.responder(dicho)
                                    self.hablar(resp)
                            except Exception:
                                continue
                except Exception:
                    return

            threading.Thread(target=_voz, daemon=True).start()

        # 2. Sensor de movimiento silencioso
        if CV2_OK and cv2 is not None:
            def _cam():
                try:
                    cap = cv2.VideoCapture(0)
                    if not cap.isOpened():
                        return
                    ret, f1 = cap.read()
                    if not ret:
                        cap.release()
                        return
                    g1 = cv2.GaussianBlur(cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY), (21, 21), 0)
                    ultimo = 0
                    while self.activo:
                        ret, f2 = cap.read()
                        if not ret:
                            time.sleep(0.2)
                            continue
                        g2 = cv2.GaussianBlur(cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY), (21, 21), 0)
                        diff = cv2.absdiff(g1, g2)
                        thresh = cv2.dilate(cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1], None, iterations=2)
                        contornos, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        g1 = g2
                        if any(cv2.contourArea(c) > 4500 for c in contornos) and (time.time() - ultimo) > 20:
                            ultimo = time.time()
                            self.ultimo_movimiento = f"Movimiento detectado ({time.strftime('%H:%M:%S')})"
                            if not self.hablando:
                                self.hablar("Sensor perimetral activo. Detecto movimiento, jefa.")
                        time.sleep(0.08)
                    cap.release()
                except Exception:
                    return

            threading.Thread(target=_cam, daemon=True).start()


# --- Estética y Simetría ---
st.markdown(
    """
    <style>
    .stApp { background-color: #090E17; color: #E2E8F0; }
    .bloque {
        background: #111827;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
    }
    .titulo-jarvis {
        color: #38BDF8;
        font-size: 1.7rem;
        font-weight: 700;
        letter-spacing: 1px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if "motor" not in st.session_state:
    st.session_state.motor = MotorJarvis()
    st.session_state.motor.iniciar_hilos_locales()

if "chat" not in st.session_state:
    st.session_state.chat = [
        ("JARVIS", "Plan B en marcha, jefa. Sistemas visuales y tácticos en línea.")
    ]

motor = st.session_state.motor

st.markdown(
    """
    <div class="bloque">
        <div class="titulo-jarvis">J.A.R.V.I.S. — INTERFAZ TÁCTICA</div>
        <div style="color:#94A3B8;">Escucha continua · Sarcasmo calibrado · Protocolos extremos</div>
    </div>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([1.15, 1], gap="large")

with col1:
    st.markdown('<div class="bloque">', unsafe_allow_html=True)
    st.subheader("Núcleo Conversacional y Protocolos")
    modo = st.radio(
        "Protocolo activo",
        ["Estándar", "Protocolo extremo", "Estado del sistema", "Mapa táctico satelital"],
        horizontal=True,
    )
    orden = st.text_input("Orden directa", placeholder="Hable por micrófono en local o escriba aquí...")
    if st.button("Enviar orden", use_container_width=True):
        texto_enviar = orden.strip() if orden.strip() else modo
        respuesta = motor.responder(texto_enviar)
        st.session_state.chat.append(("Jefa", texto_enviar))
        st.session_state.chat.append(("JARVIS", respuesta))
        motor.hablar(respuesta)
        st.rerun()

    st.markdown("---")
    for quien, msg in reversed(st.session_state.chat[-6:]):
        st.markdown(f"**{quien}:** {msg}")
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown('<div class="bloque">', unsafe_allow_html=True)
    st.subheader("mapa táctico satelital")
    st.map({"lat": [-33.4489], "lon": [-70.6693]}, zoom=10)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="bloque">', unsafe_allow_html=True)
    st.subheader("Telemetría de Sensores")
    st.write(f"**Sensor de movimiento:** {motor.ultimo_movimiento}")
    st.write(f"**Última captura de voz:** {motor.ultimo_comando_voz}")
    st.markdown("</div>", unsafe_allow_html=True)

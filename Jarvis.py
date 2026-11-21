import os
import re
import streamlit as st
import datetime
import sqlite3
import requests
import random
import time
import threading

try:
    from memoria_loader import obtener_memoria_completa
except Exception:
    def obtener_memoria_completa() -> str:
        return ""

try:
    from modulo_ingles import detectar_solicitud_idioma, responder_en_ingles
except Exception:
    def detectar_solicitud_idioma(texto: str) -> str:
        t = (texto or "").lower()
        pistas_en = [
            "in english", "speak english", "reply in english",
            "hello", "hi ", "hi!", "hey", "what ", "how ", "status", "check"
        ]
        return "en" if any(p in t for p in pistas_en) else "es"

    def responder_en_ingles(texto: str) -> str:
        return (
            f"Understood, Boss. Processing '{texto}' in English—"
            "try not to make me switch back just because you run out of vocabulary."
        )


def _resolver_respuesta_bilingue_y_memoria(mensaje_usuario: str, memoria_txt: str = "") -> str | None:
    """Devuelve respuesta en inglés si aplica, o apoyo de memoria si se consulta; None para dejar pasar tu flujo normal."""
    if not mensaje_usuario:
        return None
    if detectar_solicitud_idioma(mensaje_usuario) == "en":
        return responder_en_ingles(mensaje_usuario)

    t = mensaje_usuario.lower().strip()
    if ("cumpleaños" in t or "memoria" in t or "recuerdas" in t) and memoria_txt:
        return (
            "Señorita, tengo la memoria cargada y disponible en el panel correspondiente. "
            "Si gusta, continúo con el resto de sus órdenes."
        )
    return None


try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

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


def camara_disponible(indice: int = 0) -> bool:
    if not CV2_OK or cv2 is None:
        return False
    try:
        cap = cv2.VideoCapture(indice)
        ok = cap.isOpened()
        cap.release()
        return ok
    except Exception:
        return False


def limpiar_texto_para_voz(texto: str) -> str:
    if not texto:
        return ""
    limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace táctico ", texto)
    limpio = re.sub(r"https?://\S+", " enlace táctico ", limpio)
    limpio = re.sub(r"\[[^\]]+\]", "", limpio)
    limpio = re.sub(r"[*_`#]+", "", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio


def hablar_en_navegador(texto: str):
    limpio = (
        limpiar_texto_para_voz(texto)
        .replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace('"', '\\"')
        .replace("\n", " ")
    )
    if not limpio:
        return
    html_voz = f"""
    <script>
      (function() {{
        try {{
          if ("speechSynthesis" in window) {{
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance("{limpio}");
            utter.lang = "es-CL";
            utter.rate = 1.0;
            utter.pitch = 0.92;
            const voces = window.speechSynthesis.getVoices() || [];
            const vozEs = voces.find(v => (v.lang || "").toLowerCase().startsWith("es"));
            if (vozEs) utter.voice = vozEs;
            window.speechSynthesis.speak(utter);
          }}
        }} catch (e) {{}}
      }})();
    </script>
    """
    st.components.v1.html(html_voz, height=0)


class JarvisCoreEnhancements:
    def __init__(self):
        self.activo = True
        self.hablando = False
        self.ultimo_movimiento = "Sin novedades en el perímetro."
        self.ultimo_comando_voz = "Esperando instrucción de voz..."
        self.mostrar_mapa_tactico = False
        self.ojo_de_dios_activo = False
        self.camara_seleccionada = "CAM-01 // PERÍMETRO NODO BUIN"
        self.stream_url = ""
        self._voz_lock = threading.Lock()

        self.engine = None
        if TTS_OK and pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self._configurar_voz_varonil()
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

    def _configurar_voz_varonil(self):
        if not self.engine:
            return
        try:
            self.engine.setProperty("rate", 166)
            self.engine.setProperty("volume", 0.95)
            voces = self.engine.getProperty("voices") or []
            candidatas_varoniles = []
            candidatas_espanol = []
            excluir = ("sabina", "helena", "zira", "hazel", "female", "mujer", "sofia", "sofía", "lucia", "lucía")

            for voz in voces:
                nombre = getattr(voz, "name", "").lower()
                vid = getattr(voz, "id", "").lower()
                info = f"{nombre} {vid}"
                if any(bad in info for bad in excluir):
                    continue
                if any(m in info for m in ["male", "raul", "raúl", "pablo", "jorge", "david", "diego", "carlos", "enrique", "alvaro", "álvaro"]):
                    candidatas_varoniles.append(voz)
                elif any(es in info for es in ["es-cl", "es-es", "es-mx", "es_cl", "es_es", "spanish", "castellano", "chile"]):
                    candidatas_espanol.append(voz)

            elegida = None
            if candidatas_varoniles:
                elegida = candidatas_varoniles[0]
            elif candidatas_espanol:
                elegida = candidatas_espanol[0]

            if elegida is not None:
                self.engine.setProperty("voice", elegida.id)
        except Exception:
            pass

    def asegurar_atributos(self):
        defaults = {
            "activo": True,
            "hablando": False,
            "ultimo_movimiento": "Sin novedades en el perímetro.",
            "ultimo_comando_voz": "Esperando instrucción de voz...",
            "mostrar_mapa_tactico": False,
            "ojo_de_dios_activo": False,
            "camara_seleccionada": "CAM-01 // PERÍMETRO NODO BUIN",
            "stream_url": "",
        }
        for k, v in defaults.items():
            if not hasattr(self, k):
                setattr(self, k, v)
        if not hasattr(self, "_voz_lock"):
            self._voz_lock = threading.Lock()

    def hablar(self, texto: str):
        if not getattr(self, "engine", None) or not texto:
            return
        frase = limpiar_texto_para_voz(texto)
        if not frase:
            return
        with self._voz_lock:
            self.hablando = True
            try:
                self._configurar_voz_varonil()
                self.engine.say(frase)
                self.engine.runAndWait()
            except Exception:
                pass
            finally:
                self.hablando = False

    def iniciar_hilos(self):
        if self.recognizer and SR_OK and sr is not None:
            def _voz():
                try:
                    with sr.Microphone() as src:
                        self.recognizer.adjust_for_ambient_noise(src, duration=0.8)
                        while self.activo:
                            if self.hablando:
                                time.sleep(0.12)
                                continue
                            try:
                                audio = self.recognizer.listen(src, timeout=4, phrase_time_limit=12)
                                dicho = self.recognizer.recognize_google(audio, language="es-CL")
                                if dicho:
                                    self.ultimo_comando_voz = dicho
                                    if "mapa" in dicho.lower():
                                        self.mostrar_mapa_tactico = True
                                        self.hablar("Sí, señorita.")
                                    else:
                                        self.hablar(f"Recibido, señorita: {dicho}.")
                            except Exception:
                                continue
                except Exception:
                    return
            threading.Thread(target=_voz, daemon=True).start()

        if camara_disponible(0) and cv2 is not None:
            def _cam():
                cap = cv2.VideoCapture(0)
                if not cap.isOpened():
                    return
                try:
                    ret, f1 = cap.read()
                    if not ret:
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
                        umbral = cv2.dilate(cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1], None, iterations=2)
                        contornos, _ = cv2.findContours(umbral, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                        g1 = g2
                        if any(cv2.contourArea(c) > 4500 for c in contornos) and (time.time() - ultimo) > 20:
                            ultimo = time.time()
                            self.ultimo_movimiento = f"Movimiento detectado ({time.strftime('%H:%M:%S')})"
                            if not self.hablando:
                                self.hablar("Sensor perimetral activo. Detecto movimiento, señorita.")
                        time.sleep(0.08)
                finally:
                    cap.release()
            threading.Thread(target=_cam, daemon=True).start()


st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False
if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"
if "ver_mapa" not in st.session_state:
    st.session_state.ver_mapa = False
if "ver_ojo_dios" not in st.session_state:
    st.session_state.ver_ojo_dios = False
if "voz_pendiente" not in st.session_state:
    st.session_state.voz_pendiente = ""
if "jarvis_core" not in st.session_state:
    c_obj = JarvisCoreEnhancements()
    c_obj.iniciar_hilos()
    st.session_state.jarvis_core = c_obj

jarvis_core = st.session_state.jarvis_core
if hasattr(jarvis_core, "asegurar_atributos"):
    jarvis_core.asegurar_atributos()
else:
    for _k, _v in {
        "ojo_de_dios_activo": False,
        "camara_seleccionada": "CAM-01 // PERÍMETRO NODO BUIN",
        "stream_url": "",
        "mostrar_mapa_tactico": False,
        "ultimo_movimiento": "Sin novedades en el perímetro.",
        "hablando": False,
    }.items():
        if not hasattr(jarvis_core, _k):
            setattr(jarvis_core, _k, _v)

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"
OSIRIS_URL = "https://osirisai.live/"
GROQ_MODELO_ACTIVO = "openai/gpt-oss-120b"

api_key_groq = ""
try:
    api_key_groq = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    api_key_groq = ""
if not api_key_groq:
    api_key_groq = os.environ.get("GROQ_API_KEY", "")

client_groq = None
if GROQ_AVAILABLE and api_key_groq:
    try:
        client_groq = Groq(api_key=api_key_groq)
    except Exception:
        client_groq = None


def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS misiones (id INTEGER PRIMARY KEY AUTOINCREMENT, tarea TEXT NOT NULL, estado TEXT DEFAULT 'Pendiente')")
    cur.execute("CREATE TABLE IF NOT EXISTS memory (key_id TEXT PRIMARY KEY, fact_text TEXT, category TEXT)")
    conn.commit()
    conn.close()


init_db()


def guardar_memoria(fact_text: str, category: str = "general"):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    conn.cursor().execute(
        "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
        (f"mem_{datetime.datetime.now().timestamp()}", fact_text, category)
    )
    conn.commit()
    conn.close()


def obtener_memorias(limite: int = 5):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    rows = conn.cursor().execute("SELECT fact_text, category FROM memory ORDER BY key_id DESC LIMIT ?", (limite,)).fetchall()
    conn.close()
    return rows


def olvidar_memoria(fragmento: str) -> int:
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cur = conn.cursor()
    cur.execute("DELETE FROM memory WHERE LOWER(fact_text) LIKE ?", (f"%{fragmento.lower()}%",))
    eliminados = cur.rowcount

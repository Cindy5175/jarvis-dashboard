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

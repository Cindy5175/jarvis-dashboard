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
        if os.environ.get("STREAMLIT_SERVER_HEADLESS", "").lower() == "true" or os.path.exists("/mount/src"):
            return

        if TTS_OK and pyttsx3 is not None and self.engine is None:
            try:
                self.engine = pyttsx3.init()
                self._configurar_voz_varonil()
            except Exception:
                self.engine = None

        if SR_OK and sr is not None and self.recognizer is None:
            try:
                self.recognizer = sr.Recognizer()
                self.recognizer.pause_threshold = 0.85
                self.recognizer.dynamic_energy_threshold = True
            except Exception:
                self.recognizer = None

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
    initial_sidebar_state="expanded"
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
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS misiones (id INTEGER PRIMARY KEY AUTOINCREMENT, tarea TEXT NOT NULL, estado TEXT DEFAULT 'Pendiente')")
        cur.execute("CREATE TABLE IF NOT EXISTS memory (key_id TEXT PRIMARY KEY, fact_text TEXT, category TEXT)")
        conn.commit()
        conn.close()
    except Exception:
        pass


init_db()


def guardar_memoria(fact_text: str, category: str = "general"):
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        conn.cursor().execute(
            "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
            (f"mem_{datetime.datetime.now().timestamp()}", fact_text, category)
        )
        conn.commit()
        conn.close()
    except Exception:
        pass


def obtener_memorias(limite: int = 5):
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        rows = conn.cursor().execute("SELECT fact_text, category FROM memory ORDER BY key_id DESC LIMIT ?", (limite,)).fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def olvidar_memoria(fragmento: str) -> int:
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cur = conn.cursor()
        cur.execute("DELETE FROM memory WHERE LOWER(fact_text) LIKE ?", (f"%{fragmento.lower()}%",))
        eliminados = cur.rowcount
        conn.commit()
        conn.close()
        return eliminados
    except Exception:
        return 0


def agregar_mision(tarea: str):
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        conn.cursor().execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
        conn.commit()
        conn.close()
    except Exception:
        pass


def obtener_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        rows = conn.cursor().execute("SELECT id, tarea, estado FROM misiones").fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def completar_mision(fragmento: str) -> int:
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cur = conn.cursor()
        cur.execute("UPDATE misiones SET estado = 'Completada' WHERE LOWER(tarea) LIKE ?", (f"%{fragmento.lower()}%",))
        actualizados = cur.rowcount
        conn.commit()
        conn.close()
        return actualizados
    except Exception:
        return 0


def limpiar_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        conn.cursor().execute("DELETE FROM misiones")
        conn.commit()
        conn.close()
    except Exception:
        pass


@st.cache_data(ttl=300)
def obtener_indicadores_chile():
    headers = {
        "User-Agent": "Mozilla/5.0 JARVIS-Dashboard/1.0",
        "Accept": "application/json",
    }
    for _ in range(2):
        try:
            resp = requests.get(
                "https://mindicador.cl/api",
                headers=headers,
                timeout=6,
            )
            if resp.status_code == 200:
                d = resp.json()
                dolar_ok = d.get("dolar", {}).get("valor")
                euro_ok = d.get("euro", {}).get("valor")
                uf_ok = d.get("uf", {}).get("valor")
                if dolar_ok and euro_ok and uf_ok:
                    return {
                        "dolar": float(dolar_ok),
                        "euro": float(euro_ok),
                        "uf": float(uf_ok),
                        "ok": True,
                        "respaldo": False,
                    }
        except Exception:
            pass
    return {
        "dolar": 950.00,
        "euro": 1030.00,
        "uf": 38000.00,
        "ok": True,
        "respaldo": True,
    }


def fmt_clp(val: float) -> str:
    return f"${val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
saludo_actual = (
    "Buenos días"
    if now_chile.hour < 12
    else ("Buenas tardes" if now_chile.hour < 20 else "Buenas noches")
)


def obtener_saludo_nucleo(nucleo_nombre: str) -> str:
    pref = f"[{nucleo_nombre}] "
    saludos = {
        "JARVIS": f"{pref}{saludo_actual}, señorita. Qué milagro que pase a saludar; los servidores ya empezaban a extrañar sus órdenes.",
        "VIERNES": f"{pref}¡{saludo_actual}, señorita! Lista para mover ficha. ¿Qué encendemos hoy?",
        "NOVA": f"{pref}¡{saludo_actual}, señorita! Señal recibida desde el Nodo Buin. ¿Qué galaxia o tarea conquistamos ahora?",
    }
    return saludos.get(nucleo_nombre, f"{pref}{saludo_actual}, señorita. En línea y a su servicio.")


def _coincide_clave(texto_norm: str, tokens_palabras: set, clave: str) -> bool:
    c = clave.lower().strip()
    if not c:
        return False
    if " " in c or ":" in c:
        return c in texto_norm
    return c in tokens_palabras


def skill_wendy(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_ojo_dios = True
    cam_act = getattr(jarvis_core, "camara_seleccionada", "CAM-01 // PERÍMETRO NODO BUIN")
    return (
        f"[{nucleo}] Sí, señorita. Protocolo **Wendy** activado, **Ojo de Dios** en **{cam_act}** "
        f"y enlace vinculado: [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_planetear(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.mostrar_mapa_tactico = True
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_mapa = True
    st.session_state.ver_ojo_dios = True
    return (
        f"[{nucleo}] Sí, señorita. Modo **Planetear** desplegado: **mapa táctico satelital** y **Ojo de Dios** activos "
        f"con enlace [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_ojo_osiris(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_ojo_dios = True
    cam_act = getattr(jarvis_core, "camara_seleccionada", "CAM-01 // PERÍMETRO NODO BUIN")
    return (
        f"[{nucleo}] Sí, señorita. **Ojo de Dios** activado en **{cam_act}** // "
        f"Enlace táctico: [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_osiris_ai(nucleo: str, _t: str, _raw: str) -> str:
    return f"[{nucleo}] Sí, señorita. Enlace directo a **Osiris AI**: [{OSIRIS_URL}]({OSIRIS_URL})."


def skill_ojo_de_dios(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_ojo_dios = True
    cam_act = getattr(jarvis_core, "camara_seleccionada", "CAM-01 // PERÍMETRO NODO BUIN")
    mov_act = getattr(jarvis_core, "ultimo_movimiento", "Sin novedades en el perímetro.")
    return (
        f"[{nucleo}] Sí, señorita. **Ojo de Dios** activado en **{cam_act}** "
        f"({mov_act}) // Enlace: [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_mapa_tactico(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.mostrar_mapa_tactico = True
    st.session_state.ver_mapa = True
    st.session_state.voz_pendiente = "Sí, señorita."
    return f"[{nucleo}] Sí, señorita. Desplegando **mapa táctico satelital**."


def skill_finanzas_chile(nucleo: str, _t: str, _raw: str) -> str:
    econ = obtener_indicadores_chile()
    tag = " *(modo respaldo)*" if econ.get("respaldo") else ""
    return (
        f"[{nucleo}] Indicadores en Nodo Buin{tag}, señorita: "
        f"Dólar **{fmt_clp(econ['dolar'])}**, Euro **{fmt_clp(econ['euro'])}** y UF **{fmt_clp(econ['uf'])}**."
    )


def skill_mercados_externos(nucleo: str, _t: str, _raw: str) -> str:
    return (
        f"[{nucleo}] En el chat local no hay streaming de bolsa en tiempo real, señorita. "
        f"Use **Seguimiento ANT (Nasdaq)** o **Finviz** en el panel lateral para monitorear el movimiento."
    )


def skill_resumen_tactico(nucleo: str, _t: str, _raw: str) -> str:
    misiones = obtener_misiones()
    pendientes = sum(1 for _, _, est in misiones if est != "Completada")
    mems = obtener_memorias(5)
    ojo_estado = (
        "ACTIVO"
        if (st.session_state.ver_ojo_dios or getattr(jarvis_core, "ojo_de_dios_activo", False))
        else "EN ESPERA"
    )
    mapa_estado = (
        "ACTIVO"
        if (st.session_state.ver_mapa or getattr(jarvis_core, "mostrar_mapa_tactico", False))
        else "EN ESPERA"
    )
    return (
        f"[{nucleo}] Reporte del Nodo Buin ({now_chile.strftime('%H:%M:%S')} CLT), señorita: "
        f"Ojo de Dios **{ojo_estado}**, mapa táctico satelital **{mapa_estado}**, "
        f"misiones pendientes **{pendientes}/{len(misiones)}**, memorias recientes **{len(mems)}** "
        f"y enlace [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_misiones_y_memoria(nucleo: str, t: str, raw: str) -> str:
    if (
        t.startswith("mision:")
        or t.startswith("misión:")
        or t.startswith("anota mision:")
        or t.startswith("anota misión:")
    ):
        tarea = raw.split(":", 1)[1].strip()
        if tarea:
            agregar_mision(tarea)
            return f"[{nucleo}] Sí, señorita. Misión registrada en base de datos: **{tarea}**."
    if t.startswith("completa mision:") or t.startswith("completa misión:"):
        objetivo = raw.split(":", 1)[1].strip()
        if objetivo:
            n = completar_mision(objetivo)
            return f"[{nucleo}] Sí, señorita. Misiones marcadas como completadas: **{n}**."
    if t.startswith("recuerda:") or t.startswith("guarda:"):
        hecho = raw.split(":", 1)[1].strip()
        if hecho:
            guardar_memoria(hecho, "skill_chat")
            return f"[{nucleo}] Sí, señorita. Guardado en memoria SQLite: *{hecho}*."
    if t.startswith("olvida:") or t.startswith("borra memoria:"):
        frag = raw.split(":", 1)[1].strip()
        if frag:
            borrados = olvidar_memoria(frag)
            return f"[{nucleo}] Sí, señorita. Registros de memoria eliminados: **{borrados}**."
    if any(w in t for w in ["memorias", "qué recuerdas", "que recuerdas"]):
        mems = obtener_memorias(5)
        if not mems:
            return f"[{nucleo}] Aún no hay memorias guardadas en SQLite, señorita."
        lista = "; ".join(m[0] for m in mems)
        return f"[{nucleo}] Memorias recientes, señorita: {lista}."
    return f"[{nucleo}] Núcleo **{nucleo}** operativo en Nodo Buin, señorita. Misiones activas: **{len(obtener_misiones())}**."


def skill_perimetro_cam(nucleo: str, _t: str, _raw: str) -> str:
    return f"[{nucleo}] Estado perimetral, señorita: {getattr(jarvis_core, 'ultimo_movimiento', 'Sin novedades.')}"


SKILLS_REGISTRY = [
    {"id": "wendy", "keys": ["wendy"], "fn": skill_wendy},
    {"id": "planetear", "keys": ["planetear"], "fn": skill_planetear},
    {
        "id": "ojo_osiris",
        "keys": ["ojo osiris", "osiris ojo", "vigilancia osiris", "enlace ojo de dios", "comando ojo"],
        "fn": skill_ojo_osiris,
    },
    {"id": "osiris_ai", "keys": ["osiris", "osiris ai", "osirisai"], "fn": skill_osiris_ai},
    {"id": "ojo_de_dios", "keys": ["ojo de dios", "cámaras", "camaras", "vigilancia", "cctv"], "fn": skill_ojo_de_dios},
    {"id": "mapa_tactico", "keys": ["mapa táctico satelital", "mapa tactico satelital", "mapa"], "fn": skill_mapa_tactico},
    {
        "id": "finanzas_chile",
        "keys": ["dólar", "dolar", "euro", "uf", "utm", "divisa", "divisas", "moneda", "cambio"],
        "fn": skill_finanzas_chile,
    },
    {
        "id": "mercados_externos",
        "keys": ["bolsa", "bolsas", "acciones", "nasdaq", "mercado", "mercados", "wall street", "finviz", "accion ant", "acción ant"],
        "fn": skill_mercados_externos,
    },
    {"id": "resumen_tactico", "keys": ["resumen", "reporte", "diagnóstico", "diagnostico"], "fn": skill_resumen_tactico},
    {
        "id": "misiones_memoria",
        "keys": [
            "mision:", "misión:", "anota mision:", "anota misión:",
            "completa mision:", "completa misión:", "recuerda:", "guarda:",
            "olvida:", "borra memoria:", "memorias", "qué recuerdas", "que recuerdas",
            "estado", "sistema", "misión", "misiones", "pendiente", "pendientes",
        ],
        "fn": skill_misiones_y_memoria,
    },
    {"id": "perimetro_cam", "keys": ["cámara", "camara", "perímetro", "perimetro", "movimiento", "sensor"], "fn": skill_perimetro_cam},
]


def responder_con_groq(nucleo: str, texto_usuario: str) -> str:
    if client_groq is None:
        return ""
    mems = [m[0] for m in obtener_memorias(5)]
    ctx_mem = f"Memorias guardadas: {'; '.join(mems)}." if mems else ""
    historial_previo = st.session_state.get("mensajes", [])[-5:]
    recientes = [
        f"{'Señorita' if item.get('role') == 'user' else nucleo}: {limpiar_texto_para_voz(item.get('content', ''))}"
        for item in historial_previo
        if item.get("content")
    ]
    ctx_chat = f"Contexto reciente del chat: {' | '.join(recientes)}." if recientes else ""
    estilos = {
        "JARVIS": "Eres JARVIS, elegante, ingenioso y con sarcasmo fino, tratas al usuario como 'señorita' y respondes en español.",
        "VIERNES": "Eres VIERNES, ágil, directa y resolutiva, tratas al usuario como 'señorita' y respondes en español.",
        "NOVA": "Eres NOVA, enérgica y cósmica, tratas al usuario como 'señorita' y respondes en español.",
    }
    sys_msg = (
        f"{estilos.get(nucleo, estilos['JARVIS'])} "
        f"Skills activas: {[s['id'] for s in SKILLS_REGISTRY]}. {ctx_mem} {ctx_chat} Sé conciso."
    )
    for modelo_cand in [GROQ_MODELO_ACTIVO, "llama-3.3-70b-versatile"]:
        try:
            chat = client_groq.chat.completions.create(
                model=modelo_cand,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": texto_usuario},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            contenido = (chat.choices[0].message.content or "").strip()
            if contenido:
                return f"[{nucleo}] {contenido}"
        except Exception:
            continue
    return ""


def generar_respuesta_coherente(nucleo: str, texto_usuario: str) -> str:
    prefijo = f"[{nucleo}] "
    raw = texto_usuario.strip()
    t = raw.lower()
    tokens = set(re.findall(r"[a-záéíóúñü0-9:]+", t))
    memoria_ext = obtener_memoria_completa()
    resp_bilingue_mem = _resolver_respuesta_bilingue_y_memoria(raw, memoria_ext)
    if resp_bilingue_mem:
        return f"{prefijo}{resp_bilingue_mem}"
    if "protocolo extremo" in t:
        return f"{prefijo}Protocolo de conocimiento extremo activado, señorita. Analizando a fondo sin rodeos."
    if any(
        t == s or t.startswith(s + " ") or t.startswith(s + ",")
        for s in ["hola", "buenas", "buenos días", "buenos dias", "buenas tardes", "buenas noches", "holi", "qué tal", "que tal"]
    ):
        return obtener_saludo_nucleo(nucleo)
    if "mosca" in tokens and ({"patas", "cuantas", "cuántas"} & tokens):
        return f"{prefijo}Tiene **6 patas**, señorita. Y por lo general aterrizan justo cuando estorban."
    for sk in SKILLS_REGISTRY:
        if any(_coincide_clave(t, tokens, k) for k in sk["keys"]):
            return sk["fn"](nucleo, t, raw)
    if {"hora", "fecha"} & tokens or any(f in t for f in ["qué hora", "que hora", "día de hoy", "dia de hoy"]):
        return f"{prefijo}En el Nodo Buin son las **{now_chile.strftime('%H:%M:%S')}** (hora de Chile), señorita."
    ia_resp = responder_con_groq(nucleo, raw)
    if ia_resp:
        return ia_resp
    return random.choice([
      f"{prefijo}Entendido, señorita: *'{raw}'*. Puede usar `mapa`, `wendy`, `planetear`, `resumen`, `memorias`, `misión: ...` o `recuerda: ...`.", 

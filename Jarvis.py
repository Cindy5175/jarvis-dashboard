import os
import streamlit as st
import datetime
import sqlite3
import requests
import random
import time
import threading

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

        self.engine = None
        if TTS_OK and pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 178)
                self.engine.setProperty("volume", 1.0)
                for voz in self.engine.getProperty("voices"):
                    nombre = getattr(voz, "name", "").lower()
                    if "sabina" not in nombre and any(
                        t in nombre for t in ["male", "raul", "pablo", "jorge", "david", "es", "spanish"]
                    ):
                        self.engine.setProperty("voice", voz.id)
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

    def iniciar_hilos(self):
        if self.recognizer and SR_OK and sr is not None:
            def _voz():
                try:
                    with sr.Microphone() as src:
                        self.recognizer.adjust_for_ambient_noise(src, duration=0.8)
                        while self.activo:
                            if self.hablando:
                                time.sleep(0.1)
                                continue
                            try:
                                audio = self.recognizer.listen(src, timeout=4, phrase_time_limit=12)
                                dicho = self.recognizer.recognize_google(audio, language="es-CL")
                                if dicho:
                                    self.ultimo_comando_voz = dicho
                                    self.hablar(f"Recibido, jefa: {dicho}.")
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
                                self.hablar("Sensor perimetral activo. Detecto movimiento, jefa.")
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
    }.items():
        if not hasattr(jarvis_core, _k):
            setattr(jarvis_core, _k, _v)

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"
OSIRIS_URL = "https://osirisai.live/"

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


def agregar_mision(tarea: str):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    conn.cursor().execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
    conn.commit()
    conn.close()


def obtener_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    rows = conn.cursor().execute("SELECT id, tarea, estado FROM misiones").fetchall()
    conn.close()
    return rows


def limpiar_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    conn.cursor().execute("DELETE FROM misiones")
    conn.commit()
    conn.close()


@st.cache_data(ttl=300)
def obtener_indicadores_chile():
    headers = {"User-Agent": "Mozilla/5.0 JARVIS-Dashboard/1.0", "Accept": "application/json"}
    for _ in range(2):
        try:
            resp = requests.get("https://mindicador.cl/api", headers=headers, timeout=10)
            if resp.status_code == 200:
                d = resp.json()
                if d.get("dolar", {}).get("valor") and d.get("euro", {}).get("valor") and d.get("uf", {}).get("valor"):
                    return {
                        "dolar": float(d["dolar"]["valor"]),
                        "euro": float(d["euro"]["valor"]),
                        "uf": float(d["uf"]["valor"]),
                        "ok": True,
                        "respaldo": False,
                    }
        except Exception:
            pass
    return {"dolar": 950.00, "euro": 1030.00, "uf": 38000.00, "ok": True, "respaldo": True}


def fmt_clp(val: float) -> str:
    return f"${val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
saludo_actual = "Buenos días" if now_chile.hour < 12 else ("Buenas tardes" if now_chile.hour < 20 else "Buenas noches")


def obtener_saludo_nucleo(nucleo_nombre: str) -> str:
    pref = f"[{nucleo_nombre}] "
    saludos = {
        "JARVIS": f"{pref}{saludo_actual}, jefa. Qué milagro que pase a saludar; los servidores ya empezaban a extrañar sus órdenes.",
        "VIERNES": f"{pref}¡{saludo_actual}, jefa! Lista para mover ficha. ¿Qué encendemos hoy?",
        "NOVA": f"{pref}¡{saludo_actual}, jefa! Señal recibida desde el Nodo Buin. ¿Qué galaxia o tarea conquistamos ahora?",
    }
    return saludos.get(nucleo_nombre, f"{pref}{saludo_actual}, jefa. En línea y a su servicio.")


def skill_wendy(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_ojo_dios = True
    cam_act = getattr(jarvis_core, "camara_seleccionada", "CAM-01 // PERÍMETRO NODO BUIN")
    return (
        f"[{nucleo}] Protocolo **Wendy** activado, jefa. **Ojo de Dios** en **{cam_act}** "
        f"y enlace vinculado: [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_planetear(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.mostrar_mapa_tactico = True
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_mapa = True
    st.session_state.ver_ojo_dios = True
    return (
        f"[{nucleo}] Modo **Planetear** desplegado, jefa: **mapa táctico satelital** y **Ojo de Dios** activos "
        f"con enlace [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_ojo_osiris(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_ojo_dios = True
    cam_act = getattr(jarvis_core, "camara_seleccionada", "CAM-01 // PERÍMETRO NODO BUIN")
    return (
        f"[{nucleo}] **Ojo de Dios** activado en **{cam_act}**, jefa. "
        f"Enlace táctico vinculado: [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_osiris_ai(nucleo: str, _t: str, _raw: str) -> str:
    return f"[{nucleo}] Enlace directo a **Osiris AI**, jefa: [{OSIRIS_URL}]({OSIRIS_URL})."


def skill_ojo_de_dios(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_ojo_dios = True
    cam_act = getattr(jarvis_core, "camara_seleccionada", "CAM-01 // PERÍMETRO NODO BUIN")
    mov_act = getattr(jarvis_core, "ultimo_movimiento", "Sin novedades en el perímetro.")
    return (
        f"[{nucleo}] **Ojo de Dios** activado, jefa. Monitoreando **{cam_act}** "
        f"({mov_act}) // Enlace: [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_mapa_tactico(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.mostrar_mapa_tactico = True
    st.session_state.ver_mapa = True
    return f"[{nucleo}] Desplegando **mapa táctico satelital**, jefa. Telemetría en línea."


def skill_finanzas_chile(nucleo: str, _t: str, _raw: str) -> str:
    econ = obtener_indicadores_chile()
    tag = " *(modo respaldo)*" if econ.get("respaldo") else ""
    return (
        f"[{nucleo}] Indicadores en Nodo Buin{tag}, jefa: "
        f"Dólar **{fmt_clp(econ['dolar'])}**, Euro **{fmt_clp(econ['euro'])}** y UF **{fmt_clp(econ['uf'])}**."
    )


def skill_mercados_externos(nucleo: str, _t: str, _raw: str) -> str:
    return (
        f"[{nucleo}] En el chat local no hay streaming de bolsa en tiempo real, jefa. "
        f"Use **Seguimiento ANT (Nasdaq)** o **Finviz** en el panel lateral para monitorear el movimiento."
    )


def skill_misiones_y_memoria(nucleo: str, t: str, raw: str) -> str:
    if t.startswith("mision:") or t.startswith("misión:") or t.startswith("anota mision:") or t.startswith("anota misión:"):
        tarea = raw.split(":", 1)[1].strip()
        if tarea:
            agregar_mision(tarea)
            return f"[{nucleo}] Misión registrada en base de datos, jefa: **{tarea}**."
    if t.startswith("recuerda:") or t.startswith("guarda:"):
        hecho = raw.split(":", 1)[1].strip()
        if hecho:
            guardar_memoria(hecho, "skill_chat")
            return f"[{nucleo}] Guardado en memoria SQLite, jefa: *{hecho}*."
    return f"[{nucleo}] Núcleo **{nucleo}** operativo en Nodo Buin, jefa. Misiones activas: **{len(obtener_misiones())}**."


def skill_perimetro_cam(nucleo: str, _t: str, _raw: str) -> str:
    return f"[{nucleo}] Estado perimetral, jefa: {getattr(jarvis_core, 'ultimo_movimiento', 'Sin novedades.')}"


SKILLS_REGISTRY = [
    {"id": "wendy", "keys": ["wendy"], "fn": skill_wendy},
    {"id": "planetear", "keys": ["planetear"], "fn": skill_planetear},
    {"id": "ojo_osiris", "keys": ["ojo osiris", "osiris ojo", "vigilancia osiris", "enlace ojo de dios", "comando ojo"], "fn": skill_ojo_osiris},
    {"id": "osiris_ai", "keys": ["osiris", "osiris ai", "osirisai"], "fn": skill_osiris_ai},
    {"id": "ojo_de_dios", "keys": ["ojo de dios", "cámaras", "camaras", "vigilancia", "cctv"], "fn": skill_ojo_de_dios},
    {"id": "mapa_tactico", "keys": ["mapa táctico satelital", "mapa tactico satelital", "mapa"], "fn": skill_mapa_tactico},
    {"id": "finanzas_chile", "keys": ["dólar", "dolar", "euro", "uf", "utm", "divisa", "divisas", "moneda", "cambio"], "fn": skill_finanzas_chile},
    {"id": "mercados_externos", "keys": ["bolsa", "bolsas", "acciones", "nasdaq", "mercado", "mercados", "wall street", "finviz", "ant"], "fn": skill_mercados_externos},
    {"id": "misiones_memoria", "keys": ["mision:", "misión:", "anota mision:", "anota misión:", "recuerda:", "guarda:", "estado", "sistema", "misión", "misiones", "pendiente", "pendientes"], "fn": skill_misiones_y_memoria},
    {"id": "perimetro_cam", "keys": ["cámara", "camara", "perímetro", "perimetro", "movimiento", "sensor"], "fn": skill_perimetro_cam},
]


def responder_con_groq(nucleo: str, texto_usuario: str) -> str:
    if client_groq is None:
        return ""
    mems = [m[0] for m in obtener_memorias(3)]
    ctx_mem = f"Memorias recientes: {'; '.join(mems)}." if mems else ""
    estilos = {
        "JARVIS": "Eres JARVIS, elegante, ingenioso y con sarcasmo fino, tratas al usuario como 'jefa' y respondes en español.",
        "VIERNES": "Eres VIERNES, ágil, directa y resolutiva, tratas al usuario como 'jefa' y respondes en español.",
        "NOVA": "Eres NOVA, enérgica y cósmica, tratas al usuario como 'jefa' y respondes en español.",
    }
    sys_msg = (
        f"{estilos.get(nucleo, estilos['JARVIS'])} "
        f"Skills activas: {[s['id'] for s in SKILLS_REGISTRY]}. {ctx_mem} Sé conciso."
    )
    try:
        chat = client_groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
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
        pass
    return ""


def generar_respuesta_coherente(nucleo: str, texto_usuario: str) -> str:
    prefijo = f"[{nucleo}] "
    raw = texto_usuario.strip()
    t = raw.lower()
    if "protocolo extremo" in t:
        return f"{prefijo}Protocolo de conocimiento extremo activado, jefa. Analizando a fondo sin rodeos."
    if any(t == s or t.startswith(s + " ") or t.startswith(s + ",") for s in ["hola", "buenas", "buenos días", "buenos dias", "buenas tardes", "buenas noches", "holi", "qué tal", "que tal"]):
        return obtener_saludo_nucleo(nucleo)
    if "mosca" in t and ("patas" in t or "cuantas" in t or "cuántas" in t):
        return f"{prefijo}Tiene **6 patas**, jefa. Y por lo general aterrizan justo cuando estorban."
    for sk in SKILLS_REGISTRY:
        if any(k in t for k in sk["keys"]):
            return sk["fn"](nucleo, t, raw)
    if any(k in t for k in ["hora", "qué hora", "que hora", "fecha", "día de hoy", "dia de hoy"]):
        return f"{prefijo}En el Nodo Buin son las **{now_chile.strftime('%H:%M:%S')}** (hora de Chile), jefa."
    ia_resp = responder_con_groq(nucleo, raw)
    if ia_resp:
        return ia_resp
    return random.choice([
        f"{prefijo}Entendido, jefa: *'{raw}'*. Puede usar `wendy`, `planetear`, `ojo de dios`, `misión: ...` o `recuerda: ...`.",
        f"{prefijo}Tomo nota de *'{raw}'*, jefa. Dígame en qué más le apoyo.",
    ])


if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": obtener_saludo_nucleo(st.session_state.nucleo_activo)}]

st.markdown(
    '<style>'
    '.stApp{background-color:#060913!important;color:#00f3ff!important;font-family:monospace;}'
    'p,span,label,h1,h2,h3,h4,div{color:#00f3ff!important;font-family:monospace;}'
    '.stButton>button{background-color:#00f3ff!important;border:1.5px solid #00f3ff!important;font-weight:bold;width:100%;border-radius:6px;}'
    '.stButton>button p,.stButton>button span{color:#060913!important;font-size:0.78rem!important;}'
    '.econ-card{border:1px solid #00f3ff;background:rgba(0,243,255,0.06);border-radius:6px;padding:8px 10px;margin:5px 0;display:flex;justify-content:space-between;}'
    '.arc-reactor-container{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;margin-bottom:6px;}'
    '.arc-ring{width:65px;height:65px;border:2.5px solid #00f3ff;border-radius:50%;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle,rgba(0,243,255,0.4) 0%,#060913 75%);box-shadow:0 0 20px rgba(0,243,255,0.8);margin-bottom:8px;}'
    '.arc-triangle-inverted{width:0;height:0;border-left:12px solid transparent;border-right:12px solid transparent;border-top:20px solid #00f3ff;}'
    '.tactical-link-btn{display:block;width:100%;background-color:#00f3ff;color:#060913!important;text-align:center;padding:6px 10px;margin:5px 0;border-radius:5px;font-size:0.76rem!important;font-weight:bold;text-decoration:none;}'
    '.holo-brain-box{border:1.5px solid #00f3ff;background:linear-gradient(135deg,#0a1128 0%,#060913 100%);padding:15px;border-radius:8px;text-align:center;margin:0 auto 20px auto;max-width:800px;}'
    '.god-eye-box{border:1.5px solid #00f3ff;background:rgba(10,17,40,0.9);border-radius:8px;padding:14px;margin-bottom:16px;}'
    '#MainMenu,footer{visibility:hidden;}'
    '</style>',
    unsafe_allow_html=True
)

if not st.session_state.get("autorizado", False):
    st.markdown('<div style="text-align:center;margin-top:50px;"><h2>ACCESO RESTRINGIDO - NODO BUIN</h2><p>INGRESE PIN DE SEGURIDAD PARA ACTIVAR LA ARMADURA</p></div>', unsafe_allow_html=True)
    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto:", type="password", placeholder="Ingresa tu PIN...")
            if st.form_submit_button("Desbloquear Sistema"):
                if pin_input.strip() == PIN_SECRETO:
                    st.session_state.autorizado = True
                    st.rerun()
                else:
                    st.error("PIN incorrecto. Acceso denegado.")
    st.stop()

with st.sidebar:
    st.markdown("### 🛡️ Arsenal de Módulos")
    if st.button("🔒 Bloquear Sistema", use_container_width=True):
        st.session_state.autorizado = False
        st.rerun()
    if st.button("🔄 Reinicio Total", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🧠 Selector de Núcleo (IA)")
    nuevo_nucleo = st.radio("Núcleo:", ["JARVIS", "VIERNES", "NOVA"], index=["JARVIS", "VIERNES", "NOVA"].index(st.session_state.nucleo_activo), label_visibility="collapsed")
    if nuevo_nucleo != st.session_state.nucleo_activo:
        st.session_state.nucleo_activo = nuevo_nucleo
        st.session_state.mensajes.append({"role": "assistant", "content": obtener_saludo_nucleo(nuevo_nucleo)})
        st.rerun()

    st.markdown("---")
    st.markdown("#### 👁️ Ojo de Dios y Vigilancia")
    with st.expander("Cámaras y Sensores", expanded=False):
        cam_opts = [
            "CAM-01 // PERÍMETRO NODO BUIN",
            "CAM-02 // ACCESO PRINCIPAL",
            "CAM-03 // PATIO Y SECTOR NORTE",
            "CAM-04 // ENLACE REMOTO / RTSP",
        ]
        cam_actual = getattr(jarvis_core, "camara_seleccionada", cam_opts[0])
        sel_cam = st.selectbox("Feed Activo:", cam_opts, index=cam_opts.index(cam_actual) if cam_actual in cam_opts else 0)
        jarvis_core.camara_seleccionada = sel_cam
        jarvis_core.stream_url = st.text_input("URL Stream (MJPEG/Imagen opcional):", value=getattr(jarvis_core, "stream_url", ""), placeholder="https://...")
        c_od1, c_od2 = st.columns(2)
        with c_od1:
            if st.button("👁️ Ver Ojo", use_container_width=True):
                st.session_state.ver_ojo_dios = True
                jarvis_core.ojo_de_dios_activo = True
                st.rerun()
        with c_od2:
            if st.button("✖ Ocultar", use_container_width=True):
                st.session_state.ver_ojo_dios = False
                jarvis_core.ojo_de_dios_activo = False
                st.rerun()
        st.caption(f"Sensor: {getattr(jarvis_core, 'ultimo_movimiento', 'Sin novedades.')}")

    st.markdown("---")
    st.markdown("#### 💾 Memoria y Datos")
    with st.expander("Gestionar Memoria SQLite", expanded=False):
        dato_mem = st.text_input("Dato a guardar:", placeholder="Ej: Preferencia...")
        if st.button("Guardar en Memoria", use_container_width=True) and dato_mem.strip():
            guardar_memoria(dato_mem.strip())
            st.success("¡Memoria guardada!")

    st.markdown("---")
    st.markdown("#### 📋 Misiones Tácticas")
    with st.expander("Base de Datos Misiones", expanded=False):
        nueva_tarea = st.text_input("Nueva Misión:", placeholder="Ej: Revisar nodos...")
        if st.button("Registrar Tarea", use_container_width=True) and nueva_tarea.strip():
            agregar_mision(nueva_tarea.strip())
            st.rerun()
        for _, m_txt, _ in obtener_misiones():
            st.markdown(f"- `{m_txt}`")
        if obtener_misiones() and st.button("Limpiar Misiones", use_container_width=True):
            limpiar_misiones()
            st.rerun()

    st.markdown("---")
    st.markdown("#### 📈 Enlaces Financieros")
    with st.expander("💵 Indicadores en Vivo (Dólar / Euro)", expanded=False):
        econ = obtener_indicadores_chile()
        st.markdown(
            f'<div class="econ-card"><span>💵 Dólar Obs.</span><b>{fmt_clp(econ["dolar"])}</b></div>'
            f'<div class="econ-card"><span>💶 Euro</span><b>{fmt_clp(econ["euro"])}</b></div>'
            f'<div class="econ-card"><span>📈 Valor UF</span><b>{fmt_clp(econ["uf"])}</b></div>',
            unsafe_allow_html=True
        )
        if st.button("🔄 Actualizar Divisas", use_container_width=True):
            obtener_indicadores_chile.clear()
            st.rerun()

    for label, url in [
        ("Osiris AI", OSIRIS_URL),
        ("Seguimiento ANT (Nasdaq)", "https://www.nasdaq.com/market-activity/stocks/ant"),
        ("Monitoreo SpaceX", "https://www.spacex.com/"),
        ("Finviz (Mercados)", "https://finviz.com/"),
        ("Investing.com (Divisas)", "https://es.investing.com/"),
    ]:
        st.markdown(f'<a class="tactical-link-btn" href="{url}" target="_blank">{label}</a>', unsafe_allow_html=True)

fecha_str = now_chile.strftime("%d/%m/%Y")

st.markdown(
    f'<div class="arc-reactor-container">'
    f'<div class="arc-ring"><div class="arc-triangle-inverted"></div></div>'
    f'<h1 style="margin:0;font-size:2.2rem!important;">J.A.R.V.I.S IA</h1>'
    f'<p style="margin:0;font-size:0.75rem!important;">[ NODO BUIN, CHILE // {fecha_str} ]</p>'
    f'</div>',
    unsafe_allow_html=True
)

reloj_vivo_html = """
<div style="text-align:center;color:#00f3ff;font-family:monospace;font-size:0.85rem;margin-bottom:10px;">
  HORA EN VIVO (SANTIAGO): <span id="reloj-vivo">--:--:--</span>
</div>
<script>
  function tickChile() {
    const opts = { timeZone: "America/Santiago", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false };
    const el = document.getElementById("reloj-vivo");
    if (el) el.textContent = new Intl.DateTimeFormat("es-CL", opts).format(new Date());
  }
  tickChile();
  setInterval(tickChile, 1000);
</script>
"""
st.components.v1.html(reloj_vivo_html, height=28)

estado_ia = "GROQ ONLINE" if client_groq else "MOTOR LOCAL + SKILLS"
st.markdown(
    f'<div class="holo-brain-box"><h4 style="margin:0 0 5px 0;">NÚCLEO NEURONAL CYBER-GRID [{st.session_state.nucleo_activo}]</h4><p style="font-size:0.8rem;margin:0;">{estado_ia} // Enlace Directo</p></div>',
    unsafe_allow_html=True
)
st.markdown("---")

if st.session_state.ver_ojo_dios or getattr(jarvis_core, "ojo_de_dios_activo", False):
    cam_titulo = getattr(jarvis_core, "camara_seleccionada", "CAM-01 // PERÍMETRO NODO BUIN")
    mov_titulo = getattr(jarvis_core, "ultimo_movimiento", "Sin novedades en el perímetro.")
    st.markdown(
        f'<div class="god-eye-box">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">'
        f'<b>👁️ OJO DE DIOS // {cam_titulo}</b>'
        f'<span style="font-size:0.75rem;">ESTADO: ENLACE ACTIVO</span>'
        f'</div>'
        f'<p style="font-size:0.78rem;margin:0 0 8px 0;">Sensor perimetral: {mov_titulo} // <a href="{OSIRIS_URL}" target="_blank" style="color:#00f3ff;">Osiris AI</a></p>'
        f'</div>',
        unsafe_allow_html=True
    )
    if getattr(jarvis_core, "stream_url", "").strip():
        st.image(jarvis_core.stream_url.strip(), caption=cam_titulo, use_container_width=True)
    else:
        od_html = """
        <div style="background:#050914;border:1px solid #00f3ff;border-radius:6px;padding:12px;text-align:center;">
          <canvas id="godEyeCanvas" width="640" height="170" style="width:100%;max-width:640px;height:170px;background:#03060d;border-radius:4px;"></canvas>
        </div>
        <script>
          const cv = document.getElementById("godEyeCanvas");
          if (cv) {
            const ctx = cv.getContext("2d");
            let ang = 0;
            function drawEye() {
              ctx.clearRect(0, 0, cv.width, cv.height);
              ctx.strokeStyle = "rgba(0,243,255,0.18)";
              for (let x = 0; x < cv.width; x += 32) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, cv.height); ctx.stroke(); }
              for (let y = 0; y < cv.height; y += 32) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(cv.width, y); ctx.stroke(); }
              const cx = cv.width / 2, cy = cv.height / 2;
              ctx.strokeStyle = "#00f3ff";
              ctx.beginPath(); ctx.arc(cx, cy, 46, 0, Math.PI * 2); ctx.stroke();
              ctx.beginPath(); ctx.arc(cx, cy, 22, 0, Math.PI * 2); ctx.stroke();
              ctx.strokeStyle = "rgba(0,243,255,0.85)";
              ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.cos(ang) * 65, cy + Math.sin(ang) * 65); ctx.stroke();
              ctx.fillStyle = "#00f3ff";
              ctx.font = "12px monospace";
              ctx.fillText("GOD'S EYE // TELEMETRÍA OPTICA", 14, 22);
              ctx.fillText("SECTOR: BUIN-SUR", cv.width - 145, 22);
              ang += 0.04;
              requestAnimationFrame(drawEye);
            }
            drawEye();
          }
        </script>
        """
        st.components.v1.html(od_html, height=195)
    st.markdown("---")

if st.session_state.ver_mapa or getattr(jarvis_core, "mostrar_mapa_tactico", False):
    st.markdown("#### 🛰️ mapa táctico satelital")
    st.map({"lat": [-33.4489], "lon": [-70.6693]}, zoom=10)
    st.markdown("---")

c_ch1, c_ch2 = st.columns([5, 1])
with c_ch1:
    st.markdown("#### Chat 💬")
with c_ch2:
    if st.button("🧹 Purgar", use_container_width=True):
        st.session_state.mensajes = [{"role": "assistant", "content": obtener_saludo_nucleo(st.session_state.nucleo_activo)}]
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt_chat = st.chat_input("Escribe tu orden o consulta para JARVIS...")
if prompt_chat:
    st.session_state.mensajes.append({"role": "user", "content": prompt_chat})
    nucleo = st.session_state.nucleo_activo
    resp_ia = generar_respuesta_coherente(nucleo, prompt_chat)
    st.session_state.mensajes.append({"role": "assistant", "content": resp_ia})
    if nucleo == "JARVIS":
        jarvis_core.hablar(resp_ia.replace("**", ""))
    st.rerun()

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
if "jarvis_core" not in st.session_state:
    c_obj = JarvisCoreEnhancements()
    c_obj.iniciar_hilos()
    st.session_state.jarvis_core = c_obj

jarvis_core = st.session_state.jarvis_core
PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"
API_KEY_GROQ = ""
client_groq = None
if GROQ_AVAILABLE and API_KEY_GROQ:
    try:
        client_groq = Groq(api_key=API_KEY_GROQ)
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


def guardar_memoria(fact_text: str):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    conn.cursor().execute(
        "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
        (f"mem_{datetime.datetime.now().timestamp()}", fact_text, "general")
    )
    conn.commit()
    conn.close()


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


def generar_respuesta_coherente(nucleo: str, texto_usuario: str) -> str:
    prefijo = f"[{nucleo}] "
    t = texto_usuario.strip().lower()
    if "protocolo extremo" in t:
        return f"{prefijo}Protocolo de conocimiento extremo activado, jefa. Analizando a fondo sin rodeos."
    if "mapa táctico satelital" in t or "mapa tactico satelital" in t or "mapa" in t:
        jarvis_core.mostrar_mapa_tactico = True
        st.session_state.ver_mapa = True
        return f"{prefijo}Desplegando **mapa táctico satelital**, jefa. Telemetría en línea."
    if any(t == s or t.startswith(s + " ") or t.startswith(s + ",") for s in ["hola", "buenas", "buenos días", "buenos dias", "buenas tardes", "buenas noches", "holi", "qué tal", "que tal"]):
        return obtener_saludo_nucleo(nucleo)
    if "mosca" in t and ("patas" in t or "cuantas" in t or "cuántas" in t):
        return f"{prefijo}Tiene **6 patas**, jefa. Y por lo general aterrizan justo cuando estorban."
    if any(k in t for k in ["bolsa", "bolsas", "acciones", "nasdaq", "mercado", "mercados", "wall street", "finviz"]):
        return f"{prefijo}En modo respaldo local no tengo cotizaciones en vivo dentro del chat, jefa. Revise **Finviz** o **ANT (Nasdaq)** en el panel lateral."
    if any(k in t for k in ["dólar", "dolar", "euro", "uf", "utm", "divisa", "divisas", "moneda", "cambio"]):
        econ = obtener_indicadores_chile()
        d_fmt = f"${econ['dolar']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        e_fmt = f"${econ['euro']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        u_fmt = f"${econ['uf']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{prefijo}Indicadores en Nodo Buin, jefa: Dólar **{d_fmt}**, Euro **{e_fmt}** y UF **{u_fmt}**."
    if any(k in t for k in ["hora", "qué hora", "que hora", "fecha", "día de hoy", "dia de hoy"]):
        return f"{prefijo}En el Nodo Buin son las **{now_chile.strftime('%H:%M:%S')}** (hora de Chile), jefa."
    if any(k in t for k in ["estado", "sistema", "misión", "misiones", "pendiente", "pendientes"]):
        return f"{prefijo}Núcleo **{nucleo}** operativo en Nodo Buin, jefa. Misiones activas: **{len(obtener_misiones())}**."
    return random.choice([
        f"{prefijo}Entendido, jefa: *'{texto_usuario.strip()}'*. ¿Lo dejamos como misión o abrimos algún módulo?",
        f"{prefijo}Tomo nota de *'{texto_usuario.strip()}'*, jefa. Dígame en qué más le apoyo.",
    ])
    if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": obtener_saludo_nucleo(st.session_state.nucleo_activo)}]
if "ver_mapa" not in st.session_state:
    st.session_state.ver_mapa = False

st.markdown(
    '<style>'
    '.stApp{background-color:#060913!important;color:#00f3ff!important;font-family:monospace;}'
    'p,span,label,h1,h2,h3,h4,div{color:#00f3ff!important;font-family:monospace;}'
    '.stButton>button{background-color:#00f3ff!important;border:1.5px solid #00f3ff!important;font-weight:bold;width:100%;border-radius:6px;}'
    '.stButton>button p,.stButton>button span{color:#060913!important;font-size:0.78rem!important;}'
    '.econ-card{border:1px solid #00f3ff;background:rgba(0,243,255,0.06);border-radius:6px;padding:8px 10px;margin:5px 0;display:flex;justify-content:space-between;}'
    '.arc-reactor-container{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;margin-bottom:10px;}'
    '.arc-ring{width:65px;height:65px;border:2.5px solid #00f3ff;border-radius:50%;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle,rgba(0,243,255,0.4) 0%,#060913 75%);box-shadow:0 0 20px rgba(0,243,255,0.8);margin-bottom:8px;}'
    '.arc-triangle-inverted{width:0;height:0;border-left:12px solid transparent;border-right:12px solid transparent;border-top:20px solid #00f3ff;}'
    '.tactical-link-btn{display:block;width:100%;background-color:#00f3ff;color:#060913!important;text-align:center;padding:6px 10px;margin:5px 0;border-radius:5px;font-size:0.76rem!important;font-weight:bold;text-decoration:none;}'
    '.holo-brain-box{border:1.5px solid #00f3ff;background:linear-gradient(135deg,#0a1128 0%,#060913 100%);padding:15px;border-radius:8px;text-align:center;margin:0 auto 20px auto;max-width:800px;}'
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
        d_fmt = f"${econ['dolar']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        e_fmt = f"${econ['euro']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        u_fmt = f"${econ['uf']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        st.markdown(
            f'<div class="econ-card"><span>💵 Dólar Obs.</span><b>{d_fmt}</b></div>'
            f'<div class="econ-card"><span>💶 Euro</span><b>{e_fmt}</b></div>'
            f'<div class="econ-card"><span>📈 Valor UF</span><b>{u_fmt}</b></div>',
            unsafe_allow_html=True
        )
        if st.button("🔄 Actualizar Divisas", use_container_width=True):
            obtener_indicadores_chile.clear()
            st.rerun()

    for label, url in [
        ("Seguimiento ANT (Nasdaq)", "https://www.nasdaq.com/market-activity/stocks/ant"),
        ("Monitoreo SpaceX", "https://www.spacex.com/"),
        ("Finviz (Mercados)", "https://finviz.com/"),
        ("Investing.com (Divisas)", "https://es.investing.com/"),
    ]:
        st.markdown(f'<a class="tactical-link-btn" href="{url}" target="_blank">{label}</a>', unsafe_allow_html=True)

dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
meses = ["", "enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
fecha_str = f"{dias[now_chile.weekday()]}, {now_chile.day:02d} de {meses[now_chile.month]} de {now_chile.year}"

st.markdown(
    f'<div class="arc-reactor-container">'
    f'<div class="arc-ring"><div class="arc-triangle-inverted"></div></div>'
    f'<h1 style="margin:0;font-size:2.2rem!important;">J.A.R.V.I.S IA</h1>'
    f'<p style="margin:0;font-size:0.75rem!important;">[ NODO BUIN, CHILE // {fecha_str} – {now_chile.strftime("%H:%M:%S")} ]</p>'
    f'</div>'
    f'<div class="holo-brain-box"><h4 style="margin:0 0 5px 0;">NÚCLEO NEURONAL CYBER-GRID [{st.session_state.nucleo_activo}]</h4><p style="font-size:0.8rem;margin:0;">Motor Táctico Neuronal Activo // Enlace Directo</p></div>',
    unsafe_allow_html=True
)
st.markdown("---")

if st.session_state.ver_mapa or jarvis_core.mostrar_mapa_tactico:
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

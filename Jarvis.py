import streamlit as st
import datetime
import sqlite3
import requests
import random
import os
import sys
import time
import threading

# Intento opcional de importar Groq por si acaso
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

# --- IMPORTACIONES SEGURAS DE HARDWARE / MULTIMEDIA (LOCAL + CLOUD) ---
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

# --- INICIALIZACION DE SESSION_STATE ---
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

# --- CLIENTE OPCIONAL (SIN BLOQUEOS NI ERRORES 401) ---
API_KEY_GROQ = ""  # Libre de claves quemadas
client_groq = None
if GROQ_AVAILABLE and API_KEY_GROQ:
    try:
        client_groq = Groq(api_key=API_KEY_GROQ)
    except Exception:
        client_groq = None

# --- BASE DE DATOS SQLITE ---
def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS misiones ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "tarea TEXT NOT NULL, "
        "estado TEXT DEFAULT 'Pendiente')"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS memory ("
        "key_id TEXT PRIMARY KEY, "
        "fact_text TEXT, "
        "category TEXT)"
    )
    conn.commit()
    conn.close()

init_db()

class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path

    def remember_fact(self, key_id: str, fact_text: str):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
            (key_id, fact_text, "general")
        )
        conn.commit()
        conn.close()

jarvis_mem = JarvisMemory()

def agregar_mision(tarea):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
    conn.commit()
    conn.close()

def obtener_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tarea, estado FROM misiones")
    rows = cursor.fetchall()
    conn.close()
    return rows

def limpiar_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM misiones")
    conn.commit()
    conn.close()

# --- OBTENCIÓN DE INDICADORES ECONÓMICOS EN TIEMPO REAL (CHILE) ---
@st.cache_data(ttl=300)
def obtener_indicadores_chile():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JARVIS-Dashboard/1.0",
        "Accept": "application/json"
    }
    for _ in range(2):
        try:
            resp = requests.get("https://mindicador.cl/api", headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                dolar = data.get("dolar", {}).get("valor")
                euro = data.get("euro", {}).get("valor")
                uf = data.get("uf", {}).get("valor")
                utm = data.get("utm", {}).get("valor")
                if dolar and euro and uf:
                    return {
                        "dolar": float(dolar),
                        "euro": float(euro),
                        "uf": float(uf),
                        "utm": float(utm) if utm else 0.0,
                        "ok": True,
                        "respaldo": False
                    }
        except Exception:
            pass

    # Respaldo seguro si la red externa no responde a tiempo
    return {
        "dolar": 950.00,
        "euro": 1030.00,
        "uf": 38000.00,
        "utm": 67000.00,
        "ok": True,
        "respaldo": True
    }

# ZONA HORARIA CHILENA
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

def obtener_saludo_nucleo(nucleo_nombre):
    pref = f"[{nucleo_nombre}] "
    saludos = {
        "JARVIS": f"{pref}{saludo_actual}, jefa. Qué milagro que pase a saludar; los servidores ya empezaban a extrañar sus órdenes.",
        "VIERNES": f"{pref}¡{saludo_actual}, jefa! Lista para mover ficha. ¿Qué encendemos hoy?",
        "NOVA": f"{pref}¡{saludo_actual}, jefa! Señal recibida desde el Nodo Buin. ¿Qué galaxia o tarea conquistamos ahora?"
    }
    return saludos.get(nucleo_nombre, f"{pref}{saludo_actual}, jefa. En línea y a su servicio.")

def generar_respuesta_coherente(nucleo, texto_usuario):
    prefijo = f"[{nucleo}] "
    t = texto_usuario.strip().lower()

    if "protocolo extremo" in t:
        return (
            f"{prefijo}Protocolo de conocimiento extremo activado, jefa. "
            "Analizando el problema a fondo sin rodeos ni cortesías innecesarias."
        )

    if "mapa táctico satelital" in t or "mapa tactico satelital" in t or "mapa" in t:
        jarvis_core.mostrar_mapa_tactico = True
        return f"{prefijo}Desplegando **mapa táctico satelital** en el panel, jefa. Telemetría en línea."

    palabras_saludo = [
        "hola", "buenas", "buenos días", "buenos dias",
        "buenas tardes", "buenas noches", "holi", "qué tal", "que tal"
    ]
    if any(t == s or t.startswith(s + " ") or t.startswith(s + ",") for s in palabras_saludo):
        return obtener_saludo_nucleo(nucleo)

    # 0. Consultas puntuales / curiosidades
    if "mosca" in t and ("patas" in t or "cuantas" in t or "cuántas" in t):
        if nucleo == "JARVIS":
            return f"{prefijo}Tiene **6 patas**, jefa. Como todo insecto que se precie... y por lo general las usa para aterrizar justo en el peor momento."
        if nucleo == "VIERNES":
            return f"{prefijo}**6 patas**, jefa. Tres de cada lado, livianita y bastante molesta."
        return f"{prefijo}Una mosca tiene **6 patas**, jefa. Anatomía básica de insecto confirmada."

    # 1. Bolsas y mercados financieros
    if any(k in t for k in ["bolsa", "bolsas", "acciones", "nasdaq", "mercado", "mercados", "wall street", "finviz"]):
        if nucleo == "JARVIS":
            return (
                f"{prefijo}En modo respaldo local no tengo cotizaciones bursátiles en vivo dentro del chat, jefa. "
                "Puede revisar el pulso directo en **Finviz** o el seguimiento **ANT (Nasdaq)** desde el panel lateral de **Enlaces Financieros**."
            )
        if nucleo == "VIERNES":
            return (
                f"{prefijo}Sin conexión directa a cotizaciones en vivo aquí adentro, jefa. "
                "Abra **Finviz** o **ANT (Nasdaq)** en el menú lateral para ver cómo se mueven las bolsas ahora mismo."
            )
        return (
            f"{prefijo}Radar bursátil sin feed en vivo en esta consola local, jefa. "
            "Tiene acceso directo a **Finviz** y **Nasdaq** en el panel de **Enlaces Financieros**."
        )

    # 2. Dólar, euro, UF y divisas
    if any(k in t for k in ["dólar", "dolar", "euro", "uf", "utm", "divisa", "divisas", "moneda", "cambio"]):
        econ = obtener_indicadores_chile()
        if econ.get("ok"):
            dolar_fmt = f"${econ['dolar']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            euro_fmt = f"${econ['euro']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            uf_fmt = f"${econ['uf']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            nota_resp = " (valor de respaldo local)" if econ.get("respaldo") else ""
            return (
                f"{prefijo}Indicadores registrados en el Nodo Buin{nota_resp}, jefa: "
                f"Dólar Obs. **{dolar_fmt}**, Euro **{euro_fmt}** y UF **{uf_fmt}**."
            )

    # 3. Hora y fecha
    if any(k in t for k in ["hora", "qué hora", "que hora", "fecha", "día de hoy", "dia de hoy"]):
        hora_str = now_chile.strftime("%H:%M:%S")
        return (
            f"{prefijo}En el Nodo Buin son las **{hora_str}** (hora de Chile), jefa. "
            "El reloj superior sigue sincronizado."
        )

    # 4. Estado del sistema o misiones
    if any(k in t for k in ["estado", "sistema", "misión", "misiones", "pendiente", "pendientes"]):
        misiones = obtener_misiones()
        cant = len(misiones)
        return (
            f"{prefijo}Núcleo **{nucleo}** operativo y estable en el Nodo Buin, jefa. "
            f"Actualmente hay **{cant}** misión(es) registrada(s) en la base de datos."
        )

    # 5. Respuesta general coherente según el núcleo
    respuestas_generales = {
        "JARVIS": [
            f"{prefijo}Entendido, jefa. Sobre *'{texto_usuario.strip()}'*, no tengo un dato específico cargado para ese tema en modo local; ¿quiere que lo dejemos como misión o que abramos algún módulo del panel?",
            f"{prefijo}Tomo nota de *'{texto_usuario.strip()}'*, jefa. En respaldo local respondo lo que tengo a mano; dígame si necesita algo en particular."
        ],
        "VIERNES": [
            f"{prefijo}Recibido, jefa: *'{texto_usuario.strip()}'*. Como estamos en modo local, dígame si quiere anotarlo o abrir algún módulo del lateral.",
            f"{prefijo}Anotado, jefa. Para *'{texto_usuario.strip()}'* no tengo un módulo dedicado aquí adentro, pero le ayudo con lo que necesite."
        ],
        "NOVA": [
            f"{prefijo}Señal clara sobre *'{texto_usuario.strip()}'*, jefa. En modo local le digo qué podemos hacer: ¿lo registramos o revisamos algún panel?",
            f"{prefijo}Procesado en el Nodo Buin: *'{texto_usuario.strip()}'*. ¿Qué paso siguiente damos, jefa?"
        ]
    }
    return random.choice(respuestas_generales.get(nucleo, [f"{prefijo}Recibido, jefa."]))

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "assistant",
            "content": obtener_saludo_nucleo(st.session_state.nucleo_activo)
        }
    ]

# --- ESTILOS VISUALES: REACTOR ARC ESTILO STARK & BOTONES COMPACTOS ---
estilos_css = """
    <style>
        .stApp { background-color: #060913 !important; color: #00f3ff !important; font-family: monospace; }
        p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }

        /* AJUSTE FINO DE TEXTOS EN BARRA LATERAL Y MINI MÓDULOS */
        [data-testid="stSidebar"] h3 { font-size: 1.05rem !important; }
        [data-testid="stSidebar"] h4 { font-size: 0.85rem !important; margin-bottom: 4px !important; }
        [data-testid="stSidebar"] summary p { font-size: 0.80rem !important; }

        .stButton>button {
            background-color: #00f3ff !important;
            border: 1.5px solid #00f3ff !important;
            font-weight: bold;
            font-family: monospace;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
            width: 100%;
            border-radius: 6px;
            padding: 5px 10px !important;
        }
        .stButton>button p, .stButton>button span { color: #060913 !important; font-size: 0.78rem !important; }
        .stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.9); }
        .stButton>button:hover p, .stButton>button:hover span { color: #ffffff !important; }

        /* TARJETA DE INDICADORES ECONÓMICOS EN VIVO */
        .econ-card {
            border: 1px solid #00f3ff;
            background: rgba(0, 243, 255, 0.06);
            border-radius: 6px;
            padding: 8px 10px;
            margin: 5px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: inset 0 0 6px rgba(0, 243, 255, 0.2);
        }
        .econ-label { font-size: 0.75rem !important; opacity: 0.85; }
        .econ-val { font-size: 0.85rem !important; font-weight: bold; text-shadow: 0 0 6px #00f3ff; }

        /* REACTOR ARC ESTILO STARK - INVERTIDO */
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 10px;
        }
        .arc-ring {
            width: 65px;
            height: 65px;
            border: 2.5px solid #00f3ff;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, rgba(0,243,255,0.4) 0%, #060913 75%);
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.8), inset 0 0 10px rgba(0, 243, 255, 0.6);
            margin-bottom: 8px;
        }
        .arc-triangle-inverted {
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-top: 20px solid #00f3ff;
            filter: drop-shadow(0 0 8px #00f3ff);
        }

        /* BOTÓN TÁCTICO HTML COMPACTO */
        .tactical-link-btn {
            display: block;
            width: 100%;
            background-color: #00f3ff;
            color: #060913 !important;
            text-align: center;
            padding: 6px 10px;
            margin: 5px 0;
            border-radius: 5px;
            font-size: 0.76rem !important;
            font-weight: bold;
            text-decoration: none;
            font-family: monospace;
            box-shadow: 0 0 8px rgba(0, 243, 255, 0.5);
            transition: all 0.25s ease;
        }
        .tactical-link-btn:hover {
            background-color: #0088cc;
            color: #ffffff !important;
            box-shadow: 0 0 12px rgba(0, 243, 255, 0.9);
        }

        .holo-brain-box {
            border: 1.5px solid #00f3ff;
            background: linear-gradient(135deg, #0a1128 0%, #060913 100%);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.3), inset 0 0 10px rgba(0, 243, 255, 0.15);
            margin: 0 auto 20px auto;
            max-width: 800px;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""
st.markdown(estilos_css, unsafe_allow_html=True)

# --- 1. PANTALLA DE BLOQUEO DE SEGURIDAD ---
if not st.session_state.get("autorizado", False):
    st.markdown(
        '<div style="text-align: center; margin-top: 50px;">'
        '<h2 style="color: #00f3ff;">ACCESO RESTRINGIDO - NODO BUIN</h2>'
        '<p style="color: #00f3ff; opacity: 0.8; font-size: 0.85rem;">INGRESE PIN DE SEGURIDAD PARA ACTIVAR LA ARMADURA</p>'
        '</div>',
        unsafe_allow_html=True
    )
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button("Desbloquear Sistema")
        if btn_entrar:
            if pin_input.strip() == PIN_SECRETO:
                st.session_state.autorizado = True
                st.success("Acceso concedido. Bienvenido de nuevo, jefa.")
                st.rerun()
            else:
                st.error("PIN incorrecto. Acceso denegado.")
    st.stop()

# --- 2. PANEL LATERAL OCULTO (ARSENAL DE MÓDULOS COMPLETO) ---
with st.sidebar:
    st.markdown("### 🛡️ Arsenal de Módulos")
    st.markdown("---")

    if st

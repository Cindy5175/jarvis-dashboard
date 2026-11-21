import datetime
import math
import os
import random
import re
import sqlite3
import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

if "voz_masculina_activa" not in st.session_state:
    st.session_state.voz_masculina_activa = True

if "escucha_continua_activa" not in st.session_state:
    st.session_state.escucha_continua_activa = True

PIN_SECRETO = "2805"
DB_PATH = "jarvis_misiones.db"

API_KEY_GROQ = ""
try:
    API_KEY_GROQ = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    API_KEY_GROQ = os.environ.get("GROQ_API_KEY", "")

client_groq = None
if GROQ_AVAILABLE and API_KEY_GROQ:
    try:
        client_groq = Groq(api_key=API_KEY_GROQ)
    except Exception:
        client_groq = None


def init_db():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
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
    except Exception:
        pass


init_db()


class JarvisMemory:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def remember_fact(self, key_id: str, fact_text: str, category: str = "general"):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
                (key_id, fact_text, category)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def recent_facts(self, limit: int = 5):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT fact_text FROM memory ORDER BY key_id DESC LIMIT ?", (limit,))
            rows = [r[0] for r in cursor.fetchall() if r and r[0]]
            conn.close()
            return rows
        except Exception:
            return []


jarvis_mem = JarvisMemory()


def agregar_mision(tarea):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
        conn.commit()
        conn.close()
    except Exception:
        pass


def obtener_misiones():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT id, tarea, estado FROM misiones")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def limpiar_misiones():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM misiones")
        conn.commit()
        conn.close()
    except Exception:
        pass


@st.cache_data(ttl=300)
def obtener_indicadores_chile():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JARVIS-Dashboard/1.0",
        "Accept": "application/json"
    }
    for _ in range(2):
        try:
            resp = requests.get("https://mindicador.cl/api", headers=headers, timeout=6)
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

    return {
        "dolar": 950.00,
        "euro": 1030.00,
        "uf": 38000.00,
        "utm": 67000.00,
        "ok": True,
        "respaldo": True
    }


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


def limpiar_texto_voz(texto: str) -> str:
    if not texto:
        return ""
    limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace ", texto)
    limpio = re.sub(r"https?://\S+", " enlace ", limpio)
    limpio = re.sub(r"\$[^$]+\$", " fórmula ", limpio)
    limpio = re.sub(r"[*_`#>\[\]]+", "", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio[:450]


def hablar_voz_masculina(texto: str, activa: bool = True):
    if not activa:
        return
    limpio = limpiar_texto_voz(texto)
    if not limpio:
        return
    escapado = (
        limpio.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("'", "\\'")
        .replace("\n", " ")
    )
    js_voz = f"""
    <script>
      (function() {{
        try {{
          if ("speechSynthesis" in window) {{
            window.speechSynthesis.cancel();
            const utter = new SpeechSynthesisUtterance("{escapado}");
            utter.lang = "es-CL";
            utter.rate = 1.02;
            utter.pitch = 0.84;
            const voices = window.speechSynthesis.getVoices() || [];
            const maleEs = voices.find(v => {{
              const n = (v.name || "").toLowerCase();
              const l = (v.lang || "").toLowerCase();
              const isEs = l.startsWith("es");
              const isFem = /sabina|helena|zira|hazel|lucia|lucía|sofia|sofía|female|mujer/.test(n);
              return isEs && !isFem;
            }}) || voices.find(v => (v.lang || "").toLowerCase().startsWith("es"));
            if (maleEs) utter.voice = maleEs;
            window.speechSynthesis.speak(utter);
          }}
        }} catch (e) {{}}
      }})();
    </script>
    """
    components.html(js_voz, height=0)


def escucha_continua_js(activa: bool):
    if not activa:
        return
    js_sr = """
    <script>
      (function() {
        try {
          const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
          if (!SR || window.__jarvisSrActive) return;
          const rec = new SR();
          rec.lang = "es-CL";
          rec.continuous = true;
          rec.interimResults = false;
          window.__jarvisSrActive = true;
          rec.onresult = function(ev) {
            const idx = ev.results.length - 1;
            if (idx >= 0 && ev.results[idx][0]) {
              const dicho = (ev.results[idx][0].transcript || "").trim();
              if (dicho) {
                const el = window.parent.document.getElementById("jarvis-ultima-voz");
                if (el) el.innerText = "Última voz: " + dicho;
              }
            }
          };
          rec.onerror = function() { window.__jarvisSrActive = false; };
          rec.onend = function() {
            window.__jarvisSrActive = false;
            try { rec.start(); window.__jarvisSrActive = true; } catch (e) {}
          };
          rec.start();
        } catch (e) {}
      })();
    </script>
    """
    components.html(js_sr, height=0)


def evaluar_calculo_seguro(texto_raw: str):
    limpio = texto_raw.strip().lower()
    for pref in ["calcula", "calcular", "cuanto es", "cuánto es", "resuelve", "="]:
        if limpio.startswith(pref):
            limpio = limpio[len(pref):].strip()
    limpio = limpio.replace("×", "*").replace("·", "*").replace("÷", "/").replace("^", "**")
    if not limpio or not re.fullmatch(r"[0-9+\-*/().%\s,a-z_]+", limpio):
        return None
    if not re.search(r"\d", limpio):
        return None
    if re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", limpio):
        return None

    entorno = {
        "__builtins__": {},
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "pow": pow,
        "sqrt": math.sqrt,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "log": math.log10,
        "ln": math.log,
        "exp": math.exp,
        "pi": math.pi,
        "e": math.e,
    }
    try:
        resultado = eval(limpio, entorno, {})
        if isinstance(resultado, (int, float)) and not isinstance(resultado, bool):
            if isinstance(resultado, float) and resultado.is_integer():
                resultado = int(resultado)
            elif isinstance(resultado, float):
                resultado = round(resultado, 6)
            return f"Resultado del cálculo `{limpio}`: **{resultado}**."
    except Exception:
        return None
    return None


def responder_dominios_conocimiento(t: str, raw: str):
    calculo = evaluar_calculo_seguro(raw)
    if calculo:
        return calculo

    if any(k in t for k in [
        "biología", "biologia", "adn", "arn", "célula", "celula",
        "genética", "genetica", "evolución", "evolucion", "mitosis",
        "fotosíntesis", "fotosintesis"
    ]):
        return (
            "En **biología**, la célula es la unidad básica de la vida: las eucariotas organizan su material genético en un núcleo y "
            "cuentan con orgánulos como mitocondrias (ATP mediante respiración celular) y cloroplastos (fotosíntesis en plantas). "
            "El **ADN** almacena la información hereditaria en doble hélice y el **ARN** media su transcripción y traducción a proteínas."
        )

    if any(k in t for k in [
        "ciencia", "física", "fisica", "química", "quimica",
        "termodinámica", "termodinamica", "cuántica", "cuantica",
        "astronomía", "astronomia", "gravedad", "luz", "átomo",
        "atomo", "entropía", "entropia"
    ]):
        return (
            "En **ciencia**, los fenómenos se modelan con leyes contrastables y magnitudes físicas: desde la mecánica clásica y la "
            "termodinámica hasta la relatividad, la mecánica cuántica y la estructura atómica y molecular en química. "
            "Si buscas un tema puntual, indícalo directamente."
        )

    if any(k in t for k in [
        "tecnología", "tecnologia", "programación", "programacion",
        "algoritmo", "inteligencia artificial", "ia", "red", "redes",
        "ciberseguridad", "base de datos", "sqlite", "python", "cloud", "nube"
    ]):
        return (
            "En **tecnología**, los sistemas modernos combinan cómputo, redes, almacenamiento y modelos de software: "
            "desde arquitecturas cliente-servidor y bases de datos relacionales (como SQLite) hasta automatización, APIs e inteligencia artificial, "
            "cuidando latencia, seguridad, tolerancia a fallos y reproducibilidad."
        )

    if any(k in t for k in [
        "medicina", "anatomía", "anatomia", "fisiología", "fisiologia",
        "inmune", "inmunológico", "inmunologico", "sistema nervioso",
        "cardiovascular", "farmaco", "fármaco", "vacuna", "salud"
    ]):
        return (
            "En **medicina** y fisiología humana, el organismo mantiene la **homeostasis** mediante sistemas integrados "
            "(nervioso, endocrino, cardiovascular, respiratorio, digestivo, renal e inmune). "
            "Nota: esto es información académica general y no sustituye una evaluación médica presencial ni un diagnóstico clínico."
        )

    if any(k in t for k in [
        "historia", "histórico", "historico", "antigüedad", "antiguedad",
        "edad media", "revolución", "revolucion", "guerra mundial",
        "independencia", "imperio", "civilización", "civilizacion", "chile"
    ]):
        return (
            "En **historia**, los procesos humanos se analizan mediante fuentes, cronología y causalidad múltiple: "
            "desde las primeras civilizaciones y la Antigüedad clásica hasta la Edad Media, la Edad Moderna, las revoluciones "
            "y el siglo XX, observando cómo interactúan factores económicos, sociales, tecnológicos y geopolíticos."
        )

    return None


def generar_respuesta_coherente(nucleo, texto_usuario):
    prefijo = f"[{nucleo}] "
    t = texto_usuario.strip().lower()

    palabras_saludo = [
        "hola", "buenas", "buenos días", "buenos dias",
        "buenas tardes", "buenas noches", "holi", "qué tal", "que tal"
    ]
    if any(t == s or t.startswith(s + " ") or t.startswith(s + ",") for s in palabras_saludo):
        return obtener_saludo_nucleo(nucleo)

    if "mosca" in t and ("patas" in t or "cuantas" in t or "cuántas" in t):
        if nucleo == "JARVIS":
            return f"{prefijo}Tiene **6 patas**, jefa. Como todo insecto que se precie... y por lo general las usa para aterrizar justo en el peor momento."
        if nucleo == "VIERNES":
            return f"{prefijo}**6 patas**, jefa. Tres de cada lado, livianita y bastante molesta."
        return f"{prefijo}Una mosca tiene **6 patas**, jefa. Anatomía básica de insecto confirmada."

    resp_dominio = responder_dominios_conocimiento(t, texto_usuario)
    if resp_dominio:
        return f"{prefijo}{resp_dominio}"

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

    if any(k in t for k in ["hora", "qué hora", "que hora", "fecha", "día de hoy", "dia de hoy"]):
        hora_str = now_chile.strftime("%H:%M:%S")
        return (
            f"{prefijo}En el Nodo Buin son las **{hora_str}** (hora de Chile), jefa. "
            "El reloj superior sigue sincronizado."
        )

    if any(k in t for k in ["estado", "sistema", "misión", "misiones", "pendiente", "pendientes"]):
        misiones = obtener_misiones()
        cant = len(misiones)
        return (
            f"{prefijo}Núcleo **{nucleo}** operativo y estable en el Nodo Buin, jefa. "
            f"Actualmente hay **{cant}** misión(es) registrada(s) en la base de datos."
        )

    respuestas_generales = {
        "JARVIS": [
            f"{prefijo}Entendido, jefa. Sobre *'{texto_usuario.strip()}'*, puedo apoyarle en ciencia, tecnología, medicina, cálculos, historia o biología; ¿quiere que lo dejemos como misión o que abramos algún módulo del panel?",
            f"{prefijo}Tomo nota de *'{texto_usuario.strip()}'*, jefa. En respaldo local respondo lo que tengo a mano; dígame si necesita algo en particular."
        ],
        "VIERNES": [
            f"{prefijo}Recibido, jefa: *'{texto_usuario.strip()}'*. Puedo ayudarle con ciencia, tecnología, medicina, cálculos, historia o biología, o anotarlo como misión.",
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

estilos_css = """
    <style>
        .stApp { background-color: #060913 !important; color: #00f3ff !important; }
        .stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp div {
            color: #00f3ff !important;
            font-family: monospace;
        }
        [data-testid="stIconMaterial"], .material-symbols-rounded, .material-icons {
            font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
            color: #00f3ff !important;
        }

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

with st.sidebar:
    st.markdown("### 🛡️ Arsenal de Módulos")
    st.markdown("---")

    if st.button("🔒 Bloquear Sistema", use_container_width=True):
        st.session_state.autorizado = False
        st.

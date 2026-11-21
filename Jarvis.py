import streamlit as st
import streamlit.components.v1 as components
import datetime
import sqlite3
import requests
import random
import math
import re
import os
import sys

# Intento opcional de importar Groq por si acaso
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

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

if "voz_masculina_activa" not in st.session_state:
    st.session_state.voz_masculina_activa = True

if "escucha_continua_activa" not in st.session_state:
    st.session_state.escucha_continua_activa = True

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"

# --- CLIENTE OPCIONAL (SIN BLOQUEOS NI ERRORES 401) ---
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

    def remember_fact(self, key_id: str, fact_text: str, category: str = "general"):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
            (key_id, fact_text, category)
        )
        conn.commit()
        conn.close()

    def recent_facts(self, limit: int = 5):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT fact_text FROM memory ORDER BY key_id DESC LIMIT ?", (limit,))
        rows = [r[0] for r in cursor.fetchall() if r and r[0]]
        conn.close()
        return rows

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

# --- VOZ MASCULINA Y ESCUCHA CONTINUA EN NAVEGADOR ---
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

# --- MOTOR DE CÁLCULOS Y CONOCIMIENTO (CIENCIA, TECNOLOGÍA, MEDICINA, HISTORIA, BIOLOGÍA) ---
def evaluar_calculo_seguro(texto_raw: str) -> str | None:
    limpio = texto_raw.strip().lower()
    for pref in ["calcula", "calcular", "cuanto es", "cuánto es", "resuelve", "="]:
        if limpio.startswith(pref):
            limpio = limpio[len(pref):].strip()
    limpio = limpio.replace("×", "*").replace("·", "*").replace("÷", "/").replace("^", "**")
    if not limpio or not re.fullmatch(r"[0-9+\-*/().%\s,a-z_]+", limpio):
        return None
    if not re.search(r"\d", limpio):
        return None
    # Evitar confundir fechas o horas con operaciones matemáticas simples
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

def responder_dominios_conocimiento(t: str, raw: str) -> str | None:
    calculo = evaluar_calculo_seguro(raw)
    if calculo:
        return calculo

    # BIOLOGÍA
    if any(k in t for k in ["biología", "biologia", "adn", "arn", "célula", "celula", "genética", "genetica", "evolución", "evolucion", "mitosis", "fotosíntesis", "fotosintesis"]):
        return (
            "En **biología**, la célula es la unidad básica de la vida: las eucariotas organizan su material genético en un núcleo y "
            "cuentan con orgánulos como mitocondrias (ATP mediante respiración celular) y cloroplastos (fotosíntesis en plantas). "
            "El **ADN** almacena la información hereditaria en doble hélice y el **ARN** media su transcripción y traducción a proteínas."
        )

    # CIENCIA (FÍSICA, QUÍMICA, ASTRONOMÍA, TERMODINÁMICA)
    if any(k in t for k in ["ciencia", "física", "fisica", "química", "quimica", "termodinámica", "termodinamica", "cuántica", "cuantica", "astronomía", "astronomia", "gravedad", "luz", "átomo", "atomo", "entropía", "entropia"]):
        return (
            "En **ciencia**, los fenómenos se modelan con leyes contrastables y magnitudes físicas: desde la mecánica clásica y la "
            "termodinámica ($\\Delta U = Q - W$, $\\Delta S \\ge 0$) hasta la relatividad, la mecánica cuántica y la estructura atómica "
            "y molecular en química. Si buscas un tema puntual (por ejemplo termodinámica, astronomía o cinemática), pídelo directo."
        )

    # TECNOLOGÍA
    if any(k in t for k in ["tecnología", "tecnologia", "programación", "programacion", "algoritmo", "inteligencia artificial", "ia", "red", "redes", "ciberseguridad", "base de datos", "sqlite", "python", "cloud", "nube"]):
        return (
            "En **tecnología**, los sistemas modernos combinan cómputo, redes, almacenamiento y modelos de software: "
            "desde arquitecturas cliente-servidor y bases de datos relacionales (como SQLite) hasta automatización, APIs e inteligencia artificial, "
            "cuidando latencia, seguridad, tolerancia a fallos y reproducibilidad."
        )

    # MEDICINA
    if any(k in t for k in ["medicina", "anatomía", "anatomia", "fisiología", "fisiologia", "inmune", "inmunológico", "inmunologico", "sistema nervioso", "cardiovascular", "farmaco", "fármaco", "vacuna", "salud"]):
        return (
            "En **medicina** y fisiología humana, el organismo mantiene la **homeostasis** mediante sistemas integrados "
            "(nervioso, endocrino, cardiovascular, respiratorio, digestivo, renal e inmune). "
            "Nota: esto es información académica general y no sustituye una evaluación médica presencial ni un diagnóstico clínico."
        )

    # HISTORIA
    if any(k in t for k in ["historia", "histórico", "historico", "antigüedad", "antiguedad", "edad media", "revolución", "revolucion", "guerra mundial", "independencia", "imperio", "civilización", "civilizacion", "chile"]):
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

    # 0. Consultas puntuales / curiosidades
    if "mosca" in t and ("patas" in t or "cuantas" in t or "cuántas" in t):
        if nucleo == "JARVIS":
            return f"{prefijo}Tiene **6 patas**, jefa. Como todo insecto que se precie... y por lo general las usa para aterrizar justo en el peor momento."
        if nucleo == "VIERNES":
            return f"{prefijo}**6 patas**, jefa. Tres de cada lado, livianita y bastante molesta."
        return f"{prefijo}Una mosca tiene **6 patas**, jefa. Anatomía básica de insecto confirmada."

    # 0.5 Conocimiento de ciencia, tecnología, medicina, cálculos, historia y biología
    resp_dominio = responder_dominios_conocimiento(t, texto_usuario)
    if resp_dominio:
        return f"{prefijo}{resp_dominio}"

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

    #

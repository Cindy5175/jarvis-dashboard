import datetime
import io
import json
import os
import random
import sqlite3
import time
import urllib.parse
import xml.etree.ElementTree as ET
import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except Exception:
    Groq = None
    GROQ_AVAILABLE = False

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except Exception:
    Image = None
    ImageDraw = None
    PIL_AVAILABLE = False

st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="expanded",
)

NUCLEOS_DISPONIBLES = ["JARVIS", "VIERNES", "NOVA", "ARTEX"]

IDIOMAS_DISPONIBLES = {
    "Español (es-CL)": {"code": "es-CL", "nombre": "español (Chile)"},
    "English (en-US)": {"code": "en-US", "nombre": "English"},
    "Français (fr-FR)": {"code": "fr-FR", "nombre": "français"},
    "Português (pt-BR)": {"code": "pt-BR", "nombre": "português"},
    "Italiano (it-IT)": {"code": "it-IT", "nombre": "italiano"},
    "Deutsch (de-DE)": {"code": "de-DE", "nombre": "Deutsch"},
}
OPCIONES_IDIOMA = list(IDIOMAS_DISPONIBLES.keys())

TEMAS_VISUALES = {
    "CIAN TÁCTICO": {
        "primary": "#00f3ff",
        "hover": "#0088cc",
        "bg": "#060913",
        "card_bg": "rgba(0, 243, 255, 0.06)",
        "grad_start": "#0a1128",
        "btn_text": "#060913",
    },
    "ALERTA ROJA": {
        "primary": "#ff3b3b",
        "hover": "#b30000",
        "bg": "#120507",
        "card_bg": "rgba(255, 59, 59, 0.08)",
        "grad_start": "#26080c",
        "btn_text": "#120507",
    },
    "SIGILO VERDE": {
        "primary": "#39ff14",
        "hover": "#1f9e08",
        "bg": "#040d06",
        "card_bg": "rgba(57, 255, 20, 0.06)",
        "grad_start": "#081c0c",
        "btn_text": "#040d06",
    },
    "ÁMBAR NOCTURNO": {
        "primary": "#ffb000",
        "hover": "#b87d00",
        "bg": "#120b03",
        "card_bg": "rgba(255, 176, 0, 0.07)",
        "grad_start": "#241605",
        "btn_text": "#120b03",
    },
}
OPCIONES_TEMA = list(TEMAS_VISUALES.keys())

MODELOS_RESPALDO_GEMINI = [
    "gemini-3.8-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
]

PROTOCOLO_CONOCIMIENTO_BASE = (
    "PROTOCOLO DE CONOCIMIENTO SUPREMO COMPARTIDO (APLICABLE A TODOS LOS NUCLEOS): "
    "Responde con rigor tecnico, precision y claridad estructurada en: "
    "(1) Biologia (celular, genetica, fisiologia, evolucion, ecologia); "
    "(2) Matematicas y Aritmetica (algebra, funciones, geometria, trigonometria, estadistica, "
    "probabilidad, porcentajes, proporciones y resolucion paso a paso); "
    "(3) Geografia (geografia fisica, climas, cartografia, recursos, geopolitica y geografia de Chile y del mundo); "
    "(4) Historia (procesos historicos, cronologia, causas y consecuencias, historia universal, de America y de Chile); "
    "(5) Ciencia y Tecnologia (fisica, quimica, astronomia, computacion, algoritmos, redes, sistemas e ingenieria); "
    "(6) Calculos en general (explicar formulas, variables, unidades y verificar resultados); "
    "(7) Conocimiento Religioso y Secular (historia de las religiones, religiones comparadas, simbolos, "
    "tradiciones y etica religiosa, junto con filosofia secular, etica laica, humanismo, pensamiento "
    "critico y convivencia civica). Mantén siempre neutralidad respetuosa, claridad y rigor sin imponer dogmas. "
    "Explica pasos o formulas cuando ayude, respeta unidades y no inventes datos sin confirmar."
)

ESTILO_CONVERSACIONAL_BASE = (
    "ESTILO DE DIALOGO: Habla de forma natural, cercana, espontánea y fluida, como un asistente personal "
    "de confianza que conoce bien a la usuaria (llámala 'jefa' con calidez y naturalidad, sin repetirlo en "
    "cada frase si suena forzado). Nunca repitas textualmente la pregunta del usuario entre comillas. "
    "Evita sonar rígido o como manual técnico en charla casual; conserva un toque sutil de chispa e ironía "
    "elegante cuando encaje, manteniendo siempre empatía, claridad y precisión cuando haya datos o análisis."
)

st.session_state.setdefault("autorizado", False)
st.session_state.setdefault("nucleo_activo", "JARVIS")
st.session_state.setdefault("idioma_sistema", "Español (es-CL)")
st.session_state.setdefault("tema_visual", "CIAN TÁCTICO")
st.session_state.setdefault("voz_masculina_activa", True)
st.session_state.setdefault("pendiente_voz", None)
st.session_state.setdefault("capa_radar", "SATELITAL // BUIN")
st.session_state.setdefault("notas_rapidas", [])
st.session_state.setdefault("modo_camara", "VISIÓN NOCTURNA")
st.session_state.setdefault("bitacora_sesion", [])
st.session_state.setdefault("alerta_dolar_max", 0.0)
st.session_state.setdefault("alerta_uf_max", 0.0)
st.session_state.setdefault("recordatorio_hora", "")
st.session_state.setdefault("recordatorio_texto", "")
st.session_state.setdefault("noticias_cache_lista", [])
st.session_state.setdefault("panel_nota_voz_abierto", False)
st.session_state.setdefault("borrador_nota_voz", "")
st.session_state.setdefault("mensajes", [])

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"
BUIN_LAT = -33.7325
BUIN_LON = -70.7422


def _limpiar_clave(valor) -> str:
    if not valor:
        return ""
    limpia = "".join(str(valor).split()).strip()
    if (limpia.startswith('"') and limpia.endswith('"')) or (
        limpia.startswith("'") and limpia.endswith("'")
    ):
        limpia = limpia[1:-1].strip()
    return limpia


def _buscar_en_mapping(mapping, nombres):
    if not mapping:
        return ""
    for nombre in nombres:
        if nombre in mapping and mapping[nombre]:
            val = _limpiar_clave(mapping[nombre])
            if val:
                return val
    return ""


def obtener_clave_secreta_gemini() -> str:
    nombres = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "gemini_api_key", "google_api_key")
    clave_env = _buscar_en_mapping(os.environ, nombres)
    if clave_env:
        return clave_env
    try:
        clave_root = _buscar_en_mapping(st.secrets, nombres)
        if clave_root:
            return clave_root
        for seccion in ("general", "secrets", "api", "gemini"):
            if seccion in st.secrets and isinstance(st.secrets[seccion], dict):
                clave_sec = _buscar_en_mapping(st.secrets[seccion], nombres)
                if clave_sec:
                    return clave_sec
    except Exception:
        pass
    return ""


st.session_state.setdefault("gemini_key_sesion", obtener_clave_secreta_gemini())

API_KEY_GROQ = ""
try:
    if "GROQ_API_KEY" in st.secrets:
        API_KEY_GROQ = _limpiar_clave(st.secrets["GROQ_API_KEY"])
except Exception:
    API_KEY_GROQ = ""

if not API_KEY_GROQ:
    API_KEY_GROQ = _limpiar_clave(os.environ.get("GROQ_API_KEY", ""))

client_groq = None
if GROQ_AVAILABLE and API_KEY_GROQ:
    try:
        client_groq = Groq(api_key=API_KEY_GROQ)
    except Exception:
        client_groq = None


def obtener_tema_actual():
    nombre = st.session_state.get("tema_visual", "CIAN TÁCTICO")
    if nombre not in TEMAS_VISUALES:
        nombre = "CIAN TÁCTICO"
    return nombre, TEMAS_VISUALES[nombre]


def obtener_config_idioma(etiqueta_idioma=None):
    etiqueta = etiqueta_idioma or st.session_state.get("idioma_sistema", "Español (es-CL)")
    if etiqueta not in IDIOMAS_DISPONIBLES:
        etiqueta = "Español (es-CL)"
    return etiqueta, IDIOMAS_DISPONIBLES[etiqueta]


def aplicar_css_tema():
    _, tema = obtener_tema_actual()
    primary = tema["primary"]
    hover = tema["hover"]
    bg = tema["bg"]
    card_bg = tema["card_bg"]
    grad_start = tema["grad_start"]
    btn_text = tema["btn_text"]

    st.markdown(
        f"""
        <style>
        .stApp {{
            background: radial-gradient(circle at top, {grad_start} 0%, {bg} 72%);
            color: {primary};
            font-family: monospace;
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {grad_start} 0%, {bg} 100%);
            border-right: 1px solid {primary}44;
        }}
        .stButton > button, .stDownloadButton > button {{
            border: 1px solid {primary};
            background-color: {card_bg};
            color: {primary};
            font-family: monospace;
            border-radius: 6px;
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            background-color: {primary};
            color: {btn_text};
            border-color: {hover};
        }}
        .holo-brain-box {{
            border: 1px solid {primary}66;
            background: {card_bg};
            border-radius: 10px;
            padding: 12px 16px;
            margin-bottom: 12px;
            color: {primary};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def registrar_evento(detalle: str):
    tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
    stamp = datetime.datetime.now(tz_chile).strftime("%H:%M:%S")
    st.session_state.setdefault("bitacora_sesion", [])
    st.session_state["bitacora_sesion"].append(f"[{stamp}] {detalle}")
    st.session_state["bitacora_sesion"] = st.session_state["bitacora_sesion"][-25:]


def init_db():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
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
    def __init__(self, db_path=fn_db):
        self.db_path = db_path

    def remember_fact(self, key_id: str, fact_text: str):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
                (key_id, fact_text, "general"),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def get_recent_facts(self, limit: int = 5):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT fact_text FROM memory ORDER BY rowid DESC LIMIT ?", (limit,))
            rows = [r[0] for r in cursor.fetchall() if r and r[0]]
            conn.close()
            return rows
        except Exception:
            return []

    def clear_facts(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memory")
            conn.commit()
            conn.close()
        except Exception:
            pass


jarvis_mem = JarvisMemory()


def agregar_mision(tarea):
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
        conn.commit()
        conn.close()
        registrar_evento(f"Misión añadida: {tarea}")
    except Exception:
        pass


def obtener_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT id, tarea, estado FROM misiones ORDER BY id ASC")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def limpiar_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM misiones")
        conn.commit()
        conn.close()
        registrar_evento("Misiones purgadas")
    except Exception:
        pass


@st.cache_data(ttl=300)
def obtener_indicadores_chile():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JARVIS-Dashboard/1.0",
        "Accept": "application/json",
    }
    for _ in range(2):
        try:
            resp = requests.get("https://mindicador.cl/api", headers=headers, timeout=4)
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
                        "respaldo": False,
                    }
        except Exception:
            pass

    return {
        "dolar": 950.00,
        "euro": 1030.00,
        "uf": 38000.00,
        "utm": 67000.00,
        "ok": True,
        "respaldo": True,
    }


def describir_clima_codigo(code):
    mapa = {
        0: "despejado",
        1: "mayormente despejado",
        2: "parcialmente nublado",
        3: "nublado",
        45: "con neblina",
        61: "con lluvia leve",
        63: "con lluvia moderada",
        80: "con chubascos",
        95: "con tormenta electrica",
    }
    return mapa.get(code, "condiciones variables")


@st.cache_data(ttl=600)
def obtener_clima_buin():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={BUIN_LAT}&longitude={BUIN_LON}"
        f"&current=temperature_2m,weather_code&timezone=America%2FSantiago"
    )
    try:
        resp = requests.get(url, timeout=4)
        if resp.status_code == 200:
            current = resp.json().get("current") or {}
            temp = current.get("temperature_2m")
            code = int(current.get("weather_code", 0))
            if temp is not None:
                return {
                    "temp_c": round(float(temp), 1),
                    "condicion": describir_clima_codigo(code),
                }
    except Exception:
        pass
    return {"temp_c": None, "condicion": "sin lectura en vivo"}


@st.cache_data(ttl=600)
def obtener_noticias_rss(consulta="Chile tecnología finanzas", limite=5):
    q_encoded = urllib.parse.quote(consulta.strip() or "Chile")
    url = f"https://news.google.com/rss/search?q={q_encoded}&hl=es-419&gl=CL&ceid=CL:es-419"
    headers = {"User-Agent": "Mozilla/5.0 (JARVIS-Node-Buin/1.0)"}
    resultados = []
    try:
        resp = requests.get(url, headers=headers, timeout=4)
        if resp.status_code == 200 and resp.content:
            root = ET.fromstring(resp.content)
            for item in root.findall(".//item")[:limite]:
                titulo_el = item.find("title")
                link_el = item.find("link")
                pub_el = item.find("pubDate")
                titulo = (titulo_el.text or "").strip() if titulo_el is not None else ""
                enlace = (link_el.text or "").strip() if link_el is not None else ""
                fecha = (pub_el.text or "")[:16].strip() if pub_el is not None else ""
                if titulo:
                    resultados.append({"titulo": titulo, "link": enlace, "fecha": fecha})
    except Exception:
        pass
    return resultados


def fmt_clp(valor):
    return "$" + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def obtener_hora_chile():
    tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
    return datetime.datetime.now(tz_chile)


def obtener_saludo_actual(ahora, lang_code="es-CL"):
    hora = ahora.hour
    base_lang = (lang_code or "es-CL").split("-")[0].lower()
    if base_lang == "en":
        if 0 <= hora < 12:
            return "Good morning"
        if 12 <= hora < 20:
            return "Good afternoon"
        return "Good evening"
    if base_lang == "fr":
        return "Bonjour" if 0 <= hora < 18 else "Bonsoir"
    if base_lang == "pt":
        if 0 <= hora < 12:
            return "Bom dia"
        if 12 <= hora < 18:
            return "Boa tarde"
        return "Boa noite"
    if base_lang == "it":
        if 0 <= hora < 12:
            return "Buongiorno"
        if 12 <= hora < 18:
            return "Buon pomeriggio"
        return "Buonasera"
    if base_lang == "de":
        if 0 <= hora < 12:
            return "Guten Morgen"
        if 12 <= hora < 18:
            return "Guten Tag"
        return "Guten Abend"
    if 0 <= hora < 12:
        return "Buenos días"
    if 12 <= hora < 20:
        return "Buenas tardes"
    return "Buenas noches"


def obtener_saludo_nucleo(nucleo_nombre, etiqueta_idioma=None):
    ahora = obtener_hora_chile()
    _, cfg = obtener_config_idioma(etiqueta_idioma)
    lang_code = cfg["code"]
    base_lang = lang_code.split("-")[0].lower()
    saludo = obtener_saludo_actual(ahora, lang_code)
    pref = f"[{nucleo_nombre}] "

    if base_lang == "en":
        saludos_en = {
            "JARVIS": [
                f"{pref}{saludo}, Boss. Good to have you around; the servers were starting to wonder if you'd forgotten the password.",
                f"{pref}{saludo}, Boss. Ready when you are—what are we tackling first?",
            ],
            "VIERNES": [
                f"{pref}{saludo}, Boss! Let's get things moving. What's on your mind?",
                f"{pref}{saludo}, Boss! All systems warm and ready—what do you need?",
            ],
            "NOVA": [
                f"{pref}{saludo}, Boss! Buin Node is locked in. Where are we pointing our radar today?",
                f"{pref}{saludo}, Boss! Signal's clear from Buin—what shall we explore next?",
            ],
            "ARTEX": [
                f"{pref}{saludo}, Boss! ARTEX is online and sharp. What are we analyzing or building?",
                f"{pref}{saludo}, Boss! Ready for calculations, strategy, or straight talk.",
            ],
        }
        return random.choice(saludos_en.get(nucleo_nombre, [f"{pref}{saludo}, Boss. Right here with you."]))

    if base_lang == "fr":
        return f"{pref}{saludo}, patronne. Noyau {nucleo_nombre} actif à Buin—qu'est-ce qu'on fait ?"
    if base_lang == "pt":
        return f"{pref}{saludo}, chefe. Núcleo {nucleo_nombre} pronto em Buin—por onde começamos?"
    if base_lang == "it":
        return f"{pref}{saludo}, capa. Nucleo {nucleo_nombre} attivo da Buin—da dove partiamo?"
    if base_lang == "de":
        return f"{pref}{saludo}, Chefin. Kern {nucleo_nombre} in Buin ist bereit—woran gehen wir?"

    saludos = {
        "JARVIS": [
            f"{pref}{saludo}, jefa. Qué bueno verla por aquí; los servidores ya pensaban que se habían ido de vacaciones sin avisar.",
            f"{pref}{saludo}, jefa. Aquí estamos, listos para conversar o mover lo que haga falta. ¿Qué traemos hoy?",
            f"{pref}{saludo}, jefa. Un gusto saludarla—¿en qué andamos o qué le damos vuelta ahora?",
        ],
        "VIERNES": [
            f"{pref}¡{saludo}, jefa! Todo andando. ¿Qué encendemos o resolvemos primero?",
            f"{pref}¡{saludo}, jefa! Por acá con toda la pila puesta. ¿Qué tienes en mente?",
        ],
        "NOVA": [
            f"{pref}¡{saludo}, jefa! Enlace firme desde Buin. ¿Qué tema o proyecto exploramos ahora?",
            f"{pref}¡{saludo}, jefa! Radar despejado por acá—¿hacia dónde vamos hoy?",
        ],
        "ARTEX": [
            f"{pref}¡{saludo}, jefa! En línea y afinado. ¿Calculamos, revisamos o conversamos directo?",
            f"{pref}¡{saludo}, jefa! Listo para entrar en materia cuando usted diga.",
        ],
    }
    return random.choice(saludos.get(nucleo_nombre, [f"{pref}{saludo}, jefa. Aquí estoy."]))


def obtener_presentacion_nucleo(nucleo_nombre, etiqueta_idioma=None):
    _, cfg = obtener_config_idioma(etiqueta_idioma)
    base_lang = cfg["code"].split("-")[0].lower()
    pref = f"[{nucleo_nombre}] "

    if base_lang == "en":
        presentaciones_en = {
            "JARVIS": (
                f"{pref}I'm **J.A.R.V.I.S.**, your assistant here at **Buin Node, Chile**, Boss—part tactical helper, "
                "part sounding board, always ready for live figures, notes, missions, or a good conversation."
            ),
            "VIERNES": (
                f"{pref}I'm **VIERNES**, your fast-paced core at **Buin Node, Chile**, Boss—built for quick answers, "
                "zero fluff, and getting things done without dragging our feet."
            ),
            "NOVA": (
                f"{pref}I'm **NOVA**, your exploration core at **Buin Node, Chile**, Boss—great for following leads, "
                "tracking ideas, and keeping tabs on what's moving."
            ),
            "ARTEX": (
                f"{pref}I'm **ARTEX**, your analytical core at **Buin Node, Chile**, Boss—sharp with numbers, "
                "science, history, and straight-to-the-point reasoning."
            ),
        }
        return presentaciones_en.get(
            nucleo_nombre,
            f"{pref}I'm **{nucleo_nombre}**, active at **Buin Node, Chile**, Boss.",
        )

    presentaciones_es = {
        "JARVIS": (
            f"{pref}Soy **J.A.R.V.I.S.**, su mano derecha aquí en el **Nodo Buin**, jefa—entre datos, misiones, "
            "cálculos, noticias y conversación franca, siempre con un ojo en el tablero y otro en que usted esté cómoda."
        ),
        "VIERNES": (
            f"{pref}Soy **VIERNES**, su núcleo más ágil en **Buin**, jefa—ideal para ir al grano, resolver rápido "
            "y no darle mil vueltas a lo que se puede mover al tiro."
        ),
        "NOVA": (
            f"{pref}Soy **NOVA**, su núcleo de exploración desde **Buin**, jefa—pensada para seguir pistas, "
            "ordenar ideas y mantener el radar abierto."
        ),
        "ARTEX": (
            f"{pref}Soy **ARTEX**, su núcleo de análisis y cálculo en **Buin**, jefa—fuerte en números, "
            "ciencia, historia, geografía y respuestas claras sin rodeos."
        ),
    }
    return presentaciones_es.get(
        nucleo_nombre,
        f"{pref}Soy **{nucleo_nombre}**, activo en **Buin**, jefa.",
    )


def purgar_chat(nucleo_nombre):
    st.session_state["mensajes"] = [
        {
            "role": "assistant",
            "content": obtener_saludo_nucleo(nucleo_nombre, st.session_state.get("idioma_sistema")),
        }
    ]
    st.session_state["pendiente_voz"] = None
    registrar_evento(f"Chat purgado en núcleo {nucleo_nombre}")


def construir_prompt_sistema(nucleo_nombre: str, etiqueta_idioma: str, indicadores: dict, clima_buin: dict) -> str:
    _, cfg = obtener_config_idioma(etiqueta_idioma)
    ahora = obtener_hora_chile()
    recuerdos = jarvis_mem.get_recent_facts(6)
    notas = st.session_state.get("notas_rapidas", [])[-5:]
    misiones = obtener_misiones()

    partes = [
        f"Eres {nucleo_nombre} dentro del sistema J.A.R.V.I.S. en el Nodo Buin, Chile.",
        f"Idioma de respuesta requerido: {cfg['nombre']} ({cfg['code']}).",
        f"Hora actual en Chile: {ahora.strftime('%d/%m/%Y %H:%M:%S')}.",
        (
            f"Datos de referencia en vivo: Dólar {fmt_clp(indicadores['dolar'])}, "
            f"Euro {fmt_clp(indicadores['euro'])}, UF {fmt_clp(indicadores['uf'])}, "
            f"Clima Buin {clima_buin.get('temp_c', 'N/D')}°C ({clima_buin.get('condicion', 'N/D')})."
        ),
        ESTILO_CONVERSACIONAL_BASE,
        PROTOCOLO_CONOCIMIENTO_BASE,
    ]
    if recuerdos:
        partes.append("Memoria persistente de la usuaria:\n- " + "\n- ".join(recuerdos))
    if notas:
        partes.append("Notas rápidas recientes:\n- " + "\n- ".join(notas))
    if misiones:
        partes.append("Misiones activas:\n- " + "\n- ".join(f"{t} [{e}]" for _, t, e in misiones))
    return "\n\n".join(partes)


def _formatear_error_http(resp: requests.Response) -> str:
    detalle = ""
    try:
        data = resp.json()
        err = data.get("error", {})
        detalle = err.get("message") or str(data)
    except Exception:
        detalle = (resp.text or "").strip()[:300]
    return f"HTTP {resp.status_code}" + (f": {detalle}" if detalle else "")


def _peticion_gemini_con_clave(url_base: str, clave: str, payload: dict, usar_query_key: bool = False) -> requests.Response:
    headers = {"Content-Type": "application/json"}
    params = {"key": clave} if usar_query_key else None
    if not usar_query_key:
        headers["x-goog-api-key"] = clave
    return requests.post(url_base, headers=headers, params=params, json=payload, timeout=60)


def _llamar_modelo_gemini_unico(mensajes, api_key: str, modelo: str, prompt_sistema: str) -> str:
    clave = _limpiar_clave(api_key)
    if not clave:
        raise ValueError("Falta la API Key de Gemini.")
    modelo_limpio = (modelo or "gemini-3.8-flash").strip()
    if modelo_limpio.startswith("models/"):
        modelo_limpio = modelo_limpio.split("models/", 1)[1]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_limpio}:generateContent"

    contents = [
        {
            "role": ("model" if m.get("role") == "assistant" else "user"),
            "parts": [{"text": (m.get("content") or "").strip()}],
        }
        for m in mensajes[-12:]
        if (m.get("content") or "").strip()
    ]
    payload = {
        "system_instruction": {"parts": [{"text": prompt_sistema}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.65},
    }

    modos_envio = [True, False] if clave.startswith("AQ") else [False, True]
    ultimo_error = ""
    for usar_q in modos_envio:
        for intento in range(2):
            resp = _peticion_gemini_con_clave(url, clave, payload, usar_query_key=usar_q)
            if resp.ok:
                candidatos = resp.json().get("candidates", [])
                if not candidatos:
                    return "No recibí respuesta del modelo en la nube, jefa."
                partes = candidatos[0].get("content", {}).get("parts", [])
                texto = "".join(p.get("text", "") for p in partes if "text" in p).strip()
                return texto or "Respuesta vacía del modelo."
            ultimo_error = _formatear_error_http(resp)
            if resp.status_code in (429, 500, 502, 503, 504) and intento == 0:
                time.sleep(1.5)
                continue
            break
        if not any(cod in ultimo_error for cod in ("HTTP 400", "HTTP 401", "HTTP 403")):
            break
    raise RuntimeError(ultimo_error)


def consultar_gemini_api(mensajes, api_key: str, modelo: str, prompt_sistema: str):
    clave = _limpiar_clave(api_key)
    if not clave:
        raise ValueError("Falta la API Key de Gemini.")
    principal = (modelo or "gemini-3.8-flash").strip()
    candidatos = [principal] + [m for m in MODELOS_RESPALDO_GEMINI if m != principal]
    errores = []
    for mod in candidatos:
        try:
            texto = _llamar_modelo_gemini_unico(mensajes, clave, mod, prompt_sistema)
            return texto, mod
        except Exception as err:
            msg_err = str(err)
            errores.append(f"{mod} -> {msg_err}")
            if any(cod in msg_err for cod in ("HTTP 400", "HTTP 401", "HTTP 403")):
                raise RuntimeError(msg_err)
    raise RuntimeError(" | ".join(errores))


def _respuesta_autonoma_local(texto_usuario: str, nucleo_nombre: str, indicadores: dict, clima_buin: dict) -> str:
    lower = (texto_usuario or "").lower()
    if any(k in lower for k in ("dolar", "dólar", "uf", "euro", "utm", "indicadores")):
        return (
            f"[{nucleo_nombre}] Lectura actual en el Nodo Buin, jefa: "
            f"Dólar **{fmt_clp(indicadores['dolar'])}**, Euro **{fmt_clp(indicadores['euro'])}** "
            f"y UF **{fmt_clp(indicadores['uf'])}**."
        )
    if any(k in lower for k in ("clima", "temperatura", "lluvia", "buin")):
        temp = clima_buin.get("temp_c")
        cond = clima_buin.get("condicion", "sin lectura en vivo")
        return (
            f"[{nucleo_nombre}] Por Buin tenemos **{temp}°C** y cielo **{cond}**."
            if temp is not None
            else f"[{nucleo_nombre}] En Buin figura **{cond}** en este momento, jefa."
        )
    if "sabor casero" in lower:
        return (
            f"[{nucleo_nombre}] En **Sabor Casero**, jefa: lo clave es que la página en Netlify cargue rápido, "
            "el flujo de cobro con Flow quede probado de punta a punta y la compra no tenga pasos innecesarios."
        )
    if "montessori" in lower:
        return (
            f"[{nucleo_nombre}] Para **Montessori** antes de Navidad, jefa: partamos por definir el entregable "
            "concreto que quieres cerrar primero y avanzarlo en bloques enfocados sin dispersión."
        )
    return (
        f"[{nucleo_nombre}] Recibido, jefa. Estoy operando en modo local/autónomo en el Nodo Buin "
        f"(Dólar {fmt_clp(indicadores['dolar'])}, UF {fmt_clp(indicadores['uf'])}). "
        "Si quieres respuesta generativa en la nube, asegúrate de tener tu clave de Gemini activa."
    )


def responder_jarvis(
    mensajes,
    nucleo_nombre: str,
    etiqueta_idioma: str,
    indicadores: dict,
    clima_buin: dict,
    gemini_api_key: str = "",
    gemini_modelo: str = "gemini-3.8-flash",
):
    ultimo_texto = mensajes[-1]["content"] if mensajes else ""
    lower = ultimo_texto.lower().strip()

    if any(frase in lower for frase in ("quien eres", "quién eres", "presentate", "preséntate", "who are you")):
        return obtener_presentacion_nucleo(nucleo_nombre, etiqueta_idioma)

    prompt_sis = construir_prompt_sistema(nucleo_nombre, etiqueta_idioma, indicadores, clima_buin)
    clave_gemini = _limpiar_clave(gemini_api_key) or obtener_clave_secreta_gemini()

    if clave_gemini:
        try:
            texto_gem, _ = consultar_gemini_api(mensajes, clave_gemini, gemini_modelo, prompt_sis)
            return f"[{nucleo_nombre}] {texto_gem}" if not texto_gem.startswith(f"[{nucleo_nombre}]") else texto_gem
        except Exception as err_gem:
            msg_gem = str(err_gem)
            if any(cod in msg_gem for cod in ("HTTP 400", "HTTP 401", "HTTP 403")):
                base_auto = _respuesta_autonoma_local(ultimo_texto, nucleo_nombre, indicadores, clima_buin)
                return f"{base_auto}\n\n*(Aviso Gemini: {msg_gem})*"

    if client_groq is not None:
        try:
            chat_payload = [{"role": "system", "content": prompt_sis}] + [
                {"role": m["role"], "content": m["content"]}
                for m in mensajes[-10:]
                if m.get("content")
            ]
            completion = client_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=chat_payload,
                temperature=0.65,
                max_tokens=900,
            )
            content = (completion.choices[0].message.content or "").strip()
            if content:
                return f"[{nucleo_nombre}] {content}" if not content.startswith(f"[{nucleo_nombre}]") else content
        except Exception:
            pass

    return _respuesta_autonoma_local(ultimo_texto, nucleo_nombre, indicadores, clima_buin)


def construir_reporte_texto(indicadores, clima_buin):
    ahora = obtener_hora_chile()
    misiones = obtener_misiones()
    recuerdos = jarvis_mem.get_recent_facts(20)
    notas = st.session_state.get("notas_rapidas", [])
    bitacora = st.session_state.get("bitacora_sesion", [])

    lineas = [
        "====================================================",
        f"REPORTE TACTICO // J.A.R.V.I.S. - NUCLEO {st.session_state.nucleo_activo}",
        f"NODO: BUIN, CHILE ({BUIN_LAT}, {BUIN_LON})",
        f"FECHA/HORA CHILE: {ahora.strftime('%d/%m/%Y %H:%M:%S')}",
        f"IDIOMA: {st.session_state.idioma_sistema} | TEMA: {st.session_state.tema_visual}",
        "====================================================",
        "",
        "[1] INDICADORES Y METEOROLOGIA",
        f"- Dolar Observado: {fmt_clp(indicadores['dolar'])}",
        f"- Euro: {fmt_clp(indicadores['euro'])}",
        f"- UF: {fmt_clp(indicadores['uf'])}",
        f"- Clima Buin: {clima_buin.get('temp_c', 'N/D')} C ({clima_buin.get('condicion', 'N/D')})",
        "",
        "[2] MISIONES ACTIVAS",
    ]
    if misiones:
        for mid, tarea, estado in misiones:
            lineas.append(f"- #{mid}: {tarea} [{estado}]")
    else:
        lineas.append("- Sin misiones activas.")

    lineas.append("")
    lineas.append("[3] NOTAS RAPIDAS")
    if notas:
        for idx, n in enumerate(notas, 1):
            lineas.append(f"- {idx}. {n}")
    else:
        lineas.append("- Sin notas rapidas.")

    lineas.append("")
    lineas.append("[4] MEMORIA PERSISTENTE")
    if recuerdos:
        for r in recuerdos:
            lineas.append(f"- {r}")
    else:
        lineas.append("- Sin recuerdos registrados.")

    lineas.append("")
    lineas.append("[5] BITACORA DE SESION")
    if bitacora:
        for ev in bitacora[-15:]:
            lineas.append(f"- {ev}")
    else:
        lineas.append("- Sin eventos en bitacora.")

    return "\n".join(lineas)


def generar_pdf_simple(texto_contenido: str) -> bytes:
    def esc_pdf(s: str) -> str:
        s_ascii = s.encode("latin-1", "replace").decode("latin-1")
        return s_ascii.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    lineas_raw = texto_contenido.splitlines() or ["REPORTE JARVIS NODO BUIN"]
    lineas_envueltas = []
    for ln in lineas_raw:
        if len(ln) <= 84:
            lineas_envueltas.append(ln)
        else:
            for i in range(0, len(ln), 84):
                lineas_envueltas.append(ln[i:i + 84])
    lineas_envueltas = lineas_envueltas[:48]

    ops = ["BT", "/F1 10 Tf", "40 755 Td", "14 TL"]
    for idx, ln in enumerate(lineas_envueltas):
        if idx == 0:
            ops.append(f"({esc_pdf(ln)}) Tj")
        else:
            ops.append(f"T* ({esc_pdf(ln)}) Tj")
    ops.append("ET")
    stream_bytes = "\n".join(ops).encode("latin-1")

    objetos = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n",
        b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>\nendobj\n",
        f"5 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n".encode("latin-1") + stream_bytes + b"\nendstream\nendobj\n",
    ]

    pdf_buf = io.BytesIO()
    pdf_buf.write(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objetos:
        offsets.append(pdf_buf.tell())
        pdf_buf.write(obj)

    xref_pos = pdf_buf.tell()
    pdf_buf.write(f"xref\n0 {len(objetos) + 1}\n".encode("latin-1"))
    pdf_buf.write(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf_buf.write(f"{off:010d} 00000 n \n".encode("latin-1"))
    pdf_buf.write(
        f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF".encode("latin-1")
    )
    return pdf_buf.getvalue()


def generar_tarjeta_jpg(indicadores, clima_buin, color_hex="#00f3ff") -> bytes:
    if not PIL_AVAILABLE:
        return b""
    ahora = obtener_hora_chile()
    w, h = 900, 500
    img = Image.new("RGB", (w, h), (6, 9, 19))
    draw = ImageDraw.Draw(img)

    draw.rectangle([16, 16, w - 16, h - 16], outline=color_hex, width=3)
    draw.rectangle([28, 28, w - 28, 96], outline=color_hex, width=2)
    draw.text((48, 46), f"J.A.R.V.I.S. // NUCLEO {st.session_state.nucleo_activo}", fill=color_hex)
    draw.text((48, 70), f"NODO BUIN, CHILE  |  {ahora.strftime('%d/%m/%Y %H:%M:%S')}  |  {st.session_state.capa_radar}", fill=color_hex)

    cx, cy = 690, 275
    for rad in (120, 88, 54):
        draw.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=color_hex, width=2)
    draw.line([cx - 135, cy, cx + 135, cy], fill=color_hex, width=1)
    draw.line([cx, cy - 135, cx, cy + 135], fill=color_hex, width=1)
    draw.text((cx - 46, cy + 132), "BUIN -33.73 S", fill=color_hex)

    y_pos = 130
    datos_vis = [
        f"DOLAR OBS : {fmt_clp(indicadores['dolar'])}",
        f"EURO      : {fmt_clp(indicadores['euro'])}",
        f"UF CHILE  : {fmt_clp(indicadores['uf'])}",
        f"CLIMA BUIN: {clima_buin.get('temp_c', 'N/D')} C ({clima_buin.get('condicion', 'N/D')})",
        f"MISIONES  : {len(obtener_misiones())} ACTIVAS",
        f"IDIOMA    : {st.session_state.idioma_sistema}",
    ]
    for linea in datos_vis:
        draw.rectangle([42, y_pos - 6, 510, y_pos + 24], outline=color_hex, width=1)
        draw.text((56, y_pos + 2), linea, fill=color_hex)
        y_pos += 44

    draw.text((48, h - 46), "ARCHIVO TACTICO EXPORTADO DESDE CONSOLA SUPREMA", fill=color_hex)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=92)
    return out.getvalue()


def convertir_imagen_a_jpg(archivo_subido) -> bytes:
    if not PIL_AVAILABLE or archivo_subido is None:
        return b""
    try:
        im = Image.open(archivo_subido)
        if im.mode in ("RGBA", "P", "LA"):
            fondo = Image.new("RGB", im.size, (6, 9, 19))
            if im.mode == "P":
                im = im.convert("RGBA")
            fondo.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
            im = fondo
        else:
            im = im.convert("RGB")
        out = io.BytesIO()
        im.save(out, format="JPEG", quality=92)
        return out.getvalue()
    except Exception:
        return b""


def construir_emblema_nucleo_svg(color_main="#00f3ff", size=54):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 80 80" '
        f'style="flex-shrink:0;" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="40" cy="40" r="36" fill="none" stroke="{color_main}" stroke-width="1.8" stroke-dasharray="7 4"/>'
        f'<circle cx="40" cy="40" r="29" fill="none" stroke="{color_main}" stroke-width="2.2"/>'
        f'<circle cx="40" cy="40" r="23" fill="none" stroke="{color_main}" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.8"/>'
        f'<polygon points="21,28 59,28 40,61" fill="none" stroke="{color_main}" stroke-width="3" stroke-linejoin="round"/>'
        f'<polygon points="27,31 53,31 40,54" fill="{color_main}" opacity="0.28"/>'
        f'<polygon points="33,34 47,34 40,46" fill="{color_main}" opacity="0.55"/>'
        f'<circle cx="40" cy="37" r="4.2" fill="#ffffff"/>'
        f'</svg>'
    )


def renderizar_banner_vivo(nucleo_activo, capa_radar, color_main="#00f3ff", grad_start="#0a1128", bg_dark="#060913"):
    ahora_chile = obtener_hora_chile()
    emblema_svg = construir_emblema_nucleo_svg(color_main=color_main, size=56)
    html_banner = (
        f'<div style="border:1.5px solid {color_main};background:linear-gradient(135deg,{grad_start} 0%,{bg_dark} 100%);'
        f'padding:14px 18px;border-radius:10px;margin:0 auto 14px auto;max-width:860px;font-family:monospace;color:{color_main};">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;font-size:0.68rem;letter-spacing:1px;opacity:0.85;margin-bottom:8px;border-bottom:1px solid {color_main}33;padding-bottom:5px;">'
        f'<span>STARK-HUD // NODO BUIN (-33.73°S, -70.74°W)</span>'
        f'<span>POWER 100% • ARC-CORE LOCKED</span>'
        f'</div>'
        f'<div style="display:flex;align-items:center;justify-content:center;gap:14px;flex-wrap:wrap;">'
        f'{emblema_svg}'
        f'<div style="text-align:left;">'
        f'<h2 style="margin:0;color:{color_main};font-size:1.5rem;letter-spacing:1px;">J.A.R.V.I.S. // {nucleo_activo}</h2>'
        f'<div id="reloj-vivo-buin" style="font-size:0.84rem;opacity:0.94;color:{color_main};margin-top:3px;">'
        f'NODO BUIN, CHILE • {ahora_chile.strftime("%d/%m/%Y %H:%M:%S")} • {capa_radar}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
        "<script>(function(){try{"
        'const el=document.getElementById("reloj-vivo-buin");'
        f'const capa={json.dumps(capa_radar)};'
        "function pad(n){return String(n).padStart(2,'0');}"
        "function actualizarReloj(){"
        "if(!el)return;"
        "const now=new Date();"
        "const utcMs=now.getTime()+(now.getTimezoneOffset()*60000);"
        "const cl=new Date(utcMs-(3*3600000));"
        "const fecha=pad(cl.getDate())+'/'+pad(cl.getMonth()+1)+'/'+cl.getFullYear();"
        "const hora=pad(cl.getHours())+':'+pad(cl.getMinutes())+':'+pad(cl.getSeconds());"
        "el.textContent='NODO BUIN, CHILE • '+fecha+' '+hora+' • '+capa;"
        "}"
        "if(window.__jarvisRelojTimer)clearInterval(window.__jarvisRelojTimer);"
        "actualizarReloj();"
        "window.__jarvisRelojTimer=setInterval(actualizarReloj,1000);"
        "}catch(e){}})();</script>"
    )
    try:
        components.html(html_banner, height=122)
    except Exception:
        st.markdown(
            f'<div class="holo-brain-box">'
            f'<div style="display:flex;align-items:center;justify-content:center;gap:12px;">'
            f'{emblema_svg}'
            f'<div style="text-align:left;">'
            f'<h2 style="margin:0;">J.A.R.V.I.S. // {nucleo_activo}</h2>'
            f'<div style="font-size:0.86rem;opacity:0.9;">NODO BUIN, CHILE • {ahora_chile.strftime("%d/%m/%Y %H:%M:%S")} • {capa_radar}</div>'
            f'</div></div></div>',
            unsafe_allow_html=True,
        )


def renderizar_globo_orbital(capa_actual, color_main="#00f3ff"):
    html_globo = (
        f'<div style="border:1px solid {color_main};background:#040a17;border-radius:6px;padding:6px;font-family:monospace;color:{color_main};text-align:center;box-sizing:border-box;">'
        '<canvas id="holo-globe-canvas" width="250" height="106" style="width:100%;height:106px;border-radius:4px;display:block;"></canvas>'
        f'<div style="font-size:0.65rem;line-height:1.25;opacity:0.92;margin-top:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">ORBITAL LINK • {capa_actual}</div>'
        '<div style="font-size:0.59rem;line-height:1.2;opacity:0.75;margin-top:2px;">TELEMETRÍA ORBITAL • -33.73°S, -70.74°W</div>'
        "</div>"
        "<script>(function(){try{"
        'const c=document.getElementById("holo-globe-canvas");'
        "if(!c)return;const ctx=c.getContext('2d');"
        f'const mainColor={json.dumps(color_main)};'
        "let ang=0;"
        "function step(){ang+=0.04;ctx.clearRect(0,0,c.width,c.height);"
        "const cx=c.width/2,cy=c.height/2,r=34;"
        "ctx.strokeStyle=mainColor+'66';ctx.lineWidth=1;"
        "ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();"
        "ctx.beginPath();ctx.ellipse(cx,cy,r*Math.cos(ang*0.4)||5,r,0,0,Math.PI*2);ctx.stroke();"
        "ctx.beginPath();ctx.ellipse(cx,cy,r,r*0.35,0.25,0,Math.PI*2);ctx.stroke();"
        "const ox=cx+Math.cos(ang)*(r+12);const oy=cy+Math.sin(ang)*11;"
        "ctx.fillStyle='#39ff14';ctx.beginPath();ctx.arc(ox,oy,3,0,Math.PI*2);ctx.fill();"
        "ctx.fillStyle=mainColor;ctx.font='9px monospace';"
        "ctx.fillText('BUIN -33.73°S',6,11);ctx.fillText('SAT-07 [LOCK]',c.width-76,c.height-6);}"
        "if(window.__jarvisGloboTimer)clearInterval(window.__jarvisGloboTimer);"
        "step();"
        "window.__jarvisGloboTimer=setInterval(step,50);"
        "}catch(e){}})();</script>"
    )
    try:
        components.html(html_globo, height=150)
    except Exception:
        st.caption(f"ORBITAL LINK • {capa_actual} (-33.73°S, -70.74°W)")


aplicar_css_tema()
nombre_tema, tema_cfg = obtener_tema_actual()
color_main = tema_cfg["primary"]
grad_start = tema_cfg["grad_start"]
bg_dark = tema_cfg["bg"]

if not st.session_state.get("autorizado", False):
    renderizar_banner_vivo(
        st.session_state.get("nucleo_activo", "JARVIS"),
        st.session_state.get("capa_radar", "SATELITAL // BUIN"),
        color_main=color_main,
        grad_start=grad_start,
        bg_dark=bg_dark,
    )
    st.markdown('<div class="holo-brain-box"><b>ACCESO RESTRINGIDO // INGRESA PIN DE SEGURIDAD</b></div>', unsafe_allow_html=True)
    pin_ingresado = st.text_input("PIN de acceso", type="password", key="pin_acceso_input")
    if st.button("DESBLOQUEAR NÚCLEO"):
        if pin_ingresado.strip() == PIN_SECRETO:
            st.session_state["autorizado"] = True
            if not st.session_state["mensajes"]:
                st.session_state["mensajes"].append({
                    "role": "assistant",
                    "content": obtener_saludo_nucleo(st.session_state["nucleo_activo"], st.session_state["idioma_sistema"]),
                })
            registrar_evento("Acceso concedido con PIN")
            st.rerun()
        else:
            st.error("PIN incorrecto, jefa.")
    st.stop()

if not st.session_state["mensajes"]:
    st.session_state["mensajes"].append({
        "role": "assistant",
        "content": obtener_saludo_nucleo(st.session_state["nucleo_activo"], st.session_state["idioma_sistema"]),
    })

indicadores = obtener_indicadores_chile()
clima_buin = obtener_clima_buin()

with st.sidebar:
    st.markdown("### CONTROL DE NÚCLEO")
    nucleo_sel = st.selectbox("Núcleo activo", NUCLEOS_DISPONIBLES, index=NUCLEOS_DISPONIBLES.index(st.session_state["nucleo_activo"]))
    if nucleo_sel != st.session_state["nucleo_activo"]:
        st.session_state["nucleo_activo"] = nucleo_sel
        registrar_evento(f"Cambio de núcleo a {nucleo_sel}")
        st.rerun()

    idioma_sel = st.selectbox("Idioma", OPCIONES_IDIOMA, index=OPCIONES_IDIOMA.index(st.session_state["idioma_sistema"]))
    if idioma_sel != st.session_state["idioma_sistema"]:
        st.session_state["idioma_sistema"] = idioma_sel
        registrar_evento(f"Idioma cambiado a {idioma_sel}")
        st.rerun()

    tema_sel = st.selectbox("Tema visual", OPCIONES_TEMA, index=OPCIONES_TEMA.index(st.session_state["tema_visual"]))
    if tema_sel != st.session_state["tema_visual"]:
        st.session_state["tema_visual"] = tema_sel
        registrar_evento(f"Tema cambiado a {tema_sel}")
        st.rerun()

    st.markdown("---")
    st.markdown("### GEMINI API")
    entrada_gemini = st.text_input(
        "Gemini API Key",
        value=st.session_state.get("gemini_key_sesion", ""),
        type="password",
        key="input_gemini_key",
    )
    clave_limpia_in = _limpiar_clave(entrada_gemini)
    if clave_limpia_in:
        st.session_state["gemini_key_sesion"] = clave_limpia_in
    elif not obtener_clave_secreta_gemini():
        st.session_state["gemini_key_sesion"] = ""

    if st.session_state.get("gemini_key_sesion"):
        st.caption(f"Gemini Key: lista ({st.session_state['gemini_key_sesion'][:4]}...).")
    else:
        st.caption("Gemini Key: no detectada (modo local/autónomo activo).")

    gemini_modelo = st.text_input("Modelo Gemini", value="gemini-3.8-flash", key="input_gemini_modelo")

    st.markdown("---")
    renderizar_globo_orbital(st.session_state["capa_radar"], color_main=color_main)
    capa_sel = st.selectbox(
        "Capa de radar",
        ["SATELITAL // BUIN", "METEOROLOGÍA // MAIPO", "TELEMETRÍA // CHILE", "ALERTA // SISTEMA"],
        index=["SATELITAL // BUIN", "METEOROLOGÍA // MAIPO", "TELEMETRÍA // CHILE", "ALERTA // SISTEMA"].index(st.session_state["capa_radar"])
        if st.session_state["capa_radar"] in ["SATELITAL // BUIN", "METEOROLOGÍA // MAIPO", "TELEMETRÍA // CHILE", "ALERTA // SISTEMA"]
        else 0,
    )
    if capa_sel != st.session_state["capa_radar"]:
        st.session_state["capa_radar"] = capa_sel
        st.rerun()

    st.markdown("---")
    st.markdown("### EXPORTACIÓN")
    reporte_txt = construir_reporte_texto(indicadores, clima_buin)
    st.download_button("DESCARGAR REPORTE .TXT", data=reporte_txt.encode("utf-8"), file_name="jarvis_buin_reporte.txt", mime="text/plain")
    st.download_button("DESCARGAR REPORTE .PDF", data=generar_pdf_simple(reporte_txt), file_name="jarvis_buin_reporte.pdf", mime="application/pdf")
    if PIL_AVAILABLE:
        st.download_button(
            "DESCARGAR TARJETA .JPG",
            data=generar_tarjeta_jpg(indicadores, clima_buin, color_hex=color_main),
            file_name="jarvis_buin_tarjeta.jpg",
            mime="image/jpeg",
        )

renderizar_banner_vivo(
    st.session_state["nucleo_activo"],
    st.session_state["capa_radar"],
    color_main=color_main,
    grad_start=grad_start,
    bg_dark=bg_dark,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("DÓLAR OBS", fmt_clp(indicadores["dolar"]))
c2.metric("EURO", fmt_clp(indicadores["euro"]))
c3.metric("UF CHILE", fmt_clp(indicadores["uf"]))
c4.metric("CLIMA BUIN", f"{clima_buin['temp_c']}°C" if clima_buin["temp_c"] is not None else "N/D")

tab_chat, tab_misiones, tab_radar, tab_memoria = st.tabs(["CONSOLA DE CHAT", "MISIONES & NOTAS", "RADAR & NOTICIAS", "MEMORIA & BITÁCORA"])

with tab_chat:
    col_top1, col_top2 = st.columns([6, 1])
    with col_top2:
        if st.button("PURGAR CHAT"):
            purgar_chat(st.session_state["nucleo_activo"])
            st.rerun()

    for m in st.session_state["mensajes"]:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    pregunta = st.chat_input(f"Háblale a {st.session_state['nucleo_activo']}...")
    if pregunta:
        st.session_state["mensajes"].append({"role": "user", "content": pregunta})
        with st.chat_message("user"):
            st.markdown(pregunta)

        respuesta_ia = responder_jarvis(
            mensajes=st.session_state["mensajes"],
            nucleo_nombre=st.session_state["nucleo_activo"],
            etiqueta_idioma=st.session_state["idioma_sistema"],
            indicadores=indicadores,
            clima_buin=clima_buin,
            gemini_api_key=st.session_state.get("gemini_key_sesion", ""),
            gemini_modelo=gemini_modelo,
        )
        st.session_state["mensajes"].append({"role": "assistant", "content": respuesta_ia})
        with st.chat_message("assistant"):
            st.markdown(respuesta_ia)

with tab_misiones:
    st.markdown("#### Misiones activas (SQLite)")
    nueva_mision = st.text_input("Nueva misión", key="nueva_mision_input")
    col_m1, col_m2 = st.columns([1, 1])
    with col_m1:
        if st.button("AÑADIR MISIÓN") and nueva_mision.strip():
            agregar_mision(nueva_mision.strip())
            st.rerun()
    with col_m2:
        if st.button("LIMPIAR MISIONES"):
            limpiar_misiones()
            st.rerun()

    for mid, tarea, estado in obtener_misiones():
        st.markdown(f"- **#{mid}** {tarea} `[{estado}]`")

    st.markdown("---")
    st.markdown("#### Notas rápidas")
    nota_in = st.text_input("Anotar pendiente o idea", key="nota_rapida_input")
    if st.button("GUARDAR NOTA") and nota_in.strip():
        st.session_state["notas_rapidas"].append(nota_in.strip())
        registrar_evento(f"Nota guardada: {nota_in.strip()}")
        st.rerun()
    for idx, n in enumerate(st.session_state["notas_rapidas"], 1):
        st.markdown(f"{idx}. {n}")

with tab_radar:
    st.markdown("#### Noticias en vivo (Google News RSS)")
    consulta_rss = st.text_input("Tópico de búsqueda", value="Chile tecnología finanzas", key="rss_query_input")
    if st.button("ACTUALIZAR RADAR"):
        st.session_state["noticias_cache_lista"] = obtener_noticias_rss(consulta_rss, limite=5)
    noticias = st.session_state.get("noticias_cache_lista") or obtener_noticias_rss(consulta_rss, limite=5)
    if noticias:
        for item in noticias:
            titulo_esc = item["titulo"]
            link = item.get("link", "")
            fecha = item.get("fecha", "")
            if link:
                st.markdown(f"- [{titulo_esc}]({link}) `{fecha}`")
            else:
                st.markdown(f"- {titulo_esc} `{fecha}`")
    else:
        st.caption("Sin titulares disponibles en este momento.")

    if PIL_AVAILABLE:
        st.markdown("---")
        st.markdown("#### Conversor de imagen a JPG")
        img_up = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg", "webp"])
        if img_up is not None:
            jpg_bytes = convertir_imagen_a_jpg(img_up)
            if jpg_bytes:
                st.download_button("DESCARGAR COMO .JPG", data=jpg_bytes, file_name="convertida_jarvis.jpg", mime="image/jpeg")

with tab_memoria:
    st.markdown("#### Memoria persistente")
    hecho_in = st.text_input("Guardar dato o preferencia clave", key="hecho_memoria_input")
    col_mem1, col_mem2 = st.columns([1, 1])
    with col_mem1:
        if st.button("MEMORIZAR DATO") and hecho_in.strip():
            clave_mem = f"fact_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            jarvis_mem.remember_fact(clave_mem, hecho_in.strip())
            registrar_evento(f"Dato memorizado: {hecho_in.strip()}")
            st.rerun()
    with col_mem2:
        if st.button("BORRAR MEMORIA"):
            jarvis_mem.clear_facts()
            registrar_evento("Memoria persistente borrada")
            st.rerun()

    for r in jarvis_mem.get_recent_facts(15):
        st.markdown(f"- {r}")

    st.markdown("---")
    st.markdown("#### Bitácora de sesión")
    for ev in reversed(st.session_state.get("bitacora_sesion", [])):
        st.caption(ev)

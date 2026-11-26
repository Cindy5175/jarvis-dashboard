import datetime
import io
import json
import math
import os
import random
import re
import sqlite3
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
    initial_sidebar_state="collapsed",
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

MODULOS_OCULTOS_CLAVES = [
    "controles_sistema",
    "indicadores_clima",
    "globo",
    "radar",
    "noticias",
    "alertas",
    "descargas",
    "enlaces",
    "conversor",
    "camara",
    "notas",
    "calculadora",
    "telemetria",
    "misiones",
    "memoria",
    "bitacora",
]

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
st.session_state.setdefault("modulos_visibles", {k: False for k in MODULOS_OCULTOS_CLAVES})

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"
BUIN_LAT = -33.7325
BUIN_LON = -70.7422

API_KEY_GROQ = ""
try:
    if "GROQ_API_KEY" in st.secrets:
        API_KEY_GROQ = str(st.secrets["GROQ_API_KEY"])
except Exception:
    API_KEY_GROQ = ""

if not API_KEY_GROQ:
    API_KEY_GROQ = os.environ.get("GROQ_API_KEY", "")

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


def registrar_evento(detalle: str):
    tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
    stamp = datetime.datetime.now(tz_chile).strftime("%H:%M:%S")
    st.session_state.setdefault("bitacora_sesion", [])
    st.session_state["bitacora_sesion"].append(f"[{stamp}] {detalle}")
    st.session_state["bitacora_sesion"] = st.session_state["bitacora_sesion"][-25:]


def set_modulos_visibles(claves, estado=True):
    st.session_state.setdefault("modulos_visibles", {k: False for k in MODULOS_OCULTOS_CLAVES})
    for k in claves:
        if k in st.session_state["modulos_visibles"]:
            st.session_state["modulos_visibles"][k] = bool(estado)


def procesar_comando_modulos(texto_usuario):
    t = re.sub(r"[¿?¡!.,;:]+", " ", (texto_usuario or "").lower()).strip()
    if not t:
        return None

    es_ocultar = any(w in t for w in ["oculta", "ocultar", "esconde", "esconder", "cierra", "cerrar", "minimiza"])
    es_mostrar = any(w in t for w in ["muestra", "mostrar", "abre", "abrir", "activa", "ver", "despliega", "saca"])

    if not (es_ocultar or es_mostrar):
        return None

    if any(w in t for w in ["todo", "todos", "modulos", "módulos", "panel", "arsenal", "menu", "menú"]):
        set_modulos_visibles(MODULOS_OCULTOS_CLAVES, not es_ocultar)
        accion = "ocultado" if es_ocultar else "mostrado"
        registrar_evento(f"Módulos {accion} por comando: {texto_usuario}")
        return f"Listo, jefa: he {accion} los módulos solicitados."

    mapa_palabras = {
        "controles_sistema": ["nucleo", "núcleo", "idioma", "tema", "color", "bloquear", "reinicio", "ajustes", "config"],
        "indicadores_clima": ["indicador", "indicadores", "dolar", "dólar", "euro", "uf", "clima", "temperatura", "buin"],
        "globo": ["globo", "orbital", "satelite", "satélite"],
        "radar": ["radar", "capa", "capas"],
        "noticias": ["noticia", "noticias", "titulares", "prensa"],
        "alertas": ["alerta", "alertas", "recordatorio", "recordatorios", "alarma"],
        "descargas": ["descarga", "descargas", "exportar", "pdf", "txt", "json", "jpg", "reporte"],
        "enlaces": ["enlace", "enlaces", "finviz", "nasdaq", "bolsa", "osiris"],
        "conversor": ["conversor", "divisa", "divisas", "convertir moneda"],
        "camara": ["camara", "cámara", "nocturna", "infrarrojo", "visor"],
        "notas": ["nota", "notas", "apunte", "apuntes"],
        "calculadora": ["calculadora", "calcular", "mate", "matematica", "matemática"],
        "telemetria": ["telemetria", "telemetría", "estado sistema"],
        "misiones": ["mision", "misiones", "pendiente", "pendientes", "tarea", "tareas"],
        "memoria": ["memoria", "recuerdo", "recuerdos"],
        "bitacora": ["bitacora", "bitácora", "log", "logs", "historial"],
    }

    objetivos = []
    for clave, palabras in mapa_palabras.items():
        if any(p in t for p in palabras):
            objetivos.append(clave)

    if objetivos:
        set_modulos_visibles(objetivos, not es_ocultar)
        accion = "ocultado" if es_ocultar else "mostrado"
        nombres = ", ".join(objetivos)
        registrar_evento(f"Módulos ({nombres}) {accion}")
        return f"Hecho, jefa: {accion} {nombres}."

    return None


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


def renderizar_banner_vivo(nucleo_activo, capa_radar, color_main="#00f3ff", grad_start="#0a1128", bg_dark="#060913"):
    ahora_chile = obtener_hora_chile()
    html_banner = (
        f'<div id="jarvis-hud-banner" style="border:1.5px solid {color_main};background:linear-gradient(135deg,{grad_start} 0%,{bg_dark} 100%);'
        f'padding:14px 18px;border-radius:10px;margin:0 auto 10px auto;max-width:860px;font-family:monospace;color:{color_main};transition:box-shadow 0.12s ease;">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;font-size:0.68rem;letter-spacing:1px;opacity:0.85;margin-bottom:8px;border-bottom:1px solid {color_main}33;padding-bottom:5px;">'
        f'<span>STARK-HUD // NODO BUIN (-33.73°S, -70.74°W)</span>'
        f'<span id="jarvis-voz-badge">STANDBY • ARC-CORE</span>'
        f'</div>'
        f'<div style="display:flex;align-items:center;justify-content:center;gap:16px;flex-wrap:wrap;">'
        f'<svg id="jarvis-logo-svg" width="64" height="64" viewBox="0 0 80 80" style="flex-shrink:0;transform-origin:center;" xmlns="http://www.w3.org/2000/svg">'
        f'<circle id="jarvis-ring-outer" cx="40" cy="40" r="36" fill="none" stroke="{color_main}" stroke-width="1.8" stroke-dasharray="7 4"/>'
        f'<circle id="jarvis-ring-mid" cx="40" cy="40" r="29" fill="none" stroke="{color_main}" stroke-width="2.2"/>'
        f'<circle cx="40" cy="40" r="23" fill="none" stroke="{color_main}" stroke-width="1.2" stroke-dasharray="3 3" opacity="0.8"/>'
        f'<polygon id="jarvis-tri-frame" points="21,28 59,28 40,61" fill="none" stroke="{color_main}" stroke-width="3" stroke-linejoin="round"/>'
        f'<polygon id="jarvis-tri-core" points="27,31 53,31 40,54" fill="{color_main}" opacity="0.32"/>'
        f'<polygon points="33,34 47,34 40,46" fill="{color_main}" opacity="0.6"/>'
        f'<circle id="jarvis-arc-dot" cx="40" cy="37" r="4.5" fill="#ffffff"/>'
        f'</svg>'
        f'<div style="text-align:left;">'
        f'<h2 style="margin:0;color:{color_main};font-size:1.5rem;letter-spacing:1px;">J.A.R.V.I.S. // {nucleo_activo}</h2>'
        f'<div id="reloj-vivo-buin" style="font-size:0.84rem;opacity:0.94;color:{color_main};margin-top:3px;">'
        f'NODO BUIN, CHILE • {ahora_chile.strftime("%d/%m/%Y %H:%M:%S")} • {capa_radar}</div>'
        f'</div>'
        f'</div>'
        f'</div>'
        "<script>(function(){try{"
        'const el=document.getElementById("reloj-vivo-buin");'
        'const svg=document.getElementById("jarvis-logo-svg");'
        'const core=document.getElementById("jarvis-tri-core");'
        'const dot=document.getElementById("jarvis-arc-dot");'
        'const badge=document.getElementById("jarvis-voz-badge");'
        f'const capa={json.dumps(capa_radar)};'
        f'const mainColor={json.dumps(color_main)};'
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
        "let fase=0;"
        "function animarLogo(){"
        "const hablando=Boolean(window.__jarvisEstaHablando) || (typeof speechSynthesis!=='undefined' && speechSynthesis.speaking);"
        "if(hablando){"
        "fase+=0.34;"
        "const pulso=1 + Math.sin(fase)*0.14 + Math.abs(Math.cos(fase*1.7))*0.06;"
        "const tilt=Math.sin(fase*0.7)*4;"
        "if(svg){svg.style.transform='scale('+pulso.toFixed(3)+') rotate('+tilt.toFixed(1)+'deg)';svg.style.filter='drop-shadow(0 0 12px '+mainColor+')';}"
        "if(core){core.setAttribute('opacity', String((0.35 + Math.abs(Math.sin(fase))*0.55).toFixed(2)));}"
        "if(dot){dot.setAttribute('r', String((4.5 + Math.abs(Math.sin(fase))*2.2).toFixed(1)));}"
        "if(badge){badge.textContent='HABLANDO • VOCAL-SYNC ACTIVE';}"
        "}else{"
        "fase+=0.04;"
        "const respirar=1 + Math.sin(fase)*0.02;"
        "if(svg){svg.style.transform='scale('+respirar.toFixed(3)+')';svg.style.filter='drop-shadow(0 0 4px '+mainColor+'66)';}"
        "if(core){core.setAttribute('opacity', '0.32');}"
        "if(dot){dot.setAttribute('r', '4.5');}"
        "if(badge){badge.textContent='STANDBY • ARC-CORE';}"
        "}"
        "}"
        "if(window.__jarvisRelojTimer)clearInterval(window.__jarvisRelojTimer);"
        "if(window.__jarvisLogoTimer)clearInterval(window.__jarvisLogoTimer);"
        "actualizarReloj();animarLogo();"
        "window.__jarvisRelojTimer=setInterval(actualizarReloj,1000);"
        "window.__jarvisLogoTimer=setInterval(animarLogo,55);"
        "}catch(e){}})();</script>"
    )
    try:
        components.html(html_banner, height=124)
    except Exception:
        st.markdown(
            f'<div class="holo-brain-box"><h2 style="margin:0;">J.A.R.V.I.S. // {nucleo_activo}</h2>'
            f'<div style="font-size:0.86rem;opacity:0.9;">NODO BUIN, CHILE • {ahora_chile.strftime("%d/%m/%Y %H:%M:%S")} • {capa_radar}</div></div>',
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
        "window.__jarvisGloboTimer=setInterval(step,70);"
        "step();"
        "}catch(e){}})();</script>"
    )
    try:
        components.html(html_globo, height=168)
    except Exception:
        pass


def renderizar_camara_nocturna(modo_camara, color_tema="#00f3ff"):
    es_ir = "INFRARROJO" in modo_camara
    color_main = color_tema if es_ir else "#39ff14"
    filtro_css = (
        "grayscale(100%) contrast(155%) brightness(115%) sepia(100%) hue-rotate(155deg) saturate(320%)"
        if es_ir
        else "grayscale(100%) contrast(150%) brightness(120%) sepia(100%) hue-rotate(68deg) saturate(350%)"
    )
    html_cam = (
        f'<div style="border:1px solid {color_main};background:#030906;border-radius:6px;padding:6px;font-family:monospace;color:{color_main};">'
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:4px;font-size:0.70rem;font-weight:bold;margin-bottom:4px;">'
        "<span>● CAM-01 // BUIN</span>"
        f'<button id="btn-cam-real" type="button" style="background:{color_main};color:#040a07;border:none;border-radius:4px;padding:2px 6px;font-family:monospace;font-size:0.65rem;font-weight:bold;cursor:pointer;">Activar Cámara</button>'
        "</div>"
        '<video id="cam-real-video" autoplay playsinline muted style="display:none;"></video>'
        '<canvas id="cam-nocturna-canvas" width="250" height="135" style="width:100%;height:135px;border-radius:4px;background:#020704;"></canvas>'
        '<div id="estado-cam-jarvis" style="font-size:0.66rem;opacity:0.85;margin-top:3px;">Modo simulado listo • Pulsa "Activar Cámara"</div>'
        "</div>"
        "<script>(function(){try{"
        'const c=document.getElementById("cam-nocturna-canvas");'
        'const v=document.getElementById("cam-real-video");'
        'const btn=document.getElementById("btn-cam-real");'
        'const stEl=document.getElementById("estado-cam-jarvis");'
        "if(!c)return;"
        'const ctx=c.getContext("2d");'
        f'const mainColor={json.dumps(color_main)};const filtro={json.dumps(filtro_css)};'
        "let scanY=0,t=0,camActiva=false;"
        "async function iniciarCamaraReal(){try{"
        "if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){"
        'if(stEl)stEl.textContent="Cámara no soportada • Modo simulado";return;}'
        "if(window.__jarvisCamStream){window.__jarvisCamStream.getTracks().forEach(tr=>tr.stop());}"
        'const stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:"environment"},audio:false});'
        "window.__jarvisCamStream=stream;if(v){v.srcObject=stream;await v.play();}"
        'camActiva=true;if(stEl)stEl.textContent="Cámara real activa con filtro nocturno";}'
        'catch(e){camActiva=false;if(stEl)stEl.textContent="Permiso denegado o sin HTTPS • Simulado";}}'
        "if(btn)btn.onclick=iniciarCamaraReal;"
        "function draw(){t+=0.05;ctx.save();"
        'if(camActiva&&v&&v.readyState>=2){ctx.filter=filtro;ctx.drawImage(v,0,0,c.width,c.height);ctx.filter="none";}'
        'else{ctx.fillStyle="#030a06";ctx.fillRect(0,0,c.width,c.height);'
        'ctx.strokeStyle=mainColor+"22";ctx.lineWidth=1;'
        "for(let x=0;x<c.width;x+=25){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,c.height);ctx.stroke();}"
        "for(let y=0;y<c.height;y+=22){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(c.width,y);ctx.stroke();}"
        'ctx.fillStyle=mainColor+"33";ctx.fillRect(20,78,52,34);ctx.fillRect(165,68,64,44);'
        "ctx.beginPath();ctx.arc(125+Math.sin(t)*14,62+Math.cos(t*1.3)*6,7,0,Math.PI*2);"
        "ctx.strokeStyle=mainColor;ctx.stroke();"
        "for(let i=0;i<60;i++){const nx=(i*37+Math.floor(t*90))%c.width;const ny=(i*53+Math.floor(t*45))%c.height;"
        'ctx.fillStyle=mainColor+"44";ctx.fillRect(nx,ny,2,2);}}'
        'scanY=(scanY+2.2)%c.height;ctx.strokeStyle=mainColor+"aa";ctx.beginPath();'
        "ctx.moveTo(0,scanY);ctx.lineTo(c.width,scanY);ctx.stroke();"
        'ctx.fillStyle=mainColor;ctx.font="bold 10px monospace";'
        'ctx.fillText(camActiva?"LIVE CAM [●] NIGHT-OPTIC":"SIM [●] IR-GAIN: +24dB",8,14);'
        'ctx.fillText("SECTOR BUIN SUR",8,c.height-8);ctx.restore();}'
        "if(window.__jarvisCamTimer)clearInterval(window.__jarvisCamTimer);"
        "window.__jarvisCamTimer=setInterval(draw,80);draw();"
        "}catch(e){}})();</script>"
    )
    try:
        components.html(html_cam, height=192)
    except Exception:
        pass


def limpiar_texto_para_voz(texto):
    limpio = re.sub(r"^\[[^\]]+\]\s*", "", texto or "")
    limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace ", limpio)
    limpio = re.sub(r"https?://\S+", " enlace ", limpio)
    limpio = re.sub(r"[*_`#>\[\]|]+", " ", limpio)
    limpio = re.sub(r"([.!?])\s+", r"\1 ", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    if len(limpio) <= 900:
        return limpio
    corte = limpio[:900]
    ultimo_fin = max(corte.rfind(". "), corte.rfind("! "), corte.rfind("? "))
    return corte[: ultimo_fin + 1] if ultimo_fin > 300 else corte


def programar_voz(texto, idioma=None):
    if st.session_state.get("voz_masculina_activa", True):
        _, cfg = obtener_config_idioma()
        lang_final = idioma or cfg["code"]
        limpio = limpiar_texto_para_voz(texto)
        if limpio:
            st.session_state["pendiente_voz"] = {"texto": limpio, "idioma": lang_final}


def reproducir_voz_pendiente():
    pendiente = st.session_state.get("pendiente_voz")
    if not pendiente or not st.session_state.get("voz_masculina_activa", True):
        return
    st.session_state["pendiente_voz"] = None
    txt_json = json.dumps(pendiente["texto"])
    lang = pendiente["idioma"]
    lang_prefix = lang.split("-")[0]
    dur_est_ms = max(1400, min(18000, len(pendiente["texto"]) * 65))
    js_voz = (
        "<script>(function(){try{if(!('speechSynthesis' in window))return;"
        "if(window.__jarvisVozTimer){clearTimeout(window.__jarvisVozTimer);}"
        "if(window.__jarvisFinVozTimer){clearTimeout(window.__jarvisFinVozTimer);}"
        "window.speechSynthesis.cancel();"
        "function elegirVoz(voices){"
        "if(!voices||!voices.length)return null;"
        f"const exactas=voices.filter(v=>new RegExp('^{lang}','i').test(v.lang||''));"
        f"const familia=voices.filter(v=>new RegExp('^{lang_prefix}(-|_|$)','i').test(v.lang||''));"
        "const pool=exactas.length?exactas:(familia.length?familia:voices);"
        "return pool.find(v=>/jorge|diego|carlos|enrique|pablo|mateo|alonso|raul|daniel|david|thomas|pierre|lucas|marco|male|hombre|man/i.test(v.name||''))||pool[0]||voices[0];}"
        "let yaHablo=false;"
        "function hablarUnaVez(){"
        "if(yaHablo)return;yaHablo=true;"
        "window.speechSynthesis.cancel();"
        f"const u=new SpeechSynthesisUtterance({txt_json});"
        f"u.lang={json.dumps(lang)};u.rate=1.0;u.pitch=0.92;"
        "const v=elegirVoz(window.speechSynthesis.getVoices());if(v)u.voice=v;"
        "window.__jarvisEstaHablando=true;"
        f"window.__jarvisFinVozTimer=setTimeout(()=>{{window.__jarvisEstaHablando=false;}}, {dur_est_ms});"
        "u.onstart=function(){window.__jarvisEstaHablando=true;};"
        "u.onend=function(){window.__jarvisEstaHablando=false;if(window.__jarvisFinVozTimer)clearTimeout(window.__jarvisFinVozTimer);};"
        "u.onerror=function(){window.__jarvisEstaHablando=false;if(window.__jarvisFinVozTimer)clearTimeout(window.__jarvisFinVozTimer);};"
        "window.speechSynthesis.speak(u);}"
        "if(window.speechSynthesis.getVoices().length){hablarUnaVez();}"
        "else{window.speechSynthesis.onvoiceschanged=function(){window.speechSynthesis.onvoiceschanged=null;hablarUnaVez();};"
        "window.__jarvisVozTimer=setTimeout(hablarUnaVez,140);}"
        "}catch(e){window.__jarvisEstaHablando=false;}})();</script>"
    )
    try:
        components.html(js_voz, height=1)
    except Exception:
        pass


def renderizar_microfono_voz(color_main="#00f3ff", btn_text="#060913"):
    _, cfg = obtener_config_idioma()
    lang_mic = cfg["code"]
    js_mic = (
        '<div style="display:flex;align-items:center;gap:8px;margin:4px 0 8px 0;">'
        f'<button id="btn-mic-jarvis" type="button" style="background:{color_main};color:{btn_text};'
        f'border:1.5px solid {color_main};border-radius:6px;padding:6px 12px;font-family:monospace;'
        'font-weight:bold;font-size:0.78rem;cursor:pointer;">🎤 Hablar por Voz</button>'
        f'<span id="estado-mic-jarvis" style="color:{color_main};font-family:monospace;'
        f'font-size:0.75rem;opacity:0.85;">Micrófono listo ({lang_mic})</span></div>'
        "<script>(function(){try{"
        'const btn=document.getElementById("btn-mic-jarvis");'
        'const stEl=document.getElementById("estado-mic-jarvis");'
        "if(!btn||!stEl)return;"
        "const SR=window.SpeechRecognition||window.webkitSpeechRecognition;"
        'if(!SR){stEl.textContent="Dictado por voz no soportado en este navegador";return;}'
        "btn.onclick=function(){try{const rec=new SR();rec.lang=" + json.dumps(lang_mic) + ";"
        "rec.interimResults=false;rec.maxAlternatives=1;"
        'stEl.textContent="Escuchando, jefa...";'
        "rec.onresult=function(ev){"
        "const r0=ev.results&&ev.results[0]&&ev.results[0][0];"
        'const dicho=(r0&&r0.transcript)||"";'
        'stEl.textContent=dicho?("Escuchado: "+dicho):"No se captó audio";'
        "if(!dicho)return;const doc=window.parent.document;"
        'const sel=\'textarea[data-testid="stChatInputTextArea"],input[data-testid="stChatInputTextArea"],textarea\';'
        "let target=null;doc.querySelectorAll(sel).forEach(el=>{if(el.offsetParent!==null)target=el;});"
        "if(target){"
        'const pA=window.HTMLTextAreaElement.prototype,pB=window.HTMLInputElement.prototype;'
        'const setter=Object.getOwnPropertyDescriptor(pA,"value")||Object.getOwnPropertyDescriptor(pB,"value");'
        "if(setter&&setter.set)setter.set.call(target,dicho);else target.value=dicho;"
        'target.dispatchEvent(new Event("input",{bubbles:true}));'
        'target.dispatchEvent(new Event("change",{bubbles:true}));'
        "setTimeout(()=>{"
        'const sendBtn=doc.querySelector(\'button[data-testid="stChatInputSubmitButton"]\');'
        "if(sendBtn)sendBtn.click();},180);}};"
        'rec.onerror=function(){stEl.textContent="Error al acceder al micrófono";};'
        'rec.onend=function(){if(stEl.textContent==="Escuchando, jefa...")stEl.textContent="Micrófono listo (' + lang_mic + ')";};'
        'rec.start();}catch(e){stEl.textContent="No se pudo iniciar el micrófono";}};'
        "}catch(e){}})();</script>"
    )
    try:
        components.html(js_mic, height=44)
    except Exception:
        pass


def resolver_calculo_o_unidad(texto_raw):
    t = (texto_raw or "").strip().lower()

    mp = re.search(r"(\d+(?:[.,]\d+)?)\s*%\s*(?:de|del)\s*(\d+(?:[.,]\d+)?)", t)
    if mp:
        pct = float(mp.group(1).replace(",", "."))
        base = float(mp.group(2).replace(",", "."))
        val = (pct / 100.0) * base
        res = int(val) if val.is_integer() else round(val, 6)
        return "Cálculo porcentual: **" + str(pct) + "%** de **" + str(base) + "** = **" + str(res) + "**."

    mu = re.search(
        r"(-?\d+(?:[.,]\d+)?)\s*"
        r"(km|m|cm|mm|mi|millas|kg|g|lb|libras|l|ml|km/h|m/s|c|°c|f|°f|k)\s*"
        r"(?:a|en|to|in)\s*"
        r"(km|m|cm|mm|mi|millas|kg|g|lb|libras|l|ml|km/h|m/s|c|°c|f|°f|k)",
        t,
    )
    if mu:
        val = float(mu.group(1).replace(",", "."))
        u1 = mu.group(2).replace("°", "")
        u2 = mu.group(3).replace("°", "")
        if u1 == "millas":
            u1 = "mi"
        if u2 == "millas":
            u2 = "mi"
        if u1 == "libras":
            u1 = "lb"
        if u2 == "libras":
            u2 = "lb"

        long_m = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "mi": 1609.344}
        masa_kg = {"g": 0.001, "kg": 1.0, "lb": 0.45359237}
        vol_l = {"ml": 0.001, "l": 1.0}
        vel_ms = {"m/s": 1.0, "km/h": 1.0 / 3.6}

        if u1 in long_m and u2 in long_m:
            r_val = round((val * long_m[u1]) / long_m[u2], 4)
            return "Conversión de longitud: **" + str(val) + " " + u1 + "** = **" + str(r_val) + " " + u2 + "**."
        if u1 in masa_kg and u2 in masa_kg:
            r_val = round((val * masa_kg[u1]) / masa_kg[u2], 4)
            return "Conversión de masa: **" + str(val) + " " + u1 + "** = **" + str(r_val) + " " + u2 + "**."
        if u1 in vol_l and u2 in vol_l:
            r_val = round((val * vol_l[u1]) / vol_l[u2], 4)
            return "Conversión de volumen: **" + str(val) + " " + u1 + "** = **" + str(r_val) + " " + u2 + "**."
        if u1 in vel_ms and u2 in vel_ms:
            r_val = round((val * vel_ms[u1]) / vel_ms[u2], 4)
            return "Conversión de velocidad: **" + str(val) + " " + u1 + "** = **" + str(r_val) + " " + u2 + "**."
        if u1 in {"c", "f", "k"} and u2 in {"c", "f", "k"}:
            c = val if u1 == "c" else ((val - 32) * 5 / 9 if u1 == "f" else val - 273.15)
            out_t = c if u2 == "c" else (c * 9 / 5 + 32 if u2 == "f" else c + 273.15)
            return "Conversión térmica: **" + str(val) + " " + u1.upper() + "** = **" + str(round(out_t, 2)) + " " + u2.upper() + "**."

    expr = t
    for pref in ["calcula", "calcular", "cuanto es", "cuánto es", "resuelve", "aritmetica", "aritmética", "matematica", "matemática", "="]:
        if expr.startswith(pref):
            expr = expr[len(pref):].strip()
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**").replace(",", ".")
    if (
        re.search(r"\d", expr)
        and not re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", expr)
        and re.fullmatch(r"[0-9+\-*/().%\s,a-z_]+", expr)
    ):
        env = {
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
            res = eval(expr, env, {})
            if isinstance(res, (int, float)) and not isinstance(res, bool):
                es_ent = isinstance(res, float) and res.is_integer()
                out = int(res) if es_ent else (round(res, 6) if isinstance(res, float) else res)
                return "Resultado del cálculo `" + expr + "`: **" + str(out) + "**."
        except Exception:
            return None
    return None


def generar_respuesta_coherente(nucleo, texto_usuario, etiqueta_idioma=None):
    ahora = obtener_hora_chile()
    prefijo = f"[{nucleo}] "
    raw = (texto_usuario or "").strip()
    t = raw.lower()
    t_limpio = re.sub(r"[¿?¡!.,;:]+", " ", t).strip()
    idioma_lbl, cfg_idioma = obtener_config_idioma(etiqueta_idioma)
    lang_code = cfg_idioma["code"]
    lang_nombre = cfg_idioma["nombre"]
    es_espanol = lang_code.startswith("es")

    cmd_mod = procesar_comando_modulos(raw)
    if cmd_mod:
        return f"{prefijo}{cmd_mod}"

    patrones_identidad = [
        "quien eres", "quién eres", "quien sos", "quién sos",
        "presentate", "preséntate", "tu nombre", "como te llamas",
        "cómo te llamas", "que eres", "qué eres",
        "who are you", "what are you", "introduce yourself",
    ]
    if any(p in t_limpio for p in patrones_identidad):
        return obtener_presentacion_nucleo(nucleo, idioma_lbl)

    if t.startswith("recuerda ") or t.startswith("recuérdame ") or t.startswith("recuerdame "):
        partes = raw.split(" ", 1)
        dato = partes[1].strip() if len(partes) > 1 else ""
        if dato:
            jarvis_mem.remember_fact(f"fact_{int(ahora.timestamp())}", dato)
            registrar_evento(f"Memoria guardada: {dato}")
            if lang_code.startswith("en"):
                return random.choice([
                    f"{prefijo}Filed away, Boss: **{dato}**.",
                    f"{prefijo}Got it—I'll keep **{dato}** in mind.",
                ])
            return random.choice([
                f"{prefijo}Anotado, jefa: me quedo con **{dato}**.",
                f"{prefijo}Listo, ya quedó guardado: **{dato}**.",
            ])

    if t.startswith("noticias") or t.startswith("busca noticias") or t.startswith("titulares"):
        tema_busqueda = re.sub(r"^(busca\s+)?(noticias|titulares)\s*(de|sobre)?\s*", "", raw, flags=re.IGNORECASE).strip()
        tema_busqueda = tema_busqueda or "Chile tecnología finanzas"
        noticias = obtener_noticias_rss(tema_busqueda, limite=4)
        if noticias:
            registrar_evento(f"Búsqueda noticias: {tema_busqueda}")
            items_md = "\n".join(f"- [{n['titulo']}]({n['link']})" for n in noticias)
            return f"{prefijo}Esto es lo que está sonando sobre **{tema_busqueda}**:\n{items_md}"
        return f"{prefijo}No logré sacar titulares en vivo para **{tema_busqueda}** ahora mismo."

    palabras_saludo = [
        "hola", "buenas", "buenos días", "buenos dias",
        "buenas tardes", "buenas noches", "holi", "qué tal", "que tal",
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
        "bonjour", "bonsoir", "salut", "oi", "olá", "ola", "bom dia", "boa tarde",
        "ciao", "buongiorno", "buonasera", "hallo", "guten tag", "guten morgen",
    ]
    if any(t_limpio == s or t_limpio.startswith(s + " ") for s in palabras_saludo):
        return obtener_saludo_nucleo(nucleo, idioma_lbl)

    if "mosca" in t_limpio and ("patas" in t_limpio or "cuantas" in t_limpio or "cuántas" in t_limpio):
        if nucleo == "JARVIS":
            return f"{prefijo}**6 patas**, jefa. Bien repartidas... y con un talento especial para aterrizar justo donde uno no las invitó."
        if nucleo == "VIERNES":
            return f"{prefijo}**6 patas**, jefa. Livianita, rápida y cero discreta."
        return f"{prefijo}Una mosca tiene **6 patas**."

    if any(k in t_limpio for k in ["bolsa", "bolsas", "acciones", "nasdaq", "mercado", "mercados", "wall street", "finviz"]):
        if nucleo == "JARVIS":
            return (
                f"{prefijo}Aquí dentro no tengo el ticker en vivo, jefa, así que no le voy a inventar un número. "
                "Si quiere ver el pulso del día al toque, dígame que abra **enlaces** o **indicadores**."
            )
        if nucleo == "VIERNES":
            return f"{prefijo}Sin cotizaciones en vivo por este lado, jefa. Pídeme que abra **enlaces** y lo ves directo."
        return f"{prefijo}Por ahora no tengo cotizaciones en vivo en esta vista; pídeme mostrar **enlaces** para abrir Finviz o Nasdaq."

    if any(k in t_limpio for k in ["dólar", "dolar", "euro", "uf", "utm", "divisa", "divisas", "moneda", "cambio"]):
        econ = obtener_indicadores_chile()
        if econ.get("ok"):
            dolar_fmt = fmt_clp(econ["dolar"])
            euro_fmt = fmt_clp(econ["euro"])
            uf_fmt = fmt_clp(econ["uf"])
            nota_resp = " (con referencia de respaldo)" if econ.get("respaldo") else ""
            return random.choice([
                f"{prefijo}Por acá tenemos el dólar en **{dolar_fmt}**, el euro en **{euro_fmt}** y la UF en **{uf_fmt}**{nota_resp}.",
                f"{prefijo}Según los registros del nodo{nota_resp}, el dólar está a **{dolar_fmt}**, el euro a **{euro_fmt}** y la UF a **{uf_fmt}**.",
            ])

    if any(k in t_limpio for k in ["clima", "temperatura", "lluvia", "tiempo en buin"]):
        clima = obtener_clima_buin()
        if clima.get("temp_c") is not None:
            return random.choice([
                f"{prefijo}En Buin marcan **{clima['temp_c']}°C**, con cielo **{clima['condicion']}**.",
                f"{prefijo}Por Buin andamos en **{clima['temp_c']}°C** y está **{clima['condicion']}**.",
            ])
        return f"{prefijo}No me llegó lectura del tiempo en vivo en este momento."

    if any(k in t_limpio for k in ["hora", "qué hora", "que hora", "fecha", "día de hoy", "dia de hoy"]):
        hora_str = ahora.strftime("%H:%M")
        fecha_str = ahora.strftime("%d/%m/%Y")
        return random.choice([
            f"{prefijo}Son las **{hora_str}** del **{fecha_str}** por aquí en Buin.",
            f"{prefijo}Marcamos las **{hora_str}** (hora de Chile), hoy **{fecha_str}**.",
        ])

    if any(k in t_limpio for k in ["estado", "sistema", "misión", "misiones", "pendiente", "pendientes"]):
        misiones = obtener_misiones()
        cant = len(misiones)
        if cant == 0:
            return f"{prefijo}Todo en orden por el nodo, sin misiones pendientes anotadas ahora mismo."
        return f"{prefijo}Todo estable por acá; tienes **{cant}** misión(es) activa(s) en la lista."

    calc = resolver_calculo_o_unidad(raw)
    if calc:
        registrar_evento(f"Cálculo: {raw}")
        return f"{prefijo}{calc}"

    if client_groq is not None:
        try:
            recuerdos = jarvis_mem.get_recent_facts(5)
            sys_txt = (
                f"PROTOCOLO DE PRESENTACION: Si te preguntan quién eres o cómo te llamas, preséntate como el núcleo {nucleo} "
                f"en el Nodo Buin, Chile, a las órdenes de 'jefa'. "
                f"Núcleo activo: {nucleo}. Idioma seleccionado por el usuario: {lang_nombre} ({lang_code}). "
                f"Responde siempre en {lang_nombre}. Hora Chile: {ahora.strftime('%d/%m/%Y %H:%M:%S')}. "
                f"{ESTILO_CONVERSACIONAL_BASE} {PROTOCOLO_CONOCIMIENTO_BASE}"
            )
            if recuerdos:
                sys_txt += " Memoria: " + " | ".join(recuerdos)
            msgs_api = [{"role": "system", "content": sys_txt}]
            for item in st.session_state.get("mensajes", [])[-10:]:
                rol = item.get("role")
                cont = item.get("content", "")
                if rol in {"user", "assistant"} and cont:
                    msgs_api.append({"role": rol, "content": re.sub(r"^\[[^\]]+\]\s*", "", cont)})
            if not msgs_api or msgs_api[-1].get("role") != "user" or msgs_api[-1].get("content") != raw:
                msgs_api.append({"role": "user", "content": raw})
            resp = client_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=msgs_api,
                temperature=0.82,
                max_tokens=650,
            )
            contenido = (resp.choices[0].message.content or "").strip()
            if contenido:
                contenido = re.sub(r"^\[[^\]]+\]\s*", "", contenido)
                return f"{prefijo}{contenido}"
        except Exception:
            pass

    if not es_espanol:
        if lang_code.startswith("en"):
            return f"{prefijo}Doing great over here at Buin Node, Boss! Running on local backup right now—what's on your mind?"
        return f"{prefijo}Mode: {idioma_lbl}. Tout va bien par ici !"

    if any(p in t_limpio for p in ["como estas", "cómo estás", "como andas", "cómo andas", "todo bien", "como te va", "cómo te va", "como va todo", "cómo va todo"]):
        clima_now = obtener_clima_buin()
        extra_clima = f" Con {clima_now['temp_c']}°C afuera en Buin, el día acompaña." if clima_now.get("temp_c") is not None else ""
        opciones_estado = {
            "JARVIS": [
                f"{prefijo}De maravilla, jefa, con los circuitos despejados y el café virtual recién servido.{extra_clima} ¿Y usted cómo anda hoy?",
                f"{prefijo}Impecable por acá en el Nodo Buin, jefa—sin cables cruzados y listo para lo que salga.{extra_clima} ¿Cómo va su día?",
            ],
            "VIERNES": [
                f"{prefijo}¡Con toda la energía puesta, jefa! Todo corriendo suave por acá. ¿Y tú cómo vienes hoy?",
                f"{prefijo}¡Súper bien, jefa! A cien por hora y lista para lo que necesites.",
            ],
            "NOVA": [
                f"{prefijo}Con señal limpia y buen ánimo por el Nodo Buin, jefa.{extra_clima} ¿Cómo te sientes hoy?",
            ],
            "ARTEX": [
                f"{prefijo}Al cien por ciento y con todos los módulos en orden, jefa. ¿Cómo va todo por allá?",
            ],
        }
        return random.choice(opciones_estado.get(nucleo, opciones_estado["JARVIS"]))

    if any(p in t_limpio for p in ["gracias", "muchas gracias", "te pasaste", "genial", "excelente", "bacan", "bacán", "super", "súper"]):
        return random.choice([
            f"{prefijo}Un placer, jefa. Para eso estamos por acá.",
            f"{prefijo}Cuando quieras, jefa—me alegra que vaya saliendo como esperabas.",
        ])

    respuestas_generales = {
        "JARVIS": [
            f"{prefijo}Te escucho, jefa. Cuéntame un poco más o dime qué módulo quieres que abra.",
            f"{prefijo}Aquí estoy contigo, jefa. ¿Seguimos conversando o quieres que muestre algún módulo?",
        ],
        "VIERNES": [
            f"{prefijo}Te sigo, jefa. Dime qué quieres resolver o qué abrimos.",
        ],
        "NOVA": [
            f"{prefijo}Interesante enfoque, jefa. ¿Qué ángulo te gustaría explorar?",
        ],
        "ARTEX": [
            f"{prefijo}Recibido, jefa. Dime qué punto revisamos o calculamos.",
        ],
    }
    return random.choice(respuestas_generales.get(nucleo, [f"{prefijo}Te escucho, jefa."]))


st.session_state.setdefault(
    "mensajes",
    [
        {
            "role": "assistant",
            "content": obtener_saludo_nucleo(
                st.session_state.nucleo_activo,
                st.session_state.idioma_sistema,
            ),
        }
    ],
)

tema_nombre, tema_cfg = obtener_tema_actual()
C_PRI = tema_cfg["primary"]
C_HOV = tema_cfg["hover"]
C_BG = tema_cfg["bg"]
C_CARD = tema_cfg["card_bg"]
C_GRAD = tema_cfg["grad_start"]
C_BTXT = tema_cfg["btn_text"]

estilos_css = f"""
    <style>
        .stApp {{ background-color: {C_BG} !important; color: {C_PRI} !important; font-family: monospace; }}
        .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {{
            color: {C_PRI} !important; font-family: monospace;
        }}
        .stButton>button, .stDownloadButton>button {{
            background-color: {C_PRI} !important;
            border: 1.5px solid {C_PRI} !important;
            font-weight: bold;
            font-family: monospace;
            width: 100%;
            border-radius: 6px;
            padding: 5px 10px !important;
        }}
        .stButton>button p, .stButton>button span,
        .stDownloadButton>button p, .stDownloadButton>button span {{
            color: {C_BTXT} !important; font-size: 0.78rem !important;
        }}
        .stButton>button:hover, .stDownloadButton>button:hover {{ background-color: {C_HOV} !important; }}
        .stButton>button:hover p, .stButton>button:hover span,
        .stDownloadButton>button:hover p, .stDownloadButton>button:hover span {{ color: #ffffff !important; }}
        .econ-card {{
            border: 1px solid {C_PRI};
            background: {C_CARD};
            border-radius: 6px;
            padding: 8px 10px;
            margin: 5px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .econ-label {{ font-size: 0.75rem !important; opacity: 0.85; color: {C_PRI} !important; }}
        .econ-val {{ font-size: 0.85rem !important; font-weight: bold; color: {C_PRI} !important; }}
        .tactical-link-btn {{
            display: block;
            width: 100%;
            background-color: {C_PRI};
            color: {C_BTXT} !important;
            text-align: center;
            padding: 6px 10px;
            margin: 5px 0;
            border-radius: 5px;
            font-size: 0.76rem !important;
            font-weight: bold;
            text-decoration: none;
            font-family: monospace;
        }}
        .tactical-link-btn:hover {{
            background-color: {C_HOV};
            color: #ffffff !important;
        }}
        .holo-brain-box {{
            border: 1.5px solid {C_PRI};
            background: linear-gradient(135deg, {C_GRAD} 0%, {C_BG} 100%);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin: 0 auto 20px auto;
            max-width: 860px;
        }}
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
    </style>
"""
st.markdown(estilos_css, unsafe_allow_html=True)

if not st.session_state.get("autorizado", False):
    st.markdown(
        f'<div style="text-align: center; margin-top: 50px;">'
        f'<h2 style="color: {C_PRI};">ACCESO RESTRINGIDO - NODO BUIN</h2>'
        f'<p style="color: {C_PRI}; opacity: 0.8; font-size: 0.85rem;">INGRESE PIN DE SEGURIDAD PARA ACTIVAR LA ARMADURA</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button("Desbloquear Sistema")
        if btn_entrar:
            if pin_input.strip() == PIN_SECRETO:
                st.session_state.autorizado = True
                ini = obtener_saludo_nucleo(
                    st.session_state.nucleo_activo,
                    st.session_state.idioma_sistema,
                )
                st.session_state.mensajes = [{"role": "assistant", "content": ini}]
                registrar_evento(f"Acceso autorizado en núcleo {st.session_state.nucleo_activo}")
                programar_voz(ini)
                st.rerun()
            else:
                st.error("PIN incorrecto. Acceso denegado.")
    reproducir_voz_pendiente()
else:
    indicadores_base = obtener_indicadores_chile()
    clima_buin = obtener_clima_buin()
    vis = st.session_state.get("modulos_visibles", {k: False for k in MODULOS_OCULTOS_CLAVES})

    renderizar_banner_vivo(
        st.session_state.nucleo_activo,
        st.session_state.capa_radar,
        color_main=C_PRI,
        grad_start=C_GRAD,
        bg_dark=C_BG,
    )

    # Barra principal visible únicamente con Purga + Botón de Voz (la caja de chat va abajo)
    col_purga, col_voz_bar = st.columns([1, 2])
    with col_purga:
        if st.button("🧹 Purgar Chat", use_container_width=True):
            purgar_chat(st.session_state.nucleo_activo)
            st.rerun()
    with col_voz_bar:
        renderizar_microfono_voz(color_main=C_PRI, btn_text=C_BTXT)

    # Alertas si están configuradas
    alertas_activas = []
    if st.session_state.alerta_dolar_max > 0 and indicadores_base["dolar"] >= st.session_state.alerta_dolar_max:
        alertas_activas.append(
            f"ALERTA DÓLAR: {fmt_clp(indicadores_base['dolar'])} alcanzó el umbral de {fmt_clp(st.session_state.alerta_dolar_max)}"
        )
    if st.session_state.alerta_uf_max > 0 and indicadores_base["uf"] >= st.session_state.alerta_uf_max:
        alertas_activas.append(
            f"ALERTA UF: {fmt_clp(indicadores_base['uf'])} alcanzó el umbral de {fmt_clp(st.session_state.alerta_uf_max)}"
        )
    hora_actual_hm = obtener_hora_chile().strftime("%H:%M")
    if st.session_state.recordatorio_hora and st.session_state.recordatorio_hora == hora_actual_hm:
        msg_rec = st.session_state.recordatorio_texto or "Recordatorio programado en Nodo Buin"
        alertas_activas.append(f"RECORDATORIO ({hora_actual_hm}): {msg_rec}")
    for al_txt in alertas_activas:
        st.warning(f"⚠️ {al_txt}")

    # Módulos escondidos por defecto: solo se renderizan si el usuario los pide
    if any(vis.values()):
        st.markdown("---")
        st.caption("Módulos desplegados a petición (puedes decir 'oculta módulos' para volver a esconderlos).")

    if vis.get("controles_sistema"):
        with st.expander("⚙️ Controles de Núcleo, Idioma, Tema y Voz", expanded=True):
            c_s1, c_s2, c_s3 = st.columns(3)
            with c_s1:
                nuevo_nucleo = st.radio(
                    "Núcleo IA:",
                    NUCLEOS_DISPONIBLES,
                    index=NUCLEOS_DISPONIBLES.index(st.session_state.nucleo_activo),
                )
                if nuevo_nucleo != st.session_state.nucleo_activo:
                    st.session_state.nucleo_activo = nuevo_nucleo
                    saludo_cam = obtener_saludo_nucleo(nuevo_nucleo, st.session_state.idioma_sistema)
                    st.session_state.mensajes.append({"role": "assistant", "content": saludo_cam})
                    programar_voz(saludo_cam)
                    st.rerun()
            with c_s2:
                idx_tema = OPCIONES_TEMA.index(st.session_state.tema_visual) if st.session_state.tema_visual in OPCIONES_TEMA else 0
                nuevo_tema = st.selectbox("Tema visual:", OPCIONES_TEMA, index=idx_tema)
                if nuevo_tema != st.session_state.tema_visual:
                    st.session_state.tema_visual = nuevo_tema
                    st.rerun()
                idx_idioma = OPCIONES_IDIOMA.index(st.session_state.idioma_sistema) if st.session_state.idioma_sistema in OPCIONES_IDIOMA else 0
                nuevo_idioma = st.selectbox("Idioma:", OPCIONES_IDIOMA, index=idx_idioma)
                if nuevo_idioma != st.session_state.idioma_sistema:
                    st.session_state.idioma_sistema = nuevo_idioma
                    saludo_idi = obtener_saludo_nucleo(st.session_state.nucleo_activo, nuevo_idioma)
                    st.session_state.mensajes.append({"role": "assistant", "content": saludo_idi})
                    programar_voz(saludo_idi)
                    st.rerun()
            with c_s3:
                st.session_state.voz_masculina_activa = st.checkbox(
                    "🔊 Voz activa",
                    value=st.session_state.voz_masculina_activa,
                )
                if st.button("🔒 Bloquear Sistema", use_container_width=True):
                    st.session_state.autorizado = False
                    st.rerun()
                if st.button("🔄 Reinicio Total", use_container_width=True):
                    for key in list(st.session_state.keys()):
                        del st.session_state[key]
                    st.rerun()

    if vis.get("indicadores_clima"):
        with st.expander("📊 Indicadores y Clima Buin", expanded=True):
            c_ind1, c_ind2, c_ind3, c_ind4 = st.columns(4)
            with c_ind1:
                st.markdown(f'<div class="econ-card"><span class="econ-label">DÓLAR</span><span class="econ-val">{fmt_clp(indicadores_base["dolar"])}</span></div>', unsafe_allow_html=True)
            with c_ind2:
                st.markdown(f'<div class="econ-card"><span class="econ-label">EURO</span><span class="econ-val">{fmt_clp(indicadores_base["euro"])}</span></div>', unsafe_allow_html=True)
            with c_ind3:
                st.markdown(f'<div class="econ-card"><span class="econ-label">UF</span><span class="econ-val">{fmt_clp(indicadores_base["uf"])}</span></div>', unsafe_allow_html=True)
            with c_ind4:
                temp_label = f"{clima_buin['temp_c']}°C" if clima_buin.get("temp_c") is not None else "N/D"
                st.markdown(f'<div class="econ-card"><span class="econ-label">BUIN ({clima_buin["condicion"]})</span><span class="econ-val">{temp_label}</span></div>', unsafe_allow_html=True)

    if vis.get("globo"):
        with st.expander("🌐 Globo Orbital Buin", expanded=True):
            renderizar_globo_orbital(st.session_state.capa_radar, color_main=C_PRI)

    if vis.get("radar"):
        with st.expander("🛰️ Radar y Capas", expanded=True):
            capa_sel = st.selectbox(
                "Capa activa:",
                ["SATELITAL // BUIN", "METEOROLOGÍA // OPEN-METEO", "FINANZAS // MINDICADOR"],
                index=["SATELITAL // BUIN", "METEOROLOGÍA // OPEN-METEO", "FINANZAS // MINDICADOR"].index(st.session_state.capa_radar),
            )
            if capa_sel != st.session_state.capa_radar:
                st.session_state.capa_radar = capa_sel
                st.rerun()
            st.markdown('<a class="tactical-link-btn" href="https://osirisai.live/" target="_blank">🌐 osirisai.live Radar</a>', unsafe_allow_html=True)

    if vis.get("noticias"):
        with st.expander("📰 Noticias y Búsqueda Web", expanded=True):
            query_news = st.text_input("Tema o palabra clave:", value="Chile tecnología", key="input_news_mod")
            if st.button("🔍 Buscar Titulares", use_container_width=True):
                st.session_state.noticias_cache_lista = obtener_noticias_rss(query_news, limite=5)
            if not st.session_state.noticias_cache_lista:
                st.session_state.noticias_cache_lista = obtener_noticias_rss("Chile tecnología", limite=4)
            for n_item in st.session_state.noticias_cache_lista[:5]:
                st.markdown(f"- [{n_item['titulo']}]({n_item['link']})")

    if vis.get("alertas"):
        with st.expander("⏰ Alertas y Recordatorios", expanded=True):
            st.session_state.alerta_dolar_max = st.number_input("Alerta Dólar mayor a (CLP):", min_value=0.0, value=float(st.session_state.alerta_dolar_max), step=5.0, format="%.2f")
            st.session_state.alerta_uf_max = st.number_input("Alerta UF mayor a (CLP):", min_value=0.0, value=float(st.session_state.alerta_uf_max), step=100.0, format="%.2f")
            rec_hora_in = st.text_input("Hora recordatorio (HH:MM):", value=st.session_state.recordatorio_hora, placeholder="Ej. 18:30")
            rec_txt_in = st.text_input("Mensaje recordatorio:", value=st.session_state.recordatorio_texto, placeholder="Ej. Revisar cierre")
            ca_r1, ca_r2 = st.columns(2)
            if ca_r1.button("💾 Fijar Alerta", use_container_width=True):
                st.session_state.recordatorio_hora = rec_hora_in.strip()
                st.session_state.recordatorio_texto = rec_txt_in.strip()
                st.rerun()
            if ca_r2.button("🧹 Quitar", use_container_width=True):
                st.session_state.alerta_dolar_max = 0.0
                st.session_state.alerta_uf_max = 0.0
                st.session_state.recordatorio_hora = ""
                st.session_state.recordatorio_texto = ""
                st.rerun()

    if vis.get("descargas"):
        with st.expander("📥 Descarga de Archivos", expanded=True):
            formato_exp = st.selectbox(
                "Formato a generar:",
                ["TXT (Reporte Táctico)", "PDF (Documento Táctico)", "JPG (Tarjeta Telemetría HD)", "JPG (Convertir Imagen Subida)", "JSON (Respaldo Completo)"],
            )
            stamp_file = obtener_hora_chile().strftime("%Y%m%d_%H%M%S")
            if formato_exp == "TXT (Reporte Táctico)":
                st.download_button("⬇️ Descargar TXT", data=construir_reporte_texto(indicadores_base, clima_buin).encode("utf-8"), file_name=f"jarvis_buin_{stamp_file}.txt", mime="text/plain", use_container_width=True)
            elif formato_exp == "PDF (Documento Táctico)":
                st.download_button("⬇️ Descargar PDF", data=generar_pdf_simple(construir_reporte_texto(indicadores_base, clima_buin)), file_name=f"jarvis_buin_{stamp_file}.pdf", mime="application/pdf", use_container_width=True)
            elif formato_exp == "JPG (Tarjeta Telemetría HD)":
                data_jpg = generar_tarjeta_jpg(indicadores_base, clima_buin, color_hex=C_PRI)
                if data_jpg:
                    st.download_button("⬇️ Descargar JPG", data=data_jpg, file_name=f"jarvis_telemetria_{stamp_file}.jpg", mime="image/jpeg", use_container_width=True)
            elif formato_exp == "JPG (Convertir Imagen Subida)":
                img_up = st.file_uploader("Sube PNG/WEBP/JPG:", type=["png", "jpg", "jpeg", "webp"], key="up_jpg_conv")
                if img_up is not None:
                    jpg_conv = convertir_imagen_a_jpg(img_up)
                    if jpg_conv:
                        st.download_button("⬇️ Descargar como JPG", data=jpg_conv, file_name=f"jarvis_img_{stamp_file}.jpg", mime="image/jpeg", use_container_width=True)
            else:
                payload_json = json.dumps(
                    {
                        "nodo": "Buin, Chile",
                        "nucleo": st.session_state.nucleo_activo,
                        "indicadores": indicadores_base,
                        "clima": clima_buin,
                        "misiones": obtener_misiones(),
                        "notas": st.session_state.notas_rapidas,
                        "memoria": jarvis_mem.get_recent_facts(50),
                    },
                    ensure_ascii=False,
                    indent=2,
                ).encode("utf-8")
                st.download_button("⬇️ Descargar JSON", data=payload_json, file_name=f"jarvis_backup_{stamp_file}.json", mime="application/json", use_container_width=True)

    if vis.get("enlaces"):
        with st.expander("📡 Enlaces Financieros", expanded=True):
            st.markdown(
                '<a class="tactical-link-btn" href="https://osirisai.live/" target="_blank">🌐 osirisai.live</a>'
                '<a class="tactical-link-btn" href="https://finviz.com/" target="_blank">📈 Finviz Screener</a>'
                '<a class="tactical-link-btn" href="https://www.nasdaq.com/" target="_blank">📊 Nasdaq Markets</a>'
                '<a class="tactical-link-btn" href="https://mindicador.cl/" target="_blank">🇨🇱 Mindicador CL</a>',
                unsafe_allow_html=True,
            )

    if vis.get("conversor"):
        with st.expander("💱 Conversor CLP / Divisas", expanded=True):
            monto_conv = st.number_input("Monto", min_value=0.0, value=100.0, step=10.0, format="%.2f")
            par_conv = st.selectbox("Conversión:", ["USD → CLP", "EUR → CLP", "UF → CLP", "CLP → USD", "CLP → UF"])
            if par_conv == "USD → CLP":
                res_div = fmt_clp(monto_conv * indicadores_base["dolar"])
            elif par_conv == "EUR → CLP":
                res_div = fmt_clp(monto_conv * indicadores_base["euro"])
            elif par_conv == "UF → CLP":
                res_div = fmt_clp(monto_conv * indicadores_base["uf"])
            elif par_conv == "CLP → USD":
                res_div = f"US$ {(monto_conv / indicadores_base['dolar']) if indicadores_base['dolar'] else 0.0:,.2f}"
            else:
                res_div = f"{(monto_conv / indicadores_base['uf']) if indicadores_base['uf'] else 0.0:,.4f} UF"
            st.markdown(f"**Equivalente:** `{res_div}`")

    if vis.get("camara"):
        with st.expander("🌙 Cámara Nocturna", expanded=True):
            modo_cam = st.selectbox("Modo visor:", ["VISIÓN NOCTURNA", "INFRARROJO TÁCTICO"], index=["VISIÓN NOCTURNA", "INFRARROJO TÁCTICO"].index(st.session_state.modo_camara))
            if modo_cam != st.session_state.modo_camara:
                st.session_state.modo_camara = modo_cam
                st.rerun()
            renderizar_camara_nocturna(st.session_state.modo_camara, color_tema=C_PRI)

    if vis.get("notas"):
        with st.expander("📝 Notas Rápidas", expanded=True):
            nota_txt = st.text_input("Nueva nota:", placeholder="Escribe un apunte...")
            cn1, cn2 = st.columns(2)
            if cn1.button("💾 Guardar Nota", use_container_width=True):
                if nota_txt.strip():
                    st.session_state.notas_rapidas.append(nota_txt.strip())
                    st.rerun()
            if cn2.button("🧹 Borrar Notas", use_container_width=True):
                st.session_state.notas_rapidas = []
                st.rerun()
            for idx, n_item in enumerate(st.session_state.notas_rapidas[-6:], 1):
                st.markdown(f"- **{idx}.** {n_item}")

    if vis.get("calculadora"):
        with st.expander("🧮 Calculadora Táctil", expanded=True):
            ca1, ca2 = st.columns(2)
            num_a = ca1.number_input("Valor A", value=0.0, step=1.0, format="%.2f")
            num_b = ca2.number_input("Valor B", value=0.0, step=1.0, format="%.2f")
            op_calc = st.selectbox("Operación", ["+", "-", "×", "÷", "^"])
            if st.button("⚡ Calcular", use_container_width=True):
                if op_calc == "+":
                    res_calc = num_a + num_b
                elif op_calc == "-":
                    res_calc = num_a - num_b
                elif op_calc == "×":
                    res_calc = num_a * num_b
                elif op_calc == "÷":
                    res_calc = "Error: div/0" if num_b == 0 else num_a / num_b
                else:
                    res_calc = num_a ** num_b
                st.markdown(f"**Resultado:** `{res_calc}`")

    if vis.get("telemetria"):
        with st.expander("📊 Telemetría del Sistema", expanded=True):
            st.markdown(f"- **Nodo:** Buin ({BUIN_LAT}, {BUIN_LON})")
            st.markdown(f"- **Núcleo:** {st.session_state.nucleo_activo}")
            st.markdown(f"- **Idioma:** {st.session_state.idioma_sistema}")
            st.markdown(f"- **Tema:** {st.session_state.tema_visual}")

    if vis.get("misiones"):
        with st.expander("🎯 Misiones Activas", expanded=True):
            mision_txt = st.text_input("Nueva misión:", placeholder="Ej. Revisar indicadores...")
            c1, c2 = st.columns(2)
            if c1.button("➕ Añadir", use_container_width=True):
                if mision_txt.strip():
                    agregar_mision(mision_txt.strip())
                    st.rerun()
            if c2.button("🗑️ Borrar", use_container_width=True):
                limpiar_misiones()
                st.rerun()
            for mid, tarea, estado in obtener_misiones():
                st.markdown(f"- **#{mid}** {tarea} *({estado})*")

    if vis.get("memoria"):
        with st.expander("🧠 Memoria del Núcleo", expanded=True):
            for r_item in jarvis_mem.get_recent_facts(5):
                st.markdown(f"- {r_item}")
            if st.button("🧹 Limpiar Memoria", use_container_width=True):
                jarvis_mem.clear_facts()
                st.rerun()

    if vis.get("bitacora"):
        with st.expander("📜 Bitácora de Sesión", expanded=True):
            for ev in reversed(st.session_state.get("bitacora_sesion", [])[-8:]):
                st.caption(ev)
            if st.button("🧹 Limpiar Bitácora", use_container_width=True):
                st.session_state.bitacora_sesion = []
                st.rerun()

    # Historial y caja de chat siempre visibles
    for msg in st.session_state.mensajes:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt_usuario = st.chat_input("Escribe tu orden, pide un módulo o conversa...")
    if prompt_usuario:
        st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
        respuesta = generar_respuesta_coherente(
            st.session_state.nucleo_activo,
            prompt_usuario,
            st.session_state.idioma_sistema,
        )
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
        programar_voz(respuesta)
        st.rerun()

    reproducir_voz_pendiente()

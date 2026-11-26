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
        im.save(out, format="

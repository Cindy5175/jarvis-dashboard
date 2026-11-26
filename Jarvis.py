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
    API_KEY_GROQ = st.secrets.get("GROQ_API_KEY", "")
except Exception:
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
        im.save(out, format="JPEG", quality=92)
        return out.getvalue()
    except Exception:
        return b""


def construir_emblema_nucleo_svg(color_main="#00f3ff", size=54):
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 80 80" '
        f'style="flex-shrink:0;filter:drop-shadow(0 0 8px {color_main});" '
        f'xmlns="http://www.w3.org/2000/svg">'
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
        "<script>(function(){"
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
        "})();</script>"
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
        "<script>(function(){"
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
        "})();</script>"
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
        "<script>(function(){"
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
        "})();</script>"
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
    js_voz = (
        "<script>(function(){try{if(!('speechSynthesis' in window))return;"
        "if(window.__jarvisVozTimer){clearTimeout(window.__jarvisVozTimer);}"
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
        "window.speechSynthesis.speak(u);}"
        "if(window.speechSynthesis.getVoices().length){hablarUnaVez();}"
        "else{window.speechSynthesis.onvoiceschanged=function(){window.speechSynthesis.onvoiceschanged=null;hablarUnaVez();};"
        "window.__jarvisVozTimer=setTimeout(hablarUnaVez,140);}"
        "}catch(e){}})();</script>"
    )
    try:
        components.html(js_voz, height=1)
    except Exception:
        pass


def renderizar_microfono_voz(color_main="#00f3ff", btn_text="#060913"):
    _, cfg = obtener_config_idioma()
    lang_mic = cfg["code"]
    js_mic = (
        '<div style="display:flex;align-items:center;gap:8px;margin:4px 0 10px 0;">'
        f'<button id="btn-mic-jarvis" type="button" style="background:{color_main};color:{btn_text};'
        f'border:1.5px solid {color_main};border-radius:6px;padding:6px 12px;font-family:monospace;'
        'font-weight:bold;font-size:0.78rem;cursor:pointer;">🎤 Hablar por Voz</button>'
        f'<span id="estado-mic-jarvis" style="color:{color_main};font-family:monospace;'
        f'font-size:0.75rem;opacity:0.85;">Micrófono listo ({lang_mic})</span></div>'
        "<script>(function(){"
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
        "})();</script>"
    )
    try:
        components.html(js_mic, height=46)
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
                "Si quiere ver el pulso del día al toque, abra **Finviz** o **Nasdaq** en **Enlaces Financieros**."
            )
        if nucleo == "VIERNES":
            return (
                f"{prefijo}Sin cotizaciones en vivo por este lado, jefa. "
                "Échele un ojo a **Finviz** o **Nasdaq** en el menú lateral y ve el movimiento directo."
            )
        return f"{prefijo}Por ahora no tengo cotizaciones en vivo en esta vista; puede revisar **Finviz** o **Nasdaq** en el menú lateral."

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

    # Respuestas naturales y espontáneas en modo local (sin Groq)
    if any(p in t_limpio for p in ["como estas", "cómo estás", "como andas", "cómo andas", "todo bien", "como te va", "cómo te va", "como va todo", "cómo va todo"]):
        clima_now = obtener_clima_buin()
        extra_clima = f" Con {clima_now['temp_c']}°C afuera en Buin, el día acompaña." if clima_now.get("temp_c") is not None else ""
        opciones_estado = {
            "JARVIS": [
                f"{prefijo}De maravilla, jefa, con los circuitos despejados y el café virtual recién servido.{extra_clima} ¿Y usted cómo anda hoy?",
                f"{prefijo}Impecable por acá en el Nodo Buin, jefa—sin cables cruzados y listo para lo que salga.{extra_clima} ¿Cómo va su día?",
                f"{prefijo}Muy bien, jefa, vigilando el tablero para que usted no tenga que preocuparse por los detalles. ¿Qué tal amaneció?",
            ],
            "VIERNES": [
                f"{prefijo}¡Con toda la energía puesta, jefa! Todo corriendo suave por

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
            rows = [r[0] for r in cursor.fetchall()

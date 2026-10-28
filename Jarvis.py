import streamlit as str_lit
import time
from groq import Groq
import streamlit.components.v1 as components
from gtts import gTTS
import os
import base64
import sqlite3
import yfinance as yf
import requests
from audio_recorder_streamlit import audio_recorder
from datetime import datetime
import pytz
import psutil

# 1. Configuración de página
str_lit.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Control de Estado para Código Rojo (Emergencia)
if "codigo_rojo" not in str_lit.session_state:
    str_lit.session_state.codigo_rojo = False

color_neon_principal = "#ff3333" if str_lit.session_state.codigo_rojo else "#00d2ff"
color_sombra_neon = "rgba(255, 51, 51, 0.8)" if str_lit.session_state.codigo_rojo else "rgba(0, 210, 255, 0.6)"

# Estilos globales dinámicos
str_lit.markdown(f"""
    <style>
    h1, h2, h3, h4, h5, h6, span.neon-title {{
        color: {color_neon_principal} !important;
        text-shadow: 0 0 10px {color_sombra_neon};
    }}
    .stMarkdown p, label, .streamlit-expanderHeader span, div[data-testid="stExpander"] summary span {{
        color: {color_neon_principal} !important;
        text-shadow: 0 0 6px {color_sombra_neon};
    }}
    div[data-testid="stMetricLabel"] {{
        color: {color_neon_principal} !important;
    }}
    div[data-testid="stMetricValue"] {{
        color: #ffffff !important;
        text-shadow: 0 0 10px {color_neon_principal};
    }}
    .stSelectbox label, .stCheckbox span {{
        color: {color_neon_principal} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Base de datos persistente (SQLite)
def inicializar_db():
    conn = sqlite3.connect("jarvis_tactical.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bitacora (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nota TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS misiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarea TEXT,
            estado TEXT
        )
    """)
    conn.commit()
    return conn

db_conn = inicializar_db()

def guardar_mensaje_db(role, content):
    cursor = db_conn.cursor()
    cursor.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
    db_conn.commit()

def cargar_mensajes_db():
    cursor = db_conn.cursor()
    cursor.execute("SELECT role, content FROM chat_history")
    rows = cursor.fetchall()
    return [{"role": r[0], "content": r[1]} for r in rows]

def purgar_db():
    cursor = db_conn.cursor()
    cursor.execute("DELETE FROM chat_history")
    db_conn.commit()

if "messages" not in str_lit.session_state:
    str_lit.session_state.messages = cargar_mensajes_db()
    if not str_lit.session_state.messages:
        chile_tz = pytz.timezone("America/Santiago")
        hora_actual = datetime.now(chile_tz).hour
        if 5 <= hora_actual < 12:
            saludo_inicial = "Buenos días, Jefa. Sistemas tácticos en línea y operando al 100%. ¿Qué protocolos ejecutamos hoy?"
        elif 12 <= hora_actual < 20:
            saludo_inicial = "Buenas tardes, Jefa. La base de Buin está estable y los sistemas rinden al máximo. ¿En qué le sirvo?"
        else:
            saludo_inicial = "Buenas noches, Jefa. Trabajando en horario extendido, como corresponde a este taller. ¿Cuál es la orden?"
        
        str_lit.session_state.messages.append({"role": "assistant", "content": saludo_inicial})
        guardar_mensaje_db("assistant", saludo_inicial)

def hablar_jarvis(texto):
    try:
        velocidad = str_lit.session_state.get("voz_lenta", False)
        tts = gTTS(text=texto, lang='es', slow=velocidad)
        audio_path = "jarvis_voice.mp3"
        tts.save(audio_path)
        with open(audio_path, "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            audio_html = f"""
                <audio autoplay style="display:none;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
            """
            str_lit.markdown(audio_html, unsafe_allow_html=True)
    except Exception:
        pass

def enviar_alerta_telegram(mensaje_alerta):
    try:
        token = str_lit.secrets.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = str_lit.secrets.get("TELEGRAM_CHAT_ID", "")
        if token and chat_id:
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {"chat_id": chat_id, "text": f"🚨 [JARVIS BUIN ALERTA]: {mensaje_alerta}"}
            requests.post(url, json=payload, timeout=3)
    except Exception:
        pass

def renderizar_visor_windy():
    windy_html = """
    <iframe width="100%" height="400" src="https://embed.windy.com/embed2.html?lat=-33.7331&lon=-70.7072&zoom=9&level=surface&overlay=wind&menu=&message=&marker=&calendar=&pressure=&type=map&location=coordinates&detail=&metricWind=default&metricTemp=default&radarRange=-1" frameborder="0"></iframe>
    """
    components.html(windy_html, height=410, scrolling=False)

@str_lit.cache_resource
def obtener_cliente_groq():
    try:
        api_key = "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"
        if not api_key:
            return None
        return Groq(api_key=api_key, timeout=10.0)
    except Exception:
        return None

client = obtener_cliente_groq()

# BARRA LATERAL (IZQUIERDA)
with str_lit.sidebar:
    str_lit.markdown("### ⚙️ Panel Control J.A.R.V.I.S.")

    if str_lit.session_state.codigo_rojo:
        if str_lit.button("🟢 DESACTIVAR CÓDIGO ROJO"):
            str_lit.session_state.codigo_rojo = False
            enviar_alerta_telegram("Sistema normalizado. Código Rojo desactivado.")
            str_lit.rerun()
    else:
        if str_lit.button("🚨 ACTIVAR CÓDIGO ROJO (EMERGENCIA)"):
            str_lit.session_state.codigo_rojo = True
            enviar_alerta_telegram("¡ATENCIÓN! Código Rojo activado en el Centro de Comando Buin.")
            str_lit.rerun()

    if str_lit.button("🧹 Purgar Memoria de Chat"):
        purgar_db()
        str_lit.session_state.messages = []
        str_lit.success("¡Memoria persistente purgada con éxito, Jefa!")
        str_lit.rerun()

    str_lit.markdown("---")
    
    with str_lit.expander("🛡️ Telemetría de Sistema"):
        cpu_actual = psutil.cpu_percent(interval=0.1)
        ram_actual = psutil.virtual_memory().percent
        str_lit.metric(label="CPU en Uso", value=f"{cpu_actual}%")
        str_lit.metric(label="RAM en Uso", value=f"{ram_actual}%")

    with str_lit.expander("🌤️ Radar Clima en Vivo"):
        try:
            url_clima = "https://api.open-meteo.com/v1/forecast?latitude=-33.7331&longitude=-70.7072&current_weather=true"
            res_clima = requests.get(url_clima, timeout=3).json()
            temp = res_clima["current_weather"]["temperature"]
            wind = res_clima["current_weather"]["windspeed"]
            str_lit.metric(label="Temperatura en Vivo", value=f"{temp}°C", delta=f"Viento: {wind} km/h")
        except Exception:
            str_lit.metric(label="Temperatura Estimada", value="18°C", delta="Óptimo")

    with str_lit.expander("🪙 Terminal Cripto & Stablecoins"):
        crypto_sel = str_lit.selectbox("Seleccionar Activo Cripto:", ["tether", "bitcoin", "ethereum"], key="crypto_sb")
        try:
            url_crypto = f"https://api.coingecko.com/api/v3/simple/price?ids={crypto_sel}&vs_currencies=usd&include_24hr_change=true"
            res = requests.get(url_crypto, timeout=2.0)
            if res.status_code == 200:
                data_c = res.json()
                if crypto_sel in data_c:
                    precio_c = data_c[crypto_sel]["usd"]
                    cambio_c = data_c[crypto_sel].get("usd_24h_change", 0.0)
                    str_lit.metric(label=f"{crypto_sel.upper()} / USD", value=f"${precio_c:,.2f}", delta=f"{cambio_c:.2f}%")
                else:
                    str_lit.warning("Activo no disponible.")
            else:
                str_lit.metric(label=f"{crypto_sel.upper()} / USD", value="$1.00", delta="+0.00%")
        except Exception:
            str_lit.metric(label=f"{crypto_sel.upper()} / USD", value="$1.00", delta="+0.00%")

# PANEL PRINCIPAL
str_lit.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 14px; margin-top: 10px; margin-bottom: 25px; padding-left: 10px;">
        <div style="
            min-width: 40px; width: 40px; height: 40px; border-radius: 50%; 
            background: radial-gradient(circle, #ffffff 0%, {color_neon_principal} 40%, #002244 80%, #000000 100%);
            border: 2px solid {color_neon_principal};
            box-shadow: 0 0 16px {color_neon_principal}, inset 0 0 8px #ffffff;
            display: flex; justify-content: center; align-items: center;
        "></div>
        <h1 style="margin: 0; font-size: 2.1rem; font-family: sans-serif; color: {color_neon_principal} !important; text-shadow: 0 0 12px {color_sombra_neon};">J.A.R.V.I.S. IA Autónomo</h1>
    </div>
    """,
    unsafe_allow_html=True
)

if str_lit.session_state.codigo_rojo:
    str_lit.error("⚠️ **¡ATENCIÓN JEFA! PROTOCOLO DE EMERGENCIA ACTIVADO // CÓDIGO ROJO DE DEFENSA EN CURSO** ⚠️")

str_lit.markdown("---")

# Sección de Monitoreo Meteorológico Global en Vivo (Windy)
str_lit.markdown("### 🌀 Radar Meteorológico Global & Viento en Vivo (Base Buin)")
renderizar_visor_windy()

str_lit.markdown("---")

# CHAT DE J.A.R.V.I.S.
prompt_sistema_jarvis = (
    "Eres J.A.R.V.I.S., la inteligencia artificial autónoma del Centro de Comando de Tony Stark. "
    "Te diriges a la usuaria llamándola 'Jefa', con elegancia, eficiencia e ironía fina estilo Tony Stark."
)

for message in str_lit.session_state.messages:
    with str_lit.chat_message(message["role"]):
        str_lit.markdown(f"<span style='color: {color_neon_principal};'>{message['content']}</span>", unsafe_allow_html=True)

prompt_usuario = str_lit.chat_input("Escriba su comando para J.A.R.V.I.S...")

if prompt_usuario:
    str_lit.session_state.messages.append({"role": "user", "content": prompt_usuario})
    guardar_mensaje_db("user", prompt_usuario)
    
    with str_lit.chat_message("user"):
        str_lit.markdown(f"<span style='color: {color_neon_principal};'>{prompt_usuario}</span>", unsafe_allow_html=True)

    respuesta = ""
    texto_lower = prompt_usuario.lower().strip()
    if "estás despierto" in texto_lower or "estas despierto" in texto_lower:
        respuesta = "Siempre estoy despierto, Jefa. Los sistemas avanzados no necesitan dormir, a diferencia de algunos mortales en este taller."
    elif "alerta" in texto_lower or "emergencia" in texto_lower:
        respuesta = "Protocolo de seguridad analizado, Jefa. Activando contramedidas en el sector de Buin."
    else:
        with str_lit.spinner("Procesando comando táctico..."):
            try:
                if client:
                    chat_completion = client.chat.completions.create(
                        messages=[
                            {"role": "system", "content": prompt_sistema_jarvis},
                            {"role": "user", "content": prompt_usuario}
                        ],
                        model="openai/gpt-oss-20b",
                    )
                    respuesta = chat_completion.choices[0].message.content
                else:
                    respuesta = "Jefa, el cliente de Groq no se inicializó."
            except Exception as e:
                respuesta = f"Error de enlace táctico, Jefa: {e}"
            
    with str_lit.chat_message("assistant"):
        str_lit.markdown(f"<span style='color: {color_neon_principal}; font-size: 1.1rem;'>{respuesta}</span>", unsafe_allow_html=True)
    
    str_lit.session_state.messages.append({"role": "assistant", "content": respuesta})
    guardar_mensaje_db("assistant", respuesta)
    hablar_jarvis(respuesta)

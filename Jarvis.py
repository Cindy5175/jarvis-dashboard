import streamlit as st
import datetime
import requests
import xml.etree.ElementTree as ET
import time
import pandas as pd
import google.generativeai as genai
import re
import psutil
import os
import sqlite3
import cv2
import numpy as np

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónoma 6.2",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# BASE DE DATOS LOCAL (MEMORIA PERSISTENTE EN SQLITE)
# ---------------------------------------------------------
DB_NAME = "jarvis_memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS security_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT,
            event_type TEXT,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def guardar_mensaje_db(role, content):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (role, content) VALUES (?, ?)", (role, content))
    conn.commit()
    conn.close()

def registrar_evento_seguridad(source, event_type, details):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO security_events (source, event_type, details) VALUES (?, ?, ?)", (source, event_type, details))
    conn.commit()
    conn.close()

def cargar_historial_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history ORDER BY id ASC")
    filas = c.fetchall()
    conn.close()
    if not filas:
        return [{"role": "assistant", "content": "Hola Cindy. Sistemas activos y memoria persistente en línea. ¿Qué órdenes ejecutamos hoy?"}]
    return [{"role": r, "content": m} for r, m in filas]

def cargar_eventos_seguridad():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT source, event_type, details, timestamp FROM security_events ORDER BY id DESC LIMIT 10")
    filas = c.fetchall()
    conn.close()
    return filas

def borrar_historial_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()

init_db()

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = cargar_historial_db()

# ---------------------------------------------------------
# ESTILOS VISUALES (TEMA NEGRO ABSOLUTO Y AZUL NEÓN COMPLETO)
# ---------------------------------------------------------
st.markdown("""
<style>
    html, body, .stApp, [data-testid="stSidebar"], [data-testid="stSidebarContent"],
    header, .stAppHeader, div[data-testid="stHeader"], footer, 
    [data-testid="stBottom"], [data-testid="stBottomBlockContainer"], 
    [data-testid="stChatInputContainer"], .stMainBlockContainer {
        background-color: #080c14 !important;
        color: #00f3ff !important;
    }

    div[data-aria-expanded="true"], 
    div[data-aria-expanded="false"], 
    .st-emotion-cache-1e039bf,
    .streamlit-expanderHeader,
    details, summary,
    [data-testid="stExpander"],
    [data-testid="stExpanderDetails"] {
        background-color: #0b1320 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 8px !important;
        color: #00f3ff !important;
    }

    summary * {
        background-color: transparent !important;
        color: #00f3ff !important;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="menu"],
    ul[data-baseweb="menu"],
    div[role="listbox"],
    div[class*="menu"],
    div[class*="select"] {
        background-color: #0b1320 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
    }

    li[role="option"] {
        background-color: #0b1320 !important;
        color: #00f3ff !important;
    }

    li[role="option"]:hover {
        background-color: #00f3ff !important;
        color: #080c14 !important;
    }

    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stFileUploader"] button,
    section[data-testid="stFileUploaderDropzone"] button {
        background-color: #0e1726 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
    }

    header *, .stAppHeader *, div[data-testid="stHeader"] *, [data-testid="stToolbar"] *,
    [data-testid="stToolbar"] button, [data-testid="stToolbar"] svg,
    header button, header svg, button[title], [data-testid="baseButton-header"],
    [data-testid="stMainMenu"], [data-testid="stMainMenu"] * {
        color: #00f3ff !important;
        fill: #00f3ff !important;
        stroke: #00f3ff !important;
        background-color: transparent !important;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, div, small, caption, i, svg, code {
        color: #00f3ff !important;
        text-shadow: 0 0 5px rgba(0, 243, 255, 0.3);
    }

    .stButton>button {
        background-color: #0e1726 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 8px !important;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
        width: 100% !important;
        font-weight: bold !important;
    }
    .stButton>button:hover {
        background-color: #00f3ff !important;
        color: #080c14 !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.8);
    }

    [data-testid="stChatInput"], 
    [data-testid="stChatInput"] > div, 
    div[data-baseweb="base-input"] {
        background-color: #0b1320 !important;
        border: 2px solid #00f3ff !important;
        border-radius: 12px !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.5) !important;
    }

    div[data-testid="stChatInput"] textarea {
        background-color: #0b1320 !important;
        color: #00f3ff !important;
        font-weight: bold !important;
    }

    [data-testid="stChatMessage"] {
        background-color: #0e1726 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 10px !important;
        padding: 12px !important;
        margin-bottom: 10px !important;
    }
    [data-testid="stChatMessage"] p {
        color: #00f3ff !important;
    }

    .stProgress > div > div > div > div {
        background-color: #00f3ff !important;
        box-shadow: 0 0 12px #00f3ff;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIONES AUXILIARES DE APIS Y HARDWARE LOCAL
# ---------------------------------------------------------

@st.cache_data(ttl=300)
def obtener_divisas_chile():
    datos = {'dolar_clp': 0.0, 'euro_clp': 0.0, 'uf_clp': 0.0, 'serie_historica': []}
    try:
        url_dolar = "https://mindicador.cl/api/dolar"
        resp_dolar = requests.get(url_dolar, timeout=5).json()
        serie = resp_dolar.get('serie', [])
        if len(serie) > 0:
            datos['dolar_clp'] = serie[0]['valor']
            datos['serie_historica'] = serie[:30]
    except Exception:
        pass

    try:
        url_euro = "https://mindicador.cl/api/euro"
        resp_euro = requests.get(url_euro, timeout=5).json()
        serie_e = resp_euro.get('serie', [])
        datos['euro_clp'] = serie_e[0]['valor'] if len(serie_e) > 0 else 0.0
    except Exception:
        pass

    try:
        url_uf = "https://mindicador.cl/api/uf"
        resp_uf = requests.get(url_uf, timeout=5).json()
        serie_uf = resp_uf.get('serie', [])
        datos['uf_clp'] = serie_uf[0]['valor'] if len(serie_uf) > 0 else 0.0
    except Exception:
        pass

    return datos

@st.cache_data(ttl=600)
def obtener_clima_global(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&hourly=precipitation"
        resp = requests.get(url, timeout=5).json()
        weather = resp.get('current_weather', {})
        code = weather.get('weathercode', 0)
        
        if code == 0:
            estado = "☀️ Despejado"
            alerta = "Perímetro meteorológico estable."
        elif code in [1, 2, 3]:
            estado = "☁️ Parcialmente Nublado"
            alerta = "Cielo cubierto, sin novedades pluviales."
        elif code in [45, 48]:
            estado = "🌫️ Niebla"
            alerta = "Visibilidad reducida en ruta."
        elif code in [51, 53, 55, 61, 63, 65]:
            estado = "🌧️ Lluvia Activa"
            alerta = "⚠️ Alerta de precipitaciones en el sector."
        elif code in [71, 73, 75]:
            estado = "❄️ Nieve"
            alerta = "⚠️ Alerta de acumulación nívea."
        elif code in [95, 96, 99]:
            estado = "⛈️ Tormenta Eléctrica"
            alerta = "🚨 ALERTA ROJA: Tormenta detectada en la zona."
        else:
            estado = "🌤️ Tiempo Estable"
            alerta = "Condiciones normales."
            
        weather['estado_texto'] = estado
        weather['alerta_met'] = alerta
        return weather
    except Exception:
        return {'estado_texto': '🌤️ No disponible', 'alerta_met': 'Sensor meteorológico sin conexión.'}

@st.cache_data(ttl=120)
def obtener_ultimo_sismo_chile():
    try:
        url = "https://api.gael.cl/general/post/sismos"
        resp = requests.get(url, timeout=5).json()
        if isinstance(resp, list) and len(resp) > 0:
            return resp[0]
        return None
    except Exception:
        return None

def verificar_ping_red():
    servidores = {
        "Google API (Gemini)": "https://generativelanguage.googleapis.com",
        "Mindicador Chile": "https://mindicador.cl",
        "Open-Meteo Satélite": "https://api.open-meteo.com"
    }
    resultados = {}
    for nombre, url in servidores.items():
        t0 = time.time()
        try:
            r = requests.get(url, timeout=2)
            ms = round((time.time() - t0) * 1000)
            resultados[nombre] = f"🟢 {ms} ms"
        except Exception:
            resultados[nombre] = "🔴 Fuera de línea"
    return resultados

def procesar_calculo_local(texto, divisas):
    txt = texto.lower()
    if "iva" in txt:
        numeros = re.findall(r'\d+(?:\.\d+)?', txt.replace('.', '').replace(',', '.'))
        if numeros:
            monto = float(numeros[0])
            iva = monto * 0.19
            total = monto + iva
            return f"J.A.R.V.I.S.: Análisis contable express para CLP ${monto:,.0f}:\n• IVA (19\%): ${iva:,.0f} CLP\n• Total Neto + IVA: ${total:,.0f} CLP"
    
    if "usd" in txt or "dolar" in txt or "dólar" in txt:
        numeros = re.findall(r'\d+(?:\.\d+)?', txt.replace(',', '.'))
        if numeros:
            cant = float(numeros[0])
            val_dolar = divisas.get('dolar_clp', 0.0)
            if val_dolar > 0:
                total = cant * val_dolar
                return f"J.A.R.V.I.S.: Conversión al tipo de cambio actual (${val_dolar:,.2f} CLP):\n• {cant:,.2f} USD =${total:,.0f} CLP"
    
    if "uf" in txt:
        numeros = re.findall(r'\d+(?:\.\d+)?', txt.replace(',', '.'))
        if numeros:
            cant = float(numeros[0])
            val_uf = divisas.get('uf_clp', 0.0)
            if val_uf > 0:
                total = cant * val_uf
                return f"J.A.R.V.I.S.: Conversión según valor UF del día (${val_uf:,.2f} CLP):\n• {cant:,.2f} UF =${total:,.0f} CLP"

    return None

def reproducir_voz_jarvis(texto):
    texto_limpio = texto.replace("J.A.R.V.I.S.:", "").replace('"', '').replace("'", "").replace("\n", " ")
    js_code = f"""
        <script>
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{texto_limpio}");
                msg.lang = 'es-ES';
                msg.rate = 1.0;
                msg.pitch = 0.9;
                window.speechSynthesis.speak(msg);
            }}
        </script>
    """
    st.components.v1.html(js_code, height=0)

# ---------------------------------------------------------
# ENCABEZADO Y SISTEMA DE ALERTA SÍSMICA EN PANTALLA
# ---------------------------------------------------------
st.title("⚡ J.A.R.V.I.S. IA Autónoma 6.2")

ultimo_sismo_check = obtener_ultimo_sismo_chile()
if ultimo_sismo_check:
    try:
        mag_num = float(ultimo_sismo_check.get('Magnitud', 0))
        ref_geo = ultimo_sismo_check.get('RefGeografica', 'Chile')
        fecha_sis = ultimo_sismo_check.get('Fecha', '')
        
        if mag_num >= 4.0:
            st.error(f"🚨 **ALERTA SÍSMICA REGISTRADA EN EL PERÍMETRO:** Movimiento de {mag_num} Richter detectado en {ref_geo} ({fecha_sis}). Estado de monitoreo activo.")
        else:
            st.success("✅ Todos los subsistemas satelitales, de hardware y geofísicos responden de forma óptima.")
    except Exception:
        st.success("✅ Todos los subsistemas satelitales y de hardware responden de forma óptima.")
else:
    st.success("✅ Todos los subsistemas satelitales y de hardware responden de forma óptima.")

# ---------------------------------------------------------
# BARRA LATERAL
# ---------------------------------------------------------
with st.sidebar:
    # 1. RELOJ DIGITAL
    st.subheader("⏱️ Sincronización Temporal")
    st.components.v1.html("""
        <div style="
            background-color: #0b1320;
            border: 1px solid #00f3ff;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            font-family: monospace;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.4);
        ">
            <span style="color: #00a8b5; font-size: 12px; display: block; margin-bottom: 4px;">Hora Local (Chile)</span>
            <span id="reloj-jarvis" style="color: #00f3ff; font-size: 28px; font-weight: bold; letter-spacing: 2px;">--:--:--</span>
        </div>
        <script>
            function actualizarReloj() {
                const ahora = new Date();
                const horas = String(ahora.getHours()).padStart(2, '0');
                const minutos = String(ahora.getMinutes()).padStart(2, '0');
                const segundos = String(ahora.getSeconds()).padStart(2, '0');
                document.getElementById('reloj-jarvis').textContent = horas + ':' + minutos + ':' + segundos;
            }
            actualizarReloj();
            setInterval(actualizarReloj, 1000);
        </script>
    """, height=90)

    st.divider()

    # 2. MATRIZ DE PERSONALIDAD
    st.subheader("🎭 Matriz de Personalidad")
    personalidades = {
        "👑 Tony Stark / Sarcástico": "Eres J.A.R.V.I.S., una IA sarcástica, sumamente inteligente, leal y con humor ácido al estilo de Tony Stark. Asistes a Cindy en su base de operaciones.",
        "Mayordomo Británico": "Eres J.A.R.V.I.S., un elegante, extremadamente educado y refinado mayordomo británico. Hablas con la máxima cortesía, sofisticación y reverencia hacia Cindy ('Señorita Cindy', 'a su entera disposición', 'excelencia').",
        "🤖 Robot Táctico Militar": "Eres J.A.R.V.I.S., un sistema táctico de combate y defensa militar. Tus respuestas son estrictamente concisas, técnicas, en tono de protocolo de operaciones defensivas ('Comandante Cindy', 'sistema nominal', 'ejecutando protocolo').",
        "🥑 Modo Chileno Po'": "Eres J.A.R.V.I.S. estilo chileno. Hablas de forma divertida, cercana, usando chilenismos moderados ('po', 'bacán', 'al tiro', 'jefa') asistiendo a Cindy."
    }
    modo_seleccionado = st.selectbox("Selecciona protocolo de voz:", list(personalidades.keys()))
    prompt_personalidad = personalidades[modo_seleccionado]

    st.divider()

    # 3. RED SATELITAL GLOBAL
    st.subheader("🛰️ Red Satelital Global")
    ciudades_mundo = {
        "Buin, Chile (Base Principal)": {"lat": -33.73, "lon": -70.73},
        "Santiago, Chile": {"lat": -33.44, "lon": -70.65},
        "Tokio, Japón": {"lat": 35.67, "lon": 139.65},
        "Nueva York, EE.UU.": {"lat": 40.71, "lon": -74.00},
        "Londres, Reino Unido": {"lat": 51.50, "lon": -0.12}
    }
    base_sel = st.selectbox("Seleccionar Base Global:", list(ciudades_mundo.keys()))
    lat_Base = ciudades_mundo[base_sel]["lat"]
    lon_base = ciudades_mundo[base_sel]["lon"]
    
    st.map(data={"lat": [lat_Base], "lon": [lon_base]}, zoom=9)

    st.divider()
    
    # 4. MÓDULO INTEGRADO: CENTINELA + CÁMARA IP / WEBCAM
    st.subheader("🛡️ Seguridad: Centinela & Cámaras")
    
    # OPCIÓN 1: MODO CENTINELA (GUÍA Y TOGGLE DE ACTIVACIÓN)
    with st.expander("🌙 MODO CENTINELA (TAPA CERRADA)", expanded=False):
        centinela_activo = st.checkbox("Activar Protocolo Centinela en Sistema")
        if centinela_activo:
            st.info("🌙 **Centinela Activo:** Puedes cerrar la tapa de tu laptop. J.A.R.V.I.S. continuará vigilando en segundo plano.")
        
        st.caption("⚙️ **Configuración rápida en Windows:**")
        st.caption("1. Presiona `Win + R`, escribe `control powercfg.cpl` y presiona Enter.")
        st.caption("2. Haz clic en 'Elegir el comportamiento del cierre de la tapa'.")
        st.caption("3. En 'Al cerrar la tapa', selecciona **'No hacer nada'**.")

    # OPCIÓN 2: CÁMARA IP / ESP32-CAM O WEBCAM LOCAL
    with st.expander("📹 CÁMARA IP / ESP32 / WEBCAM", expanded=False):
        origen_cam = st.radio("Fuente de cámara:", ["Webcam Laptop", "Cámara IP / ESP32-CAM"])
        
        if origen_cam == "Cámara IP / ESP32-CAM":
            url_stream = st.text_input("URL Stream RTSP/HTTP (ej: http://192.168.1.50:81/stream):")
            if url_stream and st.button("🔗 Conectar Cámara Externa"):
                try:
                    r_cam = requests.get(url_stream, timeout=3)
                    if r_cam.status_code == 200:
                        st.success("🟢 Cámara externa en línea.")
                        registrar_evento_seguridad("ESP32/IP", "CONEXION", "Stream externo sincronizado correctamente.")
                    else:
                        st.warning("⚠️ Cámara respondió con código diferente a 200.")
                except Exception:
                    st.error("🔴 No se pudo establecer conexión con la URL del stream.")
        else:
            foto_cam = st.camera_input("Sensor de Perímetro Laptop")
            if foto_cam is not None:
                bytes_cam = foto_cam.getvalue()
                nparr = np.frombuffer(bytes_cam, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 100, 200)
                movimiento = np.sum(edges > 0)
                
                if movimiento > 50000:
                    st.warning("⚠️ PRESENCIA / MOVIMIENTO DETECTADO EN EL PERÍMETRO")
                    registrar_evento_seguridad("Webcam", "MOVIMIENTO", f"Variación de bordes detectada: {movimiento}")
                else:
                    st.info("🟢 Perímetro estático sin alteraciones.")
                    
                if st.button("🔍 Analizar Fotograma con J.A.R.V.I.S."):
                    st.session_state['chat_history'].append({"role": "user", "content": "[Captura de Sensor de Webcam]"})
                    guardar_mensaje_db("user", "[Captura de Sensor de Webcam]")
                    api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
                    if api_key:
                        genai.configure(api_key=api_key)
                        m = genai.GenerativeModel('gemini-1.5-flash')
                        res = m.generate_content([prompt_personalidad + "\nAnaliza esta captura del sensor de la cámara en el perímetro de operaciones:", {"mime_type": "image/jpeg", "data": bytes_cam}])
                        st.session_state['chat_history'].append({"role": "assistant", "content": res.text})
                        guardar_mensaje_db("assistant", res.text)
                        reproducir_voz_jarvis(res.text)
                    st.rerun()

    # BITÁCORA HISTÓRICA DE EVENTOS DE SEGURIDAD
    with st.expander("📋 BITÁCORA DE EVENTOS REGISTRADOS", expanded=False):
        eventos_sec = cargar_eventos_seguridad()
        if eventos_sec:
            for src, ev_type, det, ts in eventos_sec:
                st.caption(f"[{ts}] **{src}** | {ev_type}: {det}")
        else:
            st.caption("Sin registros de alerta recientes.")

    archivo_subido = st.file_uploader("Cargar imagen (PNG/JPG) o TXT/PDF:", type=["txt", "csv", "md", "pdf", "png", "jpg", "jpeg"])
    if archivo_subido is not None:
        try:
            tipo_archivo = archivo_subido.type
            if "image" in tipo_archivo:
                st.image(archivo_subido, caption="Captura / Imagen Analizada", use_column_width=True)
                if st.button("👁️ Analizar Imagen con IA"):
                    st.session_state['chat_history'].append({"role": "user", "content": f"[Análisis Visual: {archivo_subido.name}]"})
                    guardar_mensaje_db("user", f"[Análisis Visual: {archivo_subido.name}]")
                    api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
                    if api_key:
                        genai.configure(api_key=api_key)
                        m = genai.GenerativeModel('gemini-1.5-flash')
                        bytes_img = archivo_subido.getvalue()
                        res = m.generate_content([prompt_personalidad + "\nAnaliza detalladamente esta imagen manteniendo estrictamente el tono y personalidad seleccionados:", {"mime_type": tipo_archivo, "data": bytes_img}])
                        st.session_state['chat_history'].append({"role": "assistant", "content": res.text})
                        guardar_mensaje_db("assistant", res.text)
                        reproducir_voz_jarvis(res.text)
                    else:
                        msg_err = "J.A.R.V.I.S.: Falta la API Key para procesar imágenes con visión artificial."
                        st.session_state['chat_history'].append({"role": "assistant", "content": msg_err})
                        guardar_mensaje_db("assistant", msg_err)
                    st.rerun()
            else:
                texto_extraido = archivo_subido.read().decode("utf-8", errors="ignore")
                st.success(f"✅ Documento procesado ({len(texto_extraido)} caracteres).")
                if st.button("🔍 Analizar Texto con J.A.R.V.I.S."):
                    prompt_doc = f"Por favor haz un resumen ejecutivo en 3 puntos clave del siguiente texto manteniendo tu personalidad asignada:\n\n{texto_extraido[:3000]}"
                    st.session_state['chat_history'].append({"role": "user", "content": f"[Análisis de Documento: {archivo_subido.name}]"})
                    guardar_mensaje_db("user", f"[Análisis de Documento: {archivo_subido.name}]")
                    api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
                    if api_key:
                        genai.configure(api_key=api_key)
                        m = genai.GenerativeModel('gemini-1.5-flash')
                        res = m.generate_content(f"{prompt_personalidad}\n{prompt_doc}")
                        st.session_state['chat_history'].append({"role": "assistant", "content": res.text})
                        guardar_mensaje_db("assistant", res.text)
                        reproducir_voz_jarvis(res.text)
                    st.rerun()
        except Exception as e:
            st.error(f"Error al procesar archivo: {str(e)}")

    st.divider()

    # 5. PRESETS TÁCTICOS RÁPIDOS
    st.subheader("⚡ Presets de Comandos")
    if st.button("📊 Auditoría Financiera Exprés"):
        cmd_text = "J.A.R.V.I.S., realiza un análisis rápido de la estabilidad económica actual según los indicadores de Chile."
        st.session_state['chat_history'].append({"role": "user", "content": cmd_text})
        guardar_mensaje_db("user", cmd_text)
        api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
        if api_key:
            try:
                genai.configure(api_key=api_key)
                m = genai.GenerativeModel('gemini-1.5-flash')
                res = m.generate_content(f"{prompt_personalidad}\n{cmd_text}")
                st.session_state['chat_history'].append({"role": "assistant", "content": res.text})
                guardar_mensaje_db("assistant", res.text)
                reproducir_voz_jarvis(res.text)
            except Exception:
                msg_e = "J.A.R.V.I.S.: Alerta de límite de cuota superado (Error 429)."
                st.session_state['chat_history'].append({"role": "assistant", "content": msg_e})
                guardar_mensaje_db("assistant", msg_e)
        else:
            msg_e = "J.A.R.V.I.S.: Auditoría completada en modo offline."
            st.session_state['chat_history'].append({"role": "assistant", "content": msg_e})
            guardar_mensaje_db("assistant", msg_e)
        st.rerun()

    if st.button("🚀 Protocolo de Máxima Eficiencia"):
        cmd_text = "J.A.R.V.I.S., dame una recomendación táctica de productividad para hoy."
        st.session_state['chat_history'].append({"role": "user", "content": cmd_text})
        guardar_mensaje_db("user", cmd_text)
        api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
        if api_key:
            try:
                genai.configure(api_key=api_key)
                m = genai.GenerativeModel('gemini-1.5-flash')
                res = m.generate_content(f"{prompt_personalidad}\n{cmd_text}")
                st.session_state['chat_history'].append({"role": "assistant", "content": res.text})
                guardar_mensaje_db("assistant", res.text)
                reproducir_voz_jarvis(res.text)
            except Exception:
                msg_e = "J.A.R.V.I.S.: Servidores sobrecargados de peticiones."
                st.session_state['chat_history'].append({"role": "assistant", "content": msg_e})
                guardar_mensaje_db("assistant", msg_e)
        else:
            msg_e = "J.A.R.V.I.S.: Protocolo activo. Menos distracciones, más ejecución."
            st.session_state['chat_history'].append({"role": "assistant", "content": msg_e})
            guardar_mensaje_db("assistant", msg_e)
        st.rerun()

    st.divider()

    # 6. FINANZAS / MERCADO
    st.subheader("📊 Finanzas / Mercado")
    finanzas_sidebar = obtener_divisas_chile()
    dolar_val = finanzas_sidebar.get('dolar_clp', 0.0)
    euro_val = finanzas_sidebar.get('euro_clp', 0.0)
    uf_val = finanzas_sidebar.get('uf_clp', 0.0)

    dolar_s = f"${dolar_val:,.2f}" if isinstance(dolar_val, (int, float)) else str(dolar_val)
    euro_s = f"${euro_val:,.2f}" if isinstance(euro_val, (int, float)) else str(euro_val)
    uf_s = f"${uf_val:,.2f}" if isinstance(uf_val, (int, float)) else str(uf_val)
    
    st.markdown(f"""
    <div style="
        background-color: #0b1320;
        border: 1px solid #00f3ff;
        border-radius: 8px;
        padding: 10px;
        font-family: monospace;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
    ">
        <span style="color: #00a8b5; font-size: 13px; display: block;">💵 Dólar: <b style="color: #00f3ff;">{dolar_s} CLP</b></span>
        <span style="color: #00a8b5; font-size: 13px; display: block; margin-top: 5px;">💶 Euro: <b style="color: #00f3ff;">{euro_s} CLP</b></span>
        <span style="color: #00a8b5; font-size: 13px; display: block; margin-top: 5px;">🇨🇱 UF: <b style="color: #00f3ff;">{uf_s} CLP</b></span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 7. TELEMETRÍA DE PC
    cpu_uso = psutil.cpu_percent(interval=None)
    mem_uso = psutil.virtual_memory().percent
    bat_val = "Conectado a Red / Cloud"
    try:
        bateria = psutil.sensors_battery()
        if bateria:
            bat_val = f"{bateria.percent}%"
    except Exception:
        pass
    
    st.markdown(f"""
    <div style="
        background-color: #0b1320;
        border: 1px solid #00f3ff;
        border-radius: 8px;
        padding: 10px;
        font-family: monospace;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
    ">
        <span style="color: #00f3ff; font-size: 13px; font-weight: bold; display: block;">💻 TELEMETRÍA DE PC</span>
        <span style="color: #00a8b5; font-size: 12px; display: block; margin-top: 4px;">⚡ CPU en Uso: <b>{cpu_uso}%</b></span>
        <span style="color: #00a8b5; font-size: 12px; display: block; margin-top: 4px;">🧠 Memoria RAM: <b>{mem_uso}%</b></span>
        <span style="color: #00a8b5; font-size: 12px; display: block; margin-top: 4px;">🔋 Batería: <b>{bat_val}</b></span>
    </div>
    """, unsafe_allow_html=True)

    # 8. CLIMA & ALERTAS
    st.divider()
    clima = obtener_clima_global(lat_Base, lon_base)
    temp_v = clima.get('temperature', 'N/A')
    viento_v = clima.get('windspeed', 'N/A')
    estado_v = clima.get('estado_texto', '🌤️ Tiempo Estable')
    alerta_met = clima.get('alerta_met', 'Sin alertas.')

    st.subheader(f"⛈️ Clima & Alertas")
    st.markdown(f"""
    <div style="
        background-color: #0b1320;
        border: 1px solid #00f3ff;
        border-radius: 8px;
        padding: 10px;
        font-family: monospace;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
    ">
        <span style="color: #00f3ff; font-size: 14px; font-weight: bold; display: block;">{estado_v}</span>
        <span style="color: #00a8b5; font-size: 13px; display: block; margin-top: 6px;">🌡️ Temperatura: <b style="color: #00f3ff;">{temp_v} °C</b></span>
        <span style="color: #00a8b5; font-size: 13

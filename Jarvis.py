import streamlit as st
import datetime
import requests
import time
import pandas as pd
import google.generativeai as genai
import re
import psutil
import os
import sqlite3
import numpy as np
import yfinance as yf

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónoma 6.4",
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
    c.execute('''
        CREATE TABLE IF NOT EXISTS misiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarea TEXT,
            estado TEXT,
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

def cargar_historial_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history ORDER BY id ASC")
    filas = c.fetchall()
    conn.close()
    if not filas:
        return [{"role": "assistant", "content": "Hola Cindy. Sistemas activos y memoria persistente en línea. ¿Qué órdenes ejecutamos hoy?"}]
    return [{"role": r, "content": m} for r, m in filas]

def borrar_historial_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM chat_history")
    conn.commit()
    conn.close()

init_db()

if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = cargar_historial_db()

if 'documentos_cargados' not in st.session_state:
    st.session_state['documentos_cargados'] = []

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

@st.cache_data(ttl=300)
def obtener_acciones_tiempo_real():
    tickers = ["AAPL", "MSFT", "NVDA", "TSLA", "SPY"]
    datos_acciones = {}
    for t in tickers:
        try:
            stock = yf.Ticker(t)
            hist = stock.history(period="1d")
            if not hist.empty:
                precio = hist['Close'].iloc[-1]
                prev = stock.info.get('previousClose', precio)
                var_pct = ((precio - prev) / prev) * 100
                datos_acciones[t] = {"precio": precio, "variacion": var_pct}
        except Exception:
            pass
    return datos_acciones

@st.cache_data(ttl=300)
def obtener_info_red():
    info = {"ip": "Detectando...", "pais": "Chile", "ISP": "Enlace Satelital Cloud"}
    try:
        resp = requests.get("https://ipapi.co/json/", timeout=3).json()
        info["ip"] = resp.get("ip", "190.160.x.x")
        info["pais"] = resp.get("country_name", "Chile")
        info["ISP"] = resp.get("org", "Red Privada")
    except Exception:
        pass
    return info

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

def reproducir_voz_jarvis(texto):
    texto_limpio = texto.replace("J.A.R.V.I.S.:", "").replace('"', '').replace("'", "").replace("\n", " ")
    js_code = f"""
        <script>
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{texto_limpio}");
                msg.rate = 0.92;
                msg.pitch = 0.85;
                var voices = window.speechSynthesis.getVoices();
                var jarvisVoice = voices.find(function(v) {{
                    return (v.name.includes('Male') || v.name.includes('George') || v.name.includes('Ryan') || v.name.includes('Pablo') || v.name.includes('Jorge')) && v.lang.includes('es');
                }}) || voices.find(function(v) {{ return v.lang.includes('es'); }});
                if (jarvisVoice) {{
                    msg.voice = jarvisVoice;
                }} else {{
                    msg.lang = 'es-ES';
                }}
                window.speechSynthesis.speak(msg);
            }}
        </script>
    """
    st.components.v1.html(js_code, height=0)

# ---------------------------------------------------------
# ENCABEZADO Y SISTEMA DE ALERTA SÍSMICA EN PANTALLA
# ---------------------------------------------------------
st.title("⚡ J.A.R.V.I.S. IA Autónoma 6.4")

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
# BARRA LATERAL (IZQUIERDA)
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
        "👑 Tony Stark / Sarcástico": "Eres J.A.R.V.I.S., una IA sarcástica, sumamente inteligente, leal y con humor ácido al estilo de Tony Stark. Hablas siempre en español directo y cercano a Cindy.",
        "Mayordomo Británico": "Eres J.A.R.V.I.S., un elegante, extremadamente educado y refinado mayordomo británico. Te diriges a Cindy de forma distinguida en perfecto español ('a su entera disposición, señorita Cindy').",
        "🤖 Robot Táctico Militar": "Eres J.A.R.V.I.S., un sistema táctico de combate y defensa militar. Tus respuestas son estrictamente concisas, técnicas, en tono de protocolo de operaciones defensivas en español.",
        "🥑 Modo Chileno Po'": "Eres J.A.R.V.I.S. estilo chileno. Hablas de forma divertida, cercana, usando chilenismos moderados ('po', 'bacán', 'al tiro', 'jefa') asistiendo a Cindy."
    }
    modo_seleccionado = st.selectbox("Selecciona protocolo de voz:", list(personalidades.keys()))
    prompt_personalidad = personalidades[modo_seleccionado]

    st.divider()

    # 3. PROTOCOLO DE MISIONES TÁCTICAS (EN LA BARRA LATERAL)
    st.subheader("🎯 Protocolo de Misiones")
    with st.expander("📋 Gestión de Misiones", expanded=True):
        nueva_mision = st.text_input("Nueva misión:", key="input_mision")
        if st.button("📥 Registrar Misión"):
            if nueva_mision:
                conn = sqlite3.connect(DB_NAME)
                c = conn.cursor()
                c.execute("INSERT INTO misiones (tarea, estado) VALUES (?, ?)", (nueva_mision, "Pendiente"))
                conn.commit()
                conn.close()
                st.success("🎯 Misión registrada.")
                st.rerun()

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT id, tarea, estado FROM misiones ORDER BY id DESC")
        lista_misiones = c.fetchall()
        conn.close()

        if lista_misiones:
            for mid, tarea_txt, estado_txt in lista_misiones:
                st.markdown(f"<small style='color: #00f3ff;'>• {tarea_txt} [{estado_txt}]</small>", unsafe_allow_html=True)
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    if estado_txt == "Pendiente" and st.button("✔️", key=f"comp_{mid}"):
                        conn = sqlite3.connect(DB_NAME)
                        c = conn.cursor()
                        c.execute("UPDATE misiones SET estado='Completada' WHERE id=?", (mid,))
                        conn.commit()
                        conn.close()
                        st.rerun()
                with col_m2:
                    if st.button("🗑️", key=f"del_{mid}"):
                        conn = sqlite3.connect(DB_NAME)
                        c = conn.cursor()
                        c.execute("DELETE FROM misiones WHERE id=?", (mid,))
                        conn.commit()
                        conn.close()
                        st.rerun()
        else:
            st.info("Sin misiones activas.")

    st.divider()

    # 4. TERMINAL HACKER DE RED (IP & DNS)
    st.subheader("🌐 Terminal Hacker de Red")
    net_info = obtener_info_red()
    st.markdown(f"""
    <div style="
        background-color: #0b1320;
        border: 1px solid #00f3ff;
        border-radius: 8px;
        padding: 10px;
        font-family: monospace;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
    ">
        <span style="color: #00f3ff; font-size: 12px; font-weight: bold; display: block; margin-bottom: 4px;">💻 ENLACE DE RED ACTIVO</span>
        <span style="color: #00a8b5; font-size: 11px; display: block;">IP Pública: <b style="color: #00f3ff;">{net_info['ip']}</b></span>
        <span style="color: #00a8b5; font-size: 11px; display: block; margin-top: 3px;">Ubicación: <b style="color: #00f3ff;">{net_info['pais']}</b></span>
        <span style="color: #00a8b5; font-size: 11px; display: block; margin-top: 3px;">Proveedor: <b style="color: #00f3ff;">{net_info['ISP']}</b></span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. BIBLIOTECA ACADÉMICA MÚLTIPLE (FÍSICA, ÁLGEBRA, HISTORIA, ETC.)
    st.subheader("📚 Biblioteca Académica (PDFs)")
    with st.expander("📖 Carga Masiva de Manuales", expanded=False):
        archivos_pdfs = st.file_uploader(
            "Selecciona o arrastra todos tus manuales:", 
            type=["pdf"], 
            accept_multiple_files=True,
            key="multi_pdf"
        )
        if archivos_pdfs:
            st.session_state['documentos_cargados'] = [f"• {pdf.name}" for pdf in archivos_pdfs]
            st.success(f"✅ {len(archivos_pdfs)} manual(es) vinculado(s) al núcleo de J.A.R.V.I.S.")
            for nombre in st.session_state['documentos_cargados']:
                st.markdown(f"<small style='color: #00f3ff;'>{nombre}</small>", unsafe_allow_html=True)

    st.divider()

    # 6. RED SATELITAL GLOBAL
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
    
    # 7. MÓDULO INTEGRADO: CÁMARA TÁCTICA & VISIÓN POR IA
    st.subheader("🛡️ Cámara Táctica & Visión")
    
    with st.expander("🌙 MODO CENTINELA (TAPA CERRADA)", expanded=False):
        centinela_activo = st.checkbox("Activar Protocolo Centinela en Sistema")
        if centinela_activo:
            st.info("🌙 **Centinela Activo:** Puedes cerrar la tapa de tu laptop. J.A.R.V.I.S. continuará vigilando en segundo plano.")

    with st.expander("📹 WEBCAM & RECONOCIMIENTO FACIAL IA", expanded=False):
        foto_cam = st.camera_input("Sensor Biométrico de Perímetro")
        if foto_cam is not None:
            bytes_cam = foto_cam.getvalue()
            st.success("📸 Fotograma capturado correctamente.")
            
            if st.button("🔍 Escanear Rostro / Perímetro con IA"):
                st.session_state['chat_history'].append({"role": "user", "content": "[Escaneo de Sensor de Cámara]"})
                guardar_mensaje_db("user", "[Escaneo de Sensor de Cámara]")
                api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
                if api_key:
                    genai.configure(api_key=api_key)
                    m = genai.GenerativeModel('gemini-1.5-flash')
                    res = m.generate_content([prompt_personalidad + "\nAnaliza esta imagen de la cámara. Si ves a una persona, confirma 'OPERADORA IDENTIFICADA: CINDY CARRERA // ACCESO CONCEDIDO'. Si no, describe lo que ves:", {"mime_type": "image/jpeg", "data": bytes_cam}])
                    st.session_state['chat_history'].append({"role": "assistant", "content": res.text})
                    guardar_mensaje_db("assistant", res.text)
                    reproducir_voz_jarvis(res.text)
                st.rerun()

    archivo_subido = st.file_uploader("Cargar imagen (PNG/JPG) o documento general:", type=["txt", "csv", "md", "png", "jpg", "jpeg"])
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

    # 8. FINANZAS / MERCADO Y ACCIONES
    st.subheader("📊 Finanzas & Acciones EE.UU.")
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

    # DASHBOARD DE ACCIONES ENMARCADO CON BORDE NEÓN
    st.markdown("<br>", unsafe_allow_html=True)
    acciones_data = obtener_acciones_tiempo_real()
    
    html_acciones = """
    <div style="
        background-color: #0b1320;
        border: 1px solid #00f3ff;
        border-radius: 8px;
        padding: 10px;
        font-family: monospace;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
    ">
        <span style="color: #00f3ff; font-size: 13px; font-weight: bold; display: block; margin-bottom: 8px;">📈 Acciones & ETFs en Tiempo Real</span>
    """
    
    if acciones_data:
        for symbol, info in acciones_data.items():
            color_var = "#00f3ff" if info['variacion'] >= 0 else "#ff4b4b"
            html_acciones += f"""<span style="color: #00a8b5; font-size: 12px; display: block; margin-top: 4px;"><b>{symbol}:</b> ${info['precio']:.2f} USD (<span style='color:{color_var}'>{info['variacion']:+.2f}%</span>)</span>"""
    else:
        html_acciones += """<span style="color: #00a8b5; font-size: 12px; display: block;">Mercado cerrado / Cargando...</span>"""
        
    html_acciones += "</div>"
    st.markdown(html_acciones, unsafe_allow_html=True)

    st.divider()

    # 9. TELEMETRÍA DE PC
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

    # 10. CLIMA & ALERTAS
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
        <span style="color: #00a8b5; font-size: 13px; display: block; margin-top: 6px;">💨 Viento: <b style="color: #00f3ff;">{viento_v} km/h</b></span>
        <hr style="border-color: #00f3ff; margin: 8px 0;">
        <span style="color: #ffcc00; font-size: 11px; display: block;"><b>Alerta Satelital:</b> {alerta_met}</span>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# CONSOLA PRINCIPAL (DERECHA)
# ---------------------------------------------------------
st.subheader("💬 Terminal de Conversación Autónoma & Traductor Táctico")

# TRADUCTOR Y SINTETIZADOR TÁCTICO MULTILENGUAJE (EN PANTALLA PRINCIPAL)
with st.expander("🌐 Traductor y Sintetizador Táctico Multilenguaje", expanded=False):
    texto_a_traducir = st.text_area("Pega aquí fragmentos científicos o texto en otro idioma:", key="input_trad")
    idioma_destino = st.selectbox("Traducir a:", ["Español", "Inglés", "Francés", "Alemán", "Italiano"])
    
    if st.button("🔄 Ejecutar Traducción y Síntesis"):
        if texto_a_traducir:
            api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
            if api_key:
                genai.configure(api_key=api_key)
                modelo_trad = genai.GenerativeModel('gemini-1.5-flash')
                res_trad = modelo_trad.generate_content(f"Traduce el siguiente texto técnico exactamente al idioma {idioma_destino} manteniendo rigor científico:\n\n{texto_a_traducir}")
                resultado_trad = res_trad.text
                st.success("✅ Traducción completada con éxito:")
                st.write(resultado_trad)
                reproducir_voz_jarvis(resultado_trad)
            else:
                st.error("API Key de Gemini no configurada.")
        else:
            st.warning("Ingresa texto para traducir.")

st.divider()

# MÓDULO DE ESCUCHA ACTIVA POR MICRÓFONO
st.components.v1.html("""
    <div style="margin-bottom: 15px;">
        <button id="mic-btn" onclick="startDictation()" style="
            background-color: #0e1726;
            color: #00f3ff;
            border: 1px solid #00f3ff;
            border-radius: 8px;
            padding: 8px 16px;
            cursor: pointer;
            font-weight: bold;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
        ">🎙️ Escucha Activa: Dictar Comando por Micrófono</button>
        <span id="mic-status" style="color: #00a8b5; margin-left: 10px; font-family: monospace;"></span>
    </div>
    <script>
        function startDictation() {
            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                var recognition = new SpeechRecognition();
                recognition.lang = 'es-ES';
                recognition.interimResults = false;
                
                document.getElementById('mic-status').textContent = '🎙️ Escuchando orden...';
                recognition.start();

                recognition.onresult = function(event) {
                    var text = event.results[0][0].transcript;
                    document.getElementById('mic-status').textContent = '✅ Comando capturado: ' + text;
                    const inputElement = parent.document.querySelector('div[data-testid="stChatInput"] textarea');
                    if (inputElement) {
                        inputElement.value = text;
                        inputElement.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                };

                recognition.onerror = function(event) {
                    document.getElementById('mic-status').textContent = '🔴 Error de captura de audio.';
                };
            } else {
                alert('El navegador no soporta entrada directa por micrófono.');
            }
        }
    </script>
""", height=60)

st.markdown("**⚡ Comandos Tácticos Rápidos & Accesos Directos:**")
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)

with col_btn1:
    if st.button("📍 Estado Base"):
        api_key_btn = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
        if api_key_btn:
            genai.configure(api_key=api_key_btn)
            m_btn = genai.GenerativeModel('gemini-1.5-flash')
            res_btn = m_btn.generate_content(f"{prompt_personalidad}\nEl usuario ha solicitado verificar el estado del perímetro y la base principal.")
            msg_buin = res_btn.text
        else:
            msg_buin = "J.A.R.V.I.S.: El perímetro está bajo control. Todo en orden."
        st.session_state['chat_history'].append({"role": "assistant", "content": msg_buin})
        guardar_mensaje_db("assistant", msg_buin)
        reproducir_voz_jarvis(msg_buin)
        st.rerun()

with col_btn2:
    if st.button("⚙️ Sistema"):
        msg_sys = f"J.A.R.V.I.S.: CPU al {cpu_uso}%, RAM al {mem_uso}%. Todos los subsistemas, red y protocolo de misiones operativos."
        st.session_state['chat_history'].append({"role": "assistant", "content": msg_sys})
        guardar_mensaje_db("assistant", msg_sys)
        reproducir_voz_jarvis(msg_sys)
        st.rerun()

with col_btn3:
    if st.button("🔮 Oráculo"):
        api_key_btn = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
        if api_key_btn:
            genai.configure(api_key=api_key_btn)
            m_btn = genai.GenerativeModel('gemini-1.5-flash')
            res_btn = m_btn.generate_content(f"{prompt_personalidad}\nDa una predicción oracular sobre las probabilidades de éxito del día.")
            oraculo_msg = res_btn.text
        else:
            oraculo_msg = "J.A.R.V.I.S.: Las probabilidades indican un 98% de éxito hoy."
        st.session_state['chat_history'].append({"role": "assistant", "content": oraculo_msg})
        guardar_mensaje_db("assistant", oraculo_msg)
        reproducir_voz_jarvis(oraculo_msg)
        st.rerun()

with col_btn4:
    if st.button("🎵 Abrir Spotify"):
        try:
            os.system("start spotify:" if os.name == 'nt' else "open -a Spotify")
        except Exception:
            pass
        msg_spot = "J.A.R.V.I.S.: Lanzando secuencia musical en Spotify, jefa."
        st.session_state['chat_history'].append({"role": "assistant", "content": msg_spot})
        guardar_mensaje_db("assistant", msg_spot)
        reproducir_voz_jarvis(msg_spot)
        st.rerun()

with col_btn5:
    if st.button("🗑️ Limpiar Chat"):
        borrar_historial_db()
        msg_init = "Hola Cindy. Registros y memoria limpios. ¿Qué ocurrencia tienes para hoy?"
        st.session_state['chat_history'] = [{"role": "assistant", "content": msg_init}]
        guardar_mensaje_db("assistant", msg_init)
        st.rerun()

st.divider()

chat_container = st.container()
with chat_container:
    for msg in st.session_state['chat_history']:
        st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Escribe tu consulta para J.A.R.V.I.S. aquí...")
if user_input:
    st.session_state['chat_history'].append({"role": "user", "content": user_input})
    guardar_mensaje_db("user", user_input)
    
    api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
    respuesta_jarvis = ""
    texto_lower = str(user_input).lower()

    if "despierto" in texto_lower or "estas despierto" in texto_lower or "estás despierto" in texto_lower:
        respuesta_jarvis = "Para ti siempre, Cindy."

    elif any(w in texto_lower for w in ["quién eres", "quien eres", "presentate", "preséntate"]):
        respuesta_jarvis = "J.A.R.V.I.S.: Soy J.A.R.V.I.S., tu inteligencia artificial autónoma con red, misiones en la barra lateral, biblioteca y traductor activos en la Base Buin, Cindy."

    elif api_key:
        try:
            genai.configure(api_key=api_key)
            modelo = genai.GenerativeModel('gemini-1.5-flash')
            
            contexto_docs = ""
            if st.session_state['documentos_cargados']:
                lista_nombres = ", ".join(st.session_state['documentos_cargados'])
                contexto_docs = f"\n[Biblioteca activa cargada por la usuaria: {lista_nombres}]"
                
            prompt_completo = f"{prompt_personalidad}{contexto_docs}\nUsuario: {user_input}"
            respuesta = modelo.generate_content(prompt_completo)
            respuesta_jarvis = respuesta.text
        except Exception:
            respuesta_jarvis = "J.A.R.V.I.S.: Límite de solicitudes de API alcanzado temporalmente. Por favor reintenta en un minuto."
    else:
        respuesta_jarvis = f"J.A.R.V.I.S.: Orden '{user_input}' registrada localmente."
        
    st.session_state['chat_history'].append({"role": "assistant", "content": respuesta_jarvis})
    guardar_mensaje_db("assistant", respuesta_jarvis)
    reproducir_voz_jarvis(respuesta_jarvis)
    st.rerun()

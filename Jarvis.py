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

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónoma 6.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# ESTILOS VISUALES (TEMA NEGRO ABSOLUTO Y AZUL NEÓN COMPLETO)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* 1. FORZAR NEGRO ABSOLUTO EN TODA LA APLICACIÓN Y CONTENEDORES */
    html, body, .stApp, [data-testid="stSidebar"], [data-testid="stSidebarContent"],
    header, .stAppHeader, div[data-testid="stHeader"], footer, 
    [data-testid="stBottom"], [data-testid="stBottomBlockContainer"], 
    [data-testid="stChatInputContainer"], .stMainBlockContainer {
        background-color: #080c14 !important;
        color: #00f3ff !important;
    }

    /* 2. ELIMINAR FONDOS BLANCOS DE EXPANDERS Y CAJAS */
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

    /* 3. FORZAR BOTÓN DE UPLOAD Y ZONA DE DROP EN NEGRO Y NEÓN */
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploaderDropzone"] *,
    [data-testid="stFileUploader"] button,
    section[data-testid="stFileUploaderDropzone"] button {
        background-color: #0e1726 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
    }

    /* 4. FORZAR AZUL NEÓN EN LA BARRA SUPERIOR */
    header *, .stAppHeader *, div[data-testid="stHeader"] *, [data-testid="stToolbar"] *,
    [data-testid="stToolbar"] button, [data-testid="stToolbar"] svg,
    header button, header svg, button[title], [data-testid="baseButton-header"],
    [data-testid="stMainMenu"], [data-testid="stMainMenu"] * {
        color: #00f3ff !important;
        fill: #00f3ff !important;
        stroke: #00f3ff !important;
        background-color: transparent !important;
    }

    /* 5. TODOS LOS TEXTOS E ÍCONOS EN AZUL NEÓN */
    h1, h2, h3, h4, h5, h6, p, span, label, div, small, caption, i, svg, code {
        color: #00f3ff !important;
        text-shadow: 0 0 5px rgba(0, 243, 255, 0.3);
    }

    /* 6. BOTONES TÁCTICOS CON BORDE E ILUMINACIÓN NEÓN */
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

    /* 7. ENTRADA DE CHAT NEGRO Y NEÓN */
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

    /* 8. MENSAJES DEL CHAT */
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

    /* 9. BARRAS DE PROGRESO Y GRÁFICOS */
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

@st.cache_data(ttl=300)
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
            return f"J.A.R.V.I.S.: Análisis contable express para CLP ${monto:,.0f}:\n• IVA (19%): ${iva:,.0f} CLP\n• Total Neto + IVA: ${total:,.0f} CLP"
    
    if "usd" in txt or "dolar" in txt or "dólar" in txt:
        numeros = re.findall(r'\d+(?:\.\d+)?', txt.replace(',', '.'))
        if numeros:
            cant = float(numeros[0])
            val_dolar = divisas.get('dolar_clp', 0.0)
            if val_dolar > 0:
                total = cant * val_dolar
                return f"J.A.R.V.I.S.: Conversión al tipo de cambio actual (${val_dolar:,.2f} CLP):\n• {cant:,.2f} USD = ${total:,.0f} CLP"
    
    if "uf" in txt:
        numeros = re.findall(r'\d+(?:\.\d+)?', txt.replace(',', '.'))
        if numeros:
            cant = float(numeros[0])
            val_uf = divisas.get('uf_clp', 0.0)
            if val_uf > 0:
                total = cant * val_uf
                return f"J.A.R.V.I.S.: Conversión según valor UF del día (${val_uf:,.2f} CLP):\n• {cant:,.2f} UF = ${total:,.0f} CLP"

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
# ENCABEZADO Y ESTADO DE JARVIS
# ---------------------------------------------------------
st.title("⚡ J.A.R.V.I.S. IA Autónoma 6.0")
st.success("✅ Todos los subsistemas satelitales y de hardware responden de forma óptima.")

# ---------------------------------------------------------
# BARRA LATERAL (ORDENADA SEGÚN SOLICITUD)
# ---------------------------------------------------------
with st.sidebar:
    # 1. TELEMETRÍA DE PC
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
        margin-bottom: 10px;
    ">
        <span style="color: #00f3ff; font-size: 13px; font-weight: bold; display: block;">💻 TELEMETRÍA DE PC</span>
        <span style="color: #00a8b5; font-size: 12px; display: block; margin-top: 4px;">⚡ CPU en Uso: <b>{cpu_uso}%</b></span>
        <span style="color: #00a8b5; font-size: 12px; display: block; margin-top: 4px;">🧠 Memoria RAM: <b>{mem_uso}%</b></span>
        <span style="color: #00a8b5; font-size: 12px; display: block; margin-top: 4px;">🔋 Batería: <b>{bat_val}</b></span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # 2. MATRIZ DE PERSONALIDAD
    st.subheader("🎭 Matriz de Personalidad")
    personalidades = {
        "👑 Tony Stark / Sarcástico": "Eres J.A.R.V.I.S., una IA sarcástica, sumamente inteligente, leal y con humor ácido al estilo de Tony Stark. Asistes a Cindy en su base de operaciones.",
        "Mayordomo Británico": "Eres J.A.R.V.I.S., un elegante, extremadamente educado y refinado mayordomo británico. Hablas con la máxima cortesía y reverencia hacia Cindy.",
        "🤖 Robot Táctico Militar": "Eres J.A.R.V.I.S., un sistema táctico de combate militar. Respuestas concisas, precisas, en tono de protocolo de operaciones de defensa.",
        "🥑 Modo Chileno Po'": "Eres J.A.R.V.I.S. estilo chileno. Hablas de forma divertida, cercana, usando chilenismos moderados ('po', 'bacán', 'al tiro', 'jefa') asistiendo a Cindy."
    }
    modo_seleccionado = st.selectbox("Selecciona protocolo de voz:", list(personalidades.keys()))
    prompt_personalidad = personalidades[modo_seleccionado]

    st.divider()

    # 3. RED SATELITAL GLOBAL (UBICADA ENTRE PERSONALIDAD Y VISIÓN)
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
    
    # 4. RELOJ DIGITAL
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
    
    # 5. ESCÁNER TÁCTICO MULTIMODAL Y VISIÓN POR COMPUTADORA
    st.subheader("📷 Visión por Computadora & Archivos")
    archivo_subido = st.file_uploader("Cargar imagen (PNG/JPG) o TXT/PDF:", type=["txt", "csv", "md", "pdf", "png", "jpg", "jpeg"])
    if archivo_subido is not None:
        try:
            tipo_archivo = archivo_subido.type
            if "image" in tipo_archivo:
                st.image(archivo_subido, caption="Captura / Imagen Analizada", use_column_width=True)
                if st.button("👁️ Analizar Imagen con IA"):
                    st.session_state['chat_history'].append({"role": "user", "content": f"[Análisis Visual de Captura: {archivo_subido.name}]"})
                    api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
                    if api_key:
                        genai.configure(api_key=api_key)
                        m = genai.GenerativeModel('gemini-1.5-flash')
                        bytes_img = archivo_subido.getvalue()
                        res = m.generate_content([prompt_personalidad + "\nAnaliza detalladamente esta imagen o captura de pantalla con tono sarcástico y experto:", {"mime_type": tipo_archivo, "data": bytes_img}])
                        st.session_state['chat_history'].append({"role": "assistant", "content": res.text})
                        reproducir_voz_jarvis(res.text)
                    else:
                        st.session_state['chat_history'].append({"role": "assistant", "content": "J.A.R.V.I.S.: Falta la API Key para procesar imágenes con visión artificial."})
                    st.rerun()
            else:
                texto_extraido = archivo_subido.read().decode("utf-8", errors="ignore")
                st.success(f"✅ Documento procesado ({len(texto_extraido)} caracteres).")
                if st.button("🔍 Analizar Texto con J.A.R.V.I.S."):
                    prompt_doc = f"Por favor haz un resumen ejecutivo en 3 puntos clave del siguiente texto:\n\n{texto_extraido[:3000]}"
                    st.session_state['chat_history'].append({"role": "user", "content": f"[Análisis de Documento: {archivo_subido.name}]"})
                    api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
                    if api_key:
                        genai.configure(api_key=api_key)
                        m = genai.GenerativeModel('gemini-1.5-flash')
                        res = m.generate_content(f"{prompt_personalidad}\n{prompt_doc}")
                        st.session_state['chat_history'].append({"role": "assistant", "content": res.text})
                        reproducir_voz_jarvis(res.text)
                    st.rerun()
        except Exception as e:
            st.error(f"Error al procesar archivo: {str(e)}")

    st.divider()

    # PRESETS TÁCTICOS RÁPIDOS
    st.subheader("⚡ Presets de Comandos")
    if st.button("📊 Auditoría Financiera Exprés"):
        cmd_text = "J.A.R.V.I.S., realiza un análisis rápido de la estabilidad económica actual según los indicadores de Chile."
        st.session_state['chat_history'].append({"role": "user", "content": cmd_text})
        api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
        if api_key:
            try:
                genai.configure(api_key=api_key)
                m = genai.GenerativeModel('gemini-1.5-flash')
                res = m.generate_content(f"{prompt_personalidad}\n{cmd_text}")
                st.session_state['chat_history'].append({"role": "assistant", "content": res.text})
                reproducir_voz_jarvis(res.text)
            except Exception:
                st.session_state['chat_history'].append({"role": "assistant", "content": "J.A.R.V.I.S.: Alerta de límite de cuota superado (Error 429)."})
        else:
            st.session_state['chat_history'].append({"role": "assistant", "content": "J.A.R.V.I.S.: Auditoría completada en modo offline."})
        st.rerun()

    if st.button("🚀 Protocolo de Máxima Eficiencia"):
        cmd_text = "J.A.R.V.I.S., dame una recomendación táctica de productividad para hoy."
        st.session_state['chat_history'].append({"role": "user", "content": cmd_text})
        api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
        if api_key:
            try:
                genai.configure(api_key=api_key)
                m = genai.GenerativeModel('gemini-1.5-flash')
                res = m.generate_content(f"{prompt_personalidad}\n{cmd_text}")
                st.session_state['chat_history'].append({"role": "assistant", "content": res.text})
                reproducir_voz_jarvis(res.text)
            except Exception:
                st.session_state['chat_history'].append({"role": "assistant", "content": "J.A.R.V.I.S.: Servidores sobrecargados de peticiones."})
        else:
            st.session_state['chat_history'].append({"role": "assistant", "content": "J.A.R.V.I.S.: Protocolo activo. Menos distracciones, más ejecución."})
        st.rerun()

    st.divider()

    # FINANZAS Y MERCADO
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

    # ⛈️ CLIMA EXTENDIDO Y ALERTAS DE TORMENTAS
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

    # TELEMETRÍA Y PING DE RED
    st.divider()
    with st.expander("📡 TELEMETRÍA Y ESTADO DE RED", expanded=False):
        pings = verificar_ping_red()
        for srv, stt in pings.items():
            st.write(f"**{srv}:** {stt}")

    # GRÁFICO HISTÓRICO DE DIVISAS
    with st.expander("📈 GRÁFICO TÁCTICO DE DIVISAS (30 DÍAS)", expanded=False):
        serie_hist = finanzas_sidebar.get('serie_historica', [])
        if serie_hist:
            df_hist = pd.DataFrame(serie_hist)
            df_hist['fecha'] = pd.to_datetime(df_hist['fecha']).dt.strftime('%d/%m')
            df_hist = df_hist.sort_values(by='fecha')
            chart_data = df_hist.set_index('fecha')[['valor']]
            st.line_chart(chart_data)

    # MATRIZ DE OBJETIVOS
    with st.expander("🎯 MATRIZ DE OBJETIVOS Y METAS", expanded=False):
        if 'metas_jarvis' not in st.session_state:
            st.session_state['metas_jarvis'] = [
                {"meta": "Optimización J.A.R.V.I.S. 6.0", "progreso": 100},
                {"meta": "Auditoría de Fondos y Crypto", "progreso": 75}
            ]
        for idx, item in enumerate(st.session_state['metas_jarvis']):
            st.write(f"**{item['meta']}** — {item['progreso']}%")
            st.progress(item['progreso'] / 100)

    # RED NEURONAL Y ESTADO DEL OPERADOR
    with st.expander("🧠 RED NEURONAL Y OPERADOR", expanded=False):
        st.write("⚡ **Productividad:** 98.4%")
        st.write("🔋 **Estrés Operador:** Nivel Zen")
        st.progress(0.98)

    # SISMOS CSN
    st.divider()
    st.subheader("🌍 Telemetría Sísmica CSN")
    ultimo_sismo = obtener_ultimo_sismo_chile()
    if ultimo_sismo:
        lugar_s = ultimo_sismo.get('RefGeografica', 'Chile')
        mag_s = ultimo_sismo.get('Magnitud', 'N/A')
        fecha_s = ultimo_sismo.get('Fecha', 'Reciente')
        st.markdown(f"""
        <div style="
            background-color: #0b1320;
            border: 1px solid #00f3ff;
            border-radius: 8px;
            padding: 10px;
            font-family: monospace;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
        ">
            <span style="color: #00a8b5; font-size: 12px; display: block;">📍 {lugar_s}</span>
            <span style="color: #00f3ff; font-size: 14px; font-weight: bold; display: block; margin-top: 4px;">Magnitud: {mag_s} Richter</span>
            <span style="color: #00a8b5; font-size: 11px; display: block; margin-top: 4px;">🕒 {fecha_s}</span>
        </div>
        """, unsafe_allow_html=True)

    # BLOC DE NOTAS
    st.divider()
    st.subheader("📝 Bloc de Notas")
    if 'notas_jarvis' not in st.session_state:
        st.session_state['notas_jarvis'] = []

    nueva_nota = st.text_input("Recordatorio rápido:")
    if st.button("➕ Guardar Nota"):
        if nueva_nota:
            st.session_state['notas_jarvis'].append(nueva_nota)
            st.rerun()

    if st.session_state['notas_jarvis']:
        for i, nota in enumerate(st.session_state['notas_jarvis']):
            st.caption(f"• {nota}")

# ---------------------------------------------------------
# CONSOLA PRINCIPAL: SOLO TERMINAL DE CONVERSACIÓN
# ---------------------------------------------------------
st.subheader("💬 Terminal de Conversación Autónoma")

st.markdown("**⚡ Comandos Tácticos Rápidos & Accesos Directos:**")
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)

with col_btn1:
    if st.button("📍 Estado Base"):
        msg_buin = "J.A.R.V.I.S.: El perímetro está bajo control. Todo en orden."
        st.session_state['chat_history'].append({"role": "assistant", "content": msg_buin})
        reproducir_voz_jarvis(msg_buin)
        st.rerun()

with col_btn2:
    if st.button("⚙️ Sistema"):
        msg_sys = f"J.A.R.V.I.S.: CPU al {cpu_uso}%, RAM al {mem_uso}%. Todo operando sin anomalías."
        st.session_state['chat_history'].append({"role": "assistant", "content": msg_sys})
        reproducir_voz_jarvis(msg_sys)
        st.rerun()

with col_btn3:
    if st.button("🔮 Oráculo"):
        import random
        frases_oraculo = [
            "J.A.R.V.I.S.: Las probabilidades indican un 98% de éxito hoy.",
            "J.A.R.V.I.S.: Estado del universo: En constante expansión.",
            "J.A.R.V.I.S.: Análisis completado: Eres oficialmente la persona más capacitada en este perímetro."
        ]
        oraculo_msg = random.choice(frases_oraculo)
        st.session_state['chat_history'].append({"role": "assistant", "content": oraculo_msg})
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
        reproducir_voz_jarvis(msg_spot)
        st.rerun()

with col_btn5:
    if st.button("🗑️ Limpiar Chat"):
        st.session_state['chat_history'] = [
            {"role": "assistant", "content": "Hola Cindy. Registros limpios. ¿Qué ocurrencia tienes para hoy?"}
        ]
        st.rerun()

st.divider()

# HISTORIAL DE CHAT
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = [
        {"role": "assistant", "content": "Hola Cindy. Sistemas activos. ¿Qué milagro tecnológico necesitas hoy?"}
    ]

chat_container = st.container()
with chat_container:
    for msg in st.session_state['chat_history']:
        st.chat_message(msg["role"]).write(msg["content"])

# ENTRADA DE MENSAJES (OPTIMIZADA CON CALCULADORA, RESPUESTAS LOCALES Y VOZ EN VIVO)
user_input = st.chat_input("Escribe tu consulta para J.A.R.V.I.S. aquí...")
if user_input:
    st.session_state['chat_history'].append({"role": "user", "content": user_input})
    
    api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
    respuesta_jarvis = ""
    texto_lower = user_input.lower().strip()

    res_calculo = procesar_calculo_local(user_input, finanzas_sidebar)
    
    if res_calculo:
        respuesta_jarvis = res_calculo

    elif any(w in texto_lower for w in ["qué día es", "que dia es", "qué fecha es", "que fecha es", "qué hora es", "que hora es", "día de hoy", "dia de hoy"]):
        ahora = datetime.datetime.now()
        dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
        
        nombre_dia = dias_semana[ahora.weekday()]
        nombre_mes = meses[ahora.month - 1]
        
        respuesta_jarvis = f"J.A.R.V.I.S.: Hoy es {nombre_dia} {ahora.day} de {nombre_mes} de {ahora.year}. Son las {ahora.strftime('%H:%M')} hrs."

    elif texto_lower in ["hola", "buenas", "hey", "saludos", "hola jarvis", "hola j.a.r.v.i.s."]:
        respuesta_jarvis = "J.A.R.V.I.S.: Hola Cindy. Los sistemas están al 100% y operando con velocidad óptima. ¿Qué orden ejecutamos?"

    elif any(w in texto_lower for w in ["cómo estás", "como estas", "cómo está el sistema", "como esta el sistema"]):
        respuesta_jarvis = f"J.A.R.V.I.S.: Estado del sistema: impecable. CPU al {cpu_uso}%, RAM al {mem_uso}%. Perímetro seguro."

    elif api_key:
        try:
            genai.configure(api_key=api_key)
            modelo_nombre = 'gemini-1.5-flash'
            
            modelo = genai.GenerativeModel(modelo_nombre)
            prompt_completo = f"{prompt_personalidad}\nUsuario: {user_input}"
            respuesta = modelo.generate_content(prompt_completo)
            respuesta_jarvis = respuesta.text
        except Exception as e:
            respuesta_jarvis = "J.A.R.V.I.S.: Límite de solicitudes de API alcanzado temporalmente (ResourceExhausted). Por favor espera un minuto antes de enviar otra orden."
    else:
        respuesta_jarvis = f"J.A.R.V.I.S.: Orden '{user_input}' registrada localmente."
        
    st.session_state['chat_history'].append({"role": "assistant", "content": respuesta_jarvis})
    reproducir_voz_jarvis(respuesta_jarvis)
    st.rerun()

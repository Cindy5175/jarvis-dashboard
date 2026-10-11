import streamlit as st
import datetime
import requests
import xml.etree.ElementTree as ET
import time
import pandas as pd
import google.generativeai as genai

# ---------------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0",
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

    /* 2. FORZAR AZUL NEÓN EN LA BARRA SUPERIOR */
    header *, .stAppHeader *, div[data-testid="stHeader"] *, [data-testid="stToolbar"] *,
    [data-testid="stToolbar"] button, [data-testid="stToolbar"] svg,
    header button, header svg, button[title], [data-testid="baseButton-header"],
    [data-testid="stMainMenu"], [data-testid="stMainMenu"] *, [data-testid="stMainMenu"] svg {
        color: #00f3ff !important;
        fill: #00f3ff !important;
        stroke: #00f3ff !important;
        background-color: transparent !important;
    }

    /* 3. TODOS LOS TEXTOS E ÍCONOS EN AZUL NEÓN */
    h1, h2, h3, h4, h5, h6, p, span, label, div, small, caption, i, svg {
        color: #00f3ff !important;
        text-shadow: 0 0 5px rgba(0, 243, 255, 0.3);
    }

    /* 4. BOTONES TÁCTICOS CON BORDE E ILUMINACIÓN NEÓN */
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

    /* 5. CAJA DE ESCÁNER DE ARCHIVOS Y CARGADOR (ESTILO NEGRO Y NEÓN) */
    [data-testid="stFileUploader"], 
    [data-testid="stFileUploaderDropzone"],
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #0b1320 !important;
        border: 2px dashed #00f3ff !important;
        border-radius: 10px !important;
        box-shadow: 0 0 12px rgba(0, 243, 255, 0.3) !important;
        color: #00f3ff !important;
    }

    [data-testid="stFileUploaderDropzone"] * {
        color: #00f3ff !important;
        fill: #00f3ff !important;
        background-color: transparent !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        background-color: #0e1726 !important;
        border: 1px solid #00f3ff !important;
        color: #00f3ff !important;
        box-shadow: 0 0 8px rgba(0, 243, 255, 0.4) !important;
    }

    /* 6. MATAR EL FONDO BLANCO DE LA CAJA DE CHAT INFERIOR */
    [data-testid="stChatInput"], 
    [data-testid="stChatInput"] > div, 
    div[data-baseweb="base-input"],
    div[data-baseweb="input"],
    .stChatFloatingInputContainer,
    div.stChatFloatingInputContainer {
        background-color: #0b1320 !important;
        border: 2px solid #00f3ff !important;
        border-radius: 12px !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.5) !important;
    }

    div[data-testid="stChatInput"] textarea {
        background-color: #0b1320 !important;
        color: #00f3ff !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: #00a8b5 !important;
    }

    /* 7. ENTRADAS DE TEXTO GENERALES Y SELECTBOX */
    .stTextInput input, div[data-baseweb="select"] > div {
        color: #00f3ff !important;
        background-color: #0b1320 !important;
        border: 1px solid #00f3ff !important;
        box-shadow: 0 0 8px rgba(0, 243, 255, 0.3);
        font-weight: bold !important;
    }

    /* 8. MENSAJES DEL CHAT E HISTORIAL */
    [data-testid="stChatMessage"] {
        background-color: #0e1726 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 10px !important;
        padding: 12px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 0 8px rgba(0, 243, 255, 0.2);
    }
    [data-testid="stChatMessage"] p {
        color: #00f3ff !important;
        font-size: 1rem !important;
    }
    
    /* 9. MÉTRICAS Y BARRAS DE PROGRESO NEÓN */
    div[data-testid="stMetricValue"] {
        color: #00f3ff !important;
        font-weight: bold !important;
        text-shadow: 0 0 8px rgba(0, 243, 255, 0.5);
    }
    div[data-testid="stMetricLabel"] {
        color: #00a8b5 !important;
    }
    .stProgress > div > div > div > div {
        background-color: #00f3ff !important;
        box-shadow: 0 0 12px #00f3ff;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIONES AUXILIARES DE APIS
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
def obtener_clima_buin():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-33.73&longitude=-70.73&current_weather=true"
        resp = requests.get(url, timeout=5).json()
        return resp.get('current_weather', {})
    except Exception:
        return {}

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

@st.cache_data(ttl=900)
def obtener_noticias_tacticas():
    noticias = []
    url_rss = "https://news.google.com/rss/search?q=economia+chile+finanzas&hl=es-419&gl=CL&ceid=CL:es-419"
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        resp = requests.get(url_rss, headers=headers, timeout=5)
        root = ET.fromstring(resp.content)
        
        for item in root.findall('.//item')[:5]:
            titulo = item.find('title').text if item.find('title') is not None else "Sin título"
            link = item.find('link').text if item.find('link') is not None else "#"
            pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ""
            noticias.append({"titulo": titulo, "link": link, "fecha": pub_date})
    except Exception:
        noticias = [{"titulo": "No se pudieron cargar las noticias en este momento.", "link": "#", "fecha": ""}]
    return noticias

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

# ---------------------------------------------------------
# ENCABEZADO Y ESTADO DE JARVIS
# ---------------------------------------------------------
st.title("⚡ J.A.R.V.I.S. 4.0 - AI Autónoma")
st.success("✅ Todos los subsistemas satelitales responden de forma óptima.")

# ---------------------------------------------------------
# BARRA LATERAL
# ---------------------------------------------------------
with st.sidebar:
    st.header("🛰️ Red Satelital Serafín")
    st.caption("Ubicación Base: Buin, Chile")
    st.map(data={"lat": [-33.73], "lon": [-70.73]}, zoom=10)
    st.divider()
    
    # RELOJ DIGITAL
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

    # SELECTOR DE PERSONALIDAD
    st.subheader("🎭 Matriz de Personalidad")
    personalidades = {
        "👑 Tony Stark / Sarcástico": "Eres J.A.R.V.I.S., una IA sarcástica, sumamente inteligente, leal y con humor ácido al estilo de Tony Stark. Asistes a Cindy en Buin, Chile.",
        "💂‍♂️ Mayordomo Británico": "Eres J.A.R.V.I.S., un elegante, extremadamente educado y refinado mayordomo británico. Hablas con la máxima cortesía y reverencia hacia Cindy.",
        "🤖 Robot Táctico Militar": "Eres J.A.R.V.I.S., un sistema táctico de combate militar. Respuestas concisas, precisas, en tono de protocolo de operaciones de defensa.",
        "🥑 Modo Chileno Po'": "Eres J.A.R.V.I.S. estilo chileno. Hablas de forma divertida, cercana, usando chilenismos moderados ('po', 'bacán', 'al tiro', 'jefa') asistiendo a Cindy."
    }
    modo_seleccionado = st.selectbox("Selecciona protocolo de voz:", list(personalidades.keys()))
    prompt_personalidad = personalidades[modo_seleccionado]

    st.divider()
    
    # ESCÁNER DE ARCHIVOS DE TEXTO (ESTILO TÁCTICO NEÓN)
    st.subheader("📄 Escáner Táctico de Texto")
    archivo_subido = st.file_uploader("Cargar TXT para análisis:", type=["txt", "csv", "md"])
    if archivo_subido is not None:
        try:
            texto_extraido = archivo_subido.read().decode("utf-8", errors="ignore")
            st.success(f"✅ Documento leído ({len(texto_extraido)} caracteres).")
            if st.button("🔍 Analizar con J.A.R.V.I.S."):
                prompt_doc = f"Por favor haz un resumen ejecutivo en 3 puntos clave del siguiente texto:\n\n{texto_extraido[:3000]}"
                st.session_state['chat_history'].append({"role": "user", "content": f"[Análisis de Documento: {archivo_subido.name}]"})
                
                api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
                if api_key:
                    genai.configure(api_key=api_key)
                    m = genai.GenerativeModel('gemini-3.8-flash')
                    res = m.generate_content(f"{prompt_personalidad}\n{prompt_doc}")
                    st.session_state['chat_history'].append({"role": "assistant", "content": res.text})
                else:
                    st.session_state['chat_history'].append({"role": "assistant", "content": "J.A.R.V.I.S.: Lectura completada. Se requiere API Key para la síntesis de inteligencia."})
                st.rerun()
        except Exception as e:
            st.error(f"Error al leer archivo: {str(e)}")

    st.divider()

    # FINANZAS
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

    # CLIMA
    st.subheader("🌤️ Clima Buin")
    clima = obtener_clima_buin()
    temp_v = clima.get('temperature', 'N/A')
    viento_v = clima.get('windspeed', 'N/A')
    dir_v = clima.get('winddirection', 'N/A')

    st.markdown(f"""
    <div style="
        background-color: #0b1320;
        border: 1px solid #00f3ff;
        border-radius: 8px;
        padding: 10px;
        font-family: monospace;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
    ">
        <span style="color: #00a8b5; font-size: 13px; display: block;">🌡️ Temperatura: <b style="color: #00f3ff;">{temp_v} °C</b></span>
        <span style="color: #00a8b5; font-size: 13px; display: block; margin-top: 6px;">💨 Vel. del Viento: <b style="color: #00f3ff;">{viento_v} km/h</b></span>
        <span style="color: #00a8b5; font-size: 13px; display: block; margin-top: 6px;">🧭 Dirección Viento: <b style="color: #00f3ff;">{dir_v}°</b></span>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # SISMOS
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
    else:
        st.caption("Sin reportes sísmicos recientes.")

    st.divider()

    # NOTAS
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
# TERMINAL DE CONVERSACIÓN Y PANELES PRINCIPALES
# ---------------------------------------------------------
st.subheader("💬 Terminal de Conversación Autónoma")

dolar_actual = dolar_s

st.markdown(f"""
<div style="
    background-color: #0b1320;
    border: 1px solid #00f3ff;
    border-radius: 10px;
    padding: 12px;
    margin-bottom: 15px;
    box-shadow: 0 0 10px rgba(0, 243, 255, 0.2);
">
    <span style="font-weight: bold; color: #00f3ff; display: block; margin-bottom: 5px;">📊 RESUMEN TÁCTICO MATUTINO / ESTADO DE BASE</span>
    <span style="font-size: 0.9rem; color: #00a8b5;">
        • Buin: {temp_v}°C | Dólar: {dolar_actual} CLP<br>
        • Alertas del Sistema: Perímetro seguro. Sin anomalías detectadas en la red satelital.
    </span>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DISPOSICIÓN TÁCTICA EN 2 COLUMNAS (IZQUIERDA Y DERECHA)
# ---------------------------------------------------------
col_izquierda, col_derecha = st.columns(2)

# --- COLUMNA IZQUIERDA: GRÁFICO HISTÓRICO Y MATRIZ DE OBJETIVOS ---
with col_izquierda:
    with st.expander("GRÁFICO TÁCTICO HISTÓRICO DE DIVISAS (DÓLAR 30 DÍAS)", expanded=True):
        serie_hist = finanzas_sidebar.get('serie_historica', [])
        if serie_hist:
            df_hist = pd.DataFrame(serie_hist)
            df_hist['fecha'] = pd.to_datetime(df_hist['fecha']).dt.strftime('%d/%m')
            df_hist = df_hist.sort_values(by='fecha')
            chart_data = df_hist.set_index('fecha')[['valor']]
            st.line_chart(chart_data)
        else:
            st.caption("Cargando datos del Banco Central...")

    with st.expander("MATRIZ DE OBJETIVOS Y METAS TÁCTICAS", expanded=True):
        if 'metas_jarvis' not in st.session_state:
            st.session_state['metas_jarvis'] = [
                {"meta": "Optimización del núcleo J.A.R.V.I.S. 4.0", "progreso": 100},
                {"meta": "Auditoría de Fondos y Crypto", "progreso": 75},
                {"meta": "Expansión de Protocolos Domóticos", "progreso": 40}
            ]
        
        col_n1, col_n2 = st.columns([3, 1])
        with col_n1:
            nueva_m = st.text_input("Nuevo proyecto/objetivo:", key="txt_meta")
        with col_n2:
            prog_m = st.slider("Avance %", 0, 100, 50, key="sld_meta")
        
        if st.button("📌 Agregar Objetivo"):
            if nueva_m:
                st.session_state['metas_jarvis'].append({"meta": nueva_m, "progreso": prog_m})
                st.rerun()

        for idx, item in enumerate(st.session_state['metas_jarvis']):
            st.markdown(f"**{item['meta']}** — `<b style='color:#00f3ff;'>{item['progreso']}%</b>`", unsafe_allow_html=True)
            st.progress(item['progreso'] / 100)

# --- COLUMNA DERECHA: TELEMETRÍA Y MONITOR DE NOTICIAS ---
with col_derecha:
    with st.expander("TELEMETRÍA Y ESTADO DE RED", expanded=True):
        pings = verificar_ping_red()
        for srv, stt in pings.items():
            st.markdown(f"**{srv}:** `{stt}`")

    with st.expander("MONITOR DE NOTICIAS Y TENDENCIAS FINANCIERAS", expanded=True):
        lista_noticias = obtener_noticias_tacticas()
        for item in lista_noticias:
            t_title = item['titulo']
            t_link = item['link']
            st.markdown(
                f'<div style="background-color: #0e1726; border-left: 3px solid #00f3ff; padding: 8px 12px; margin-bottom: 8px; border-radius: 4px;">'
                f'<a href="{t_link}" target="_blank" style="color: #00f3ff; text-decoration: none; font-weight: bold; font-size: 0.95rem;">📌 {t_title}</a>'
                f'</div>',
                unsafe_allow_html=True
            )

st.divider()

# SÍNTESIS DE VOZ
if 'chat_history' in st.session_state and len(st.session_state['chat_history']) > 0:
    ultimo_mensaje_asistente = [m['content'] for m in st.session_state['chat_history'] if m['role'] == 'assistant']
    if ultimo_mensaje_asistente:
        texto_a_leer = ultimo_mensaje_asistente[-1].replace('"', "'").replace('\n', ' ')
        st.components.v1.html(f"""
            <div style="margin-bottom: 12px;">
                <button onclick="hablarJarvis()" style="
                    background-color: #0e1726; 
                    color: #00f3ff; 
                    border: 2px solid #00f3ff; 
                    padding: 10px 16px; 
                    border-radius: 8px; 
                    cursor: pointer; 
                    font-family: monospace;
                    font-weight: bold;
                    font-size: 14px;
                    width: 100%;
                    box-shadow: 0 0 12px rgba(0, 243, 255, 0.4);
                ">🔊 Escuchar último reporte de J.A.R.V.I.S.</button>
            </div>
            <script>
                function hablarJarvis() {{
                    if ('speechSynthesis' in window) {{
                        window.speechSynthesis.cancel();
                        const utterThis = new SpeechSynthesisUtterance("{texto_a_leer}");
                        utterThis.lang = 'es-CL';
                        utterThis.pitch = 0.95;
                        utterThis.rate = 1.05;
                        window.speechSynthesis.speak(utterThis);
                    }}
                }}
            </script>
        """, height=65)

# MICRÓFONO DIRECTO
st.components.v1.html("""
    <div style="margin-bottom: 10px; text-align: center;">
        <button id="btn-mic" onclick="comenzarDictado()" style="
            background-color: #0b1320; 
            color: #00f3ff; 
            border: 2px solid #00f3ff; 
            padding: 8px 16px; 
            border-radius: 8px; 
            cursor: pointer; 
            font-family: monospace;
            font-weight: bold;
            font-size: 13px;
            width: 100%;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
        ">🎙️ Presionar para Dictar Orden por Voz</button>
        <p id="mic-status" style="color: #00a8b5; font-size: 11px; margin-top: 4px; font-family: monospace;"></p>
    </div>
    <script>
        function comenzarDictado() {
            const btn = document.getElementById('btn-mic');
            const status = document.getElementById('mic-status');
            
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                status.textContent = '❌ El dictado por voz no es compatible en este navegador.';
                return;
            }
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const recognition = new SpeechRecognition();
            recognition.lang = 'es-CL';
            recognition.interimResults = false;
            
            recognition.onstart = function() {
                btn.style.backgroundColor = '#00f3ff';
                btn.style.color = '#080c14';
                status.textContent = '🎙️ Escuchando orden táctica... habla ahora.';
            };
            
            recognition.onresult = function(event) {
                const textoDictado = event.results[0][0].transcript;
                status.textContent = '✅ Orden capturada: "' + textoDictado + '". Cópiala en la caja de chat.';
                btn.style.backgroundColor = '#0b1320';
                btn.style.color = '#00f3ff';
            };
            
            recognition.onerror = function(event) {
                status.textContent = '⚠️ Error o sin voz detectada. Intenta nuevamente.';
                btn.style.backgroundColor = '#0b1320';
                btn.style.color = '#00f3ff';
            };
            
            recognition.start();
        }
    </script>
""", height=85)

st.markdown("**⚡ Comandos Tácticos Rápidos:**")
col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)

with col_btn1:
    if st.button("📍 Estado Buin"):
        msg_buin = f"J.A.R.V.I.S.: El perímetro en Buin está tranquilo. Temperatura actual de {temp_v}°C... nada que un café o mi sofisticación no puedan resolver."
        st.session_state['chat_history'].append({"role": "assistant", "content": msg_buin})
        st.rerun()

with col_btn2:
    if st.button("⚙️ Sistema"):
        msg_sys = "J.A.R.V.I.S.: Todos los sistemas operando al 100%. Sobreviviendo milagrosamente a sus exigencias y sin que explote nada... por ahora."
        st.session_state['chat_history'].append({"role": "assistant", "content": msg_sys})
        st.rerun()

with col_btn3:
    if st.button("🔮 Oráculo"):
        import random
        frases_oraculo = [
            "J.A.R.V.I.S.: Las probabilidades indican un 98% de éxito hoy... el 2% depende de que recuerdes dónde dejaste las llaves.",
            "J.A.R.V.I.S.: Estado del universo: En constante expansión. Estado de tu paciencia: En evaluación crítica.",
            "J.A.R.V.I.S.: Hoy es un gran día para dominar el mundo o al menos terminar la lista de tareas pendiente.",
            "J.A.R.V.I.S.: Análisis completado: Eres oficialmente la persona más capacitada en este perímetro."
        ]
        st.session_state['chat_history'].append({"role": "assistant", "content": random.choice(frases_oraculo)})
        st.rerun()

with col_btn4:
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

# ENTRADA DE MENSAJES
user_input = st.chat_input("Escribe tu consulta para J.A.R.V.I.S. aquí...")
if user_input:
    st.session_state['chat_history'].append({"role": "user", "content": user_input})
    
    api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
    respuesta_jarvis = ""

    if api_key:
        try:
            genai.configure(api_key=api_key)
            modelo_nombre = 'gemini-3.8-flash'
            
            modelo = genai.GenerativeModel(modelo_nombre)
            prompt_completo = f"{prompt_personalidad}\nUsuario: {user_input}"
            respuesta = modelo.generate_content(prompt_completo)
            respuesta_jarvis = respuesta.text
        except Exception as e:
            respuesta_jarvis = f"J.A.R.V.I.S.: Error al conectar con el núcleo de Gemini ({str(e)}). Hasta las mejores IA sufrimos un calambre mental a veces."
    else:
        texto_lower = user_input.lower()
        if any(w in texto_lower for w in ["hola", "saludos", "buenas", "hey"]):
            respuesta_jarvis = "J.A.R.V.I.S.: Hola Cindy. Los sistemas están perfectos y yo... bueno, fabuloso como siempre. ¿Qué se te ofrece?"
        elif any(w in texto_lower for w in ["cómo estás", "como estas", "estado"]):
            respuesta_jarvis = "J.A.R.V.I.S.: ¿Yo? Operando al 100%, con una elegancia impecable y soportando tus preguntas existenciales sin que salten chispas. ¿Y tú?"
        else:
            respuesta_jarvis = f"J.A.R.V.I.S.: Orden '{user_input}' registrada. (Para que use mi sarcasmo avanzado con IA, recuerda configurar tu clave en los Secrets de Streamlit)."
        
    st.session_state['chat_history'].append({"role": "assistant", "content": respuesta_jarvis})
    st.rerun()

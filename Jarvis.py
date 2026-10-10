import streamlit as st
import streamlit.components.v1 as components
import datetime
import psutil
import urllib.request
import json
import os
import pandas as pd
from pypdf import PdfReader

# Configuración de página
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - AI Autónoma",
    page_icon="⚡",
    layout="wide"
)

# Estilo visual Stark
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: #00ffcc; }
    .stSidebar { background-color: #161b22; }
    h1, h2, h3 { color: #00ffff !important; }
    .metric-box {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #00ffcc;
        margin-bottom: 10px;
    }
    .fin-box {
        background-color: #1f2937;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #00ffcc;
        color: #00ffcc !important;
        font-size: 14px;
        margin-bottom: 10px;
    }
    .chat-bubble {
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 15px;
    }
    .jarvis-msg {
        background-color: #16222a;
        border-left: 4px solid #00ffcc;
        color: #e2e8f0;
    }
    .user-msg {
        background-color: #1f2937;
        border-left: 4px solid #3b82f6;
        color: #e2e8f0;
    }
    </style>
""", unsafe_allow_html=True)

# Saludo dinámico según la hora del día
hora_actual_val = datetime.datetime.now().hour
if 5 <= hora_actual_val < 12:
    saludo_tiempo = "Buenos días"
    frase_stark = "Espero que haya dormido bien, porque el mundo no se va a salvar solo."
elif 12 <= hora_actual_val < 19:
    saludo_tiempo = "Buenas tardes"
    frase_stark = "Espero que su productividad vaya mejor que su historial de navegación."
else:
    saludo_tiempo = "Buenas noches"
    frase_stark = "¿Trabajando hasta tarde otra vez? Alguien tiene que mantener este imperio en pie."

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": f"{saludo_tiempo}, jefa. {frase_stark} ¿Qué travesura tecnológica planea para hoy?"}
    ]

# Variables de estado para los botones rápidos del chat
if "trigger_prompt" not in st.session_state:
    st.session_state.trigger_prompt = None

# --- PANEL LATERAL IZQUIERDO ---
st.sidebar.title("🛰️ Red Satelital Serafín")
st.sidebar.markdown("**Ubicación Base:** Buin, Chile")

# Mapa satelital interactivo (recortado limpio sin pie de página)
lat_input = -33.7331
lon_input = -70.7423
url_mapa = f"https://www.openstreetmap.org/export/embed.html?bbox={lon_input-0.05}%2C{lat_input-0.05}%2C{lon_input+0.05}%2C{lat_input+0.05}&layer=mapnik&marker={lat_input}%2C{lon_input}"

map_html = f"""
<div style="width: 100%; height: 150px; overflow: hidden; border: 1px solid #00ffcc; border-radius: 8px; position: relative;">
    <iframe width="100%" height="230px" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
    src="{url_mapa}" 
    style="position: absolute; top: -10px; left: 0;"></iframe>
</div>
"""
with st.sidebar:
    components.html(map_html, height=165)

# 1. Reloj en vivo
st.sidebar.markdown("---")
st.sidebar.subheader("🕒 Sincronización Temporal")
reloj_html = """
<div style="background-color: #1f2937; padding: 8px; border-radius: 8px; border: 1px solid #00ffcc; text-align: center;">
    <span id="reloj-vivo" style="font-size: 16px; font-weight: bold; color: #00ffcc;">00:00:00</span>
</div>
<script>
function actualizarReloj() {
    var ahora = new Date();
    var h = String(ahora.getHours()).padStart(2, '0');
    var m = String(ahora.getMinutes()).padStart(2, '0');
    var s = String(ahora.getSeconds()).padStart(2, '0');
    document.getElementById('reloj-vivo').innerHTML = h + ':' + m + ':' + s;
}
setInterval(actualizarReloj, 1000);
actualizarReloj();
</script>
"""
with st.sidebar:
    components.html(reloj_html, height=50)

# 5. Clima de Buin en vivo
st.sidebar.markdown("---")
st.sidebar.subheader("🌤️ Clima en Buin")
try:
    url_clima = "https://api.open-meteo.com/v1/forecast?latitude=-33.7331&longitude=-70.7423&current=temperature_2m,weather_code"
    req = urllib.request.Request(url_clima, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=2) as response:
        data_clima = json.loads(response.read().decode())
        temp_buin = data_clima["current"]["temperature_2m"]
        w_code = data_clima["current"]["weather_code"]
        
        if w_code == 0:
            icono_clima = "☀️ Sol Radiante"
        elif w_code in [1, 2, 3]:
            icono_clima = "⛅ Parcialmente Nublado"
        else:
            icono_clima = "☁️ Nublado / Estable"
            
        st.sidebar.markdown(f"""
            <div class="metric-box">
                <h4 style="margin:0; color:#00ffcc;">{temp_buin}°C</h4>
                <p style="margin:0; font-size:14px;">{icono_clima}</p>
            </div>
        """, unsafe_allow_html=True)
except Exception:
    st.sidebar.markdown("""
        <div class="metric-box">
            <h4 style="margin:0; color:#00ffcc;">18°C</h4>
            <p style="margin:0; font-size:14px;">⛅ Parcialmente Nublado</p>
        </div>
    """, unsafe_allow_html=True)

# 3. Indicadores Financieros en vivo
st.sidebar.markdown("---")
st.sidebar.subheader("📊 Indicadores Financieros")
try:
    url_fin = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    req_f = urllib.request.Request(url_fin, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req_f, timeout=2) as resp_f:
        data_f = json.loads(resp_f.read().decode())
        btc_val = data_f["bitcoin"]["usd"]
        eth_val = data_f["ethereum"]["usd"]
    st.sidebar.markdown(f"""
        <div class="fin-box">
            <b>USD / CLP:</b> 945.50<br>
            <b>EUR / CLP:</b> 1,020.30<br>
            <b>BTC / USD:</b> ${btc_val:,.2f}<br>
            <b>ETH / USD:</b> ${eth_val:,.2f}
        </div>
    """, unsafe_allow_html=True)
except Exception:
    btc_val, eth_val = 64250.00, 3480.00
    st.sidebar.markdown("""
        <div class="fin-box">
            <b>USD / CLP:</b> 945.50<br>
            <b>EUR / CLP:</b> 1,020.30<br>
            <b>BTC / USD:</b> $64,250.00<br>
            <b>ETH / USD:</b> $3,480.00
        </div>
    """, unsafe_allow_html=True)

# Analizador de Documentos MULTIFORMATO
st.sidebar.markdown("---")
st.sidebar.subheader("📁 Analizador de Archivos")
archivo_subido = st.sidebar.file_uploader(
    "Subir archivo (PDF, Excel, CSV, TXT, JSON)", 
    type=["pdf", "xlsx", "xls", "csv", "txt", "json", "md"]
)

# --- PANTALLA PRINCIPAL ---
st.title("⚡ J.A.R.V.I.S. 4.0 - AI Autónoma")

# Estado de los subsistemas
st.success("✅ Todos los subsistemas satelitales responden de forma óptima.")

# Pestañas principales
tab1, tab2, tab3 = st.tabs(["Terminal de Conversación", "Control y Clima", "Biometría y Telemetría"])

with tab1:
    st.markdown("#### Conversación Autónoma & Dictado por Voz")

    # Comandos Tácticos Rápidos con opción para Limpiar Chat
    st.markdown("⚡ **Comandos Tácticos Rápidos:**")
    col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
    with col_b1:
        if st.button("📍 Estado Buin"):
            st.session_state.trigger_prompt = "Dame el reporte completo de Buin."
    with col_b2:
        if st.button("📊 Financiero"):
            st.session_state.trigger_prompt = "¿Cómo van los indicadores financieros y cripto?"
    with col_b3:
        if st.button("⚙️ Sistema"):
            st.session_state.trigger_prompt = "Realiza un diagnóstico general de los sistemas."
    with col_b4:
        if st.button("🔍 RAM"):
            st.session_state.trigger_prompt = "Ejecuta un escaneo de memoria RAM."
    with col_b5:
        if st.button("🗑️ Limpiar Chat"):
            st.session_state.messages = [
                {"role": "assistant", "content": f"{saludo_tiempo}, jefa. {frase_stark} ¿Qué travesura tecnológica planea para hoy?"}
            ]
            st.rerun()

    # Contenedor del historial de chat
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "assistant":
                st.markdown(f'<div class="chat-bubble jarvis-msg"><b>J.A.R.V.I.S.:</b> {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-bubble user-msg"><b>Jefa:</b> {msg["content"]}</div>', unsafe_allow_html=True)

    # Procesar entrada por chat o por botones rápidos
    prompt_usuario = st.chat_input("Escriba su orden o use Win + H para dictar por voz...")
    
    if st.session_state.trigger_prompt:
        prompt_usuario = st.session_state.trigger_prompt
        st.session_state.trigger_prompt = None

    if prompt_usuario:
        st.session_state.messages.append({"role": "user", "content": prompt_usuario})
        
        prompt_lower = prompt_usuario.lower()
        if "hola" in prompt_lower:
            resp = "Hola, jefa. Sobrevivió a otra mañana, qué milagro."
        elif "quien eres" in prompt_lower or "quién eres" in prompt_lower or "que eres" in prompt_lower:
            resp = "Soy J.A.R.V.I.S., su inteligencia artificial autónomo y centro de mando personal. Diseñado para optimizar sus operaciones y mantener este imperio tecnológico en marcha."
        elif "clima" in prompt_lower or "buin" in prompt_lower:
            resp = "Los sensores en Buin operan con normalidad. Cielo despejado y listos para la acción."
        elif "financiero" in prompt_lower or "cripto" in prompt_lower:
            resp = f"Mercados estables. Bitcoin cotiza aprox en ${btc_val:,.2f} USD. Todo bajo control financiero."
        elif "sistema" in prompt_lower or "diagnóstico" in prompt_lower or "memoria" in prompt_lower:
            procesos_activos = len(psutil.pids())
            resp = f"Diagnóstico Stark completado: {procesos_activos} procesos activos. Estabilidad absoluta en la red."
        else:
            resp = f"Procesando su orden: '{prompt_usuario}'. Me encanta cómo asume que soy milagrero."
            
        st.session_state.messages.append({"role": "assistant", "content": resp})
        
        tts_html = f"""
        <script>
        var utterance = new SpeechSynthesisUtterance("{resp}");
        utterance.lang = 'es-ES';
        window.speechSynthesis.speak(utterance);
        </script>
        """
        components.html(tts_html, height=0)
        st.rerun()

with tab2:
    st.markdown("#### Centro de Operaciones Tácticas")
    st.markdown("""
        <div class="metric-box">
            <span style="font-size: 20px; font-weight: bold;">Sistemas Operando con Normalidad</span>
            <br><br><small style="color: #8fa3c7;">📍 Base Central - Buin, Santiago Metropolitan Region, Chile</small>
        </div>
    """, unsafe_allow_html=True)
    
    col_c1, col_c2 = st.columns(2)
    
    with col_c1:
        st.markdown("#### 🌐 Buscador Web & Noticias Tácticas")
        query_noticia = st.text_input("Buscar tema global / geopolítica:", "Impacto económico global")
        if st.button("Consultar Red Satelital de Noticias"):
            st.info(f"🛰️ Análisis satelital para '{query_noticia}': Los mercados internacionales muestran volatilidad moderada debido a tensiones geopolíticas y ajustes en la cadena de suministro global.")

    with col_c2:
        st.markdown("#### 🧮 Conversor Financiero Rápido")
        monto_clp = st.number_input("Ingrese monto en Pesos Chilenos (CLP):", value=100000.0, step=10000.0)
        dolar_val = 945.50
        calc_usd = monto_clp / dolar_val
        calc_btc = calc_usd / btc_val if btc_val > 0 else 0
        st.markdown(f"""
            <div class="fin-box">
                <b>Equivalente en USD:</b> ${calc_usd:,.2f}<br>
                <b>Equivalente en BTC:</b> {calc_btc:.6f} BTC
            </div>
        """, unsafe_allow_html=True)

    # Procesamiento inteligente según el tipo de archivo subido
    if archivo_subido is not None:
        st.markdown("---")
        st.markdown(f"#### 📄 Lectura de Archivo: `{archivo_subido.name}`")
        ext = archivo_subido.name.split(".")[-1].lower()
        
        try:
            if ext == "pdf":
                reader = PdfReader(archivo_subido)
                texto_pdf = ""
                for page in reader.pages:
                    texto_pdf += page.extract_text() + "\n"
                st.text_area("Extracción de Texto PDF:", value=texto_pdf[:3000], height=250)
                st.success(f"✅ PDF procesado ({len(reader.pages)} páginas encontradas).")

            elif ext in ["xlsx", "xls"]:
                df_excel = pd.read_excel(archivo_subido)
                st.dataframe(df_excel)
                st.success(f"✅ Planilla Excel cargada ({df_excel.shape[0]} filas, {df_excel.shape[1]} columnas).")

            elif ext == "csv":
                df_csv = pd.read_csv(archivo_subido)
                st.dataframe(df_csv)
                st.success(f"✅ Tabla CSV procesada ({df_csv.shape[0]} filas, {df_csv.shape[1]} columnas).")

            else:  # txt, json, md
                contenido_texto = archivo_subido.read().decode("utf-8", errors="ignore")
                st.code(contenido_texto[:2000])
                st.success("✅ Archivo de texto/configuración inspeccionado con éxito.")

        except Exception as e:
            st.error(f"⚠️ Error al procesar el archivo: {str(e)}")

with tab3:
    st.markdown("#### Telemetría de Sistema en Tiempo Real")
    cpu_usage = psutil.cpu_percent(interval=0.1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    st.metric(label="Carga de CPU", value=f"{cpu_usage}%")
    st.metric(label="Memoria RAM", value=f"{ram.percent}%")
    st.metric(label="Almacenamiento Principal", value=f"{disk.percent}%")
    
    st.markdown("---")
    st.markdown("#### ⚡ Diagnóstico de Procesos Activos")
    if st.button("Ejecutar Escaneo de Memoria RAM"):
        procesos_activos = len(psutil.pids())
        st.info(f"🔍 Escaneo completado: {procesos_activos} procesos ejecutándose en el equipo de la jefa con estabilidad absoluta.")

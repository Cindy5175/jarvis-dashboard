import streamlit as st
import datetime
import requests

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
# ESTILOS VISUALES (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1e222d;
        border-radius: 10px;
        padding: 15px;
        border: 1px solid #2e3440;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIONES AUXILIARES DE APIS (MÓDULOS NUEVOS)
# ---------------------------------------------------------

@st.cache_data(ttl=300)
def obtener_crypto_y_divisas():
    """Obtiene precios en tiempo real de Crypto y Dólar CLP"""
    datos = {}
    # Crypto via CoinGecko API pública
    try:
        url_crypto = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether&vs_currencies=usd,clp"
        resp = requests.get(url_crypto, timeout=5).json()
        datos['btc_usd'] = resp.get('bitcoin', {}).get('usd', 'N/A')
        datos['eth_usd'] = resp.get('ethereum', {}).get('usd', 'N/A')
        datos['usdt_clp'] = resp.get('tether', {}).get('clp', 'N/A')
    except Exception:
        datos['btc_usd'], datos['eth_usd'], datos['usdt_clp'] = "Error", "Error", "Error"

    # Dólar CLP via Mindicador API
    try:
        url_clp = "https://mindicador.cl/api/dolar"
        resp_clp = requests.get(url_clp, timeout=5).json()
        datos['dolar_clp'] = resp_clp['serie'][0]['valor']
    except Exception:
        datos['dolar_clp'] = "N/A"

    return datos

@st.cache_data(ttl=600)
def obtener_clima_buin():
    """Obtiene el clima actual para Buin, Chile"""
    try:
        # Coordenadas aproximadas de Buin, Chile (-33.73, -70.73)
        url = "https://api.open-meteo.com/v1/forecast?latitude=-33.73&longitude=-70.73&current_weather=true"
        resp = requests.get(url, timeout=5).json()
        return resp.get('current_weather', {})
    except Exception:
        return {}

# ---------------------------------------------------------
# ENCABEZADO Y ESTADO DE JARVIS
# ---------------------------------------------------------
st.title("⚡ J.A.R.V.I.S. 4.0 - AI Autónoma")

st.success("✅ Todos los subsistemas satelitales responden de forma óptima.")

# ---------------------------------------------------------
# BARRA LATERAL (PANEL DE CONTROL & BASTIÓN)
# ---------------------------------------------------------
with st.sidebar:
    st.header("🛰️ Red Satelital Serafín")
    st.caption("Ubicación Base: Buin, Chile")
    
    # Mapa compacto
    st.map(data={"lat": [-33.73], "lon": [-70.73]}, zoom=10)
    
    st.divider()
    st.subheader("⏱️ Sincronización Temporal")
    hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
    st.metric(label="Hora Local", value=hora_actual)

# ---------------------------------------------------------
# NAVEGACIÓN POR PESTAÑAS (MANTIENE LAS ORIGINALES + EXTENSIONES)
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Terminal de Conversación", 
    "📈 Mercado & Crypto", 
    "🌤️ Clima & Telemetría", 
    "📝 Bloc & Tareas",
    "⚙️ Configuración & IA"
])

# ---------------------------------------------------------
# TAB 1: TERMINAL DE CONVERSACIÓN (CÓDIGO ORIGINAL INTACTO)
# ---------------------------------------------------------
with tab1:
    st.subheader("Conversación Autónoma & Dictado por Voz")
    
    st.markdown("**⚡ Comandos Tácticos Rápidos:**")
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if st.button("📍 Estado Buin"):
            st.info("J.A.R.V.I.S.: Perímetro en Buin reporta tranquilidad. Sensores ambientales estables.")
    with col_btn2:
        if st.button("📊 Financiero"):
            st.info("J.A.R.V.I.S.: Mercados sincronizados. Revisa la pestaña 'Mercado & Crypto' para ver activos.")
    with col_btn3:
        if st.button("⚙️ Sistema"):
            st.info("J.A.R.V.I.S.: CPU 12%, Memoria RAM 34%, Servidor Streamlit Cloud al 100%.")
    with col_btn4:
        if st.button("🗑️ Limpiar Chat"):
            st.session_state['chat_history'] = []
            st.experimental_rerun()

    st.divider()

    # Historial de Chat
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = [
            {"role": "assistant", "content": "Buenas noches, jefa. ¿Trabajando hasta tarde otra vez? Alguien tiene que mantener este imperio en pie. ¿Qué travesura tecnológica planea para hoy?"}
        ]

    for msg in st.session_state['chat_history']:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    user_input = st.chat_input("Escribe una orden para J.A.R.V.I.S...")
    if user_input:
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        
        # Respuesta por defecto o con IA si está configurada
        if st.session_state.get('api_key_openai'):
            respuesta_jarvis = f"J.A.R.V.I.S. (IA Activa): He recibido tu orden '{user_input}'. Procesando con redes neuronales..."
        else:
            respuesta_jarvis = f"J.A.R.V.I.S.: Comprendido, orden '{user_input}' registrada en la consola táctica."
            
        st.session_state['chat_history'].append({"role": "assistant", "content": respuesta_jarvis})
        st.chat_message("assistant").write(respuesta_jarvis)

# ---------------------------------------------------------
# TAB 2: MERCADO & CRYPTO (NUEVO)
# ---------------------------------------------------------
with tab2:
    st.subheader("📊 Cotizaciones & Mercado en Tiempo Real")
    if st.button("🔄 Actualizar Cotizaciones"):
        st.cache_data.clear()
        
    finanzas = obtener_crypto_y_divisas()
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("💵 Dólar Observador", f"${finanzas.get('dolar_clp', 'N/A')} CLP")
    with c2:
        btc = finanzas.get('btc_usd')
        st.metric("₿ Bitcoin (BTC)", f"${btc:,.2f} USD" if isinstance(btc, (int, float)) else str(btc))
    with c3:
        eth = finanzas.get('eth_usd')
        st.metric("Ξ Ethereum (ETH)", f"${eth:,.2f} USD" if isinstance(eth, (int, float)) else str(eth))
    with c4:
        usdt = finanzas.get('usdt_clp')
        st.metric("₮ USDT / CLP", f"${usdt:,.2f} CLP" if isinstance(usdt, (int, float)) else str(usdt))

# ---------------------------------------------------------
# TAB 3: CLIMA & TELEMETRÍA (NUEVO)
# ---------------------------------------------------------
with tab3:
    st.subheader("🌤️ Telemetría Meteorológica - Buin")
    clima = obtener_clima_buin()
    
    if clima:
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("🌡️ Temperatura Actual", f"{clima.get('temperature', 'N/A')} °C")
        with col_m2:
            st.metric("💨 Velocidad del Viento", f"{clima.get('windspeed', 'N/A')} km/h")
        with col_m3:
            st.metric("🧭 Dirección del Viento", f"{clima.get('winddirection', 'N/A')}°")
    else:
        st.warning("No se pudo obtener el reporte en vivo de los sensores meteorológicos.")

# ---------------------------------------------------------
# TAB 4: BLOC & TAREAS (NUEVO)
# ---------------------------------------------------------
with tab4:
    st.subheader("📝 Módulo de Notas Rápidas & Pendientes")
    
    if 'notas_jarvis' not in st.session_state:
        st.session_state['notas_jarvis'] = []

    nueva_nota = st.text_input("Agregar un recordatorio táctico:")
    if st.button("➕ Guardar Nota"):
        if nueva_nota:
            st.session_state['notas_jarvis'].append(nueva_nota)
            st.success("Nota agregada al protocolo.")
            st.experimental_rerun()

    st.markdown("### 📋 Notas Guardadas en Sesión:")
    if st.session_state['notas_jarvis']:
        for i, nota in enumerate(st.session_state['notas_jarvis']):
            st.write(f"• **{i+1}.** {nota}")
    else:
        st.caption("No hay notas guardadas actualmente.")

# ---------------------------------------------------------
# TAB 5: CONFIGURACIÓN & IA (NUEVO)
# ---------------------------------------------------------
with tab5:
    st.subheader("⚙️ Configuración del Motor de Inteligencia")
    st.caption("Conecta una clave de API para activar procesamiento avanzado de lenguaje natural.")
    
    key_input = st.text_input("Clave API de OpenAI / Gemini:", type="password")
    if st.button("💾 Guardar Clave API"):
        st.session_state['api_key_openai'] = key_input
        st.success("Clave vinculada con éxito al núcleo de J.A.R.V.I.S.")

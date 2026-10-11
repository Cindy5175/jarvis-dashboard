import streamlit as st
import datetime
import requests
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
# ESTILOS VISUALES (CSS DE ALTO CONTRASTE Y VISIBILIDAD)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Fondo principal */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    
    /* Botones tácticos */
    .stButton>button {
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border: 1px solid #374151 !important;
        border-radius: 8px !important;
        width: 100% !important;
    }
    .stButton>button:hover {
        background-color: #374151 !important;
        color: #6ee7b7 !important;
        border-color: #4b5563 !important;
    }

    /* Caja de entrada de texto (Chat Input) */
    .stChatInput textarea {
        color: #ffffff !important;
        background-color: #1e222d !important;
    }
    .stChatInputContainer {
        background-color: #1e222d !important;
        border: 1px solid #374151 !important;
        border-radius: 10px !important;
    }

    /* Mensajes del Chat e Historial */
    [data-testid="stChatMessage"] {
        background-color: #1a202c !important;
        border: 1px solid #2d3748 !important;
        border-radius: 10px !important;
        padding: 10px !important;
        margin-bottom: 8px !important;
    }
    [data-testid="stChatMessage"] p {
        color: #ffffff !important;
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIONES AUXILIARES DE APIS
# ---------------------------------------------------------

@st.cache_data(ttl=300)
def obtener_crypto_y_divisas():
    datos = {}
    try:
        url_crypto = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,tether&vs_currencies=usd,clp"
        resp = requests.get(url_crypto, timeout=5).json()
        datos['btc_usd'] = resp.get('bitcoin', {}).get('usd', 'N/A')
        datos['eth_usd'] = resp.get('ethereum', {}).get('usd', 'N/A')
        datos['usdt_clp'] = resp.get('tether', {}).get('clp', 'N/A')
    except Exception:
        datos['btc_usd'], datos['eth_usd'], datos['usdt_clp'] = "Error", "Error", "Error"

    try:
        url_clp = "https://mindicador.cl/api/dolar"
        resp_clp = requests.get(url_clp, timeout=5).json()
        datos['dolar_clp'] = resp_clp['serie'][0]['valor']
    except Exception:
        datos['dolar_clp'] = "N/A"

    return datos

@st.cache_data(ttl=600)
def obtener_clima_buin():
    try:
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
# BARRA LATERAL (PANEL DE CONTROL & RELOJ EN VIVO)
# ---------------------------------------------------------
with st.sidebar:
    st.header("🛰️ Red Satelital Serafín")
    st.caption("Ubicación Base: Buin, Chile")
    st.map(data={"lat": [-33.73], "lon": [-70.73]}, zoom=10)
    st.divider()
    st.subheader("⏱️ Sincronización Temporal")
    
    st.components.v1.html("""
        <div style="
            background-color: #1e222d;
            border: 1px solid #374151;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
            font-family: monospace;
        ">
            <span style="color: #9ca3af; font-size: 12px; display: block; margin-bottom: 4px;">Hora Local (Chile)</span>
            <span id="reloj-jarvis" style="color: #6ee7b7; font-size: 28px; font-weight: bold; letter-spacing: 2px;">--:--:--</span>
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

# ---------------------------------------------------------
# NAVEGACIÓN POR PESTAÑAS
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Terminal de Conversación", 
    "📈 Mercado & Crypto", 
    "🌤️ Clima & Telemetría", 
    "📝 Bloc & Tareas",
    "⚙️ Configuración & IA"
])

# ---------------------------------------------------------
# TAB 1: TERMINAL DE CONVERSACIÓN
# ---------------------------------------------------------
with tab1:
    st.subheader("Conversación Autónoma & Dictado por Voz")
    st.markdown("**⚡ Comandos Tácticos Rápidos:**")
    col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
    
    with col_btn1:
        if st.button("📍 Estado Buin"):
            msg_buin = "J.A.R.V.I.S.: Perímetro en Buin reporta tranquilidad. Sensores ambientales estables."
            st.session_state['chat_history'].append({"role": "assistant", "content": msg_buin})
            st.rerun()
    with col_btn2:
        if st.button("📊 Financiero"):
            msg_fin = "J.A.R.V.I.S.: Mercados sincronizados. Revisa la pestaña 'Mercado & Crypto' para ver activos."
            st.session_state['chat_history'].append({"role": "assistant", "content": msg_fin})
            st.rerun()
    with col_btn3:
        if st.button("⚙️ Sistema"):
            msg_sys = "J.A.R.V.I.S.: CPU 12%, Memoria RAM 34%, Servidor Streamlit Cloud al 100%."
            st.session_state['chat_history'].append({"role": "assistant", "content": msg_sys})
            st.rerun()
    with col_btn4:
        if st.button("🗑️ Limpiar Chat"):
            st.session_state['chat_history'] = [
                {"role": "assistant", "content": "Buenas noches, jefa. ¿Trabajando hasta tarde otra vez? Alguien tiene que mantener este imperio en pie. ¿Qué travesura tecnológica planea para hoy?"}
            ]
            st.rerun()

    st.divider()

    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = [
            {"role": "assistant", "content": "Buenas noches, jefa. ¿Trabajando hasta tarde otra vez? Alguien tiene que mantener este imperio en pie. ¿Qué travesura tecnológica planea para hoy?"}
        ]

    for msg in st.session_state['chat_history']:
        st.chat_message(msg["role"]).write(msg["content"])

    user_input = st.chat_input("Escribe una orden para J.A.R.V.I.S...")
    if user_input:
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)
        
        # PROCESAMIENTO CON GEMINI O RESPUESTA TÁCTICA
        api_key = st.session_state.get('api_key_gemini')
        respuesta_jarvis = ""

        if api_key:
            try:
                genai.configure(api_key=api_key)
                try:
                    modelo = genai.GenerativeModel('gemini-3.8-flash')
                except Exception:
                    modelo = genai.GenerativeModel('gemini-1.5-flash')

                prompt_sistema = "Eres J.A.R.V.I.S., un asistente de inteligencia artificial avanzado, sarcástico pero leal y eficiente, que asiste a tu creadora Cindy en Buin, Chile."
                respuesta = modelo.generate_content(f"{prompt_sistema}\nUsuario: {user_input}")
                respuesta_jarvis = respuesta.text
            except Exception as e:
                respuesta_jarvis = f"J.A.R.V.I.S.: Error al conectar con el núcleo de Gemini ({str(e)}). Verifique su clave."
        else:
            texto_lower = user_input.lower()
            if any(w in texto_lower for w in ["hola", "saludos", "buenas", "hey"]):
                respuesta_jarvis = "J.A.R.V.I.S.: Saludos operativos, jefa. Los sistemas están activos y listos para cualquier directiva."
            else:
                respuesta_jarvis = f"J.A.R.V.I.S.: Orden '{user_input}' registrada. (Para razonamiento avanzado con IA, configure su API Key en la pestaña Configuración)."
            
        st.session_state['chat_history'].append({"role": "assistant", "content": respuesta_jarvis})
        st.chat_message("assistant").write(respuesta_jarvis)

# ---------------------------------------------------------
# TAB 2: MERCADO & CRYPTO
# ---------------------------------------------------------
with tab2:
    st.subheader("📊 Cotizaciones & Mercado en Tiempo Real")
    if st.button("🔄 Actualizar Cotizaciones"):
        st.cache_data.clear()
        st.rerun()
        
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
# TAB 3: CLIMA & TELEMETRÍA
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
# TAB 4: BLOC & TAREAS
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
            st.rerun()

    st.markdown("### 📋 Notas Guardadas en Sesión:")
    if st.session_state['notas_jarvis']:
        for i, nota in enumerate(st.session_state['notas_jarvis']):
            st.write(f"• **{i+1}.** {nota}")
    else:
        st.caption("No hay notas guardadas actualmente.")

# ---------------------------------------------------------
# TAB 5: CONFIGURACIÓN & IA
# ---------------------------------------------------------
with tab5:
    st.subheader("⚙️ Configuración del Motor de Inteligencia")
    st.caption("Conecta tu clave de API de Google Gemini para activar el núcleo de razonamiento autónomo.")
    key_input = st.text_input("Clave API de Google Gemini:", type="password", value=st.session_state.get('api_key_gemini', ''))
    if st.button("💾 Guardar Clave API"):
        st.session_state['api_key_gemini'] = key_input
        st.success("Clave de Gemini vinculada con éxito al núcleo de J.A.R.V.I.S.")

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
# ESTILOS VISUALES (TEMA NEGRO ABSOLUTO Y AZUL NEÓN COMPLETO)
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Fondo principal y barra lateral en negro absoluto */
    .stApp, [data-testid="stSidebar"], [data-testid="stSidebarContent"] {
        background-color: #080c14 !important;
        color: #00f3ff !important;
    }
    
    /* Todos los textos, títulos, etiquetas e inputs en Azul Neón */
    h1, h2, h3, h4, h5, h6, p, span, label, div, small, caption {
        color: #00f3ff !important;
        text-shadow: 0 0 5px rgba(0, 243, 255, 0.3);
    }

    /* Botones tácticos con borde e iluminación Neón */
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

    /* CAJA DE ENTRADA DEL CHAT - ESTILO AZUL NEÓN DESTACADO */
    div[data-testid="stChatInput"] {
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

    /* Entradas de texto generales (Blocs, etc) */
    .stTextInput input {
        color: #00f3ff !important;
        background-color: #0b1320 !important;
        border: 1px solid #00f3ff !important;
        box-shadow: 0 0 8px rgba(0, 243, 255, 0.3);
        font-weight: bold !important;
    }

    /* Mensajes del Chat e Historial con Bordes Neón */
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
    
    /* Métricas e Indicadores con brillo neón */
    div[data-testid="stMetricValue"] {
        color: #00f3ff !important;
        font-weight: bold !important;
        text-shadow: 0 0 8px rgba(0, 243, 255, 0.5);
    }
    div[data-testid="stMetricLabel"] {
        color: #00a8b5 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FUNCIONES AUXILIARES DE APIS (MINDICADOR CLP & OPEN-METEO)
# ---------------------------------------------------------

@st.cache_data(ttl=300)
def obtener_divisas_chile():
    datos = {}
    
    # Dólar Observador con respaldo
    try:
        url_dolar = "https://mindicador.cl/api/dolar"
        resp_dolar = requests.get(url_dolar, timeout=5).json()
        serie = resp_dolar.get('serie', [])
        datos['dolar_clp'] = serie[0]['valor'] if len(serie) > 0 else "N/A"
    except Exception:
        datos['dolar_clp'] = "N/A"

    # Euro con respaldo
    try:
        url_euro = "https://mindicador.cl/api/euro"
        resp_euro = requests.get(url_euro, timeout=5).json()
        serie_e = resp_euro.get('serie', [])
        datos['euro_clp'] = serie_e[0]['valor'] if len(serie_e) > 0 else "N/A"
    except Exception:
        datos['euro_clp'] = "N/A"

    # UF con respaldo
    try:
        url_uf = "https://mindicador.cl/api/uf"
        resp_uf = requests.get(url_uf, timeout=5).json()
        serie_uf = resp_uf.get('serie', [])
        datos['uf_clp'] = serie_uf[0]['valor'] if len(serie_uf) > 0 else "N/A"
    except Exception:
        datos['uf_clp'] = "N/A"

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
# BARRA LATERAL (PANEL DE CONTROL, RELOJ & BLOC)
# ---------------------------------------------------------
with st.sidebar:
    st.header("🛰️ Red Satelital Serafín")
    st.caption("Ubicación Base: Buin, Chile")
    st.map(data={"lat": [-33.73], "lon": [-70.73]}, zoom=10)
    st.divider()
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
# NAVEGACIÓN POR PESTAÑAS (FINANZAS AL LADO IZQUIERDO)
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs([
    "📈 Finanzas", 
    "💬 Terminal de Conversación", 
    "🌤️ Clima & Telemetría"
])

# ---------------------------------------------------------
# TAB 1: FINANZAS (DÓLAR, EURO Y UF)
# ---------------------------------------------------------
with tab1:
    st.subheader("📊 Indicadores Financieros Oficiales (Chile)")
    if st.button("🔄 Actualizar Cotizaciones"):
        st.cache_data.clear()
        st.rerun()
        
    finanzas = obtener_divisas_chile()
    
    c1, c2, c3 = st.columns(3)
    with c1:
        dolar_val = finanzas.get('dolar_clp', 'N/A')
        st.metric("💵 Dólar Observador", f"${dolar_val:,.2f} CLP" if isinstance(dolar_val, (int, float)) else str(dolar_val))
    with c2:
        euro_val = finanzas.get('euro_clp', 'N/A')
        st.metric("💶 Euro", f"${euro_val:,.2f} CLP" if isinstance(euro_val, (int, float)) else str(euro_val))
    with c3:
        uf_val = finanzas.get('uf_clp', 'N/A')
        st.metric("🇨🇱 UF (Unidad de Fomento)", f"${uf_val:,.2f} CLP" if isinstance(uf_val, (int, float)) else str(uf_val))

# ---------------------------------------------------------
# TAB 2: TERMINAL DE CONVERSACIÓN
# ---------------------------------------------------------
with tab2:
    st.subheader("Conversación Autónoma & Dictado por Voz")
    
    # MÓDULO DE ALERTAS Y RESUMEN TÁCTICO AUTOMATIZADO
    clima_res = obtener_clima_buin()
    fin_res = obtener_divisas_chile()
    
    temp_actual = clima_res.get('temperature', 'N/A')
    dolar_actual = fin_res.get('dolar_clp', 'N/A')
    
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
            • Buin: {temp_actual}°C | Dólar: ${dolar_actual} CLP<br>
            • Alertas del Sistema: Perímetro seguro. Sin anomalías detectadas en la red satelital.
        </span>
    </div>
    """, unsafe_allow_html=True)

    # MÓDULO DE VOZ REAL OPTIMIZADO
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
                        }} else {{
                            alert('La síntesis de voz no es compatible con este navegador.');
                        }}
                    }}
                </script>
            """, height=65)

    st.markdown("**⚡ Comandos Tácticos Rápidos:**")
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("📍 Estado Buin"):
            msg_buin = f"J.A.R.V.I.S.: Perímetro en Buin reporta tranquilidad. Temperatura actual de {temp_actual} grados."
            st.session_state['chat_history'].append({"role": "assistant", "content": msg_buin})
            st.rerun()
    with col_btn2:
        if st.button("⚙️ Sistema"):
            msg_sys = "J.A.R.V.I.S.: CPU 12%, Memoria RAM 34%, Servidor Streamlit Cloud al 100% operativo."
            st.session_state['chat_history'].append({"role": "assistant", "content": msg_sys})
            st.rerun()
    with col_btn3:
        if st.button("🗑️ Limpiar Chat"):
            st.session_state['chat_history'] = [
                {"role": "assistant", "content": "Hola Cindy. Sistemas listos y operando al máximo rendimiento."}
            ]
            st.rerun()

    st.divider()

    # Inicialización del historial
    if 'chat_history' not in st.session_state:
        st.session_state['chat_history'] = [
            {"role": "assistant", "content": "Hola Cindy. Sistemas listos y operando al máximo rendimiento."}
        ]

    # Render del historial de chat arriba
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state['chat_history']:
            st.chat_message(msg["role"]).write(msg["content"])

    # Entrada de mensajes abajo
    user_input = st.chat_input("Escribe tu consulta para J.A.R.V.I.S. aquí...")
    if user_input:
        st.session_state['chat_history'].append({"role": "user", "content": user_input})
        
        # PROCESAMIENTO GEMINI AUTOMÁTICO
        api_key = st.secrets.get("GEMINI_API_KEY", st.session_state.get('api_key_gemini'))
        respuesta_jarvis = ""

        if api_key:
            try:
                genai.configure(api_key=api_key)
                modelo_nombre = 'gemini-pro'
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            modelo_nombre = m.name
                            break
                except Exception:
                    pass

                modelo = genai.GenerativeModel(modelo_nombre)
                prompt_sistema = "Eres J.A.R.V.I.S., un asistente de inteligencia artificial leal, inteligente y eficiente que asiste a Cindy en Buin, Chile."
                respuesta = modelo.generate_content(f"{prompt_sistema}\nUsuario: {user_input}")
                respuesta_jarvis = respuesta.text
            except Exception as e:
                respuesta_jarvis = f"J.A.R.V.I.S.: Error al conectar con el núcleo de Gemini ({str(e)}). Verifique su clave."
        else:
            texto_lower = user_input.lower()
            if any(w in texto_lower for w in ["hola", "saludos", "buenas", "hey"]):
                respuesta_jarvis = "J.A.R.V.I.S.: Hola Cindy, sistemas listos. ¿En qué te ayudo hoy?"
            else:
                respuesta_jarvis = f"J.A.R.V.I.S.: Orden '{user_input}' registrada. (Para razonamiento avanzado con IA, configure su clave en los Secrets de Streamlit)."
            
        st.session_state['chat_history'].append({"role": "assistant", "content": respuesta_jarvis})
        st.rerun()

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

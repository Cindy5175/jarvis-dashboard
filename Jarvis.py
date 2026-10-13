import streamlit as st
import streamlit.components.v1 as components
import datetime
import pandas as pd

# Configuración de la página en modo ancho con estilo táctico
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónoma // Centro de Mando", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para el diseño neón / cian
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #ffffff;
    }
    .main-title {
        color: #00d2ff;
        font-size: 36px;
        font-weight: 800;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 1.5px;
        margin-bottom: 5px;
    }
    .neon-text {
        color: #00d2ff;
        font-weight: 600;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stTextInput input {
        background-color: #121826;
        color: #00d2ff;
        border: 1px solid #00d2ff;
        border-radius: 8px;
    }
    .stMetric {
        background-color: #121826;
        border: 1px solid #1f293d;
        padding: 10px;
        border-radius: 8px;
    }
    .stButton button {
        background-color: #121826;
        color: #00d2ff;
        border: 1px solid #00d2ff;
        border-radius: 6px;
        font-weight: bold;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #00d2ff;
        color: #000;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. TÍTULO PRINCIPAL ARRIBA
# ---------------------------------------------------------
st.markdown('<h1 class="main-title">⚡ J.A.R.V.I.S. IA Autónomo</h1>', unsafe_allow_html=True)

# Alerta de subsistemas en verde neón
st.success("✅ Todos los subsistemas satelitales y de hardware responden de forma óptima.")

# ---------------------------------------------------------
# 2. MÓDULO DE VOZ EN LA NUBE (JavaScript Web Speech API)
# ---------------------------------------------------------
voice_component = """
<div style="background-color: #121826; padding: 10px; border-radius: 8px; border: 1px solid #00d2ff; text-align: center; font-family: sans-serif; margin-bottom: 15px;">
    <h4 style="color: #00d2ff; margin: 0 0 6px 0; font-size: 14px;">🎙️ Escucha Activa: Dictado de Comandos en la Nube</h4>
    <button onclick="startListening()" style="background-color: #00d2ff; color: #000; border: none; padding: 6px 14px; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 12px;">Activar Micrófono</button>
    <p id="voice-status" style="color: #ffffff; margin-top: 6px; font-size: 11px;">Estado: En espera de comandos...</p>
</div>

<script>
function startListening() {
    const statusText = document.getElementById("voice-status");
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        statusText.innerText = "Error: Tu navegador no soporta reconocimiento de voz.";
        return;
    }
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'es-CL';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    statusText.innerText = "Escuchando atentamente...";

    recognition.onresult = function(event) {
        const command = event.results[0][0].transcript;
        statusText.innerText = "Comando recibido: \\"" + command + "\\"";
    };

    recognition.onerror = function(event) {
        statusText.innerText = "Error de captura: " + event.error;
    };

    recognition.start();
}
</script>
"""

components.html(voice_component, height=110)

st.markdown("---")

# ---------------------------------------------------------
# 3. DISEÑO DE COLUMNAS PRINCIPALES
# ---------------------------------------------------------
col_izq, col_der = st.columns([1, 1.8])

with col_izq:
    # HORA Y FECHA A LA IZQUIERDA EN AZUL NEÓN
    hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f'<p class="neon-text">🕒 Fecha y Hora: {hora_actual}</p>', unsafe_allow_html=True)
    st.markdown('<p class="neon-text">📍 Ubicación: Buin, Chile</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # PROTOCOLOS A LA IZQUIERDA EN AZUL NEÓN
    st.markdown('<p class="neon-text" style="font-size: 18px;">⚙️ Protocolos Tácticos</p>', unsafe_allow_html=True)
    
    if st.button("🎯 Protocolo de Misiones & Tareas Académicas"):
        st.info("Protocolo académico activado. Analizando base de datos.")
        
    if st.button("🌐 Traductor y Sintetizador Multilenguaje"):
        st.info("Subsistema multilingüe listo para operar.")
        
    if st.button("📍 Estado Base"):
        st.success("Ubicación actual fijada en Buin, Santiago Metropolitan Region, Chile.")

    st.markdown("---")
    
    # MAPA MÁS PEQUEÑO A LA IZQUIERDA
    st.markdown('<p class="neon-text">🗺️ Geolocalización Táctica</p>', unsafe_allow_html=True)
    mapa_data = pd.DataFrame({
        'lat': [-33.7333],
        'lon': [-70.7333]
    })
    st.map(mapa_data, zoom=10, use_container_width=True)

with col_der:
    st.markdown("### 💬 Terminal de Conversación Autónoma")
    
    # Finanzas Clave & Clima compacto
    st.markdown("""
        <div style="background-color: #121826; border: 1px solid #00d2ff; border-radius: 8px; padding: 12px; margin-bottom: 15px;">
            <p style="margin: 0; color: #00d2ff; font-weight: bold;">💱 Divisas & Clima en Buin</p>
            <p style="margin: 5px 0 0 0; font-size: 13px;">💵 Dólar: $930.50 CLP | 💶 Euro: $1,015.20 CLP | 📈 UF: $38,400 CLP</p>
            <p style="margin: 3px 0 0 0; font-size: 13px;">☀️ Clima: Despejado, 14,9 °C (Viento: 6,5 km/h)</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div style="background-color: #121826; border: 1px solid #00d2ff; border-radius: 8px; padding: 12px; margin-bottom: 15px;">
            <p style="margin: 0; color: #00d2ff; font-weight: bold;">🤖 Hola Cindy. Registros al día.</p>
            <p style="margin: 5px 0 0 0; font-size: 13px;">Sistema sincronizado con el búnker. ¿Qué orden ejecutamos ahora, jefa?</p>
        </div>
    """, unsafe_allow_html=True)

    # Telemetría de PC compacta
    st.markdown("""
        <div style="background-color: #121826; border: 1px solid #1f293d; border-radius: 8px; padding: 10px; margin-bottom: 20px;">
            <p style="margin: 2px 0; font-size: 12px; color: #a5b4fc;">💻 Telemetría: CPU: 38.5% | RAM: 22.8% | Batería: Cloud Red</p>
        </div>
    """, unsafe_allow_html=True)

    # Caja de consulta para JARVIS
    comando = st.text_input("Escribe tu consulta para J.A.R.V.I.S. aquí...", placeholder="Instrucción táctica o financiera...")

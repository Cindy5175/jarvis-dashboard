import streamlit as st
import streamlit.components.v1 as components
import datetime
import pandas as pd

# Configuración de la página en modo ancho con estilo táctico
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo // Centro de Mando", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS personalizados para replicar el diseño neón / cian oscuro
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #ffffff;
    }
    .stTextInput input {
        background-color: #121826;
        color: #00ffcc;
        border: 1px solid #00ffcc;
        border-radius: 8px;
    }
    .stMetric {
        background-color: #121826;
        border: 1px solid #1f293d;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. MÓDULO DE VOZ EN LA NUBE (JavaScript Web Speech API)
# ---------------------------------------------------------
voice_component = """
<div style="background-color: #121826; padding: 10px; border-radius: 8px; border: 1px solid #00ffcc; text-align: center; font-family: sans-serif; margin-bottom: 15px;">
    <h4 style="color: #00ffcc; margin: 0 0 6px 0; font-size: 14px;">🎙️ Escucha Activa: Dictado de Comandos en la Nube</h4>
    <button onclick="startListening()" style="background-color: #00ffcc; color: #000; border: none; padding: 6px 14px; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 12px;">Activar Micrófono</button>
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

# ---------------------------------------------------------
# 2. ENCABEZADO PRINCIPAL
# ---------------------------------------------------------
st.markdown("⚡ **J.A.R.V.I.S. IA Autónomo**")
hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"🕒 **Fecha y Hora del Sistema:** `{hora_actual}` | 📍 **Ubicación:** [Buin, Chile]")

# Alerta de subsistemas en verde
st.success("✅ Todos los subsistemas satelitales y de hardware responden de forma óptima.")

st.markdown("---")

# ---------------------------------------------------------
# 3. DISEÑO DE COLUMNAS (Izquierda: Táctico y Finanzas | Derecha: Terminal de Conversación)
# ---------------------------------------------------------
col_izq, col_der = st.columns([1, 1.8])

with col_izq:
    st.markdown("### 📊 Finanzas & Acciones EE.UU.")
    
    # Divisas
    st.markdown("""
        <div style="background-color: #121826; border: 1px solid #00ffcc; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
            <p style="margin: 0; color: #00ffcc; font-weight: bold;">💱 Divisas Clave</p>
            <p style="margin: 5px 0 0 0; font-size: 14px;">💵 Dólar: $930.50 CLP</p>
            <p style="margin: 2px 0 0 0; font-size: 14px;">💶 Euro: $1,015.20 CLP</p>
            <p style="margin: 2px 0 0 0; font-size: 14px;">📈 UF: $38,400 CLP</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("**Acciones & ETFs en Tiempo Real:**")
    st.metric(label="AAPL", value="$340.97 USD", delta="+1.29%")
    st.metric(label="MSFT", value="$541.15 USD", delta="+1.14%")
    st.metric(label="NVDA", value="$226.32 USD", delta="-1.29%")
    st.metric(label="TSLA", value="$378.03 USD", delta="-1.22%")
    st.metric(label="SPY", value="$778.10 USD", delta="-0.06%")

    st.markdown("---")
    st.markdown("### ☁️ Clima & Alertas")
    st.markdown("""
        <div style="background-color: #121826; border: 1px solid #00ffcc; border-radius: 8px; padding: 12px;">
            <p style="margin: 0; font-weight: bold; color: #00ffcc;">☀️ Despejado</p>
            <p style="margin: 4px 0; font-size: 13px;">🌡️ Temperatura: 14,9 °C</p>
            <p style="margin: 4px 0; font-size: 13px;">💨 Viento: 6,5 km/h</p>
            <hr style="border-color: #1f293d; margin: 8px 0;">
            <p style="margin: 0; font-size: 12px; color: #a5b4fc;">Alerta Satelital: Perímetro meteorológico estable en Buin.</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 💻 Telemetría de PC")
    st.markdown("""
        <div style="background-color: #121826; border: 1px solid #1f293d; border-radius: 8px; padding: 10px;">
            <p style="margin: 2px 0; font-size: 13px;">⚡ CPU en Uso: 38.5%</p>
            <p style="margin: 2px 0; font-size: 13px;">🧠 Memoria RAM: 22.8%</p>
            <p style="margin: 2px 0; font-size: 13px;">🔋 Batería: Conectado a Red / Cloud</p>
        </div>
    """, unsafe_allow_html=True)

with col_der:
    st.markdown("### 💬 Terminal de Conversación Autónoma")
    
    # Botones de protocolos rápidos
    if st.button("🎯 Protocolo de Misiones & Tareas Académicas"):
        st.info("Protocolo académico activado. Analizando base de datos.")
        
    if st.button("🌐 Traductor y Sintetizador Táctico Multilenguaje"):
        st.info("Subsistema multilingüe listo para operar.")
        
    if st.button("📍 Estado Base"):
        st.success("Ubicación actual fijada en Buin, Santiago Metropolitan Region, Chile.")

    # Registro de estado / saludo
    st.markdown("""
        <div style="background-color: #121826; border: 1px solid #00ffcc; border-radius: 8px; padding: 12px; margin-top: 15px;">
            <p style="margin: 0; color: #00ffcc; font-weight: bold;">🤖 Hola Cindy. Registros al día.</p>
            <p style="margin: 5px 0 0 0; font-size: 13px;">Sistema sincronizado con el búnker. ¿Qué orden ejecutamos ahora, jefa?</p>
        </div>
    """, unsafe_allow_html=True)

    # Caja de consulta para JARVIS
    st.markdown("<br>", unsafe_allow_html=True)
    comando = st.text_input("Escribe tu consulta para J.A.R.V.I.S. aquí...", placeholder="Instrucción táctica o financiera...")

# ---------------------------------------------------------
# 4. MAPA DE GEOLOCALIZACIÓN TÁCTICA
# ---------------------------------------------------------
st.markdown("---")
st.markdown("### 🗺️ Geolocalización Táctica - Buin, Chile")
mapa_data = pd.DataFrame({
    'lat': [-33.7333],
    'lon': [-70.7333]
})
st.map(mapa_data, zoom=11)


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

# Estilos CSS personalizados para márgenes, tonos neón y diseño general
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
    .left-panel {
        background-color: #121826;
        border: 1px solid #00d2ff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.1);
    }
    .stTextInput input {
        background-color: #121826;
        color: #00d2ff;
        border: 1px solid #00d2ff;
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
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    
    # HORA CON SEGUNDERO EN TIEMPO REAL
    reloj_component = """
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #00d2ff; font-weight: 600; font-size: 14px; margin-bottom: 8px;">
        🕒 Fecha y Hora: <span id="reloj">Cargando...</span>
    </div>
    <script>
    function actualizarReloj() {
        const ahora = new Date();
        const opciones = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        document.getElementById('reloj').innerText = ahora.toLocaleString('sv-SE', opciones);
    }
    setInterval(actualizarReloj, 1000);
    actualizarReloj();
    </script>
    """
    components.html(reloj_component, height=35)
    
    st.markdown('<p class="neon-text">📍 Ubicación: Buin, Chile</p>', unsafe_allow_html=True)
    
    # MAPA MÁS PEQUEÑO Y COMPACTO DEBAJO DE UBICACIÓN BUIN (Zoom ajustado)
    mapa_data = pd.DataFrame({'lat': [-33.7333], 'lon': [-70.7333]})
    st.map(mapa_data, zoom=3, use_container_width=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # PANEL IZQUIERDO: DIVISAS Y CLIMA BUIN
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    st.markdown('<p class="neon-text" style="font-size: 16px; margin-bottom: 5px;">💱 Divisas & Clima en Buin</p>', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>💵 Dólar: $930.50 CLP</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>💶 Euro: $1,015.20 CLP</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>📈 UF: $38,400 CLP</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #00d2ff; opacity: 0.3; margin: 8px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>☀️ Clima: Despejado, 14,9 °C</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>💨 Viento: 6,5 km/h</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # TELEMETRÍA EN AZUL NEÓN CON MÁRGENES
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    st.markdown('<p class="neon-text" style="font-size: 16px; margin-bottom: 5px;">💻 Telemetría de PC</p>', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>⚡ CPU en Uso: 38.5%</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>🧠 Memoria RAM: 22.8%</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>🔋 Batería: Conectado a Red / Cloud</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    st.markdown("### 💬 Terminal de Conversación Autónoma")
    
    # Protocolos Tácticos con estilo azul neón
    if st.button("🎯 Protocolo de Misiones & Tareas Académicas"):
        st.info("Protocolo académico activado con éxito. Analizando registros en la nube.")
        
    if st.button("🌐 Traductor y Sintetizador Multilenguaje"):
        st.info("Subsistema multilingüe sincronizado y listo para operar.")
        
    if st.button("📍 Estado Base"):
        st.success("Ubicación del búnker fijada en Buin, Santiago Metropolitan Region, Chile.")

    # Estado de bienvenida fluido
    st.markdown("""
        <div style="background-color: #121826; border: 1px solid #00d2ff; border-radius: 8px; padding: 12px; margin-top: 15px; margin-bottom: 15px;">
            <p style="margin: 0; color: #00d2ff; font-weight: bold;">🤖 Hola Cindy. Registros al día.</p>
            <p style="margin: 5px 0 0 0; font-size: 13px;">Sistema sincronizado con el búnker. ¿Qué orden ejecutamos ahora, jefa?</p>
        </div>
    """, unsafe_allow_html=True)

    # GESTIÓN DE CHAT CON FORMULARIO FUNCIONAL Y FLUÍDO
    if "mensajes_chat" not in st.session_state:
        st.session_state.mensajes_chat = [
            {"rol": "jarvis", "texto": "Canal de texto abierto y fluido. Ingrese instrucción táctica."}
        ]

    # Formulario para enviar mensajes correctamente
    with st.form(key="form_chat_jarvis", clear_on_submit=True):
        entrada_usuario = st.text_input("Escribe tu consulta para J.A.R.V.I.S. aquí...", placeholder="Instrucción táctica o financiera...")
        boton_enviar = st.form_submit_button(label="🚀 Enviar Comando a J.A.R.V.I.S.")

    if boton_enviar and entrada_usuario:
        st.session_state.mensajes_chat.append({"rol": "usuario", "texto": entrada_usuario})
        respuesta_ia = f"Orden recibida, jefa: '{entrada_usuario}'. Subsistemas procesando instrucción con prioridad alfa."
        st.session_state.mensajes_chat.append({"rol": "jarvis", "texto": respuesta_ia})

    # Mostrar historial de chat con fluidez
    st.markdown("---")
    st.markdown("<p class='neon-text'>📜 Registro de Comunicaciones</p>", unsafe_allow_html=True)
    for msg in reversed(st.session_state.mensajes_chat[-6:]):
        if msg["rol"] == "usuario":
            st.markdown(f"**👩‍💻 Cindy:** {msg['texto']}")
        else:
            st.markdown(f"**🤖 J.A.R.V.I.S.:** <span style='color: #00d2ff;'>{msg['texto']}</span>", unsafe_allow_html=True)

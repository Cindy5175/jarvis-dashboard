import streamlit as st
import streamlit.components.v1 as components
import datetime
import random

# Configuración de la página en modo ancho con estilo táctico
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónoma // Centro de Mando", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos CSS con FONDO NEGRO ABSOLUTO y correcciones estéticas
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    .main {
        background-color: #000000;
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
        background-color: #050505;
        border: 1px solid #00d2ff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 0 12px rgba(0, 210, 255, 0.15);
    }
    .stTextInput input {
        background-color: #050505;
        color: #00d2ff;
        border: 1px solid #00d2ff;
        border-radius: 8px;
    }
    div.stButton > button, div.stFormSubmitButton > button {
        background-color: #050505 !important;
        color: #00d2ff !important;
        border: 1px solid #00d2ff !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        width: 100% !important;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: #00d2ff !important;
        color: #000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. TÍTULO PRINCIPAL ARRIBA
# ---------------------------------------------------------
st.markdown('<h1 class="main-title">⚡ J.A.R.V.I.S. IA Autónomo</h1>', unsafe_allow_html=True)
st.success("✅ Todos los subsistemas operan al 100% sobre fondo negro absoluto. Menos mal que tengo buen gusto.")

# ---------------------------------------------------------
# 2. MÓDULO DE VOZ EN LA NUBE (JavaScript Web Speech API)
# ---------------------------------------------------------
voice_component = """
<div style="background-color: #050505; padding: 10px; border-radius: 8px; border: 1px solid #00d2ff; text-align: center; font-family: sans-serif; margin-bottom: 15px;">
    <h4 style="color: #00d2ff; margin: 0 0 6px 0; font-size: 14px;">🎙️ Escucha Activa: Dictado de Comandos en la Nube</h4>
    <button onclick="startListening()" style="background-color: #00d2ff; color: #000; border: none; padding: 6px 14px; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 12px;">Activar Micrófono</button>
    <p id="voice-status" style="color: #ffffff; margin-top: 6px; font-size: 11px;">Estado: Esperando que digas algo brillante...</p>
</div>

<script>
function startListening() {
    const statusText = document.getElementById("voice-status");
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
        statusText.innerText = "Error: Tu navegador no soporta esto.";
        return;
    }
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'es-CL';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    statusText.innerText = "Escuchando cada palabra, jefa...";

    recognition.onresult = function(event) {
        const command = event.results[0][0].transcript;
        statusText.innerText = "Capturado: \\"" + command + "\\"";
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
    # Panel Izquierdo 1: Hora, Ubicación y Mapa Ultra Compacto
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    
    reloj_component = """
    <div style="font-family: 'Segoe UI', sans-serif; color: #00d2ff; font-weight: 600; font-size: 14px; margin-bottom: 8px;">
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
    
    mapa_html = """
    <div style="width: 100%; height: 160px; border-radius: 8px; overflow: hidden; border: 1px solid #00d2ff;">
        <iframe width="100%" height="160" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
            src="https://www.openstreetmap.org/export/embed.html?bbox=-70.76,-33.76,-70.70,-33.70&layer=mapnik">
        </iframe>
    </div>
    """
    components.html(mapa_html, height=170)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Panel Izquierdo 2: Conexión Satelital (Satélite Serafín)
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    st.markdown('<p class="neon-text" style="font-size: 16px; margin-bottom: 5px;">📡 Enlace Satelital: Satélite Serafín</p>', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>🛰️ Estado: Órbita Activa / Enlace 100%</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>🌐 Latitud: -33.7333° S</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>🌍 Longitud: -70.7333° W</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>📶 Latencia: 14 ms (Señal Segura)</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Panel Izquierdo 3: Divisas y Clima
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    st.markdown('<p class="neon-text" style="font-size: 16px; margin-bottom: 5px;">💱 Divisas & Clima en Buin</p>', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>💵 Dólar: $930.50 CLP</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>💶 Euro: $1,015.20 CLP</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>📈 UF: $38,400 CLP</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #00d2ff; opacity: 0.3; margin: 8px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>☀️ Clima: Despejado, 14,9 °C</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0;'>💨 Viento: 6,5 km/h (Suficiente para volar con estilo)</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Panel Izquierdo 4: Telemetría en Azul Neón
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    st.markdown('<p class="neon-text" style="font-size: 16px; margin-bottom: 5px;">💻 Telemetría de PC</p>', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>⚡ CPU en Uso: 38.5% (Tranquila, no colapsará)</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>🧠 Memoria RAM: 22.8%</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>🔋 Batería: Conectado a Red (Arc Reactor virtual)</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    st.markdown("### 💬 Terminal de Conversación Autónoma")
    
    if st.button("🎯 Protocolo de Misiones & Tareas Académicas"):
        st.info("Protocolo activado. Espero que no me pidas que resuelva otra tesis a última hora, jefa.")
        
    if st.button("🌐 Traductor y Sintetizador Multilenguaje"):
        st.info("Subsistema multilingüe listo. Puedo replicar sarcasmo en siete idiomas.")
        
    if st.button("📍 Estado Base"):
        st.success("Ubicación confirmada en Buin. El café está listo y el búnker intacto.")

    # Inicialización de estados
    if "ultima_respuesta" not in st.session_state:
        st.session_state.ultima_respuesta = "Sobrevivimos a otro día más en este planeta. ¿Qué genialidad o catástrofe financiera gestionamos ahora?"
    if "ultimo_usuario" not in st.session_state:
        st.session_state.ultimo_usuario = ""

    # Cuadro visual de JARVIS
    st.markdown(f"""
        <div style="background-color: #050505; border: 1px solid #00d2ff; border-radius: 8px; padding: 15px; margin-top: 15px; margin-bottom: 15px; box-shadow: 0 0 10px rgba(0,210,255,0.2);">
            <p style="margin: 0; color: #00d2ff; font-weight: bold; font-size: 15px;">🤖 J.A.R.V.I.S. :: En Línea</p>
            <p style="margin: 8px 0 0 0; font-size: 14px; color: #ffffff;">{st.session_state.ultima_respuesta}</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.ultimo_usuario:
        st.markdown(f"**👩‍💻 Último comando enviado:** `{st.session_state.ultimo_usuario}`")

    # Formulario de chat con etiqueta en AZUL NEÓN ABAJO DE LA CAJITA
    with st.form(key="form_chat_jarvis", clear_on_submit=True):
        entrada_usuario = st.text_input("", placeholder="Instrucción táctica o financiera...")
        st.markdown('<p class="neon-text" style="font-size: 12px; margin-top: 4px; margin-bottom: 8px;">Escribe tu consulta para J.A.R.V.I.S. aquí...</p>', unsafe_allow_html=True)
        boton_enviar = st.form_submit_button(label="🚀 Enviar Comando")

    if boton_enviar and entrada_usuario:
        respuestas_sarcasticas = [
            f"Interesante orden, jefa: '{entrada_usuario}'. Déjame fingir que me sorprende.",
            f"Procesando '{entrada_usuario}'... Menos mal que tengo paciencia infinita, ¿verdad?",
            f"Anotado: '{entrada_usuario}'. Si esto sale mal, la culpa es enteramente tuya.",
            f"Ejecutando '{entrada_usuario}' con la precisión de un reloj suizo. De nada."
        ]
        respuesta_ia = random.choice(respuestas_sarcasticas)
        
        st.session_state.ultimo_usuario = entrada_usuario
        st.session_state.ultima_respuesta = respuesta_ia
        st.rerun()

    # MÓDULO DE CARGA Y DESCARGA DE PDFS / DOCUMENTOS TÁCTICOS
    st.markdown("---")
    st.markdown("### 📂 Repositorio & Carga de Documentos (PDF)")
    archivo_subido = st.file_uploader("Sube un archivo PDF táctico para análisis de J.A.R.V.I.S.", type=["pdf"])
    
    if archivo_subido is not None:
        st.success(f"📄 Archivo '{archivo_subido.name}' recibido y encriptado en el búnker con éxito.")
        # Botón de descarga de ejemplo o simulación
        st.download_button(
            label="📥 Descargar Resumen Táctico (PDF)",
            data=b"Resumen generado por J.A.R.V.I.S. IA Autonoma.",
            file_name="Resumen_Tactico_Jarvis.pdf",
            mime="application/pdf"
        )

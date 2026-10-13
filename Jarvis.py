import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="J.A.R.V.I.S. // CENTRO DE MANDO", layout="wide")

st.title("JARVIS // CENTRO DE MANDO CENTRAL")

# ---------------------------------------------------------
# 1. COMPONENTE DE VOZ WEB (HTML5 + Web Speech API)
# ---------------------------------------------------------
voice_component = """
<div style="background-color: #121212; padding: 15px; border-radius: 10px; border: 1px solid #00ffcc; text-align: center; font-family: sans-serif;">
    <h4 style="color: #00ffcc; margin: 0 0 10px 0;">🎙️ Módulo de Voz en la Nube</h4>
    <button onclick="startListening()" style="background-color: #00ffcc; color: #000; border: none; padding: 10px 20px; font-weight: bold; border-radius: 5px; cursor: pointer; font-size: 14px;">Activar Micrófono</button>
    <p id="voice-status" style="color: #ffffff; margin-top: 10px; font-size: 13px;">Estado: En espera de comandos...</p>
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

# Renderizar el componente de voz dentro de la app
components.html(voice_component, height=140)

# ---------------------------------------------------------
# 2. TU CENTRO DE MANDO VISUAL (Diseño Original)
# ---------------------------------------------------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🔵 JARVIS IA")
    st.info("Sistema en línea, jefa. Sobrevivimos a otro día más sin que el búnker colapse.")
    
    # Caja de texto táctico (método tradicional)
    comando = st.text_input("Instrucciones para JARVIS...", placeholder="Escribe un comando táctico...")

with col2:
    st.subheader("🌐 CENTRO TÁCTICO")
    st.metric(label="Clima en Buin", value="14,9 °C", delta="V 6,5 km/h")

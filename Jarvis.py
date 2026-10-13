import streamlit as st
import streamlit.components.v1 as components
import datetime
import pandas as pd

# Configuración inicial de la página en modo ancho
st.set_page_config(page_title="J.A.R.V.I.S. // CENTRO DE MANDO", layout="wide")

# ---------------------------------------------------------
# 1. MÓDULO DE VOZ EN LA NUBE (JavaScript Web Speech API)
# ---------------------------------------------------------
voice_component = """
<div style="background-color: #121212; padding: 10px; border-radius: 8px; border: 1px solid #00ffcc; text-align: center; font-family: sans-serif; margin-bottom: 10px;">
    <h4 style="color: #00ffcc; margin: 0 0 6px 0; font-size: 14px;">🎙️ Módulo de Voz en la Nube</h4>
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
# 2. ENCABEZADO Y HORA ACTUALIZADA
# ---------------------------------------------------------
st.title("JARVIS // CENTRO DE MANDO CENTRAL")

hora_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"🕒 **Fecha y Hora del Sistema:** `{hora_actual}` | 📍 **Ubicación:** [Buin, Chile]")

# ---------------------------------------------------------
# 3. DISEÑO PRINCIPAL (Centro Táctico compacto IZQUIERDA, JARVIS IA DERECHA)
# ---------------------------------------------------------
col_izq, col_der = st.columns([1, 2])

with col_izq:
    st.subheader("🌐 CENTRO TÁCTICO")
    
    # Pestañas compactas a la izquierda
    pestana_control, pestana_biometria, pestana_finanzas = st.tabs(["Control y Clima", "Biometría", "Finanzas"])
    
    with pestana_control:
        st.metric(label="Clima en Buin", value="14,9 °C", delta="V 6,5 km/h")
        
    with pestana_biometria:
        st.metric(label="Estado Biométrico", value="Estable", delta="98% Óptimo")
        
    with pestana_finanzas:
        st.metric(label="Índice Financiero", value="USD/CLP", delta="+1.2%")

with col_der:
    st.subheader("🔵 JARVIS IA")
    st.info("Sistema en línea, jefa. Sobrevivimos a otro día más sin que el búnker colapse. ¿Qué milagro operativo ejecutamos ahora?")
    
    # Caja de comandos tácticos a la derecha
    comando = st.text_input("Instrucciones para JARVIS...", placeholder="Escribe un comando táctico...")

# ---------------------------------------------------------
# 4. MAPA DE GEOLOCALIZACIÓN (Buin, Chile)
# ---------------------------------------------------------
st.markdown("---")
st.subheader("🗺️ Geolocalización Táctica - Buin")

mapa_data = pd.DataFrame({
    'lat': [-33.7333],
    'lon': [-70.7333]
})
st.map(mapa_data, zoom=11)

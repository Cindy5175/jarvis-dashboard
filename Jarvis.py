import streamlit.components.v1 as components

# --- NÚCLEO DE ESCUCHA CONTINUA HANDS-FREE (JS WEBSPEECH API) ---
with st.sidebar:
    st.markdown("### 🎙️ ESCUCHA CONTINUA (HANDS-FREE)")
    st.markdown("El sistema de audio perimetral está activo en segundo plano, jefa.")
    
    # Componente HTML con JavaScript para reconocimiento de voz continuo
    reconocimiento_html = """
    <div style="background-color: #0b1d3a; padding: 12px; border-radius: 8px; border: 1px solid #00e5ff; font-family: monospace; text-align: center;">
        <p style="color: #00e5ff; margin: 0 0 8px 0; font-size: 0.85rem; font-weight: bold;">ESTADO: ESCUCHANDO...</p>
        <button onclick="iniciarEscucha()" style="background-color: #00e5ff; color: #050505; border: none; padding: 6px 12px; border-radius: 4px; font-weight: bold; cursor: pointer; font-size: 0.8rem;">ACTIVAR AUDIO PASIVO</button>
        <p id="transcripcion" style="color: #ffffff; margin: 8px 0 0 0; font-size: 0.8rem; font-style: italic;">(Haz clic en activar y habla con el sistema)</p>
    </div>

    <script>
    function iniciarEscucha() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            document.getElementById('transcripcion').innerText = "Tu navegador no soporta reconocimiento de voz directo.";
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = 'es-CL';
        recognition.continuous = true;
        recognition.interimResults = false;

        recognition.onstart = function() {
            document.getElementById('transcripcion').innerText = "🔴 Escuchando activamente en Nodo Buin...";
        };

        recognition.onresult = function(event) {
            const current = event.resultIndex;
            const transcript = event.results[current][0].transcript;
            document.getElementById('transcripcion').innerText = "Última orden: \"" + transcript + "\"";
            
            // Opcional: Aquí podemos enviar la orden de forma automática a Streamlit
            console.log("Comando capturado:", transcript);
        };

        recognition.onerror = function(event) {
            document.getElementById('transcripcion').innerText = "⚠️ Error de audio: reiniciando sensor...";
            setTimeout(() => { recognition.start(); }, 1000);
        };

        recognition.onend = function() {
            // Mantener la escucha activa reiniciándola automáticamente
            recognition.start();
        };

        recognition.start();
    }
    </script>
    """
    
    components.html(reconocimiento_html, height=140)

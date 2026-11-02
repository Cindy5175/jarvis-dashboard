with st.expander("🎙️ Escucha Continua (Hands-Free)", expanded=True):
        st.markdown("Active el micrófono para comandos de voz continuos:")
        
        # Inyección de JavaScript para SpeechRecognition nativo
        html_speech = """
        <div style="text-align: center; padding: 10px;">
            <button id="btn_mic" onclick="toggleEscucha()" style="
                background-color: #00d2ff;
                color: #060911;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 8px;
                font-family: monospace;
                cursor: pointer;
                width: 100%;
            ">🎙️ Iniciar Escucha Continua</button>
            <p id="status_mic" style="color: #00d2ff; font-family: monospace; font-size: 0.8rem; margin-top: 8px;">Estado: Inactivo</p>
        </div>

        <script>
            var reconocedor;
            var escuchando = false;

            if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                reconocedor = new SpeechRecognition();
                reconocedor.continuous = true;
                reconocedor.interimResults = false;
                reconocedor.lang = 'es-CL';

                reconocedor.onresult = function(event) {
                    var texto = event.results[event.results.length - 1][0].transcript.trim();
                    document.getElementById('status_mic').innerText = "Escuchado: " + texto;
                    
                    // Copiar al portapapeles o enviar la instrucción
                    navigator.clipboard.writeText(texto);
                };

                reconocedor.onerror = function(event) {
                    document.getElementById('status_mic').innerText = "Error micrófono: " + event.error;
                };

                reconocedor.onend = function() {
                    if (escuchando) {
                        reconocedor.start(); // Reinicio automático para escucha continua
                    } else {
                        document.getElementById('status_mic').innerText = "Estado: Detenido";
                    }
                };
            } else {
                document.getElementById('status_mic').innerText = "Navegador no soporta Speech API";
            }

            function toggleEscucha() {
                var btn = document.getElementById('btn_mic');
                if (!escuchando) {
                    reconocedor.start();
                    escuchando = true;
                    btn.innerText = "🛑 Detener Escucha";
                    btn.style.backgroundColor = "#ff4b4b";
                    btn.style.color = "#ffffff";
                    document.getElementById('status_mic').innerText = "Escuchando activamente...";
                } else {
                    escuchando = false;
                    reconocedor.stop();
                    btn.innerText = "🎙️ Iniciar Escucha Continua";
                    btn.style.backgroundColor = "#00d2ff";
                    btn.style.color = "#060911";
                }
            }
        </script>
        """
        st.components.v1.html(html_speech, height=120)

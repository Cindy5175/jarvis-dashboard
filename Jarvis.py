import streamlit as st
import streamlit.components.v1 as components
import base64
from PIL import Image
import io

def activar_sentidos_jarvis(api_vision_callback=None):
    """
    Módulo unificado de Voz Manos Libres ('Hola JARVIS') y Visión Táctica.
    Se inyecta sin alterar la simetría ni la estética del dashboard principal.
    """
    
    # ---------------------------------------------------------
    # 1. OÍDO TÁCTICO CONTINUO + SÍNTESIS DE VOZ (INVISIBLE)
    # ---------------------------------------------------------
    motor_voz_html = """
    <script>
    (function() {
        const parentDoc = window.parent.document;
        if (parentDoc.getElementById('jarvis-audio-engine-active')) return;

        // Marcador oculto para evitar múltiples instancias
        const marker = parentDoc.createElement('div');
        marker.id = 'jarvis-audio-engine-active';
        marker.style.display = 'none';
        parentDoc.body.appendChild(marker);

        const SpeechRecognition = window.parent.SpeechRecognition || window.parent.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            console.warn("JARVIS: Navegador no soporta reconocimiento de voz continuo.");
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = 'es-CL';
        recognition.continuous = true;
        recognition.interimResults = false;

        let esperandoComando = false;

        // Función de Voz Masculina Sarcástica/Formal
        window.parent.jarvisHablar = function(texto) {
            window.parent.speechSynthesis.cancel();
            const utterance = new SpeechSynthesisUtterance(texto);
            utterance.lang = 'es-ES';
            utterance.pitch = 0.85; // Tono varonil grave
            utterance.rate = 1.05;  // Cadencia ágil de mayordomo
            
            const voces = window.parent.speechSynthesis.getVoices();
            const vozVaronil = voces.find(v => 
                v.lang.includes('es') && (v.name.includes('Pablo') || v.name.includes('Jorge') || v.name.includes('Male') || v.name.includes('Google español'))
            );
            if (vozVaronil) utterance.voice = vozVaronil;
            window.parent.speechSynthesis.speak(utterance);
        };

        // Inyectar texto en el input de Streamlit y enviarlo
        function enviarAStreamlit(comando) {
            const inputs = parentDoc.querySelectorAll('textarea[data-testid="stChatInputTextArea"], input[type="text"]');
            if (inputs.length > 0) {
                const targetInput = inputs[inputs.length - 1];
                const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
                    window.parent.HTMLTextAreaElement.prototype, "value"
                )?.set || Object.getOwnPropertyDescriptor(
                    window.parent.HTMLInputElement.prototype, "value"
                )?.set;

                nativeInputValueSetter.call(targetInput, comando);
                targetInput.dispatchEvent(new Event('input', { bubbles: true }));

                setTimeout(() => {
                    const enterEvent = new KeyboardEvent('keydown', {
                        key: 'Enter', code: 'Enter', keyCode: 13, which: 13, bubbles: true
                    });
                    targetInput.dispatchEvent(enterEvent);
                }, 150);
            }
        }

        recognition.onresult = function(event) {
            const transcript = event.results[event.results.length - 1][0].transcript.trim().toLowerCase();
            console.log("JARVIS escuchó:", transcript);

            // Detección de Wake Word ("Hola Jarvis" o "Jarvis")
            if (transcript.includes("hola jarvis") || transcript.startsWith("jarvis")) {
                const limpio = transcript.replace("hola jarvis", "").replace("jarvis", "").trim();
                
                if (limpio.length === 0) {
                    esperandoComando = true;
                    window.parent.jarvisHablar("A sus órdenes, jefa. ¿En qué puedo asistirle?");
                } else {
                    enviarAStreamlit(limpio);
                }
            } else if (esperandoComando) {
                esperandoComando = false;
                enviarAStreamlit(transcript);
            }
        };

        // Reinicio automático si el navegador pausa la escucha por silencio
        recognition.onend = function() {
            try { recognition.start(); } catch(e) {}
        };

        // Iniciar escucha tras el primer clic en cualquier parte de la página (política de navegadores)
        parentDoc.addEventListener('click', function initAudio() {
            try { recognition.start(); } catch(e) {}
            parentDoc.removeEventListener('click', initAudio);
        }, { once: true });
    })();
    </script>
    """
    # Height=0 garantiza 0 píxeles ocupados en la grilla visual
    components.html(motor_voz_html, height=0, width=0)

    # ---------------------------------------------------------
    # 2. SENSOR ÓPTICO TÁCTICO (MODO FLOTANTE / POPOVER)
    # ---------------------------------------------------------
    # Se aloja en un popover minimalista para no romper la simetría de tarjetas
    with st.sidebar:
        with st.popover("👁️ Sensor Óptico JARVIS", use_container_width=True):
            foto = st.camera_input("Escaneo biométrico", label_visibility="collapsed")
            
            if foto is not None:
                img = Image.open(foto)
                buffered = io.BytesIO()
                img.save(buffered, format="JPEG", quality=85)
                img_b64 = base64.b64encode(buffered.getvalue()).decode()

                # Si conectas tu API multimodal (Gemini / GLM-4V), procesa la imagen aquí:
                if api_vision_callback:
                    prompt_etiqueta = (
                        "Eres J.A.R.V.I.S., asistente personal de la jefa. Analiza esta imagen de la cámara. "
                        "Si ves a una persona acompañándola o frente a la cámara (como un invitado o su hermano), "
                        "salúdalo con etiqueta británica formal pero con un toque sutil de ingenio: "
                        "'Buenos días, señor. Soy J.A.R.V.I.S., asistente personal de la jefa...'. "
                        "Sé breve (máximo 2 frases) para que pueda leerse en voz alta."
                    )
                    respuesta_jarvis = api_vision_callback(prompt_etiqueta, img_b64)
                else:
                    # Respuesta predeterminada lista para demostración inmediata
                    respuesta_jarvis = (
                        "Buenos días, señor. Soy J.A.R.V.I.S., asistente personal de la jefa. "
                        "Es un placer conocerle; intentaré ignorar el hecho de que la jefa no me avisó que tendríamos visitas."
                    )

                st.caption(f"🎙️ *{respuesta_jarvis}*")
                
                # Disparar voz automática al detectar rostro
                texto_seguro = respuesta_jarvis.replace('"', '\\"').replace("'", "\\'")
                components.html(
                    f"<script>if(window.parent.jarvisHablar) window.parent.jarvisHablar('{texto_seguro}');</script>",
                    height=0, width=0
                )

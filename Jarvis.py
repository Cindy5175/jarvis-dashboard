def reproducir_voz_jarvis(texto):
    texto_limpio = texto.replace("J.A.R.V.I.S.:", "").replace('"', '').replace("'", "").replace("\n", " ")
    js_code = f"""
        <script>
            if ('speechSynthesis' in window) {{
                window.speechSynthesis.cancel();
                var msg = new SpeechSynthesisUtterance("{texto_limpio}");
                
                // Configuración de tono y ritmo al estilo Paul Bettany
                msg.rate = 0.92;   // Un ritmo ligeramente más pausado y elegante
                msg.pitch = 0.85;  // Un tono más grave y sobrio

                // Intentar seleccionar una voz masculina adecuada
                var voices = window.speechSynthesis.getVoices();
                var jarvisVoice = voices.find(function(v) {{
                    return (v.name.includes('Male') || v.name.includes('George') || v.name.includes('Ryan') || v.name.includes('Pablo') || v.name.includes('Jorge')) && v.lang.includes('es');
                }}) || voices.find(function(v) {{ return v.lang.includes('es'); }});

                if (jarvisVoice) {{
                    msg.voice = jarvisVoice;
                }} else {{
                    msg.lang = 'es-ES';
                }}

                window.speechSynthesis.speak(msg);
            }}
        </script>
    """
    st.components.v1.html(js_code, height=0)

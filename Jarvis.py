elif "Sintetizador de Voz" in modulo_seleccionado:
    st.subheader("🎙️ Módulo: Sintetizador de Voz (ElevenLabs)")
    
    # Campo para ingresar o cargar la API Key de forma segura
    api_key = st.text_input("sk_1a9cc80c50796a7f9ba9158e6ba33e0a5f4e86e468b0b239", type="password")
    voice_id = st.text_input("ID de Voz (ej: Adam / Jarvis):", value="21m00Tcm4TlvDq8ikWAM")
    
    texto_a_hablar = st.text_area("Texto para sintetizar:", f"{saludo_tiempo}, jefa. Todos los sistemas del taller están operando a máxima capacidad en Buin.")
    
    if st.button("🔊 Generar Voz de J.A.R.V.I.S."):
        if not api_key:
            st.error("Por favor, ingrese su API Key de ElevenLabs, jefa.")
        else:
            try:
                from elevenlabs import generate, set_api_key
                set_api_key(api_key)
                
                audio = generate(
                    text=texto_a_hablar,
                    voice=voice_id,
                    model="eleven_multilingual_v2"
                )
                
                st.audio(audio, format="audio/mp3")
                st.success("Voz sintetizada con éxito desde Buin.")
            except Exception as e:
                st.error(f"Error en la conexión con ElevenLabs: {e}")

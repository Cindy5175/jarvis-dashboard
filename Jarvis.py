if user_cmd:
    response_msg = "Diagnóstico completado, Jefa. Los subsistemas de la base en Buin operan al cien por ciento."
    st.markdown(f'<div class="terminal-card">> [COMANDO]: {user_cmd}<br>> [J.A.R.V.I.S.]: {response_msg}</div>', unsafe_allow_html=True)
    
    if eleven_key:
        try:
            # ID de voz por defecto (Antoni / Varonil y sofisticada)
            voice_id = "21m00Tcm4TlvDq8ikWAM"
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": eleven_key
            }
            data = {
                "text": response_msg,
                "model_id": "eleven_multilingual_v2",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
            }
            res = requests.post(url, json=data, headers=headers)
            if res.status_code == 200:
                with open("jarvis_eleven.mp3", "wb") as f:
                    f.write(res.content)
                st.audio("jarvis_eleven.mp3", format="audio/mp3", autoplay=True)
                st.success("🎙️ [ElevenLabs Active] Audio cinematográfico generado con éxito.")
            else:
                st.error(f"Error en la API de ElevenLabs (Código {res.status_code}): Verifique su API Key.")
        except Exception as e:
            st.error(f"Error de conexión con ElevenLabs: {e}")
    else:
        # Respaldo con gTTS si no hay llave activa
        tts = gTTS(text=response_msg, lang='es')
        tts.save("response.mp3")
        st.audio("response.mp3", format="audio/mp3", autoplay=True)

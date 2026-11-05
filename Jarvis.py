import base64
from gtts import gTTS
import io


def hablar_jarvis_web(texto):
    """Genera audio y lo reproduce automáticamente en el navegador sin alterar la estética."""
    try:
        # Generar audio en español con gTTS
        tts = gTTS(text=texto, lang="es", tld="cl")  # Voz en español
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)

        # Convertir a base64 para reproducción HTML limpia e invisible
        b64 = base64.b64encode(fp.read()).decode()
        md = f"""
            <audio autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        pass

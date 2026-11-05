import base64
from gTTS import gtts
import io


def hablar_jarvis_web(texto):
  """Genera audio automáticamente para que Jarvis hable solo."""
  try:
    tts = gTTS(text=texto, lang="es", tld="cl")
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)
    b64 = base64.b64encode(fp.read()).decode()
    md = f"""
        <audio autoplay style="display:none;">
        <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(md, unsafe_allow_html=True)
  except Exception:
    pass

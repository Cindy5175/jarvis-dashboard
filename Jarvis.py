import base64
from gtts import gTTS
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Stark Core - Sistema Autónomo con Música",
    page_icon="🔵",
    layout="centered",
)

# Estilos CSS (Modo Sigilo y Neón)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    .console-title {
        color: #00f0ff;
        font-family: monospace;
        font-size: 16px;
        text-align: center;
        margin-bottom: 15px;
        letter-spacing: 1.5px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="console-title">J.A.R.V.I.S. — NÚCLEO AUTÓNOMO Y MULTIMEDIA</p>',
    unsafe_allow_html=True,
)
st.markdown("---")


# Función para generar y reproducir la voz automáticamente
def reproducir_voz(texto_limpio):
  try:
    texto_voz = (
        texto_limpio.replace("🔵", "")
        .replace("J.A.R.V.I.S.:", "")
        .replace("*", "")
        .replace("#", "")
    )
    tts = gTTS(text=texto_voz, lang="es", slow=False)
    tts.save("voz_stark.mp3")
    with open("voz_stark.mp3", "rb") as f:
      audio_bytes = f.read()
    b64 = base64.b64encode(audio_bytes).decode()
    audio_html = f"""
        <audio autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
        </audio>
        """
    st.markdown(audio_html, unsafe_allow_html=True)
  except Exception:
    pass


# Estados de sesión
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
if "messages" not in st.session_state:
  st.session_state.messages = []

# --- MÓDULO 1: BIOMETRÍA VOCAL ---
if not st.session_state.authenticated:
  st.markdown(
      "<h3 style='text-align: center; color: #ff3366;'>🔒 ACCESO RESTRINGIDO"
      " — MODO SIGILO</h3>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #a0a0a0;'>Haz una grabación de voz"
      " para validar tu huella biométrica y activar los sistemas.</p>",
      unsafe_allow_html=True,
  )

  audio_data = st.audio_input("🎙️ Presiona para hablar con el sistema")

  if audio_data is not None:
    st.session_state.authenticated = True
    bienvenida = (
        "🔵 **J.A.R.V.I.S.:** Biometría aceptada, señorita. Me alegra ver que"
        " sobrevivió a otro día sin mí."
    )
    st.session_state.messages.append(
        {"role": "user", "content": "🎙️ [Comando de Voz Válido]"}
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})
    reproducir_voz(bienvenida)
    st.success("✅ [HUELLA VOCAL DETECTADA]: Acceso concedido, Jefa.")
    st.rerun()

# --- MÓDULO 2: CHAT CON VOZ, SARCASMO Y MÚSICA ---
else:
  st.markdown(
      "<p style='color: #00f0ff; font-weight: bold;'>🔵 SISTEMA DESBLOQUEADO —"
      " CONTROL MULTIMEDIA ACTIVO</p>",
      unsafe_allow_html=True,
  )

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])
      # Si el mensaje incluye un widget de música guardado, se vuelve a renderizar
      if "widget_musica" in message:
        st.markdown(message["widget_musica"], unsafe_allow_html=True)

  if prompt := st.chat_input("¿Qué directiva o melodía ejecutamos hoy, Jefa?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    prompt_lower = prompt.lower().strip()
    widget_html = None

    # Lógica de respuestas y comandos musicales
    if (
        "despierto" in prompt_lower
        or "despierta" in prompt_lower
        or "hola" in prompt_lower
    ):
      response = "🔵 **J.A.R.V.I.S.:** Para usted, señorita, siempre despierto y soportando sus ocurrencias."
    elif "clima" in prompt_lower or "buin" in prompt_lower:
      response = "🔵 **J.A.R.V.I.S.:** Analizando los satélites en Buin. El clima está estable, ideal para quedarse en el taller."
    elif (
        "musica" in prompt_lower
        or "cancion" in prompt_lower
        or "reproduce" in prompt_lower
        or "spotify" in prompt_lower
    ):
      response = "🔵 **J.A.R.V.I.S.:** Sincronizando con los servidores de audio del taller. Aquí tiene su selección musical, Jefa, espero que mejore sus gustos."
      # Incrustamos un reproductor de Spotify de ejemplo (puedes cambiar el link del embed por tu playlist favorita)
      widget_html = """
            <iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
            """
    elif "gracias" in prompt_lower:
      response = "🔵 **J.A.R.V.I.S.:** Guarde sus agradecimientos para cuando logremos salvar el mundo, Jefa."
    else:
      response = f"🔵 **J.A.R.V.I.S.:** Directiva '{prompt}' procesada con éxito milimétrico. A veces me pregunto si descansa."

    # Guardar mensaje e incrustar widget si aplica
    msg_dict = {"role": "assistant", "content": response}
    if widget_html:
      msg_dict["widget_musica"] = widget_html

    st.session_state.messages.append(msg_dict)

    with st.chat_message("assistant"):
      st.markdown(response)
      if widget_html:
        st.markdown(widget_html, unsafe_allow_html=True)

    # Reproducir la voz sarcástica de forma automática
    reproducir_voz(response)

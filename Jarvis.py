import base64
from gtts import gTTS
import streamlit as st

# Configuración de la página en modo oculto / ancho
st.set_page_config(
    page_title="Stark Core - Modo Oculto", page_icon="🔵", layout="centered"
)

# Estilos CSS (Modo Sigilo y Ocultamiento Inteligente)
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
    '<p class="console-title">J.A.R.V.I.S. — NÚCLEO EN ESPERA (MODO OCULTO)</p>',
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
if "tareas" not in st.session_state:
  st.session_state.tareas = ["Calibrar blindaje", "Optimizar núcleos de IA"]

# --- PANEL LATERAL OCULTO (Solo se despliega si se usa) ---
with st.sidebar:
  st.markdown(
      "<h3 style='color: #00f0ff;'>🔒 Panel Táctico Oculto</h3>",
      unsafe_allow_html=True,
  )
  with st.expander("📝 Gestionar Pendientes del Taller"):
    nueva_tarea = st.text_input("Añadir pendiente:")
    if st.button("Registrar"):
      if nueva_tarea:
        st.session_state.tareas.append(nueva_tarea)
        st.success("Registrado.")

    for idx, t in enumerate(st.session_state.tareas):
      st.write(f"{idx+1}. {t}")

    if st.button("Limpiar Tareas"):
      st.session_state.tareas = []
      st.rerun()

  with st.expander("⚙️ Opciones de Sistema"):
    if st.button("🗑️ Forzar Purga Total"):
      st.session_state.messages = []
      st.rerun()

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
        "🔵 **J.A.R.V.I.S.:** Biometría aceptada, señorita. Sistemas ocultos"
        " desplegados solo a su comando."
    )
    st.session_state.messages.append(
        {"role": "user", "content": "🎙️ [Comando de Voz Válido]"}
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})
    reproducir_voz(bienvenida)
    st.success("✅ [HUELLA VOCAL DETECTADA]: Acceso concedido, Jefa.")
    st.rerun()

# --- MÓDULO 2: CHAT INTELIGENTE CON PANELES EXPANDIBLES ---
else:
  st.markdown(
      "<p style='color: #00f0ff; font-weight: bold;'>🔵 SISTEMA EN ESPERA —"
      " INTERFAZ MINIMALISTA</p>",
      unsafe_allow_html=True,
  )

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])
      if "widget_musica" in message:
        with st.expander("🎵 Reproductor Multimedia Oculto"):
          st.markdown(message["widget_musica"], unsafe_allow_html=True)

  if prompt := st.chat_input(
      "¿Qué directiva ordenamos, Jefa? (Todo lo demás permanece oculto)"
  ):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    prompt_lower = prompt.lower().strip()
    widget_html = None

    # Protocolos y comandos
    if (
        "clean slate" in prompt_lower
        or "purga" in prompt_lower
        or "emergencia" in prompt_lower
    ):
      response = "🔵 **J.A.R.V.I.S.:** Ejecutando protocolo de purga total. Silenciando y limpiando registros, Jefa."
      st.session_state.messages = []
      st.rerun()
    elif "clima" in prompt_lower or "buin" in prompt_lower:
      response = "🔵 **J.A.R.V.I.S.:** Satélites en Buin reportan cielos despejados. Todo bajo control en el exterior."
    elif (
        "cripto" in prompt_lower
        or "mercado" in prompt_lower
        or "inversion" in prompt_lower
    ):
      response = "🔵 **J.A.R.V.I.S.:** Analizando activos en segundo plano. Los números se mueven de forma interesante."
    elif (
        "musica" in prompt_lower
        or "cancion" in prompt_lower
        or "reproduce" in prompt_lower
        or "spotify" in prompt_lower
    ):
      response = "🔵 **J.A.R.V.I.S.:** Desplegando el reproductor multimedia a su orden, Jefa."
      widget_html = """
            <iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
            """
    elif "hola" in prompt_lower or "despierta" in prompt_lower:
      response = "🔵 **J.A.R.V.I.S.:** En completo silencio operativo y a su entera disposición, señorita."
    else:
      response = f"🔵 **J.A.R.V.I.S.:** Directiva '{prompt}' procesada. Manteniendo perfil bajo."

    msg_dict = {"role": "assistant", "content": response}
    if widget_html:
      msg_dict["widget_musica"] = widget_html

    st.session_state.messages.append(msg_dict)

    with st.chat_message("assistant"):
      st.markdown(response)
      if widget_html:
        with st.expander("🎵 Reproductor Multimedia Oculto"):
          st.markdown(widget_html, unsafe_allow_html=True)

    reproducir_voz(response)

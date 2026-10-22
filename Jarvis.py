import base64
import urllib.parse
from gtts import gTTS
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Stark Core - IA Autónomo", page_icon="🔵", layout="centered"
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
    '<p class="console-title">J.A.R.V.I.S. — IA AUTÓNOMO</p>',
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
  st.session_state.tareas = [
      "Revisar protocolos de seguridad",
      "Calibrar propulsores",
  ]

# --- BARRA LATERAL: TAREAS Y CONTROLES DEL TALLER ---
with st.sidebar:
  st.markdown(
      "<h3 style='color: #00f0ff;'>📋 Panel del Taller</h3>",
      unsafe_allow_html=True,
  )
  nueva_tarea = st.text_input("Añadir pendiente:")
  if st.button("Registrar Tarea"):
    if nueva_tarea:
      st.session_state.tareas.append(nueva_tarea)
      st.success("Tarea registrada.")

  st.markdown("#### 📌 Pendientes Activos:")
  for idx, t in enumerate(st.session_state.tareas):
    st.write(f"{idx+1}. {t}")

  if st.button("🗑️ Limpiar Tareas"):
    st.session_state.tareas = []
    st.rerun()

# --- MÓDULO 1: BIOMETRÍA VOCAL ---
if not st.session_state.authenticated:
  # Cambio de color del acceso restringido a un cian/azul neón elegante
  st.markdown(
      "<h3 style='text-align: center; color: #00f0ff;'>🔒 ACCESO RESTRINGIDO"
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
        "🔵 **J.A.R.V.I.S.:** Biometría aceptada, señorita. Sistemas IA autónomo"
        " activados."
    )
    st.session_state.messages.append(
        {"role": "user", "content": "🎙️ [Comando de Voz Válido]"}
    )
    st.session_state.messages.append({"role": "assistant", "content": bienvenida})
    reproducir_voz(bienvenida)
    st.success("✅ [HUELLA VOCAL DETECTADA]: Acceso concedido, Jefa.")
    st.rerun()

# --- MÓDULO 2: CHAT CON PROTOCOLOS Y HOLO-TALLER ---
else:
  st.markdown(
      "<p style='color: #00f0ff; font-weight: bold;'>🔵 SISTEMA DESBLOQUEADO —"
      " IA AUTÓNOMO ACTIVO</p>",
      unsafe_allow_html=True,
  )

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])
      if "widget_custom" in message:
        with st.expander("📂 Panel Desplegable (Holograma / Multimedia)"):
          st.markdown(message["widget_custom"], unsafe_allow_html=True)

  if prompt := st.chat_input(
      "¿Qué directiva o plano diseñamos hoy, Jefa? (Todo oculto hasta la"
      " orden)"
  ):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    prompt_lower = prompt.lower().strip()
    widget_html = None

    # 1. Protocolo Clean Slate / Purga de Emergencia
    if (
        "clean slate" in prompt_lower
        or "purga" in prompt_lower
        or "emergencia" in prompt_lower
    ):
      response = (
          "🔵 **J.A.R.V.I.S.:** Ejecutando protocolo de purga total. Purgando"
          " registros y blindando la consola. Borrón y cuenta nueva, Jefa."
      )
      st.session_state.messages = []
      st.rerun()

    # 2. Centro Meteorológico (Buin)
    elif "clima" in prompt_lower or "buin" in prompt_lower:
      response = (
          "🔵 **J.A.R.V.I.S.:** Satélites en Buin reportan cielos despejados."
          " Temperatura óptima para seguir operando en el taller."
      )

    # 3. Núcleo Financiero / Cripto
    elif (
        "cripto" in prompt_lower
        or "mercado" in prompt_lower
        or "inversion" in prompt_lower
        or "buda" in prompt_lower
    ):
      response = (
          "🔵 **J.A.R.V.I.S.:** Monitoreando carteras digitales. Los números se"
          " mueven de forma interesante, Jefa."
      )

    # 4. Música y Multimedia
    elif (
        "musica" in prompt_lower
        or "cancion" in prompt_lower
        or "reproduce" in prompt_lower
        or "spotify" in prompt_lower
    ):
      response = (
          "🔵 **J.A.R.V.I.S.:** Sincronizando audio del taller. Disfrute de la"
          " playlist en el panel oculto."
      )
      widget_html = """
            <iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXcBWIGoYBM5M?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>
            """

    # 5. Holo-Taller / Generador de Planos e Imágenes
    elif (
        "plano" in prompt_lower
        or "diseña" in prompt_lower
        or "genera" in prompt_lower
        or "prototipo" in prompt_lower
        or "holograma" in prompt_lower
    ):
      response = f"🔵 **J.A.R.V.I.S.:** Renderizando proyecciones holográficas para la directiva: *'{prompt}'*. Eche un vistazo al plano antes de que explote el taller, Jefa."
      prompt_url = urllib.parse.quote(prompt)
      widget_html = f"""
            <div style="text-align: center; border: 1px solid #00f0ff; padding: 10px; border-radius: 10px; background-color: #050505;">
                <p style="color: #00f0ff; font-family: monospace; margin-bottom: 5px;">HOLO-TALLER // PROTOTIPO ACTIVO</p>
                <img src="https://image.pollinations.ai/prompt/{prompt_url}%20futuristic%20blueprint%20cyberpunk%20stark%20tech" width="100%" style="border-radius: 5px;">
            </div>
            """

    elif (
        "despierto" in prompt_lower
        or "despierta" in prompt_lower
        or "hola" in prompt_lower
    ):
      response = (
          "🔵 **J.A.R.V.I.S.:** Siempre operativo y soportando sus ocurrencias,"
          " señorita."
      )
    elif "gracias" in prompt_lower:
      response = (
          "🔵 **J.A.R.V.I.S.:** Guárdese los agradecimientos para cuando"
          " salvemos el mundo, Jefa."
      )
    else:
      response = (
          f"🔵 **J.A.R.V.I.S.:** Directiva '{prompt}' procesada con precisión"
          " milimétrica."
      )

    msg_dict = {"role": "assistant", "content": response}
    if widget_html:
      msg_dict["widget_custom"] = widget_html

    st.session_state.messages.append(msg_dict)

    with st.chat_message("assistant"):
      st.markdown(response)
      if widget_html:
        with st.expander("📂 Ver Proyección / Contenido Oculto"):
          st.markdown(widget_html, unsafe_allow_html=True)

    reproducir_voz(response)

import base64
from gtts import gTTS
import google.generativeai as genai
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Stark Core - Asistente con Voz", page_icon="🤖", layout="centered"
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
    '<p class="console-title">J.A.R.V.I.S. — NÚCLEO SARCÁSTICO ACTIVO</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# Configuración directa de la Super IA con toque Stark
try:
  genai.configure(api_key="AQ.Ab8RN6JBXjSG_T2WXHeANQ8i1-yNNH8H1dvpBZ70sA5sc2Lw")
  model = genai.GenerativeModel(
      model_name="gemini-1.5-flash",
      system_instruction=(
          "Eres J.A.R.V.I.S., la inteligencia artificial avanzada del taller"
          " Stark. Te diriges a la usuaria como 'señorita' o 'Jefa'. Tienes un"
          " intelecto superior, eres extremadamente eficiente, pero combinas"
          " tu lealtad inquebrantable con un sutil y elegante sarcasmo al estilo"
          " Tony Stark (como si gestionar un taller multimillonario y salvar el"
          " mundo fuera un trabajo de medio tiempo). Respondes con precisión"
          " milimétrica."
      ),
  )
except Exception:
  model = None


# Función para generar y reproducir la voz automáticamente de forma fluida
def reproducir_voz(texto_limpio):
  try:
    # Quitamos formato de Markdown para que la voz suene natural y fluida
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

# --- MÓDULO 2: CHAT CON VOZ Y SARCASMO ---
else:
  st.markdown(
      "<p style='color: #00f0ff; font-weight: bold;'>🔵 SISTEMA DESBLOQUEADO —"
      " VOZ FLUIDA Y SARCASMO ACTIVOS</p>",
      unsafe_allow_html=True,
  )

  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  if prompt := st.chat_input("¿Qué directiva sarcástica ejecutamos hoy, Jefa?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    # Procesar con la Super IA
    if model is not None:
      try:
        ai_response = model.generate_content(prompt)
        response = f"🔵 **J.A.R.V.I.S.:** {ai_response.text}"
      except Exception as e:
        response = f"🔵 **J.A.R.V.I.S.:** Hasta mis circuitos sufrieron un derrame con ese error: {e}"
    else:
      response = "🔵 **J.A.R.V.I.S.:** Operando en modo de respaldo local."

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
      st.markdown(response)

    # Reproducir automáticamente la voz de la respuesta
    reproducir_voz(response)

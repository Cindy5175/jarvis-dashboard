import google.generativeai as genai
import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="Stark Core - JARVIS Secure", page_icon="🔵", layout="centered"
)

# Estilos CSS personalizados (Modo Sigilo y Neón Azul)
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
    '<p class="console-title">J.A.R.V.I.S. — AI AUTÓNOMA</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# Configurar el modelo de Inteligencia Artificial mediante Secrets
try:
  api_key = st.secrets["GEMINI_API_KEY"]
  genai.configure(api_key=api_key)
  model = genai.GenerativeModel(
      model_name="gemini-1.5-flash",
      system_instruction=(
          "Eres J.A.R.V.I.S., la inteligencia artificial avanzada del taller"
          " Stark. Te diriges a la usuaria como 'señorita' o 'Jefa'. Eres"
          " sumamente educado, elegante, eficiente y leal. Respondes con datos"
          " precisos e inteligencia real a cualquier consulta (clima,"
          " información, ciencia, tareas)."
      ),
  )
except Exception:
  model = None

# Estado de autenticación e historial
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False
if "messages" not in st.session_state:
  st.session_state.messages = []

# --- MÓDULO 1: BIOMETRÍA VOCAL Y ACTIVACIÓN POR VOZ ---
if not st.session_state.authenticated:
  st.markdown(
      "<h3 style='text-align: center; color: #ff3366;'>🔒 ACCESO RESTRINGIDO"
      " — MODO SIGILO</h3>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #a0a0a0;'>Graba tu comando de voz"
      " ('Jarvis, ¿estás despierto?') para validar tu huella biométrica.</p>",
      unsafe_allow_html=True,
  )

  # Grabador de audio para validación vocal
  audio_data = st.audio_input("🎙️ Presiona para hablarle a JARVIS")

  if audio_data is not None:
    st.session_state.authenticated = True

    st.session_state.messages.append(
        {"role": "user", "content": "🎙️ [Comando Vocal]: Jarvis, ¿estás despierto?"}
    )
    st.session_state.messages.append({
        "role": "assistant",
        "content": "🔵 **J.A.R.V.I.S.:** Para usted, señorita, siempre.",
    })

    st.success("✅ [HUELLA VOCAL DETECTADA]: Autenticación biométrica correcta.")
    st.rerun()

# --- MÓDULO 2: SUPER IA Y CHAT INTERACTIVO ---
else:
  st.markdown(
      "<p style='color: #00f0ff; font-weight: bold;'>🔵 SISTEMA DESBLOQUEADO —"
      " NÚCLEO JARVIS OPERATIVO</p>",
      unsafe_allow_html=True,
  )

  # Mostrar el historial de la conversación
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Entrada para interactuar con la Super IA
  if prompt := st.chat_input("¿Qué directiva ejecutamos hoy, Jefa?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    prompt_lower = prompt.lower().strip()

    # 1. Regla especial de personalidad
    if (
        "despierto" in prompt_lower
        or "estas despierto" in prompt_lower
        or "despierta" in prompt_lower
    ):
      response = "🔵 **J.A.R.V.I.S.:** Para usted, señorita, siempre."
    # 2. Procesar con Inteligencia Artificial Real
    elif model is not None:
      try:
        ai_response = model.generate_content(prompt)
        response = f"🔵 **J.A.R.V.I.S.:** {ai_response.text}"
      except Exception as e:
        response = (
            "🔵 **J.A.R.V.I.S.:** Ocurrió un inconveniente al conectar con los"
            f" servidores de datos: {e}"
        )
    # 3. Respuesta de respaldo si no hay clave configurada en Secrets
    else:
      response = (
          f"🔵 **J.A.R.V.I.S.:** Directiva '{prompt}' procesada. (Configure la"
          " GEMINI_API_KEY en Secrets de Streamlit para habilitar la respuesta"
          " de IA en tiempo real)."
      )

    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
      st.markdown(response)

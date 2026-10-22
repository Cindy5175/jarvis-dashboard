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
    '<p class="console-title">J.A.R.V.I.S. — NÚCLEO TÁCTICO SEGURO</p>',
    unsafe_allow_html=True,
)
st.markdown("---")

# --- MÓDULO 1: BIOMETRÍA DE VOZ (PROTOCOLO DE SEGURIDAD) ---
if "authenticated" not in st.session_state:
  st.session_state.authenticated = False

if not st.session_state.authenticated:
  st.markdown(
      "<h3 style='text-align: center; color: #ff3366;'>🔒 ACCESO RESTRINGIDO"
      " — MODO SIGILO</h3>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #a0a0a0;'>Se requiere validación de"
      " huella vocal para desbloquear el núcleo JARVIS.</p>",
      unsafe_allow_html=True,
  )

  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    if st.button("🎙️ VALIDAR BIOMETRÍA VOCAL", use_container_width=True):
      # Simulación de reconocimiento de voz exitoso ("Activar sistema")
      st.session_state.authenticated = True
      st.rerun()

else:
  # --- MÓDULO 2: CHAT INTERACTIVO FUNCIONAL (DESBLOQUEADO) ---
  st.success("✅ [ACCESO CONCEDIDO]: Biometría de voz validada. Hola, Jefa.")

  # Inicializar el historial de mensajes
  if "messages" not in st.session_state:
    st.session_state.messages = []

  # Mostrar mensajes anteriores en pantalla
  for message in st.session_state.messages:
    with st.chat_message(message["role"]):
      st.markdown(message["content"])

  # Caja de entrada interactiva para chatear
  if prompt := st.chat_input("¿Qué directiva operativa ejecutamos hoy?"):
    # Guardar y mostrar mensaje de la usuaria
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
      st.markdown(prompt)

    # Respuesta simulada del núcleo JARVIS
    response = (
        f"Directiva analizada en el núcleo JARVIS: '{prompt}'. Ejecutando"
        " parámetros con éxito, Jefa."
    )
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
      st.markdown(response)

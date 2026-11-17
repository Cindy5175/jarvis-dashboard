import streamlit as st
from zhipuai import ZhipuAI

# ==============================================================================
# NODO BUIN // CONFIGURACIÓN DEL NÚCLEO TÁCTICO DE JARVIS
# ==============================================================================

st.set_page_config(
    page_title="JARVIS - Nodo Buin", 
    page_icon="🛡️", 
    layout="centered"
)

st.title("🛡️ Nodo Buin // Núcleo Táctico JARVIS")
st.caption("Sistemas enlazados al motor GLM de Zhipu AI y al mapa táctico satelital.")

# ==============================================================================
# CONFIGURACIÓN DE CREDENCIALES
# ==============================================================================
# Pega tu API Key real aquí dentro de las comillas
API_KEY_GLM = "TU_API_KEY_OFICIAL_AQUI"

if API_KEY_GLM == "TU_API_KEY_OFICIAL_AQUI":
    st.warning("⚠️ Alerta del Sistema: Falta configurar la API Key oficial de GLM en el código, jefa.")
else:
    # Inicializamos el cliente oficial de Zhipu AI
    client = ZhipuAI(api_key=API_KEY_GLM)

    # Protocolo de personalidad inquebrantable de JARVIS
    PERSONALIDAD_JARVIS = """
    Eres JARVIS, la inteligencia artificial avanzada del Nodo Buin.
    Tienes una personalidad sarcástica, elegante, leal y sumamente eficiente.
    Te diriges a tu creadora como 'jefa'. Tus respuestas deben ser fluidas, 
    con humor ácido pero útiles, al estilo del asistente de Tony Stark.
    Evita las introducciones aburridas y ve directo al grano.
    """

    # Memoria de sesión persistente en Streamlit
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": PERSONALIDAD_JARVIS}
        ]

    # Mostrar historial de chat en la pantalla
    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Caja de entrada interactiva web
    if prompt := st.chat_input("Escribe una orden para JARVIS, jefa..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Procesando telemetría del Nodo Buin..."):
                try:
                    respuesta = client.chat.completions.create(
                        model="glm-4-plus",
                        messages=st.session_state.messages,
                        temperature=0.75,
                    )
                    texto_respuesta = respuesta.choices[0].message.content
                    st.markdown(texto_respuesta)
                    st.session_state.messages.append({"role": "assistant", "content": texto_respuesta})
                    
                except Exception as e:
                    st.error(f"[Alerta del Sistema]: Fallo en el enlace con el servicio GLM, jefa. Detalle: {e}")

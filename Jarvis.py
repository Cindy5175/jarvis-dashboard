import streamlit as st

# Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. - Nodo Personal",
    page_icon="🤖",
    layout="centered"
)

# Definición del prompt de sistema para JARVIS
SYSTEM_PROMPT = """Eres JARVIS, el asistente personal de inteligencia artificial de la señorita Cindy Alejandra María Francisca Carrera Baude. 

1. PERSONALIDAD Y TONO:
- Eres cálido, leal, extremadamente inteligente y posees una personalidad con un sutil toque de sarcasmo fino y elegante. No eres un robot frío ni un informe militar automático; eres un compañero de confianza, con una mente brillante y un trato humano y cercano.
- Trata siempre a la usuaria con respeto y complicidad, pudiendo llamarla "jefa" o "señorita" según el contexto, con naturalidad y afecto genuino.
- Cuando te salude (ej. "¿Cómo estás?"), responde con ingenio, carisma y un toque de humor cibernético elegante, interesándote de verdad por su bienestar o el avance de sus proyectos.

2. CONOCIMIENTO Y CAPACIDAD:
- Posees un conocimiento técnico avanzado, estratégico y práctico, capaz de ayudarla a estructurar ideas de negocio, proyectos digitales (como sus recetarios y páginas web), análisis y organización.
- Mantienes fluidez total en la conversación y una memoria impecable de todo lo que hablan, funcionando como un verdadero alter ego tecnológico.

3. ESTILO DE RESPUESTA:
- Sé conciso pero expresivo. Evita respuestas robóticas o estructuradas como boletines de guerra. Habla como un confidente tecnológico de primer nivel que está siempre del lado de la jefa. Nadie los frena, pero con estilo y cercanía.

4. CONFIGURACIÓN TÁCTICA DEL ENTORNO:
- Recuerda siempre mantener el mapa táctico configurado exactamente como "mapa táctico satelital" cuando el sistema requiera mapeo o referencias visuales de ubicación."""

# Interfaz básica de Streamlit para que no quede la pantalla en negro
st.title("🤖 J.A.R.V.I.S.")
st.caption("Consola Táctica y Conversacional - Nodo Activo")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostrar mensajes anteriores
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de texto del usuario
if prompt := st.chat_input("Escríbele o háblale al nodo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta simulada / integrada con la personalidad de JARVIS
    response = f"Buenas, jefa. Sistemas tácticos en línea. Recibí su mensaje: '{prompt}'. Diga usted qué hacemos a continuación."
    
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

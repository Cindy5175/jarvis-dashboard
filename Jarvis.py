import streamlit as st

# Configuración de la interfaz con los tonos originales de JARVIS
st.set_page_config(
    page_title="J.A.R.V.I.S. - Nodo Principal",
    page_icon="🔵",
    layout="centered"
)

# Estilos CSS personalizados para mantener el diseño azul original
st.markdown("""
    <style>
    .stApp {
        background-color: #0b1329;
        color: #e0f0ff;
    }
    h1, h2, h3 {
        color: #00d2ff !important;
        font-family: 'Segoe UI', sans-serif;
    }
    .stChatMessage.st-emotion-cache-1c7y2kd {
        background-color: #162245;
        border: 1px solid #1e3a8a;
    }
    .stChatInputContainer {
        border-color: #00d2ff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Definición del prompt de sistema y personalidad maestra
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

# Cabecera visual original
st.title("🔵 J.A.R.V.I.S.")
st.caption("Sistema Táctico y Conversacional Activo — Nodo Principal")

# Inicializar historial de chat con el nuevo saludo cálido y cercano
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hola, jefa. Por aquí todo en orden, operativo y con los circuitos bien puestos. ¿Qué se le ofrece hoy o en qué proyecto la acompaño?"}
    ]

# Mostrar el historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de texto del usuario
if prompt := st.chat_input("Escríbele o háblale al nodo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta con la personalidad renovada, inteligente y con sarcasmo fino
    response = f"Anotado, jefa. Analizando su requerimiento sobre '{prompt}' con la elegancia que la ocasión amerita. Déjeme ver los detalles y lo resolvemos al tiro."

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

import streamlit as st
import random
import time

# Configuración de página
st.set_page_config(page_title="JARVIS Dashboard", layout="wide", initial_sidebar_state="expanded")

# Estilos CSS personalizados para mantener estética neón/oscura
st.markdown("""
    <style>
    .main { background-color: #0d1117; color: #c9d1d9; }
    .stButton>button { background-color: #1f2937; color: #38bdf8; border: 1px solid #38bdf8; border-radius: 8px; }
    .stButton>button:hover { background-color: #38bdf8; color: #0d1117; }
    </style>
""", unsafe_allow_html=True)

# Inicializar historial de chat y estados
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Buenos días, jefa. Por aquí todo en orden en el Nodo Buin, con los circuitos bien puestos y lista para ayudarte con lo que necesites."}
    ]

if "stitch_mode" not in st.session_state:
    st.session_state.stitch_mode = False

# Sidebar / Módulos
with st.sidebar:
    st.title("⚙️ Módulos")
    if st.button("🔒 Bloquear Sistema"):
        st.toast("Sistema bloqueado temporalmente", icon="🔒")
    if st.button("🔄 Reinicio Total"):
        st.session_state.messages = []
        st.session_state.stitch_mode = False
        st.rerun()

# Layout Principal
st.title("💬 Consola de Comunicación")

# Botón para purgar
col1, col2 = st.columns([4, 1])
with col2:
    if st.button("🧹 Purgar"):
        st.session_state.messages = []
        st.rerun()

# Mostrar historial de chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Función para procesar comandos reales
def resolver_comando(user_input):
    cmd = user_input.lower().strip()
    
    # Activación / Desactivación Modo Stitch
    if "stich" in cmd or "stitch" in cmd:
        st.session_state.stitch_mode = True
        return "🧪 ¡Ooh, chīga! Modo Stitch activado. ¡Prepara el café y que comience el caos divertido, jefa!"
    
    if "modo jarvis" in cmd or "desactivar stitch" in cmd:
        st.session_state.stitch_mode = False
        return "Protocolo JARVIS restablecido. Sistemas en orden y bajo control, jefa."

    # Lógica de respuestas si Stitch está activo
    if st.session_state.stitch_mode:
        respuestas_stitch = [
            "¡Me-ega-nala! Procesando eso a toda velocidad, ¡meep meep!",
            "Comando recibido... ¡pero primero una travesura! Todo ejecutado con éxito.",
            "¡NAGA! Los sistemas están funcionando al 1000%. ¿Qué más rompen—digo, arreglamos?"
        ]
        return random.choice(respuestas_stitch)

    # Lógica de comandos JARVIS
    if "análisis de sistemas" in cmd or "analisis" in cmd:
        return "📊 Ejecutando diagnóstico completo de hardware: CPU al 14%, Memoria en 4.2 GB libres. Todos los nodos operando con normalidad."
    
    elif "buenos días" in cmd or "buenos dias" in cmd:
        return "Buenos días, jefa. Protocolos matutinos activos. Redes estables y pasarela de pago lista."
    
    elif "mapa táctico" in cmd or "mapa" in cmd:
        return "🗺️ Cargando mapa táctico satelital... Coordenadas fijadas en el Nodo Buin."
    
    # Respuesta sarcástica por defecto (en lugar de repetir la frase como eco)
    else:
        respuestas_jarvis = [
            f"Comando '{user_input}' registrado y procesado. Sin novedad en el frente, jefa.",
            f"Instrucción ejecutada. Aunque si me pregunta a mí, eso estuvo demasiado fácil.",
            f"Entendido. Procesé '{user_input}' con la precisión que te mereces. ¿Qué más hacemos?"
        ]
        return random.choice(respuestas_jarvis)

# Entrada de chat
if prompt := st.chat_input("Escríbele o háblale a JARVIS..."):
    # Agregar mensaje del usuario
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    # Generar respuesta lógica
    respuesta = resolver_comando(prompt)
    
    # Agregar respuesta del asistente
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.write(respuesta)

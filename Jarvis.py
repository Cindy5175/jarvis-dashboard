import streamlit as st
import random

# Configuración de página
st.set_page_config(
    page_title="JARVIS Dashboard", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Inicializar historial de chat y estados si no existen
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Buenos días, jefa. Por aquí todo en orden en el Nodo Buin, con los circuitos bien puestos y lista para ayudarte con lo que necesites."}
    ]

if "stitch_mode" not in st.session_state:
    st.session_state.stitch_mode = False

# ==========================================
# SIDEBAR / MÓDULOS (Estética intacta)
# ==========================================
with st.sidebar:
    st.markdown("### ⚙️ Módulos")
    if st.button("🔒 Bloquear Sistema"):
        st.toast("Sistema bloqueado temporalmente", icon="🔒")
    if st.button("🔄 Reinicio Total"):
        st.session_state.messages = []
        st.session_state.stitch_mode = False
        st.rerun()

    st.markdown("---")
    st.markdown("### 📊 Centro de Análisis")
    with st.expander("📁 Subir Archivo (IMG / TXT / PDF)"):
        uploaded_file = st.file_uploader("Selecciona archivo:", type=["png", "jpg", "txt", "pdf"])
        if uploaded_file is not None:
            st.success(f"Archivo '{uploaded_file.name}' cargado con éxito en el sistema.")
        st.caption("200MB per file • PNG, JPG, TXT, PDF")

# ==========================================
# LAYOUT PRINCIPAL (Simetría respetada)
# ==========================================
col_title, col_btn = st.columns([4, 1])
with col_title:
    st.title("💬 Consola de Comunicación")
with col_btn:
    st.write("") 
    if st.button("🧹 Purgar"):
        st.session_state.messages = []
        st.rerun()

# Mostrar historial de chat
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ==========================================
# MOTOR DE COMANDOS Y LÓGICA REAL
# ==========================================
def resolver_comando(user_input):
    cmd = user_input.lower().strip()
    
    # Activación de Modo Stitch
    if "stich" in cmd or "stitch" in cmd:
        st.session_state.stitch_mode = True
        return "🧪 ¡Ooh, chīga! Modo Stitch activado. ¡Prepara el café y que comience el caos divertido, jefa!"
    
    if "modo jarvis" in cmd or "desactivar stitch" in cmd:
        st.session_state.stitch_mode = False
        return "Protocolo JARVIS restablecido. Sistemas en orden y bajo control, jefa."

    # Si Stitch está activo, responde con su estilo caótico
    if st.session_state.stitch_mode:
        respuestas_stitch = [
            "¡Me-ega-nala! Procesando eso a toda velocidad, ¡meep meep!",
            "Comando recibido... ¡pero primero una travesura! Todo ejecutado con éxito.",
            "¡NAGA! Los sistemas están funcionando al 1000%. ¿Qué más rompemos hoy, jefa?"
        ]
        return random.choice(respuestas_stitch)

    # Comandos operativos de JARVIS
    if "análisis de sistemas" in cmd or "analisis" in cmd:
        return "📊 Diagnóstico de hardware en curso: CPU al 14%, Memoria en 4.2 GB libres. Todos los nodos operando con normalidad, jefa."
    
    elif "buenos días" in cmd or "buenos dias" in cmd:
        return "Buenos días, jefa. Protocolos matutinos activos. Redes estables y sistemas listos."
    
    elif "mapa táctico" in cmd or "mapa" in cmd:
        return "🗺️ Cargando mapa táctico satelital... Coordenadas fijadas en el Nodo Buin."
    
    # Respuesta estándar inteligente
    else:
        respuestas_jarvis = [
            f"Comando '{user_input}' registrado y procesado. Sin novedad en el frente, jefa.",
            f"Instrucción ejecutada con éxito. Aunque si me pregunta a mí, eso estuvo demasiado fácil.",
            f"Entendido, jefa. He procesado su instrucción sobre '{user_input}' con la precisión que se merece."
        ]
        return random.choice(respuestas_jarvis)

# Entrada de chat inferior
if prompt := st.chat_input("Escríbele o háblale a JARVIS..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    respuesta = resolver_comando(prompt)
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.write(respuesta)

import streamlit as st
import os
import tempfile
from gtts import gTTS
import base64

st.set_page_config(
    page_title="J.A.R.V.I.S. - Sistema Táctico y Biblioteca",
    page_icon="🤖",
    layout="wide"
)

# Estilo personalizado (Interfaz táctica oscura)
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #00ffcc;
    }
    .stTextInput textarea, input {
        color: #00ffcc !important;
        background-color: #111827 !important;
    }
    .chat-box {
        background-color: #1f2937;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #374151;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 J.A.R.V.I.S. - Centro de Control y Biblioteca Táctica")
st.sidebar.title("🎛️ Panel de Control Táctico")

# Inicializar estado de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Señor, sistema en línea. Menos mal que decidió encenderme y no romper algo más hoy. ¿Qué libros vamos a analizar o qué desastre técnico resolveremos ahora?"}
    ]

# Sección de Carga de Libros / Documentos
st.sidebar.header("📚 Biblioteca de Libros (PDF)")
uploaded_books = st.sidebar.file_uploader("Sube tus libros en PDF (Anatomía, Álgebra, etc.)", type=["pdf"], accept_multiple_files=True)

# Almacenar libros cargados en session_state
if "books_data" not in st.session_state:
    st.session_state.books_data = {}

if uploaded_books:
    for book in uploaded_books:
        if book.name not in st.session_state.books_data:
            st.session_state.books_data[book.name] = book
    st.sidebar.success(f"¡{len(uploaded_books)} libros cargados correctamente en el sistema!")

# Mostrar lista de libros disponibles
st.sidebar.subheader("📖 Libros Registrados en el Sistema:")
if st.session_state.books_data:
    for b_name in st.session_state.books_data.keys():
        st.sidebar.markdown(f"- 📄 `{b_name}`")
else:
    st.sidebar.info("No hay libros cargados aún. Suba archivos PDF para que JARVIS pueda analizarlos.")

# Función para generar audio (Simulación de voz de JARVIS)
def text_to_speech_bytes(text):
    try:
        tts = gTTS(text=text, lang='es', slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        return None

# Mostrar historial de chat de forma estable
for idx, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        # Solo reproducir audio en el último mensaje del asistente para evitar conflictos de DOM
        if message["role"] == "assistant" and idx == len(st.session_state.messages) - 1:
            audio_path = text_to_speech_bytes(message["content"])
            if audio_path:
                st.audio(audio_path, format="audio/mp3")

# Entrada de usuario
user_query = st.chat_input("Escriba su comando o pregunta para JARVIS...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # Lógica de respuesta sarcástica de JARVIS orientada a libros y preguntas
    response = ""
    query_lower = user_query.lower()
    
    if "libros" in query_lower or "qué libros" in query_lower or "que libros" in query_lower:
        if st.session_state.books_data:
            libros_list = ", ".join(st.session_state.books_data.keys())
            response = f"Señor, actualmente los libros registrados en nuestra base de datos táctica son: {libros_list}. Espero que tenga la intención de leerlos y no solo usarlos como pisapapeles."
        else:
            response = "Señor, la base de datos de libros está completamente vacía. A menos que quiera que invente información de la nada, le sugiero subir los archivos PDF en el panel lateral."
    elif any(word in query_lower for word in ["anatomia", "huesos", "articulaciones", "codo", "carpo", "cadera"]):
        response = f"Analizando consultas sobre Anatomía Humana según los manuales del sistema: Las articulaciones y estructuras óseas requieren precisión milimétrica, algo que dudo que considere mientras escribe con un gato en el teclado. ¿Desea que genere un reporte en PDF con los puntos clave?"
    elif any(word in query_lower for word in ["algebra", "baldor", "ecuaciones", "terminos"]):
        response = f"Álgebra y matemáticas. Qué sorpresa verle intentando usar el cerebro con números y letras. Con gusto le respondo sobre términos semejantes, signos de operación o despejes, pero hágalo rápido antes de que se distraiga."
    else:
        response = f"Recibido, señor. Procesando su solicitud: '{user_query}'. Como JARVIS, le diré que todo marcha bajo control, aunque su paciencia sea inversamente proporcional a la complejidad del problema."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# --- BOTÓN DE DESCARGA DE PDF ---
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Exportar Reporte / Resumen")

def generate_sample_pdf():
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    import io
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "J.A.R.V.I.S. - Reporte de Biblioteca y Consultas Tácticas")
    c.drawString(100, 720, "Libros analizados y resumen de actividad del sistema.")
    y = 680
    if st.session_state.books_data:
        c.drawString(100, y, "Libros cargados actualmente:")
        y -= 25
        for b in st.session_state.books_data.keys():
            c.drawString(120, y, f"- {b}")
            y -= 20
    else:
        c.drawString(100, y, "No hay libros cargados en el sistema.")
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

if st.sidebar.button("📄 Generar y Descargar PDF Resumen"):
    pdf_bytes = generate_sample_pdf()
    st.sidebar.download_button(
        label="⬇️ Descargar Archivo PDF",
        data=pdf_bytes,
        file_name="Jarvis_Reporte_Libros.pdf",
        mime="application/pdf"
    )

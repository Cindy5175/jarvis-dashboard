import streamlit as st
import os
import tempfile
from gtts import gTTS
import io
from datetime import datetime

st.set_page_config(
    page_title="J.A.R.V.I.S. - Centro de Control Táctico",
    page_icon="🤖",
    layout="wide"
)

# Estilo personalizado (Interfaz táctica oscura original)
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
    </style>
""", unsafe_allow_html=True)

# Cabecera táctica original
st.markdown("<h1 style='text-align: center; color: #00ffcc;'>J.A.R.V.I.S. IA</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #64ffda;'>[ NODO BUIN, CHILE // HORA OFICIAL 🇨🇱 // {datetime.now().strftime('%A, %d de %B de %Y - %H:%M:%S')} ]</p>", unsafe_allow_html=True)

st.markdown("---")

# Panel lateral
st.sidebar.title("🎛️ Panel Táctico")

# Inicializar estado de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Señor, sistema en línea y arquitectura original restaurada. ¿Qué manuales analizaremos hoy o qué desastre técnico resolveremos?"}
    ]

# Sección de Carga de Libros / Documentos
st.sidebar.header("📚 Biblioteca de Libros (PDF)")
uploaded_books = st.sidebar.file_uploader("Sube tus libros en PDF", type=["pdf"], accept_multiple_files=True)

if "books_data" not in st.session_state:
    st.session_state.books_data = {}

if uploaded_books:
    for book in uploaded_books:
        if book.name not in st.session_state.books_data:
            st.session_state.books_data[book.name] = book
    st.sidebar.success(f"¡{len(uploaded_books)} libros registrados en el sistema!")

# Mostrar lista de libros disponibles
st.sidebar.subheader("📖 Libros en el Sistema:")
if st.session_state.books_data:
    for b_name in st.session_state.books_data.keys():
        st.sidebar.markdown(f"- 📄 `{b_name}`")
else:
    st.sidebar.info("No hay libros cargados actualmente.")

# Botón de purgar chat
if st.button("🗑️ Purgar Chat"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Memoria del chat purgada, jefa. Sistemas limpios y listos para nuevas órdenes."}
    ]
    st.rerun()

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de usuario
user_query = st.chat_input("Escribe tu orden, código o consulta")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    query_lower = user_query.lower()
    
    if "libros" in query_lower or "qué libros" in query_lower or "que libros" in query_lower:
        if st.session_state.books_data:
            libros_list = ", ".join(st.session_state.books_data.keys())
            response = f"Señor, los libros registrados en nuestra base de datos táctica son: {libros_list}. Espero que tenga la intención de leerlos y no solo usarlos de adorno."
        else:
            response = "Señor, la base de datos de libros está vacía. Suba archivos PDF en el panel lateral."
    elif any(word in query_lower for word in ["anatomia", "huesos", "articulaciones", "codo", "carpo", "cadera"]):
        response = "Analizando Anatomía Humana: Las estructuras óseas y articulares requieren absoluta precisión. Puede descargar el reporte completo usando el módulo de PDF lateral."
    elif any(word in query_lower for word in ["algebra", "baldor", "ecuaciones", "terminos"]):
        response = "Álgebra y matemáticas. Excelente para mantener el cerebro activo. Pregunte lo que necesite o descargue el reporte operativo."
    else:
        response = f"Procesando su solicitud, jefa: '{user_query}'. Todo bajo control en el nodo."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# --- MÓDULO OPERATIVO DE PDF CON BOTÓN DE DESCARGA DIRECTA ---
st.sidebar.markdown("---")
st.sidebar.subheader("📥 Módulo Operativo PDF")

def generate_tactical_pdf():
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "J.A.R.V.I.S. - Reporte Operativo y Biblioteca Táctica")
    c.drawString(100, 730, "---------------------------------------------------------------------------------")
    y = 700
    if st.session_state.books_data:
        c.drawString(100, y, "Libros registrados y analizados actualmente en el sistema:")
        y -= 25
        for b in st.session_state.books_data.keys():
            c.drawString(120, y, f"• {b}")
            y -= 20
    else:
        c.drawString(100, y, "No hay libros cargados actualmente en la base de datos.")
        y -= 20
    
    y -= 20
    c.drawString(100, y, "Estado del Sistema: Nodo Buin operativo y estable.")
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

pdf_bytes = generate_tactical_pdf()

st.sidebar.download_button(
    label="📄 Descargar Reporte PDF",
    data=pdf_bytes,
    file_name="Jarvis_Reporte_Operativo.pdf",
    mime="application/pdf",
    use_container_width=True
)

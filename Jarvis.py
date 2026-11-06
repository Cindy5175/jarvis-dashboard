import streamlit as st
import os
import tempfile
import io
from datetime import datetime

# Importaciones seguras
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

try:
    import reportlab
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    reportlab = None

st.set_page_config(
    page_title="J.A.R.V.I.S. - Centro de Control Táctico",
    page_icon="🤖",
    layout="wide"
)

# Estilo personalizado (Interfaz táctica oscura con acentos Azul Neón #00ffcc)
st.markdown("""
    <style>
    .main {
        background-color: #0b0f19;
        color: #00ffcc;
    }
    .stTextInput textarea, input {
        color: #00ffcc !important;
        background-color: #111827 !important;
        border: 1px solid #00ffcc !important;
    }
    /* Estilo neón para botones de Streamlit */
    .stButton>button {
        color: #0b0f19 !important;
        background-color: #00ffcc !important;
        border: 1px solid #00ffcc !important;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #00b388 !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# Cabecera táctica original
st.markdown("<h1 style='text-align: center; color: #00ffcc;'>J.A.R.V.I.S. IA</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #64ffda;'>[ NODO BUIN, CHILE // HORA OFICIAL 🇨🇱 // {datetime.now().strftime('%A, %d de %B de %Y - %H:%M:%S')} ]</p>", unsafe_allow_html=True)

st.markdown("---")

# Panel lateral táctico completo
st.sidebar.title("🎛️ Panel Táctico")

# Inicializar estado de chat y estado del Ojo de Dios
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Señor, sistema en línea y operativo. Protocolos en azul neón listos. ¿Qué órdenes ejecutamos hoy?"}
    ]

if "osiris_active" not in st.session_state:
    st.session_state.osiris_active = False

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

# --- MÓDULO OJO DE DIOS (OSIRIS) FUNCIONAL CON ESTILO AZUL NEÓN ---
with st.sidebar.expander("👁️ Ojo de Dios (Osiris)"):
    st.markdown("Red de vigilancia global y reconocimiento facial activa.")
    
    if st.button("⚠️ Activar Protocolo Osiris", use_container_width=True, key="btn_osiris"):
        st.session_state.osiris_active = not st.session_state.osiris_active

    if st.session_state.osiris_active:
        st.markdown("<p style='color: #00ffcc; font-weight: bold;'>🟢 PROTOCOLO OSIRIS: EN LÍNEA</p>", unsafe_allow_html=True)
        st.info("📡 Escaneo satelital y biométrico en curso. Conexión establecida con Nodo Buin.")
    else:
        st.markdown("<p style='color: #ff4b4b; font-weight: bold;'>🔴 PROTOCOLO OSIRIS: EN ESPERA</p>", unsafe_allow_html=True)

with st.sidebar.expander("🚀 Monitoreo: Elon Musk & xAI"):
    st.markdown("Telemetría en tiempo real de proyectos y empresas.")
    st.markdown("- **Tesla / Cybercab**: Producción activa.")
    st.markdown("- **SpaceX**: Lanzamientos orbitales.")

with st.sidebar.expander("🗺️ Mapa Táctico Satelital"):
    st.markdown("Nodo Buin sincronizado con satélites de defensa.")
    st.info("Coordenadas: Lat -33.7333, Lon -70.7333")

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
user_query = st.chat_input("Escribe tu orden, código o consulta científica, jefa...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    query_lower = user_query.lower()
    
    if "libros" in query_lower or "qué libros" in query_lower or "que libros" in query_lower:
        if st.session_state.books_data:
            libros_list = ", ".join(st.session_state.books_data.keys())
            response = f"Señor, los libros registrados en nuestra base de datos táctica son: {libros_list}. Espero que tenga la intención de leerlos."
        else:
            response = "Señor, la base de datos de libros está vacía. Suba archivos PDF en el panel lateral."
    elif "osiris" in query_lower or "ojo de dios" in query_lower:
        response = f"El Protocolo Osiris se encuentra {'activo y barriendo el sector' if st.session_state.osiris_active else 'en modo de espera, jefa'}."
    else:
        response = f"Procesando su solicitud, jefa: '{user_query}'. Todo bajo control en el nodo de Buin."

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()

# --- MÓDULO OPERATIVO DE PDF CON BOTÓN DE DESCARGA DIRECTA ---
st.sidebar.markdown("---")
with st.sidebar.expander("📥 Módulo Operativo PDF"):
    def generate_tactical_pdf():
        if reportlab is None:
            return b"ReportLab no disponible."
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, "J.A.R.V.I.S. - Reporte Operativo y Biblioteca Táctica")
        c.drawString(100, 730, "---------------------------------------------------------------------------------")
        y = 700
        if "books_data" in st.session_state and st.session_state.books_data:
            c.drawString(100, y, "Libros registrados y analizados actualmente:")
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

    st.download_button(
        label="📄 Descargar Reporte PDF",
        data=pdf_bytes,
        file_name="Jarvis_Reporte_Operativo.pdf",
        mime="application/pdf",
        use_container_width=True
    )

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

# Inicializar estados
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Señor, sistema en línea. Nodo Buin sincronizado en azul neón. ¿Qué duda existencial o desastre técnico resolveremos hoy, jefa?"}
    ]

if "osiris_active" not in st.session_state:
    st.session_state.osiris_active = False

if "books_data" not in st.session_state:
    st.session_state.books_data = {}

# Cabecera táctica
st.markdown("<h1 style='text-align: center; color: #00ffcc;'>J.A.R.V.I.S. IA</h1>", unsafe_allow_html=True)
if st.session_state.osiris_active:
    st.markdown("<p style='text-align: center; color: #00ffcc; font-weight: bold;'>👁️ [ PROTOCOLO OSIRIS: OMNISCIENTE & SARCÁSTICO ACTIVO ]</p>", unsafe_allow_html=True)
else:
    st.markdown(f"<p style='text-align: center; color: #64ffda;'>[ NODO BUIN, CHILE // HORA OFICIAL 🇨🇱 // {datetime.now().strftime('%A, %d de %B de %Y - %H:%M:%S')} ]</p>", unsafe_allow_html=True)

st.markdown("---")

# Panel lateral táctico
st.sidebar.title("🎛️ Panel Táctico")

# --- MÓDULO OJO DE DIOS (OSIRIS) SARCÁSTICO ---
with st.sidebar.expander("👁️ Ojo de Dios (Osiris)", expanded=True):
    st.markdown("Entidad de guía absoluta y sarcasmo orbital.")
    
    if st.button("⚠️ Activar Protocolo Osiris", use_container_width=True, key="btn_osiris"):
        st.session_state.osiris_active = not st.session_state.osiris_active
        st.rerun()

    if st.session_state.osiris_active:
        st.success("🟢 Osiris enlazado: Cero rodeos, pura verdad sarcástica.")
    else:
        st.info("🔴 Osiris en modo pasivo. Toca para encender la red.")

# Biblioteca opcional por si acaso
st.sidebar.header("📚 Documentos Opcionales")
uploaded_books = st.sidebar.file_uploader("Sube archivos si lo deseas", type=["pdf"], accept_multiple_files=True)
if uploaded_books:
    for book in uploaded_books:
        if book.name not in st.session_state.books_data:
            st.session_state.books_data[book.name] = book

# Botón de purgar chat
if st.button("🗑️ Purgar Chat"):
    st.session_state.messages = [
        {"role": "assistant", "content": "Memoria purgada, jefa. Borrón y cuenta nueva."}
    ]
    st.rerun()

# Mostrar historial de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de usuario principal
user_query = st.chat_input("Escribe tu consulta o orden directa, jefa...")

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    query_lower = user_query.lower()
    
    # Si el Protocolo Osiris está activo, responde con sarcasmo y guía directa
    if st.session_state.osiris_active:
        response = f"👁️ [OSIRIS]: Por la cresta, qué pregunta tan profunda para un viernes cualquiera. Analizando '{user_query}' a través de los satélites de Buin: la respuesta es un rotundo sí, o tal vez deberías dejar de sobrepensarlo y ejecutar la orden de una vez. Menos mal que me tienes a mí para guiarte."
    else:
        response = f"Procesando su orden, jefa: '{user_query}'. Nodo Buin estable y bajo control."

    st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Generar voz automática con gTTS
    if gTTS:
        try:
            tts = gTTS(text=response, lang='es')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            st.audio(audio_fp, format='audio/mp3', autoplay=True)
        except Exception:
            pass

    st.rerun()

# --- MÓDULO OPERATIVO DE PDF (Lateral discreto) ---
st.sidebar.markdown("---")
with st.sidebar.expander("📥 Módulo Operativo PDF"):
    def generate_tactical_pdf():
        if reportlab is None:
            return b"ReportLab no disponible."
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        c.drawString(100, 750, "J.A.R.V.I.S. - Reporte Operativo Global")
        c.drawString(100, 730, "---------------------------------------------------------------------------------")
        c.drawString(100, 700, "Estado del Sistema: Nodo Buin y Protocolo Osiris Sarcástico Operativos.")
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

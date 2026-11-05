import os
import datetime
import streamlit as st
from pypdf import PdfReader
from streamlit_autorefresh import st_autorefresh
from openai import OpenAI

# ---------------------------------------------------------
# Configuración inicial de la página
# ---------------------------------------------------------
st.set_page_config(
    page_title="JARVIS System Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Estilo Visual: Azul Neón Avanzado (Estilo Stark / E.D.I.T.H.)
# ---------------------------------------------------------
st.markdown("""
    <style>
    /* Fondo general de la aplicación */
    .stApp {
        background-color: #0b0f19;
        color: #e0fbfc;
    }
    
    /* Barra lateral táctica */
    [data-testid="stSidebar"] {
        background-color: #0d1b2a;
        border-right: 1px solid #00f3ff33;
    }
    
    /* Títulos y cabeceras con brillo neón */
    h1, h2, h3 {
        color: #00f3ff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.4);
    }
    
    /* Estilo específico para el rótulo de Stark Industries */
    .stark-header {
        color: #00f3ff !important;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.15rem;
        font-weight: bold;
        text-shadow: 0 0 12px rgba(0, 243, 255, 0.7);
        padding: 10px 0;
        letter-spacing: 1px;
    }
    
    /* Botones con estilo neón */
    .stButton>button {
        background-color: #0d1b2a;
        color: #00f3ff;
        border: 1px solid #00f3ff;
        border-radius: 6px;
        box-shadow: 0 0 8px rgba(0, 243, 255, 0.3);
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #00f3ff;
        color: #0b0f19;
        box-shadow: 0 0 15px #00f3ff;
    }
    
    /* Inputs de chat */
    .stChatInput input {
        background-color: #1b263b !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Funciones auxiliares: Lectura de PDFs con pypdf
# ---------------------------------------------------------
@st.cache_data(show_spinner="Indexando base de datos de libros y documentos...")
def cargar_documentos_pdf(directorio_pdf="documentos"):
    documentos = []
    if not os.path.exists(directorio_pdf):
        os.makedirs(directorio_pdf)
        return documentos

    for archivo in os.listdir(directorio_pdf):
        if archivo.endswith(".pdf"):
            ruta_pdf = os.path.join(directorio_pdf, archivo)
            try:
                reader = PdfReader(ruta_pdf)
                texto_archivo = ""
                for idx, pagina in enumerate(reader.pages):
                    texto = pagina.extract_text()
                    if texto:
                        texto_archivo += f"\n--- Página {idx + 1} ---\n" + texto
                if texto_archivo.strip():
                    documentos.append({
                        "nombre": archivo,
                        "contenido": texto_archivo
                    })
            except Exception as e:
                st.error(f"Error al leer el archivo {archivo}: {e}")
    return documentos

def buscar_contexto_relevante(query, documentos, max_caracteres=4000):
    if not documentos:
        return "No hay documentos cargados en el sistema."

    contexto_acumulado = ""
    palabras_clave = [p.lower() for p in query.split() if len(p) > 3]

    for doc in documentos:
        lineas = doc["contenido"].split("\n")
        lineas_relevantes = [linea for linea in lineas if any(kw in linea.lower() for kw in palabras_clave)]
        if lineas_relevantes:
            fragmento = f"\n[Fuente: {doc['nombre']}]\n" + "\n".join(lineas_relevantes[:15])
            if len(contexto_acumulado) + len(fragmento) < max_caracteres:
                contexto_acumulado += fragmento

    if not contexto_acumulado and documentos:
        contexto_acumulado = f"[Fuente: {documentos[0]['nombre']}]\n" + documentos[0]["contenido"][:max_caracteres]

    return contexto_acumulado

docs_cargados = cargar_documentos_pdf("documentos")

# ---------------------------------------------------------
# Interfaz: Barra Lateral (Módulos Tácticos Desplegables)
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Estado del Sistema")
    st.success("🟢 Sistema Operativo" if docs_cargados else "🟡 Operativo (Sin PDFs)")
    
    st.subheader("📚 Base de Datos (PDFs)")
    if docs_cargados:
        for doc in docs_cargados:
            st.write(f"📖 {doc['nombre']}")
    else:
        st.info("Coloca tus archivos PDF en la carpeta 'documentos/' del proyecto.")
        
    st.divider()
    
    # 1. Mapa Táctico Satelital
    with st.expander("🗺️ Mapa Táctico Satelital"):
        st.markdown("Nodo Buin sincronizado con satélites de defensa.")
        st.map(latitude=-33.7333, longitude=-70.7333, zoom=10)

    # 2. Cámaras en Vivo (ISS)
    with st.expander("📷 Cámara en Vivo: Espacio (ISS)"):
        st.video("https://www.youtube.com/watch?v=21X5lGlDOfg")

    # 3. Cámaras

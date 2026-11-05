import os
import streamlit as st
from pypdf import PdfReader
from streamlit_autorefresh import st_autorefresh
from openai import OpenAI
import datetime

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
# Estilo Visual: Azul Neón & Tema Táctico Starksiano
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
    
    /* Cajas de métricas y contenedores */
    div[data-testid="stMetric"] {
        background-color: #1b263b;
        border: 1px solid #00f3ff55;
        padding: 10px;
        border-radius: 8px;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.15);
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
# Funciones auxiliares: Lectura de PDFs
# ---------------------------------------------------------
@st.cache_data(show_spinner="Cargando base de datos de documentos...")
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

# Cargar documentos al inicio
docs_cargados = cargar_documentos_pdf("documentos")

# ---------------------------------------------------------
# Interfaz: Barra Lateral (Módulos a la izquierda)
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
    
    st.subheader("🎙️ Configuración de Audio")
    escucha_activa = st.checkbox("🎙️ Escucha Continua (Hands-Free)", value=False)
    
    st.button("➕ Registrar Tarea", use_container_width=True)
    st.button("📷 Alternar Cámaras", use_container_width=True)

# ---------------------------------------------------------
# Cuerpo Principal del Dashboard
# ---------------------------------------------------------
st.title("🤖 JARVIS - Dashboard Táctico & Asistente")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ mapa táctico satelital")
    st.info("Visualización táctica activa y sincronizada con el nodo central en Buin.")

with col2:
    st.subheader("⏱️ Estado del Tiempo")
    st_autorefresh(interval=1000, key="reloj_jarvis")
    hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
    st.metric(label="Hora del Sistema", value=hora_actual)

st.divider()

# ---------------------------------------------------------
# Módulo de

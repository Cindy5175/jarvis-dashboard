import os
import datetime
import re
import zoneinfo
import io
import streamlit as st
from pypdf import PdfReader
from streamlit_autorefresh import st_autorefresh
from openai import OpenAI
import google.generativeai as genai
from gtts import gTTS

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
    .stApp {
        background-color: #0b0f19;
        color: #e0fbfc;
    }
    [data-testid="stSidebar"] {
        background-color: #0d1b2a;
        border-right: 1px solid #00f3ff33;
    }
    h1, h2, h3 {
        color: #00f3ff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        text-shadow: 0 0 10px rgba(0, 243, 255, 0.4);
    }
    .ark-reactor-container {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        margin: 5px 0 5px 0;
    }
    .ark-reactor {
        width: 55px;
        height: 55px;
        background: radial-gradient(circle, #00f3ff 0%, #0d1b2a 70%);
        border: 2px solid #00f3ff;
        border-radius: 50%;
        box-shadow: 0 0 15px #00f3ff, inset 0 0 10px #00f3ff;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    .ark-triangle {
        width: 0;
        height: 0;
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-bottom: 18px solid #ffffff;
        filter: drop-shadow(0 0 5px #00f3ff);
    }
    .stark-header {
        color: #00f3ff !important;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.15rem;
        font-weight: bold;
        text-shadow: 0 0 12px rgba(0, 243, 255, 0.7);
        padding: 2px 0;
        letter-spacing: 1px;
        text-align: left;
    }
    .stark-sub {
        color: #8be9fd !important;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        margin-bottom: 15px;
        text-align: left;
    }
    .stButton>button {
        background-color: #0d1b2a;
        color: #00f3ff;
        border: 1px solid #00f3ff;
        border-radius: 6px;
        box-shadow: 0 0 8px rgba(0, 243, 255, 0.3);
        transition: 0.3s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #00f3ff;
        color: #0b0f19;
        box-shadow: 0 0 15px #00f3ff;
    }
    .stChatInput input {
        background-color: #1b263b !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Módulos en Funciones Independientes
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
                        "contenido": texto_archivo,
                        "ruta": ruta_pdf
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

def limpiar_texto_para_voz(texto):
    texto_limpio = re.sub(r'[*#_`>-]', '', texto)
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    return texto_limpio

def generar_audio_bytes(texto):
    try:
        texto_procesado = limpiar_texto_para_voz(texto)
        if not texto_procesado:
            return None
        tts = gTTS(text=texto_procesado, lang='es', tld='cl')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp
    except Exception:
        return None

def renderizar_barra_lateral(docs_cargados):
    with st.sidebar:
        st.header("⚙️ Estado del Sistema")
        
        # Módulo de Base de Datos y PDFs con opción de descarga
        with st.expander("📚 Base de Datos & PDFs", expanded=True):
            if docs_cargados:
                st.success("🟢 Operativo (PDFs Activos)")
                for doc in docs_cargados:
                    st.write(f"📖 {doc['nombre']}")
                    try:
                        with open(doc["ruta"], "rb") as archivo_pdf:
                            st.download_button(
                                label=f"📥 Descargar {doc['nombre'][:12]}...",
                                data=archivo_pdf,
                                file_name=doc['nombre'],
                                mime="application/pdf",
                                key=f"dl_{doc['nombre']}"
                            )
                    except Exception:
                        pass
            else:
                st.warning("🟡 Operativo (Sin PDFs en carpetas)")
                st.info("Coloca tus archivos PDF en la carpeta 'documentos/'.")
            
        st.divider()
        
        # Ojo de Dios (Osiris)
        with st.expander("👁️ Ojo de Dios (Osiris)"):
            st.markdown("Red de vigilancia global y reconocimiento facial activa.")
            if st.button("⚠️ Activar Protocolo Osiris", use_container_width=True):
                st.error("¡Ojo de Dios enlazado a los sensores del Nodo Buin, jefa!")

        # Módulo Extra: Vigilancia Elon Musk & Ecosistema Tecnológico
        with st.expander("🚀 Monitoreo: Elon Musk & xAI"):
            st.markdown("Telemetría en tiempo real de proyectos y empresas:")
            st.markdown("- **Tesla / Cybercab**: Transición de producción.")
            st.markdown("- **SpaceX**: Lanzamientos y evolución orbital.")
            st.markdown("- **xAI / Grok**: Modelos de inteligencia artificial.")
            if st.button("🛰️ Consultar Estado Musk", use_container_width=True):
                st.toast("Enlazando telemetría corporativa...")
                st.info("Reporte: Fábrica de Austin adaptándose a flotas autónomas y xAI con procesamiento optimizado.")

        # Módulo Extra: Logística, Ciberseguridad & Cartografía
        with st.expander("🛠️ Utilidades Logísticas & Red"):
            st.markdown("Herramientas de auditoría y cartografía avanzada:")
            st.markdown("- **LocalSend**: Transferencia local segura.")
            st.markdown("- **Gobuster / Nikto**: Auditoría web.")
            st.markdown("- **WorldCam**: Cámaras globales.")
            st.markdown("- **SunCalc / Ventusky**: Análisis solar y meteorológico.")
            if st.button("🌐 Lanzar Enlaces Tácticos", use_container_width=True):
                st

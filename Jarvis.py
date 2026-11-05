import os
import datetime
import re
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
    .stark-header {
        color: #00f3ff !important;
        font-family: 'Courier New', Courier, monospace;
        font-size: 1.15rem;
        font-weight: bold;
        text-shadow: 0 0 12px rgba(0, 243, 255, 0.7);
        padding: 5px 0;
        letter-spacing: 1px;
    }
    .stark-sub {
        color: #8be9fd !important;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        margin-bottom: 15px;
    }
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
    .stChatInput input {
        background-color: #1b263b !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Funciones auxiliares: Lectura de PDFs con pypdf y Limpieza de Texto
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

def limpiar_texto_para_voz(texto):
    """Filtra asteriscos, hashtags, guiones y símbolos para la síntesis de voz."""
    texto_limpio = re.sub(r'[*#_`>-]', '', texto)
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()
    return texto_limpio

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
    
    # Módulos tácticos requeridos
    with st.expander("🗺️ Mapa Táctico Satelital"):
        st.markdown("Nodo Buin sincronizado con satélites de defensa.")
        st.info("Coordenadas: Lat -33.7333, Lon -70.7333")

    with st.expander("📷 Cámara en Vivo: Espacio (ISS)"):
        st.video("https://www.youtube.com/watch?v=21X5lGlDOfg")

    with st.expander("🌍 Cámara en Vivo: Red Mundial (earthTV)"):
        st.info("Conectando con feeds públicos globales de earthTV...")

    with st.expander("🎥 Cámara en Vivo: Global (SkylineWebcams)"):
        st.info("Canal de streaming óptico activo.")

    with st.expander("🌤️ Clima en Vivo (Buin)"):
        st.metric(label="Temperatura Nodo Buin", value="21 °C", delta="Estable")
        st.caption("Humedad: 45% | Viento: 12 km/h")

    with st.expander("🎙️ Escucha Continua (Hands-Free)"):
        st.checkbox("Activar escucha de voz continua", value=False)
        st.caption("Micrófono periférico en espera de comandos.")

    with st.expander("➕ Registro de Tareas"):
        nueva_tarea = st.text_input("Nueva Misión / Tarea:")
        if st.button("Registrar Tarea ➕", use_container_width=True):
            if nueva_tarea:
                st.success(f"Misión registrada: {nueva_tarea}")
            else:
                st.warning("Escribe una descripción para la misión.")

    with st.expander("🛡️ Módulo E.D.I.T.H. & Ojo de Dios"):
        st.markdown("Control satelital de defensa y vigilancia activo.")
        if st.button("⚠️ Activar Protocolo E.D.I.T.H.", use_container_width=True):
            st.error("¡Protocolo de defensa E.D.I.T.H. desplegado en el Nodo Buin, jefa!")

    st.divider()
    st.caption("Stark Industries // Nodo Buin, Chile 🇨🇱")

# ---------------------------------------------------------
# Encabezado Principal (J.A.R.V.I.S. IA, Triángulo Stark y Fecha)
# ---------------------------------------------------------
st_autorefresh(interval=1000, key="reloj_jarvis_top")
tiempo_actual_str = datetime.datetime.now().strftime("%A, %d de %B de %Y – %H:%M:%S")

st.markdown('<div class="stark-header">▲ J.A.R.V.I.S. IA // STARK INDUSTRIES</div>', unsafe_allow_html=True)
st.markdown(f'<div class="stark-sub">[ NODO BUIN, CHILE // {tiempo_actual_str} ]</div>', unsafe_allow_html=True)

if st.button("🔒 Bloquear Búnker", use_container_width=True):
    st.warning("Protocolo de seguridad activado. Cierre perimetral en curso, jefa.")

st.divider()

# ---------------------------------------------------------
# Botones de Protocolos Rápidos (Base, Alerta, Diagnóstico)
# ---------------------------------------------------------
col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    if st.button("📊 Protocolo Base"):
        st.toast("Ejecutando telemetría nominal de CPU, RAM y clima de Buin...")
        st.info("Reporte del búnker: Temperatura óptima a 21°C, consumo de CPU al 12%, sistemas estables por la cresta.")
with col_p2:
    if st.button("🚨 Protocolo Alerta"):
        st.toast("Activando perímetro y mapa satelital...")
        st.warning("Alerta táctica: Perímetro del nodo seguro, sin intrusos detectados en Buin.")
with col_p3:
    if st.button("⚙️ Protocolo Diagnóstico"):
        st.toast("Purgando caché temporal del Core LLM...")
        st.success("Diagnóstico completado: Núcleo neuronal y enciclopedia interna al 100% de operatividad.")

st.divider()

# ---------------------------------------------------------
# Chat IA & Protocolo E.D.I.T.H.
# ---------------------------------------------------------
st.subheader("💬 Chat IA & Protocolo E.D.I.T.H.")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "Buenos días, jefa. El nodo de Buin está operativo, la temperatura es perfecta y, por la cresta, nadie ha intentado hackearnos hoy. ¿Qué ciencia, historia o experimento nos trae por aquí?"}
    ]

for msj in st.session_state.mensajes:
    with st.chat_message(msj["role"]):
        st.markdown(msj["content"])

if prompt := st.chat_input("Escribe tu orden o dicta a E.D.I.T.H., jefa..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    
    if not api

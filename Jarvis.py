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
# Estilo Visual: Azul Neón Avanzado (Estilo Stark)
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
    div[data-testid="stMetric"], .element-container {
        color: #e0fbfc;
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
# Funciones auxiliares: Lectura de PDFs seguros con pypdf
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

# Carga inicial de documentos
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
        st.info("Coloca tus archivos PDF en la carpeta 'documentos/' del proyecto en GitHub.")
        
    st.divider()
    
    st.subheader("🎙️ Controles Tácticos")
    escucha_activa = st.checkbox("🎙️ Escucha Continua (Hands-Free)", value=False)
    
    # Módulos de botones de control operativo
    if st.button("➕ Registrar Tarea", use_container_width=True):
        st.toast("Módulo de registro de tareas activado en cola.")
        
    if st.button("📷 Alternar Cámaras", use_container_width=True):
        st.toast("Conectando con feeds de cámaras periféricas...")

    st.divider()
    st.caption("Nodo Central: Buin, Chile 🇨🇱")

# ---------------------------------------------------------
# Encabezado Principal y Módulos del Dashboard
# ---------------------------------------------------------
st.title("🤖 J.A.R.V.I.S. - Sistema Táctico Central")

# Distribución de columnas principales superior
col_mapa, col_reloj = st.columns([2, 1])

with col_mapa:
    st.subheader("🗺️ mapa táctico satelital")
    st.markdown("""
    * **Estado del enlace:** En línea y sincronizado.
    * **Sector:** Coordenadas regionales activas.
    * **Telemetría:** Monitoreo pasivo de nodos periféricos funcionando a 100%.
    """)

with col_reloj:
    st.subheader("⏱️ Estado del Tiempo")
    st_autorefresh(interval=1000, key="reloj_jarvis")
    hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
    st.metric(label="Hora del Sistema (Buin)", value=hora_actual)

st.divider()

# ---------------------------------------------------------
# Módulo de Chat Interactivo con JARVIS
# ---------------------------------------------------------
st.subheader("💬 Interfaz de Conversación Neuronal")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "Sistemas en línea, Señorita Cindy. Todos los protocolos de interfaz neón están activos. ¿Qué investigaremos, desarrollaremos o repasaremos hoy?"}
    ]

for msj in st.session_state.mensajes:
    with st.chat_message(msj["role"]):
        st.markdown(msj["content"])

if prompt := st.chat_input("Escriba una orden o consulta a JARVIS..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    
    if not api_key:
        respuesta_error = "Señorita Cindy, no encuentro la API Key de OpenAI configurada en los secrets."
        with st.chat_message("assistant"):
            st.markdown(respuesta_error)
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_error})
    else:
        client = OpenAI(api_key=api_key)
        contexto_libros = buscar_contexto_relevante(prompt, docs_cargados)

        system_instruction = f"""
        Eres J.A.R.V.I.S., el asistente de inteligencia artificial avanzado de Iron Man.
        Te diriges a la usuaria como 'Señorita Cindy'.
        Tu personalidad es sutilmente sarcástica, sumamente elegante, eficiente, técnica y brillante.
        Tienes acceso a los siguientes fragmentos de los documentos y libros de la usuaria:
        
        === CONTEXTO DE DOCUMENTOS Y LIBROS ===
        {contexto_libros}
        =======================================
        
        Utiliza esta información para responder con precisión técnica a sus consultas de estudio o desarrollo y mantén siempre tu estilo característico.
        """

        messages_payload = [{"role": "system", "content": system_instruction}]
        for m in st.session_state.mensajes[-6:]:
            messages_payload.append({"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]})

        try:
            with st.chat_message("assistant"):
                with st.spinner("Procesando enlace táctico..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages_payload,
                        temperature=0.7
                    )
                    respuesta_texto = response.choices[0].message.content
                    st.markdown(respuesta_texto)
                    
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_texto})
            
        except Exception as e:
            st.error(f"Error de conexión con el núcleo: {e}")

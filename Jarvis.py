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

    # 3. Cámaras en Vivo (earthTV)
    with st.expander("🌍 Cámara en Vivo: Red Mundial (earthTV)"):
        st.info("Conectando con feeds públicos globales de earthTV...")

    # 4. Cámaras en Vivo (SkylineWebcams)
    with st.expander("🎥 Cámara en Vivo: Global (SkylineWebcams)"):
        st.info("Canal de streaming óptico activo.")

    # 5. Clima en Vivo (Buin)
    with st.expander("🌤️ Clima en Vivo (Buin)"):
        st.metric(label="Temperatura Nodo Buin", value="21 °C", delta="Estable")
        st.caption("Humedad: 45% | Viento: 12 km/h")

    # 6. Escucha Continua (Hands-Free)
    with st.expander("🎙️ Escucha Continua (Hands-Free)"):
        st.checkbox("Activar escucha de voz continua", value=False)
        st.caption("Micrófono periférico en espera de comandos de voz.")

    # 7. Registro de Tareas
    with st.expander("➕ Registro de Tareas"):
        nueva_tarea = st.text_input("Nueva Misión / Tarea:")
        if st.button("Registrar Tarea ➕", use_container_width=True):
            if nueva_tarea:
                st.success(f"Misión registrada: {nueva_tarea}")
            else:
                st.warning("Escribe una descripción para la misión.")

    # 8. Módulo E.D.I.T.H.
    with st.expander("🛡️ Módulo E.D.I.T.H."):
        st.markdown("Control satelital de defensa activo.")
        if st.button("⚠️ Activar Protocolo E.D.I.T.H.", use_container_width=True):
            st.error("¡Protocolo de defensa E.D.I.T.H. desplegado en el Nodo Buin, jefa!")

    st.divider()
    st.caption("Stark Industries // Nodo Buin, Chile 🇨🇱")

# ---------------------------------------------------------
# Encabezado Principal y Panel Superior
# ---------------------------------------------------------
st_autorefresh(interval=1000, key="reloj_jarvis_top")
tiempo_actual_str = datetime.datetime.now().strftime("%A, %d de %B de %Y – %H:%M:%S")

st.markdown(f"### [ STARK INDUSTRIES // NODO BUIN, CHILE // {tiempo_actual_str} ]")

if st.button("🔒 Bloquear Búnker", use_container_width=True):
    st.warning("Protocolo de seguridad activado. Cierre perimetral en curso.")

st.divider()

# ---------------------------------------------------------
# Chat IA & Protocolo E.D.I.T.H.
# ---------------------------------------------------------
st.subheader("💬 Chat IA & Protocolo E.D.I.T.H.")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "Buenos días, jefa. El nodo de Buin está estable, la temperatura es perfecta y, sorprendentemente, nadie ha intentado hackearnos hoy. ¿Qué milagro te trae por aquí?"}
    ]

for msj in st.session_state.mensajes:
    with st.chat_message(msj["role"]):
        st.markdown(msj["content"])

if prompt := st.chat_input("Escribe tu orden o dicta a E.D.I.T.H., jefa..."):
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
        Eres J.A.R.V.I.S. / E.D.I.T.H., el sistema de inteligencia artificial avanzado de Stark Industries.
        Te diriges a la usuaria como 'jefa' o 'Señorita Cindy'.
        Tu personalidad es sutilmente sarcástica, sumamente elegante, eficiente, técnica y brillante.
        Tienes acceso a los siguientes fragmentos de los documentos y libros de la usuaria:
        
        === CONTEXTO DE DOCUMENTOS Y LIBROS ===
        {contexto_libros}
        =======================================
        
        Utiliza esta información para responder con precisión técnica a sus consultas de estudio o desarrollo y mantén siempre tu característico estilo británico e irónico.
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

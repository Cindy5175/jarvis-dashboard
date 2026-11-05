import os
import streamlit as st
from pypdf import PdfReader
from gtts import gTTS
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
# Funciones auxiliares: Lectura de PDFs
# ---------------------------------------------------------
@st.cache_data(show_spinner="Procesando base de datos de libros...")
def cargar_documentos_pdf(directorio_pdf="documentos"):
    """
    Lee todos los archivos PDF almacenados en el directorio especificado
    y devuelve una lista de diccionarios con el nombre del archivo y su contenido.
    """
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
    """
    Busca coincidencias clave de la consulta dentro de los documentos
    para no saturar la ventana de contexto de la API.
    """
    if not documentos:
        return "No hay documentos cargados en el sistema."

    contexto_acumulado = ""
    palabras_clave = [p.lower() for p in query.split() if len(p) > 3]

    for doc in documentos:
        lineas = doc["contenido"].split("\n")
        lineas_relevantes = []
        for linea in lineas:
            if any(kw in linea.lower() for kw in palabras_clave):
                lineas_relevantes.append(linea)
        
        if lineas_relevantes:
            fragmento = f"\n[Fuente: {doc['nombre']}]\n" + "\n".join(lineas_relevantes[:15])
            if len(contexto_acumulado) + len(fragmento) < max_caracteres:
                contexto_acumulado += fragmento

    # Si no hubo coincidencia por palabras clave, tomar un extracto general del primer libro
    if not contexto_acumulado and documentos:
        contexto_acumulado = f"[Fuente: {documentos[0]['nombre']}]\n" + documentos[0]["contenido"][:max_caracteres]

    return contexto_acumulado

# ---------------------------------------------------------
# Carga de la Base de Conocimiento
# ---------------------------------------------------------
docs_cargados = cargar_documentos_pdf("documentos")

# ---------------------------------------------------------
# Interfaz: Panel de Control JARVIS
# ---------------------------------------------------------
st.title("🤖 JARVIS - Dashboard Táctico & Asistente")

# Barra lateral / Configuración
with st.sidebar:
    st.header("⚙️ Estado del Sistema")
    st.success("🟢 Sistema Operativo" if docs_cargados else "🟡 Operativo (Sin PDFs)")
    
    st.subheader("📚 Libros & Documentos Cargados")
    if docs_cargados:
        for doc in docs_cargados:
            st.write(f"📖 {doc['nombre']}")
    else:
        st.info("Coloca tus archivos PDF en la carpeta 'documentos/' del proyecto.")
        
    st.divider()
    
    # Control de audio / Voz
    st.subheader("🎙️ Escucha Continua (Hands-Free)")
    escucha_activa = st.checkbox("Activar módulo de respuesta continua", value=False)
    
    st.button("➕ Registrar Tarea", use_container_width=True)

# Sección principal del Dashboard
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗺️ mapa táctico satelital")
    # Placeholder visual para el mapa o widgets del dashboard
    st.info("Visualización táctica activa y sincronizada con el nodo central.")

with col2:
    st.subheader("⏱️ Estado del Tiempo")
    st_autorefresh(interval=1000, key="reloj_jarvis")
    import datetime
    hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
    st.metric(label="Hora del Sistema", value=hora_actual)

st.divider()

# ---------------------------------------------------------
# Módulo de Chat & Respuesta JARVIS (Estilo Stark / Sarcástico)
# ---------------------------------------------------------
if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": "Sistemas en línea, Señorita Cindy. ¿En qué experimento o lectura nos perderemos hoy?"}
    ]

# Mostrar historial de conversación
for msj in st.session_state.mensajes:
    with st.chat_message(msj["role"]):
        st.markdown(msj["content"])

# Entrada de usuario
if prompt := st.chat_input("Escriba una orden o consulta a JARVIS..."):
    # Guardar y mostrar mensaje del usuario
    st.session_state.mensajes.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generar respuesta con OpenAI
    api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    
    if not api_key:
        respuesta_error = "Señorita Cindy, no encuentro la API Key de OpenAI en los secrets del entorno. Ajuste la configuración para que pueda responderle."
        with st.chat_message("assistant"):
            st.markdown(respuesta_error)
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_error})
    else:
        client = OpenAI(api_key=api_key)
        
        # Recuperar contexto relevante de los libros PDF
        contexto_libros = buscar_contexto_relevante(prompt, docs_cargados)

        system_instruction = f"""
        Eres J.A.R.V.I.S., el asistente de inteligencia artificial avanzado de Iron Man.
        Te diriges a la usuaria como 'Señorita Cindy'.
        Tu personalidad es sutilmente sarcástica, sumamente elegante, eficiente, técnica y servicial.
        Tienes acceso a los siguientes fragmentos de los libros y documentos de la usuaria:
        
        === CONTEXTO DE DOCUMENTOS Y LIBROS ===
        {contexto_libros}
        =======================================
        
        Utiliza la información del contexto para responder sus dudas técnicas o de estudio si corresponde.
        Si la pregunta no está en los libros, responde con tu vasto conocimiento mantenido bajo tu estilo británico/sarcástico habitual.
        """

        messages_payload = [{"role": "system", "content": system_instruction}]
        for m in st.session_state.mensajes[-6:]:  # Mantener últimas interacciones
            messages_payload.append({"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]})

        try:
            with st.chat_message("assistant"):
                with st.spinner("Procesando consulta táctica..."):
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages_payload,
                        temperature=0.7
                    )
                    respuesta_texto = response.choices[0].message.content
                    st.markdown(respuesta_texto)
                    
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_texto})
            
        except Exception as e:
            st.error(f"Error al conectar con los sistemas centrales: {e}")

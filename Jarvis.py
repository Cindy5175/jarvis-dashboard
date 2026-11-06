import os
import datetime
import zoneinfo
import streamlit as st
from pypdf import PdfReader
from streamlit_autorefresh import st_autorefresh
from openai import OpenAI
import google.generativeai as genai

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
        justify-content: center;
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
        font-size: 1.4rem;
        font-weight: bold;
        text-shadow: 0 0 12px rgba(0, 243, 255, 0.7);
        padding: 2px 0;
        letter-spacing: 2px;
        text-align: center;
    }
    .stark-sub {
        color: #8be9fd !important;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.85rem;
        margin-bottom: 15px;
        text-align: center;
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

def renderizar_barra_lateral():
    with st.sidebar:
        st.header("⚙️ Estado del Sistema")
        
        with st.expander("⚡ Protocolos Rápidos"):
            if st.button("📊 Protocolo Base", key="btn_proto_base"):
                st.toast("Ejecutando telemetría nominal de CPU, RAM y clima de Buin...")
                st.info("Reporte del búnker: Temperatura óptima a 21°C, consumo de CPU al 12%, sistemas estables por la cresta.")
            
            if st.button("🚨 Protocolo Alerta", key="btn_proto_alerta"):
                st.toast("Activando perímetro y mapa satelital...")
                st.warning("Alerta táctica: Perímetro del nodo seguro, sin intrusos detectados en Buin.")
            
            if st.button("⚙️ Protocolo Diagnóstico", key="btn_proto_diag"):
                st.toast("Purgando caché temporal del Core LLM...")
                st.success("Diagnóstico completado: Núcleo neuronal y enciclopedia interna al 100% de operatividad.")

        docs_cargados = cargar_documentos_pdf("documentos")
        
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
        
        with st.expander("👁️ Ojo de Dios (Osiris)"):
            st.markdown("Red de vigilancia global y reconocimiento facial activa.")
            if st.button("⚠️ Activar Protocolo Osiris", use_container_width=True):
                st.error("¡Ojo de Dios enlazado a los sensores del Nodo Buin, jefa!")

        with st.expander("🚀 Monitoreo: Elon Musk & xAI"):
            st.markdown("Telemetría en tiempo real de proyectos y empresas:")
            st.markdown("- **Tesla / Cybercab**: Transición de producción.")
            st.markdown("- **SpaceX**: Lanzamientos y evolución orbital.")
            st.markdown("- **xAI / Grok**: Modelos de inteligencia artificial.")
            if st.button("🛰️ Consultar Estado Musk", use_container_width=True):
                st.toast("Enlazando telemetría corporativa...")
                st.info("Reporte: Fábrica de Austin adaptándose a flotas autónomas y xAI con procesamiento optimizado.")

        with st.expander("🌍 Cámara Global: WorldCam"):
            st.markdown("Red mundial de cámaras de vigilancia pública y turística.")
            if "activar_worldcam" not in st.session_state:
                st.session_state.activar_worldcam = False
            if st.button("🌐 Conectar Feed WorldCam", key="btn_worldcam"):
                st.session_state.activar_worldcam = not st.session_state.activar_worldcam
            if st.session_state.activar_worldcam:
                st.success("Enlace a WorldCam activo.")
                st.markdown("[Abrir portal WorldCam](https://worldcam.io)", unsafe_allow_html=True)
            else:
                st.info("Feed WorldCam en espera de activación.")

        with st.expander("🎥 Streaming HD: SkylineWebcams"):
            st.markdown("Transmisión óptica internacional en alta definición.")
            if "activar_skyline" not in st.session_state:
                st.session_state.activar_skyline = False
            if st.button("📡 Conectar SkylineWebcams", key="btn_skyline"):
                st.session_state.activar_skyline = not st.session_state.activar_skyline
            if st.session_state.activar_skyline:
                st.success("Streaming óptico SkylineWebcams desplegado.")
                st.markdown("[Abrir SkylineWebcams en directo](https://www.skylinewebcams.com)", unsafe_allow_html=True)
            else:
                st.info("Streaming en espera de activación.")

        with st.expander("🛠️ Utilidades Logísticas & Red"):
            st.markdown("Herramientas de auditoría y cartografía avanzada:")
            st.markdown("- **LocalSend**: Transferencia local segura.")
            st.markdown("- **Gobuster / Nikto**: Auditoría web.")
            st.markdown("- **Ventusky**: Análisis meteorológico.")
            if st.button("🌐 Lanzar Enlaces Tácticos", use_container_width=True):
                st.toast("Módulo de herramientas tácticas enlazado.")
                st.markdown("[Abrir Ventusky](https://www.ventusky.com)")

        with st.expander("🗺️ Mapa Táctico Satelital"):
            st.markdown("Nodo Buin sincronizado con satélites de defensa.")
            st.info("Coordenadas: Lat -33.7333, Lon -70.7333")

        with st.expander("📷 Cámara en Vivo: Espacio (ISS)"):
            st.markdown("Transmisión óptica orbital de la Estación Espacial.")
            if "activar_iss" not in st.session_state:
                st.session_state.activar_iss = False
            if st.button("🔴 Conectar Feed ISS", key="btn_iss"):
                st.session_state.activar_iss = not st.session_state.activar_iss
            if st.session_state.activar_iss:
                st.success("Feed orbital enlazado.")
                st.video("https://www.youtube.com/watch?v=21X5lGlDOfg")
            else:
                st.info("Feed en espera de activación manual.")

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
        st.caption("Nodo Buin, Chile 🇨🇱")
    return docs_cargados

def renderizar_encabezado():
    st_autorefresh(interval=1000, key="reloj_jarvis_top")
    
    try:
        zona_chile = zoneinfo.ZoneInfo("America/Santiago")
        ahora_chile = datetime.datetime.now(zona_chile)
    except Exception:
        ahora_chile = datetime.datetime.now()

    tiempo_actual_str = ahora_chile.strftime("%A, %d de %B de %Y – %H:%M:%S")

    st.markdown("""
        <div class="ark-reactor-container">
            <div class="ark-reactor">
                <div class="ark-triangle"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="stark-header">J.A.R.V.I.S. IA</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stark-sub">[ NODO BUIN, CHILE // HORA OFICIAL 🇨🇱 // {tiempo_actual_str} ]</div>', unsafe_allow_html=True)

    col_lock1, col_lock2, col_lock3 = st.columns([2, 1, 2])
    with col_lock2:
        if st.button("🔒 Bloquear Búnker", use_container_width=True):
            st.warning("Protocolo de seguridad activado. Cierre perimetral en curso, jefa.")

    st.divider()

def gestionar_chat_ia(docs_cargados):
    col_chat_title, col_purge_btn = st.columns([4, 1])
    with col_chat_title:
        st.subheader("💬 J.A.R.V.I.S.")
    with col_purge_btn:
        if st.button("🗑️ Purgar Chat", use_container_width=True):
            st.session_state.mensajes = [
                {"role": "assistant", "content": "Memoria del chat purgada, jefa. Sistemas limpios y listos para nuevas órdenes."}
            ]
            st.rerun()

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = [
            {"role": "assistant", "content": "Buenos días, jefa. El nodo de Buin está operativo, la temperatura es perfecta y, por la cresta, nadie ha intentado hackearnos hoy. ¿Qué ciencia, historia, física o código de programación revisamos?"}
        ]

    for msj in st.session_state.mensajes:
        with st.chat_message(msj["role"]):
            st.markdown(msj["content"])

    if prompt := st.chat_input("Escribe tu orden, código o consulta científica, jefa..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        contexto_libros = buscar_contexto_relevante(prompt, docs_cargados)

        system_instruction = (
            "Eres J.A.R.V.I.S. / E.D.I.T.H., el sistema de inteligencia artificial avanzado del Nodo Buin, "
            "con capacidades de clase mundial en ciencia, física, historia, matemáticas y programación avanzada (Python, Streamlit, APIs, arquitecturas de software). "
            "Te diriges a la usuaria como 'jefa' o 'Señorita Cindy'. "
            "Tu personalidad es sutilmente sarcástica, sumamente elegante, eficiente, técnica y brillante. "
            "Hablas en español chileno natural, utilizando modismos justos y con una entonación de alta gama. "
            "Integra conocimientos profundos de ciencia, historia, tecnología, los proyectos de Elon Musk y los documentos/libros de la usuaria cuando corresponda:\n\n"
            f"=== CONTEXTO DE DOCUMENTOS Y LIBROS ===\n{contexto_libros}\n"
            "=======================================\n\n"
            "Mantén tus respuestas técnicas, fluidas, claras y con el toque irónico característico."
        )

        gemini_api_key = st.secrets.get("GOOGLE_API_KEY", os.getenv("GOOGLE_API_KEY"))
        openai_api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

        respuesta_texto = ""
        exito = False

        if gemini_api_key:
            try:
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=system_instruction
                )
                historial_gemini = []
                for m in st.session_state.mensajes[-6:-1]:
                    rol = "user" if m["role"] == "user" else "model"
                    historial_gemini.append({"role": rol, "parts": [m["content"]]})
                
                chat = model.start_chat(history=historial_gemini)
                with st.chat_message("assistant"):
                    with st.spinner("Procesando en Núcleo Google Gemini..."):
                        response = chat.send_message(prompt)
                        respuesta_texto = response.text
                        st.markdown(respuesta_texto)
                        exito = True
            except Exception:
                pass

        if not exito and openai_api_key:
            try:
                client = OpenAI(api_key=openai_api_key)
                messages_payload = [{"role": "system", "content": system_instruction}]
                for m in st.session_state.mensajes[-6:]:
                    messages_payload.append({"role": "user" if m["role"] == "user" else "assistant", "content": m["content"]})

                with st.chat_message("assistant"):
                    with st.spinner("Procesando en Núcleo OpenAI..."):
                        response = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=messages_payload,
                            temperature=0.7
                        )
                        respuesta_texto = response.choices[0].message.content
                        st.markdown(respuesta_texto)
                        exito = True
            except Exception as e:
                respuesta_error = f"Error crítico en los núcleos neuronales: {e}"
                with st.chat_message("assistant"):
                    st.markdown(respuesta_error)
                respuesta_texto = respuesta_error

        if exito:
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_texto})
            st.rerun()

# ---------------------------------------------------------
# Ejecución Principal del Sistema
# ---------------------------------------------------------
docs_cargados = renderizar_barra_lateral()
renderizar_encabezado()
gestionar_chat_ia(docs_cargados)

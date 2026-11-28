import os
import streamlit as st
from pypdf import PdfReader
from jarvis_brain import MODOS_CEREBRO, listar_modelos_ollama, responder_jarvis

st.session_state.setdefault("jarvis_chat", [])
st.session_state.setdefault("contexto_doc", "")

with st.sidebar:
    st.markdown("### Núcleo de Cerebro")
    motor = st.selectbox(
        "Motor de lenguaje",
        ["Híbrido (API con respaldo Ollama)", "API Nube (Gemini)", "Local (Ollama)"],
    )
    modo = st.selectbox("Perfil operativo", list(MODOS_CEREBRO.keys()))
    temperatura = st.slider("Creatividad / Precisión", 0.1, 1.0, 0.65, 0.05)

    gemini_key = st.text_input(
        "Gemini API Key",
        value=os.getenv("GEMINI_API_KEY", ""),
        type="password",
        help="También puedes definir GEMINI_API_KEY en tu entorno o st.secrets.",
    )
    gemini_modelo = st.selectbox(
        "Modelo Gemini",
        ["gemini-2.5-flash", "gemini-2.5-pro"],
    )

    ollama_url = st.text_input("URL Ollama", value="http://localhost:11434")
    modelos_locales = listar_modelos_ollama(ollama_url)
    ollama_modelo = st.selectbox(
        "Modelo Ollama local",
        modelos_locales if modelos_locales else ["llama3.1:8b", "qwen2.5:7b", "mistral"],
    )

    archivo_pdf = st.file_uploader("Cargar PDF de consulta (opcional)", type=["pdf"])
    if archivo_pdf is not None:
        lector = PdfReader(archivo_pdf)
        texto_pdf = "\n".join(pagina.extract_text() or "" for pagina in lector.pages)
        st.session_state.contexto_doc = texto_pdf
        st.caption(f"Documento cargado: {len(lector.pages)} páginas listas como contexto.")

for msg in st.session_state.jarvis_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("motor"):
            st.caption(f"Vía: {msg['motor']}")

prompt = st.chat_input("Háblale a Jarvis...")
if prompt:
    st.session_state.jarvis_chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    resultado = responder_jarvis(
        mensajes=st.session_state.jarvis_chat,
        motor=motor,
        gemini_api_key=gemini_key,
        gemini_modelo=gemini_modelo,
        ollama_modelo=ollama_modelo,
        ollama_url=ollama_url,
        modo=modo,
        contexto_extra=st.session_state.contexto_doc,
        temperatura=temperatura,
    )

    st.session_state.jarvis_chat.append(
        {
            "role": "assistant",
            "content": resultado["respuesta"],
            "motor": resultado["motor_usado"],
        }
    )
    with st.chat_message("assistant"):
        st.markdown(resultado["respuesta"])
        st.caption(f"Vía: {resultado['motor_usado']}")

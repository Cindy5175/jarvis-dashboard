import os
import io
import base64
import streamlit as st
from groq import Groq

# 1. Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S AI autónoma", 
    page_icon="⚛️", 
    layout="centered"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .neon-title {
        color: #00d2ff;
        text-shadow: 0 0 10px #00d2ff, 0 0 20px #00d2ff, 0 0 40px #0072ff;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 2.3rem;
        text-align: center;
        margin-top: -20px;
        margin-bottom: 25px;
    }
    .block-container {
        max-width: 750px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }
    .stChatInput {
        max-width: 750px;
        margin: 0 auto;
    }
    </style>
""", unsafe_allow_html=True)

# Encabezado centrado con Reactor Arc
st.markdown('<h1 class="neon-title">⚛️ J.A.R.V.I.S AI autónoma</h1>', unsafe_allow_html=True)

# 2. Conexión directa y segura con la API de Groq
groq_api_key = "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"

if not groq_api_key:
    st.error("⚠️ Error con la clave API.")
    st.stop()

client = Groq(api_key=groq_api_key)

# 3. Historial de chat en la sesión
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system", 
            "content": "Eres J.A.R.V.I.S., una super IA avanzada, brillante, lógica, cercana y leal. Te diriges al usuario siempre como 'Jefa' y respondes con un tono servicial, astuto y resolutivo."
        }
    ]

# 4. Sección desplegable para adjuntar archivos / imágenes
with st.expander("📎 Adjuntar archivo o imagen para análisis"):
    archivo_subido = st.file_uploader(
        "Carga una imagen (PNG, JPG, JPEG) o un archivo de texto/código (TXT, CSV, PY, MD):",
        type=["png", "jpg", "jpeg", "txt", "csv", "py", "md"]
    )

# Mostrar los mensajes anteriores (omitiendo la instrucción del sistema)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. Entrada de texto del usuario
if prompt := st.chat_input("Escribe tu instrucción o pregunta para J.A.R.V.I.S..."):
    
    # Procesar archivo si fue adjuntado
    contenido_adjunto = ""
    imagen_base64 = None
    
    if archivo_subido is not None:
        nombre_archivo = archivo_subido.name
        tipo_archivo = archivo_subido.type
        
        if "image" in tipo_archivo:
            bytes_data = archivo_subido.read()
            imagen_base64 = base64.b64encode(bytes_data).decode('utf-8')
            contenido_adjunto = f"\n\n[El usuario adjuntó la imagen: {nombre_archivo}]"
        else:
            try:
                texto_archivo = archivo_subido.read().decode("utf-8")
                contenido_adjunto = f"\n\n--- INICIO CONTENIDO DEL ARCHIVO '{nombre_archivo}' ---\n{texto_archivo}\n--- FIN CONTENIDO DEL ARCHIVO ---"
            except Exception:
                contenido_adjunto = f"\n\n[No se pudo leer el archivo '{nombre_archivo}' como texto plano.]"

    prompt_completo = prompt + contenido_adjunto

    # Guardar en el historial
    st.session_state.messages.append({"role": "user", "content": prompt_completo})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        if archivo_subido is not None:
            if "image" in archivo_subido.type:
                st.image(archivo_subido, caption=f"Imagen adjunta: {archivo_subido.name}", use_column_width=True)
            else:
                st.caption(f"📄 Archivo adjunto: {archivo_subido.name}")

    # Generar respuesta con la IA de Groq
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Selección de modelos (usando visió/multimodal si hay imagen)
        if imagen_base64:
            modelos_candidatos = [
                "llama-3.2-11b-vision-preview",
                "llama-3.2-90b-vision-preview"
            ]
            # Construir estructura especial para mensajes con imágenes
            mensajes_api = []
            for msg in st.session_state.messages:
                if msg["role"] == "system":
                    mensajes_api.append(msg)
                elif msg["role"] == "user":
                    if msg == st.session_state.messages[-1]:
                        mensajes_api.append({
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_completo},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{archivo_subido.type};base64,{imagen_base64}"
                                    }
                                }
                            ]
                        })
                    else:
                        mensajes_api.append(msg)
                else:
                    mensajes_api.append(msg)
        else:
            modelos_candidatos = [
                "openai/gpt-oss-120b",
                "openai/gpt-oss-20b",
                "qwen/qwen3.8-27b",
                "meta-llama/llama-4-maverick-17b-128e-instruct"
            ]
            mensajes_api = st.session_state.messages

        exito = False
        for modelo_actual in modelos_candidatos:
            try:
                completion = client.chat.completions.create(
                    model=modelo_actual,
                    messages=mensajes_api,
                    stream=True,
                )
                
                for chunk in completion:
                    content = chunk.choices[0].delta.content or ""
                    full_response += content
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                exito = True
                break
            except Exception:
                continue
        
        if not exito:
            full_response = "Lo siento, Jefa. Tuve un inconveniente al procesar el archivo o comunicarme con los motores centrales."
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

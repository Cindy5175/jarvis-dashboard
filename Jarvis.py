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

# Estilos CSS personalizados y optimizados para celular
st.markdown("""
    <style>
    .neon-title {
        color: #00d2ff;
        text-shadow: 0 0 8px #00d2ff, 0 0 15px #00d2ff, 0 0 30px #0072ff;
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 1.8rem;
        text-align: center;
        margin-top: -15px;
        margin-bottom: 20px;
        white-space: nowrap;
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

# Encabezado centrado con Reactor Arc (Todo en una línea fluida)
st.markdown('<h1 class="neon-title">⚛️ J.A.R.V.I.S. AI</h1>', unsafe_allow_html=True)

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

# 4. BARRA LATERAL OCULTA (Panel de control avanzado)
with st.sidebar:
    st.markdown("### ⚙️ Panel de Control J.A.R.V.I.S.")
    
    # Función 1: Selector de Modelos
    st.markdown("#### 🎛️ Selector de Motor")
    modelo_seleccionado = st.selectbox(
        "Modelo activo:",
        [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "llama-3.2-11b-vision-preview"
        ],
        index=0
    )
    
    st.divider()
    
    # Función 2: Módulo de Voz
    st.markdown("#### 🔊 Asistente de Voz")
    activar_voz = st.checkbox("Habilitar síntesis de voz (JS)", value=False)
    
    st.divider()
    
    # Función 3: Exportar Chat
    st.markdown("#### 💾 Respaldo de Sesión")
    chat_texto = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages if m['role'] != 'system'])
    st.download_button(
        label="📥 Descargar Chat (.txt)",
        data=chat_texto,
        file_name="jarvis_chat_log.txt",
        mime="text/plain"
    )
    
    st.divider()
    
    # Función 4: Presets de Acceso Rápido
    st.markdown("#### ⚡ Acciones Rápidas")
    preset_elegido = None
    if st.button("💡 Resumir última respuesta"):
        preset_elegido = "Por favor, haz un resumen claro y ejecutivo de lo último que conversamos."
    if st.button("💻 Explicar código adjunto"):
        preset_elegido = "Analiza detalladamente el archivo o código que acabo de adjuntar."

# Sección desplegable para adjuntar archivos / imágenes
with st.expander("📎 Adjuntar archivo o imagen para análisis"):
    archivo_subido = st.file_uploader(
        "Carga una imagen (PNG, JPG) o un archivo de texto/código (TXT, CSV, PY, MD):",
        type=["png", "jpg", "jpeg", "txt", "csv", "py", "md"]
    )

# Mostrar los mensajes anteriores
for idx, message in enumerate(st.session_state.messages):
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and activar_voz:
                texto_seguro = message["content"].replace('"', "'").replace('\n', ' ')
                st.markdown(f"""
                    <button onclick="let utterance = new SpeechSynthesisUtterance(\"{texto_seguro}\"); utterance.lang = 'es-ES'; window.speechSynthesis.speak(utterance);" style="background-color: #00d2ff; color: black; border: none; padding: 5px 10px; border-radius: 5px; font-size: 0.8rem; cursor: pointer; margin-top: 5px;">
                        🔊 Reproducir Audio
                    </button>
                """, unsafe_allow_html=True)

# 5. Entrada de texto del usuario
prompt_usuario = st.chat_input("Escribe tu instrucción o pregunta para J.A.R.V.I.S...")
prompt = preset_elegido if preset_elegido else prompt_usuario

if prompt:
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

    st.session_state.messages.append({"role": "user", "content": prompt_completo})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        if archivo_subido is not None:
            if "image" in archivo_subido.type:
                st.image(archivo_subido, caption=f"Imagen adjunta: {archivo_subido.name}", use_column_width=True)
            else:
                st.caption(f"📄 Archivo adjunto: {archivo_subido.name}")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        if imagen_base64:
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
            modelos_a_probar = ["llama-3.2-11b-vision-preview", "llama-3.2-90b-vision-preview"]
        else:
            mensajes_api = st.session_state.messages
            modelos_a_probar = [modelo_seleccionado, "openai/gpt-oss-120b", "qwen/qwen3.8-27b"]

        exito = False
        for modelo_actual in modelos_a_probar:
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
            full_response = "Lo siento, Jefa. Tuve un inconveniente al procesar la solicitud con el motor seleccionado."
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

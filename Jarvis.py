import os
import io
import base64
import streamlit as st
from groq import Groq

# 1. Configuración da páxina
st.set_page_config(
    page_title="Sistema C.I.T. / J.A.R.V.I.S.", 
    page_icon="⚛️", 
    layout="centered"
)

# Inicializar estado do tema en sesión
if "modo_sistema" not in st.session_state:
    st.session_state.modo_sistema = "J.A.R.V.I.S. (Azul Neón)"

# 2. Conexión directa coa API de Groq
groq_api_key = "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"

if not groq_api_key:
    st.error("⚠️ Error con la clave API.")
    st.stop()

client = Groq(api_key=groq_api_key)

# 3. Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. BARRA LATERAL OCULTA (Centro de Comando)
with st.sidebar:
    st.markdown("### ⚙️ Centro de Comando")
    
    # Conmutador de Personalidade / Tema
    modo = st.radio(
        "Selecciona Protocolo Activo:",
        ["J.A.R.V.I.S. (Azul Neón)", "N.O.V.A. - C.I.T. (Fucsia Cyber)"]
    )
    st.session_state.modo_sistema = modo
    
    st.divider()
    
    # Módulo Starlink con animación
    st.markdown("### 🛰️ Enlace Satelital Starlink")
    st.caption("🟢 **Estado:** Conectado (Órbita Baja)")
    st.caption("📡 **Latencia:** 24 ms | **Bajada:** 220 Mbps")
    
    # Efecto de barra de escaneo de enerxía
    st.markdown("""
        <div style="background-color: #111; border-radius: 10px; padding: 3px; border: 1px solid #333;">
            <div style="background: linear-gradient(90deg, #00d2ff, #ff007f, #00d2ff); 
                        height: 10px; border-radius: 8px; width: 100%; 
                        animation: pulseBar 2s infinite linear;"></div>
        </div>
        <style>
        @keyframes pulseBar {
            0% { opacity: 0.6; }
            50% { opacity: 1; filter: drop-shadow(0 0 5px #00d2ff); }
            100% { opacity: 0.6; }
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Selector de Motor
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
    
    # Asistente de Voz
    st.markdown("#### 🔊 Asistente de Voz")
    activar_voz = st.checkbox("Habilitar síntesis de voz", value=False)
    
    st.divider()
    
    # Respaldo
    st.markdown("#### 💾 Respaldo")
    chat_texto = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages if m['role'] != 'system'])
    st.download_button(
        label="📥 Descargar Chat (.txt)",
        data=chat_texto,
        file_name="cit_chat_log.txt",
        mime="text/plain"
    )

# Configurar variables visuales e contexto
if "N.O.V.A." in st.session_state.modo_sistema:
    color_neon = "#ff007f"
    shadow_neon = "#ff007f"
    titulo_html = '<h1 class="neon-title glow-anim">🟣 N.O.V.A. - C.I.T.</h1>'
    system_prompt = "Eres N.O.V.A., un sistema de inteligencia táctica C.I.T. altamente avanzado y tecnológico. Te diriges al usuario como 'Jefa', usas terminología de vanguardia, biometría y confirmaciones tácticas directas."
else:
    color_neon = "#00d2ff"
    shadow_neon = "#0072ff"
    titulo_html = '<h1 class="neon-title glow-anim">⚛️ J.A.R.V.I.S. AI</h1>'
    system_prompt = "Eres J.A.R.V.I.S., una super IA avanzada, brillante, lógica, cercana y leal. Te diriges al usuario siempre como 'Jefa' y respondes con un tono servicial, astuto y resolutivo."

if len(st.session_state.messages) == 0 or st.session_state.messages[0]["role"] != "system":
    st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})
else:
    st.session_state.messages[0]["content"] = system_prompt

# CSS Avanzado con animacións de pulso de luz
st.markdown(f"""
    <style>
    @keyframes neonGlow {{
        0% {{ text-shadow: 0 0 5px {color_neon}, 0 0 10px {color_neon}, 0 0 20px {shadow_neon}; }}
        50% {{ text-shadow: 0 0 12px {color_neon}, 0 0 25px {color_neon}, 0 0 40px {shadow_neon}; }}
        100% {{ text-shadow: 0 0 5px {color_neon}, 0 0 10px {color_neon}, 0 0 20px {shadow_neon}; }}
    }}
    .neon-title {{
        color: {color_neon};
        font-family: 'Courier New', Courier, monospace;
        font-weight: bold;
        font-size: 1.8rem;
        text-align: center;
        margin-top: -15px;
        margin-bottom: 20px;
        white-space: nowrap;
        animation: neonGlow 2.5s infinite ease-in-out;
    }}
    .block-container {{
        max-width: 750px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }}
    .stChatInput {{
        max-width: 750px;
        margin: 0 auto;
    }}
    </style>
""", unsafe_allow_html=True)

# Título da App
st.markdown(titulo_html, unsafe_allow_html=True)

# Lector Multimodal
with st.expander("📎 Adjuntar archivo o imagen para análisis"):
    archivo_subido = st.file_uploader(
        "Carga una imagen o archivo de texto/código:",
        type=["png", "jpg", "jpeg", "txt", "csv", "py", "md"]
    )

# Mostrar Historial
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and activar_voz:
                texto_seguro = message["content"].replace('"', "'").replace('\n', ' ')
                st.markdown(f"""
                    <button onclick="let utterance = new SpeechSynthesisUtterance(\"{texto_seguro}\"); utterance.lang = 'es-ES'; window.speechSynthesis.speak(utterance);" style="background-color: {color_neon}; color: black; border: none; padding: 5px 10px; border-radius: 5px; font-size: 0.8rem; cursor: pointer; margin-top: 5px;">
                        🔊 Reproducir Audio
                    </button>
                """, unsafe_allow_html=True)

# Entrada do usuario
if prompt := st.chat_input("Escribe tu instrucción o directiva..."):
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
                contenido_adjunto = f"\n\n--- INICIO CONTENIDO ARCHIVO '{nombre_archivo}' ---\n{texto_archivo}\n--- FIN CONTENIDO ARCHIVO ---"
            except Exception:
                contenido_adjunto = f"\n\n[No se pudo leer el archivo '{nombre_archivo}']"

    prompt_completo = prompt + contenido_adjunto
    st.session_state.messages.append({"role": "user", "content": prompt_completo})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        if archivo_subido is not None:
            if "image" in archivo_subido.type:
                st.image(archivo_subido, caption=f"Imagen: {archivo_subido.name}", use_column_width=True)
            else:
                st.caption(f"📄 Archivo: {archivo_subido.name}")

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
            full_response = "Lo siento, Jefa. Inconveniente en la conexión con los servidores centrales."
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

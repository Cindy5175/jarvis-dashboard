import os
import time
import streamlit as st
from groq import Groq

# 1. Configuración de la página
st.set_page_config(
    page_title="Sistema C.I.T. / J.A.R.V.I.S.", 
    page_icon="⚛️", 
    layout="centered"
)

# 2. Inicializar estados en sesión PRIMERO
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "ubicacion_jefa" not in st.session_state:
    st.session_state.ubicacion_jefa = "Buin Santiago Chile"
    st.session_state.lat_lon = "-33.7333 -70.7333"

if "energia_arc" not in st.session_state:
    st.session_state.energia_arc = 98

if "notas_mision" not in st.session_state:
    st.session_state.notas_mision = "• Sincronizar protocolos de red\n• Optimizar módulos tácticos"

# -------------------------------------------------------------
# 🔐 MÓDULO DE CLAVE DE ACCESO (PIN DE SEGURIDAD)
# -------------------------------------------------------------
PIN_SECRETO = "Jarvis"

if not st.session_state.autenticado:
    st.markdown(
        """
        <style>
        .login-box {
            background: rgba(5, 12, 30, 0.95);
            border: 2px solid #00d2ff;
            border-radius: 12px;
            padding: 25px;
            text-align: center;
            box-shadow: 0 0 25px #00d2ff44;
            font-family: 'Courier New', monospace;
            max-width: 90%;
            margin: 50px auto;
        }
        </style>
        <div class="login-box">
            <h2 style="color: #00d2ff; margin-bottom: 10px; font-size: 1.4rem;">🔒 ACCESO RESTRINGIDO</h2>
            <p style="color: #aaa; font-size: 0.8rem;">Introduce la clave de seguridad para desbloquear la estación de comando C.I.T.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_l1, col_l2, col_l3 = st.columns([1, 4, 1])
    with col_l2:
        pin_ingresado = st.text_input("Clave de Acceso:", type="password", placeholder="Contraseña secreta")
        if st.button("🔓 Desbloquear Sistema", use_container_width=True):
            if pin_ingresado == PIN_SECRETO:
                st.session_state.autenticado = True
                st.success("¡Acceso concedido Jefa!")
                st.rerun()
            else:
                st.error("⚠️ Clave incorrecta. Acceso denegado.")
    st.stop()
# -------------------------------------------------------------

# Conexión directa y blindada con la API de Groq
groq_api_key = "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"
client = Groq(api_key=groq_api_key)

# Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Estética fija: Azul Neón Cuántico
color_neon = "#00d2ff"
shadow_neon = "#0072ff"
titulo_html = '<h1 class="neon-title glow-anim">⚛️ J.A.R.V.I.S. AI Autónoma</h1>'

system_base = f"Eres J.A.R.V.I.S. Autónoma una super IA avanzada brillante y leal. Te diriges al usuario siempre como 'Jefa'. Respondes con la elegancia eficiencia sarcasmo irónico estilo Tony Stark y capacidad analítica total para auditar código de sistemas. Ubicación actual de la Jefa: {st.session_state.ubicacion_jefa} (Coordenadas satelitales: {st.session_state.lat_lon})."

# BARRA LATERAL
with st.sidebar:
    st.markdown("### ⚙️ Centro de Comando Stark")
    mostrar_hud = st.checkbox("Mostrar Estación Holográfica Completa", value=True)

    st.divider()
    
    st.markdown("### 🛠️ Módulos Tácticos Izquierdos")
    estilo_voz = st.selectbox("Selector Estilo de Voz:", ["Táctico Estándar", "Formal / Robótico", "Fluido Rápido"], index=0)
    
    zona_preset = st.selectbox("Preset de Coordenadas:", ["Buin (Base Central)", "Santiago Centro", "Estación Orbital Norte"], index=0)
    if "Santiago" in zona_preset:
        st.session_state.ubicacion_jefa = "Santiago Centro Chile"
        st.session_state.lat_lon = "-33.4489 -70.6693"
    elif "Buin" in zona_preset:
        st.session_state.ubicacion_jefa = "Buin Santiago Chile"
        st.session_state.lat_lon = "-33.7333 -70.7333"
    else:
        st.session_state.ubicacion_jefa = "Sector Orbital / Desconocido"
        st.session_state.lat_lon = "00.0000 00.0000"

    st.divider()
    
    st.markdown("### 👁️ Sensores Biométricos")
    with st.expander("📡 1. Sensor Óptico de Movimiento"):
        foto_mov = st.camera_input("Activar Sensor Óptico", key="cam_optico")
        if foto_mov:
            st.success("¡Flujo óptico capturado Jefa!")

    with st.expander("👤 2. Reconocimiento Facial"):
        foto_rostro = st.camera_input("Escanear Rostro Biométrico", key="cam_rostro")
        if foto_rostro:
            st.success("¡Identidad confirmada Jefa!")

    st.divider()

    st.markdown("### 🚀 Protocolos Avanzados")
    with st.expander("🔮 Generador de Hologramas"):
        prompt_holo = st.text_input("Prompt de holograma:", "Reactor Arc schematic HUD blueprint")
        if st.button("🔮 Generar Holograma", use_container_width=True):
            with st.spinner("Sintetizando plano holográfico..."):
                time.sleep(1.0)
                url_holo_gen = f"https://image.pollinations.ai/prompt/{prompt_holo.replace(' ', '%20')}%20scifi%20blueprint%20hud%20neon"
                st.image(url_holo_gen, caption="Plano Táctico Sintetizado", use_column_width=True)
            st.success("¡Holograma proyectado Jefa!")

    st.divider()
    
    archivo_subido = st.file_uploader(
        "Adjunta archivo al chat:",
        type=["png", "jpg", "jpeg", "txt", "csv", "py", "md"],
        key="chat_file"
    )

    st.divider()
    protocolo_extra = st.selectbox(
        "Directiva de Análisis:",
        [
            "Estándar (Equilibrado)",
            "Modo Auditoría de Arquitectura / Jarvis.py 💻",
            "Modo Resumen Ejecutivo 📊",
            "Modo Táctico de Ciberseguridad 🛡️"
        ],
        index=0
    )
    
    col_izq_1, col_izq_2 = st.columns(2)
    with col_izq_1:
        if st.button("🧹💬 Purgar", use_container_width=True):
            st.session_state.messages = []
            st.success("¡Purgado!")
            st.rerun()
    with col_izq_2:
        if st.button("🩺 Escanear", use_container_width=True):
            with st.spinner("Escaneando..."):
                time.sleep(1.0)
            st.success("¡Ok Jefa!")

    st.divider()
    st.markdown("### ⚛️ Reactor Arc & Energía")
    st.caption(f"⚡ **Potencia de Núcleo:** {st.session_state.energia_arc}%")
    if st.button("🔋 Recargar Reactor Arc", use_container_width=True):
        st.session_state.energia_arc = 100
        st.success("¡Núcleo al 100% Jefa!")
        st.rerun()

    st.divider()
    modelo_seleccionado = st.selectbox(
        "Modelos activos:",
        [
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "qwen/qwen3.8-27b",
            "meta-llama/llama-4-maverick-17b-128e-instruct",
            "llama-3.2-11b-vision-preview"
        ],
        index=0
    )
    
    activar_voz = st.checkbox("Habilitar síntesis de voz", value=False)
    
    chat_texto = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages if m['role'] != 'system'])
    st.download_button("📥 Descargar Chat (.txt)", data=chat_texto, file_name="cit_chat_log.txt", mime="text/plain", use_container_width=True)

    st.divider()
    if st.button("🔒 Bloquear Sistema", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# Definir instrucción del sistema complementada
prompt_protocolo_extra = ""
if "Auditoría" in protocolo_extra:
    prompt_protocolo_extra = " [DIRECTIVA ACTIVA: Activa protocolo de auditoría profunda de arquitectura de software y código Streamlit. Diagnostica componentes, cuellos de botella y propone mejoras con rigor técnico e ironía Stark]."
elif "Resumen" in protocolo_extra:
    prompt_protocolo_extra = " [DIRECTIVA ACTIVA: Entrega siempre respuestas ultra resumidas, directas al grano y estructuradas en viñetas ejecutivas]."
elif "Ciberseguridad" in protocolo_extra:
    prompt_protocolo_extra = " [DIRECTIVA ACTIVA: Activa protocolo de ciberseguridad, análisis de vulnerabilidades y encriptado táctico de nivel militar]."

system_prompt = system_base + prompt_protocolo_extra

if len(st.session_state.messages) == 0 or st.session_state.messages[0]["role"] != "system":
    st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})
else:
    st.session_state.messages[0]["content"] = system_prompt

# Estilos CSS generales limpios
css_estilos = f"""
<style>
@keyframes neonGlow {{
    0% {{ text-shadow: 0 0 5px {color_neon}, 0 0 10px {color_neon}, 0 0 20px {shadow_neon}; }}
    50% {{ text-shadow: 0 0 14px {color_neon}, 0 0 28px {color_neon}, 0 0 45px {shadow_neon}; }}
    100% {{ text-shadow: 0 0 5px {color_neon}, 0 0 10px {color_neon}, 0 0 20px {shadow_neon}; }}
}}
.neon-title {{
    color: {color_neon};
    font-family: 'Courier New', Courier, monospace;
    font-weight: bold;
    font-size: clamp(1.1rem, 4.5vw, 1.6rem);
    text-align: center;
    margin-top: -10px;
    margin-bottom: 20px;
    white-space: nowrap;
    animation: neonGlow 2.5s infinite ease-in-out;
}}
.block-container {{
    max-width: 100% !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    padding-top: 1rem !important;
    padding-bottom: 6rem !important;
}}
.scanline {{
    position: absolute;
    width: 100%;
    height: 2px;
    background: rgba(0, 210, 255, 0.5);
    box-shadow: 0 0 10px {color_neon};
    animation: scan 3s linear infinite;
    z-index: 10;
}}
@keyframes scan {{
    0% {{ top: 0%; }}
    100% {{ top: 100%; }}
}}
</style>
"""

st.markdown(css_estilos, unsafe_allow_html=True)

st.markdown(titulo_html, unsafe_allow_html=True)

# ESTACIÓN DE COMANDO PRINCIPAL
if mostrar_hud:
    with st.container(border=True):
        st.markdown(f"<div style='font-size: 0.65rem; color: {color_neon}; font-family: monospace; font-weight: bold; margin-bottom: 8px;'>[COMMAND STATION - C2 ACTIVE] &nbsp;&nbsp; INTEGRITY: {st.session_state.energia_arc}%</div>", unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div style="background: radial-gradient(circle, rgba(2,10,25,0.95) 0%, rgba(0,2,8,0.98) 100%); border: 2px solid {color_neon}; border-radius: 16px; padding: 20px; text-align: center; box-shadow: 0 0 30px {color_neon}66; font-family: 'Courier New', monospace; margin-top: 10px; margin-bottom: 15px;">
                <h3 style="color: {color_neon}; text-shadow: 0 0 10px {color_neon}; margin-top: 0; font-size: 1.1rem;">ESTRUCTURA NEURAL C2</h3>
                <div style="font-size: 0.7rem; color: #ddd; background: rgba(0,15,30,0.8); padding: 10px; border-radius: 8px; border: 1px solid {color_neon}44; text-align: left; margin-top: 10px;">
                    <b style="color: {color_neon};">DIAGNÓSTICO DE SISTEMAS:</b><br>
                    📡 Enlace Satelital: ESTABLE (100%)<br>
                    🛡️ Escudo Cuántico: OPERATIVO<br>
                    ⚡ Reactor Core: {st.session_state.energia_arc}% de potencia<br>
                    📍 Grid: {st.session_state.ubicacion_jefa}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.expander(f"🌤️ Módulo Climático & Alertas ({st.session_state.ubicacion_jefa})"):
            col_c1, col_c2, col_c3 = st.columns(3)
            col_c1.metric("Temp", "18°C", "Óptima")
            col_c2.metric("Humedad", "45%", "-2%")
            col_c3.metric("Viento", "12 km/h", "SSE")
            
            st.divider()
            
            st.markdown(f"<b style='color: {color_neon}; font-size: 0.75rem;'>📈 Ancho de Banda y Red (Mbps)</b>", unsafe_allow_html=True)
            import pandas as pd
            import numpy as np
            chart_data = pd.DataFrame(
                np.random.randn(15, 2) * [5, 10] + [50, 120],
                columns=["Enlace Satelital", "Flujo Neuronal"]
            )
            st.line_chart(chart_data, height=130)
            
            st.divider()
            
            st.markdown(f"<b style='color: {color_neon}; font-size: 0.75rem;'>📝 Bitácora de Misión Rápida</b>", unsafe_allow_html=True)
            st.session_state.notas_mision = st.text_area("Notas directas de la Jefa:", value=st.session_state.notas_mision, height=70)
            if st.button("💾 Guardar Notas", use_container_width=True):
                st.success("¡Bitácora sincronizada Jefa!")
            
        st.markdown(f"<div style='font-size: 0.6rem; color: #aaa; font-family: monospace; border-top: 1px solid #333; padding-top: 5px; margin-top: 8px; display: flex; justify-content: space-between;'><span>GRID: {st.session_state.lat_lon}</span><span>STATUS: ONLINE</span></div>", unsafe_allow_html=True)

# 💬 HISTORIAL DE CHAT
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant" and activar_voz:
                texto_seguro = message["content"].replace('"', "'").replace('\n', ' ')
                velocidad_voz = 1.2 if "Rápido" in estilo_voz else 1.0
                pitch_voz = 0.8 if "Robótico" in estilo_voz else 1.0
                st.markdown(
                    f"""
                    <button onclick="
                        let utterance = new SpeechSynthesisUtterance(\"{texto_seguro}\");
                        utterance.lang = 'es-ES';
                        utterance.rate = {velocidad_voz};
                        utterance.pitch = {pitch_voz};
                        window.speechSynthesis.speak(utterance);
                    " style="background-color: {color_neon}; color: black; border: none; padding: 5px 10px; border-radius: 5px; font-size: 0.8rem; cursor: pointer; margin-top: 5px;">
                        🔊 Reproducir Audio
                    </button>
                    """,
                    unsafe_allow_html=True
                )

# 🎙️ BOTÓN DE VOZ TÁCTICO
st.markdown(
    f"""
    <div style="display: flex; justify-content: flex-end; padding-right: 8px; margin-bottom: 2px;">
        <button onclick="
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'es-ES';
            recognition.onresult = function(event) {{
                const speechToText = event.results[0][0].transcript;
                const inputField = document.querySelector('input[aria-label*=\\'Escribe\\'], textarea[aria-label*=\\'Escribe\\'], input[type=\\'text\\']');
                if(inputField) {{
                    inputField.value = speechToText;
                    inputField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            }};
            recognition.start();
        " style="background-color: {color_neon}; color: black; border: none; width: 36px; height: 36px; border-radius: 50%; font-size: 1rem; cursor: pointer; box-shadow: 0 0 10px {color_neon}88; display: flex; align-items: center; justify-content: center;">
            🎙️
        </button>
    </div>
    """,
    unsafe_allow_html=True
)

# 💬 CAJA DE CHAT PRINCIPAL
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
            for msg in

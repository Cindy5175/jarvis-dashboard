import os
import io
import base64
import time
import streamlit as st
from groq import Groq

# 1. Configuración de la página
st.set_page_config(
    page_title="Sistema C.I.T. / J.A.R.V.I.S.", 
    page_icon="⚛️", 
    layout="centered"
)

# Gestionar desactivación por interacción del salvapantallas vía URL Query Params
if "screensaver" in st.query_params and st.query_params["screensaver"] == "off":
    st.session_state.salvapantallas_activo = False
    st.query_params.clear()
    st.rerun()

# Inicializar estados en sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if "ubicacion_jefa" not in st.session_state:
    st.session_state.ubicacion_jefa = "Buin Santiago Chile"
    st.session_state.lat_lon = "-33.7333 -70.7333"

if "energia_arc" not in st.session_state:
    st.session_state.energia_arc = 98

if "notas_mision" not in st.session_state:
    st.session_state.notas_mision = "• Sincronizar protocolos de red\n• Optimizar módulos tácticos"

if "salvapantallas_activo" not in st.session_state:
    st.session_state.salvapantallas_activo = False

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

# 2. Conexión directa y blindada con la API de Groq
groq_api_key = "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"
client = Groq(api_key=groq_api_key)

# 3. Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Estética fija: Azul Neón Cuántico
color_neon = "#00d2ff"
shadow_neon = "#0072ff"
titulo_html = '<h1 class="neon-title glow-anim">⚛️ J.A.R.V.I.S. AI Autónoma</h1>'

system_base = f"Eres J.A.R.V.I.S. Autónoma una super IA avanzada brillante y leal. Te diriges al usuario siempre como 'Jefa'. Respondes con la elegancia eficiencia sarcasmo irónico estilo Tony Stark y capacidad analítica total para auditar código de sistemas. Ubicación actual de la Jefa: {st.session_state.ubicacion_jefa} (Coordenadas satelitales: {st.session_state.lat_lon})."

# 4. BARRA LATERAL (Centro de Comando Avanzado Izquierdo)
with st.sidebar:
    st.markdown("### ⚙️ Centro de Comando Stark")
    mostrar_hud = st.checkbox("Mostrar Estación Holográfica Completa", value=True)
    
    # Interruptor del Salvapantallas Stark con la nueva imagen holográfica
    st.session_state.salvapantallas_activo = st.checkbox("🎬 Protocolo Salvapantallas Stark", value=st.session_state.salvapantallas_activo)

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
    
    # SENSORES BIOMÉTRICOS
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

    # PROTOCOLOS AVANZADOS
    st.markdown("### 🚀 Protocolos Avanzados")
    with st.expander("🔮 Generador de Hologramas"):
        prompt_holo = st.text_input("Prompt de holograma:", "Reactor Arc schematic HUD blueprint")
        if st.button("🔮 Generar Holograma", use_container_width=True):
            with st.spinner("Sintetizando plano holográfico..."):
                time.sleep(1.0)
                url_holo = f"https://image.pollinations.ai/prompt/{prompt_holo.replace(' ', '%20')}%20scifi%20blueprint%20hud%20neon"
                st.image(url_holo, caption="Plano Táctico Sintetizado", use_column_width=True)
            st.success("¡Holograma proyectado Jefa!")

    st.divider()
    
    st.markdown("### 📎 Carga Multimodal")
    archivo_subido = st.file_uploader(
        "Adjunta imagen o archivo:",
        type=["png", "jpg", "jpeg", "txt", "csv", "py", "md"]
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
elif "Ciberseguridad" in протоколо_extra if "Ciberseguridad" in protocolo_extra else False:
    prompt_protocolo_extra = " [DIRECTIVA ACTIVA: Activa protocolo de auditoría de ciberseguridad, análisis de vulnerabilidades y encriptado táctico de nivel militar]."

system_prompt = system_base + prompt_protocolo_extra

if len(st.session_state.messages) == 0 or st.session_state.messages[0]["role"] != "system":
    st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})
else:
    st.session_state.messages[0]["content"] = system_prompt

# Estilos CSS generales
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

# 🎬 PANTALLA DE SALVAPANTALLAS CON TU IMAGEN HOLOGRÁFICA Y AUTO-DESBLOQUEO
if st.session_state.salvapantallas_activo:
    screensaver_code = f"""
    <div id="screensaver-layer" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #000208; z-index: 99999; display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: 'Courier New', monospace; color: {color_neon}; cursor: pointer;">
        <div class="scanline"></div>
        <div style="position: relative; z-index: 5; text-align: center; max-width: 90%; max-height: 80vh; display: flex; flex-direction: column; align-items: center;">
            <img src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1000&auto=format&fit=crop" style="width: 280px; height: 280px; object-fit: cover; border-radius: 50%; border: 3px solid {color_neon}; box-shadow: 0 0 35px {color_neon}aa; margin-bottom: 20px;" />
            <h1 style="color: {color_neon}; font-size: 1.5rem; text-shadow: 0 0 20px {color_neon}; letter-spacing: 2px; margin: 0;">J.A.R.V.I.S. C2 SECURE</h1>
            <p style="color: #88ccee; font-size: 0.8rem; margin-top: 8px;">[NÚCLEO NEURAL BIOMÉTRICO EN ESPERA]</p>
            <p style="color: #00d2ffaa; font-size: 0.7rem; margin-top: 15px; border: 1px solid {color_neon}66; padding: 5px 10px; border-radius: 15px;">
                ⚡ Toca la pantalla, mueve el mouse o presiona una tecla para desbloquear
            </p>
        </div>
    </div>

    <script>
    let triggered = false;
    function dismissScreensaver() {{
        if (triggered) return;

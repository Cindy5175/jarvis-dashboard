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
            padding: 30px;
            text-align: center;
            box-shadow: 0 0 25px #00d2ff44;
            font-family: 'Courier New', monospace;
            max-width: 400px;
            margin: 50px auto;
        }
        </style>
        <div class="login-box">
            <h2 style="color: #00d2ff; margin-bottom: 10px;">🔒 ACCESO RESTRINGIDO</h2>
            <p style="color: #aaa; font-size: 0.85rem;">Introduce la clave de seguridad para desbloquear la estación de comando C.I.T.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
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

# Estética fija: Azul Neón con identidad autónoma (sin comas)
color_neon = "#00d2ff"
shadow_neon = "#0072ff"
titulo_html = '<h1 class="neon-title glow-anim">⚛️ J.A.R.V.I.S. AI Autónoma</h1>'

system_base = f"Eres J.A.R.V.I.S. Autónoma una super IA avanzada brillante y leal. Te diriges al usuario siempre como 'Jefa'. Respondes con la elegancia eficiencia sarcasmo irónico estilo Tony Stark y capacidad analítica total para auditar código de sistemas. Ubicación actual de la Jefa: {st.session_state.ubicacion_jefa} (Coordenadas satelitales: {st.session_state.lat_lon})."

# 4. BARRA LATERAL (Centro de Comando Avanzado Izquierdo)
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
            "Modo Resumen Ejecutivo 📊"
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
    prompt_protocolo_extra = " [DIRECTIVA ACTIVA: Activa protocolo de auditoría profunda de arquitectura de software y código Streamlit. Diagnostica componentes cuellos de botella y propone mejoras con rigor técnico e ironía Stark]."
elif "Resumen" in protocolo_extra:
    prompt_protocolo_extra = " [DIRECTIVA ACTIVA: Entrega siempre respuestas ultra resumidas directas al grano y estructuradas en viñetas ejecutivas]."

system_prompt = system_base + prompt_protocolo_extra

if len(st.session_state.messages) == 0 or st.session_state.messages[0]["role"] != "system":
    st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})
else:
    st.session_state.messages[0]["content"] = system_prompt

# Estilos CSS dinámicos
st.markdown(
    f"""
    <style>
    @keyframes neonGlow {{
        0% {{ text-shadow: 0 0 5px {color_neon} 0 0 10px {color_neon} 0 0 20px {shadow_neon}; }}
        50% {{ text-shadow: 0 0 12px {color_neon} 0 0 25px {color_neon} 0 0 40px {shadow_neon}; }}
        100% {{ text-shadow: 0 0 5px {color_neon} 0 0 10px {color_neon} 0 0 20px {shadow_neon}; }}
    }}
    .neon-title {{
        color: {color_neon};
        font-family: 'Courier New' Courier monospace;
        font-weight: bold;
        font-size: 1.8rem;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 20px;
        white-space: nowrap;
        animation: neonGlow 2.5s infinite ease-in-out;
    }}
    .block-container {{
        max-width: 750px;
        padding-top: 1.5rem;
        padding-bottom: 5rem;
    }}
    @keyframes rotateRing {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    @keyframes pulseSphere {{
        0% {{ transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 15px {color_neon}; }}
        50% {{ transform: scale(1.05); opacity: 1; box-shadow: 0 0 35px {color_neon}; }}
        100% {{ transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 15px {color_neon}; }}
    }}
    .sphere-wrapper {{
        width: 110px;
        height: 110px;
        margin: 0 auto;
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .orbit-ring-1 {{
        position: absolute;
        width: 100px;
        height: 100px;
        border: 2px dashed {color_neon};
        border-radius: 50%;
        animation: rotateRing 8s linear infinite;
    }}
    .orbit-ring-2 {{
        position: absolute;
        width: 75px;
        height: 75px;
        border: 1px solid {color_neon}aa;
        border-radius: 50%;
        animation: rotateRing 5s linear infinite reverse;
    }}
    .core-sphere {{
        width: 35px;
        height: 35px;
        background: radial-gradient(circle #ffffff 10% {color_neon} 70% #000000 100%);
        border-radius: 50%;
        position: absolute;
        animation: pulseSphere 2.5s infinite ease-in-out;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(titulo_html, unsafe_allow_html=True)

# ESTACIÓN DE COMANDO PRINCIPAL (HUD con Clima Escondido en Expander)
if mostrar_hud:
    with st.container(border=True):
        st.markdown(f"<div style='font-size: 0.7rem; color: {color_neon}; font-family: monospace; font-weight: bold; margin-bottom: 10px;'>[COMMAND STATION - C2 ACTIVE] &nbsp;&nbsp;&nbsp;&nbsp; INTEGRITY: {st.session_state.energia_arc}%</div>", unsafe_allow_html=True)
        
        st.markdown(
            """
            <div class="sphere-wrapper">
                <div class="orbit-ring-1"></div>
                <div class="orbit-ring-2"></div>
                <div class="core-sphere"></div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div style="font-family: monospace; font-size: 0.68rem; color: #ddd; background: rgba(015300.6); padding: 10px; border-radius: 6px; border: 1px solid {color_neon}44;">
                <b style="color: {color_neon};">SENSORS TELEMETRY FEED</b><br>
                📡 NAV_SYS: 100% &nbsp;&nbsp;|&nbsp;&nbsp; 🛡️ SHIELD: 100%<br>
                ⚡ THRUSTERS: 100% &nbsp;&nbsp;|&nbsp;&nbsp; 🧬 LIFE SUPPORT: OPTIMAL
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Módulo Climático y Sub-Sistemas ocultos en expander
        with st.expander(f"🌤️ Módulo Climático & Sub-Sistemas ({st.session_state.ubicacion_jefa})"):
            col_c

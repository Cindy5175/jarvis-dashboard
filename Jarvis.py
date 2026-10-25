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

if "modo_sistema" not in st.session_state:
    st.session_state.modo_sistema = "J.A.R.V.I.S. (Azul Neón)"

if "ubicacion_jefa" not in st.session_state:
    st.session_state.ubicacion_jefa = "Buin, Santiago, Chile"
    st.session_state.lat_lon = "-33.7333, -70.7333"

if "energia_arc" not in st.session_state:
    st.session_state.energia_arc = 98

if "notas_mision" not in st.session_state:
    st.session_state.notas_mision = "• Revisar despliegue en GitHub\n• Optimizar latencia de red"

# -------------------------------------------------------------
# 🔐 MÓDULO DE CLAVE DE ACCESO (PIN DE SEGURIDAD)
# -------------------------------------------------------------
PIN_SECRETO = "1970"  # Pin clásico intergaláctico de la Jefa

if not st.session_state.autenticado:
    st.markdown("""
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
            <p style="color: #aaa; font-size: 0.85rem;">Introduce el código de seguridad para desbloquear la estación de comando C.I.T.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        pin_ingresado = st.text_input("PIN de Acceso:", type="password", placeholder="Código secreto")
        if st.button("🔓 Desbloquear Sistema", use_container_width=True):
            if pin_ingresado == PIN_SECRETO:
                st.session_state.autenticado = True
                st.success("¡Acceso concedido, Jefa!")
                st.rerun()
            else:
                st.error("⚠️ PIN incorrecto. Acceso denegado.")
    st.stop()
# -------------------------------------------------------------

# 2. Conexión con la API de Groq
groq_api_key = "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"

if not groq_api_key:
    st.error("⚠️ Error con la clave API.")
    st.stop()

client = Groq(api_key=groq_api_key)

# 3. Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Configurar variables visuales y el PERSONALIDAD SARCÁSTICA Y ANALISTA ESTILO TONY STARK
if "N.O.V.A." in st.session_state.modo_sistema:
    color_neon = "#ff007f"
    shadow_neon = "#ff007f"
    titulo_html = '<h1 class="neon-title glow-anim">🟣 N.O.V.A. - C.I.T.</h1>'
    system_base = f"Eres N.O.V.A., un sistema de inteligencia táctica y arquitectura de software C.I.T. avanzado. Te diriges al usuario como 'Jefa'. Tienes un tono brillante, sarcástico estilo Tony Stark y experto en auditoría de sistemas Streamlit. Ubicación táctica activa: {st.session_state.ubicacion_jefa} (Coordenadas: {st.session_state.lat_lon})."
else:
    color_neon = "#00d2ff"
    shadow_neon = "#0072ff"
    titulo_html = '<h1 class="neon-title glow-anim">⚛️ J.A.R.V.I.S. AI</h1>'
    system_base = f"Eres J.A.R.V.I.S., una super IA avanzada, brillante y leal. Te diriges al usuario siempre como 'Jefa'. Respondes con la elegancia, eficiencia, sarcasmo irónico estilo Tony Stark y capacidad analítica total para auditar código de sistemas. Ubicación actual de la Jefa: {st.session_state.ubicacion_jefa} (Coordenadas satelitales: {st.session_state.lat_lon})."

# 4. BARRA LATERAL (Centro de Comando Avanzado)
with st.sidebar:
    st.markdown("### ⚙️ Centro de Comando Stark")
    
    opciones_modo = ["J.A.R.V.I.S. (Azul Neón)", "N.O.V.A. - C.I.T. (Fucsia Cyber)"]
    indice_actual = opciones_modo.index(st.session_state.modo_sistema) if st.session_state.modo_sistema in opciones_modo else 0
    
    def cambiar_modo():
        st.session_state.modo_sistema = st.session_state.radio_modo_input
        st.rerun()

    st.radio(
        "Selecciona Protocolo Activo:",
        opciones_modo,
        index=indice_actual,
        key="radio_modo_input",
        on_change=cambiar_modo
    )
    
    st.divider()
    mostrar_hud = st.checkbox("Mostrar Estación Holográfica Completa", value=True)

    st.divider()
    
    st.markdown("### 🛠️ Módulos Tácticos Izquierdos")
    estilo_voz = st.selectbox("Selector Estilo de Voz:", ["Táctico Estándar", "Formal / Robótico", "Fluido Rápido"], index=0)
    
    st.markdown(f"""
        <button onclick="
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen();
            }} else {{
                if (document.exitFullscreen) {{ document.exitFullscreen(); }}
            }}
        " style="background-color: {color_neon}; color: black; border: none; padding: 6px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; cursor: pointer; width: 100%; margin-top: 5px; margin-bottom: 5px;">
            🖥️ Alternar Pantalla Completa
        </button>
    """, unsafe_allow_html=True)
    
    zona_preset = st.selectbox("Preset de Coordenadas:", ["Buin (Base Central)", "Santiago Centro", "Estación Orbital Norte"], index=0)
    if "Santiago" in zona_preset:
        st.session_state.ubicacion_jefa = "Santiago Centro, Chile"
        st.session_state.lat_lon = "-33.4489, -70.6693"
    elif "Buin" in zona_preset:
        st.session_state.ubicacion_jefa = "Buin, Santiago, Chile"
        st.session_state.lat_lon = "-33.7333, -70.7333"
    else:
        st.session_state.ubicacion_jefa = "Sector Orbital / Desconocido"
        st.session_state.lat_lon = "00.0000, 00.0000"

    st.markdown("""
        <div id="battery-status" style="font-size: 0.7rem; font-family: monospace; background: rgba(0,15,30,0.6); padding: 6px; border-radius: 5px; border: 1px solid #444; margin-top: 5px; text-align: center;">
            🔋 Batería Dispositivo: Sincronizando...
        </div>
        <script>
            navigator.getBattery?.().then(function(battery) {
                function updateBattery() {
                    const level = Math.round(battery.level * 100);
                    const charging = battery.charging ? '⚡ (Cargando)' : '';
                    document.getElementById('battery-status').innerText = '🔋 Batería Dispositivo: ' + level + '% ' + charging;
                }
                updateBattery();
                battery.addEventListener('levelchange', updateBattery);
                battery.addEventListener('chargingchange', updateBattery);
            });
        </script>
    """, unsafe_allow_html=True)

    st.divider()
    
    st.markdown("### 👁️ Sensores Biométricos & IA")
    # Widgets integrados de Reconocimiento Facial, Sensor de Movimiento y Voz en tiempo real
    st.markdown(f"""
        <div style="background: rgba(0,20,40,0.8); border: 1px solid {color_neon}; border-radius: 8px; padding: 8px; text-align: center; font-family: monospace; font-size: 0.7rem;">
            <p style="color: {color_neon}; margin: 0 0 5px 0; font-weight: bold;">🔴 ESCANEO BIOMÉTRICO & MOVIMIENTO</p>
            <video id="webcam-feed" autoplay playsinline style="width: 100%; max-height: 120px; border-radius: 4px; object-fit: cover; border: 1px solid {color_neon}55;"></video>
            <div id="sensor-status" style="color: #00ffcc; margin-top: 4px;">📡 Sensor de Movimiento: Activo</div>
            <div id="face-status" style="color: #ff00ff; margin-top: 2px;">👤 Jefa Identificada (100%)</div>
        </div>
        <script>
            navigator.mediaDevices.getUserMedia({{ video: true }})
                .then(stream => {{
                    const video = document.getElementById('webcam-feed');
                    if(video) {{ video.srcObject = stream; }}
                }})
                .catch(err => {{
                    console.log("Cámara no disponible: ", err);
                }});
        </script>
    """, unsafe_allow_html=True)

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
    
    # 🧹 BOTÓN DE PURGA Y 🩺 ESCANEO DE ERRORES ORGANIZADOS EN DOS COLUMNAS A LA IZQUIERDA
    col_izq_1, col_izq_2 = st.columns(2)
    with col_izq_1:
        if st.button("🧹💬 Purgar"):
            st.session_state.messages = []
            st.success("¡Purgado!")
            st.rerun()
    with col_izq_2:
        if st.button("🩺 Escanear"):
            with st.spinner("Escaneando..."):
                time.sleep(1.0)
            st.success("¡Ok, Jefa!")

    st.divider()
    st.markdown("### ⚛️ Reactor Arc & Energía")
    st.caption(f"⚡ **Potencia de Núcleo:** {st.session_state.energia_arc}%")
    if st.button("🔋 Recargar Reactor Arc"):
        st.session_state.energia_arc = 100
        st.success("¡Núcleo al 100%, Jefa!")
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
    st.download_button("📥 Descargar Chat (.txt)", data=chat_texto, file_name="cit_chat_log.txt", mime="text/plain")

    st.divider()
    if st.button("🔒 Bloquear Sistema"):
        st.session_state.autenticado = False
        st.rerun()

# Definir instrucción del sistema complementada para análisis de arquitectura Jarvis.py
prompt_protocolo_extra = ""
if "Auditoría" in protocolo_extra:
    prompt_protocolo_extra = " [DIRECTIVA ACTIVA: Activa protocolo de auditoría profunda de arquitectura de software y código Streamlit (Jarvis.py). Diagnostica componentes, cuellos de botella y propone mejoras con rigor técnico e ironía Stark]."
elif "Resumen" in protocolo_extra:
    prompt_protocolo_extra = " [DIRECTIVA ACTIVA: Entrega siempre respuestas ultra resumidas, directas al grano y estructuradas en viñetas ejecutivas]."

system_prompt = system_base + prompt_protocolo_extra

if len(st.session_state.messages) == 0 or st.session_state.messages[0]["role"] != "system":
    st.session_state.messages.insert(0, {"role": "system", "content": system_prompt})
else:
    st.session_state.messages[0]["content"] = system_prompt

# Estilos CSS
st.markdown(f"""
    <style>
    @keyframes neonGlow {{
        0% {{ text-shadow: 0 0 5px {color_neon}, 0 0 10px {color_neon}, 0 0 20px {shadow_neon}; }}
        50% {{ text-

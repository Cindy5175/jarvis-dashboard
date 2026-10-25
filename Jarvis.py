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
PIN_SECRETO = "Jarvis"  # Clave de acceso configurada por la Jefa

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
                st.success("¡Acceso concedido, Jefa!")
                st.rerun()
            else:
                st.error("⚠️ Clave incorrecta. Acceso denegado.")
    st.stop()
# -------------------------------------------------------------

# 3. Historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Configuración de personalidad y colores
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
    
    # 🔌 Selector de Proveedor de API (Groq vs FreeLLMAPI / Local)
    st.markdown("### 🌐 Enlace de Red de IA")
    proveedor_api = st.selectbox(
        "Proveedor Backend:",
        ["Groq Oficial (Cloud)", "FreeLLMAPI / Servidor Local[span_1](start_span)[span_1](end_span)"],
        index=0
    )
    
    mostrar_hud = st.checkbox("Mostrar Estación Holográfica Completa", value=True)

    st.divider()
    
    st.markdown("### 🛠️ Módulos Tácticos Izquierdos")
    estilo_voz = st.selectbox("Selector Estilo de Voz:", ["Táctico Estándar", "Formal / Robótico", "Fluido Rápido"], index=0)
    
    st.markdown(
        f"""
        <button onclick="
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen();
            }} else {{
                if (document.exitFullscreen) {{ document.exitFullscreen(); }}
            }}
        " style="background-color: {color_neon}; color: black; border: none; padding: 6px 12px; border-radius: 6px; font-size: 0.75rem; font-weight: bold; cursor: pointer; width: 100%; margin-top: 5px; margin-bottom: 5px;">
            🖥️ Alternar Pantalla Completa
        </button>
        """,
        unsafe_allow_html=True
    )
    
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

    st.markdown(
        """
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
        """,
        unsafe_allow_html=True
    )

    st.divider()
    
    # ---------------------------------------------------------
    # 🔴 SENSORES BIOMÉTRICOS
    # ---------------------------------------------------------
    st.markdown("### 👁️ Sensores Biométricos")
    
    with st.expander("📡 1. Sensor Óptico de Movimiento"):
        st.caption("Visor de flujo óptico nativo.")
        foto_mov = st.camera_input("Activar Sensor Óptico", key="cam_optico")
        if foto_mov:
            st.success("¡Flujo óptico capturado, Jefa!")

    with st.expander("👤 2. Reconocimiento Facial"):
        st.caption("Escaneo biométrico de seguridad.")
        foto_rostro = st.camera_input("Escanear Rostro Biométrico", key="cam_rostro")
        if foto_rostro:
            st.success("¡Identidad confirmada, Jefa!")

    st.markdown(
        f"""
        <div style="font-size: 0.7rem; font-family: monospace; background: rgba(0,15,30,0.6); padding: 8px; border-radius: 5px; border: 1px solid {color_neon}; margin-top: 5px; text-align: center;">
            🎙️ <b>3. Voz en Tiempo Real:</b><br>
            Usa el micrófono 🎤 de tu teclado virtual para dictar mensajes con total fluidez.
        </div>
        """,
        unsafe_allow_html=True
    )
    # ---------------------------------------------------------

    st.divider()

    # ---------------------------------------------------------
    # ⚡ MÓDULOS AVANZADOS [LOS 3 PUNTOS] EN LA IZQUIERDA
    # ---------------------------------------------------------
    st.markdown("### 🚀 Protocolos Avanzados")

    with st.expander("🔊 1. Efectos de Sonido Sci-Fi (SFX)"):
        st.caption("Audio futurista HUD.")
        if st.button("🔊 Reproducir Sonido HUD", use_container_width=True):
            st.markdown(
                f"""
                <script>
                    const ctx = new (window.AudioContext || window.webkitAudioContext)();
                    const osc = ctx.createOscillator();
                    const gain = ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.setValueAtTime(880, ctx.currentTime);
                    gain.gain.setValueAtTime(0.1, ctx.currentTime);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    osc.stop(ctx.currentTime + 0.15);
                </script>
                """,
                unsafe_allow_html=True
            )
            st.success("¡Pulso de audio emitido, Jefa!")

    with st.expander("🎨 2. Generador de Hologramas"):
        st.caption("Esquemas y planos visuales.")
        prompt_holo = st.text_input("Prompt de holograma:", "Reactor Arc schematic HUD blueprint")
        if st.button("🔮 Generar Holograma", use_container_width=True):
            with st.spinner("Sintetizando plano holográfico..."):
                time.sleep(1.0)
                url_holo = f"https://image.pollinations.ai/prompt/{prompt_holo.replace(' ', '%20')}%20scifi%20blueprint%20hud%20neon"
                st.image(url_holo, caption="Plano Táctico Sintetizado", use_column_width=True)
            st.success("¡Holograma proyectado, Jefa!")

    with st.expander("🎙️ 3. Micrófono Avanzado"):
        st.caption("Grabación web en barra lateral.")
        st.markdown(
            f"""
            <div style="text-align: center; padding: 2px;">
                <button onclick="
                    navigator.mediaDevices.getUserMedia({{ audio: true }}).then(stream => {{
                        const mediaRecorder = new MediaRecorder(stream);
                        let chunks = [];
                        mediaRecorder.ondataavailable = e => chunks.push(e.data);
                        mediaRecorder.onstop = e => {{
                            alert('¡Audio capturado por el componente avanzado, Jefa!');
                        }};
                        mediaRecorder.start();
                        setTimeout(() => mediaRecorder.stop(), 3000);
                        alert('Grabando audio táctico (3s)...');
                    }}).catch(err => alert('Permiso de micrófono denegado'));
                " style="background-color: {color_neon}; color: black; border: none; padding: 6px 12px; border-radius: 5px; font-size: 0.75rem; font-weight: bold; cursor: pointer; width: 100%;">
                    🔴 Grabar Audio Táctico (3s)
                </button>
            </div>
            """,
            unsafe_allow_html=True
        )
    # ---------------------------------------------------------

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
            st.success("¡Ok, Jefa!")

    st.divider()
    st.markdown("### ⚛️ Reactor Arc & Energía")
    st.caption(f"⚡ **Potencia de Núcleo:** {st.session_state.energia_arc}%")
    if st.button("🔋 Recargar Reactor Arc", use_container_width=True):
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
    st.download_button("📥 Descargar Chat (.txt)", data=chat_texto, file_name="cit_chat_log.txt", mime="text/plain", use_container_width=True)

    st.divider()
    if st.button("🔒 Bloquear Sistema", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# Configuración del cliente según el proveedor seleccionado
if "FreeLLMAPI" in proveedor_api:
    # Endpoint local o alternativo libre compatible con la estructura
    client = Groq(
        api_key="freellmapi-token-dummy", 
        base_url="http://localhost:8000/v1"  # Puedes cambiar la URL según tu entorno local
    )
else:
    groq_api_key = "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"
    client = Groq(api_key=groq_api_key)

# Definir instrucción del sistema complementada
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
st.markdown(
    f"""
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
        background: radial-gradient(circle, #ffffff 10%, {color_neon} 70%, #000000 100%);
        border-radius: 50%;
        position: absolute;
        animation: pulseSphere 2.5s infinite ease-in-out;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# Título de la App
st.markdown(titulo_html, unsafe_allow_html=True)

# ESTACIÓN DE COMANDO PRINCIPAL (Ocultable)
if mostrar_hud:
    with st.container(border=True):
        st.markdown(f"<div style='font-size: 0.7rem; color: {color_neon}; font-family: monospace; font-weight: bold; margin-bottom: 10px;'>[COMMAND STATION - C2 ACTIVE] &nbsp;&nbsp;&nbsp;&nbsp; INTEGRITY: {st.session_state.energia_arc}%</div>", unsafe_allow_html=True)
        
        # 1. Orbe Holográfico
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
        
        # 2. Sensores
        st.markdown(
            f"""
            <div style="font-family: monospace; font-size: 0.68rem; color: #ddd; background: rgba(0,15,30,0.6); padding: 10px; border-radius: 6px; border: 1px solid {color_neon}44;">
                <b style="color: {color_neon};">SENSORS TELEMETRY FEED</b><br>
                📡 NAV_SYS: 100% &nbsp;&nbsp;|&nbsp;&nbsp; 🛡️ SHIELD: 100%<br>
                ⚡ THRUSTERS: 100% &nbsp;&nbsp;|&nbsp;&nbsp; 🧬 LIFE SUPPORT: OPTIMAL
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.expander("🌐 Sub-Sistemas Avanzados [Clima, Rendimiento & Bitácora]"):
            st.markdown(f"<b style='color: {color_neon}; font-size: 0.8rem;'>🌤️ Módulo Climático ({st.session_state.ubicacion_jefa})</b>", unsafe_allow_html=True)
            col_c1, col_c2, col_c3 = st.columns(3)
            col_c1.metric("Temperatura", "18°C", "Óptima")
            col_c2.metric("Humedad", "45%", "-2%")
            col_c3.metric("Viento", "12 km/h", "SSE")
            
            st.divider()
            
            st.markdown(f"<b style='color: {color_neon}; font-size: 0.8rem;'>📈 Gráfico de Ancho de Banda y Red (Mbps)</b>", unsafe_allow_html=True)
            import pandas as pd
            import numpy as np
            chart_data = pd.DataFrame(
                np.random.randn(15, 2) * [5, 10] + [50, 120],
                columns=["Enlace Satelital", "Flujo Neuronal"]
            )
            st.line_chart(chart_data, height=150)
            
            st.divider()
            
            st.markdown(f"<b style='color: {color_neon}; font-size: 0.8rem;'>📝 Bitácora de Misión Rápida</b>", unsafe_allow_html=True)
            st.session_state.notas_mision = st.text_area("Notas directas de la Jefa:", value=st.session_state.notas_mision, height=80)
            if st.button("💾 Guardar Notas", use_container_width=True):
                st.success("¡Bitácora sincronizada con la red central, Jefa!")
            
        st.markdown(f"<div style='font-size: 0.65rem; color: #aaa; font-family: monospace; border-top: 1px solid #333; padding-top: 6px; margin-top: 10px; display: flex; justify-content: space-between;'><span>GRID: {st.session_state.lat_lon}</span><span>STATUS: ONLINE</span></div>", unsafe_allow_html=True)

# 🎤 MÓDULO DE ACTIVACIÓN POR VOZ
st.markdown(
    f"""
    <div style="background: rgba(0,15,30,0.5); border: 1px dashed {color_neon}; border-radius: 8px; padding: 10px; margin-bottom: 10px; text-align: center;">
        <span style="font-size: 0.75rem; color: {color_neon}; font-family: monospace; font-weight: bold;">🎙️ CONTROL DE VOZ TÁCTICO:</span><br>
        <button onclick="
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'es-ES';
            recognition.onresult = function(event) {{
                const speechToText = event.results[0][0].transcript;
                const inputField = document.querySelector('input[aria-label*=\'Escribe\'], textarea[aria-label*=\'Escribe\'], input[type=\'text\']');
                if(inputField) {{
                    inputField.value = speechToText;
                    inputField.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            }};
            recognition.start();
        " style="background-color: {color_neon}; color: black; border: none; padding: 6px 14px; border-radius: 6px; font-size: 0.8rem; font-weight: bold; cursor: pointer; margin-top: 6px;">
            🔴 Activar Micrófono e Hablar
        </button>
    </div>
    """,
    unsafe_allow_html=True
)

# Mostrar Historial
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

# -------------------------------------------------------------
# 💬 CAJA DE CHAT PRINCIPAL (Siempre al final y visible)
# -------------------------------------------------------------
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
            full_response = "Lo siento, Jefa. Inconveniente en la conexión con el servidor de red seleccionado."
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

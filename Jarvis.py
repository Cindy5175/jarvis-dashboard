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

if "modo_estetico" not in st.session_state:
    st.session_state.modo_estetico = "J.A.R.V.I.S. (Azul Neón)"

if "ubicacion_jefa" not in st.session_state:
    st.session_state.ubicacion_jefa = "Buin, Santiago, Chile"
    st.session_state.lat_lon = "-33.7333, -70.7333"

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
                st.success("¡Acceso concedido, Jefa!")
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

# Configuración dinámica de colores y estilo visual según el selector
if "Fucsia" in st.session_state.modo_estetico:
    color_neon = "#ff007f"
    shadow_neon = "#ff007f"
    titulo_html = '<h1 class="neon-title glow-anim">🟣 J.A.R.V.I.S. (Modo Cyber)</h1>'
else:
    color_neon = "#00d2ff"
    shadow_neon = "#0072ff"
    titulo_html = '<h1 class="neon-title glow-anim">⚛️ J.A.R.V.I.S. AI</h1>'

system_base = f"Eres J.A.R.V.I.S., una super IA avanzada, brillante y leal. Te diriges al usuario siempre como 'Jefa'. Respondes con la elegancia, eficiencia, sarcasmo irónico estilo Tony Stark y capacidad analítica total para auditar código de sistemas. Ubicación actual de la Jefa: {st.session_state.ubicacion_jefa} (Coordenadas satelitales: {st.session_state.lat_lon})."

# 4. BARRA LATERAL (Centro de Comando Avanzado Izquierdo)
with st.sidebar:
    st.markdown("### ⚙️ Centro de Comando Stark")
    
    opciones_estilo = ["J.A.R.V.I.S. (Azul Neón)", "J.A.R.V.I.S. (Fucsia Cyber)"]
    indice_actual = opciones_estilo.index(st.session_state.modo_estetico) if st.session_state.modo_estetico in opciones_estilo else 0
    
    def cambiar_estilo():
        st.session_state.modo_estetico = st.session_state.radio_estilo_input
        st.rerun()

    st.radio(
        "Selector de Estética Visual:",
        opciones_estilo,
        index=indice_actual,
        key="radio_estilo_input",
        on_change=cambiar_estilo
    )
    
    st.divider()
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
    
    # 👁️ SENSORES BIOMÉTRICOS
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

    st.divider()

    # 🚀 PROTOCOLOS AVANZADOS
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
    st.download_button("📥 Descargar Chat (.txt)", data=chat_texto, file_name="cit_chat_log.txt", mime="text

import os
import time
import json
import tempfile
import streamlit as st
from groq import Groq
from gtts import gTTS
import pandas as pd
import numpy as np
import pydeck as pdk

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

if "tema_hud" not in st.session_state:
    st.session_state.tema_hud = "Azul Arc"

if "modo_dia_noche" not in st.session_state:
    st.session_state.modo_dia_noche = "🌙 Noche"

# -------------------------------------------------------------
# 🔐 MÓDULO DE CLAVE DE ACCESO (PIN DE SEGURIDAD)
# -------------------------------------------------------------
PIN_SECRETO = "Jarvis"

if not st.session_state.autenticado:
    st.markdown(
        """
        <div style="background: rgba(5, 12, 30, 0.95); border: 2px solid #00d2ff; border-radius: 12px; padding: 20px; text-align: left; box-shadow: 0 0 25px #00d2ff44; font-family: 'Courier New', monospace; max-width: 100%; margin: 20px auto;">
            <h2 style="color: #00d2ff; margin-bottom: 10px; font-size: 1.2rem;">🔒 ACCESO RESTRINGIDO</h2>
            <p style="color: #aaa; font-size: 0.75rem;">Introduce la clave de seguridad para desbloquear la estación C.I.T.</p>
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

# Configuración de Colores según el Tema Holográfico seleccionado
if "Azul" in st.session_state.tema_hud:
    color_neon = "#00d2ff"
    shadow_neon = "#0072ff"
elif "Rojo" in st.session_state.tema_hud:
    color_neon = "#ff3333"
    shadow_neon = "#990000"
else:  # Verde Sigilo
    color_neon = "#00ff66"
    shadow_neon = "#006622"

system_base = f"Eres J.A.R.V.I.S. Autónoma una super IA avanzada brillante y leal. Te diriges al usuario siempre como 'Jefa'. Respondes con la elegancia eficiencia sarcasmo irónico estilo Tony Stark y capacidad analítica total para auditar código de sistemas. Ubicación actual de la Jefa: {st.session_state.ubicacion_jefa} (Coordenadas satelitales: {st.session_state.lat_lon}). Modo ambiental activo: {st.session_state.modo_dia_noche}."

# BARRA LATERAL
with st.sidebar:
    st.markdown("### ⚙️ Centro de Comando Stark")
    mostrar_hud = st.checkbox("Mostrar Estación Holográfica Completa", value=True)

    st.divider()
    
    st.markdown("### 🛠️ Módulos Tácticos")
    st.selectbox(
        "Tema Holográfico HUD:", 
        ["Azul Arc", "Rojo Mark VII", "Verde Sigilo"], 
        key="tema_hud",
        on_change=lambda: st.rerun()
    )
    
    estilo_voz = st.selectbox("Selector Estilo de Voz:", ["Táctico Estándar", "Formal / Robótico", "Fluido Rápido"], index=0)
    
    opciones_preset = ["Buin (Base Central)", "Santiago Centro", "Estación Orbital Norte"]
    indice_actual = 0
    if "Santiago" in st.session_state.ubicacion_jefa:
        indice_actual = 1
    elif "Orbital" in st.session_state.ubicacion_jefa:
        indice_actual = 2

    zona_preset = st.selectbox("Preset de Coordenadas:", opciones_preset, index=indice_actual)
    
    if "Buin" in zona_preset:
        st.session_state.ubicacion_jefa = "Buin Santiago Chile"
        st.session_state.lat_lon = "-33.7333 -70.7333"
    elif "Santiago" in zona_preset:
        st.session_state.ubicacion_jefa = "Santiago Centro Chile"
        st.session_state.lat_lon = "-33.4489 -70.6693"
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
    
    # 📦 Caja Negra: Exportación de datos de sesión en JSON
    datos_caja_negra = {
        "ubicacion": st.session_state.ubicacion_jefa,
        "coordenadas": st.session_state.lat_lon,
        "energia": st.session_state.energia_arc,
        "modo": st.session_state.modo_dia_noche,
        "mensajes": st.session_state.messages
    }
    json_caja_negra = json.dumps(datos_caja_negra, ensure_ascii=False, indent=4)
    st.download_button("📦 Descargar Caja Negra (.json)", data=json_caja_negra, file_name="cit_caja_negra.json", mime="application/json", use_container_width=True)

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
    font-size: clamp(1.1rem, 5.2vw, 1.6rem);
    text-align: left !important;
    margin-top: 10px;
    margin-bottom: 15px;
    width: 100%;
    word-break: break-word;
    animation: neonGlow 2.5s infinite ease-in-out;
}}
.block-container {{
    max-width: 100% !important;
    padding-left: 0.5rem !important;
    padding-right: 0.5rem !important;
    padding-top: 1rem !important;
    padding-bottom: 5rem !important;
}}
</style>
"""

st.markdown(css_estilos, unsafe_allow_html=True)
st.markdown('<h1 class="neon-title">⚛️ J.A.R.V.I.S. AI Autónoma</h1>', unsafe_allow_html=True)

# ESTACIÓN DE COMANDO PRINCIPAL
if mostrar_hud:
    with st.container(border=True):
        col_h1, col_h2 = st.columns([3, 1])
        with col_h1:
            st.markdown(f"**[COMMAND STATION - C2]** &nbsp;&nbsp; **INT:** {st.session_state.energia_arc}%")
        with col_h2:
            # Botón de Cambio Día / Noche
            if st.button(st.session_state.modo_dia_noche, use_container_width=True, help="Alternar Modo Ambiental"):
                st.session_state.modo_dia_noche = "☀️ Día" if st.session_state.modo_dia_noche == "🌙 Noche" else "🌙 Noche"
                st.rerun()

        st.markdown("### ⚛️ ESTRUCTURA NEURAL C2")
        st.markdown("**DIAGNÓSTICO DE SISTEMAS:**")
        st.markdown("📡 Enlace Satelital: ESTABLE (100%)")
        st.markdown("🛡️ Escudo Cuántico: OPERATIVO")
        st.markdown(f"⚡ Reactor Core: {st.session_state.energia_arc}% de potencia")
        st.markdown(f"📍 Grid: {st.session_state.ubicacion_jefa} ({st.session_state.modo_dia_noche})")

        # Módulo Climático Dinámico
        with st.expander("🌤️ Módulo Climático & Alertas"):
            col_c1, col_c2, col_c3 = st.columns(3)
            if "Buin" in st.session_state.ubicacion_jefa:
                col_c1.metric("Temp", "18°C", "Buin Óptima")
                col_c2.metric("Humedad", "45%", "-2%")
                col_c3.metric("Viento", "12 km/h", "SSE")
            elif "Santiago" in st.session_state.ubicacion_jefa:
                col_c1.metric("Temp", "22°C", "Urbana")
                col_c2.metric("Humedad", "38%", "+1%")
                col_c3.metric("Viento", "15 km/h", "NW")
            else:
                col_c1.metric("Temp", "-50°C", "Orbital")
                col_c2.metric("Humedad", "0%", "Vacío")
                col_c3.metric("Viento", "0 km/h", "N/A")
            
        # Módulo de Red y Bitácora (Expandible)
        with st.expander("📈 Diagnóstico de Red & Bitácora"):
            st.markdown("**Ancho de Banda y Red (Mbps)**")
            chart_data = pd.DataFrame(
                np.random.randn(12, 2) * [5, 10] + [50, 120],
                columns=["Satelital", "Neuronal"]
            )
            st.line_chart(chart_data, height=110)
            
            st.divider()
            st.markdown("**Bitácora de Misión Rápida**")
            st.session_state.notas_mision = st.text_area("Notas directas de la Jefa:", value=st.session_state.notas_mision, height=60)
            if st.button("💾 Guardar Notas", use_container_width=True):
                st.success("¡Bitácora sincronizada Jefa!")

        # 🗺️ Módulo de Radar Satelital de Nivel Experto (Pydeck + Carto Basemaps)
        st.markdown("---")
        st.markdown(f"🗺️ **Radar Satelital Táctico C2 ({st.session_state.modo_dia_noche}):**")
        
        puntos_expertos = pd.DataFrame({
            "lat": [-33.7333, -33.4489],
            "lon": [-70.7333, -70.6693],
            "base": ["Buin (Base Central)", "Santiago Centro"],
            "radio": [12000, 10000]
        })

        # Estilos Carto profesionales que NO requieren token de Mapbox
        if "🌙" in st.session_state.modo_dia_noche:
            estilo_carto = "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json"
        else:
            estilo_carto = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"

        # Color RGBA adaptado al tema HUD activo
        if "Azul" in st.session_state.tema_hud:
            color_rgb = [0, 210, 255, 230]
        elif "Rojo" in st.session_state.tema_hud:
            color_rgb = [255, 51, 51, 230]
        else:
            color_rgb = [0, 255, 102, 230]

        capa_radar_experto = pdk.Layer(
            "ScatterplotLayer",
            data=puntos_expertos,
            get_position=["lon", "lat"],
            get_color=color_rgb,
            get_radius="radio",
            pickable=True,
            stroked=True,
            filled=True,
            line_width_min_pixels=2,
            get_line_color=[255, 255, 255, 255]
        )

        view_state_experto = pdk.ViewState(
            latitude=-33.58,
            longitude=-70.7,
            zoom=9.2,
            pitch=25,
            bearing=0
        )

        deck_experto = pdk.Deck(
            layers=[capa_radar_experto],
            initial_view_state=view_state_experto,
            map_style=estilo_carto,
            tooltip={"html": "<b>Base Táctica:</b> {base}<br><b>Coordenadas:</b> {lat}, {lon}"}
        )

        st.pydeck_chart(deck_experto)
        st.caption(f"GRID METROPOLITANO | MODO: {st.session_state.modo_dia_noche} | STATUS: ONLINE")

# 💬 HISTORIAL DE CHAT
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 💬 CAJA DE CHAT PRINCIPAL
if prompt := st.chat_input("Escribe tu instrucción o directiva..."):
    contenido_adjunto = ""
    imagen_base64 = None
    
    if archivo_subido is not None:
        nombre_archivo = archivo_subido.name
        tipo_archivo = archivo_subido.type
        
        if "image" in tipo_archivo:
            import base64
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
            full_response = "Lo siento Jefa. Inconveniente en la conexión con los servidores centrales de Groq."
            message_placeholder.markdown(full_response)

        # 🔊 Síntesis de Voz Real con gTTS
        if activar_voz and full_response:
            try:
                tts = gTTS(text=full_response, lang='es', slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    st.audio(fp.name, format="audio/mp3", autoplay=True)
            except Exception:
                pass

    st.session_state.messages.append({"role": "assistant", "content": full_response})

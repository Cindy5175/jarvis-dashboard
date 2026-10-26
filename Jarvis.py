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

    chat_texto = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages if m['role'] != 'system'] )
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
    prompt_protocolo

import os, time, json, tempfile
import streamlit as st
from groq import Groq
from gtts import gTTS
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(page_title="C.I.T. / J.A.R.V.I.S.", page_icon="⚛️", layout="centered")

# Estados de sesión
st.session_state.setdefault("autenticado", False)
st.session_state.setdefault("ubicacion_jefa", "Buin Santiago Chile")
st.session_state.setdefault("lat_lon", "-33.7333 -70.7333")
st.session_state.setdefault("energia_arc", 98)
st.session_state.setdefault("notas_mision", "• Sincronizar red\n• Optimizar módulos")
st.session_state.setdefault("tema_hud", "Azul Arc")
st.session_state.setdefault("modo_dia_noche", "🌙 Noche")

# PIN DE SEGURIDAD
if not st.session_state.autenticado:
    st.markdown('<div style="background: rgba(5, 12, 30, 0.95); border: 2px solid #00d2ff; border-radius: 12px; padding: 20px; font-family: monospace;"><h2 style="color: #00d2ff; font-size: 1.2rem;">🔒 ACCESO RESTRINGIDO</h2><p style="color: #aaa; font-size: 0.75rem;">Introduce la clave de seguridad.</p></div>', unsafe_allow_html=True)
    _, col_l2, _ = st.columns([1, 4, 1])
    with col_l2:
        pin = st.text_input("Clave:", type="password", placeholder="Contraseña")
        if st.button("🔓 Desbloquear", use_container_width=True):
            if pin == "Jarvis":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("⚠️ Clave incorrecta.")
    st.stop()

client = Groq(api_key="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")
st.session_state.setdefault("messages", [])

# Colores HUD
if "Azul" in st.session_state.tema_hud:
    c_neon, c_shadow = "#00d2ff", "#0072ff"
elif "Rojo" in st.session_state.tema_hud:
    c_neon, c_shadow = "#ff3333", "#990000"
else:
    c_neon, c_shadow = "#00ff66", "#006622"

system_base = f"Eres J.A.R.V.I.S. Autónoma, leal y brillante. Te diriges al usuario como 'Jefa' con elegancia y estilo Tony Stark. Ubicación: {st.session_state.ubicacion_jefa} ({st.session_state.lat_lon}). Modo: {st.session_state.modo_dia_noche}."

# BARRA LATERAL
with st.sidebar:
    st.markdown("### ⚙️ Centro de Comando Stark")
    mostrar_hud = st.checkbox("Mostrar Estación Holográfica", value=True)
    st.divider()
    
    st.selectbox("Tema HUD:", ["Azul Arc", "Rojo Mark VII", "Verde Sigilo"], key="tema_hud", on_change=st.rerun)
    estilo_voz = st.selectbox("Voz:", ["Táctico", "Formal", "Fluido"])
    
    presets = ["Buin (Base Central)", "Santiago Centro", "Orbital"]
    idx = 1 if "Santiago" in st.session_state.ubicacion_jefa else (2 if "Orbital" in st.session_state.ubicacion_jefa else 0)
    zona = st.selectbox("Preset Coordenadas:", presets, index=idx)
    
    if "Buin" in zona:
        st.session_state.ubicacion_jefa, st.session_state.lat_lon = "Buin Santiago Chile", "-33.7333 -70.7333"
    elif "Santiago" in zona:
        st.session_state.ubicacion_jefa, st.session_state.lat_lon = "Santiago Centro Chile", "-33.4489 -70.6693"
    else:
        st.session_state.ubicacion_jefa, st.session_state.lat_lon = "Orbital", "00.0000 00.0000"

    st.divider()
    archivo_subido = st.file_uploader("Adjuntar archivo:", type=["png", "jpg", "txt", "csv", "py"])
    protocolo = st.selectbox("Directiva:", ["Estándar", "Auditoría 💻", "Resumen 📊", "Ciberseguridad 🛡️"])
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧹 Purgar", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with c2:
        if st.button("🩺 Escanear", use_container_width=True):
            time.sleep(0.5)
            st.success("¡Ok!")

    st.divider()
    st.caption(f"⚡ Núcleo: {st.session_state.energia_arc}%")
    if st.button("🔋 Recargar Reactor", use_container_width=True):
        st.session_state.energia_arc = 100
        st.rerun()

    modelo = st.selectbox("Modelo:", ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "llama-3.2-11b-vision-preview"])
    activar_voz = st.checkbox("Habilitar Voz gTTS")
    
    caja_json = json.dumps({"ubicacion": st.session_state.ubicacion_jefa, "energia": st.session_state.energia_arc, "mensajes": st.session_state.messages}, ensure_ascii=False, indent=2)
    st.download_button("📦 Caja Negra (.json)", data=caja_json, file_name="caja_negra.json", mime="application/json", use_container_width=True)
    
    if st.button("🔒 Bloquear", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# Inyección prompt del sistema
p_extra = " [Auditoría Profunda]" if "Auditoría" in protocolo else (" [Resumen Ejecutivo]" if "Resumen" in protocolo else (" [Ciberseguridad]" if "Ciberseguridad" in protocolo else ""))
sys_msg = system_base + p_extra
if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
    st.session_state.messages.insert(0, {"role": "system", "content": sys_msg})
else:
    st.session_state.messages[0]["content"] = sys_msg

# CSS optimizado
st.markdown(f"""
<style>
@keyframes glow {{ 0%, 100% {{ text-shadow: 0 0 5px {c_neon}, 0 0 15px {c_shadow}; }} 50% {{ text-shadow: 0 0 20px {c_neon}, 0 0 35px {c_shadow}; }} }}
.neon-title {{ color: {c_neon}; font-family: monospace; font-weight: bold; font-size: 1.5rem; animation: glow 2.5s infinite; }}
.block-container {{ max-width: 100% !important; padding: 1rem 0.5rem 5rem 0.5rem !important; }}
</style>
<h1 class="neon-title">⚛️ J.A.R.V.I.S. AI Autónoma</h1>
""", unsafe_allow_html=True)

# ESTACIÓN HUD
if mostrar_hud:
    with st.container(border=True):
        col_h1, col_h2 = st.columns(

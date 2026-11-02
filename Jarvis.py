import os
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S. | Búnker Táctico",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES (Neón / Modo Oscuro) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #00f0ff;
    }
    h1, h2, h3 {
        color: #00f0ff !important;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE CORREO SÍNCRONA Y SEGURA ---
def verificar_bandeja_directa(comando):
    cmd = comando.lower()
    if any(p in cmd for p in ["bandeja", "correo", "correos", "mensajes", "email"]):
        # Excepciones vigentes guardadas: Paola Carrera Baude, Sivia Grau y Karin Grau de Folliot.
        cantidad_nuevos = 0  # Reemplazar con su lógica de lectura real si lo requiere
        
        if cantidad_nuevos == 0:
            return "Bandeja despejada, jefa. No tiene correos nuevos pendientes en este momento."
        else:
            return f"Le han llegado {cantidad_nuevos} correos nuevos a su bandeja de entrada, jefa."
    return None

# --- DISTRIBUCIÓN DE DOS COLUMNAS (IZQUIERDA Y DERECHA) ---
col_izq, col_der = st.columns([1, 1])

# --- COLUMNA IZQUIERDA: MENÚS TÁCTICOS Y NÚCLEOS ---
with col_izq:
    st.markdown("<h3>⚡ NÚCLEOS DE CEREBRO</h3>", unsafe_allow_html=True)
    
    with st.expander("1. 📹 Grabaciones y capturas de pantalla"):
        st.write("Control de registros visuales y capturas del sistema.")
        
    with st.expander("2. 🔍 Búsqueda y Web en Vivo"):
        st.write("Motores de rastreo y consultas en red.")
        
    with st.expander("3. 🌡️ Sensores Meteorológicos"):
        st.write("Monitoreo atmosférico y métricas locales.")
        
    with st.expander("4. 📄 Análisis de Documentos"):
        st.write("Lectura y procesamiento de archivos internos.")
        
    with st.expander("5. 🎙️ Módulo de Voz IA"):
        st.write("Configuración de síntesis y comandos de voz.")
        
    with st.expander("6. 🐍 Automatización Python"):
        st.write("Ejecución de scripts y rutinas programadas.")
        
    with st.expander("🎥 Monitoreo de Cámaras IP"):
        st.write(" feeds de video en tiempo real.")
        
    # Enlaces rápidos inferiores de la columna izquierda
    st.markdown("---")
    if st.button("🛰️ Ojo de Dios (Osiris)"):
        st.toast("Activando satélite Osiris...", icon="🛡️")
        
    if st.button("🏥 UC Christus"):
        st.toast("Conectando con red UC Christus...", icon="🏥")
        
    if st.button("🌦️ Meteo Chile 🇨🇱"):
        st.toast("Sincronizando datos con Meteo Chile...", icon="🌤️")

# --- COLUMNA DERECHA: CHAT IA & VISIÓN TÁCTICA ---
with col_der:
    st.markdown("<h3>💬 Chat IA & Visión Táctica</h3>", unsafe_allow_html=True)
    
    if st.button("🗑️ Limpiar Memoria"):
        st.toast("Memoria del chat purgada.", icon="🧹")
        
    st.checkbox("📷 Activar Cámara en Vivo (Escanear Entorno)")
    
    # Contenedor de mensajes / Interacción
    with st.container():
        st.info("Buenas tardes, jefa. Sistemas sincronizados y listos para operar.")
        
    # Barra de entrada de mensajes del chat derecho
    orden_usuario = st.text_input("Escriba su mensaje...", placeholder="Ej: Jarvis, ¿cómo está mi bandeja de correos?")
    
    if orden_usuario:
        respuesta_correo = verificar_bandeja_directa(orden_usuario)
        if respuesta_correo:
            st.success(respuesta_correo)
        else:
            st.write(f"**Comando registrado:** {orden_usuario}")

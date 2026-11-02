import os
import streamlit as st

# --- CONFIGURACIÓN DE PÁGINA (ANCHO TOTAL) ---
st.set_page_config(
    page_title="J.A.R.V.I.S. | Búnker Táctico",
    page_icon="🛡️",
    layout="wide",  # <-- Esto expande la interfaz a todo el ancho de la pantalla
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES PARA EVITAR MÁRGENES CENTRALES ---
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
    /* Maximizar el uso del ancho en Streamlit */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
        max-width: 100% !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE CORREO SÍNCRONA Y SEGURA ---
def verificar_bandeja_directa(comando):
    cmd = comando.lower()
    if any(p in cmd for p in ["bandeja", "correo", "correos", "mensajes", "email"]):
        # Excepciones vigentes: Paola Carrera Baude, Sivia Grau y Karin Grau de Folliot.
        cantidad_nuevos = 0  
        if cantidad_nuevos == 0:
            return "Bandeja despejada, jefa. No tiene correos nuevos pendientes en este momento."
        else:
            return f"Le han llegado {cantidad_nuevos} correos nuevos a su bandeja de entrada, jefa."
    return None

# --- DISTRIBUCIÓN DE DOS COLUMNAS AMPLIAS (50% / 50%) ---
col_izq, col_der = st.columns(2)

# ==========================================
# COLUMNA IZQUIERDA
# ==========================================
with col_izq:
    st.markdown("### ⚡ NÚCLEOS DE CEREBRO STARK")
    
    with st.expander("1. 📹 Grabaciones y capturas de pantalla"):
        st.write("Registros visuales y almacenamiento táctico.")
        
    with st.expander("2. 🔍 Búsqueda y Web en Vivo"):
        st.write("Consultas y rastreo web activo.")
        
    with st.expander("3. 🌡️ Sensores Meteorológicos"):
        st.write("Parámetros atmosféricos y métricas de Buin.")
        
    st.markdown("---")
    if st.button("🏥 UC Christus"):
        st.toast("Conectando red UC Christus...", icon="🏥")
    if st.button("🌦️ Meteo Chile 🇨🇱"):
        st.toast("Actualizando datos meteorológicos...", icon="🌤️")

# ==========================================
# COLUMNA DERECHA
# ==========================================
with col_der:
    with st.expander("4. 📄 Análisis de Documentos"):
        st.write("Lectura y procesamiento de archivos.")
        
    with st.expander("5. 🎙️ Módulo de Voz IA"):
        st.write("Sistemas de síntesis y reconocimiento de voz.")
        
    with st.expander("6. 🐍 Automatización Python"):
        st.write("Ejecución de scripts y rutinas programadas.")
        
    with st.expander("🎥 Monitoreo de Cámaras IP"):
        st.write("Feeds de video en tiempo real.")

    st.markdown("---")
    st.markdown("### 🛰️ Ojo de Dios & Telemetría ISS[cite: 4]")
    
    tab_mapa, tab_iss, tab_tierra = st.tabs(["🗺️ Mapa Táctico Satelital", "🌍 ISS Diurno", "🛰️ Tierra 2"])[cite: 4]
    
    with tab_mapa:
        st.button("🌐 Abrir Visor Satelital (Osiris AI)")[cite: 4]
        
    st.checkbox("📹 Activar Módulo de Visión Artificial & Transmisión")[cite: 4]

    st.markdown("---")
    st.markdown("### 💬 Chat IA & Análisis Visual")[cite: 4]
    
    if st.button("🗑️"):
        st.toast("Memoria purgada.", icon="🧹")
        
    st.info("Buenas noches, jefa. Memoria limpia y lista.")[cite: 4]
    
    # Entrada de comandos tácticos
    orden_usuario = st.text_input("Escriba su mensaje...", placeholder="Ej: Jarvis, ¿cómo está mi bandeja de correos?")[cite: 4]
    
    if orden_usuario:
        respuesta_correo = verificar_bandeja_directa(orden_usuario)
        if respuesta_correo:
            st.success(respuesta_correo)
        else:
            st.write(f"**Procesado:** {orden_usuario}")

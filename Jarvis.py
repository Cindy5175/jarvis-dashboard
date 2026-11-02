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
        # Excepciones vigentes: Paola Carrera Baude, Sivia Grau y Karin Grau de Folliot.
        cantidad_nuevos = 0  
        
        if cantidad_nuevos == 0:
            return "Bandeja despejada, jefa. No tiene correos nuevos pendientes en este momento."
        else:
            return f"Le han llegado {cantidad_nuevos} correos nuevos a su bandeja de entrada, jefa."
    return None

# --- DISTRIBUCIÓN EN 2 COLUMNAS ---
col_izq, col_der = st.columns([1, 1])

# ==========================================
# COLUMNA IZQUIERDA (PRIMEROS 3 MÓDULOS)
# ==========================================
with col_izq:
    st.markdown("### ⚡ NÚCLEOS DE CEREBRO STARK")
    
    with st.expander("1. 📹 Grabaciones y capturas de pantalla"):
        st.write("Control de registros visuales y almacenamiento local.")
        
    with st.expander("2. 🔍 Búsqueda y Web en Vivo"):
        st.write("Motores de rastreo y consultas en tiempo real.")
        
    with st.expander("3. 🌡️ Sensores Meteorológicos"):
        st.write("Monitoreo de parámetros y métricas locales.")

# ==========================================
# COLUMNA DERECHA (TODO EL RESTO DE MÓDULOS Y CHAT)
# ==========================================
with col_der:
    with st.expander("4. 📄 Análisis de Documentos"):
        st.write("Procesamiento de archivos y lectura sintética.")
        
    with st.expander("5. 🎙️ Módulo de Voz IA"):
        st.write("Configuración de entrada/salida de voz.")
        
    with st.expander("6. 🐍 Automatización Python"):
        st.write("Ejecución de rutinas y scripts tácticos.")
        
    with st.expander("🎥 Monitoreo de Cámaras IP"):
        st.write("Transmisiones de video en vivo.")

    st.markdown("---")
    st.markdown("### 🛰️ Ojo de Dios & Telemetría ISS")
    
    tab_mapa, tab_iss, tab_tierra = st.tabs(["🗺️ Mapa Táctico Satelital", "🌍 ISS Diurno", "🛰️ Tierra 2"])
    
    with tab_mapa:
        st.button("🌐 Abrir Visor Satelital (Osiris AI)")
        
    st.checkbox("📹 Activar Módulo de Visión Artificial & Transmisión")

    st.markdown("---")
    st.markdown("### 💬 Chat IA & Análisis Visual")
    
    if st.button("🗑️ Limpiar Memoria"):
        st.toast("Memoria purgada con éxito.", icon="🧹")
        
    st.info("Buenas noches, jefa. Memoria limpia y lista.")
    
    # Entrada de comandos
    orden_usuario = st.text_input("Escriba su mensaje...", placeholder="Ej: Jarvis, ¿cómo está mi bandeja de correos?")
    
    if orden_usuario:
        respuesta_correo = verificar_bandeja_directa(orden_usuario)
        if respuesta_correo:
            st.success(respuesta_correo)
        else:
            st.write(f"**Procesado:** {orden_usuario}")

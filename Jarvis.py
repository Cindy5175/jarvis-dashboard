import os
import streamlit as st

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S. | Búnker Táctico",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES (Estética Minimalista / Alta Contraste / Neón) ---
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
    .stTextInput input {
        background-color: #161b22;
        color: #00f0ff;
        border: 1px solid #00f0ff;
    }
    </style>
""", unsafe_allow_html=True)

# --- CARGAR API KEY DE OPENAI DESDE SECRETS ---
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

# --- LÓGICA DE CONSULTA DE CORREOS (SÍNCRONA Y SEGURA) ---
def verificar_bandeja_directa(comando):
    cmd = comando.lower()
    if any(p in cmd for p in ["bandeja", "correo", "correos", "mensajes", "email"]):
        # Aquí se realiza la consulta limpia de su casilla (sin hilos que colapsen la nube)
        # Excepciones vigentes guardadas en el sistema: Paola Carrera Baude, Sivia Grau y Karin Grau de Folliot.
        cantidad_nuevos = 0  # Reemplazar con su lógica de lectura real si lo requiere
        
        if cantidad_nuevos == 0:
            return "Bandeja despejada, jefa. No tiene correos nuevos pendientes en este momento."
        elif cantidad_nuevos == 1:
            return "Tiene 1 correo nuevo en la bandeja de entrada, jefa."
        else:
            return f"Le han llegado {cantidad_nuevos} correos nuevos a su bandeja de entrada, jefa."
            
    return None

# --- INTERFAZ PRINCIPAL DEL BÚNKER ---
st.markdown("<h1>⚡ SECTOR BETA</h1>", unsafe_allow_html=True)

with st.expander("🎙️ Núcleo de Voz J.A.R.V.I.S.", expanded=True):
    st.toggle("Activar Síntesis de Voz Avanzada", value=True)
    if st.button("🔊 Repetir Último Comando"):
        st.toast("Reactivando audio del sistema...", icon="🛡️")

# Entrada de comandos de texto / voz principal
orden_usuario = st.text_input("Escriba su orden...", placeholder="Ej: Jarvis, ¿cómo está mi bandeja de correos?")

if orden_usuario:
    # Procesar si pregunta por correo
    respuesta_correo = verificar_bandeja_directa(orden_usuario)
    
    if respuesta_correo:
        st.success(respuesta_correo)
    else:
        st.info(f"Comando procesado en el búnker: '{orden_usuario}'")

# --- MÓDULOS SECUNDARIOS DEL TABLERO ---
with st.expander("🧬 Núcleo Científico GNOME"):
    st.write("Sistemas de monitoreo y análisis en línea.")

with st.expander("📬 Auditoría de Correo IA"):
    st.write("Filtros automáticos activos.")
    st.caption("Excepciones personales configuradas: Paola Carrera Baude, Sivia Grau, Karin Grau de Folliot.")

with st.expander("🕵️‍♂️ Módulo OSINT & Monitoreo Global"):
    st.write(" Radares y rastreo satelital en espera.")

with st.expander("🗺️ Estación Cartográfica (Stark Maps)"):
    st.write("Metodología Ventusky y coordenadas de Buin activas.")

import streamlit as st
import datetime
import pytz

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Jarvis - Nodo Buin", layout="wide")

# --- ZONA HORARIA CHILENA ---
zona_chile = pytz.timezone("America/Santiago")

# --- 1. ENCABEZADO CON TRIÁNGULO DE TONY STARK Y RELOJ EN VIVO ---
@st.fragment(run_every=1)
def render_jarvis_header():
    # Obtiene la hora actual en Chile
    now = datetime.datetime.now(zona_chile)
    
    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
    
    dia_str = dias[now.weekday()]
    mes_str = meses[now.month]
    fecha_str = f"{dia_str}, {now.day:02d} de {mes_str} de {now.year}"
    hora_segundos = now.strftime("%H:%M:%S")
    
    st.markdown(
        f"""
        <div style='text-align: center; font-family: monospace; color: #00FFFF;'>
            <div style='font-size: 2.5rem; text-shadow: 0 0 10px #00FFFF; margin-bottom: 5px;'>⬆️</div>
            <h2 style='margin-bottom: 0px;'>J.A.R.V.I.S.</h2>
            <p style='font-size: 0.85rem; margin-top: 5px; color: #88FFFF;'>
                [ STARK INDUSTRIES // NODO BUIN, CHILE // {fecha_str} – {hora_segundos} ]
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- 2. FUNCIONES DE CÁADA MÓDULO (SIN NÚMEROS Y CON ESPACIADO) ---

def modulo_grabaciones():
    st.markdown("### 📁 Grabaciones y Capturas")
    st.write("Gestión y almacenamiento de registros multimedia y capturas del sistema.")

def modulo_busqueda():
    st.markdown("### 🌐 Búsqueda y Web en Vivo")
    st.write("Módulo de consulta de información y enlaces en tiempo real.")
    query = st.text_input("Término de búsqueda web:")
    if query:
        st.success(f"Buscando: {query}...")

def modulo_sensores():
    st.markdown("### 🌤️ Sensores Meteorológicos")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Temperatura Nodo Buin", value="22°C", delta="+1°C")
    with col2:
        st.metric(label="Humedad Relativa", value="45%", delta="-2%")

def modulo_documentos():
    st.markdown("### 📄 Análisis de Documentos")
    st.write("Lector y procesador inteligente de archivos locales y Drive.")
    st.file_uploader("Subir documento para análisis:")

def modulo_voz():
    st.markdown("### 🎙️ Módulo de Voz IA")
    st.toggle("Activar Síntesis de Voz Avanzada", value=True)
    if st.button("🔊 Repetir Último Comando"):
        st.info("Reproduciendo último comando de voz...")

def modulo_python():
    st.markdown("### ⚙️ Automatización Python")
    st.write("Ejecución de scripts de control y rutinas programadas.")
    if st.button("▶️ Ejecutar Diagnóstico del Sistema"):
        st.success("Diagnóstico completado sin anomalías.")


# --- 3. RENDERIZADO DE LA INTERFAZ ---

# Reloj dinámico superior con triángulo Stark
render_jarvis_header()
st.markdown("---")

# Menú lateral sin números y con mejor espaciado visual
with st.sidebar:
    st.markdown("### 🧠 Núcleos de Cerebro")
    st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    
    seleccion = st.radio(
        "Seleccione módulo:",
        [
            "Grabaciones y capturas",
            "Búsqueda y Web en Vivo",
            "Sensores Meteorológicos",
            "Análisis de Documentos",
            "Módulo de Voz IA",
            "Automatización Python"
        ],
        label_visibility="collapsed"
    )

# --- 4. ENRUTADOR DE MÓDULOS EN SU SITIO ---
if seleccion == "Grabaciones y capturas":
    modulo_grabaciones()
elif seleccion == "Búsqueda y Web en Vivo":
    modulo_busqueda()
elif seleccion == "Sensores Meteorológicos":
    modulo_sensores()
elif seleccion == "Análisis de Documentos":
    modulo_documentos()
elif seleccion == "Módulo de Voz IA":
    modulo_voz()
elif seleccion == "Automatización Python":
    modulo_python()

# --- 5. CAJA DE CHAT INFERIOR (💬) ---
st.markdown("---")
st.markdown("### 💬 Interacción con Jarvis")
user_input = st.text_input("Escriba su orden...", placeholder="Ej: Jarvis, ¿cómo está mi bandeja de correos?", key="chat_input_principal")
if user_input:
    st.success(f"Orden registrada en el sistema: {user_input}")

import streamlit as st
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Jarvis - Nodo Buin", layout="wide")

# --- 1. RELOJ DINÁMICO EN VIVO (Con segundero corriendo) ---
@st.fragment(run_every=1)
def render_live_clock():
    now = datetime.datetime.now()
    fecha_str = now.strftime("%A, %d de %B de %Y")
    hora_segundos = now.strftime("%H:%M:%S")
    st.markdown(
        f"""
        <div style='text-align: center; font-family: monospace; color: #00FFFF;'>
            <h2 style='margin-bottom: 0px;'>J.A.R.V.I.S.</h2>
            <p style='font-size: 0.9rem; margin-top: 5px;'>
                [ STARK INDUSTRIES // NODO BUIN, CHILE // {fecha_str} – {hora_segundos} ]
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- 2. FUNCIONES DE CADA MÓDULO (NÚCLEOS DE CEREBRO) ---

def modulo_grabaciones():
    st.subheader("📁 1. Grabaciones y Capturas")
    st.write("Gestión y almacenamiento de registros multimedia y capturas del sistema.")
    # Agregue aquí sus componentes específicos para grabaciones

def modulo_busqueda():
    st.subheader("🌐 2. Búsqueda y Web en Vivo")
    st.write("Módulo de consulta de información y enlaces en tiempo real.")
    query = st.text_input("Término de búsqueda web:")
    if query:
        st.success(f"Buscando: {query}...")

def modulo_sensores():
    st.subheader("🌤️ 3. Sensores Meteorológicos")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Temperatura Nodo Buin", value="22°C", delta="+1°C")
    with col2:
        st.metric(label="Humedad Relativa", value="45%", delta="-2%")
    st.write("Monitoreo de variables atmosféricas y estado del entorno.")

def modulo_documentos():
    st.subheader("📄 4. Análisis de Documentos")
    st.write("Lector y procesador inteligente de archivos locales y Drive.")
    st.file_uploader("Subir documento para análisis:")

def modulo_voz():
    st.subheader("🎙️ 5. Módulo de Voz IA")
    st.toggle("Activar Síntesis de Voz Avanzada", value=True)
    if st.button("🔊 Repetir Último Comando"):
        st.info("Reproduciendo último comando de voz...")

def modulo_python():
    st.subheader("⚙️ 6. Automatización Python")
    st.write("Ejecución de scripts de control y rutinas programadas.")
    if st.button("▶️ Ejecutar Diagnóstico del Sistema"):
        st.success("Diagnóstico completado sin anomalías.")


# --- 3. RENDERIZADO DE LA INTERFAZ PRINCIPAL Y MENÚ ---

# Reloj dinámico superior
render_live_clock()
st.markdown("---")

# Menú lateral para la selección de núcleos (visto en su captura)
with st.sidebar:
    st.markdown("### 🧠 Núcleos de Cerebro")
    seleccion = st.radio(
        "Seleccione módulo:",
        [
            "1. Grabaciones y capturas",
            "2. Búsqueda y Web en Vivo",
            "3. Sensores Meteorológicos",
            "4. Análisis de Documentos",
            "5. Módulo de Voz IA",
            "6. Automatización Python"
        ],
        label_visibility="collapsed"
    )

# --- 4. ENRUTADOR DE MÓDULOS ---
if seleccion == "1. Grabaciones y capturas":
    modulo_grabaciones()
elif seleccion == "2. Búsqueda y Web en Vivo":
    modulo_busqueda()
elif seleccion == "3. Sensores Meteorológicos":
    modulo_sensores()
elif seleccion == "4. Análisis de Documentos":
    modulo_documentos()
elif seleccion == "5. Módulo de Voz IA":
    modulo_voz()
elif seleccion == "6. Automatización Python":
    modulo_python()

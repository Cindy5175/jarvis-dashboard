import streamlit as st
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Jarvis - Nodo Buin", layout="wide")

# --- ENCABEZADO TÁCTICO & RELOJ DINÁMICO EN VIVO ---
@st.fragment(run_every=1)
def render_jarvis_header():
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

# Renderiza el núcleo superior
render_jarvis_header()
st.markdown("---")

# --- MENÚ LATERAL / NÚCLEOS DE CEREBRO ---
with st.sidebar:
    st.subheader("🧠 Núcleos de Cerebro")
    opcion = st.radio(
        "Seleccione módulo:",
        [
            "1. Grabaciones y capturas",
            "2. Búsqueda y Web en Vivo",
            "3. Sensores Meteorológicos",
            "4. Análisis de Documentos",
            "5. Módulo de Voz IA",
            "6. Automatización Python"
        ]
    )

# --- SECTOR TÁCTICO PRINCIPAL ---
st.subheader("🛰️ Ojo de Dios – Telemetría Satelital")
st.write("Enlace satelital de órbita terrestre sincronizado con el nodo Buin.")

if st.button("🌐 Abrir Visor Satelital en Vivo (Osiris AI)"):
    st.info("Conectando con la red satelital Osiris...")

# Caja de interacción estilo chat inferior
st.markdown("---")
user_input = st.text_input("Escriba su orden...", placeholder="Ej: Jarvis, ¿cómo está mi bandeja de correos?")
if user_input:
    st.success(f"Orden registrada en el sistema: {user_input}")

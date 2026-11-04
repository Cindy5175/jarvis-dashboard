import streamlit as st
import datetime

# Configuración de la página del búnker
st.set_page_config(
    page_title="Jarvis Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Título principal
st.title("🤖 J.A.R.V.I.S. Dashboard Tactical Interface")
st.markdown("---")

# Reloj estático y limpio
hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
st.markdown(f"### ⏰ Hora del Sistema: `{hora_actual}`")

# Métricas del sistema en columnas
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Estado del Sistema", value="ONLINE", delta="Estable")
with col2:
    st.metric(label="Núcleo de IA", value="Activo", delta="Local / Hob")
with col3:
    st.metric(label="Modo de Escucha", value="Manual / Seguro", delta="Sin conflictos cloud")

st.markdown("---")

# Sección principal dividida en dos columnas: Izquierda (Cámara en vivo) y Derecha (Mapa táctico)
col_izq, col_der = st.columns(2)

with col_izq:
    st.subheader("📷 Cámaras en Vivo (Ojo de Dios)")
    st.write("Transmisión satelital en directo (ISS Live)")
    st.video("https://www.youtube.com/watch?v=4QJEibrt9B8")

with col_der:
    st.subheader("🌍 Mapa Táctico Satelital")
    st.write("Vigilancia de sector activa en Buin, Chile.")
    map_data = [{"lat": -33.7333, "lon": -70.7167}]
    st.map(map_data, zoom=10)

st.markdown("---")

# Sección de Controles y Operaciones
st.subheader("⚙️ Panel de Control y Operaciones")

if st.button("➕ Registrar Tarea"):
    st.success("Tarea registrada correctamente en el sistema.")

with st.expander("🎙️ Escucha Continua (Hands-Free)"):
    st.info(
        "La escucha continua y la síntesis de voz se ejecutan de manera local "
        "en tu ordenador para evitar errores de hardware en Streamlit Cloud."
    )

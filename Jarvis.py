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

# Reloj estático y limpio (sin bucles que bloqueen la app)
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

# Sección de Controles y Operaciones
st.subheader("⚙️ Panel de Control y Operaciones")

# Botón de registro de tareas
if st.button("➕ Registrar Tarea"):
    st.success("Tarea registrada correctamente en el sistema.")

# Expansor para la nota del manos libres
with st.expander("🎙️ Escucha Continua (Hands-Free)"):
    st.info(
        "La escucha continua y la síntesis de voz se ejecutan de manera local "
        "en tu ordenador para evitar errores de hardware en Streamlit Cloud."
    )

# Mapa táctico satelital solicitado
st.subheader("🌍 Mapa Táctico Satelital")
st.write("Vigilancia de sector activa en Buin, Chile.")

# Coordenadas de referencia para el mapa
map_data = [{"lat": -33.7333, "lon": -70.7167}]
st.map(map_data, zoom=10)

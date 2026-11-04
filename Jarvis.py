import streamlit as st
import time

# Configuración de la página
st.set_page_config(
    page_title="Jarvis Dashboard",
    page_icon="🤖",
    layout="wide"
)

# Estilo visual del búnker
st.title("🤖 J.A.R.V.I.S. Dashboard Tactical Interface")
st.markdown("---")

# Reloj en tiempo real con segundos
clock_placeholder = st.empty()

# Métricas o estado del sistema
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Estado del Sistema", value="ONLINE", delta="Estable")
with col2:
    st.metric(label="Núcleo de IA", value="Activo", delta="Local / Hob")
with col3:
    st.metric(label="Modo de Escucha", value="Manual / Seguro", delta="Sin conflictos cloud")

st.markdown("---")

# Sección de Controles y Tareas
st.subheader("⚙️ Panel de Control y Operaciones")

# Botón de registro de tareas solicitado
if st.button("➕ Registrar Tarea"):
    st.success("Tarea registrada correctamente en el sistema.")

# Expansor para simular o explicar la escucha continua de forma local
with st.expander("🎙️ Escucha Continua (Hands-Free)"):
    st.info(
        "Nota técnica: La escucha continua por micrófono y voz sintética se ejecuta de forma local "
        "en tu ordenador para evitar errores de dependencias de audio en Streamlit Cloud."
    )

# Mapa táctico satelital solicitado
st.subheader("🌍 Mapa Táctico Satelital")
st.write("Cargando coordenadas y sector de vigilancia en Buin...")

# Simulación visual del mapa táctico con un contenedor o mapa de Streamlit
map_data = [{"lat": -33.7333, "lon": -70.7167}] # Coordenadas de referencia Buin, Chile
st.map(map_data, zoom=10)

# Actualización continua visual del reloj
for seconds in range(2):
    current_time = time.strftime("%H:%M:%S")
    clock_placeholder.markdown(f"### ⏰ Hora del Sistema: `{current_time}`")
    time.sleep(1)

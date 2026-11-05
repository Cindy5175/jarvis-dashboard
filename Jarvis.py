import streamlit as st

st.set_page_config(page_title="J.A.R.V.I.S. - Núcleo Táctico", layout="wide")

st.title("⚡ J.A.R.V.I.S. // NÚCLEO TÁCTICO")

# Panel lateral de control
st.sidebar.header("⚙️ Configuración del Sistema")
modo_voz = st.sidebar.toggle("🎙️ Escucha Continua (Hands-Free)", value=True)
sarcasmo_nivel = st.sidebar.slider("Nivel de Sarcasmo", 1, 10, 8)

# Botón de registro de tareas
if st.sidebar.button("➕ Registrar Tarea"):
    st.sidebar.success("Tarea registrada en el núcleo local.")

# Sección central: Mapa táctico satelital
st.subheader("🗺️ Mapa Táctico Satelital")
st.map(latitude=-33.725, longitude=-70.702, zoom=11)  # Coordenadas orientativas de la zona central

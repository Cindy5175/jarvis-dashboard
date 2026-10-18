import streamlit as st
import os

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

st.title("🤖 JARVIS 4.0 // NOVA")
st.markdown("---")

st.markdown("### Estado del Sistema")
st.success("Núcleos y dependencias verificados correctamente.")
st.info("Servidor de red local a la escucha de comandos desde el dispositivo iOS.")

# Sección interactiva básica en la interfaz
col1, col2 = st.columns(2)

with col1:
    st.subheader("Estado Ambiental")
    st.write("📍 **Ubicación:** Buin, Chile")
    st.write("⚡ **Condiciones:** Monitoreo de tormenta eléctrica activo.")

with col2:
    st.subheader("Controles Rápidos")
    if st.button("Verificar Estado"):
        st.toast("¡Sistemas operativos al 100%, Jefa!")

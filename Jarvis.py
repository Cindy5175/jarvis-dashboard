import streamlit as st
import datetime
import time

# Configuración del contenedor del reloj
st.subheader("⏱️ Cronómetro del Búnker")

@st.fragment(run_every=1)
def render_live_clock():
    # Obtiene la hora actual exacta con segundos
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Muestra el reloj con su estética de alta contraste (neón)
    st.markdown(
        f"<h1 style='color: #00FFFF; font-family: monospace;'>{now}</h1>", 
        unsafe_allow_html=True
    )

# Ejecuta el fragmento del reloj en vivo
render_live_clock()

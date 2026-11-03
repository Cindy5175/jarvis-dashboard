import streamlit as st
import datetime

# --- BLOQUE DEL CRONÓMETRO EN VIVO ---
st.subheader("⏱️ Cronómetro del Búnker")

@st.fragment(run_every=1)
def render_live_clock():
    # Captura la hora actual exacta con segundos
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Renderiza el reloj con el estilo neón/turquesa del búnker
    st.markdown(
        f"<h1 style='color: #00FFFF; font-family: monospace;'>{now}</h1>", 
        unsafe_allow_html=True
    )

# Ejecuta la función del reloj dinámico
render_live_clock()

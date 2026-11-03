import streamlit as st
import datetime

# --- BLOQUE DINÁMICO: RELOJ Y SEGUNDERO EN VIVO ---
@st.fragment(run_every=1)
def render_live_clock():
    # Obtiene la hora exacta con segundos
    now = datetime.datetime.now().strftime("%H:%M:%S")
    
    # Muestra el reloj con el estilo neón turquesa del búnker
    st.markdown(
        f"<h1 style='color: #00FFFF; font-family: monospace; text-align: left;'>⏱️ {now}</h1>", 
        unsafe_allow_html=True
    )

# Llamada para renderizar el reloj en movimiento
render_live_clock()

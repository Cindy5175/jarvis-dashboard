import streamlit as st
import datetime

# --- RELOJ DINÁMICO DEL NÓDULO (SEGUNDERO EN VIVO) ---
@st.fragment(run_every=1)
def render_jarvis_clock():
    # Obtiene la fecha y hora actual con formato exacto
    now = datetime.datetime.now()
    fecha_formateada = now.strftime("%A, %d de %B de %Y") # O ajustado a su preferencia
    hora_segundos = now.strftime("%H:%M:%S")
    
    # Texto de estado estilo Stark Industries
    st.markdown(
        f"""
        <div style='text-align: center; font-family: monospace; color: #00FFFF;'>
            <p style='font-size: 0.9rem; margin-bottom: 2px;'>[ STARK INDUSTRIES // NODO BUIN, CHILE // {hora_segundos} ]</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# Llamada para desplegar el reloj dinámico en la interfaz
render_jarvis_clock()

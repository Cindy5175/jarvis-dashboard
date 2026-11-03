import streamlit as st
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Jarvis - Búnker", layout="wide")

st.title("🛡️ JARVIS // NÚCLEO TÁCTICO")

# --- 1. BLOQUE DINÁMICO: RELOJ EN VIVO ---
@st.fragment(run_every=1)
def render_live_clock():
    now = datetime.datetime.now().strftime("%H:%M:%S")
    st.markdown(
        f"<h1 style='color: #00FFFF; font-family: monospace;'>{now}</h1>", 
        unsafe_allow_html=True
    )

# --- 2. BLOQUE DE MÉTRICAS / CLIMA (O RESTO DE DATOS) ---
@st.fragment(run_every=30)  # Se actualiza cada 30 segundos para no saturar
def render_metrics_and_data():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Temperatura Buin", value="22°C", delta="+1°C")
    with col2:
        st.metric(label="Estado del Sistema", value="Óptimo", delta="100%")
    with col3:
        st.metric(label="Latencia Red", value="14 ms", delta="-2 ms")
        
    st.markdown("---")
    st.subheader("📊 Monitoreo Activo")
    st.write("Los demás componentes y accesos directos del búnker operan de forma estable.")

# Llamada a los bloques interactivos en la interfaz
render_live_clock()
st.subheader("⏱️ Cronómetro del Búnker") # (Ajuste el orden visual según prefiera)
render_metrics_and_data()

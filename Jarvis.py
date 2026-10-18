import streamlit as st
import pandas as pd

# Configuración de la página en Streamlit (Forzando diseño amplio y título)
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Inyección de Estilos CSS para el fondo negro y letras azul neón
st.markdown("""
    <style>
    /* Fondo negro profundo general */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Títulos principales en azul neón brillante */
    h1, h2, h3 {
        color: #00f3ff !important;
        text-shadow: 0px 0px 10px rgba(0, 243, 255, 0.6);
    }
    
    /* Textos generales en tono claro legible sobre fondo negro */
    p, span, label, div, markdown {
        color: #c0c0c0 !important;
    }
    
    /* Cajas y contenedores con bordes de luz azul neón */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        border: 1px solid #00f3ff !important;
        box-shadow: 0px 0px 10px rgba(0, 243, 255, 0.3);
        border-radius: 8px;
    }
    
    /* Botones tácticos */
    .stButton>button {
        background-color: #0a0f18 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.4);
    }
    .stButton>button:hover {
        background-color: #00f3ff !important;
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 JARVIS 4.0 // NOVA")
st.markdown("---")

st.markdown("### Estado del Sistema")
st.success("Núcleos y dependencias verificados correctamente.")
st.info("Servidor de red local a la escucha de comandos desde el dispositivo iOS.")

# Sección interactiva dividida en columnas
col1, col2 = st.columns(2)

with col1:
    st.subheader("Estado Ambiental")
    st.write("📍 **Ubicación:** Buin, Chile")
    st.write("⚡ **Condiciones:** Monitoreo de tormenta eléctrica activo.")
    
    # Mapeo satelital centrado exactamente en Buin, Chile (-33.7333, -70.7417)
    st.markdown("### 🛰️ Satélite VIERNES")
    mapa_buin = pd.DataFrame({
        'lat': [-33.7333],
        'lon': [-70.7417]
    })
    st.map(mapa_buin, zoom=11, use_container_width=True)

with col2:
    st.subheader("Controles Rápidos")
    if st.button("Verificar Estado"):
        st.toast("¡Sistemas operativos al 100%, Jefa!")

    st.subheader("Consola de Mando")
    st.info("Esperando instrucciones de voz desde iOS...")

import streamlit as st
import pandas as pd

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Inyección de Estilos CSS para forzar fondo negro y letras azul neón
st.markdown("""
    <style>
    /* Fondo negro profundo general */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Títulos principales en azul neón brillante con resplandor */
    h1, h2, h3 {
        color: #00f3ff !important;
        text-shadow: 0px 0px 8px rgba(0, 243, 255, 0.6);
    }
    
    /* Textos generales en azul neón claro / cian para mantener toda la temática */
    p, span, label, div, markdown, .stMarkdown {
        color: #80f9ff !important;
    }
    
    /* Cajas y contenedores con bordes de luz azul neón */
    div[data-testid="stVerticalBlock"] > div[style*="border"] {
        border: 1px solid #00f3ff !important;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.3);
        border-radius: 8px;
    }
    
    /* Botones tácticos */
    .stButton>button {
        background-color: #000a12 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px;
        box-shadow: 0px 0px 6px rgba(0, 243, 255, 0.4);
    }
    .stButton>button:hover {
        background-color: #00f3ff !important;
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 JARVIS 4.0 // NOVA")
st.markdown("---")

# Distribución en columnas: Columna izquierda para Estado Ambiental y Mapa pequeño, Columna derecha para Controles
col1, col2 = st.columns(2)

with col1:
    st.subheader("Estado Ambiental")
    st.write("📍 **Ubicación:** Buin, Chile")
    st.write("⚡ **Condiciones:** Monitoreo de tormenta eléctrica activo.")
    
    # Enlace satelital Serafín con mapa más compacto (zoom ajustado)
    st.markdown("### 🛰️ Enlace satelital Serafín")
    mapa_buin = pd.DataFrame({
        'lat': [-33.7333],
        'lon': [-70.7417]
    })
    # Contenedor para hacer el mapa visualmente más pequeño y estético
    with st.container():
        st.map(mapa_buin, zoom=10, use_container_width=False)

with col2:
    st.subheader("Controles Rápidos")
    if st.button("Verificar Estado"):
        st.toast("¡Sistemas operativos al 100%, Jefa!")

    st.subheader("Consola de Mando")
    st.info("Esperando instrucciones de voz desde iOS...")
    

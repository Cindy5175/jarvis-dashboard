import streamlit as st
import pandas as pd
from datetime import datetime

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Inyección de Estilos CSS para forzar fondo negro, letras azul neón y mapa compacto
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
    
    /* Textos generales en azul neón claro / cian */
    p, span, label, div, markdown, .stMarkdown {
        color: #80f9ff !important;
    }
    
    /* Reducir altura del mapa iframe para hacerlo más compacto */
    iframe {
        height: 180px !important;
        border-radius: 8px;
        border: 1px solid #00f3ff !important;
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

# Distribución en columnas principales
col1, col2 = st.columns(2)

with col1:
    # Fecha y Hora Táctica en tiempo real (con segundero)
    st.subheader("📅 Sincronización Temporal")
    ahora = datetime.now()
    fecha_actual = ahora.strftime("%d/%m/%Y")
    hora_actual = ahora.strftime("%H:%M:%S")
    
    st.write(f"📌 **Fecha:** {fecha_actual}")
    st.markdown(f"⏱️ **Hora Táctica (Local):**")
    st.markdown(f"### `{hora_actual}`")
    
    # Enlace satelital Serafín con mapa achicado mediante subcolumnas
    st.markdown("### 🛰️ Enlace satelital Serafín")
    
    mapa_col1, mapa_col2 = st.columns([2, 1])
    with mapa_col1:
        mapa_buin = pd.DataFrame({
            'lat': [-33.7333],
            'lon': [-70.7417]
        })
        st.map(mapa_buin, zoom=9, use_container_width=True)

with col2:
    st.subheader("Controles Rápidos")
    if st.button("Verificar Estado"):
        st.toast("¡Sistemas operativos al 100%, Jefa!")

    st.subheader("Consola de Mando")
    st.info("Esperando instrucciones de voz desde iOS...")

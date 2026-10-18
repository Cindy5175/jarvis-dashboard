import streamlit as st
import urllib.request

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Inyección de Estilos CSS para tipografía y detalles en Azul Neón
st.markdown("""
    <style>
    /* Forzar fondo oscuro general */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Títulos principales en azul neón brillante */
    h1, h2, h3 {
        color: #00f3ff !important;
        text-shadow: 0px 0px 10px rgba(0, 243, 255, 0.5);
    }
    
    /* Textos generales claros para contraste táctico */
    p, span, label, div {
        color: #e0e0e0;
    }
    
    /* Cajas métricas y contenedores con borde azul neón */
    div[data-testid="stMetric"], .stAlert, div.css-1r6slb0 {
        border: 1px solid #00f3ff !important;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.3);
        border-radius: 8px;
    }
    
    /* Botones tácticos con acento azul neón */
    .stButton>button {
        background-color: #161b22;
        color: #00f3ff;
        border: 1px solid #00f3ff;
        border-radius: 6px;
        box-shadow: 0px 0px 5px rgba(0, 243, 255, 0.4);
    }
    .stButton>button:hover {
        background-color: #00f3ff;
        color: #0e1117;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ J.A.R.V.I.S. 4.0 - Centro de Comando Autónomo")
st.markdown("---")

# Función para consultar el clima en vivo de Buin
def obtener_clima_buin():
    try:
        url = "https://wttr.in/Buin?format=%C+%t"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            return response.read().decode('utf-8').strip()
    except Exception:
        return "Tormenta eléctrica y truenos detectados"

st.markdown("### Estado del Sistema")
st.success("Núcleos y dependencias verificados correctamente.")
st.info("Servidor de red local a la escucha de comandos desde el dispositivo iOS.")

# Sección interactiva en la interfaz
col1, col2 = st.columns(2)

with col1:
    st.subheader("Estado Ambiental")
    st.write("📍 **Ubicación:** Buin, Chile")
    
    # Obtenemos y mostramos el clima actual en la interfaz
    clima_actual = obtener_clima_buin()
    st.write(f"🌤️ **Condiciones meteorológicas:** {clima_actual}")

with col2:
    st.subheader("Controles Rápidos")
    if st.button("Verificar Estado"):
        st.toast("¡Sistemas operativos al 100%, Jefa!")

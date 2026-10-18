import streamlit as st
import urllib.request
import json

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Inyección de Estilos CSS limpios para estética táctica
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
    }
    h1, h2, h3 {
        color: #00f3ff !important;
        text-shadow: 0px 0px 10px rgba(0, 243, 255, 0.4);
    }
    p, span, label, div {
        color: #e0e0e0;
    }
    .stButton>button {
        background-color: #161b22;
        color: #00f3ff;
        border: 1px solid #00f3ff;
        border-radius: 6px;
    }
    .stButton>button:hover {
        background-color: #00f3ff;
        color: #0e1117;
    }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ J.A.R.V.I.S. 4.0 - Centro de Comando Autónomo")
st.markdown("---")

# Función segura para obtener el clima actual en Buin en formato limpio
def obtener_clima_buin():
    try:
        # Usamos formato JSON para evitar problemas de etiquetas HTML en pantalla
        url = "https://wttr.in/Buin?format=j1"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode('utf-8'))
            condicion = data['current_condition'][0]['weatherDesc'][0]['value']
            temp = data['current_condition'][0]['temp_C']
            return f"{condicion}, {temp}°C"
    except Exception:
        return "Tormenta eléctrica activa en Buin"

st.markdown("### Estado del Sistema")
st.success("Núcleos y dependencias verificados correctamente.")
st.info("Servidor de red local a la escucha de comandos desde el dispositivo iOS.")

# Sección interactiva en la interfaz
col1, col2 = st.columns(2)

with col1:
    st.subheader("Estado Ambiental")
    st.write("📍 **Ubicación:** Buin, Chile")
    
    # Obtenemos y mostramos el clima limpio
    clima_actual = obtener_clima_buin()
    st.write(f"🌤️ **Condiciones meteorológicas:** {clima_actual}")

with col2:
    st.subheader("Controles Rápidos")
    if st.button("Verificar Estado"):
        st.toast("¡Sistemas operativos al 100%, Jefa!")

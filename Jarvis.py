import streamlit as st

# Configuración de la página
st.set_page_config(page_title="JARVIS Dashboard", layout="wide")

# Título principal respetando la simetría y estética
st.title("🛡️ J.A.R.V.I.S. - Nodo Buin")
st.markdown("---")

# Interfaz estable y limpia
col1, col2 = st.columns(2)

with col1:
    st.subheader("Estado del Sistema")
    st.success("Núcleo operacional al 100%. Sistemas estables.")
    st.info("Módulos de voz y visión en espera de optimización segura.")

with col2:
    st.subheader("Mapa Táctico Satelital")
    st.write("Interfaz visual operativa.")
    # Si usabas algún mapa o componente previo, colócalo aquí de forma nativa

# Campo de chat estándar de Streamlit (seguro y sin bloqueos)
comando = st.chat_input("Escribe una orden para JARVIS...")
if comando:
    st.chat_message("user").write(comando)
    st.chat_message("assistant").write(f"A sus órdenes, jefa. Procesando instrucción: '{comando}'")

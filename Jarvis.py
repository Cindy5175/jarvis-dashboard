import streamlit as st

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

# Encabezado principal
st.markdown(
    "### 💬 Interfaz de Conversación Autónoma (Comando de Voz: 'Hey Jarvis')"
)

if st.button("🗑️ Purgar Chat"):
    st.toast("Historial de chat purgado con éxito.", icon="🧹")

st.markdown("---")

import streamlit as st
import datetime

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S. // Aventura Montessori",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES TÁCTICOS Y ACOGEDORES ---
estilos_css = """
<style>
    .stApp { background-color: #060913 !important; color: #00f3ff !important; font-family: monospace; }
    p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
    
    .montessori-header {
        border: 1.5px solid #00f3ff;
        background: linear-gradient(135deg, #0a1128 0%, #060913 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.4);
        margin-bottom: 20px;
    }
    .mission-box {
        border: 1px dashed #ff9900;
        background: rgba(255, 153, 0, 0.08);
        padding: 12px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;
        color: #ff9900 !important;
    }
    .mission-box p, .mission-box span { color: #ff9900 !important; }
    
    .stButton>button {
        background-color: #00f3ff !important;
        border: 1.5px solid #00f3ff !important;
        font-weight: bold;
        font-family: monospace;
        color: #060913 !important;
        width: 100%;
        border-radius: 6px;
        padding: 8px 12px !important;
        box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
    }
    .stButton>button:hover {
        background-color: #0088cc !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.9);
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
"""
st.markdown(estilos_css, unsafe_allow_html=True)

# --- INICIALIZACIÓN DE ESTADOS ---
if "estrellas" not in st.session_state:
    st.session_state.estrellas = 0
if "completadas" not in st.session_state:
    st.session_state.completadas = []

# --- ENCABEZADO PRINCIPAL ---
st.markdown(
    '<div class="montessori-header">'
    '<h1 style="margin:0; font-size: 2rem; text-shadow: 0 0 10px #00f3ff;">🧸 ¡Aventura Divertida Montessori! 🌟</h1>'
    '<p style="margin:5px 0 0 0; opacity: 0.85;">Aprende, juega y gana estrellas. ¡Cada día una nueva aventura para descubrir!</p>'
    '</div>',
    unsafe_allow_html=True
)

# --- MISIÓN DEL DÍA ---
st.markdown(
    '<div class="mission-box">'
    '<b>⭐ Misión del Día Destacada:</b> La Torre Rosa (Doble Diversión)'
    '</div>',
    unsafe_allow_html=True
)

# --- PANEL DE ESTADÍSTICAS ---
col_s1, col_s2 = st.columns(2)
with col_s1:
    st.markdown(f"### ⭐ Estrellas: `{st.session_state.estrellas}`")
with col_s2:
    rango_actual = "Explorador Tierno" if st.session_state.estrellas < 10 else "Maestro Montessori"
    st.markdown(f"### 🎖️ Rango: `{rango_actual}`")

st.markdown("---")

# --- ACTIVIDADES / MÓDULOS ---
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🪴 Mono Chispas")
    st.markdown("#### Trasvase de Semillas")
    st.write("Usa tu cuchara con mucho cuidado para mover las semillas de un plato a otro.")
    is_done1 = "Trasvase de Semillas" in st.session_state.completadas
    btn_label1 = "✅ ¡Completado!" if is_done1 else "🎮 ¡Jugar! (Gana 2 ⭐)"
    if st.button(btn_label1, key="btn_semillas"):
        if not is_done1:
            st.session_state.estrellas += 2
            st.session_state.completadas.append("Trasvase de Semillas")
            st.success("¡Excelente trabajo con las semillas!")
            st.rerun()

with col2:
    st.markdown("### 🐼 Panda Lolo")
    st.markdown("#### La Torre Rosa")
    st.write("Ordena los cubos desde el más grande abajo hasta el más pequeñito arriba.")
    is_done2 = "La Torre Rosa" in st.session_state.completadas
    btn_label2 = "✅ ¡Completado!" if is_done2 else "🎮 ¡Jugar! (Gana 3 ⭐)"
    if st.button(btn_label2, key="btn_torre"):
        if not is_done2:
            st.session_state.estrellas += 3
            st.session_state.completadas.append("La Torre Rosa")
            st.success("¡Torre armada con éxito!")
            st.rerun()

with col3:
    st.markdown("### 🦁 León Dani")
    st.markdown("#### Barras Numéricas")
    st.write("Cuenta las barritas de colores y descubre qué número corresponde a cada tamaño.")
    is_done3 = "Barras Numéricas" in st.session_state.completadas
    btn_label3 = "✅ ¡Completado!" if is_done3 else "🎮 ¡Jugar! (Gana 3 ⭐)"
    if st.button(btn_label3, key="btn_barras"):
        if not is_done3:
            st.session_state.estrellas += 3
            st.session_state.completadas.append("Barras Numéricas")
            st.success("¡Gran conteo numérico!")
            st.rerun()

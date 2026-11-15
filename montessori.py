import streamlit as st

st.set_page_config(
    page_title="Módulo Montessori // Nodo Buin",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos idénticos a la versión lúdica y colorida que te encantó
st.markdown("""
    <style>
        .stApp { background-color: #fff9e6 !important; color: #2c3e50 !important; font-family: 'Comic Sans MS', 'Segoe UI', Tahoma, sans-serif; }
        p, span, label, h1, h2, h3, h4, div { color: #2c3e50; font-family: 'Comic Sans MS', 'Segoe UI', Tahoma, sans-serif; }
        .montessori-header {
            text-align: center;
            padding: 15px 0;
            background: linear-gradient(135deg, #1e90ff, #2ed573);
            color: white;
            border-radius: 15px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }
        .montessori-header h1 { color: white !important; font-size: 2rem; margin: 0; text-shadow: 2px 2px 0px rgba(0,0,0,0.2); }
        .montessori-header p { color: white !important; font-size: 1rem; margin: 5px 0 0 0; }
        
        .badge-estrellas {
            background-color: #ffa502;
            color: white;
            padding: 8px 15px;
            border-radius: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            font-weight: bold;
            display: inline-block;
            margin-bottom: 20px;
        }
        .mascota-guia {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 12px;
            background: #f1f2f6;
            padding: 8px 12px;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: bold;
        }
        .stButton>button {
            background-color: #2ed573 !important;
            color: white !important;
            border: none !important;
            padding: 8px 16px !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            box-shadow: 0 3px 6px rgba(46, 213, 115, 0.3);
            width: 100%;
        }
        .stButton>button:hover { background-color: #26af5f !important; }
    </style>
""", unsafe_allow_html=True)

if "estrellas_montessori" not in st.session_state:
    st.session_state.estrellas_montessori = 0

st.markdown("""
    <div class="montessori-header">
        <h1>🐵 ¡Aventura Divertida Montessori! 🌟</h1>
        <p>Aprende, juega y gana estrellas en el Nodo Buin (Versión Nativa Streamlit)</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f'<div style="text-align: center;"><div class="badge-estrellas">⭐ Estrellas ganadas: {st.session_state.estrellas_montessori}</div></div>', unsafe_allow_html=True)

# Filtro de categorías
categoria = st.radio(
    "Filtrar Actividades:",
    ["Todas", "🔴 Vida Práctica", "🟢 Sensorial", "🟡 Matemáticas", "🔵 Lenguaje"],
    horizontal=True
)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    if categoria in ["Todas", "🔴 Vida Práctica"]:
        st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 20px; border-top: 8px solid #ff4757; box-shadow: 0 6px 12px rgba(0,0,0,0.08); margin-bottom: 20px;">
            <div class="mascota-guia"><span>🐵</span><span>¡Mono Chispas te acompaña!</span></div>
            <h3 style="margin: 0 0 8px 0;">Trasvase de Semillas</h3>
            <p style="color: #57606f; font-size: 0.9rem;">Usa tu cuchara con mucho cuidado para mover las semillas de un plato a otro sin botar nada.</p>
            <p style="font-size: 0.8rem; color: #ff4757; font-weight: bold;">🎁 Premia: ⭐️⭐️</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("¡Jugar Trasvase!", key="btn_1"):
            st.session_state.estrellas_montessori += 2
            st.success("🎉 ¡Excelente trabajo! Ganaste 2 estrellas.")
            st.rerun()

    if categoria in ["Todas", "🟡 Matemáticas"]:
        st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 20px; border-top: 8px solid #ffa502; box-shadow: 0 6px 12px rgba(0,0,0,0.08); margin-bottom: 20px;">
            <div class="mascota-guia"><span>🦁</span><span>¡León Dani te enseña!</span></div>
            <h3 style="margin: 0 0 8px 0;">Barras Numéricas</h3>
            <p style="color: #57606f; font-size: 0.9rem;">Cuenta las barritas de colores y descubre qué número corresponde a cada tamaño.</p>
            <p style="font-size: 0.8rem; color: #ffa502; font-weight: bold;">🎁 Premia: ⭐️⭐️⭐️</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("¡Jugar Barras Numéricas!", key="btn_3"):
            st.session_state.estrellas_montessori += 3
            st.success("🎉 ¡Impresionante! Ganaste 3 estrellas.")
            st.rerun()

with col2:
    if categoria in ["Todas", "🟢 Sensorial"]:
        st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 20px; border-top: 8px solid #2ed573; box-shadow: 0 6px 12px rgba(0,0,0,0.08); margin-bottom: 20px;">
            <div class="mascota-guia"><span>🐼</span><span>¡Panda Lolo te guía!</span></div>
            <h3 style="margin: 0 0 8px 0;">La Torre Rosa</h3>
            <p style="color: #57606f; font-size: 0.9rem;">Ordena los cubos desde el más grande abajo hasta el más pequeñito arriba.</p>
            <p style="font-size: 0.8rem; color: #2ed573; font-weight: bold;">🎁 Premia: ⭐️⭐️⭐️</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("¡Jugar Torre Rosa!", key="btn_2"):
            st.session_state.estrellas_montessori += 3
            st.success("🎉 ¡Fantástico! Ganaste 3 estrellas.")
            st.rerun()

    if categoria in ["Todas", "🔵 Lenguaje"]:
        st.markdown("""
        <div style="background: white; border-radius: 16px; padding: 20px; border-top: 8px solid #1e90ff; box-shadow: 0 6px 12px rgba(0,0,0,0.08); margin-bottom: 20px;">
            <div class="mascota-guia"><span>🐰</span><span>¡Conejo Saltarín te ayuda!</span></div>
            <h3 style="margin: 0 0 8px 0;">Letras de Lija</h3>
            <p style="color: #57606f; font-size: 0.9rem;">Sigue con tu dedito la forma de las letras mientras escuchas su sonido mágico.</p>
            <p style="font-size: 0.8rem; color: #1e90ff; font-weight: bold;">🎁 Premia: ⭐️⭐️</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("¡Jugar Letras de Lija!", key="btn_4"):
            st.session_state.estrellas_montessori += 2
            st.success("🎉 ¡Muy bien hecho! Ganaste 2 estrellas.")
            st.rerun()

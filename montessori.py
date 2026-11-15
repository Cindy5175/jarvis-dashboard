import streamlit as st

st.set_page_config(
    page_title="Módulo Montessori // Nodo Buin",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos idénticos con diseño lúdico, colores vivos y animaciones de estrellas
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
            margin-bottom: 20px;
        }
        .montessori-header h1 { color: white !important; font-size: 2rem; margin: 0; text-shadow: 2px 2px 0px rgba(0,0,0,0.2); }
        .montessori-header p { color: white !important; font-size: 1rem; margin: 5px 0 0 0; }
        
        .banner-dia {
            background: linear-gradient(135deg, #ffa502, #ff4757);
            color: white;
            padding: 12px 20px;
            border-radius: 14px;
            text-align: center;
            font-weight: bold;
            margin-bottom: 20px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            font-size: 1rem;
        }
        
        .badge-estrellas {
            background-color: #ffa502;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            font-weight: bold;
            display: inline-block;
        }
        .badge-rango {
            background-color: #1e90ff;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            font-weight: bold;
            display: inline-block;
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
            padding: 10px 16px !important;
            border-radius: 10px !important;
            font-weight: bold !important;
            box-shadow: 0 3px 6px rgba(46, 213, 115, 0.3);
            width: 100%;
        }
        .stButton>button:hover { background-color: #26af5f !important; }
    </style>
""", unsafe_allow_html=True)

# Inicializar memoria de sesión para estrellas
if "estrellas_montessori" not in st.session_state:
    st.session_state.estrellas_montessori = 0

# Calcular rango actual según estrellas
estrellas = st.session_state.estrellas_montessori
rango = "🐾 Explorador Tierno"
if estrellas >= 10:
    rango = "📖 Genio de las Letras"
if estrellas >= 20:
    rango = "🚀 Maestro del Nodo Buin"

# Cabecera visual
st.markdown("""
    <div class="montessori-header">
        <h1>🐵 ¡Aventura Divertida Montessori! 🌟</h1>
        <p>Aprende, juega y gana estrellas en el Nodo Buin</p>
    </div>
""", unsafe_allow_html=True)

# Banner de Misión del Día
st.markdown("""
    <div class="banner-dia">
        🌟 ¡Misión del Día Destacada: La Torre Rosa (Doble Diversión)! 🐼
    </div>
""", unsafe_allow_html=True)

# Barra de marcadores (Estrellas y Rango)
col_m1, col_m2 = st.columns(2)
with col_m1:
    st.markdown(f'<div style="text-align: center;"><div class="badge-estrellas">⭐ Estrellas: {estrellas}</div></div>', unsafe_allow_html=True)
with col_m2:
    st.markdown(f'<div style="text-align: center;"><div class="badge-rango">Rango: {rango}</div></div>', unsafe_allow_html=True)

st.markdown("---")

# Tarjetas de actividades en dos columnas
col1, col2 = st.columns(2)

with col1:
    # Tarjeta 1: Vida Práctica
    st.markdown("""
    <div style="background: white; border-radius: 16px; padding: 20px; border-top: 8px solid #1e90ff; box-shadow: 0 6px 12px rgba(0,0,0,0.08); margin-bottom: 20px;">
        <div class="mascota-guia"><span>🐵</span><span>¡Mono Chispas te acompaña!</span></div>
        <h3 style="margin: 0 0 8px 0;">Trasvase de Semillas</h3>
        <p style="color: #57606f; font-size: 0.9rem;">Usa tu cuchara con mucho cuidado para mover las semillas de un plato a otro.</p>
        <p style="font-size: 0.8rem; color: #ff4757; font-weight: bold;">🎁 Premia: ⭐️⭐️ (2 Estrellas)</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("¡Jugar Trasvase!", key="btn_1"):
        st.session_state.estrellas_montessori += 2
        st.success("🎉 ¡Excelente trabajo! Completaste 'Trasvase de Semillas' y ganaste 2 estrellas brillantes.")
        st.rerun()

    # Tarjeta 3: Matemáticas
    st.markdown("""
    <div style="background: white; border-radius: 16px; padding: 20px; border-top: 8px solid #ffa502; box-shadow: 0 6px 12px rgba(0,0,0,0.08); margin-bottom: 20px;">
        <div class="mascota-guia"><span>🦁</span><span>¡León Dani te enseña!</span></div>
        <h3 style="margin: 0 0 8px 0;">Barras Numéricas</h3>
        <p style="color: #57606f; font-size: 0.9rem;">Cuenta las barritas de colores y descubre qué número corresponde a cada tamaño.</p>
        <p style="font-size: 0.8rem; color: #ffa502; font-weight: bold;">🎁 Premia: ⭐️⭐️⭐️ (3 Estrellas)</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("¡Jugar Barras Numéricas!", key="btn_3"):
        st.session_state.estrellas_montessori += 3
        st.success("🎉 ¡Impresionante! Completaste 'Barras Numéricas' y ganaste 3 estrellas brillantes.")
        st.rerun()

with col2:
    # Tarjeta 2: Sensorial
    st.markdown("""
    <div style="background: white; border-radius: 16px; padding: 20px; border-top: 8px solid #2ed573; box-shadow: 0 6px 12px rgba(0,0,0,0.08); margin-bottom: 20px;">
        <div class="mascota-guia"><span>🐼</span><span>¡Panda Lolo te guía!</span></div>
        <h3 style="margin: 0 0 8px 0;">La Torre Rosa</h3>
        <p style="color: #57606f; font-size: 0.9rem;">Ordena los cubos desde el más grande abajo hasta el más pequeñito arriba.</p>
        <p style="font-size: 0.8rem; color: #2ed573; font-weight: bold;">🎁 Premia: ⭐️⭐️⭐️ (3 Estrellas)</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("¡Jugar Torre Rosa!", key="btn_2"):
        st.session_state.estrellas_montessori += 3
        st.success("🎉 ¡Fantástico! Completaste 'La Torre Rosa' y ganaste 3 estrellas brillantes.")
        st.rerun()

    # Tarjeta 4: Lenguaje
    st.markdown("""
    <div style="background: white; border-radius: 16px; padding: 20px; border-top: 8px solid #ff4757; box-shadow: 0 6px 12px rgba(0,0,0,0.08); margin-bottom: 20px;">
        <div class="mascota-guia"><span>🐰</span><span>¡Conejo Saltarín te ayuda!</span></div>
        <h3 style="margin: 0 0 8px 0;">Letras de Lija</h3>
        <p style="color: #57606f; font-size: 0.9rem;">Sigue con tu dedito la forma de las letras mientras escuchas su sonido mágico.</p>
        <p style="font-size: 0.8rem; color: #1e90ff; font-weight: bold;">🎁 Premia: ⭐️⭐️ (2 Estrellas)</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("¡Jugar Letras de Lija!", key="btn_4"):
        st.session_state.estrellas_montessori += 2
        st.success("🎉 ¡Muy bien hecho! Completaste 'Letras de Lija' y ganaste 2 estrellas brillantes.")
        st.rerun()

import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

# Estilos CSS personalizados (Fondo negro y estética neón azul)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #050505;
        color: #00f0ff;
    }
    .neon-header {
        color: #00f0ff;
        font-size: 2rem;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 240, 255, 0.6);
        margin-bottom: 0px;
    }
    .metric-box {
        background-color: #000000;
        border: 1px solid #00f0ff;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 12px;
        box-shadow: 0 0 8px rgba(0, 240, 255, 0.2);
    }
    .metric-title {
        font-size: 0.8em;
        color: #00f0ff;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 1.2em;
        font-weight: bold;
        color: #00f0ff;
    }
    .metric-sub {
        font-size: 0.8em;
        color: #00ff66;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Encabezado principal
st.markdown('<div class="neon-header">J.A.R.V.I.S IA</div>', unsafe_allow_html=True)

if st.button("🗑️ Purgar Chat"):
    st.toast("Historial purgado con éxito.", icon="🧹")

st.markdown("---")

# Distribución principal: Izquierda (Módulos de Telemetría), Derecha (Chat + Mapas y Globo 3D)
col_left, col_right = st.columns([1, 2], gap="medium")

with col_left:
    st.markdown("#### ⚡ Telemetría y Sistemas")

    # Bloque 1: Ubicación Base
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Ubicación Base</div>
            <div class="metric-value">Buin, CL</div>
            <div class="metric-sub">↑ Seguro / Biometría OK</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Bloque 2: Clima Real
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Clima Real (Buin)</div>
            <div class="metric-value">21.1 °C</div>
            <div class="metric-sub">↑ Viento: 9.2 km/h</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Bloque 3: Estado del Sistema
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Estado del Sistema</div>
            <div class="metric-value">99.8% Neural</div>
            <div class="metric-sub">↑ Quantum Core</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Bloque 4: Latencia de Red
    st.markdown(
        """
        <div class="metric-box">
            <div class="metric-title">Latencia de Red</div>
            <div class="metric-value">0.38 ms</div>
            <div class="metric-sub">↑ Óptimo</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown("#### 🎙️ Núcleo Conversacional")

    chat_container = st.container(height=220)

    with chat_container:
        st.chat_message("assistant").write(
            "Sistemas en línea, Cindy. Enlace cartográfico y globo táctico activados. ¿Qué orden ejecutamos hoy?"
        )

    user_input = st.chat_input("Escriba su comando o diga 'Hey Jarvis'...")

    if user_input:
        with chat_container:
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write(
                f"Comando procesado correctamente: '{user_input}'"
            )

    st.markdown("---")
    st.markdown("#### 🌍 Enlace Cartográfico y Globo Táctico")

    # Coordenadas base para Buin, Chile (-33.7333, -70.7333)
    map_data = pd.DataFrame(
        {
            "latitude": [-33.7333],
            "longitude": [-70.7333],
            "name": ["Buin Central"],
        }
    )

    map_col1, map_col2 = st.columns(2)

    with map_col1:
        st.markdown(
            "<small style='color: #00f0ff;'>🗺️ Mapa Cartográfico</small>",
            unsafe_allow_html=True,
        )
        layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position=["longitude", "latitude"],
            get_color=[0, 240, 255, 200],
            get_radius=400,
            pickable=True,
        )
        view_state = pdk.ViewState(
            latitude=-33.7333, longitude=-70.7333, zoom=11, pitch=30
        )
        r_map = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style="mapbox://styles/mapbox/dark-v10",
            tooltip={"text": "{name} - Buin, CL"},
        )
        st.pydeck_chart(r_map, use_container_width=True, height=220)

    with map_col2:
        st.markdown(
            "<small style='color: #00f0ff;'>🌐 Globo Terráqueo 3D</small>",
            unsafe_allow_html=True,
        )
        globe_view = pdk.ViewState(
            latitude=-33.7333,
            longitude=-70.7333,
            zoom=1.5,
            pitch=0,
            projection="globe",
        )
        r_globe = pdk.Deck(
            views=[pdk.View(type="MapView")],
            initial_view_state=globe_view,
            tooltip={"text": "Buin, Chile - Nodo Activo"},
        )
        st.pydeck_chart(r_globe, use_container_width=True, height=220)

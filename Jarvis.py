import pandas as pd
import pydeck as pdk
import streamlit as st

# Configuración inicial de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónomo", page_icon="⚡", layout="wide"
)

# Estilos CSS personalizados (Estética oscura y neón azul)
st.markdown(
    """
    <style>
    .stApp {
        background-color: #050505;
        color: #00f0ff;
    }
    .metric-box {
        background-color: #0a0e14;
        border: 1px solid #00f0ff;
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .metric-title {
        font-size: 0.75em;
        color: #8a99ad;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-value {
        font-size: 1.1em;
        font-weight: bold;
        color: #00f0ff;
    }
    .metric-sub {
        font-size: 0.75em;
        color: #00ff66;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Encabezado principal
st.markdown("## J.A.R.V.I.S IA Autónomo")
st.markdown(
    "<small style='color: #8a99ad;'>Taller de Inteligencia Autónoma | Buin, Chile</small>",
    unsafe_allow_html=True,
)

col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    if st.button("🗑️ Purgar Chat"):
        st.toast("Historial de chat purgado con éxito.", icon="🧹")

st.markdown("---")

# Distribución principal: Izquierda (Módulos), Derecha (Chat arriba + Mapas compactos abajo)
col_left, col_right = st.columns([1, 2], gap="medium")

with col_left:
    st.markdown("#### ⚡ Telemetría y Sistemas")

    # Módulo 1: Ubicación Base
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

    # Módulo 2: Clima Real
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

    # Módulo 3: Estado del Sistema
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

    # Módulo 4: Latencia de Red
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
    # --- 1. CAJA DE CHAT ARRIBA ---
    st.markdown("#### 🎙️ Núcleo Conversacional")

    chat_container = st.container(height=200)

    with chat_container:
        st.chat_message("assistant").write(
            "Sistemas operativos, Cindy. Panel táctico configurado. ¿Qué orden ejecutamos hoy?"
        )

    user_input = st.chat_input("Escriba su comando o diga 'Hey Jarvis'...")

    if user_input:
        with chat_container:
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write(
                f"Comando procesado: '{user_input}'"
            )

    st.markdown("---")

    # --- 2. CONTROLES Y MAPAS ABAJO ---
    st.markdown("#### 🌍 Enlace Cartográfico y Globo Táctico")

    ctrl_col1, ctrl_col2 = st.columns(2)
    with ctrl_col1:
        modo_noche = st.toggle("🌙 Modo Noche / Día", value=True)
    with ctrl_col2:
        tipo_mapa = st.selectbox(
            "Capa Cartográfica", ["Calles y Ciudades", "Satélite"], index=0
        )

    # Definir estilos de mapa según el modo y selector
    if modo_noche:
        map_style = "mapbox://styles/mapbox/dark-v10"
    else:
        map_style = (
            "mapbox://styles/mapbox/streets-v11"
            if tipo_mapa == "Calles y Ciudades"
            else "mapbox://styles/mapbox/satellite-v9"
        )

    map_data = pd.DataFrame(
        {
            "latitude": [-33.7333],
            "longitude": [-70.7333],
            "name": ["Buin Central"],
        }
    )

    # Mapas compactos lado a lado
    map_col1, map_col2 = st.columns(2)

    with map_col1:
        st.markdown(
            "<small style='color: #00f0ff;'>🗺️ Mapa Cartográfico (Calles)</small>",
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
            latitude=-33.7333, longitude=-70.7333, zoom=12, pitch=30
        )
        r_map = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            map_style=map_style,
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

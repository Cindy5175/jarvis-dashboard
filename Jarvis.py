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
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .metric-title {
        font-size: 0.8em;
        color: #8a99ad;
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
st.markdown(
    "### 💬 Interfaz de Conversación Autónoma (Comando de Voz: 'Hey Jarvis')"
)

col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    if st.button("🗑️ Purgar Chat"):
        st.toast("Historial de chat purgado con éxito.", icon="🧹")

st.markdown("---")

# Distribución clásica original: Izquierda (Módulos de Telemetría), Derecha (Mapas / Globo + Chat abajo)
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

    st.markdown(
        "<small style='color: #8a99ad;'>J.A.R.V.I.S. IA Autónomo — Taller de Inteligencia Autónoma | Buin, Chile.</small>",
        unsafe_allow_html=True,
    )

with col_right:
    st.markdown("#### 🌍 Enlace Cartográfico y Globo Táctico")

    # Coordenadas base para Buin, Chile (-33.7333, -70.7333)
    map_data = pd.DataFrame(
        {"latitude": [-33.7333], "longitude": [-70.7333]}
    )

    # Sub-columnas a la derecha para mostrar Mapa y Globo lado a lado
    map_col1, map_col2 = st.columns(2)

    with map_col1:
        st.markdown(
            "<small style='color: #00f0ff;'>🗺️ Mapa Cartográfico (Buin)</small>",
            unsafe_allow_html=True,
        )
        st.map(map_data, zoom=10, use_container_width=True)

    with map_col2:
        st.markdown(
            "<small style='color: #00f0ff;'>🌐 Globo Terráqueo 3D</small>",
            unsafe_allow_html=True,
        )
        globe_view = pdk.ViewState(
            latitude=-33.7333,
            longitude=-70.7333,
            zoom=2,
            pitch=0,
            projection="globe",
        )
        r = pdk.Deck(
            views=[pdk.View(type="MapView")],
            initial_view_state=globe_view,
            tooltip={"text": "Buin, Chile - Núcleo Activo"},
        )
        st.pydeck_chart(r, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 🎙️ Núcleo Conversacional")

    # Contenedor del historial de chat abajo
    chat_container = st.container(height=300)

    with chat_container:
        st.chat_message("assistant").write(
            "Sistemas restaurados a la interfaz clásica, Cindy. ¿Qué orden ejecutamos hoy?"
        )

    # Entrada de texto del chat
    user_input = st.chat_input("Escriba su comando o diga 'Hey Jarvis'...")

    if user_input:
        with chat_container:
            st.chat_message("user").write(user_input)
            st.chat_message("assistant").write(
                f"Comando ejecutado con éxito: '{user_input}'"
            )

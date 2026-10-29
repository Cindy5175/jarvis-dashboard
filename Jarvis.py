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
    /* Estilo para los botones táctiles neón */
    .stButton button {
        background-color: #000000;
        color: #00f0ff;
        border: 1px solid #00f0ff;
        width: 100%;
        border-radius: 6px;
        font-weight: bold;
    }
    .stButton button:hover {
        background-color: #00f0ff;
        color: #000000;
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

# Distribución principal: Izquierda (Módulo rígido con botones táctiles), Derecha (Chat + Mapas)
col_left, col_right = st.columns([1, 2], gap="medium")

with col_left:
    st.markdown("#### ⚡ Módulos Tácticos del Sistema")

    # Inicializar estados de los botones en la sesión si no existen
    if "show_telemetria" not in st.session_state:
        st.session_state.show_telemetria = True
    if "show_voz" not in st.session_state:
        st.session_state.show_voz = False
    if "show_radar" not in st.session_state:
        st.session_state.show_radar = False
    if "show_clave" not in st.session_state:
        st.session_state.show_clave = False
    if "show_satelite" not in st.session_state:
        st.session_state.show_satelite = False

    # Botones táctiles apilados a la izquierda
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("📊 Telemetría"):
            st.session_state.show_telemetria = not st.session_state.show_telemetria
        if st.button("🎙️ Voz Fluida"):
            st.session_state.show_voz = not st.session_state.show_voz
        if st.button("📡 Radar"):
            st.session_state.show_radar = not st.session_state.show_radar
    with col_b2:
        if st.button("🔑 Clave"):
            st.session_state.show_clave = not st.session_state.show_clave
        if st.button("🛰️ Satelital"):
            st.session_state.show_satelite = not st.session_state.show_satelite

    st.markdown("---")

    # Despliegue condicional según el botón táctil presionado
    if st.session_state.show_telemetria:
        st.markdown("##### 📊 Telemetría del Sistema")
        st.markdown(
            """
            <div class="metric-box">
                <div class="metric-title">Ubicación Base</div>
                <div class="metric-value">Buin, CL</div>
                <div class="metric-sub">↑ Seguro / Biometría OK</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">Clima Real (Buin)</div>
                <div class="metric-value">21.1 °C</div>
                <div class="metric-sub">↑ Viento: 9.2 km/h</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">Estado del Sistema</div>
                <div class="metric-value">99.8% Neural</div>
                <div class="metric-sub">↑ Quantum Core</div>
            </div>
            <div class="metric-box">
                <div class="metric-title">Latencia de Red</div>
                <div class="metric-value">0.38 ms</div>
                <div class="metric-sub">↑ Óptimo</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.show_voz:
        st.markdown("##### 🎙️ Subsistema de Voz Fluida")
        st.markdown(
            """
            <div class="metric-box">
                <div class="metric-title">Estado de Audio</div>
                <div class="metric-value">Activo / gTTS Link</div>
                <div class="metric-sub">↑ Comando 'Hey Jarvis' en escucha</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.show_radar:
        st.markdown("##### 📡 Radar Táctico")
        st.markdown(
            """
            <div class="metric-box">
                <div class="metric-title">Frecuencia de Barrido</div>
                <div class="metric-value">1.4 GHz (Buin Sector)</div>
                <div class="metric-sub">↑ Sin anomalías detectadas</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.show_clave:
        st.markdown("##### 🔑 Protocolo de Claves")
        st.markdown(
            """
            <div class="metric-box">
                <div class="metric-title">Nivel de Autorización</div>
                <div class="metric-value">Omega-1 (Cindy)</div>
                <div class="metric-sub">↑ Encriptación Cuántica OK</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.show_satelite:
        st.markdown("##### 🛰️ Enlace Satelital")
        st.markdown(
            """
            <div class="metric-box">
                <div class="metric-title">Órbita Activa</div>
                <div class="metric-value">SYN-OS 4.2</div>
                <div class="metric-sub">↑ Conexión Estable</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

with col_right:
    st.markdown("#### 🎙️ Núcleo Conversacional")

    chat_container = st.container(height=220)

    with chat_container:
        st.chat_message("assistant").write(
            "Sistemas en línea, Cindy. Panel táctico izquierdo configurado con botones modulares. ¿Qué orden ejecutamos hoy?"
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

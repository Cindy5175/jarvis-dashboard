import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Inyección de Estilos CSS avanzados (Fondo negro, azul neón total y título centrado)
st.markdown("""
    <style>
    /* Fondo negro profundo general */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Centrar el encabezado principal y darle azul neón brillante */
    h1 {
        text-align: center;
        color: #00f3ff !important;
        text-shadow: 0px 0px 10px rgba(0, 243, 255, 0.7);
    }
    
    /* Demás títulos en azul neón */
    h2, h3 {
        color: #00f3ff !important;
        text-shadow: 0px 0px 8px rgba(0, 243, 255, 0.6);
    }
    
    /* Textos generales en azul neón claro / cian */
    p, span, label, div, markdown, .stMarkdown {
        color: #80f9ff !important;
    }
    
    /* Forzar que cualquier cuadro de alerta o info mantenga la estética azul neón (sin verde) */
    div[data-testid="stNotification"], .stAlert {
        background-color: #000a12 !important;
        color: #80f9ff !important;
        border: 1px solid #00f3ff !important;
    }
    
    /* Reducir altura del mapa iframe para que quede como un cuadrado medio */
    iframe {
        height: 200px !important;
        width: 100% !important;
        border-radius: 8px;
        border: 1px solid #00f3ff !important;
    }
    
    /* Cajas de entrada de chat y elementos interactivos */
    .stTextInput>div>div>input {
        background-color: #000a12 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
    }
    
    /* Botones tácticos */
    .stButton>button {
        background-color: #000a12 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px;
        box-shadow: 0px 0px 6px rgba(0, 243, 255, 0.4);
    }
    .stButton>button:hover {
        background-color: #00f3ff !important;
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 JARVIS 4.0 // NOVA")
st.markdown("---")

# Distribución en columnas principales
col_izq, col_centro, col_der = st.columns([1.2, 2, 1.2])

with col_izq:
    st.subheader("📅 Sincronización Temporal")
    
    # Fragmento con actualización automática cada 1 segundo para el segundero en vivo
    @st.fragment(run_every=1)
    def reloj_en_vivo():
        zona_chile = pytz.timezone('America/Santiago')
        ahora_chile = datetime.now(zona_chile)
        
        fecha_actual = ahora_chile.strftime("%d/%m/%Y")
        hora_actual = ahora_chile.strftime("%H:%M:%S")
        
        st.write(f"📌 **Fecha:** {fecha_actual}")
        st.markdown(f"⏱️ **Hora Táctica (Chile):**")
        st.markdown(f"### `{hora_actual}`")

    # Llamada al reloj en vivo
    reloj_en_vivo()
    
    # Enlace satelital Serafín (Cuadrado medio)
    st.markdown("### 🛰️ Enlace satelital Serafín")
    mapa_buin = pd.DataFrame({
        'lat': [-33.7333],
        'lon': [-70.7417]
    })
    st.map(mapa_buin, zoom=11, use_container_width=True)

with col_centro:
    st.subheader("💬 Consola Central / Conexión Gemini")
    
    # Inicializar historial de chat si no existe
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Saludos, Jefa. Núcleos operativos y enlace con Gemini sincronizados."}
        ]

    # Mostrar mensajes del chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de chat central conectada
    if prompt := st.chat_input("Ingrese comando táctico o consulta para Gemini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Respuesta simulada/integrada del núcleo
        respuesta_nucleo = f"Procesamiento autónomo completado para: '{prompt}'. Sistemas al 100%, Jefa."
        st.session_state.messages.append({"role": "assistant", "content": respuesta_nucleo})
        with st.chat_message("assistant"):
            st.markdown(respuesta_nucleo)

with col_der:
    st.subheader("Controles Rápidos")
    if st.button("Verificar Estado de Núcleos"):
        st.toast("¡Sistemas operativos y telemetría al 100%, Jefa!")
        
    st.markdown("### ⚡ Telemetría")
    st.info("Red local iOS: Activa\nServidor Flask: Escuchando\nTormenta Buin: Monitoreada")

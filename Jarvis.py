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

# Inyección de Estilos CSS (Fondo negro, letras azul marino, mapa cuadrado y banner de ondas de IA)
st.markdown("""
    <style>
    /* Fondo negro profundo general */
    .stApp {
        background-color: #000000 !important;
    }
    
    /* Centrar el encabezado principal y darle azul marino brillante */
    h1 {
        text-align: center;
        color: #1E3A8A !important;
        text-shadow: 0px 0px 10px rgba(30, 58, 138, 0.7);
    }
    
    /* Demás títulos en azul marino */
    h2, h3 {
        color: #1E3A8A !important;
        text-shadow: 0px 0px 8px rgba(30, 58, 138, 0.6);
    }
    
    /* Textos generales en azul marino / cian oscuro para mantener la legibilidad */
    p, span, label, div, markdown, .stMarkdown {
        color: #3B82F6 !important;
    }
    
    /* Forzar alertas/infos a diseño oscuro */
    div[data-testid="stNotification"], .stAlert {
        background-color: #000a12 !important;
        color: #3B82F6 !important;
        border: 1px solid #1E3A8A !important;
    }
    
    /* Banner de ondas de IA táctico */
    .banner-ondas {
        width: 100%;
        height: 110px;
        background: linear-gradient(90deg, #000000 0%, #031525 50%, #000000 100%);
        border: 1px solid #1E3A8A;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0px 0px 15px rgba(30, 58, 138, 0.5);
        margin-bottom: 20px;
    }
    
    /* Reducir aún más el mapa para que sea un cuadrado pequeño y compacto */
    iframe {
        height: 180px !important;
        width: 180px !important;
        max-width: 100% !important;
        border-radius: 8px !important;
        border: 1px solid #1E3A8A !important;
        box-shadow: 0px 0px 10px rgba(30, 58, 138, 0.4);
    }
    
    /* Contenedor específico para centrar el mapa */
    .mapa-cuadrado {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    
    /* Cajas de entrada de chat y elementos interactivos */
    .stTextInput>div>div>input {
        background-color: #000a12 !important;
        color: #3B82F6 !important;
        border: 1px solid #1E3A8A !important;
    }
    
    /* Botones tácticos */
    .stButton>button {
        background-color: #000a12 !important;
        color: #3B82F6 !important;
        border: 1px solid #1E3A8A !important;
        border-radius: 6px;
        box-shadow: 0px 0px 6px rgba(30, 58, 138, 0.4);
    }
    .stButton>button:hover {
        background-color: #1E3A8A !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 JARVIS 4.0 // NOVA")

# Inyección del Banner de Ondas Azules estilo IA debajo del encabezado
st.markdown("""
    <div class="banner-ondas">
        <div style="text-align: center; color: #00f3ff; font-family: monospace; font-size: 14px; letter-spacing: 2px; text-shadow: 0px 0px 8px #00f3ff;">
            ||||||| |||| |||||||| || | ||||||||| |||| ||||||<br>
            <span style="font-size: 11px; color: #3B82F6;">[ NÚCLEO NEURAL ACTIVO: CONEXIÓN CUÁNTICA ESTABLE ]</span>
        </div>
    </div>
""", unsafe_allow_html=True)

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
    
    # Enlace satelital Serafín (Cuadrado pequeño)
    st.markdown("### 🛰️ Enlace satelital Serafín")
    mapa_buin = pd.DataFrame({
        'lat': [-33.7333],
        'lon': [-70.7417]
    })
    
    st.markdown('<div class="mapa-cuadrado">', unsafe_allow_html=True)
    st.map(mapa_buin, zoom=10, use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

with col_centro:
    # Espaciado superior para bajar la caja del chat
    st.markdown("<br>", unsafe_allow_html=True)
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

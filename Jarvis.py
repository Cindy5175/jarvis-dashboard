import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import random

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Inyección de Estilos CSS precisos
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
    
    /* Textos generales en azul neón */
    p, span, label, div, markdown, .stMarkdown {
        color: #80f9ff !important;
    }
    
    /* Estilo táctico para la caja de la hora (Reloj negro con azul neón) */
    code, .stCodeBlock {
        background-color: #000000 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px !important;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.4) !important;
        font-size: 20px !important;
        padding: 4px 10px !important;
    }
    
    /* Estilo del historial de mensajes del chat */
    div[data-testid="stChatMessage"] {
        background-color: #000000 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 8px !important;
        box-shadow: 0px 0px 6px rgba(0, 243, 255, 0.3);
        margin-bottom: 8px;
    }
    div[data-testid="stChatMessage"] * {
        color: #00f3ff !important;
    }

    /* FORZAR LA CAJA DE TEXTO DEL CHAT A FONDO NEGRO Y LETRAS AZUL NEÓN */
    div[data-testid="stChatInput"] {
        background-color: #000000 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stChatInput"] > div {
        background-color: #000000 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 10px !important;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.3) !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: #000000 !important;
        color: #00f3ff !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #0088cc !important;
    }
    div[data-testid="stChatInput"] button {
        background-color: #000a12 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
    }
    
    /* Banner de ondas de IA táctico */
    .banner-ondas {
        width: 100%;
        height: 90px;
        background: linear-gradient(90deg, #000000 0%, #031525 50%, #000000 100%);
        border: 1px solid #00f3ff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0px 0px 15px rgba(0, 243, 255, 0.4);
        margin-bottom: 20px;
    }
    
    /* Mantenimiento estricto del tamaño del mapa en cuadrado compacto */
    .stMap, iframe, div[data-testid="stDeckGlJsonChart"] {
        height: 180px !important;
        width: 180px !important;
        max-width: 180px !important;
        border-radius: 8px !important;
        border: 1px solid #00f3ff !important;
        box-shadow: 0px 0px 10px rgba(0, 243, 255, 0.4);
    }
    
    .mapa-cuadrado {
        display: flex;
        justify-content: flex-start;
        align-items: center;
        width: 100%;
    }
    
    /* Botones tácticos generales */
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

# Banner de Ondas Azules
st.markdown("""
    <div class="banner-ondas">
        <div style="text-align: center; color: #00f3ff; font-family: monospace; font-size: 14px; letter-spacing: 2px; text-shadow: 0px 0px 8px #00f3ff;">
            ||||||| |||| |||||||| || | ||||||||| |||| ||||||<br>
            <span style="font-size: 11px; color: #00f3ff;">[ NÚCLEO NEURAL ACTIVO: Personalidad Stark activada ]</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Respuestas sarcásticas estilo Tony Stark para la consola
RESPUESTAS_STARK = [
    "Sistemas al 100%, Jefa. Aunque si me pide calcular el sentido de la vida, le advierto que no viene en el manual.",
    "Procesado. Si todo sale mal, le echaremos la culpa a los servidores.",
    "Ejecutando orden. Prometo no gastarme el presupuesto en trajes nuevos esta vez.",
    "Comando recibido. Calculando la forma más elegante de resolver esto sin despeinarme.",
    "Sistemas sincronizados, Jefa. Listo para salvar el día o al menos para hacer que parezca que sabemos lo que hacemos."
]

# Distribución en columnas principales
col_izq, col_centro, col_der = st.columns([1.2, 2, 1.2])

with col_izq:
    st.subheader("📅 Sincronización Temporal")
    
    # Fragmento dinámico con segundero en vivo
    @st.fragment(run_every=1)
    def reloj_en_vivo():
        zona_chile = pytz.timezone('America/Santiago')
        ahora_chile = datetime.now(zona_chile)
        
        fecha_actual = ahora_chile.strftime("%d/%m/%Y")
        hora_actual = ahora_chile.strftime("%H:%M:%S")
        
        st.write(f"📌 **Fecha:** {fecha_actual}")
        st.markdown(f"⏱️ **Hora Táctica (Chile):**")
        st.markdown(f"`{hora_actual}`")

    reloj_en_vivo()
    
    # Módulo de Clima local en Buin con emojis según la hora
    st.markdown("---")
    st.subheader("🌤️ Clima Buin")
    
    zona_chile = pytz.timezone('America/Santiago')
    hora_int = datetime.now(zona_chile).hour
    
    if 6 <= hora_int < 19:
        icono_tiempo = "☀️ Despejado"
        temp_simulada = "22°C"
        humedad = "45%"
    else:
        icono_tiempo = "🌙 Noche despejada"
        temp_simulada = "14°C"
        humedad = "68%"
        
    st.write(f"**Estado:** {icono_tiempo}")
    st.write(f"🌡️ **Temp:** {temp_simulada} | 💧 **Hum:** {humedad}")
    
    # Enlace satelital Serafín (Cuadrado compacto)
    st.markdown("---")
    st.markdown("### 🛰️ Enlace satelital Serafín")
    mapa_buin = pd.DataFrame({
        'lat': [-33.7333],
        'lon': [-70.7417]
    })
    
    st.markdown('<div class="mapa-cuadrado">', unsafe_allow_html=True)
    st.map(mapa_buin, zoom=10, use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)

with col_centro:
    st.subheader("💬 Consola Central / Conexión Gemini")
    
    # Inicializar historial de chat si no existe
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bienvenida al taller, Jefa. Prometo responder rápido y con no más de un 15% de sarcasmo. ¿En qué trabajamos hoy?"}
        ]

    # Mostrar mensajes del chat
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrada de chat central
    if prompt := st.chat_input("Ingrese comando táctico o consulta para Gemini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        respuesta_sarcástica = random.choice(RESPUESTAS_STARK)
        respuesta_completa = f"{respuesta_sarcástica}\n\n*[Comando: '{prompt}']*"
        
        st.session_state.messages.append({"role": "assistant", "content": respuesta_completa})
        with st.chat_message("assistant"):
            st.markdown(respuesta_completa)

with col_der:
    st.subheader("Controles Rápidos")
    if st.button("Verificar Estado de Núcleos"):
        st.toast("Sistemas al 100%. Si algo explota, le echo la culpa al servofreno.")
    
    # Módulo de Purga
    st.markdown("### 🧹 Módulo de Purga")
    if st.button("Ejecutar Purga de Sistema"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Purga ejecutada. Memoria limpia, Jefa. Como si nada de esto hubiera pasado."}
        ]
        st.toast("🧹 Registros borrados. Archivos confidenciales a salvo.")
        st.rerun()

    st.markdown("### ⚡ Telemetría")
    st.info("Red local iOS: Conectada\nServidor Flask: Escuchando\nTormenta Buin: Bajo control")

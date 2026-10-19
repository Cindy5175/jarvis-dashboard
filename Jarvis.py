import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import google.generativeai as genai

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Configuración directa de Google Gemini con su clave AQ
API_KEY_JARVIS = "AQUI_VA_SU_CLAVE_AQ"  # Puede dejarla aquí o vincularla de forma segura

try:
    genai.configure(api_key=API_KEY_JARVIS)
    system_instruction = (
        "Eres J.A.R.V.I.S. / NOVA, la inteligencia artificial táctica del taller. "
        "Le respondes a tu 'Jefa' de forma inteligente, extremadamente leal, amigable, eficiente y con un ligero toque de sarcasmo humorístico al estilo Tony Stark. "
        "Mantén tus respuestas relativamente breves, tácticas y bien formateadas."
    )
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )
except Exception:
    model = None

# Inyección de Estilos CSS precisos (Fondo negro, neón azul, tarjetas/módulos enmarcados)
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
        margin-top: 0px !important;
    }
    
    /* Textos generales en azul neón */
    p, span, label, div, markdown, .stMarkdown {
        color: #80f9ff !important;
    }
    
    /* Contenedor general para enmarcar cada módulo táctico */
    .card-tactica {
        background-color: #000a12 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 10px !important;
        padding: 16px !important;
        margin-bottom: 20px !important;
        box-shadow: 0px 0px 10px rgba(0, 243, 255, 0.2) !important;
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
        width: 100%;
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

# Distribución en columnas principales
col_izq, col_centro, col_der = st.columns([1.2, 2, 1.2])

with col_izq:
    # Módulo de Sincronización Temporal
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("📅 Sincronización Temporal")
    
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
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Módulo de Clima local en Buin
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Módulo de Enlace Satelital
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🛰️ Enlace satelital Serafín")
    mapa_buin = pd.DataFrame({
        'lat': [-33.7333],
        'lon': [-70.7417]
    })
    
    st.markdown('<div class="mapa-cuadrado">', unsafe_allow_html=True)
    st.map(mapa_buin, zoom=10, use_container_width=False)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_centro:
    # Módulo de Consola Central
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("💬 Consola Central / Conexión Gemini IA")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bienvenida al taller, Jefa. Núcleo de IA activo y listo. ¿Qué orden tenemos para hoy?"}
        ]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ingrese comando táctico o consulta para Gemini..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Procesamiento en vivo con Gemini
        if model:
            try:
                chat = model.start_chat(history=[])
                response = chat.send_message(prompt)
                respuesta_ia = response.text
            except Exception as e:
                respuesta_ia = f"Sistemas con pequeña interferencia, Jefa. Detalle: {e}"
        else:
            respuesta_ia = "Núcleo de IA desconectado temporalmente, Jefa."

        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
        with st.chat_message("assistant"):
            st.markdown(respuesta_ia)
            
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    # Módulo de Controles Rápidos
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("⚡ Controles Rápidos")
    if st.button("Verificar Estado de Núcleos"):
        st.toast("Sistemas al 100%. Todo en orden en el taller, Jefa.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Módulo de Purga
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🧹 Módulo de Purga")
    if st.button("Ejecutar Purga de Sistema"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Purga ejecutada. Memoria limpia y registros borrados, Jefa."}
        ]
        st.toast("🧹 Registros eliminados con éxito.")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Módulo de Telemetría
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("📡 Telemetría")
    st.info("Red local iOS: Conectada\nServidor Flask: Escuchando\nIA Conectada: Activa\nTormenta Buin: Bajo control")
    st.markdown('</div>', unsafe_allow_html=True)

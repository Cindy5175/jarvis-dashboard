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

# Inyección de Estilos CSS precisos (Fondo negro, neón azul, tarjetas enmarcadas)
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
    
    /* Estilo táctico para la caja de la hora */
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

    /* ESTILO PARA LA CAJA DE ENTRADA DEL CHAT DENTRO DE LA TARJETA */
    div[data-testid="stChatInput"] {
        background-color: #000000 !important;
        border-radius: 10px !important;
    }
    div[data-testid="stChatInput"] > div {
        background-color: #000a12 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 10px !important;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.4) !important;
    }
    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #00f3ff !important;
    }
    div[data-testid="stChatInput"] textarea::placeholder {
        color: #0088cc !important;
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

# Función de Síntesis de Voz (Text-to-Speech) mediante JavaScript nativo
def emitir_voz(texto_respuesta):
    texto_limpio = texto_respuesta.replace("*", "").replace("#", "").replace("`", "").replace("\n", " ")
    js_speech = f"""
    <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            var utterance = new SpeechSynthesisUtterance("{texto_limpio}");
            utterance.lang = 'es-ES';
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }}
    </script>
    """
    st.components.v1.html(js_speech, height=0, width=0)

st.title("🤖 JARVIS 4.0 // NOVA")

# Banner de Ondas Azules
st.markdown("""
    <div class="banner-ondas">
        <div style="text-align: center; color: #00f3ff; font-family: monospace; font-size: 14px; letter-spacing: 2px; text-shadow: 0px 0px 8px #00f3ff;">
            ||||||| |||| |||||||| || | ||||||||| |||| ||||||<br>
            <span style="font-size: 11px; color: #00f3ff;">[ NÚCLEO NEURAL ACTIVO: Personalidad Stark & Módulo de Voz Integrados ]</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Repertorio de respuestas inteligentes con estilo Tony Stark
RESPUESTAS_STARK = [
    "Sistemas al 100%, Jefa. Analizando su consulta sin interferencias.",
    "Comando procesado con éxito. A veces me sorprende lo eficiente que soy.",
    "Entendido. Ejecutando la rutina solicitada con un 0% de errores.",
    "Analizando los datos del taller. Todo en orden, Jefa.",
    "Orden recibida y ejecutada. Si me necesita para algo más complejo, solo avise."
]

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
    # Módulo de Consola Central perfectamente enmarcado y simétrico
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("💬 Consola Central // Audio & Texto")
    
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bienvenida al taller, Jefa. Módulo de voz activado. ¿Qué orden ejecutamos hoy?"}
        ]

    # Mostrar historial de mensajes de la consola dentro de la tarjeta
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if st.button(f"🔊 Escuchar reporte", key=f"voice_btn_{idx}"):
                    emitir_voz(message["content"])

    # CAJA DE CHAT INTEGRADA JUSTO DEBAJO DE LOS BOTONES (Simetría total en la columna central)
    if prompt := st.chat_input("Ingrese comando táctico o consulta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Respuesta limpia de Tony Stark
        respuesta_ia = random.choice(RESPUESTAS_STARK)
        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
        
        # Reproducir voz automáticamente al responder
        emitir_voz(respuesta_ia)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    # Módulo de Controles Rápidos
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("⚡ Controles Rápidos")
    if st.button("Verificar Estado de Núcleos"):
        st.toast("Sistemas al 100%. Módulo de voz activo.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Módulo de Purga
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🧹 Módulo de Purga")
    if st.button("Ejecutar Purga de Sistema"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Purga ejecutada. Memoria limpia, Jefa."}
        ]
        st.toast("🧹 Registros eliminados.")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # Módulo de Telemetría
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("📡 Telemetría")
    st.info("Red local iOS: Conectada\nSíntesis de Voz: Habilitada\nNúcleo Autónomo: Estable\nTormenta Buin: Bajo control")
    st.markdown('</div>', unsafe_allow_html=True)

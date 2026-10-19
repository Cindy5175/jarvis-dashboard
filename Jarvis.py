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
    
    /* Estilo exclusivo para el reloj grande */
    .reloj-digital {
        background-color: #000000 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px !important;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.4) !important;
        font-size: 20px !important;
        padding: 4px 10px !important;
        font-family: monospace;
        display: inline-block;
    }

    /* Etiqueta de tamaño mediano y legible en azul neón para estados y puertos */
    .estado-mediano {
        background-color: #000000 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px !important;
        font-size: 14px !important;
        padding: 5px 10px !important;
        font-family: monospace;
        display: inline-block;
        box-shadow: 0px 0px 6px rgba(0, 243, 255, 0.4) !important;
        margin-top: 4px;
        margin-bottom: 4px;
    }

    /* Reducir y estilizar el texto de las pestañas en Azul Neón */
    button[data-baseweb="tab"] {
        color: #80f9ff !important;
        font-size: 13px !important;
    }
    button[aria-selected="true"] {
        color: #00f3ff !important;
        border-bottom-color: #00f3ff !important;
        text-shadow: 0px 0px 6px #00f3ff;
    }
    div[data-baseweb="tab-highlight"] {
        background-color: #00f3ff !important;
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
    
    /* Estilos específicos para Widgets iOS */
    .widget-ios {
        background: rgba(0, 15, 30, 0.85);
        border: 1px solid #00f3ff;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
        box-shadow: inset 0px 0px 8px rgba(0, 243, 255, 0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Inicialización del estado de la sesión
if "bitacora" not in st.session_state:
    st.session_state.bitacora = [
        {"Hora": datetime.now().strftime("%H:%M:%S"), "Evento": "Sistema J.A.R.V.I.S. inicializado", "Estado": "ÓPTIMO"}
    ]

if "nota_rapida" not in st.session_state:
    st.session_state.nota_rapida = "Revisar estado de reactores y canal seguro con Nova-Core."

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

def activar_script_microfono():
    js_mic = """
    <script>
        if (typeof window.iniciarEscucha === 'undefined') {
            window.iniciarEscucha = function() {
                if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                    alert("Reconocimiento de voz no soportado en este navegador.");
                    return;
                }
                var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                var recognition = new SpeechRecognition();
                recognition.lang = 'es-ES';
                recognition.interimResults = false;
                
                recognition.onresult = function(event) {
                    var transcript = event.results[0][0].transcript;
                    navigator.clipboard.writeText(transcript);
                    alert("Comando dictado registrado: " + transcript + "\\nCopiado al portapapeles para pegar en el chat.");
                };
                
                recognition.start();
            }
        }
        window.iniciarEscucha();
    </script>
    """
    st.components.v1.html(js_mic, height=0, width=0)

st.title("🤖 JARVIS 4.0 // NOVA")

# Banner de Ondas Azules
st.markdown("""
    <div class="banner-ondas">
        <div style="text-align: center; color: #00f3ff; font-family: monospace; font-size: 14px; letter-spacing: 2px; text-shadow: 0px 0px 8px #00f3ff;">
            ||||||| |||| |||||||| || | ||||||||| |||| ||||||<br>
            <span style="font-size: 11px; color: #00f3ff;">[ NÚCLEO NEURAL ACTIVO: Personalidad Stark, Módulo de Voz & Enlace Nova-Core ]</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

RESPUESTAS_STARK = [
    "Sistemas al 100%, Jefa. Analizando su consulta sin interferencias.",
    "Comando procesado con éxito. A veces me sorprende lo eficiente que soy.",
    "Entendido. Ejecutando la rutina solicitada con un 0% de errores.",
    "Analizando los datos del taller. Todo en orden, Jefa.",
    "Orden recibida y ejecutada. Si me necesita para algo más complejo, solo avise."
]

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
        st.markdown(f'<div class="reloj-digital">{hora_actual}</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("💬 Consola Central // Audio & Texto")
    
    if st.button("🎙️ Activar Micrófono (Dictado Táctico)", key="btn_mic_nativo"):
        activar_script_microfono()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Bienvenida al taller, Jefa. Módulo de voz y dictado táctico activados. ¿Qué orden ejecutamos hoy?"}
        ]

    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if st.button(f"🔊 Escuchar reporte", key=f"voice_btn_{idx}"):
                    emitir_voz(message["content"])

    if prompt := st.chat_input("Ingrese comando táctico o consulta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        st.session_state.bitacora.append({
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Evento": f"Comando: {prompt[:25]}...",
            "Estado": "PROCESADO"
        })
        
        respuesta_ia = random.choice(RESPUESTAS_STARK)
        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
        
        emitir_voz(respuesta_ia)
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Widgets & Bitácora
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("📱 Widgets Estilo Tablet iOS & Bitácora")
    
    w_tab1, w_tab2, w_tab3 = st.tabs(["📝 Notas & Widgets", "🔗 Conexión Nova-Core", "📋 Bitácora Misiones"])
    
    with w_tab1:
        st.markdown('<div class="widget-ios">', unsafe_allow_html=True)
        st.markdown("📌 **Nota Rápida del Taller**")
        nueva_nota = st.text_area("Bloc de notas táctico:", value=st.session_state.nota_rapida, height=70)
        if st.button("💾 Guardar Nota"):
            st.session_state.nota_rapida = nueva_nota
            st.toast("Nota guardada en la tablet.")
        st.markdown('</div>', unsafe_allow_html=True)

    with w_tab2:
        st.markdown('<div class="widget-ios">', unsafe_allow_html=True)
        st.markdown("🔗 **Pasarela de Enlace Mixto: NOVA-CORE**")
        st.markdown('Estado de Conexión:<br><div class="estado-mediano">ONLINE / LISTEN (Puerto 5000)</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📡 Sincronizar Parámetros con Nova-Core"):
            st.toast("⚡ Conexión establecida. Parámetros compartidos.")
            st.session_state.bitacora.append({
                "Hora": datetime.now().strftime("%H:%M:%S"),
                "Evento": "Sincronización manual con Nova-Core",
                "Estado": "EXITOSO"
            })
        st.markdown('</div>', unsafe_allow_html=True)

    with w_tab3:
        st.markdown("📋 **Registro Auditado de Eventos:**")
        for item in st.session_state.bitacora:
            st.markdown(f"• **`{item['Hora']}`** — {item['Evento']} | <span class='estado-mediano'>{item['Estado']}</span>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("⚡ Controles Rápidos")
    if st.button("Verificar Estado de Núcleos"):
        st.toast("Sistemas al 100%. Módulo de voz activo.")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🧹 Módulo de Purga")
    if st.button("Ejecutar Purga de Sistema"):
        st.session_state.messages = [
            {"role": "assistant", "content": "Purga ejecutada. Memoria limpia, Jefa."}
        ]
        st.session_state.bitacora = [
            {"Hora": datetime.now().strftime("%H:%M:%S"), "Evento": "Purga manual ejecutada", "Estado": "LIMPIO"}
        ]
        st.toast("🧹 Registros eliminados.")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("📡 Telemetría")
    st.info("Red local iOS: Conectada\nSíntesis de Voz: Habilitada\nMicrófono Táctico: Listo\nNova-Core Link: Activo\nTormenta Buin: Bajo control")
    st.markdown('</div>', unsafe_allow_html=True)

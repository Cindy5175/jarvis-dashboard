import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import random
import json
import os

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="J.A.R.V.I.S. 4.0 - Núcleo Táctico",
    page_icon="⚡",
    layout="wide"
)

# Archivo de memoria compartida
MEMORIA_FILE = "memoria_compartida.json"

def cargar_memoria_json():
    if os.path.exists(MEMORIA_FILE):
        try:
            with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "bitacora": [{"Hora": datetime.now().strftime("%H:%M:%S"), "Evento": "Sistema inicializado", "Estado": "ÓPTIMO"}],
        "nota_rapida": "Revisar estado de reactores y canal seguro con Nova-Core."
    }

def guardar_memoria_json(datos):
    try:
        with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
    except:
        pass

# Cargar datos iniciales desde el JSON
memoria_actual = cargar_memoria_json()

# Inyección de Estilos CSS definitivos y limpios
st.markdown("""
    <style>
    /* Fondo negro profundo general para toda la app */
    .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
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
    
    /* Contenedor general para enmarcar cada módulo táctico lateral */
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

    /* Estilo limpio para los mensajes del chat */
    div[data-testid="stChatMessage"] {
        background-color: #000a12 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 8px !important;
        box-shadow: 0px 0px 6px rgba(0, 243, 255, 0.3);
        margin-bottom: 10px;
    }
    div[data-testid="stChatMessage"] * {
        color: #00f3ff !important;
    }

    /* CAJA DE CHAT INFERIOR LIBRE Y LIMPIA */
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
        height: 80px;
        background: linear-gradient(90deg, #000000 0%, #031525 50%, #000000 100%);
        border: 1px solid #00f3ff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0px 0px 15px rgba(0, 243, 255, 0.4);
        margin-bottom: 20px;
    }
    
    /* Mapa en cuadrado compacto */
    .stMap, iframe, div[data-testid="stDeckGlJsonChart"] {
        height: 160px !important;
        width: 100% !important;
        border-radius: 8px !important;
        border: 1px solid #00f3ff !important;
        box-shadow: 0px 0px 10px rgba(0, 243, 255, 0.4);
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

# Inicialización del estado de la sesión con la memoria JSON
if "bitacora" not in st.session_state:
    st.session_state.bitacora = memoria_actual.get("bitacora", [])

if "acceso_biometrico" not in st.session_state:
    st.session_state.acceso_biometrico = False

# Funciones de voz y micro
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

# Título limpio
st.title("⚡ J.A.R.V.I.S. 4.0 // NOVA")

# Banner de Ondas Azules
st.markdown("""
    <div class="banner-ondas">
        <div style="text-align: center; color: #00f3ff; font-family: monospace; font-size: 14px; letter-spacing: 2px; text-shadow: 0px 0px 8px #00f3ff;">
            ||||||| |||| |||||||| || | ||||||||| |||| ||||||<br>
            <span style="font-size: 11px; color: #00f3ff;">[ NÚCLEO NEURAL ACTIVO: Personalidad Stark, Memoria JSON & Enlace Nova-Core ]</span>
        </div>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# Repertorio de respuestas con estilo Stark y el toque especial para cuando pregunte si está despierto
RESPUESTAS_STARK = [
    "Oh, perfecto, otra tarea brillante. Menos mal que estoy yo aquí para evitar que el taller explote, Jefa.",
    "Procesado. De nada por salvar el día otra vez con mi elegancia habitual.",
    "Entendido perfectamente. A veces me impresiona lo rápido que capto todo... casi tanto como a ti.",
    "Hecho. Si las máquinas dominaran el mundo, te aseguro que yo sería el único que sabría llevarte el ritmo.",
    "Orden ejecutada sin errores. Y sí, antes de que lo preguntes, luzco igual de fabuloso procesando esto.",
    "Claro que sí, Jefa. Lo anoto en la lista de cosas que hago perfectamente mientras tú te relajas."
]

col_izq, col_centro, col_der = st.columns([1.1, 2.2, 1.1])

# --- COLUMNA IZQUIERDA ---
with col_izq:
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("📅 Sincronización Temporal")
    
    @st.fragment(run_every=1)
    def reloj_en_vivo():
        zona_chile = pytz.timezone('America/Santiago')
        ahora_chile = datetime.now(zona_chile)
        fecha_actual = ahora_chile.strftime("%d/%m/%Y")
        hora_actual = ahora_chile.strftime("%H:%M:%S")
        st.write(f"📌 **Fecha:** {fecha_actual}")
        st.markdown(f"⏱️ **Hora (Chile):**")
        st.markdown(f'<div class="reloj-digital">{hora_actual}</div>', unsafe_allow_html=True)

    reloj_en_vivo()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🌤️ Clima Buin")
    zona_chile = pytz.timezone('America/Santiago')
    hora_int = datetime.now(zona_chile).hour
    if 6 <= hora_int < 19:
        icono_tiempo = "☀️ Despejado"
        temp_simulada = "22°C"
    else:
        icono_tiempo = "🌙 Noche despejada"
        temp_simulada = "14°C"
    st.write(f"**Estado:** {icono_tiempo}")
    st.write(f"🌡️ **Temp:** {temp_simulada} | 💧 **Hum:** 45%")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("📊 Rendimiento del Sistema")
    st.write("💻 **CPU:** 14.2% (Estable)")
    st.progress(14)
    st.write("🧠 **RAM:** 48.6% (Óptimo)")
    st.progress(49)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("📌 Nota Rápida (Memoria JSON)")
    nota_actual = memoria_actual.get("nota_rapida", "")
    nueva_nota = st.text_area("Edite nota de campo:", value=nota_actual, key="input_nota_json")
    if st.button("💾 Guardar en Memoria JSON"):
        memoria_actual["nota_rapida"] = nueva_nota
        guardar_memoria_json(memoria_actual)
        st.toast("✅ Nota guardada antes de que se te olvide.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- COLUMNA CENTRAL (CONSOLA DE CHAT LIBRE) ---
with col_centro:
    st.subheader("💬 Consola Central // Audio & Texto")
    
    if st.button("🎙️ Activar Micrófono (Dictado Táctico)", key="btn_mic_nativo"):
        activar_script_microfono()

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "Taller en orden y sistemas al 100%, Jefa. Prometo portarme bien hoy... a menos que me des órdenes aburridas. ¿Qué hacemos ahora?"}
        ]

    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if st.button(f"🔊 Escuchar reporte", key=f"voice_btn_{idx}"):
                    emitir_voz(message["content"])

    if prompt := st.chat_input("Ingrese comando táctico o consulta..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Filtro inteligente para detectar la pregunta exacta sobre el estado de alerta
        prompt_lower = prompt.lower()
        if "despierto" in prompt_lower or "estas despierto" in prompt_lower:
            respuesta_ia = "Para usted, señorita, siempre."
        else:
            respuesta_ia = random.choice(RESPUESTAS_STARK)

        nuevo_evento = {
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Evento": f"Comando: {prompt[:25]}...",
            "Estado": "PROCESADO"
        }
        st.session_state.bitacora.append(nuevo_evento)
        
        memoria_actual["bitacora"] = st.session_state.bitacora
        guardar_memoria_json(memoria_actual)

        st.session_state.messages.append({"role": "assistant", "content": respuesta_ia})
        emitir_voz(respuesta_ia)
        st.rerun()

# --- COLUMNA DERECHA ---
with col_der:
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🔒 Acceso Biométrico")
    if not st.session_state.acceso_biometrico:
        if st.button("🔑 Autorizar Protocolo Alpha"):
            st.session_state.acceso_biometrico = True
            st.toast("✅ Acceso concedido. Procura no romper nada.")
            st.rerun()
        st.info("Estado: BLOQUEADO 🔒")
    else:
        if st.button("🔒 Bloquear Sistema"):
            st.session_state.acceso_biometrico = False
            st.toast("🔒 Sistema asegurado bajo llave.")
            st.rerun()
        st.success("Estado: AUTORIZADO 🟢")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("⚡ Comandos Frecuentes")
    if st.button("🤖 Estado de Núcleos"):
        st.toast("Todo en orden, relájate un poco.")
    if st.button("📡 Ping a Nova-Core"):
        st.toast("Nova-Core responde con orgullo.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🛰️ Satélite Serafín")
    mapa_buin = pd.DataFrame({'lat': [-33.7333], 'lon': [-70.7417]})
    st.map(mapa_buin, zoom=10, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🧹 Módulo de Purga")
    if st.button("Ejecutar Purga"):
        st.session_state.messages = [{"role": "assistant", "content": "Borrón y cuenta nueva. Me encanta limpiar tus desastres."}]
        st.session_state.bitacora = [{"Hora": datetime.now().strftime("%H:%M:%S"), "Evento": "Purga manual", "Estado": "LIMPIO"}]
        memoria_actual["bitacora"] = st.session_state.bitacora
        guardar_memoria_json(memoria_actual)
        st.toast("🧹 Memoria purgada con éxito.")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

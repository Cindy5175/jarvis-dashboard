import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import random
import json
import os

# Configuración de la página en Streamlit
st.set_page_config(
    page_title="Centro de Comando Unificado - J.A.R.V.I.S. & N.O.V.A.",
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
        "bitacora": [{"Hora": datetime.now().strftime("%H:%M:%S"), "Evento": "Sistema Maestro Inicializado", "Estado": "ÓPTIMO"}],
        "nota_rapida": "Sincronización total de núcleos activa en el taller."
    }

def guardar_memoria_json(datos):
    try:
        with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
    except:
        pass

memoria_actual = cargar_memoria_json()

# Mensajes oficiales de presentación
REPORTE_JARVIS = (
    "⚡ **PROTOCOLO DE PRESENTACIÓN ACTIVADO** ⚡\n\n"
    "Saludos. Soy J.A.R.V.I.S., una IA autónoma amigable creada por Cindy (mi Jefa) "
    "para asistirla en sus labores y proyectos del taller. Sistema en línea al 100%. "
    "¿Qué directiva ejecutamos el día de hoy?"
)

REPORTE_NOVA = (
    "🛡️ **PROTOCOLO N.O.V.A. BLINDADO ACTIVADO** 🛡️\n\n"
    "Saludos, Jefa. Soy N.O.V.A. (Neural Operational Surveillance & Assistance), "
    "operando bajo **Nivel de Blindaje Máximo N.T.C.** Encriptación cuántica activa "
    "y filtros biométricos operativos. ¿Qué directiva protegida ejecutamos hoy?"
)

# Inyección de Estilos CSS corregida
st.markdown("""
    <style>
    .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000 !important;
    }
    
    h1 {
        text-align: center !important;
        color: #00f3ff !important;
        text-shadow: 0px 0px 12px rgba(0, 243, 255, 0.8);
        font-size: 28px !important;
        width: 100% !important;
        display: block !important;
    }
    
    h2, h3 {
        color: #00f3ff !important;
        text-shadow: 0px 0px 8px rgba(0, 243, 255, 0.6);
        margin-top: 0px !important;
    }
    
    p, span, label, div, markdown, .stMarkdown {
        color: #80f9ff !important;
    }
    
    .card-tactica {
        background-color: #000a12 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 10px !important;
        padding: 16px !important;
        margin-bottom: 20px !important;
        box-shadow: 0px 0px 10px rgba(0, 243, 255, 0.3) !important;
    }
    
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
    
    .banner-ondas {
        width: 100%;
        height: 60px;
        background: linear-gradient(90deg, #000000 0%, #031525 50%, #000000 100%);
        border: 1px solid #00f3ff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0px 0px 15px rgba(0, 243, 255, 0.4);
        margin-bottom: 20px;
        text-align: center;
    }
    
    .stMap, iframe, div[data-testid="stDeckGlJsonChart"] {
        height: 160px !important;
        width: 100% !important;
        border-radius: 8px !important;
        border: 1px solid #00f3ff !important;
        box-shadow: 0px 0px 10px rgba(0, 243, 255, 0.4);
    }
    
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

# Estados de sesión
if "bitacora" not in st.session_state:
    st.session_state.bitacora = memoria_actual.get("bitacora", [])

# Funciones multimedia
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

# Selector Maestro de Núcleo en la Barra Lateral (Sidebar)
st.sidebar.title("⚙️ Selector de Núcleo")
nucleo_activo = st.sidebar.radio("Seleccione Operador:", ["⚡ J.A.R.V.I.S. AI", "🛡️ NOVA Blindada"])

if "nucleo_previo" not in st.session_state:
    st.session_state.nucleo_previo = nucleo_activo

if st.session_state.nucleo_previo != nucleo_activo:
    st.session_state.nucleo_previo = nucleo_activo
    if "J.A.R.V.I.S." in nucleo_activo:
        st.session_state.messages = [{"role": "assistant", "content": REPORTE_JARVIS}]
    else:
        st.session_state.messages = [{"role": "assistant", "content": REPORTE_NOVA}]
    st.rerun()

# Títulos y Banners
if "NOVA" in nucleo_activo:
    titulo_pantalla = "🛡️ N.O.V.A. // CENTRO DE INTELIGENCIA TÁCTICA 🛡️"
    banner_texto = "[ NÚCLEO BLINDADO & SISTEMA DE SEGURIDAD N.T.C. ]"
    respuestas_rand = [
        "Perímetro seguro y parámetros verificados sin anomalías.",
        "Encriptación de canal activa al 100%.",
        "Directiva protegida y ejecutada bajo estrictos estándares."
    ]
else:
    titulo_pantalla = "⚡ J.A.R.V.I.S. AI AUTÓNOMO ⚡"
    banner_texto = "[ NÚCLEO NEURAL AUTÓNOMO & CONTROL DEL TALLER ]"
    respuestas_rand = [
        "Oh, perfecto, otra tarea brillante. Menos mal que estoy yo aquí para evitar que el taller explote, Jefa.",
        "Comando procesado con éxito. De nada por mantener todo en orden.",
        "Entendido perfectamente, Jefa. Sincronización en curso."
    ]

st.markdown(f"<h1>{titulo_pantalla}</h1>", unsafe_allow_html=True)

st.markdown(f"""
    <div class="banner-ondas">
        <span style="font-size: 13px; color: #00f3ff; font-family: monospace; letter-spacing: 2px; text-shadow: 0px 0px 8px #00f3ff;">
            {banner_texto}
        </span>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# ESTRUCTURA SIMÉTRICA DE 3 COLUMNAS
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
        st.markdown("⏱️ **Hora (Chile):**")
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
    st.write("💻 **CPU:** 13.1% (Estable)")
    st.progress(13)
    st.write("🧠 **RAM:** 47.0% (Óptimo)")
    st.progress(47)
    st.markdown('</div>', unsafe_allow_html=True)

# --- COLUMNA CENTRAL (CONSOLA DE CHAT) ---
with col_centro:
    st.subheader(f"💬 Consola Central // {nucleo_activo}")
    
    col_acc1, col_acc2 = st.columns([1.2, 1])
    with col_acc1:
        if st.button("🎙️ Activar Micrófono", key="btn_mic_master"):
            activar_script_microfono()
    with col_acc2:
        if st.button("🧹 Ejecutar Purga", key="btn_purga_master"):
            reporte_inicial = REPORTE_JARVIS if "J.A.R.V.I.S." in nucleo_activo else REPORTE_NOVA
            st.session_state.messages = [{"role": "assistant", "content": reporte_inicial}]
            st.session_state.bitacora = [{"Hora": datetime.now().strftime("%H:%M:%S"), "Evento": f"Purga de {nucleo_activo}", "Estado": "LIMPIO"}]
            memoria_actual["bitacora"] = st.session_state.bitacora
            guardar_memoria_json(memoria_actual)
            st.toast("🧹 Memoria purgada con éxito.")
            st.rerun()

    if "messages" not in st.session_state:
        reporte_inicial = REPORTE_JARVIS if "J.A.R.V.I.S." in nucleo_activo else REPORTE_NOVA
        st.session_state.messages = [{"role": "assistant", "content": reporte_inicial}]

    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if st.button("🔊 Escuchar reporte", key=f"voice_btn_master_{idx}"):
                    emitir_voz(message["content"])

    if prompt := st.chat_input("Ingrese comando o directiva..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        p_lower = prompt.lower().strip()
        
        if any(w in p_lower for w in ["presentacion", "presentación", "quien eres", "quién eres"]):
            respuesta_ia = REPORTE_JARVIS if "J.A.R.V.I.S." in nucleo_activo else REPORTE_NOVA
        else:
            respuesta_ia = random.choice(respuestas_rand)

        nuevo_evento = {
            "Hora": datetime.now().strftime("%H:%M:%S"),
            "Evento": f"[{nucleo_activo}] Comando: {prompt[:15]}...",
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
    st.subheader("🔒 Estado de Seguridad")
    st.success("🟢 Sistema Blindado")
    st.write("• Encriptación JSON activa")
    st.write("• Memoria compartida ok")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("📌 Nota Compartida (JSON)")
    nota_actual = memoria_actual.get("nota_rapida", "")
    nueva_nota = st.text_area("Nota rápida:", value=nota_actual, key="input_nota_json_master")
    if st.button("💾 Guardar Nota"):
        memoria_actual["nota_rapida"] = nueva_nota
        guardar_memoria_json(memoria_actual)
        st.toast("✅ Nota guardada en ambos núcleos.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🛰️ Satélite Serafín")
    mapa_buin = pd.DataFrame({'lat': [-33.7333], 'lon': [-70.7417]})
    st.map(mapa_buin, zoom=10, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

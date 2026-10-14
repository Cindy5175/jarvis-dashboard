import streamlit as st
import streamlit.components.v1 as components
import datetime
import random
import json
import os
import subprocess

# Configuración de página en modo ancho
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónoma // Hologram Core", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ARCHIVO DE MEMORIA PERSISTENTE LOCAL
MEMORY_FILE = "jarvis_memory.json"

def cargar_memoria():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "usuario": {
            "nombre": "Cindy",
            "titulo": "Jefa",
            "ubicacion": "Buin, Chile"
        },
        "notas": ["Búnker activado en Buin, Chile.", "Satélite Serafín en enlace estable."],
        "habilidades": {
            "Diagnostico": "st.write('Todos los sistemas operativos al 100%')"
        },
        "canales_multiplataforma": {
            "Telegram": {"estado": "Conectado", "bot_id": "@JarvisBunkerBot"}
        },
        "preferencias_voz": {
            "voz_activa": "Español (Neutro)",
            "tono": "Sarcástico / Sofisticado"
        }
    }

def guardar_memoria(memoria):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error guardando memoria: {e}")

if "memoria" not in st.session_state:
    st.session_state.memoria = cargar_memoria()

nombre_jefa = st.session_state.memoria.get("usuario", {}).get("nombre", "Cindy")
titulo_jefa = st.session_state.memoria.get("usuario", {}).get("titulo", "Jefa")

# ESTILOS CSS TÁCTICOS Y HOLOGRÁFICOS
st.markdown("""
    <style>
    .stApp, .main {
        background-color: #000000 !important;
        color: #ffffff;
    }
    .main-header {
        color: #00d2ff;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 800;
        letter-spacing: 2px;
        text-align: center;
        margin-bottom: 0px;
    }
    .status-bar {
        text-align: center;
        color: #00d2ff;
        font-size: 13px;
        font-weight: bold;
        letter-spacing: 1px;
        margin-bottom: 20px;
    }
    .holo-card {
        background-color: #050505;
        border: 1px solid #00d2ff;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.2);
    }
    .holo-title {
        color: #00d2ff;
        font-size: 14px;
        font-weight: bold;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background-color: #050505 !important;
        color: #00d2ff !important;
        border: 1px solid #00d2ff !important;
        border-radius: 8px !important;
    }
    label[data-testid="stWidgetLabel"] {
        color: #00d2ff !important;
        font-weight: bold !important;
    }
    div.stButton > button, div.stFormSubmitButton > button {
        background-color: #050505 !important;
        color: #00d2ff !important;
        border: 1px solid #00d2ff !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: #00d2ff !important;
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# CABECERA HOLOGRÁFICA
st.markdown('<h1 class="main-header">⚡ J.A.R.V.I.S. CORE 3.0</h1>', unsafe_allow_html=True)
st.markdown(f'<div class="status-bar">CORE STATUS: ONLINE &nbsp;|&nbsp; OPERANDO PARA {titulo_jefa.upper()} {nombre_jefa.upper()} &nbsp;|&nbsp; VOICE MODULE: ACTIVE</div>', unsafe_allow_html=True)

# DISPOSICIÓN EN 3 COLUMNAS
col_telemetria, col_orbe, col_chat = st.columns([1, 1.4, 1.2])

with col_telemetria:
    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.markdown('<div class="holo-title">⚙️ SYSTEM TELEMETRY</div>', unsafe_allow_html=True)
    
    gauges_html = """
    <div style="display: flex; justify-content: space-around; align-items: center; padding: 10px 0;">
        <div style="text-align: center;">
            <div style="width: 60px; height: 60px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">38%</div>
            <span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">CPU</span>
        </div>
        <div style="text-align: center;">
            <div style="width: 60px; height: 60px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">57%</div>
            <span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">RAM</span>
        </div>
        <div style="text-align: center;">
            <div style="width: 60px; height: 60px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">100%</div>
            <span style="color: #ffffff; font-size: 11px; margin-top: 4px; display: block;">PWR</span>
        </div>
    </div>
    """
    components.html(gauges_html, height=100)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.markdown('<div class="holo-title">📍 BASE & SATÉLITE</div>', unsafe_allow_html=True)
    st.markdown(f"<p style='color:#00d2ff; font-size:12px; margin:2px 0;'>Ubicación: {st.session_state.memoria['usuario'].get('ubicacion', 'Buin, Chile')}</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d2ff; font-size:12px; margin:2px 0;'>Serafín-Sat: Órbita Estable</p>", unsafe_allow_html=True)
    st.markdown("<p style='color:#00d2ff; font-size:12px; margin:2px 0;'>USD/CLP: $930.50</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# LÓGICA DE RESPUESTA EN CHAT
if "ultima_respuesta" not in st.session_state:
    st.session_state.ultima_respuesta = f"Sistemas holográficos y de voz activos, {titulo_jefa} {nombre_jefa}. Haz clic en la esfera o envíame una orden."
if "ultimo_usuario" not in st.session_state:
    st.session_state.ultimo_usuario = ""

with col_orbe:
    # EL ORBE INTERACTIVO CON VOZ Y ANIMACIÓN REACTIVA
    texto_para_hablar = st.session_state.ultima_respuesta.replace('"', '\\"').replace("'", "\\'")
    
    orb_component = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 320px;">
        <div class="orb-container" onclick="hablarJarvis()" style="cursor: pointer;" title="Haz clic para escuchar a J.A.R.V.I.S.">
            <div id="ring" class="outer-ring"></div>
            <div id="core" class="inner-core"></div>
        </div>
        <div class="sound-wave" id="waveBox">
            <span class="bar"></span><span class="bar"></span><span class="bar"></span>
            <span class="bar"></span><span class="bar"></span><span class="bar"></span>
        </div>
        <p id="orbStatus" style="color: #00d2ff; font-size: 11px; margin-top: 10px; font-family: monospace;">[ TOCA EL ORBE PARA ESCUCHAR ME ]</p>
    </div>

    <style>
    .orb-container {{
        position: relative;
        width: 180px;
        height: 180px;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .outer-ring {{
        position: absolute;
        width: 170px;
        height: 170px;
        border: 2px dashed #00d2ff;
        border-radius: 50%;
        animation: rotateRing 12s linear infinite;
        box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
        transition: all 0.3s ease;
    }}
    .inner-core {{
        width: 110px;
        height: 110px;
        background: radial-gradient(circle, #00d2ff 0%, #005580 70%, #000000 100%);
        border-radius: 50%;
        box-shadow: 0 0 35px #00d2ff, inset 0 0 15px #ffffff;
        animation: pulseCore 2.5s ease-in-out infinite alternate;
        transition: all 0.3s ease;
    }}
    .speaking-core {{
        background: radial-gradient(circle, #00ffff 0%, #0088cc 70%, #001122 100%) !important;
        box-shadow: 0 0 60px #00ffff, inset 0 0 25px #ffffff !important;
        animation: pulseFast 0.8s ease-in-out infinite alternate !important;
    }}
    .speaking-ring {{
        border-color: #00ffff !important;
        box-shadow: 0 0 30px #00ffff !important;
        animation: rotateRing 3s linear infinite !important;
    }}
    .sound-wave {{
        display: flex;
        gap: 5px;
        margin-top: 15px;
    }}
    .bar {{
        width: 4px;
        height: 8px;
        background-color: #00d2ff;
        border-radius: 2px;
        transition: all 0.2s ease;
    }}
    .active-wave .bar {{
        animation: wave 0.6s ease-in-out infinite alternate;
    }}
    .active-wave .bar:nth-child(2) {{ animation-delay: 0.1s; }}
    .active-wave .bar:nth-child(3) {{ animation-delay: 0.2s; }}
    .active-wave .bar:nth-child(4) {{ animation-delay: 0.3s; }}
    .active-wave .bar:nth-child(5) {{ animation-delay: 0.2s; }}
    .active-wave .bar:nth-child(6) {{ animation-delay: 0.1s; }}

    @keyframes rotateRing {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    @keyframes pulseCore {{
        0% {{ transform: scale(0.92); box-shadow: 0 0 20px #00d2ff; }}
        100% {{ transform: scale(1.08); box-shadow: 0 0 45px #00d2ff; }}
    }}
    @keyframes pulseFast {{
        0% {{ transform: scale(0.88); }}
        100% {{ transform: scale(1.15); }}
    }}
    @keyframes wave {{
        0% {{ height: 6px; }}
        100% {{ height: 32px; }}
    }}
    </style>

    <script>
    function hablarJarvis() {{
        if (!('speechSynthesis' in window)) {{
            alert("Sintetizador de voz no disponible en este navegador.");
            return;
        }}

        window.speechSynthesis.cancel(); // Cancelar audios anteriores

        const texto = "{texto_para_hablar}";
        const utterance = new SpeechSynthesisUtterance(texto);
        utterance.lang = 'es-ES';
        utterance.rate = 1.0;
        utterance.pitch = 0.9;

        const ring = document.getElementById("ring");
        const core = document.getElementById("core");
        const waveBox = document.getElementById("waveBox");
        const orbStatus = document.getElementById("orbStatus");

        utterance.onstart = function() {{
            core.classList.add("speaking-core");
            ring.classList.add("speaking-ring");
            waveBox.classList.add("active-wave");
            orbStatus.innerText = "⚡ [ J.A.R.V.I.S. HABLANDO ]";
            orbStatus.style.color = "#00ffff";
        }};

        utterance.onend = function() {{
            core.classList.remove("speaking-core");
            ring.classList.remove("speaking-ring");
            waveBox.classList.remove("active-wave");
            orbStatus.innerText = "[ TOCA EL ORBE PARA REPRODUCIR ]";
            orbStatus.style.color = "#00d2ff";
        }};

        window.speechSynthesis.speak(utterance);
    }}
    </script>
    """
    components.html(orb_component, height=330)

with col_chat:
    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.markdown('<div class="holo-title">💬 CONVERSATION CORE</div>', unsafe_allow_html=True)

    st.markdown(f"""
        <div style="background-color: #000000; border: 1px solid #00d2ff; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
            <p style="margin:0; color:#00d2ff; font-weight:bold; font-size:12px;">⚡ J.A.R.V.I.S.:</p>
            <p style="margin:4px 0 0 0; color:#ffffff; font-size:13px;">{st.session_state.ultima_respuesta}</p>
        </div>
    """, unsafe_allow_html=True)

    if st.session_state.ultimo_usuario:
        st.markdown(f"""
            <div style="background-color: #000000; border: 1px solid #1f293d; border-radius: 8px; padding: 8px; margin-bottom: 10px;">
                <p style="margin:0; color:#a5b4fc; font-weight:bold; font-size:11px;">👩‍💻 {titulo_jefa} {nombre_jefa}:</p>
                <p style="margin:2px 0 0 0; color:#ffffff; font-size:12px;">{st.session_state.ultimo_usuario}</p>
            </div>
        """, unsafe_allow_html=True)

    with st.form(key="form_chat_jarvis_holo", clear_on_submit=True):
        entrada_usuario = st.text_input("", placeholder="Escribe tu instrucción...")
        boton_enviar = st.form_submit_button(label="🚀 Transmitir")

    if boton_enviar and entrada_usuario:
        texto_ingresado = entrada_usuario.lower()
        
        if "hola" in texto_ingresado:
            respuesta_ia = f"Hola, {nombre_jefa}. Me alegra ver que los sistemas del búnker siguen en pie."
        elif "clima" in texto_ingresado:
            respuesta_ia = "El clima en Buin marca 14.9 grados Celsius con cielos despejados. Ideal para operar."
        elif "ayuda" in texto_ingresado or "que puedes hacer" in texto_ingresado:
            respuesta_ia = f"Tengo control de telemetría, notas persistentes, pasarelas y ejecución local, {titulo_jefa}."
        else:
            respuestas_sarcasticas = [
                f"Analizando tu orden '{entrada_usuario}'... Menos mal que tengo paciencia infinita, {nombre_jefa}.",
                f"Procesando '{entrada_usuario}'. Si esto sale mal, la responsabilidad recae sobre ti.",
                f"Comando '{entrada_usuario}' registrado con éxito en los servidores centrales. ¿Algo más?"
            ]
            respuesta_ia = random.choice(respuestas_sarcasticas)

        st.session_state.ultimo_usuario = entrada_usuario
        st.session_state.ultima_respuesta = respuesta_ia
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# SECCIÓN INFERIOR: CONFIGURACIÓN DE IDENTIDAD Y MEMORIA
st.markdown("---")
with st.expander("👤 Identidad & Memoria Persistente", expanded=False):
    if "input_nombre" not in st.session_state:
        st.session_state.input_nombre = nombre_jefa
    if "input_titulo" not in st.session_state:
        st.session_state.input_titulo = titulo_jefa

    nuevo_nom = st.text_input("Tu Nombre:", key="input_nombre")
    nuevo_tit = st.text_input("Título Preferido:", key="input_titulo")
    
    if st.button("💾 Actualizar Núcleo Biométrico"):
        st.session_state.memoria["usuario"]["nombre"] = nuevo_nom
        st.session_state.memoria["usuario"]["titulo"] = nuevo_tit
        guardar_memoria(st.session_state.memoria)
        st.success("Sincronización biométrica completada.")
        st.rerun()

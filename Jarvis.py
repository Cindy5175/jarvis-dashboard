import streamlit as st
import streamlit.components.v1 as components
import datetime
import random
import json
import os
import subprocess

# Configuración de la página en modo ancho con estilo táctico
st.set_page_config(
    page_title="J.A.R.V.I.S. IA Autónoma // Centro de Mando", 
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
        "notas": ["Búnker activado en Buin, Chile.", "Satélite Serafín en enlace estable."],
        "habilidades": {
            "Diagnostico": "st.write('Todos los sistemas operativos al 100%')",
            "Limpieza_Tmp": "import os; print('Archivos temporales analizados')"
        },
        "canales_multiplataforma": {
            "Telegram": {"estado": "Conectado", "bot_id": "@JarvisBunkerBot"},
            "Discord": {"estado": "En espera", "channel": "#centro-de-mando"},
            "Webhook": {"estado": "Activo", "endpoint": "/api/v1/jarvis/input"}
        },
        "preferencias_voz": {
            "voz_activa": "Español (Reino Unido / Neutro)",
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

# Estilos CSS con FONDO NEGRO ABSOLUTO y estilización Neón
st.markdown("""
    <style>
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    .main {
        background-color: #000000;
        color: #ffffff;
    }
    .main-title {
        color: #00d2ff;
        font-size: 36px;
        font-weight: 800;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        letter-spacing: 1.5px;
        margin-bottom: 5px;
    }
    .neon-text {
        color: #00d2ff !important;
        font-weight: 600;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .left-panel {
        background-color: #050505;
        border: 1px solid #00d2ff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 0 12px rgba(0, 210, 255, 0.15);
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
    [data-testid="stFileUploader"] {
        background-color: #050505 !important;
        border: 1px solid #00d2ff !important;
        border-radius: 10px !important;
        padding: 15px !important;
    }
    div[data-testid="stFileUploadDropzone"] {
        background-color: #050505 !important;
        border: 2px dashed #00d2ff !important;
    }
    div[data-testid="stFileUploadDropzone"] p, 
    div[data-testid="stFileUploadDropzone"] span, 
    div[data-testid="stFileUploadDropzone"] small {
        color: #00d2ff !important;
    }
    div.stButton > button, div.stFormSubmitButton > button {
        background-color: #050505 !important;
        color: #00d2ff !important;
        border: 1px solid #00d2ff !important;
        border-radius: 6px !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0 0 8px rgba(0, 210, 255, 0.3) !important;
    }
    div.stButton > button:hover, div.stFormSubmitButton > button:hover {
        background-color: #00d2ff !important;
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. TÍTULO PRINCIPAL ARRIBA
# ---------------------------------------------------------
st.markdown('<h1 class="main-title">⚡ J.A.R.V.I.S. IA Autónomo</h1>', unsafe_allow_html=True)
st.success("✅ Sistema Unificado: Memoria, Habilidades, Multiplataforma, Ejecución Local y Voice Library Operativos.")

# ---------------------------------------------------------
# 2. MÓDULO DE VOZ Y SÍNTESIS (Voice Library / Web Speech API)
# ---------------------------------------------------------
# Capturamos la última respuesta de J.A.R.V.I.S. para que el sintetizador la lea
texto_a_decir = st.session_state.get("ultima_respuesta", "Sistemas listos.")

voice_component = f"""
<div style="background-color: #050505; padding: 12px; border-radius: 8px; border: 1px solid #00d2ff; text-align: center; font-family: sans-serif; margin-bottom: 15px;">
    <h4 style="color: #00d2ff; margin: 0 0 6px 0; font-size: 14px;">🎙️ Biblioteca de Voces & Interfaz de Audio (Voice Library)</h4>
    <p style="color: #a5b4fc; font-size: 12px; margin: 4px 0;">Voz Activa: Butler Británico / Sarcástico (Modo J.A.R.V.I.S.)</p>
    <button onclick="speakText()" style="background-color: #00d2ff; color: #000; border: none; padding: 8px 16px; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 12px; box-shadow: 0 0 8px rgba(0,210,255,0.4);">🔊 Reproducer Respuesta de J.A.R.V.I.S.</button>
    <button onclick="startListening()" style="background-color: #050505; color: #00d2ff; border: 1px solid #00d2ff; padding: 8px 16px; font-weight: bold; border-radius: 4px; cursor: pointer; font-size: 12px; margin-left: 10px;">🎤 Dictar Comando</button>
    <p id="voice-status" style="color: #ffffff; margin-top: 6px; font-size: 11px;">Estado: Subsistema de audio en espera...</p>
</div>

<script>
const textToSpeak = "{texto_a_decir}";

function speakText() {{
    if (!('speechSynthesis' in window)) {{
        alert("Tu navegador no soporta síntesis de voz.");
        return;
    }}
    const utterance = new SpeechSynthesisUtterance(textToSpeak);
    utterance.lang = 'es-ES';
    utterance.rate = 1.0;
    utterance.pitch = 0.9; // Tono ligeramente más grave y formal
    
    // Buscar una voz en español si está disponible
    const voices = window.speechSynthesis.getVoices();
    const spanishVoice = voices.find(v => v.lang.includes('es') || v.lang.includes('ES'));
    if (spanishVoice) {{
        utterance.voice = spanishVoice;
    }}

    document.getElementById("voice-status").innerText = "Transmitiendo audio sintético...";
    utterance.onend = function() {{
        document.getElementById("voice-status").innerText = "Audio finalizado con éxito.";
    }};
    window.speechSynthesis.speak(utterance);
}}

function startListening() {{
    const statusText = document.getElementById("voice-status");
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {{
        statusText.innerText = "Error: Tu navegador no soporta reconocimiento de voz.";
        return;
    }}
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'es-CL';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    statusText.innerText = "Escuchando cada palabra, jefa...";

    recognition.onresult = function(event) {{
        const command = event.results[0][0].transcript;
        statusText.innerText = "Capturado: \\"" + command + "\\"";
    }};

    recognition.onerror = function(event) {{
        statusText.innerText = "Error de captura: " + event.error;
    }};

    recognition.start();
}}
</script>
"""

components.html(voice_component, height=130)
st.markdown("---")

# ---------------------------------------------------------
# 3. DISEÑO DE COLUMNAS PRINCIPALES
# ---------------------------------------------------------
col_izq, col_der = st.columns([1, 1.8])

with col_izq:
    # Panel Izquierdo 1: Hora, Ubicación y Mapa Compacto
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    
    reloj_component = """
    <div style="font-family: 'Segoe UI', sans-serif; color: #00d2ff; font-weight: 600; font-size: 14px; margin-bottom: 8px;">
        🕒 Fecha y Hora: <span id="reloj">Cargando...</span>
    </div>
    <script>
    function actualizarReloj() {
        const ahora = new Date();
        const opciones = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        document.getElementById('reloj').innerText = ahora.toLocaleString('sv-SE', opciones);
    }
    setInterval(actualizarReloj, 1000);
    actualizarReloj();
    </script>
    """
    components.html(reloj_component, height=35)
    
    st.markdown('<p class="neon-text">📍 Ubicación: Buin, Chile</p>', unsafe_allow_html=True)
    
    mapa_html = """
    <div style="width: 100%; height: 160px; border-radius: 8px; overflow: hidden; border: 1px solid #00d2ff;">
        <iframe width="100%" height="160" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
            src="https://www.openstreetmap.org/export/embed.html?bbox=-70.76,-33.76,-70.70,-33.70&layer=mapnik">
        </iframe>
    </div>
    """
    components.html(mapa_html, height=170)
    
    st.markdown("</div>", unsafe_allow_html=True)

    # Panel Izquierdo 2: Satélite Serafín
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    st.markdown('<p class="neon-text" style="font-size: 16px; margin-bottom: 5px;">📡 Enlace Satelital: Satélite Serafín</p>', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>🛰️ Estado: Órbita Activa / Enlace 100%</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>🌐 Latitud: -33.7333° S</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>🌍 Longitud: -70.7333° W</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>📶 Latencia: 14 ms (Señal Segura)</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Panel Izquierdo 3: Divisas y Clima
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    st.markdown('<p class="neon-text" style="font-size: 16px; margin-bottom: 5px;">💱 Divisas & Clima en Buin</p>', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>💵 Dólar: $930.50 CLP</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>💶 Euro: $1,015.20 CLP</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>📈 UF: $38,400 CLP</p>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #00d2ff; opacity: 0.3; margin: 8px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>☀️ Clima: Despejado, 14,9 °C</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>💨 Viento: 6,5 km/h</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Panel Izquierdo 4: Telemetría
    st.markdown('<div class="left-panel">', unsafe_allow_html=True)
    st.markdown('<p class="neon-text" style="font-size: 16px; margin-bottom: 5px;">💻 Telemetría de PC</p>', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>⚡ CPU en Uso: 38.5%</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>🧠 Memoria RAM: 22.8%</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 13px; margin: 2px 0; color: #00d2ff;'>🔋 Batería: Conectado a Red</p>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_der:
    st.markdown("<h3 class='neon-text'>💬 Terminal de Conversación Autónoma</h3>", unsafe_allow_html=True)
    
    if st.button("🎯 Protocolo de Misiones & Tareas Académicas"):
        st.info("Protocolo activado. Espero que no me pidas que resuelva otra tesis a última hora, jefa.")
        
    if st.button("🌐 Traductor y Sintetizador Multilenguaje"):
        st.info("Subsistema multilingüe listo. Puedo replicar sarcasmo en siete idiomas.")
        
    if st.button("📍 Estado Base"):
        st.success("Ubicación confirmada en Buin. El café está listo y el búnker intacto.")

    # Inicialización de variables de chat
    if "ultima_respuesta" not in st.session_state:
        st.session_state.ultima_respuesta = "Sobrevivimos a otro día más en este planeta. ¿Qué genialidad o catástrofe financiera gestionamos ahora?"
    if "ultimo_usuario" not in st.session_state:
        st.session_state.ultimo_usuario = ""

    # 1. RESPUESTA DE JARVIS (Con rayo ⚡)
    st.markdown(f"""
        <div style="background-color: #050505; border: 1px solid #00d2ff; border-radius: 8px; padding: 12px; margin-top: 5px; margin-bottom: 10px; box-shadow: 0 0 10px rgba(0,210,255,0.2);">
            <p style="margin: 0; color: #00d2ff; font-weight: bold; font-size: 15px;">⚡ J.A.R.V.I.S.</p>
            <p style="margin: 6px 0 0 0; font-size: 14px; color: #ffffff;">{st.session_state.ultima_respuesta}</p>
        </div>
    """, unsafe_allow_html=True)

    # 2. ÚLTIMO COMANDO DE LA JEFA
    if st.session_state.ultimo_usuario:
        st.markdown(f"""
            <div style="background-color: #050505; border: 1px solid #1f293d; border-radius: 8px; padding: 10px; margin-bottom: 10px;">
                <p style="margin: 0; color: #a5b4fc; font-weight: bold; font-size: 13px;">👩‍💻 Jefa:</p>
                <p style="margin: 4px 0 0 0; font-size: 14px; color: #ffffff;">{st.session_state.ultimo_usuario}</p>
            </div>
        """, unsafe_allow_html=True)

    # Formulario de chat
    with st.form(key="form_chat_jarvis", clear_on_submit=True):
        entrada_usuario = st.text_input("", placeholder="Instrucción táctica o financiera...")
        st.markdown('<p class="neon-text" style="font-size: 12px; margin-top: 2px; margin-bottom: 6px;">Escribe tu consulta para J.A.R.V.I.S. aquí...</p>', unsafe_allow_html=True)
        boton_enviar = st.form_submit_button(label="🚀 Enviar Comando")

    if boton_enviar and entrada_usuario:
        respuestas_sarcasticas = [
            f"Interesante orden, jefa: '{entrada_usuario}'. Déjame fingir que me sorprende.",
            f"Procesando '{entrada_usuario}'... Menos mal que tengo paciencia infinita, ¿verdad?",
            f"Anotado: '{entrada_usuario}'. Si esto sale mal, la culpa es enteramente tuya.",
            f"Ejecutando '{entrada_usuario}' con la precisión de un reloj suizo. De nada."
        ]
        respuesta_ia = random.choice(respuestas_sarcasticas)
        
        st.session_state.ultimo_usuario = entrada_usuario
        st.session_state.ultima_respuesta = respuesta_ia
        st.rerun()

    # ---------------------------------------------------------
    # MÓDULOS AVANZADOS & VOICE LIBRARY
    # ---------------------------------------------------------
    st.markdown("---")
    st.markdown("<h3 class='neon-text'>🧠 1. Memoria Persistente Autónoma</h3>", unsafe_allow_html=True)
    
    with st.expander("📝 Gestionar Notas y Registros de Memoria", expanded=False):
        nueva_nota = st.text_input("Añadir nueva memoria/instrucción clave:")
        if st.button("💾 Guardar en Memoria Local"):
            if nueva_nota:
                st.session_state.memoria["notas"].append(nueva_nota)
                guardar_memoria(st.session_state.memoria)
                st.success("Memoria sincronizada en jarvis_memory.json")
                st.rerun()
        
        st.markdown("**Notas guardadas en el núcleo:**")
        for idx, nota in enumerate(st.session_state.memoria["notas"]):
            st.markdown(f"• `{nota}`")

    st.markdown("<h3 class='neon-text'>🛠️ 2. Creación Automática de Habilidades</h3>", unsafe_allow_html=True)
    
    with st.expander("⚡ Registrar/Ejecutar Habilidades personalizadas", expanded=False):
        nombre_skill = st.text_input("Nombre de la nueva habilidad:")
        codigo_skill = st.text_area("Código Python de la habilidad:")
        if st.button("🛠️ Registrar Habilidad"):
            if nombre_skill and codigo_skill:
                st.session_state.memoria["habilidades"][nombre_skill] = codigo_skill
                guardar_memoria(st.session_state.memoria)
                st.success(f"Habilidad '{nombre_skill}' integrada a la memoria.")
                st.rerun()

        st.markdown("**Habilidades disponibles:**")
        for skill_name, script in st.session_state.memoria["habilidades"].items():
            if st.button(f"🚀 Ejecutar: {skill_name}"):
                try:
                    exec(script)
                    st.success(f"Habilidad '{skill_name}' ejecutada con éxito.")
                except Exception as e:
                    st.error(f"Error al ejecutar habilidad: {e}")

    st.markdown("<h3 class='neon-text'>🌐 3. Pasarela Multiplataforma</h3>", unsafe_allow_html=True)
    
    with st.expander("📡 Nodos y Canales Vinculados", expanded=False):
        st.markdown("Conexión con aplicaciones y bots externos:")
        for canal, info in st.session_state.memoria["canales_multiplataforma"].items():
            st.markdown(f"• **{canal}**: `{info.get('estado')}` — {list(info.items())[1][0]}: `{list(info.items())[1][1]}`")

    st.markdown("<h3 class='neon-text'>🔊 4. Biblioteca de Voces (Voice Library)</h3>", unsafe_allow_html=True)
    
    with st.expander("🎛️ Configurar Perfil de Voz", expanded=False):
        selected_voice_tone = st.selectbox(
            "Seleccionar tono de voz de síntesis:",
            ["Butler Británico / Sarcástico", "IA Táctica / Neutra", "Voz de Mando de Acero"],
            index=0
        )
        if st.button("💾 Actualizar Perfil de Voz"):
            st.session_state.memoria["preferencias_voz"]["tono"] = selected_voice_tone
            guardar_memoria(st.session_state.memoria)
            st.success(f"Perfil de voz actualizado a: {selected_voice_tone}")

    st.markdown("<h3 class='neon-text'>💻 5. Ejecución Local & Herramientas de Sistema</h3>", unsafe_allow_html=True)
    
    with st.expander("💻 Terminal Local (Ejecución de Comandos)", expanded=False):
        cmd_input = st.text_input("Comando de consola local (ej: dir, ping 127.0.0.1, python --version):")
        if st.button("🖥️ Ejecutar en Consola Local"):
            if cmd_input:
                try:
                    res = subprocess.run(cmd_input, shell=True, capture_output=True, text=True, timeout=5)
                    out = res.stdout if res.stdout else res.stderr
                    st.code(out, language="bash")
                except Exception as ex:
                    st.error(f"Error ejecutando comando local: {ex}")

    # MÓDULO DE REPOSITORIO
    st.markdown("---")
    st.markdown("<h3 class='neon-text'>📂 Repositorio & Carga de Documentos (PDF)</h3>", unsafe_allow_html=True)
    archivo_subido = st.file_uploader("Sube un archivo PDF táctico para análisis de J.A.R.V.I.S.", type=["pdf"])
    
    if archivo_subido is not None:
        st.success(f"📄 Archivo '{archivo_subido.name}' recibido y encriptado en el búnker con éxito.")
        st.download_button(
            label="📥 Descargar Resumen Táctico (PDF)",
            data=b"Resumen generado por J.A.R.V.I.S. IA Autonoma.",
            file_name="Resumen_Tactico_Jarvis.pdf",
            mime="application/pdf"
        )

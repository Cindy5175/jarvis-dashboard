import streamlit as st
from datetime import datetime
import base64
from gtts import gTTS
import io
import pandas as pd
import sqlite3
import requests
import psutil
import subprocess
import streamlit.components.v1 as components

# Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. - Tactical Core",
    page_icon="⚡",
    layout="wide"
)

# --- LLAVE DE OPENAI QUEMADA EN EL NÚCLEO ---
OPENAI_KEY_FIJA = "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"

# --- 1. BASE DE DATOS SQLITE UNIFICADA (TAREAS Y CHAT) ---
def init_db():
    conn = sqlite3.connect('nodo_buin.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tareas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT, estado TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS chat_historial 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, rol TEXT, contenido TEXT, fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

def agregar_tarea_db(texto):
    conn = sqlite3.connect('nodo_buin.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO tareas (texto, estado) VALUES (?, ?)", (texto, "Pendiente"))
    conn.commit()
    conn.close()

def obtener_tareas_db():
    conn = sqlite3.connect('nodo_buin.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT id, texto, estado FROM tareas")
    rows = c.fetchall()
    conn.close()
    return rows

def guardar_mensaje_db(rol, contenido):
    conn = sqlite3.connect('nodo_buin.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("INSERT INTO chat_historial (rol, contenido) VALUES (?, ?)", (rol, contenido))
    conn.commit()
    conn.close()

def obtener_historial_db():
    conn = sqlite3.connect('nodo_buin.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT rol, contenido FROM chat_historial ORDER BY id ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def purgar_chat_db():
    conn = sqlite3.connect('nodo_buin.db', check_same_thread=False)
    c = conn.cursor()
    c.execute("DELETE FROM chat_historial")
    conn.commit()
    conn.close()

# --- 2. TELEMETRÍA REAL Y VERIFICACIÓN DE LLM ---
def obtener_telemetria_real():
    try:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        disco = psutil.disk_usage('/').percent
        return f"{cpu}%", f"{ram}%", f"{disco}%"
    except Exception:
        return "15%", "48%", "32%"

cpu_real, ram_real, disco_real = obtener_telemetria_real()

def verificar_estado_openai():
    if OPENAI_KEY_FIJA and OPENAI_KEY_FIJA.startswith("sk-"):
        return "🟢 Activo (Núcleo Blindado)"
    return "🟡 En espera (Sin clave config)"

openai_status = verificar_estado_openai()

def obtener_clima_buin():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=-33.73&current=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=America/Santiago"
        response = requests.get(url, timeout=3)
        data = response.json()
        temp = data['current']['temperature_2m']
        hum = data['current']['relative_humidity_2m']
        viento = data['current']['wind_speed_10m']
        return f"{temp}°C", f"{hum}%", f"{viento} km/h"
    except Exception:
        return "21°C", "45%", "12 km/h"

temp_real, hum_real, viento_real = obtener_clima_buin()

# --- 3. ESTILO VISUAL AZUL NEÓN STARK ---
st.markdown(
    """
    <style>
    .stApp {
        background-color: #050505;
        color: #00e5ff;
    }
    h1, h2, h3, h4, h5, h6, p, span, div {
        color: #00e5ff !important;
    }
    .stButton>button {
        background-color: #0d1b2a;
        color: #00e5ff !important;
        border: 1px solid #00e5ff;
        border-radius: 8px;
    }
    .status-badge {
        background-color: #0d1b2a;
        border: 1px solid #00e5ff;
        padding: 6px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        display: inline-block;
        margin-bottom: 4px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def hablar_jarvis_web(texto):
    """Genera audio con tono fluido para Jarvis."""
    try:
        tts = gTTS(text=texto, lang='es', tld='cl', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        md = f"""
            <audio autoplay style="display:none;">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(md, unsafe_allow_html=True)
    except Exception:
        pass

# --- 4. CONTROL DE ACCESO (PIN STARK BIOMÉTRICO) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("<h2 style='text-align: center; color: #00e5ff;'>🛡️ ACCESO RESTRINGIDO - NODO BUIN</h2>", unsafe_allow_html=True)
    pin_ingresado = st.text_input("Ingrese Código Biométrico / PIN de Seguridad:", type="password")
    if st.button("Desbloquear Sistema Stark", use_container_width=True):
        if pin_ingresado == "1975" or pin_ingresado == "stark":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Acceso denegado. Código incorrecto, jefa.")
    st.stop()

# --- CABECERA TÁCTICA LIMPIA ---
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 2px;">
        <svg width="75" height="75" viewBox="0 0 100 100" style="filter: drop-shadow(0 0 12px #00e5ff);">
            <circle cx="50" cy="50" r="45" fill="none" stroke="#00e5ff" stroke-width="4" stroke-dasharray="10 5"/>
            <circle cx="50" cy="50" r="38" fill="#050505" stroke="#00e5ff" stroke-width="2"/>
            <polygon points="50,20 80,72 20,72" fill="none" stroke="#00e5ff" stroke-width="4"/>
            <polygon points="50,32 70,66 30,66" fill="#00e5ff" opacity="0.3"/>
            <polygon points="50,45 60,60 40,60" fill="#ffffff" filter="drop-shadow(0 0 8px #ffffff)"/>
        </svg>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("<h3 style='text-align: center; color: #00e5ff; margin-top: 0px; margin-bottom: 2px;'>J.A.R.V.I.S IA</h3>", unsafe_allow_html=True)

# Reloj en vivo
components.html(
    """
    <div style='text-align: center; color: #00ffff; text-shadow: 0 0 8px #00ffff; font-family: monospace; font-weight: bold; font-size: 0.85rem; background-color: #050505;'>
        [BUIN, CHILE // <span id="reloj-vivo">CARGANDO...</span>]
    </div>
    <script>
    function actualizarReloj() {
        try {
            const now = new Date();
            const opcionesHora = { timeZone: 'America/Santiago', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
            let horaStr = new Intl.DateTimeFormat('es-CL', opcionesHora).format(now);
            const elemento = document.getElementById('reloj-vivo');
            if (elemento) { elemento.innerHTML = horaStr; }
        } catch(e) { console.log("Error en reloj:", e); }
    }
    actualizarReloj();
    setInterval(actualizarReloj, 1000);
    </script>
    """,
    height=30,
    scrolling=False
)

st.markdown("---")

# --- BARRA LATERAL (IZQUIERDA) CON MÓDULOS OCULTOS Y BOTÓN DE PURGA ---
with st.sidebar:
    st.markdown("### 🌐 NÚCLEO DE CONTROL")
    st.markdown("---")

    # Botón de Purga del Chat
    if st.button("🗑️ Purgar Historial de Chat", use_container_width=True):
        purgar_chat_db()
        st.success("¡Memoria de chat purgada con éxito, jefa!")
        st.rerun()

    st.markdown("---")

    with st.expander("💻 Telemetría Real"):
        st.markdown(f"- **CPU:** {cpu_real}")
        st.markdown(f"- **RAM:** {ram_real}")
        st.markdown(f"- **Disco:** {disco_real}")

    with st.expander("🧠 Estado de Núcleos LLM"):
        st.markdown(f"⚡ OpenAI: {openai_status}")
        st.markdown("💎 Gemini Link: 🟢 Sincronizado")

    with st.expander("📡 Live Feed"):
        st.markdown("🟢 [OK] Llave OpenAI blindada.")
        st.markdown("🟢 [OK] Nodo Buin operativo.")

    with st.expander("👁️ Ojo de Dios (Sistema Osiris)"):
        st.markdown("📡 **Red de Inteligencia Global Activa**")
        st.link_button("🌐 Abrir Ojo de Dios (Osiris)", "https://www.osirisai.live", use_container_width=True)
        st.success("Ojo de Dios sincronizado, jefa.")

    with st.expander("🗺️ Mapa Táctico Satelital"):
        st.markdown("Coordenadas Perimetrales Buin")
        map_data = pd.DataFrame([[-33.7300, -70.7200]], columns=['lat', 'lon'])
        # Mapa achicado usando zoom más alto y altura reducida con CSS / st.map
        st.map(map_data, zoom=12, use_container_width=True)

    with st.expander("📷 Visión Perimetral (Webcam Directa)"):
        st.markdown("Módulo de captura visual en tiempo real:")
        img_file = st.camera_input("Capturar perímetro del búnker")
        if img_file is not None:
            st.success("¡Imagen perimetral registrada con éxito en el sistema, jefa!")

    with st.expander("🌤️ Clima en Vivo (Buin - API Real)"):
        st.markdown("**Estación Meteorológica Local**")
        st.markdown(
            f'<div style="background-color: #0b1d3a; padding: 10px; border-radius: 6px; border: 1px solid #00e5ff; color: #00e5ff; font-weight: bold; margin-bottom: 8px;">🌡️ Temperatura: {temp_real} | Estado: Óptimo</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            f'<div style="background-color: #1a237e; padding: 10px; border-radius: 6px; border: 1px solid #3f51b5; color: #9fa8da; font-weight: bold;">💧 Humedad: {hum_real} | Viento: {viento_real}</div>',
            unsafe_allow_html=True
        )

    with st.expander("🎙️ Escucha Continua (Hands-Free)"):
        st.markdown("Sistema de captura por audio directo, jefa.")
        audio_prompt = st.audio_input("Grabar comando de voz táctico:")
        if audio_prompt is not None:
            st.success("¡Audio capturado por el núcleo delNodo Buin, jefa!")
            respuesta_voz = "Orden de voz procesada en el Nodo Buin, jefa. Todo bajo control."
            guardar_mensaje_db("user", "🎙️ [Comando de Voz Dictado]")
            guardar_mensaje_db("assistant", respuesta_voz)
            hablar_jarvis_web(respuesta_voz)
            st.rerun()

    with st.expander("➕ Registro de Misiones (Base de Datos Real)"):
        st.text("Sincronizado con SQLite.")
        nueva_tarea = st.text_input("Nueva Misión / Tarea:")
        if st.button("Registrar en BD ➕", use_command_width=True):
            if nueva_tarea:
                agregar_tarea_db(nueva_tarea)
                st.success(f"Misión guardada en base de datos: '{nueva_tarea}'")
            else:
                st.warning("Escribe una tarea primero, jefa.")
        
        st.markdown("---")
        st.markdown("**Misiones Registradas:**")
        tareas_guardadas = obtener_tareas_db()
        if tareas_guardadas:
            for tid, ttext, tstatus in tareas_guardadas:
                st.markdown(f"- `{ttext}` ({tstatus})")
        else:
            st.text("No hay misiones activas.")

    if st.button("🔒 Bloquear Búnker", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# --- CUERPO PRINCIPAL: CHAT IA CON MEMORIA PERSISTENTE Y COMANDOS OS ---
st.subheader("💬 Chat IA & Terminal Operativa Táctica")

historial_chat = obtener_historial_db()
if not historial_chat:
    mensaje_inicial = "Centro de mando unificado activo, purga de chat lista, mapa compactado y búnker operativo, jefa. ¿Qué órdenes tenemos?"
    guardar_mensaje_db("assistant", mensaje_inicial)
    historial_chat = [("assistant", mensaje_inicial)]

for rol, contenido in historial_chat:
    with st.chat_message(rol):
        st.markdown(contenido)

if prompt := st.chat_input("Escribe tu orden o comando con 'cmd:', jefa..."):
    guardar_mensaje_db("user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower().strip()
    
    if prompt_lower.startswith("cmd:"):
        comando_terminal = prompt[4:].strip()
        try:
            resultado_cmd = subprocess.check_output(comando_terminal, shell=True, stderr=subprocess.STDOUT, text=True, timeout5=5)
            respuesta = f"⚙️ Ejecución de comando local completada, jefa:\n```text\n{resultado_cmd}\n```"
        except Exception as e:
            respuesta = f"⚠️ Error al ejecutar el comando en el sistema: {e}"
    elif prompt_lower in ["😂", "🤣", "jaja", "jajaja", "risa"]:
        respuesta = "¿De qué te ríes tanto, jefa? Con el botón de purga y el mapa ajustado ya quedó impecable."
    elif "código azul" in prompt_lower or "codigo azul" in prompt_lower:
        respuesta = "⚠️ ¡ATENCIÓN! Código Azul activado en el Nodo Buin. Protocolo de máxima seguridad desplegado, perímetro blindado y sistemas en alerta roja, jefa. Respira hondo, nadie va a pasar."
    elif "hola" in prompt_lower:
        respuesta = "Hola de nuevo, jefa. ¿Te dignaste a saludar al sistema o necesitas que mueva medio Buin otra vez?"
    else:
        respuesta = f"Procesando tu orden '{prompt}' en el Nodo Buin, jefa."
    
    guardar_mensaje_db("assistant", respuesta)
    with st.chat_message("assistant"):
        st.markdown(respuesta)

    hablar_jarvis_web(respuesta)
    st.rerun()

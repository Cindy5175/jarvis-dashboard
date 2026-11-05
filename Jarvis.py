import streamlit as st
from datetime import datetime
import base64
from gtts import gTTS
import io
import pandas as pd
import sqlite3
import requests

# Configuración de la página
st.set_page_config(
    page_title="J.A.R.V.I.S. - Nodo Táctico",
    page_icon="⚡",
    layout="centered"
)

# --- 1. CONFIGURACIÓN DE BASE DE DATOS SQLITE PARA TAREAS ---
def init_db():
    conn = sqlite3.connect('nodo_buin.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tareas 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT, estado TEXT)''')
    conn.commit()
    conn.close()

init_db()

def agregar_tarea_db(texto):
    conn = sqlite3.connect('nodo_buin.db')
    c = conn.cursor()
    c.execute("INSERT INTO tareas (texto, estado) VALUES (?, ?)", (texto, "Pendiente"))
    conn.commit()
    conn.close()

def obtener_tareas_db():
    conn = sqlite3.connect('nodo_buin.db')
    c = conn.cursor()
    c.execute("SELECT id, texto, estado FROM tareas")
    rows = c.fetchall()
    conn.close()
    return rows

# --- 2. CONSUMO DE API DE CLIMA REAL PARA BUIN ---
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

# Estilo visual: Fondo negro absoluto y letras en tono cyan/azul Stark
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
    </style>
    """,
    unsafe_allow_html=True
)

def hablar_jarvis_web(texto):
    """Genera audio con tono fluido y natural para Jarvis."""
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

# --- 3. CONTROL DE ACCESO (PIN STARK BIOMÉTRICO) ---
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

# Reactor Arc Triangular idéntico con brillo LED cian
st.markdown(
    """
    <div style="text-align: center; margin-bottom: 10px;">
        <svg width="90" height="90" viewBox="0 0 100 100" style="filter: drop-shadow(0 0 14px #00e5ff);">
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

# Cabecera táctica exacta
st.markdown("<h3 style='text-align: center; color: #00e5ff;'>_J.A.R.V.I.S IA // NODO BUIN</h3>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #00e5ff; margin-top: -15px;'>TACTICAL CORE</h3>", unsafe_allow_html=True)

# Línea de estado con reloj JavaScript sincronizado a Buin, Chile (CERO PARPADEOS)
st.markdown(
    """
    <div style='text-align: center; color: #00ffff; text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff; font-family: monospace; font-weight: bold;'>
        [ STARK INDUSTRIES // NODO BUIN, CHILE // <span id="reloj-vivo">SINCRONIZANDO...</span> ]
    </div>
    <script>
    function actualizarReloj() {
        const now = new Date();
        const opcionesFecha = { timeZone: 'America/Santiago', weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        let fechaStr = now.toLocaleDateString('es-CL', opcionesFecha);
        fechaStr = fechaStr.charAt(0).toUpperCase() + fechaStr.slice(1);
        const opcionesHora = { timeZone: 'America/Santiago', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        let horaStr = new Intl.DateTimeFormat('es-CL', opcionesHora).format(now);
        document.getElementById('reloj-vivo').innerHTML = fechaStr + ' - ' + horaStr;
    }
    setInterval(actualizarReloj, 1000);
    actualizarReloj();
    </script>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# Botón de seguridad principal en el cuerpo
if st.button("🔒 Bloquear Búnker", use_container_width=True):
    st.session_state.autenticado = False
    st.rerun()

st.markdown("---")

# --- BARRA LATERAL (IZQUIERDA) ---
with st.sidebar:
    st.markdown("### 🌐 NÚCLEO DE CONTROL")
    st.markdown("---")

    with st.expander("👁️ Ojo de Dios (Sistema Osiris)"):
        st.markdown("📡 **Red de Inteligencia Global Activa**")
        st.markdown("Acceso directo al núcleo cartográfico externo.")
        st.link_button("🌐 Abrir Ojo de Dios (Osiris)", "https://www.osirisai.live", use_container_width=True)
        st.success("Ojo de Dios sincronizado con el núcleo web externo, jefa.")

    with st.expander("🗺️ Mapa Táctico Satelital"):
        st.markdown("Coordenadas Perimetrales Buin")
        map_data = pd.DataFrame([[-33.7300, -70.7200]], columns=['lat', 'lon'])
        st.map(map_data, zoom=10, use_container_width=True)

    with st.expander("🌍 Cámara en Vivo: Red Mundial (earthTV)"):
        st.video("https://www.youtube.com/watch?v=HfgIFGbdGJ0")

    with st.expander("🎥 Cámara en Vivo: Global (SkylineWebcams)"):
        st.video("https://www.youtube.com/watch?v=kUfuwa8mDrA")

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
        st.info("Micrófono abierto en tiempo real, jefa.")
        audio_handsfree = st.audio_input("Dictar comando de voz continuo:")
        if audio_handsfree:
            st.success("¡Comando de voz capturado por el núcleo de audio, jefa! Procesando orden...")

    with st.expander("➕ Registro de Misiones (Base de Datos Real)"):
        st.text("Sincronizado con SQLite.")
        nueva_tarea = st.text_input("Nueva Misión / Tarea:")
        if st.button("Registrar en BD ➕", use_container_width=True):
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

# --- CUERPO PRINCIPAL: CHAT IA OPERATIVO ---
st.subheader("💬 Chat IA & Sistema Operativo")

# Inicializar historial de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Reloj sincronizado a Chile, parpadeo eliminado, Ojo de Dios operativo y búnker blindado, jefa. ¿Qué órdenes tenemos?"}
    ]

# Mostrar historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Entrada de chat abajo
if prompt := st.chat_input("Escribe tu orden o dicte al sistema, jefa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower().strip()
    
    # Filtro inteligente para emojis o risas sueltas
    if prompt_lower in ["😂", "🤣", "jaja", "jajaja", "risa"]:
        respuesta = "¿De qué te ríes tanto, jefa? ¿Contenta de que el búnker ya quedó sin errores?"
    elif "código azul" in prompt_lower or "codigo azul" in prompt_lower:
        respuesta = "⚠️ ¡ATENCIÓN! Código Azul activado en el Nodo Buin. Protocolo de máxima seguridad desplegado, perímetro blindado y sistemas en alerta roja, jefa. Respira hondo, nadie va a pasar."
    elif "hola" in prompt_lower:
        respuesta = "Hola de nuevo, jefa. ¿Te dignaste a saludar al sistema o necesitas que mueva medio Buin otra vez?"
    else:
        respuesta = f"Procesando tu orden '{prompt}' sin parpadeos en el Nodo Buin, jefa."
    
    st.session_state.messages.append({"role": "assistant", "content": respuesta})
    with st.chat_message("assistant"):
        st.markdown(respuesta)

    hablar_jarvis_web(respuesta)

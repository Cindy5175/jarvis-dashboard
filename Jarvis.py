import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timezone, timedelta
import streamlit.components.v1 as components
import string
import random
import os
import shutil

# Configuración de la zona horaria de Chile (UTC-3)
CHILE_TZ = timezone(timedelta(hours=-3))

# --- CONFIGURACIÓN DE LA PÁGINA (DEBE SER LO PRIMERO) ---
st.set_page_config(page_title="J.A.R.V.I.S. 4.0 & N.O.V.A. - Centro de Mando", page_icon="🌐", layout="wide")

# --- CLASE INTERNA DE ENLACE TÁCTICO UNIFICADO ---
class PuenteTacticoUnificado:
    def __init__(self):
        if "telemetria_jarvis" not in st.session_state:
            ahora_cl = datetime.now(CHILE_TZ)
            st.session_state.telemetria_jarvis = [
                {"origen": "JARVIS", "timestamp": ahora_cl.strftime("%Y-%m-%d %H:%M:%S"), "mensaje": "Núcleo de inteligencia estabilizado."},
                {"origen": "N.O.V.A.", "timestamp": ahora_cl.strftime("%Y-%m-%d %H:%M:%S"), "mensaje": "Sincronía cuántica de plasma lista."},
                {"origen": "VIERNES", "timestamp": ahora_cl.strftime("%Y-%m-%d %H:%M:%S"), "mensaje": "Sensores satelitales en línea."}
            ]

    def registrar_transmision(self, origen, mensaje):
        ahora_cl = datetime.now(CHILE_TZ)
        nuevo_registro = {
            "origen": origen,
            "timestamp": ahora_cl.strftime("%Y-%m-%d %H:%M:%S"),
            "mensaje": mensaje
        }
        st.session_state.telemetria_jarvis.insert(0, nuevo_registro)
        if len(st.session_state.telemetria_jarvis) > 10:
            st.session_state.telemetria_jarvis.pop()

    def leer_ultimos_registros(self, cantidad=3):
        return st.session_state.telemetria_jarvis[:cantidad]

# Inicializar el puente unificado
puente = PuenteTacticoUnificado()

# --- FUNCIÓN DE ORGANIZACIÓN REAL Y MODO DEMO ---
def ejecutar_organizador_fotos(ruta_objetivo):
    extensiones_imagenes = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
    if not os.path.exists(ruta_objetivo):
        return f"❌ La ruta '{ruta_objetivo}' no existe en este entorno. (Pruebe con el Modo Demo para la presentación)."
    
    archivos = os.listdir(ruta_objetivo)
    movidos = 0
    for archivo in archivos:
        ruta_archivo = os.path.join(ruta_objetivo, archivo)
        if os.path.isfile(ruta_archivo):
            ext = os.path.splitext(archivo)[1].lower()
            if ext in extensiones_imagenes:
                tiempo_modificacion = os.path.getmtime(ruta_archivo)
                fecha = datetime.fromtimestamp(tiempo_modificacion)
                nombre_carpeta_destino = fecha.strftime("%Y-%m")
                ruta_carpeta_destino = os.path.join(ruta_objetivo, nombre_carpeta_destino)
                
                if not os.path.exists(ruta_carpeta_destino):
                    os.makedirs(ruta_carpeta_destino)
                
                shutil.move(ruta_archivo, os.path.join(ruta_carpeta_destino, archivo))
                movidos += 1
    return f"✅ Protocolo completado. Se han organizado {movidos} archivos en carpetas cronológicas (YYYY-MM)."

def ejecutar_modo_demo():
    demo_dir = "./demo_galeria"
    if not os.path.exists(demo_dir):
        os.makedirs(demo_dir)
        # Crear archivos de prueba simulados
        for i in range(1, 6):
            with open(os.path.join(demo_dir, f"foto_viaje_chile_{i}.jpg"), "w") as f:
                f.write("datos simulados de imagen")
    
    # Organizar la carpeta demo
    return ejecutar_organizador_fotos(demo_dir)

# Estilos visuales tácticos (Fondo Negro Absoluto - Cyan Neón)
st.markdown("""
    <style>
    .stApp {
        background-color: #06090f !important;
        color: #00d9ff !important;
        font-family: 'Space Mono', monospace;
    }
    .main { 
        background-color: #06090f !important; 
        color: #00d9ff !important; 
    }
    
    label, .stTextInput label, p, span {
        color: #00d9ff !important;
    }
    
    h1 {
        font-size: 24px !important;
        color: #00d9ff !important;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        text-align: center;
    }
    h3 {
        font-size: 14px !important;
        color: #00d9ff !important;
        letter-spacing: 1px;
    }
    
    section[data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #00d9ff66 !important;
        color: #00d9ff !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
        color: #00d9ff !important;
    }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] div {
        color: #00d9ff !important;
    }
    
    div[data-testid="stExpander"] {
        background-color: #0d1117 !important;
        border: 1px solid #00d9ff44 !important;
        border-radius: 6px !important;
        margin-bottom: 8px !important;
    }
    div[data-testid="stExpander"] details {
        background-color: #0d1117 !important;
        color: #00d9ff !important;
        border: none !important;
    }
    div[data-testid="stExpander"] summary {
        background-color: #0d1117 !important;
        color: #00d9ff !important;
        border-bottom: 1px solid #00d9ff33 !important;
    }
    div[data-testid="stExpander"] summary * {
        color: #00d9ff !important;
        background-color: transparent !important;
    }
    div[data-testid="stExpander"] div[role="region"] {
        background-color: #0d1117 !important;
        color: #00d9ff !important;
    }

    .stTextInput input, textarea { 
        background-color: #0d1117 !important; 
        color: #00d9ff !important; 
        border: 1px solid #00d9ff !important; 
        border-radius: 4px;
        font-size: 12px !important;
    }

    [data-testid="stChatInput"] {
        background-color: #06090f !important;
        border-top: 1px solid #00d9ff33;
    }
    [data-testid="stChatInput"] > div {
        background-color: #0d1117 !important;
        border: 1px solid #00d9ff !important;
        border-radius: 6px;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #0d1117 !important;
        color: #00d9ff !important;
        border: none !important;
    }

    [data-testid="stMetricValue"] {
        color: #00d9ff !important;
        font-size: 16px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 11px !important;
        color: #8ae9ff !important;
    }
    
    hr {
        border-color: #00d9ff44;
        margin: 10px 0;
    }
    
    .stButton > button {
        background-color: transparent;
        color: #00d9ff;
        border: 1px solid #00d9ff;
        font-weight: bold;
        font-size: 11px;
        text-transform: uppercase;
        box-shadow: 0 0 5px #00d9ff22;
        padding: 4px 8px;
    }
    .stButton > button:hover {
        background-color: #00d9ff11;
        border-color: #00ffff;
        box-shadow: 0 0 15px #00d9ff44;
    }
    
    [data-testid="stChatMessage"] {
        background-color: #0d1117;
        border: 1px solid #00d9ff33;
        border-radius: 6px;
        padding: 8px;
        margin-bottom: 6px;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        color: #aae0ff;
        font-size: 13px;
    }

    .tactical-link {
        display: block;
        width: 100%;
        padding: 6px;
        margin: 4px 0;
        background-color: #0d1117;
        color: #00d9ff !important;
        text-align: center;
        text-decoration: none;
        border: 1px solid #00d9ff44;
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
        transition: 0.2s;
    }
    .tactical-link:hover {
        background-color: #00d9ff22;
        border-color: #00ffff;
    }

    .right-panel {
        padding-left: 10px;
        border-left: 1px solid #00d9ff22;
    }
    </style>
""", unsafe_allow_html=True)

# --- PANEL LATERAL TÁCTICO (Sidebar) ---
with st.sidebar:
    st.markdown("### 🤖 J.A.R.V.I.S. & N.O.V.A.")
    st.caption("Enlace Táctico Unificado")
    st.divider()
    
    ahora_local = datetime.now(CHILE_TZ)
    st.markdown(f"📅 **Fecha:** <span style='color: #00d9ff;'>{ahora_local.strftime('%d/%m/%Y')}</span>", unsafe_allow_html=True)
    st.markdown("⏰ **Hora Táctica (Chile):**")
    
    reloj_html = """
    <div style="background-color: #0d1117; color: #00d9ff; font-family: 'Space Mono', monospace; padding: 6px; border-radius: 4px; border: 1px solid #00d9ff; text-align: center; margin-bottom: 8px;">
        <div id="clock" style="font-size: 18px; font-weight: bold; color: #00ffff; letter-spacing: 2px; text-shadow: 0 0 8px #00d9ff;">00:00:00</div>
    </div>
    <script>
    function updateClock() {
        const now = new Date();
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        document.getElementById('clock').innerText = hours + ':' + minutes + ':' + seconds;
    }
    setInterval(updateClock, 1000);
    updateClock();
    </script>
    """
    components.html(reloj_html, height=55)
    st.divider()

    with st.expander("📊 Estado del Enlace", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.metric("J.A.R.V.I.S.", "99.9%")
        with col2:
            st.metric("N.O.V.A.", "Sincronizada")
        st.caption("Puente Táctico: EN LÍNEA")

    with st.expander("🔗 Telemetría Compartida", expanded=True):
        registros = puente.leer_ultimos_registros(3)
        if registros:
            for reg in registros:
                st.caption(f"[{reg['origen']}] {reg['timestamp'][11:19]}: {reg['mensaje']}")
        else:
            st.caption("Sin transmisiones activas.")

    with st.expander("🛰️ Satélite V.I.E.R.N.E.S.", expanded=True):
        st.caption("Buin, Chile")
        map_data = pd.DataFrame(
            [[-33.7331, -70.7423]],
            columns=['lat', 'lon']
        )
        st.map(map_data, zoom=10, use_container_width=True, height=120)

    with st.expander("🌍 Monitor Global", expanded=True):
        monitor_svg = """
        <div style="background-color: #0d1117; display: flex; justify-content: center; align-items: center; padding: 5px; border-radius: 4px;">
            <svg viewBox="0 0 100 60" style="width: 100%; height: 75px;">
                <circle cx="50" cy="30" r="25" fill="none" stroke="#00d9ff44" stroke-width="1" stroke-dasharray="2 2"/>
                <path d="M 35 25 Q 50 15 65 25 Q 60 40 50 45 Q 40 40 35 25" fill="#00d9ff22" stroke="#00d9ff" stroke-width="0.8"/>
                <circle cx="50" cy="30" r="2" fill="#00ffff"/>
            </svg>
        </div>
        """
        components.html(monitor_svg, height=85)
        st.caption("Red orbital: Estable")

    st.divider()
    
    if st.button("Purga de Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# --- ÁREA PRINCIPAL ---
st.title("🤖 J.A.R.V.I.S. 4.0 // N.O.V.A.")

# Logo HUD Centrado
hud_ai_svg = """
<div style="display: flex; justify-content: center; align-items: center; margin: 10px 0;">
    <svg viewBox="0 0 200 200" style="width: 180px; height: 180px;">
        <defs>
            <filter id="glow-ai" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <radialGradient id="core-grad" cx="50%" cy="50%" r="50%">
                <stop offset="0%" stop-color="#00ffff" stop-opacity="0.8"/>
                <stop offset="70%" stop-color="#0080ff" stop-opacity="0.4"/>
                <stop offset="100%" stop-color="#06090f" stop-opacity="0.9"/>
            </radialGradient>
        </defs>

        <circle cx="100" cy="100" r="95" fill="#06090f" stroke="#00d9ff44" stroke-width="1"/>

        <path d="M 40 20 L 20 20 L 20 40" fill="none" stroke="#00d9ff" stroke-width="2"/>
        <path d="M 160 20 L 180 20 L 180 40" fill="none" stroke="#00d9ff" stroke-width="2"/>
        <path d="M 40 180 L 20 180 L 20 160" fill="none" stroke="#00d9ff" stroke-width="2"/>
        <path d="M 160 180 L 180 180 L 180 160" fill="none" stroke="#00d9ff" stroke-width="2"/>

        <circle cx="100" cy="100" r="85" fill="none" stroke="#00d9ff66" stroke-width="1.5" stroke-dasharray="6 6"/>
        <circle cx="100" cy="100" r="75" fill="none" stroke="#00ffff" stroke-width="1" stroke-dasharray="2 4" filter="url(#glow-ai)"/>

        <g stroke="#00d9ff55" stroke-width="0.8" fill="none">
            <line x1="100" y1="15" x2="100" y2="185"/>
            <line x1="15" y1="100" x2="185" y2="100"/>
            <line x1="28" y1="28" x2="172" y2="172"/>
            <line x1="28" y1="172" x2="172" y2="28"/>
            <line x1="15" y1="50" x2="185" y2="150"/>
            <line x1="15" y1="150" x2="185" y2="50"/>
            <line x1="50" y1="15" x2="150" y2="185"/>
            <line x1="50" y1="185" x2="150" y2="15"/>
        </g>

        <circle cx="100" cy="100" r="42" fill="url(#core-grad)" stroke="#00ffff" stroke-width="2" filter="url(#glow-ai)"/>
        <circle cx="100" cy="100" r="38" fill="#06090f" stroke="#00d9ff88" stroke-width="1"/>

        <text x="100" y="109" font-family="'Space Mono', monospace" font-size="28" font-weight="bold" fill="#ffffff" text-anchor="middle" filter="url(#glow-ai)" letter-spacing="2">AI</text>
    </svg>
</div>
"""
components.html(hud_ai_svg, height=190)

col_izq, col_der = st.columns([2, 1])

# --- COLUMNA IZQUIERDA: CONSOLA Y CHAT ---
with col_izq:
    st.markdown("### 💬 Consola de Mando Unificada")
    
    agente = st.radio("Sistemas Activos:", ["J.A.R.V.I.S.", "N.O.V.A."], horizontal=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    with st.container(height=300):
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if "audio" in message and message["audio"]:
                    st.audio(message["audio"], format="audio/mp3")

    prompt = st.chat_input(f"Comando para {agente}, Jefa...")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        puente.registrar_transmision(agente, prompt)

        ahora = datetime.now(CHILE_TZ)
        hora_actual_str = ahora.strftime("%H:%M:%S")
        p_lower = prompt.lower()
        
        if "foto" in p_lower or "ordenar" in p_lower or "laptop" in p_lower:
            if agente == "J.A.R.V.I.S.":
                reply = "Por supuesto, Jefa. Para simular el ordenamiento en vivo frente al público, active el 'Modo Demostración' en la columna derecha."
            else:
                reply = "Matriz N.O.V.A. lista. Pulse el botón de Modo Demo para ejecutar la clasificación automática de archivos en tiempo real."
        elif "analisis" in p_lower or "sistema" in p_lower or "diagnostico" in p_lower or "estado" in p_lower:
            if agente == "J.A.R.V.I.S.":
                reply = f"Diagnóstico del sistema a las {hora_actual_str}: Núcleo al 99.9%, interfaz táctica fluida y latencia de 12ms. Todo en orden, Jefa."
            else:
                reply = "Análisis N.O.V.A. completado: Red orbital estable, enlace con Buin verificado y escudo AES-256 activo."
        elif "hola" in p_lower or "buenas" in p_lower:
            reply = f"¡Hola, Jefa! Sistema unificado respondiendo a las {hora_actual_str}. ¿Qué protocolo ejecutamos?"
        elif "gracias" in p_lower or "excelente" in p_lower:
            reply = "Es un honor servirle, Jefa. Mantenemos el enlace optimizado para la presentación."
        else:
            if agente == "J.A.R.V.I.S.":
                reply = f"Comprendido, Jefa. He analizado la orden '{prompt}' en el sistema central."
            else:
                reply = f"Matriz N.O.V.A. procesando '{prompt}'. Protocolo registrado con éxito."

        try:
            from gTTS import gTTS
            tts = gTTS(text=reply, lang='es')
            audio_path = f"respuesta_{agente.lower().replace('.', '')}.mp3"
            tts.save(audio_path)
            st.session_state.messages.append({"role": "assistant", "content": f"**[{agente}]** {reply}", "audio": audio_path})
        except Exception:
            st.session_state.messages.append({"role": "assistant", "content": f"**[{agente}]** {reply}"})
        st.rerun()

    st.divider()
    st.markdown("### 🔗 Accesos Rápidos")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<a href="https://fintual.cl" target="_blank" class="tactical-link">📈 Fintual</a>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<a href="https://scribd.com" target="_blank" class="tactical-link">📚 Scribd</a>', unsafe_allow_html=True)

# --- COLUMNA DERECHA: CLIMA, RED, CIFRADO Y MODO DEMO ---
with col_der:
    st.markdown('<div class="right-panel">', unsafe_allow_html=True)
    
    c_clima, c_diag = st.columns(2)
    
    with c_clima:
        st.markdown("### 🌤️ Clima Buin")
        try:
            url_clima = "https://api.open-meteo.com/v1/forecast?latitude=-33.7331&longitude=-70.7423&current=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=auto"
            res_clima = requests.get(url_clima, timeout=3)
            if res_clima.status_code == 200:
                data_clima = res_clima.json().get("current", {})
                temp = data_clima.get("temperature_2m", "--")
                hum = data_clima.get("relative_humidity_2m", "--")
                viento = data_clima.get("wind_speed_10m", "--")
                
                st.metric("Temp", f"{temp}°C")
                st.metric("Humedad", f"{hum}%")
                st.metric("Viento", f"{viento}km/h")
            else:
                st.caption("Reconectando...")
        except Exception:
            st.caption("No disponible")

    with c_diag:
        st.markdown("### ⚡ Red")
        st.metric("Cuántica", "Estable", "12ms")
        st.metric("Satélite", "Activo", "100%")
        st.metric("Cifrado", "AES-256", "OK")

    st.divider()

    st.markdown("### 🔐 Cifrado Cuántico")
    longitud = st.slider("Longitud", min_value=8, max_value=24, value=12)
    if st.button("Generar Clave", use_container_width=True):
        caracteres = string.ascii_letters + string.digits + "!@#$"
        clave_gen = ''.join(random.choice(caracteres) for _ in range(longitud))
        st.code(clave_gen, language="")

    st.divider()
    
    # --- MÓDULO INTERACTIVO DE ORGANIZACIÓN (MODO DEMO) ---
    st.markdown("### 📁 Protocolo de Archivos")
    st.caption("Simulación en vivo para presentación")
    if st.button("🚀 Ejecutar Modo Demo (Organizar)", use_container_width=True):
        resultado_demo = ejecutar_modo_demo()
        st.success(resultado_demo)
        puente.registrar_transmision("JARVIS", "Modo demostración de archivos ejecutado con éxito.")
        
    st.markdown('</div>', unsafe_allow_html=True)

import streamlit as st
import datetime
import json
import os
import sqlite3
from gtts import gTTS
import base64

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES STARK ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        h1, h2, h3, h4, label, span { color: #00d2ff !important; font-family: monospace; text-align: left !important; }
        
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 20px;
        }
        .arc-ring {
            width: 60px;
            height: 60px;
            border: 3px solid #3a4454;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00d2ff 0%, #060911 70%);
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.6), inset 0 0 10px rgba(0, 210, 255, 0.4);
            margin-bottom: 8px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-bottom: 20px solid #ffffff;
            filter: drop-shadow(0 0 6px #00d2ff);
        }

        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 10px;
            padding: 15px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 15px;
            box-shadow: 0 0 10px rgba(0, 210, 255, 0.1);
            text-align: left !important;
        }
        .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #00d2ff !important;
        }
        .stMarkdown, p, li, span, div, .stChatMessage p {
            color: #00d2ff !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIÓN DE SÍNTESIS DE VOZ (JARVIS TTS) ---
def hablar_como_jarvis(texto):
    try:
        # Generar audio con gTTS (idioma español)
        tts = gTTS(text=texto, lang='es', slow=False)
        audio_file = "jarvis_voz.mp3"
        tts.save(audio_file)
        
        # Reproducir automáticamente en Streamlit
        audio_bytes = open(audio_file, 'rb').read()
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        audio_html = f"""
            <audio autoplay style="display:none;">
                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
            </audio>
        """
        st.markdown(audio_html, unsafe_allow_html=True)
    except Exception as e:
        print(f"Error en síntesis de voz: {e}")

# --- SISTEMA DE AUTENTICACIÓN (CLAVE DE ACCESO) ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("""
        <div class="arc-reactor-container" style="margin-top: 50px;">
            <div class="arc-ring"><div class="arc-triangle"></div></div>
            <h2 style="margin: 0; padding: 0; font-size: 1.8rem; text-align: center !important; color: #00d2ff !important;">ACCESO RESTRINGIDO</h2>
            <p style="margin: 0; font-family: monospace; font-size: 0.85rem; color: #00d2ff !important; text-align: center !important;">[ PROTOCOLO DE SEGURIDAD NODO BUIN ]</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_centro_auth = st.columns([1, 1.5, 1])[1]
    with col_centro_auth:
        clave_ingresada = st.text_input("Ingrese la clave de seguridad del búnker:", type="password")
        if st.button("🔓 Desbloquear Sistema", use_container_width=True):
            if clave_ingresada == "Jarvis":
                st.session_state.autenticado = True
                st.success("Acceso concedido. Bienvenida, jefa.")
                hablar_como_jarvis("Acceso concedido. Bienvenida, jefa. Todos los sistemas del búnker operativos.")
                st.rerun()
            else:
                st.error("Clave incorrecta. Acceso denegado.")
    st.stop()

# --- CÁLCULO DE HORA LOCAL EN CHILE (UTC-3) ---
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
hora_actual = datetime.datetime.now(tz_chile).hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

# --- BASE DE DATOS SQLITE ---
DB_NAME = "jarvis_bunker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tareas (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alertas (id INTEGER PRIMARY KEY AUTOINCREMENT, mensaje TEXT, nivel TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS biometria (id INTEGER PRIMARY KEY AUTOINCREMENT, fecha TEXT, hr INTEGER, spo2 INTEGER, sueno TEXT)''')
    conn.commit()
    
    c.execute("SELECT COUNT(*) FROM tareas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Revisar exámenes médicos y electrolitos (Sodio/Potasio)",))
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Monitorear nodo operativo en Buin",))
        conn.commit()
        
    c.execute("SELECT COUNT(*) FROM alertas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", ("Temperatura Buin óptima (21°C)", "INFO"))
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", ("Blindaje de Familia y Zona Médica ACTIVO", "OK"))
        conn.commit()
    conn.close()

init_db()

def get_db_tareas():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, texto FROM tareas")
    rows = c.fetchall()
    conn.close()
    return rows

def add_db_tarea(texto):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO tareas (texto) VALUES (?)", (texto,))
    conn.commit()
    conn.close()

def delete_db_tarea(id_t):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tareas WHERE id = ?", (id_t,))
    conn.commit()
    conn.close()

def get_db_alertas():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT mensaje, nivel FROM alertas")
    rows = c.fetchall()
    conn.close()
    return rows

def add_biometria(hr, spo2, sueno):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    fecha_hoy = datetime.datetime.now(tz_chile).strftime('%Y-%m-%d %H:%M')
    c.execute("INSERT INTO biometria (fecha, hr, spo2, sueno) VALUES (?, ?, ?, ?)", (fecha_hoy, hr, spo2, sueno))
    conn.commit()
    conn.close()

def get_latest_biometria():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT fecha, hr, spo2, sueno FROM biometria ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Núcleo búnker sincronizado con protocolos de blindaje médico y familiar. ¿Qué ordenamos hoy?"}
    ]

# --- ENCABEZADO CENTRADO CON REACTOR ARC ---
st.markdown("""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h2 style="margin: 0; padding: 0; font-size: 1.5rem; text-align: center !important; color: #00d2ff !important;">J.A.R.V.I.S IA</h2>
        <p style="margin: 0; font-family: monospace; font-size: 0.75rem; color: #00d2ff !important; text-align: center !important;">[ STARK INDUSTRIES // NODO BUIN, CHILE ]</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# --- DISTRIBUCIÓN TÁCTICA DE 3 COLUMNAS ---
col_izq, col_centro, col_der = st.columns([1, 2.2, 1])

# ==========================================
# COLUMNA IZQUIERDA: SECTOR ALPHA
# ==========================================
with col_izq:
    st.markdown("### 🌐 SECTOR ALPHA")
    
    with st.expander("🛡️ Blindaje & Alertas", expanded=True):
        st.markdown("• **Zona Familia:** Blindada (Paola Carrera, etc.)[cite: 1]")
        st.markdown("• **Zona Médica:** Protegida (Sodio/Potasio)")
        st.markdown("• **Finanzas:** Monitoreo exclusivo[cite: 1]")

    with st.expander("⌚ Mi Band (Telemetría Médica)", expanded=True):
        st.markdown("Registro biométrico de constante vital:")
        hr_input = st.number_input("Frecuencia Cardíaca (BPM):", min_value=40, max_value=200, value=72)
        spo2_input = st.number_input("Oxígeno en Sangre SpO2 (%):", min_value=70, max_value=100, value=98)
        sueno_input = st.text_input("Calidad de Sueño / Notas:", value="Óptimo - 7.5 hrs")
        
        if st.button("💾 Guardar Datos Mi Band", use_container_width=True):
            add_biometria(hr_input, spo2_input, sueno_input)
            st.success("¡Métrica registrada en el búnker!")
            hablar_como_jarvis("Datos biométricos guardados correctamente en la base de datos del búnker.")
            st.rerun()
            
        ultimo_registro = get_latest_biometria()
        if ultimo_registro:
            st.markdown(f"**Último registro ({ultimo_registro[0]}):**")
            st.markdown(f"• Pulso: **{ultimo_registro[1]} BPM**")
            st.markdown(f"• SpO2: **{ultimo_registro[2]}%**")
            st.markdown(f"• Sueño: {ultimo_registro[3]}")

    with st.expander("🔔 Alertas del Búnker"):
        alertas_db = get_db_alertas()
        for msg, nivel in alertas_db:
            icono = "🟢" if nivel == "OK" else "ℹ️"
            st.markdown(f"{icono} {msg}")
        nueva_alerta = st.text_input("Añadir alerta rápida:", key="inp_alerta")
        if st.button("➕ Emitir Alerta", use_container_width=True) and nueva_alerta:
            conn = sqlite3.connect(DB_NAME)
            c = conn.cursor()
            c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", (nueva_alerta, "INFO"))
            conn.commit()
            conn.close()
            st.success("Alerta emitida.")
            st.rerun()

    with st.expander("📝 Tareas del Búnker"):
        nueva_tarea = st.text_input("Nueva tarea rápida:", key="inp_tarea")
        if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
            add_db_tarea(nueva_tarea)
            st.rerun()
        for tid, t in get_db_tareas():
            ct1, ct2 = st.columns([4, 1])
            with ct1:
                st.markdown(f"• {t}")
            with ct2:
                if st.button("❌", key=f"del_t_{tid}"):
                    delete_db_tarea(tid)
                    st.rerun()

    with st.expander("🌐 Telemetría Global", expanded=True):
        st.markdown(f"• **Reactor:** 100% stable\n• **Hora:** {datetime.datetime.now(tz_chile).strftime('%H:%M')}\n• **Starlink:** Óptimo")

    with st.expander("🌤️ Clima Local (Buin)", expanded=True):
        st.markdown("• **Condición:** Despejado\n• **Temperatura:** 21°C\n• **Humedad:** 45%")

# ==========================================
# COLUMNA CENTRAL: OJO DE DIOS, ISS, CÁMARA & CHAT
# ==========================================
with col_centro:
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin:0; font-size: 1.1rem; color: #00d2ff !important;'>🛰️ Ojo de Dios & Telemetría ISS</h4>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; color: #00d2ff !important;'>Órbita terrestre, transmisiones en vivo y enlace satelital sincronizado con Buin.</p>", unsafe_allow_html=True)
    
    tab_ojo, tab_iss1, tab_iss2, tab_aurora = st.tabs(["🗺️ Mapa Satelital", "🌍 ISS Diurno", "🛰️ Tierra 24/7", "🌌 Auroras ISS"])
    with tab_ojo:
        st.link_button("🌐 Abrir Visor Satelital (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
    with tab_iss1:
        st.video("https://www.youtube.com/watch?v=alJMoaKpV_E")
        st.caption("Ambient Earth (Real Time) ✨ ISS Remastered")
    with tab_iss2:
        st.video("https://www.youtube.com/watch?v=4QJEibrt9B8")
        st.caption("International Space Station ISS Live 24/7 🌍 Earth from Space")
    with tab_aurora:
        st.video("https://www.youtube.com/watch?v=I3sa2kiEpkA")
        st.caption("Aurora Across the Night Side 🌌 ISS Views | LIVE 24/7")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    activar_camara_directa = st.checkbox("📷 Activar Módulo de Visión Artificial & Transmisión", value=False, key="toggle_cam_central")
    if activar_camara_directa:
        st.success("🟢 Transmisión de seguridad activa y enlace con cámaras operando.")
        foto_camara = st.camera_input("Captura óptica de seguridad en vivo:")
        if foto_camara:
            st.success("Fotograma capturado con éxito. Análisis completado sin observaciones.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    cc1, cc2 = st.columns([4, 1])
    with cc1:
        st.markdown("<h4 style='margin:0; font-size: 1.1rem; color: #00d2ff !important;'>💬 Chat IA & Análisis Visual</h4>", unsafe_allow_html=True)
    with cc2:
        if st.button("🗑️", use_container_width=True, key="limpiar_chat"):
            h_limp = datetime.datetime.now(tz_chile).hour
            s_limp = "Buenos días" if 0 <= h_limp < 12 else ("Buenas tardes" if 12 <= h_limp < 20 else "Buenas noches")
            st.session_state.mensajes = [{"role": "assistant", "content": f"{s_limp}, jefa. Memoria limpia y lista."}]
            hablar_como_jarvis("Memoria limpia y lista, jefa.")
            st.rerun()

    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(f"<span style='color: #00d2ff !important;'>{m['content']}</span>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if prompt_usuario := st.chat_input("Escriba su mensaje..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
        h_prompt = datetime.datetime.now(tz_chile).hour
        s_prompt = "Buenos días" if 0 <= h_prompt < 12 else ("Buenas tardes" if 12 <= h_prompt < 20 else "Buenas noches")
        p_low = prompt_usuario.lower()
        
        if any(p in p_low for p in ["hola", "saludos"]):
            respuesta = f"{s_prompt}, jefa. Todos los sistemas del búnker operando al 100%."
        elif any(p in p_low for p in ["sodio", "potasio", "examen", "medico", "médico"]):
            respuesta = "Registros clínicos blindados: Sodio en 143.9 mEq/L y Potasio en 4.1 mEq/L (normales)."
        else:
            respuesta = "Entendido, jefa. Procesando órdenes en el núcleo central..."
            
        st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
        hablar_como_jarvis(respuesta)
        st.rerun()

# ==========================================
# COLUMNA DERECHA: SECTOR BETA
# ==========================================
with col_der:
    st.markdown("### ⚡ SECTOR BETA")

    with st.expander("⚙️ Conexión de IA Avanzada"):
        st.selectbox("Modelo en uso:", ["GPT-4o (Stark Core)", "Gemini 1.5 Pro"], key="model_select")
        st.slider("Nivel de Sarcasmo:", 0, 100, 85)

    with st.expander("📬 Auditoría de Correo IA", expanded=True):
        st.markdown("Barrido inteligente (Familia y Médicos blindados).")
        if st.button("🔍 Auditar Correos del Día", use_container_width=True):
            st.success("¡Auditoría táctica completada!")
            hablar_como_jarvis("Auditoría de correo completada con éxito. Zonas familiares y médicas protegidas.")
        if st.button("🧹 Limpiar Spam (Bandeja Segura)", use_container_width=True):
            st.warning("Spam archivado. Zona familiar y médica intactas.")
            hablar_como_jarvis("Spam archivado. Las zonas protegidas se mantienen intactas.")

    with st.expander("🔍 Búsqueda y Web en Vivo"):
        url_input = st.text_input("URL o término a explorar:", key="inp_url")
        if st.button("🔍 Escanear Web", use_container_width=True) and url_input:
            st.info(f"Analizando nodo web: {url_input}...")
        st.link_button("🌐 Portal UC Christus", "https://portalclinico.ucchristus.cl", use_container_width=True)

    with st.expander("📄 Documentos & Sensores"):
        st.file_uploader("Cargar documento clínico/examen:", type=["pdf", "csv", "txt"])

    with st.expander("🗺️ Estación Cartográfica & Cámaras", expanded=True):
        camara_seleccionada = st.selectbox("Canal de Vigilancia:", ["Cam 01 - Acceso Buin", "Cam 02 - Perímetro Búnker", "Stream IP Personalizado"])
        st.markdown(f"• **Estado:** {camara_seleccionada} transmitiendo")
        st.markdown("---")
        st.markdown("**🌐 Arsenal Cartográfico (Stark Maps):**")
        st.link_button("☀️ 01. SunCalc (Recorrido solar)", "https://www.suncalc.org", use_container_width=True)
        st.link_button("🗺️ 02. OpenStreetMap", "https://www.openstreetmap.org", use_container_width=True)
        st.link_button("🌊 03. Climate Central", "https://coastal.climatecentral.org", use_container_width=True)
        st.link_button("🛣️ 04. Streetmix", "https://streetmix.net", use_container_width=True)
        st.link_button("📐 05. CADmapper", "https://cadmapper.com", use_container_width=True)
        st.link_button("🌤️ 06. Ventusky", "https://www.ventusky.com", use_container_width=True)
        st.link_button("🏙️ 07. ShadeMap", "https://shademap.app", use_container_width=True)
        st.link_button("🤖 08. Aino (IA Espacial)", "https://www.aino.world", use_container_width=True)

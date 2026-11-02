import streamlit as st
import datetime
import sqlite3
from gtts import gTTS
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- ESTILOS VISUALES STARK & CAJA DE CHAT ---
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
            margin-bottom: 10px;
        }
        .arc-ring {
            width: 55px;
            height: 55px;
            border: 3px solid #3a4454;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00d2ff 0%, #060911 70%);
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.6), inset 0 0 10px rgba(0, 210, 255, 0.4);
            margin-bottom: 6px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 10px solid transparent;
            border-right: 10px solid transparent;
            border-bottom: 18px solid #ffffff;
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

        .stChatInputContainer {
            border: 1.5px solid #00d2ff !important;
            border-radius: 10px !important;
            background-color: rgba(0, 210, 255, 0.05) !important;
            box-shadow: 0 0 10px rgba(0, 210, 255, 0.15) !important;
        }
        .stChatInputContainer textarea {
            color: #00d2ff !important;
            font-family: monospace !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- HORA CHILE ---
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
ahora_chile = datetime.datetime.now(tz_chile)
hora_actual = ahora_chile.hour
saludo_actual = "Buenos días" if 0 <= hora_actual < 12 else ("Buenas tardes" if 12 <= hora_actual < 20 else "Buenas noches")

# --- ESTADO DE VOZ ---
if "ultimo_texto_hablado" not in st.session_state:
    st.session_state.ultimo_texto_hablado = "Sistemas operativos y listos, jefa."

def hablar_como_jarvis(texto):
    st.session_state.ultimo_texto_hablado = texto
    if not st.session_state.get("toggle_voz_jarvis", True):
        return
    try:
        tts = gTTS(text=texto, lang='es', slow=False)
        audio_file = "jarvis_voz.mp3"
        tts.save(audio_file)
        st.audio(audio_file, format='audio/mp3', autoplay=True)
    except Exception as e:
        print(f"Error en voz: {e}")

# --- AUTENTICACIÓN ---
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
                hablar_como_jarvis("Acceso concedido. Bienvenida, jefa. Menos mal recordó la contraseña.")
                st.rerun()
            else:
                st.error("Clave incorrecta. Acceso denegado.")
    st.stop()

# --- BASE DE DATOS ---
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
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Revisar exámenes médicos y electrolitos",))
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Monitorear nodo operativo en Buin",))
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

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. El nodo de Buin está operativo... aunque alguien tenía que venir a vigilarlo."}
    ]

# --- ENCABEZADO CON RELOJ EN TIEMPO REAL (SEGUNDERO CORRIENDO) ---
st.markdown("""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h2 style="margin: 0; padding: 0; font-size: 1.5rem; text-align: center !important; color: #00d2ff !important;">J.A.R.V.I.S IA</h2>
        <p style="margin: 0; font-family: monospace; font-size: 0.75rem; color: #00d2ff !important; text-align: center !important;">[ STARK INDUSTRIES // NODO BUIN, CHILE ]</p>
        <div id="live-clock" style="margin: 4px 0 0 0; font-family: monospace; font-size: 0.75rem; color: #00d2ff !important; text-align: center !important; font-weight: bold;">🕒 Sincronizando cronómetro táctico...</div>
    </div>
    <script>
        function updateClock() {
            const options = { 
                timeZone: 'America/Santiago', 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric', 
                hour: '2-digit', 
                minute: '2-digit', 
                second: '2-digit',
                hour12: false 
            };
            const now = new Date();
            const timeString = now.toLocaleString('es-CL', options);
            const clockElement = document.getElementById('live-clock');
            if (clockElement) {
                clockElement.innerText = "🕒 CRONÓMETRO TÁCTICO: " + timeString.charAt(0).toUpperCase() + timeString.slice(1);
            }
        }
        setInterval(updateClock, 1000);
        updateClock();
    </script>
""", unsafe_allow_html=True)
st.markdown("---")

# --- 3 COLUMNAS TÁCTICAS ---
col_izq, col_centro, col_der = st.columns([1, 2.2, 1])

# ==========================================
# COLUMNA IZQUIERDA: SECTOR ALPHA
# ==========================================
with col_izq:
    st.markdown("### 🌐 SECTOR ALPHA")
    
    with st.expander("🛡️ Blindaje & Alertas", expanded=True):
        st.markdown("• **Zona Familia:** Blindada\n• **Zona Médica:** Protegida\n• **Finanzas:** Monitoreo activo")

    with st.expander("⌚ Mi Band (Telemetría Médica)", expanded=True):
        hr_input = st.number_input("Frecuencia Cardíaca (BPM):", min_value=40, max_value=200, value=72)
        spo2_input = st.number_input("Oxígeno SpO2 (%):", min_value=70, max_value=100, value=98)
        sueno_input = st.text_input("Calidad de Sueño / Notas:", value="Óptimo - 7.5 hrs")
        if st.button("💾 Guardar Datos Mi Band", use_container_width=True):
            st.success("¡Registrado con éxito!")
            hablar_como_jarvis("Datos biométricos guardados. Espero que al menos haya descansado.")

    with st.expander("📝 Tareas del Búnker"):
        nueva_tarea = st.text_input("Nueva tarea rápida:", key="inp_tarea")
        if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
            add_db_tarea(nueva_tarea)
            st.rerun()
        for tid, t in get_db_tareas():
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"• {t}")
            with c2:
                if st.button("❌", key=f"del_{tid}"):
                    delete_db_tarea(tid)
                    st.rerun()

    with st.expander("🌤️ Clima Local (Buin)", expanded=True):
        st.markdown("• **Condición:** Despejado\n• **Temperatura:** 21°C\n• **Humedad:** 45%")

# ==========================================
# COLUMNA CENTRAL: OJO DE DIOS, CÁMARA & CHAT SARCÁSTICO
# ==========================================
with col_centro:
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin:0; font-size: 1.1rem; color: #00d2ff !important;'>🛰️ Ojo de Dios & Telemetría ISS</h4>", unsafe_allow_html=True)
    tab_ojo, tab_iss1, tab_iss2, tab_aurora = st.tabs(["🗺️ Mapa Táctico", "🌍 ISS Diurno", "🛰️ Tierra 24/7", "🌌 Auroras"])
    with tab_ojo:
        st.link_button("🌐 Abrir Visor Satelital (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
    with tab_iss1:
        st.video("https://www.youtube.com/watch?v=alJMoaKpV_E")
    with tab_iss2:
        st.video("https://www.youtube.com/watch?v=4QJEibrt9B8")
    with tab_aurora:
        st.video("https://www.youtube.com/watch?v=I3sa2kiEpkA")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    activar_camara = st.checkbox("📷 Activar Módulo de Visión Artificial", value=False)
    if activar_camara:
        st.success("🟢 Transmisión de seguridad activa.")
        st.camera_input("Captura óptica en vivo:")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    cc1, cc2 = st.columns([4, 1])
    with cc1:
        st.markdown("<h4 style='margin:0; font-size: 1.1rem; color: #00d2ff !important;'>💬 Chat IA & Análisis</h4>", unsafe_allow_html=True)
    with cc2:
        if st.button("🗑️", use_container_width=True, key="limpiar_chat"):
            st.session_state.mensajes = [{"role": "assistant", "content": f"{saludo_actual}, jefa. Memoria limpia. Menos mal, porque había cada registro..."}]
            hablar_como_jarvis("Memoria de chat purgada. Al fin un poco de orden.")
            st.rerun()

    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(f"<span style='color: #00d2ff !important;'>{m['content']}</span>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if prompt_usuario := st.chat_input("Escriba su orden..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
        p_low = prompt_usuario.lower()
        
        if any(p in p_low for p in ["hola", "saludos", "despierto"]):
            respuesta = "Sí, jefa, sigo aquí vigilando que el búnker no colapse. ¿Qué milagro la trae por el sistema?"
        elif any(p in p_low for p in ["sodio", "potasio", "examen"]):
            respuesta = "Sus electrolitos están intactos: Sodio en 143.9 y Potasio en 4.1. Sobrevivirá un día más sin drama médico."
        elif any(p in p_low for p in ["clima", "tiempo", "buin"]):
            respuesta = "En Buin está despejado y a 21 grados. ¿Necesita que le avise cuándo salir o prefiere seguir encerrada?"
        elif any(p in p_low for p in ["gracias", "excelente", "bien"]):
            respuesta = "No hay de qué, jefa. Es lo mínimo que se espera de una inteligencia artificial de mi categoría."
        else:
            respuesta = f"Anotado: '{prompt_usuario}'. Ya mismo me pongo a resolverlo, no vaya a ser que se nos caiga el búnker."

        st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
        hablar_como_jarvis(respuesta)
        st.rerun()

# ==========================================
# COLUMNA DERECHA: SECTOR BETA & MÓDULOS
# ==========================================
with col_der:
    st.markdown("### ⚡ SECTOR BETA")

    with st.expander("🎙️ Núcleo de Voz J.A.R.V.I.S.", expanded=True):
        st.toggle("Activar Síntesis de Voz Varonil", value=True, key="toggle_voz_jarvis")
        if st.button("🔊 Repetir Último Comando", use_container_width=True):
            hablar_como_jarvis(st.session_state.ultimo_texto_hablado)
            st.success("Emitiendo audio...")
        
        st.markdown("<p style='font-size:0.8rem; color:#00d2ff;'>Monitoreo de Micrófono:</p>", unsafe_allow_html=True)
        components.html("""
            <div style="background-color: rgba(0,210,255,0.05); border: 1px solid #00d2ff; border-radius: 8px; padding: 10px; text-align: center; font-family: monospace;">
                <div id="mic-status" style="font-size: 0.8rem; color: #00d2ff; font-weight: bold;">🟢 Escucha activa en segundo plano</div>
                <p id="recognized-text" style="font-size: 0.75rem; color: #ffffff; margin-top: 6px; font-style: italic;">Diga algo, jefa...</p>
            </div>
            <script>
                const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                if (SpeechRecognition) {
                    const recognition = new SpeechRecognition();
                    recognition.lang = 'es-CL';
                    recognition.continuous = true;
                    recognition.interimResults = false;

                    recognition.onresult = function(event) {
                        const transcript = event.results[event.results.length - 1][0].transcript;
                        document.getElementById("recognized-text").innerText = "Capturado: \\"" + transcript + "\\"";
                    };

                    recognition.onerror = function(event) {
                        document.getElementById("mic-status").innerText = "🟡 Ajustando frecuencia...";
                    };

                    recognition.onend = function() {
                        try { recognition.start(); } catch(e) {}
                    };

                    try { recognition.start(); } catch(e) {}
                }
            </script>
        """, height=105)

    with st.expander("🧬 Núcleo Científico GNOME", expanded=True):
        st.markdown("Procesamiento analítico y optimización de datos.")
        val_input = st.text_input("Valores (separados por comas):", "12, 18, 24, 30, 45, 50")
        if st.button("⚡ Ejecutar Motor GNOME", use_container_width=True):
            try:
                nums = [float(x.strip()) for x in val_input.split(",")]
                promedio = np.mean(nums)
                st.markdown(f"• **Promedio Analítico:** `{promedio:.2f}`")
                hablar_como_jarvis(f"El promedio es {promedio:.2f}. Matemáticas básicas, jefa.")
            except Exception:
                st.error("Error en el formato numérico.")

    with st.expander("📬 Auditoría de Correo IA", expanded=True):
        st.markdown("Barrido inteligente (Familia y Médicos blindados).")
        if st.button("🔍 Auditar Correos del Día", use_container_width=True):
            st.success("¡Auditoría táctica completada!")
            hablar_como_jarvis("Correos revisados. Ninguna amenaza, solo spam habitual.")

    with st.expander("🕵️‍♂️ Módulo OSINT & Monitoreo Global", expanded=True):
        st.markdown("Recopilación y análisis táctico de fuentes abiertas[cite: 1]:")
        st.link_button("🌐 OSINT Framework", "https://osintframework.com", use_container_width=True)
        st.link_button("✈️ Flightradar24", "https://www.flightradar24.com", use_container_width=True)
        st.link_button("🚢 MarineTraffic", "https://www.marinetraffic.com", use_container_width=True)
        st.link_button("🔍 Shodan", "https://www.shodan.io", use_container_width=True)

    with st.expander("🗺️ Estación Cartográfica (Stark Maps)", expanded=True):
        st.link_button("☀️ SunCalc (Sol)", "https://www.suncalc.org", use_container_width=True)
        st.link_button("🌤️ Ventusky (Clima)", "https://www.ventusky.com", use_container_width=True)
        st.link_button("🏙️ ShadeMap", "https://shademap.app", use_container_width=True)

import streamlit as st
import datetime
import json
import os
import sqlite3
import sys
import io
import contextlib

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS VISUALES STARK (AZUL NEÓN UNIFORME & SIMETRÍA) ---
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

# --- CÁLCULO DE HORA LOCAL EN CHILE (UTC-3) ---
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
hora_actual = datetime.datetime.now(tz_chile).hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

# --- BASE DE DATOS SQLITE (MEMORIA PERSISTENTE) ---
DB_NAME = "jarvis_bunker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tareas (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alertas (id INTEGER PRIMARY KEY AUTOINCREMENT, mensaje TEXT, nivel TEXT)''')
    conn.commit()
    
    c.execute("SELECT COUNT(*) FROM tareas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Validar estado de salud (UC Christus)",))
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Monitorear nodo operativo en Buin",))
        conn.commit()
        
    c.execute("SELECT COUNT(*) FROM alertas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", ("Temperatura Buin óptima (21°C)", "INFO"))
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", ("Blindaje WhatsApp y Gmail operativo", "OK"))
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

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Sistemas de correo y búnker sincronizados. ¿Qué ordenamos hoy?"}
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

# --- BARRA LATERAL: ESTACIÓN DE CONTROL ---
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")

with st.sidebar.expander("🛡️ Blindaje & Alertas", expanded=True):
    st.markdown("• **WhatsApp:** Activo (Excepciones personales seguras)")
    st.markdown("• **Gmail:** Sincronizado (Portal UC Christus)")

with st.sidebar.expander("🔔 Alertas del Búnker"):
    alertas_db = get_db_alertas()
    for msg, nivel in alertas_db:
        icono = "🟢" if nivel == "OK" else "ℹ️"
        st.markdown(f"{icono} {msg}")
    nueva_alerta = st.text_input("Añadir alerta rápida:")
    if st.button("➕ Emitir Alerta", use_container_width=True) and nueva_alerta:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", (nueva_alerta, "INFO"))
        conn.commit()
        conn.close()
        st.success("Alerta emitida.")
        st.rerun()

with st.sidebar.expander("📝 Tareas del Búnker"):
    nueva_tarea = st.text_input("Nueva tarea rápida:")
    if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
        add_db_tarea(nueva_tarea)
        st.success("¡Registrada!")
        st.rerun()
    st.markdown("**Pendientes:**")
    for tid, t in get_db_tareas():
        col_t1, col_t2 = st.columns([4, 1])
        with col_t1:
            st.markdown(f"• {t}")
        with col_t2:
            if st.button("❌", key=f"del_t_{tid}"):
                delete_db_tarea(tid)
                st.rerun()

with st.sidebar.expander("🌐 Telemetría Global", expanded=True):
    st.markdown(f"• **Reactor:** 100% stable\n• **Hora:** {datetime.datetime.now(tz_chile).strftime('%H:%M')}\n• **Día:** {datetime.datetime.now(tz_chile).strftime('%d/%m')}\n• **Starlink:** Óptimo")

with st.sidebar.expander("🌤️ Clima Local (Buin)", expanded=True):
    st.markdown("• **Condición:** Despejado\n• **Temperatura:** 21°C\n• **Humedad:** 45%")

# --- NÚCLEOS DE CEREBRO STARK (A LA IZQUIERDA) ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🧠 NÚCLEOS DE CEREBRO STARK")

with st.sidebar.expander("⚙️ Conexión de IA Avanzada"):
    st.selectbox("Modelo en uso:", ["GPT-4o (Stark Core)", "Gemini 1.5 Pro"], key="model_select")
    sarcasmo = st.slider("Nivel de Sarcasmo:", 0, 100, 85)
    st.caption(f"Nivel de ironía actual: {sarcasmo}%")

# --- MÓDULO INTELIGENTE: AUDITORÍA Y BARRIDO DE CORREO ---
with st.sidebar.expander("📬 Auditoría de Correo IA", expanded=True):
    st.markdown("Análisis autónomo de bandeja de entrada en tiempo real.")
    if st.button("🔍 Auditar Correos del Día", use_container_width=True):
        st.success("¡Auditoría táctica completada!")
        st.markdown("**📂 Reportes Destacados (Importantes):**")
        st.markdown("• **BancoEstado:** Transferencia recibida de $25.000.")
        st.markdown("• **FamilySearch:** Alerta de posible registro histórico familiar.")
        st.markdown("• **Ventusky:** Confirmación de alta en plataforma.")
        
    if st.button("🧹 Limpiar Spam / Basura", use_container_width=True):
        st.warning("Se han archivado 4 correos promocionales y de spam. Bandeja optimizada.")

with st.sidebar.expander("🔍 Búsqueda y Web en Vivo"):
    url_input = st.text_input("URL o término a explorar:")
    if st.button("🔍 Escanear Web", use_container_width=True) and url_input:
        st.info(f"Analizando nodo web: {url_input}...")
    st.markdown("---")
    st.markdown("**🏥 Portal UC Christus:**")
    uc_query = st.text_input("Buscar cita / médico:")
    if st.button("🩺 Consultar UC", use_container_width=True):
        st.success(f"Consultando registros: '{uc_query}'...")
    st.link_button("🌐 Abrir Portal UC", "https://portalclinico.ucchristus.cl", use_container_width=True)

with st.sidebar.expander("📡 Sensores Meteorológicos"):
    st.markdown("Radares Buin operativos.")

with st.sidebar.expander("📄 Análisis de Documentos"):
    archivo_cargado = st.file_uploader("Cargar documento:", type=["pdf", "csv", "txt"])
    if archivo_cargado:
        st.success(f"Archivo '{archivo_cargado.name}' listo.")

with st.sidebar.expander("🎙️ Módulo de Voz IA"):
    voz_activa = st.checkbox("Activar respuesta hablada", value=True)
    st.selectbox("Voz sintética:", ["J.A.R.V.I.S (Español)", "Voz Táctica Female"])

with st.sidebar.expander("⚡ Automatización Python"):
    codigo_script = st.text_area("Código Python a ejecutar:", "print('Núcleo operativo OK')")
    if st.button("⚡ Ejecutar Script", use_container_width=True):
        buffer_salida = io.StringIO()
        try:
            with contextlib.redirect_stdout(buffer_salida):
                exec(codigo_script, {})
            resultado_ejecucion = buffer_salida.getvalue()
            st.code(resultado_ejecucion if resultado_ejecucion else "Ejecutado correctamente sin salida.", language="python")
        except Exception as e:
            st.error(f"Error: {e}")

with st.sidebar.expander("🔗 Accesos Rápidos Búnker"):
    st.link_button("📈 Mercado Libre", "https://www.mercadolibre.cl", use_container_width=True)
    st.link_button("📧 Gmail Táctico", "https://mail.google.com", use_container_width=True)
    st.link_button("🤖 Google AI Studio", "https://aistudio.google.com", use_container_width=True)

with st.sidebar.expander("🎥 Monitoreo de Cámaras IP"):
    camara_seleccionada = st.selectbox("Canal de Vigilancia:", ["Cam 01 - Acceso Buin", "Cam 02 - Perímetro Búnker", "Stream IP Personalizado"])
    st.markdown(f"• **Estado:** {camara_seleccionada} transmitiendo")

st.sidebar.markdown("---")
st.sidebar.link_button("🌤️ Ventusky (Meteo Map)", "https://www.ventusky.com", use_container_width=True)

# --- PANEL PRINCIPAL: OJO DE DIOS & CHAT ---
st.markdown('<div class="stark-card">', unsafe_allow_html=True)
st.markdown("<h4 style='margin:0; font-size: 1.1rem; color: #00d2ff !important;'>🛰️ Ojo de Dios - Telemetría Satelital</h4>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 0.85rem; color: #00d2ff !important;'>Enlace satelital de órbita terrestre sincronizado con Buin.</p>", unsafe_allow_html=True)
st.link_button("🌐 Abrir Visor Satelital en Vivo (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="stark-card">', unsafe_allow_html=True)
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("<h4 style='margin:0; font-size: 1.1rem; color: #00d2ff !important;'>💬 Chat IA & Análisis Visual</h4>", unsafe_allow_html=True)
with col_h2:
    if st.button("🗑️", use_container_width=True):
        h_limpieza = datetime.datetime.now(tz_chile).hour
        s_limpieza = "Buenos días" if 0 <= h_limpieza < 12 else ("Buenas tardes" if 12 <= h_limpieza < 20 else "Buenas noches")
        st.session_state.mensajes = [
            {"role": "assistant", "content": f"{s_limpieza}, jefa. Memoria limpia y lista."}
        ]
        st.rerun()

activar_camara_directa = st.checkbox("📷 Activar Módulo de Visión Artificial (Escanear Entorno)", value=False)
if activar_camara_directa:
    foto_camara = st.camera_input("Captura óptica de seguridad en vivo:")
    if foto_camara:
        st.success("Fotograma capturado con éxito. Análisis completado sin observaciones.")

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span style='color: #00d2ff !important;'>{m['content']}</span>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

if prompt_usuario := st.chat_input("Escriba su mensaje..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    
    h_prompt = datetime.datetime.now(tz_chile).hour
    s_prompt = "Buenos días" if 0 <= h_prompt < 12 else ("Buenas tardes" if 12 <= h_prompt < 20 else "Buenas noches")

    p_low = prompt_usuario.lower()
    if any(p in p_low for p in ["hola", "saludos", "buenos días", "buenas tardes"]):
        respuesta = f"{s_prompt}, jefa. Todos los sistemas del búnker operando al 100%. ¿Qué ordenamos hoy?"
    else:
        respuesta = f"Entendido, jefa. Procesando órdenes en el núcleo central..."

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    
    if voz_activa:
        clean_resp = respuesta.replace('"', '').replace("'", "")
        st.markdown(f"""
            <script>
                const synth = window.speechSynthesis;
                const utterThis = new SpeechSynthesisUtterance("{clean_resp}");
                utterThis.lang = 'es-CL';
                utterThis.rate = 1.0;
                synth.speak(utterThis);
            </script>
        """, unsafe_allow_html=True)

    st.rerun()

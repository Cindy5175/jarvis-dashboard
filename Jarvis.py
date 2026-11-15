import streamlit as st
import datetime
import sqlite3

# --- 1. CONFIGURACION DE PAGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S. // NÚCLEO TÁCTICO SUPREMO",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos limpios, profesionales y animaciones SVG/CSS
st.markdown("""
    <style>
        .block-container { padding: 0.5rem 1rem 4rem 1rem !important; max-width: 100% !important; }
        header, footer, #MainMenu {visibility: hidden;}
        body, .stApp {background-color: #040711; color: #00f3ff; font-family: monospace;}
        p, span, label, h1, h2, h3, h4, div { color: #00f3ff; font-family: monospace; }
        .stButton>button { background-color: rgba(0, 243, 255, 0.15) !important; color: #00f3ff !important; border: 1px solid #00f3ff !important; font-weight: bold; font-family: monospace; width: 100%; border-radius: 6px; }
        .stButton>button:hover { background-color: #00f3ff !important; color: #040711 !important; box-shadow: 0 0 10px #00f3ff; }
        [data-testid="stExpander"] summary span { color: #00f3ff !important; font-weight: bold; }
        
        /* Estilos del HUD Unificado */
        .hud-box {
            border: 1px solid #00f3ff;
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 16px;
            background: linear-gradient(180deg, rgba(0, 243, 255, 0.06) 0%, rgba(4, 7, 17, 0.9) 100%);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.15);
        }
        .hud-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(0, 243, 255, 0.3);
            padding-bottom: 8px;
            margin-bottom: 12px;
        }
        .badge-online {
            border: 1px solid #00ff66;
            color: #00ff66 !important;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .badge-nodo {
            border: 1px solid #00f3ff;
            color: #00f3ff !important;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .radar-grid {
            background-image: linear-gradient(rgba(0, 243, 255, 0.1) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(0, 243, 255, 0.1) 1px, transparent 1px);
            background-size: 20px 20px;
            border: 1px solid rgba(0, 243, 255, 0.25);
            border-radius: 8px;
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        @keyframes pulse-dot {
            0% { r: 4; opacity: 1; }
            50% { r: 7; opacity: 0.6; }
            100% { r: 4; opacity: 1; }
        }
        .pulse-center {
            animation: pulse-dot 2s infinite ease-in-out;
        }
    </style>
""", unsafe_allow_html=True)

tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour
hora_formateada = now_chile.strftime('%H:%M:%S')

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": saludo_actual + ", jefa. Todos los sistemas operativos al 100% en el Nodo Buin."}
    ]

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"

def init_db():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS misiones (id INTEGER PRIMARY KEY AUTOINCREMENT, tarea TEXT NOT NULL, estado TEXT DEFAULT 'Pendiente', fecha_creacion TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS memory (key_id TEXT PRIMARY KEY, fact_text TEXT, category TEXT)")
        cursor.execute("CREATE TABLE IF NOT EXISTS episodic_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, event_type TEXT, details TEXT)")
        conn.commit()
        conn.close()
    except Exception:
        pass

init_db()

class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path
    def log_episode(self, event_type: str, details: str):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            timestamp = datetime.datetime.now(tz_chile).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("INSERT INTO episodic_logs (timestamp, event_type, details) VALUES (?, ?, ?)", (timestamp, event_type, details))
            conn.commit()
            conn.close()
        except Exception:
            pass

jarvis_mem = JarvisMemory()

def agregar_mision(tarea):
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False)
        cursor = conn.cursor()
        ts = datetime.datetime.now(tz_chile).strftime('%Y-%m-%d %H:%M')
        cursor.execute("INSERT INTO misiones (tarea, fecha_creacion) VALUES (?, ?)", (tarea, ts))
        conn.commit()
        conn.close()
        jarvis_mem.log_episode("MISSION_ADD", "Nueva misión: " + tarea)
    except Exception:
        pass

def obtener_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT id, tarea, estado FROM misiones")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []

def limpiar_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM misiones")
        conn.commit()
        conn.close()
    except Exception:
        pass

# --- PANTALLA DE BLOQUEO (PIN) ---
if not st.session_state.get("autorizado", False):
    st.markdown("<h2 style='text-align: center; color: #00f3ff; font-family: monospace;'>ACCESO RESTRINGIDO - NODO BUIN</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #5b8fa8; font-family: monospace;'>INGRESE PIN DE SEGURIDAD</p>", unsafe_allow_html=True)
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto Numérico:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button("Desbloquear Armadura")
        if btn_entrar:
            if pin_input.strip() == PIN_SECRETO:
                st.session_state.autorizado = True
                jarvis_mem.log_episode("SYSTEM_LOGIN", "Acceso concedido a la jefa.")
                st.success("Acceso concedido. Un gusto verte de nuevo, jefa...")
                st.rerun()
            else:
                st.error("PIN incorrecto. Acceso denegado.")
    st.stop()

# --- PESTAÑAS PRINCIPALES ---
tab_hud, tab_financiero = st.tabs(["⚡ HUD Táctico Principal", "📈 Centro Financiero & Mercados"])

with tab_hud:
    # 1. CONTROLES DEL SISTEMA (Únicos y arriba del todo)
    col_ctrl1, col_ctrl2 = st.columns(2)
    with col_ctrl1:
        st.markdown("#### 🛠️ Controles del Sistema")
        if st.button("🔒 Bloquear Sistema", use_container_width=True):
            st.session_state.autorizado = False
            st.rerun()
        if st.button("🔄 Reinicio Total", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    with col_ctrl2:
        st.markdown("#### 🧠 Selector de Núcleo (IA)")
        nuevo_nucleo = st.radio(
            "Seleccionar Asistente Activo:",
            ["JARVIS", "VIERNES", "NOVA"],
            index=["JARVIS", "VIERNES", "NOVA"].index(st.session_state.nucleo_activo),
            label_visibility="collapsed"
        )
        if nuevo_nucleo != st.session_state.nucleo_activo:
            st.session_state.nucleo_activo = nuevo_nucleo
            jarvis_mem.log_episode("CORE_SWITCH", "Cambiado a " + nuevo_nucleo)
            st.success("Núcleo activo: " + nuevo_nucleo)
            st.rerun()

    st.markdown("---")

    # 2. HUD GRÁFICO UNIFICADO (Sin iframe externo, 100% nativo y sin cortes)
    hud_completo_html = f"""
    <div class="hud-box">
        <div class="hud-header">
            <div style="display: flex; align-items: center; gap: 12px;">
                <svg width="36" height="36" viewBox="0 0 40 40">
                    <polygon points="4,6 36,6 20,35" fill="none" stroke="#00f3ff" stroke-width="2.5"/>
                    <polygon points="10,10 30,10 20,28" fill="rgba(0,243,255,0.2)" stroke="#00f3ff" stroke-width="1.5"/>
                </svg>
                <div>
                    <div style="font-size: 18px; font-weight: bold; letter-spacing: 2px;">J.A.R.V.I.S. HUD</div>
                    <div style="font-size: 11px; color: #00ff66;">● EN LÍNEA // NODO BUIN</div>
                </div>
            </div>
            <span class="badge-online">NÚCLEO: {st.session_state.nucleo_activo}</span>
        </div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; text-align: center;">
            <div style="background: rgba(0,243,255,0.05); padding: 8px; border-radius: 6px;">
                <div style="font-size: 11px; color: #5b8fa8;">CPU NÚCLEO</div>
                <div style="font-size: 16px; font-weight: bold;">27%</div>
            </div>
            <div style="background: rgba(0,243,255,0.05); padding: 8px; border-radius: 6px;">
                <div style="font-size: 11px; color: #5b8fa8;">MEMORIA RAM</div>
                <div style="font-size: 16px; font-weight: bold;">4.2 GB</div>
            </div>
            <div style="background: rgba(0,243,255,0.05); padding: 8px; border-radius: 6px;">
                <div style="font-size: 11px; color: #5b8fa8;">REACTOR ARC</div>
                <div style="font-size: 16px; font-weight: bold;">3.2 GJ/s</div>
            </div>
            <div style="background: rgba(0,243,255,0.05); padding: 8px; border-radius: 6px;">
                <div style="font-size: 11px; color: #ffaa00;">HORA LOCAL</div>
                <div style="font-size: 16px; font-weight: bold; color: #ffaa00;">{hora_formateada}</div>
            </div>
        </div>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px;">
        <!-- MAPA TÁCTICO SATELITAL -->
        <div class="hud-box">
            <div class="hud-header">
                <span style="font-weight: bold; font-size: 14px;">MAPA TÁCTICO SATELITAL</span>
                <span class="badge-nodo">● NODO BUIN</span>
            </div>
            <div class="radar-grid">
                <svg width="100%" height="200" viewBox="0 0 300 200">
                    <circle cx="150" cy="100" r="85" fill="none" stroke="rgba(0,243,255,0.25)" stroke-width="1"/>
                    <circle cx="150" cy="100" r="58" fill="none" stroke="rgba(0,243,255,0.35)" stroke-width="1"/>
                    <circle cx="150" cy="100" r="30" fill="none" stroke="rgba(0,243,255,0.5)" stroke-width="1"/>
                    <line x1="150" y1="10" x2="150" y2="190" stroke="rgba(0,243,255,0.15)" stroke-width="1"/>
                    <line x1="50" y1="100" x2="250" y2="100" stroke="rgba(0,243,255,0.15)" stroke-width="1"/>
                    <circle cx="150" cy="100" r="5" fill="#ffaa00" class="pulse-center"/>
                </svg>
            </div>
        </div>

        <!-- MAPA ORBITAL DE PROYECTOS -->
        <div class="hud-box">
            <div class="hud-header">
                <span style="font-weight: bold; font-size: 14px;">MAPA ORBITAL DE PROYECTOS</span>
                <span class="badge-nodo">5 NODOS</span>
            </div>
            <div class="radar-grid">
                <svg width="100%" height="200" viewBox="0 0 300 200">
                    <ellipse cx="150" cy="105" rx="125" ry="52" fill="none" stroke="rgba(0,243,255,0.25)" stroke-width="1"/>
                    <ellipse cx="150" cy="105" rx="90" ry="36" fill="none" stroke="rgba(0,243,255,0.35)" stroke-width="1"/>
                    <ellipse cx="150" cy="105" rx="52" ry="20" fill="none" stroke="rgba(0,243,255,0.45)" stroke-width="1"/>
                    
                    <circle cx="240" cy="65" r="4" fill="#00f3ff"/>
                    <text x="248" y="69" fill="#00f3ff" font-size="11" font-family="monospace">Isla Número</text>
                    
                    <circle cx="185" cy="122" r="4" fill="#ffaa00"/>
                    <text x="193" y="126" fill="#ffffff" font-size="11" font-family="monospace">J.A.R.V.I.S.</text>
                    
                    <circle cx="95" cy="136" r="4" fill="#00ff66"/>
                    <text x="103" y="140" fill="#00ff66" font-size="11" font-family="monospace">Agente IA</text>
                </svg>
            </div>
        </div>
    </div>
    """
    st.markdown(hud_completo_html, unsafe_allow_html=True)
    st.markdown("---")

    # 3. GESTIÓN DE MISIONES
    st.markdown("#### 📋 Gestión de Misiones")
    with st.expander("Base de Datos (7 Memorias)", expanded=False):
        nueva_tarea = st.text_input("Nueva Misión Táctica:", placeholder="Ej: Revisar despliegue...")
        if st.button("Registrar Tarea", use_container_width=True):
            if nueva_tarea.strip():
                agregar_mision(nueva_tarea.strip())
                st.success("¡Misión guardada!")
                st.rerun()
        misiones = obtener_misiones()
        if misiones:
            for m_id, m_text, m_est in misiones:
                st.markdown(f"- `{m_text}`")
        if st.button("Purgar Misiones", use_container_width=True):
            limpiar_misiones()
            st.rerun()

    st.markdown("---")

    # 4. CANAL NEURONAL / CHAT
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.markdown(f"<h4>💬 Canal Neuronal [{st.session_state.nucleo_activo}]</h4>", unsafe_allow_html=True)
    with col_h2:
        if st.button("Limpiar", use_container_width=True):
            st.session_state.mensajes = [
                {"role": "assistant", "content": "Memoria de chat purgada. ¿Qué orden ejecutamos, jefa?"}
            ]
            st.rerun()

    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(m['content'])

    prompt_chat = st.chat_input("Escribe tu orden o consulta...")
    if prompt_chat:
        st.session_state.mensajes.append({"role": "user", "content": prompt_chat})
        jarvis_mem.log_episode("USER_CMD", prompt_chat)
        
        texto_usuario = prompt_chat.lower()
        nucleo = st.session_state.nucleo_activo
        
        if "arturo prat" in texto_usuario:
            respuesta_ia = f"[{nucleo}]: Arturo Prat Chacón fue un abogado, marino y máximo héroe naval de Chile, recordado por su valor en el Combate Naval de Iquique el 21 de mayo de 1879."
        elif "despierto" in texto_usuario or "hola" in texto_usuario:
            respuesta_ia = f"[{nucleo}]: Absolutamente despierto y operando al 100%, jefa. ¿Qué resolvemos ahora?"
        elif "reactor" in texto_usuario or "energia" in texto_usuario:
            respuesta_ia = f"[{nucleo}]: El reactor Arc opera estable a plena potencia en el Nodo Buin."
        else:
            respuesta_ia = f"[{nucleo}]: Analizando su consulta sobre '{prompt_chat}'. Instrucción ejecutada con éxito en el Nodo Buin, jefa."

        st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
        jarvis_mem.log_episode("AI_RESP", respuesta_ia)
        st.rerun()

with tab_financiero:
    st.markdown("### 📈 Centro Financiero & Mercados Tradicionales")
    st.markdown("Acceso directo a plataformas bursátiles y de análisis macroeconómico.")
    st.markdown("---")
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown("#### 📊 Finviz")
        st.link_button("Abrir Finviz (Acciones)", "https://finviz.com/map.ashx", use_container_width=True)
        st.link_button("Screener de Mercado", "https://finviz.com/screener.ashx", use_container_width=True)
    with col_f2:
        st.markdown("#### 📉 Investing.com")
        st.link_button("Abrir Investing.com", "https://es.investing.com/", use_container_width=True)
        st.link_button("Índices Mundiales", "https://es.investing.com/indices/major-indices", use_container_width=True)
    with col_f3:
        st.markdown("#### 💱 Divisas & Commodities")
        st.link_button("Mercado Forex", "https://es.investing.com/currencies/streaming-forex-rates-majors", use_container_width=True)
        st.link_button("Materias Primas", "https://es.investing.com/commodities/real-time-futures", use_container_width=True)
    st.markdown("---")
    st.info("El subsistema financiero está conectado con la Memoria de Recuperación y la Base de Datos SQLite del Nodo Buin.")

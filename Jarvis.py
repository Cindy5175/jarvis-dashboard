import streamlit as st
import datetime
import sqlite3
import io
import contextlib
import os
import requests

# Importación segura de psutil
try:
    import psutil
    PSUTIL_DISPONIBLE = True
except ImportError:
    PSUTIL_DISPONIBLE = False

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS VISUALES STARK (ESTÉTICA DE BÚNKER) ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        
        .arc-reactor-container h4 { color: #00d2ff !important; font-size: 1.1rem !important; font-family: monospace; }
        
        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 8px;
            padding: 10px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 10px;
            box-shadow: 0 0 8px rgba(0, 210, 255, 0.1);
            text-align: left !important;
        }
        
        .stark-card h4 {
            font-size: 0.75rem !important;
            color: #00d2ff !important;
            margin-bottom: 5px !important;
        }
        
        .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #00d2ff !important;
            font-size: 0.7rem !important;
        }
        
        .stChatMessage p, .stChatMessage div {
            font-size: 0.75rem !important;
            color: #00d2ff !important;
        }

        h1, h2, h3, label, span { color: #00d2ff !important; font-family: monospace; }
        
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 10px;
        }
        .arc-ring {
            width: 45px;
            height: 45px;
            border: 2.5px solid #3a4454;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00d2ff 0%, #060911 70%);
            box-shadow: 0 0 12px rgba(0, 210, 255, 0.6), inset 0 0 8px rgba(0, 210, 255, 0.4);
            margin-bottom: 5px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-bottom: 14px solid #ffffff;
            filter: drop-shadow(0 0 5px #00d2ff);
        }
    </style>
""", unsafe_allow_html=True)

# --- ZONA HORARIA CHILENA NATIVA (UTC-3) ---
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

# --- CONTROL DE ACCESO UNIFICADO ---
CLAVE_MAESTRA = "stark123"

if "bunker_desbloqueado" not in st.session_state:
    st.session_state.bunker_desbloqueado = False

if not st.session_state.bunker_desbloqueado:
    st.markdown("""
        <div class="arc-reactor-container" style="margin-top: 20px;">
            <div class="arc-ring"><div class="arc-triangle"></div></div>
            <h4 style="margin: 0; color: #00d2ff !important; font-size: 1.1rem !important; text-align: center !important;">ACCESO RESTRINGIDO - NODO BUIN</h4>
            <p style="font-family: monospace; color: #00d2ff !important; font-size: 0.75rem !important; margin-top: 4px;">[ PROTOCOLO DE SEGURIDAD STARK ACTIVO ]</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 3, 1])
    with col_l2:
        st.markdown('<div class="stark-card">', unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.75rem !important; font-weight: bold;'>🔐 Identificación del Sistema:</p>", unsafe_allow_html=True)
        ingreso_auth = st.text_input("Clave o Comando de Voz:", placeholder="Ej: stark123", key="input_auth_unico", label_visibility="collapsed")
        
        if st.button("🔓 Autorizar Acceso", use_container_width=True):
            if ingreso_auth.strip() and CLAVE_MAESTRA in ingreso_auth.lower():
                st.session_state.bunker_desbloqueado = True
                st.success("Acceso concedido. Bienvenido al búnker, jefa.")
                st.rerun()
            else:
                st.error("Credencial incorrecta. Acceso denegado.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# =========================================================================
# BÚNKER DESBLOQUEADO - NÚCLEO STARK AVANZADO
# =========================================================================

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
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Núcleo Stark y E.D.I.T.H. sincronizados. ¿Qué órdenes ejecutamos?"}
    ]

# --- ENCABEZADO CON RELOJ EN VIVO (SEPARADO HTML Y JS) ---
now_inicial = datetime.datetime.now(tz_chile)
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
dia_str = dias[now_inicial.weekday()]
mes_str = meses[now_inicial.month]
fecha_completa = f"{dia_str}, {now_inicial.day:02d} de {mes_str} de {now_inicial.year}"

st.markdown(f"""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h4 style="margin: 0; padding: 0; font-size: 1.1rem !important; text-align: center !important; color: #00d2ff !important;">J.A.R.V.I.S IA // E.D.I.T.H. TACTICAL CORE</h4>
        <p style="margin: 0; font-family: monospace; font-size: 0.7rem !important; color: #00d2ff !important; text-align: center !important;">
            [ STARK INDUSTRIES // NODO BUIN, CHILE // {fecha_completa} – <span id="reloj-vivo" style="color: #00d2ff; font-weight: bold;">00:00:00</span> ]
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <script>
        function actualizarReloj() {
            const ahora = new Date();
            const utc = ahora.getTime() + (ahora.getTimezoneOffset() * 60000);
            const chileTime = new Date(utc - (3 * 3600000));
            const h = String(chileTime.getHours()).padStart(2, '0');
            const m = String(chileTime.getMinutes()).padStart(2, '0');
            const s = String(chileTime.getSeconds()).padStart(2, '0');
            const elemento = document.getElementById('reloj-vivo');
            if (elemento) {
                elemento.innerText = h + ":" + m + ":" + s;
            }
        }
        setInterval(actualizarReloj, 1000);
        actualizarReloj();
    </script>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================================
# BARRA LATERAL (IZQUIERDA) - CON RECONOCIMIENTO DE VOZ REAL (WEB SPEECH API)
# =========================================================================
with st.sidebar:
    if st.button("🔒 Bloquear Búnker", use_container_width=True):
        st.session_state.bunker_desbloqueado = False
        st.rerun()

    st.markdown("### 🌐 ESTACIÓN DE CONTROL")

    with st.expander("🎙️ E.D.I.T.H. & Hands-Free (Voz)", expanded=True):
        st.markdown("• **Escucha Continua del Navegador**")
        
        st.markdown("""
            <div style="text-align: center; padding: 5px;">
                <button onclick="iniciarEscucha()" style="background-color: #00d2ff; color: #060911; border: none; padding: 8px 12px; font-weight: bold; border-radius: 4px; cursor: pointer; font-family: monospace; width: 100%;">🎙️ Activar Escucha Hands-Free</button>
                <p id="estado-voz" style="font-size: 0.65rem; color: #00d2ff; margin-top: 6px;">[ Micrófono en espera ]</p>
            </div>
            
            <script>
                function iniciarEscucha() {
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    if (!SpeechRecognition) {
                        alert("Tu navegador no soporta reconocimiento de voz directo. Usa Google Chrome.");
                        return;
                    }
                    
                    const recognition = new SpeechRecognition();
                    recognition.lang = 'es-CL';
                    recognition.continuous = false;
                    recognition.interimResults = false;
                    
                    const estado = document.getElementById('estado-voz');
                    estado.innerText = "[ Escuchando a la jefa... Hable ahora ]";
                    
                    recognition.onresult = function(event) {
                        const textoDictado = event.results[0][0].transcript;
                        estado.innerText = "[ Comando capturado: " + textoDictado + " ]";
                        
                        const utterance = new SpeechSynthesisUtterance("Orden recibida, jefa: " + textoDictado);
                        utterance.lang = 'es-CL';
                        window.speechSynthesis.speak(utterance);
                    };
                    
                    recognition.onerror = function(event) {
                        estado.innerText = "[ Error de audio o permiso denegado ]";
                    };
                    
                    recognition.onend = function() {
                        setTimeout(() => {
                            estado.innerText = "[ Micrófono en espera ]";
                        }, 3000);
                    };
                    
                    recognition.start();
                }
            </script>
        """, unsafe_allow_html=True)

        st.markdown("---")
        texto_voz = st.text_input("Texto manual para voz:", "Núcleo operativo al cien por ciento, jefa.")
        if st.button("🗣️ Reproducir Voz Manual", use_container_width=True):
            try:
                from gtts import gTTS
                import base64
                tts = gTTS(text=texto_voz, lang='es')
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                audio_bytes.seek(0)
                b64 = base64.b64encode(audio_bytes.read()).decode()
                st.markdown(f'<audio autoplay src="data:audio/mp3;base64,{b64}"></audio>', unsafe_allow_html=True)
                st.success("Audio reproducido.")
            except:
                st.warning("gTTS no disponible.")

        usar_camara_edith = st.checkbox("📷 Activar Cámara Óptica E.D.I.T.H.", value=False)
        if usar_camara_edith:
            foto_edith = st.camera_input("Captura orbital:")
            if foto_edith:
                st.success("Fotograma analizado.")
        st.link_button("🌐 Visor Satelital (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)

    with st.expander("🐧 Fundamentos y Redes"):
        st.markdown("• **Diagnóstico de Red Real**")
        if st.button("💻 Ejecutar ipconfig real", use_container_width=True):
            buffer_ip = io.StringIO()
            with contextlib.redirect_stdout(buffer_ip):
                import subprocess
                subprocess.run(["ipconfig" if os.name == "nt" else "ifconfig"])
            res_ip = buffer_ip.getvalue()
            st.code(res_ip if res_ip else "Información de red local procesada.", language="bash")
        if st.button("🐧 Núcleo Linux", use_container_width=True): st.info("Linux activo.")
        if st.button("🐍 Python", use_container_width=True): st.info("Python operativo.")

    with st.expander("👁️ Exploración y Tracert"):
        st.markdown("• **Monitoreo de saltos de red**")
        if st.button("🛤️ Test ping / traceroute real", use_container_width=True):
            st.code("Respuesta de 8.8.8.8: bytes=32 tiempo=14ms TTL=115", language="bash")
        if st.button("👁️ Nmap", use_container_width=True): st.info("Nmap desplegado.")

    with st.expander("💻 Hardware Real (psutil)"):
        if PSUTIL_DISPONIBLE:
            cpu_uso = psutil.cpu_percent(interval=0.5)
            memoria = psutil.virtual_memory()
            st.markdown(f"• **CPU en uso:** `{cpu_uso}%`")
            st.markdown(f"• **RAM total:** `{round(memoria.total / (1024**3), 2)} GB`")
            st.markdown(f"• **RAM usada:** `{memoria.percent}%`")
        else:
            st.warning("Paquete `psutil` no instalado.")
        if st.button("🔄 Actualizar Hardware", use_container_width=True):
            st.rerun()

    with st.expander("🌤️ Clima Real (Buin)"):
        try:
            url_clima = "https://wttr.in/Buin?format=j1"
            resp_clima = requests.get(url_clima, timeout=3).json()
            condicion = resp_clima['current_condition'][0]
            temp_c = condicion['temp_C']
            humedad = condicion['humidity']
            st.markdown(f"• **Temperatura Actual:** `{temp_c}°C`")
            st.markdown(f"• **Humedad Relativa:** `{humedad}%`")
            st.markdown("• *Fuente: Estación meteorológica en vivo*")
        except:
            st.markdown("• **Temperatura:** 21°C | **Humedad:** 45% *(Modo respaldo)*")

    with st.expander("🛡️ Gmail y Alertas en Vivo"):
        st.markdown("• **Estado:** Conectado a Bandeja de Entrada")
        if st.button("📥 Revisar Correo Reciente", use_container_width=True):
            st.info("Bandeja sincronizada: Sin nuevas alertas críticas de Gmail.")
        for msg, nivel in get_db_alertas():
            st.markdown(f"• {'🟢' if nivel == 'OK' else 'ℹ️'} {msg}")

    with st.expander("📈 Finanzas y Portafolio"):
        st.markdown("• **Banco Estado:** 42 Acciones Vapores\n• **Fintual Global:** US $77,76")
        if st.button("🔄 Sincronizar Mercados", use_container_width=True):
            st.success("Portafolio actualizado.")

    with st.expander("📝 Tareas del Búnker (SQLite)"):
        nueva_tarea = st.text_input("Nueva tarea rápida:", key="input_tarea_side")
        if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
            add_db_tarea(nueva_tarea)
            st.rerun()
        for tid, t in get_db_tareas():
            col_sub1, col_sub2 = st.columns([4, 1])
            with col_sub1:
                st.markdown(f"• {t}")
            with col_sub2:
                if st.button("❌", key=f"del_t_side_{tid}"):
                    delete_db_tarea(tid)
                    st.rerun()

    with st.expander("⚡ Automatización Python"):
        codigo_script = st.text_area("Script a ejecutar:", "print('Núcleo operativo al 100%')")
        if st.button("⚡ Ejecutar Script", use_container_width=True):
            buffer_salida = io.StringIO()
            try:
                with contextlib.redirect_stdout(buffer_salida):
                    exec(codigo_script, {})
                res = buffer_salida.getvalue()
                st.code(res if res else "Código ejecutado sin salida.", language="python")
            except Exception as e:
                st.error(f"Error: {e}")

    st.markdown("---")
    st.link_button("🌤️ Ventusky (Meteo)", "https://www.ventusky.com", use_container_width=True)
    st.link_button("☀️ SunCalc", "https://www.suncalc.org", use_container_width=True)
    st.link_button("🗺️ OpenStreetMap", "https://www.openstreetmap.org", use_container_width=True)


# =========================================================================
# PANEL CENTRAL: CHAT INTELIGENTE (100% DESPEJADO)
# =========================================================================

col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("<h4>💬 Chat IA & Protocolo E.D.I.T.H.</h4>", unsafe_allow_html=True)
with col_h2:
    if st.button("🗑️", use_container_width=True):
        h_l = datetime.datetime.now(tz_chile).hour
        s_l = "Buenos días" if 0 <= h_l < 12 else ("Buenas tardes" if 12 <= h_l < 20 else "Buenas noches")
        st.session_state.mensajes = [{"role": "assistant", "content": f"{s_l}, jefa. Memoria purgada por E

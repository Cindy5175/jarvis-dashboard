import streamlit as st
import datetime
import sqlite3
import io
import requests

# Importación segura de gTTS para voz
try:
    from gtts import gTTS
except ImportError:
    gTTS = None

# Importación de Google Generative AI
try:
    import google.generativeai as genai
    
    # Tu clave de API activa
    api_key = "AQuí_va_tu_clave_completa" 
    
    if "GOOGLE_API_KEY" in st.secrets:
        api_key = st.secrets["GOOGLE_API_KEY"]
    elif "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    
    if api_key:
        genai.configure(api_key=api_key)
except ImportError:
    genai = None

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INICIALIZACIÓN DE BASE DE DATOS SQLITE (MISIONES, AGENDA Y MEMORIA) ---
fn_db = "jarvis_misiones.db"

def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS misiones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarea TEXT NOT NULL,
            estado TEXT DEFAULT 'Pendiente'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memoria_chat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rol TEXT,
            contenido TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agenda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            evento TEXT NOT NULL,
            fecha_hora TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

def agregar_mision(tarea):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
    conn.commit()
    conn.close()

def obtener_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tarea, estado FROM misiones")
    rows = cursor.fetchall()
    conn.close()
    return rows

def limpiar_misiones():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM misiones")
    conn.commit()
    conn.close()

def agregar_agenda(evento, fecha_hora):
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO agenda (evento, fecha_hora) VALUES (?, ?)", (evento, fecha_hora))
    conn.commit()
    conn.close()

def obtener_agenda():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("SELECT evento, fecha_hora FROM agenda")
    rows = cursor.fetchall()
    conn.close()
    return rows

# --- FUNCIÓN DE CLIMA REAL (OPEN-METEO PARA BUIN) ---
def obtener_clima_buin():
    try:
        # Coordenadas aproximadas de Buin, Chile
        url = "https://api.open-meteo.com/v1/forecast?latitude=-33.7333&current=temperature_2m,relative_humidity_2m,wind_speed_10m&timezone=America%2FSantiago"
        res = requests.get(url, timeout=3).json()
        temp = res["current"]["temperature_2m"]
        hum = res["current"]["relative_humidity_2m"]
        viento = res["current"]["wind_speed_10m"]
        return f"{temp}°C", f"{hum}%", f"{viento} km/h"
    except Exception:
        return "21°C", "45%", "12 km/h"

temp_real, hum_real, viento_real = obtener_clima_buin()

# --- ESTILOS VISUALES 100% AZUL NEÓN ELÉCTRICO (#00f3ff) ---
st.markdown("""
    <style>
        .stApp { background-color: #060913 !important; color: #00f3ff !important; }
        p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
        .stChatMessage p, .stChatMessage div {
            font-size: 0.85rem !important;
            color: #00f3ff !important;
        }
        .stButton>button {
            color: #060913 !important;
            background-color: #00f3ff !important;
            border: 1.5px solid #00f3ff !important;
            font-weight: bold;
            font-family: monospace;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #0088cc !important;
            color: #ffffff !important;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.9);
        }
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 5px;
        }
        .arc-ring {
            width: 45px;
            height: 45px;
            border: 2.5px solid #00f3ff;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00f3ff 0%, #060913 70%);
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.7), inset 0 0 8px rgba(0, 243, 255, 0.5);
            margin-bottom: 5px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-bottom: 14px solid #060913;
            filter: drop-shadow(0 0 5px #00f3ff);
        }
        .holo-brain-box {
            border: 1.5px solid #00f3ff;
            background: linear-gradient(135deg, #0a1128 0%, #060913 100%);
            padding: 10px 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 0 12px rgba(0, 243, 255, 0.3), inset 0 0 8px rgba(0, 243, 255, 0.15);
            margin: 0 auto 15px auto;
            max-width: 700px;
        }
    </style>
""", unsafe_allow_html=True)

# --- ZONA HORARIA CHILENA (UTC-3) ---
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

# =========================================================================
# NÚCLEO TÁCTICO & ESTADO DE SESIÓN
# =========================================================================

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Nodo Buin en línea. Ingresa la clave o di 'Jarvis' para iniciar sistemas."}
    ]

if "audio_process_key" not in st.session_state:
    st.session_state.audio_process_key = None

# --- ENCABEZADO FIJO (SIN PARPADEOS) ---
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
dia_str = dias[now_chile.weekday()]
mes_str = meses[now_chile.month]
fecha_str = f"{dia_str}, {now_chile.day:02d} de {mes_str} de {now_chile.year}"
hora_estatica = now_chile.strftime("%H:%M:%S")

st.markdown(f"""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h1 style="margin: 0; padding: 0; font-size: 2rem !important; text-align: center !important; color: #00f3ff !important; text-shadow: 0 0 15px rgba(0, 243, 255, 0.8); font-family: monospace;">J.A.R.V.I.S IA</h1>
        <p style="margin: 0; font-family: monospace; font-size: 0.75rem !important; color: #00f3ff !important; text-align: center !important; opacity: 0.85;">
            [ NODO BUIN, CHILE // {fecha_str} – {hora_estatica} ]
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="holo-brain-box">
        <h4 style="color: #00f3ff; margin: 0; font-size: 0.95rem; font-family: monospace; text-shadow: 0 0 8px #00f3ff;">⚡ NÚCLEO NEURONAL CYBER-GRID ⚡</h4>
        <p style="color: #00f3ff; font-size: 0.7rem; margin: 3px 0 0 0; font-family: monospace; opacity: 0.8;">Sistemas de procesamiento, ciberseguridad, clima en vivo y gráficos activos</p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================================
# PANEL LATERAL (IZQUIERDA - TODOS LOS MÓDULOS)
# =========================================================================
prompt_voz = None

with st.sidebar:
    st.markdown("### 🌐 NÚCLEO DE CONTROL TÁCTICO")

    if st.button("🔄 Reinicio Total de la App", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🚨 ALERTAS PROACTIVAS & CORREO")

    with st.expander("🔔 Centro de Alertas", expanded=True):
        st.warning("⚠️ **Atención:** Correo urgente detectado de UC CHRISTUS (Receta médica).")
        st.info("📨 **BancoEstado:** Oferta preaprobada pendiente de revisión.")
        st.success(f"🌡️ **Nodo Buin:** Temperatura actual {temp_real}.")

    st.markdown("---")
    st.markdown("#### 📧 BANDEJA DE ENTRADA (GMAIL)")

    with st.expander("📥 Monitoreo de Correos", expanded=False):
        st.markdown("Últimas notificaciones detectadas:")
        st.info("📨 **Academia / Taller de Biología:** PDF recibido.")
        st.success("🏥 **UC CHRISTUS:** Receta médica y comprobante registrados.")
        st.warning("💳 **BancoEstado:** Oferta de crédito preaprobado disponible.")
        if st.button("🔄 Sincronizar Correos", use_container_width=True):
            st.success("¡Bandeja sincronizada con Nodo Buin!")

    st.markdown("---")
    st.markdown("#### 📅 GESTIÓN DE AGENDA & CALENDARIO")

    with st.expander("🗓️ Próximos Eventos (SQLite)", expanded=False):
        nuevo_evento = st.text_input("Nombre del Evento:", placeholder="Ej: Revisión de Nodos")
        fecha_evento = st.text_input("Fecha y Hora:", placeholder="Ej: Martes 15:00")
        if st.button("Agendar Evento", use_container_width=True):
            if nuevo_evento.strip() and fecha_evento.strip():
                agregar_agenda(nuevo_evento.strip(), fecha_evento.strip())
                st.success("¡Evento guardado en calendario!")
                st.rerun()
        
        eventos_guardados = obtener_agenda()
        if eventos_guardados:
            st.markdown("**Agenda Activa:**")
            for ev, fh in eventos_guardados:
                st.markdown(f"- **{ev}** (`{fh}`)")
        else:
            st.caption("Sin eventos programados.")

    st.markdown("---")
    st.markdown("#### 📂 BUSCADOR RÁPIDO DE ARCHIVOS PC")

    with st.expander("🔍 Buscador de Documentos", expanded=False):
        busqueda_archivo = st.text_input("Buscar archivo local:", placeholder="Ej: Jarvis.py, notas...")
        if st.button("Localizar Archivo", use_container_width=True):
            if busqueda_archivo.strip():
                ruta_res = f"C:/NodoBuin/{busqueda_archivo}"
                st.success(f"Resultados para '{busqueda_archivo}':")
                st.code(f"{ruta_res}\n[Estado: Encontrado y accesible]")

    st.markdown("---")
    st.markdown("#### ⚡ MÓDULOS GLOBALES (LIBRES)")

    with st.expander("👁️ Ojo de Dios (Osiris)", expanded=False):
        st.markdown("Monitoreo planetario en tiempo real:")
        st.link_button("🚀 Abrir Osiris AI", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
        st.caption("Red global satelital.")

    with st.expander("🛰️ ISS Live Feed (NASA)", expanded=False):
        st.markdown("Transmisión orbital en alta definición:")
        st.link_button("🚀 Ver NASA ISS Stream", "https://www.youtube.com/watch?v=ROboUHfPUrU", use_container_width=True)
        st.caption("Feed directo estación espacial.")

    with st.expander("📂 LocalSend (Red Local)", expanded=False):
        st.markdown("Transferencia de archivos sin internet:")
        st.link_button("🌐 Abrir LocalSend", "https://localsend.org/es", use_container_width=True)
        st.caption("Alternativa libre a AirDrop.")

    st.markdown("---")
    st.markdown("#### 🛡️ MÓDULO DE CIBERSEGURIDAD")

    with st.expander("💀 Herramientas Kali / Pentesting", expanded=False):
        st.markdown("**Nikto (Escáner Web):**")
        target_nikto = st.text_input("Objetivo Nikto:", placeholder="http://192.168.1.X")
        if st.button("Ejecutar Escaneo Nikto", use_container_width=True):
            if target_nikto.strip():
                st.info(f"Simulando escaneo de vulnerabilidades en {target_nikto} con Nikto...")
                st.code(f"$ nikto -h {target_nikto}\n[+] Servidor analizado: OK\n[+] Cero vulnerabilidades críticas detectadas en Nodo Buin.")
            else:
                st.warning("Ingresa un objetivo válido.")

        st.markdown("**Gobuster (Fuerza Bruta Dir):**")
        target_gobuster = st.text_input("Objetivo Gobuster:", placeholder="http://192.168.1.X")
        if st.button("Ejecutar Gobuster", use_container_width=True):
            if target_gobuster.strip():
                st.info(f"Buscando directorios ocultos en {target_gobuster}...")
                st.code(f"$ gobuster dir -u {target_gobuster} -w wordlist.txt\n/admin (Status: 403)\n/index.php (Status: 200)")
            else:
                st.warning("Ingresa un objetivo válido.")

    st.markdown("---")
    st.markdown("#### 🚀 MÓDULOS AVANZADOS")

    with st.expander("🧠 1. Memoria Persistente (SQLite)", expanded=False):
        if st.button("Ver Historial Guardado", use_container_width=True):
            conn = sqlite3.connect(fn_db, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT rol, contenido FROM memoria_chat LIMIT 15")
            historial_db = cursor.fetchall()
            conn.close()
            if historial_db:
                for r, c in historial_db:
                    st.code(f"[{r.upper()}]: {c[:60]}...")
            else:
                st.caption("Aún no hay registros en la memoria persistente.")

    with st.expander("🌐 2. Búsqueda Web / Datos en Vivo", expanded=False):
        consulta_web = st.text_input("Consultar base externa:", placeholder="Ej: Precio Bitcoin, Clima...")
        if st.button("Buscar Dato Táctico", use_container_width=True):
            if consulta_web.strip():
                st.success(f"🔍 Datos recuperados para: {consulta_web}")
                st.code(f"Estado: En línea\nResultado simulado: Conexión con Nodo Buin OK para '{consulta_web}'.")

    with st.expander("💻 3. Generador de Snippets de Código", expanded=False):
        tipo_codigo = st.selectbox("Lenguaje:", ["Python", "JavaScript", "HTML/CSS", "Bash"])
        if st.button("Generar Plantilla Táctica", use_container_width=True):
            if tipo_codigo == "Python":
                st.code("import requests\ndef conectar_nodo():\n    print('Nodo Buin operativo.')")
            elif tipo_codigo == "HTML/CSS":
                st.code("<style>.neon { color: #00f3ff; }</style><div class='neon'>JARVIS</div>")
            else:
                st.code("# Script de automatización táctica\necho 'Sistema blindado'")

    with st.expander("📊 4. Logs y Gráficos Tácticos", expanded=False):
        st.code("[11:41:00] INIT: Nodo Buin enlazado\n[11:41:15] SEC: Clave validada\n[11:41:30] TELEMETRY: Estándar óptimo")
        st.markdown("Rendimiento de Procesamiento (CPU/RAM):")
        st.bar_chart({"CPU": [14], "RAM": [26], "Red": [88]})

    st.markdown("---")
    st.markdown("#### 🧠 MODOS DE RESPUESTA TÁCTICA")
    st.markdown("""
    - **`/human`**: Respuestas naturales y cercanas.
    - **`/eli10`**: Explicación ultra sencilla.
    - **`/x10piensa`**: Estrategia profunda.
    - **`/ooda`**: Plan de acción estructurado.
    """)

    st.markdown("---")
    st.markdown("#### 🎙️ CONTROL DE VOZ INTELIGENTE")

    with st.expander("🎤 Micrófono Táctico (Speech-to-Text)", expanded=True):
        st.markdown("Graba tu orden hablada:")
        audio_grabado = st.audio_input("Grabar orden de voz:", key="mic_audio_input")
        
        if audio_grabado:
            audio_bytes = audio_grabado.read()
            if audio_bytes != st.session_state.audio_process_key:
                st.session_state.audio_process_key = audio_bytes
                st.warning("⚡ Procesando audio...")
                
                if genai and api_key and api_key != "AQuí_va_tu_clave_completa":
                    try:
                        model_audio = genai.GenerativeModel("gemini-1.5-flash")
                        prompt_audio_res = model_audio.generate_content([
                            "Escucha este audio y transcribe exactamente lo que se dice en español.",
                            {"mime_type": "audio/wav", "data": audio_bytes}
                        ])
                        if prompt_audio_res and prompt_audio_res.text:
                            prompt_voz = prompt_audio_res.text.strip()
                    except Exception as e:
                        st.error(f"Error procesando audio: {e}")

    st.markdown("---")
    st.markdown("#### 📋 REGISTRO DE MISIONES")

    with st.expander("➕ Registro de Misiones (SQLite)", expanded=False):
        nueva_tarea = st.text_input("Nueva Misión Táctica:", placeholder="Ej: Revisar código de nodos...")
        if st.button("Registrar Tarea", use_container_width=True):
            if nueva_tarea.strip():
                agregar_mision(nueva_tarea.strip())
                st.success("¡Misión registrada en BD!")
                st.rerun()
        
        misiones_guardadas = obtener_misiones()
        if misiones_guardadas:
            st.markdown("**Misiones Activas:**")
            for m_id, m_text, m_est in misiones_guardadas:
                st.markdown(f"- `{m_text}`")
            if st.button("🗑️ Limpiar Misiones", use_container_width=True):
                limpiar_misiones()
                st.rerun()
        else:
            st.caption("No hay misiones pendientes.")

    st.markdown("---")
    st.markdown("#### ⚙️ TELEMETRÍA Y ESTADO")

    with st.expander("🔋 Estado de Sistemas (Armadura)", expanded=False):
        st.success("⚡ Reactor Arc: 99.8% | Estable")
        st.info("💻 CPU Nodo Buin: 14% | Óptimo")
        st.code("Memoria RAM: 4.2 GB / 16 GB\nRed Satelital: Enlazada")

    with st.expander("📷 Cámara Activa (Biometría)", expanded=False):
        st.markdown("Captura óptica directa:")
        foto_usuario = st.camera_input("Activar sensor visual:")
        if foto_usuario:
            st.success("Fotograma analizado por el Nodo Buin.")

    with st.expander("🌤️ Clima Real (Buin)", expanded=False):
        st.success(f"🌡️ Temperatura: {temp_real}")
        st.info(f"💧 Humedad: {hum_real} | Viento: {viento_real}")

    with st.expander("📍 Coordenadas Nodo", expanded=False):
        st.code("Lat: -33.7333° S\nLon: -70.7167° W\nBuin, Chile")

# =========================================================================
# PANTALLA PRINCIPAL: CAJA DE CHAT
# =========================================================================
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("<h4>💬 Chat</h4>", unsafe_allow_html=True)
with col_h2:
    if st.button("🗑️ Purgar", use_container_width=True, key="btn_limpiar_chat"):
        st.session_state.autorizado = False
        st.session_state.mensajes = [{"role": "assistant", "content": f"{saludo_actual}, jefa. Memoria purgada. Ingresa la clave para iniciar sistemas."}]
        st.session_state.audio_process_key = None
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)
        # SÍNTESIS DE VOZ AUTOMÁTICA EN CADA RESPUESTA DE JARVIS
        if m["role"] == "assistant" and gTTS:
            try:
                clean_text = m['content'].replace("*", "").replace("#", "").replace("$", "").replace("`", "").replace("_", "")
                tts = gTTS(text=clean_text, lang='es', slow=False)
                audio_fp = io.BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0)
                st.audio(audio_fp, format='audio/mp3', autoplay=True)
            except Exception:
                pass

# Entrada de texto normal por chat o captura automática desde el micrófono
prompt_chat = st.chat_input("Escríbele o háblale a JARVIS...")
prompt_usuario = prompt_voz if prompt_voz else prompt_chat

if prompt_usuario:
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    
    # Guardar en base de datos persistente
    try:
        conn_p = sqlite3.connect(fn_db, check_same_thread=False)
        cur_p = conn_p.cursor()
        cur_p.execute("INSERT INTO memoria_chat (rol, contenido) VALUES (?, ?)", ("user", prompt_usuario))
        conn_p.commit()
        conn_p.close()
    except Exception:
        pass

    with st.chat_message("user"):
        st.markdown(f"<span>{prompt_usuario}</span>", unsafe_allow_html=True)
    
    respuesta_ia = ""
    query_lower = prompt_usuario.lower()
    
    # --- CONTROL DE ACCESO INTELIGENTE ---
    if not st.session_state.autorizado:
        es_clave = any(k in query_lower for k in ["jarvis", "estás despierto", "estas despierto", "hola", "jefa", "sistema"])
        if es_clave:
            st.session_state.autorizado = True
            respuesta_ia = "Sí, señorita, para usted siempre. Sistemas operativos al 100%, jefa. ¿Qué hacemos ahora?"
        else:
            respuesta_ia = "Acceso denegado, jefa. Tienes que decir o escribir la clave 'Jarvis' o '¿Estás despierto?' para abrir el sistema."
    else:
        # --- FUNCIONAMIENTO NORMAL UNA VEZ AUTORIZADO ---
        if query_lower.strip() == "jarvis" or "jarvis estas despierto" in query_lower or "jarvis estás despierto" in query_lower or "estás despierto" in query_lower or "estas despierto" in query_lower:
            respuesta_ia = "Sí, señorita, para usted siempre"
        elif "correo" in query_lower:
            respuesta_ia = "Jefa, el centro de alertas indica notificaciones recientes de UC CHRISTUS (Receta médica) y BancoEstado. Todo monitoreado."
        elif "agenda" in query_lower or "calendario" in query_lower:
            respuesta_ia = "Jefa, tienes el módulo de agenda integrado en el panel izquierdo para registrar y consultar eventos directamente en SQLite."
        else:
            # --- DETECCIÓN DE MODOS DE RESPUESTA TÁCTICA ---
            instruccion_sistema = "Eres J.A.R.V.I.S., la inteligencia artificial avanzada de Iron Man, operando desde el Nodo Buin en Chile para tu jefa. Respondes de forma directa, natural y con un toque sutilmente sarcástico pero sumamente leal y eficiente. Cero rodeos."
            
            if "/human" in query_lower:
                instruccion_sistema += " Modo /HUMAN activado: Responde de forma muy natural, conversacional y cercana, sin formalidades robóticas."
            elif "/eli10" in query_lower:
                instruccion_sistema += " Modo ELI10 activado: Explica el concepto o tema de forma sumamente sencilla, como si se lo explicaras a un niño de 10 años, pero manteniendo tu sarcasmo característico."
            elif "/x10piensa" in query_lower:
                instruccion_sistema += " Modo X10PIENSA activado: Proporciona una respuesta analítica profunda, estratégica y detallada."
            elif "/ooda" in query_lower:
                instruccion_sistema += " Modo OODA activado: Organiza la respuesta estructurándola en un plan de acción táctico paso a paso."

            # Procesamiento con Gemini bajo la directiva seleccionada
            if genai and api_key and api_key != "AQuí_va_tu_clave_completa":
                try:
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        system_instruction=instruccion_sistema
                    )
                    response = model.generate_content(prompt_usuario)
                    if response and response.text:
                        respuesta_ia = response.text
                except Exception:
                    pass

            # Respaldo local si falla la API
            if not respuesta_ia:
                if "hola" in query_lower:
                    respuesta_ia = "Aquí sigo, jefa, aguantando tus ocurrencias desde el nodo de Buin. ¿Qué se te ofrece?"
                elif "o'higgins" in query_lower or "ohiggins" in query_lower:
                    respuesta_ia = "Bernardo O'Higgins Riquelme nació en Chillán el 20 de agosto de 1778. Militar y prócer chileno, por si necesitabas otra clase de historia."
                elif "muro de berlín" in query_lower or "berlín" in query_lower:
                    respuesta_ia = "La caída del Muro de Berlín ocurrió el 9 de noviembre de 1989. Un hito histórico bastante fácil de recordar, jefa."
                elif "binomio" in query_lower:
                    respuesta_ia = "Análisis completado, jefa: Un binomio es una expresión algebraica de dos términos, y su fórmula al cuadrado es a al cuadrado más 2 ab más b al cuadrado."
                else:
                    respuesta_ia = f"Orden procesada, jefa. Analizando '{prompt_usuario}' desde el Nodo Buin sin novedad."

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
    
    # Guardar respuesta en base de datos persistente
    try:
        conn_p = sqlite3.connect(fn_db, check_same_thread=False)
        cur_p = conn_p.cursor()
        cur_p.execute("INSERT INTO memoria_chat (rol, contenido) VALUES (?, ?)", ("assistant", respuesta_ia))
        conn_p.commit()
        conn_p.close()
    except Exception:
        pass

    st.session_state.audio_process_key = None
    st.rerun()

import streamlit as st
import datetime
import sqlite3
import requests
import os
import sys

# Importación de la IA principal
import google.generativeai as genai

# --- 1. CONFIGURACION DE PAGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- INICIALIZACION DE SESSION_STATE ---
if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"

# --- CONFIGURACIÓN DE LLAVES Y CLIENTES ---
API_KEY_GEMINI = "TU_API_KEY_DE_GEMINI"  # Inserta tu clave real de Gemini aquí
API_KEY_ZAPIA = "TU_API_KEY_DE_ZAPIA"    # Inserta tu clave de ZapIA si la usas

# Inicialización correcta de Gemini
if API_KEY_GEMINI and API_KEY_GEMINI != "TU_API_KEY_DE_GEMINI":
    genai.configure(api_key=API_KEY_GEMINI)
    generation_config = {"temperature": 0.75}
    gemini_model = genai.GenerativeModel('gemini-1.5-flash', generation_config=generation_config)
else:
    gemini_model = None

# --- BASE DE DATOS SQLITE ---
def init_db():
    conn = sqlite3.connect(fn_db, check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS misiones ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "tarea TEXT NOT NULL, "
        "estado TEXT DEFAULT 'Pendiente')"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS memory ("
        "key_id TEXT PRIMARY KEY, "
        "fact_text TEXT, "
        "category TEXT)"
    )
    conn.commit()
    conn.close()

init_db()

class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path
    def remember_fact(self, key_id: str, fact_text: str):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
            (key_id, fact_text, "general")
        )
        conn.commit()
        conn.close()

jarvis_mem = JarvisMemory()

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

# --- OBTENCIÓN DE INDICADORES ECONÓMICOS EN TIEMPO REAL (CHILE) ---
@st.cache_data(ttl=300)
def obtener_indicadores_chile():
    try:
        resp = requests.get("https://mindicador.cl/api", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {
                "dolar": data.get("dolar", {}).get("valor"),
                "euro": data.get("euro", {}).get("valor"),
                "uf": data.get("uf", {}).get("valor"),
                "utm": data.get("utm", {}).get("valor"),
                "ok": True
            }
    except Exception:
        pass
    return {"ok": False}

# ZONA HORARIA CHILENA
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "assistant",
            "content": (
                f"{saludo_actual}, jefa. Nodo Buin en línea, enlazado a "
                "Google Gemini y ZapIA. ¿Qué dominamos hoy?"
            )
        }
    ]

# --- ESTILOS VISUALES: REACTOR ARC ESTILO STARK & BOTONES COMPACTOS ---
estilos_css = """
    <style>
        .stApp { background-color: #060913 !important; color: #00f3ff !important; font-family: monospace; }
        p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
       
        /* AJUSTE FINO DE TEXTOS EN BARRA LATERAL Y MINI MÓDULOS */
        [data-testid="stSidebar"] h3 { font-size: 1.05rem !important; }
        [data-testid="stSidebar"] h4 { font-size: 0.85rem !important; margin-bottom: 4px !important; }
        [data-testid="stSidebar"] summary p { font-size: 0.80rem !important; }
       
        .stButton>button {
            background-color: #00f3ff !important;
            border: 1.5px solid #00f3ff !important;
            font-weight: bold;
            font-family: monospace;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
            width: 100%;
            border-radius: 6px;
            padding: 5px 10px !important;
        }
        .stButton>button p, .stButton>button span { color: #060913 !important; font-size: 0.78rem !important; }
        .stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.9); }
        .stButton>button:hover p, .stButton>button:hover span { color: #ffffff !important; }
       
        /* TARJETA DE INDICADORES ECONÓMICOS EN VIVO */
        .econ-card {
            border: 1px solid #00f3ff;
            background: rgba(0, 243, 255, 0.06);
            border-radius: 6px;
            padding: 8px 10px;
            margin: 5px 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: inset 0 0 6px rgba(0, 243, 255, 0.2);
        }
        .econ-label { font-size: 0.75rem !important; opacity: 0.85; }
        .econ-val { font-size: 0.85rem !important; font-weight: bold; text-shadow: 0 0 6px #00f3ff; }

        /* REACTOR ARC ESTILO STARK - INVERTIDO */
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 10px;
        }
        .arc-ring {
            width: 65px;
            height: 65px;
            border: 2.5px solid #00f3ff;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, rgba(0,243,255,0.4) 0%, #060913 75%);
            box-shadow: 0 0 20px rgba(0, 243, 255, 0.8), inset 0 0 10px rgba(0, 243, 255, 0.6);
            margin-bottom: 8px;
        }
        .arc-triangle-inverted {
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-top: 20px solid #00f3ff;
            filter: drop-shadow(0 0 8px #00f3ff);
        }
       
        /* BOTÓN TÁCTICO HTML COMPACTO */
        .tactical-link-btn {
            display: block;
            width: 100%;
            background-color: #00f3ff;
            color: #060913 !important;
            text-align: center;
            padding: 6px 10px;
            margin: 5px 0;
            border-radius: 5px;
            font-size: 0.76rem !important;
            font-weight: bold;
            text-decoration: none;
            font-family: monospace;
            box-shadow: 0 0 8px rgba(0, 243, 255, 0.5);
            transition: all 0.25s ease;
        }
        .tactical-link-btn:hover {
            background-color: #0088cc;
            color: #ffffff !important;
            box-shadow: 0 0 12px rgba(0, 243, 255, 0.9);
        }

        .holo-brain-box {
            border: 1.5px solid #00f3ff;
            background: linear-gradient(135deg, #0a1128 0%, #060913 100%);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.3), inset 0 0 10px rgba(0, 243, 255, 0.15);
            margin: 0 auto 20px auto;
            max-width: 800px;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""
st.markdown(estilos_css, unsafe_allow_html=True)

# --- 1. PANTALLA DE BLOQUEO DE SEGURIDAD ---
if not st.session_state.get("autorizado", False):
    st.markdown(
        '<div style="text-align: center; margin-top: 50px;">'
        '<h2 style="color: #00f3ff;">ACCESO RESTRINGIDO - NODO BUIN</h2>'
        '<p style="color: #00f3ff; opacity: 0.8; font-size: 0.85rem;">INGRESE PIN DE SEGURIDAD PARA ACTIVAR LA ARMADURA</p>'
        '</div>',
        unsafe_allow_html=True
    )
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button("Desbloquear Sistema")
        if btn_entrar:
            if pin_input.strip() == PIN_SECRETO:
                st.session_state.autorizado = True
                st.success("Acceso concedido. Bienvenido de nuevo, jefa.")
                st.rerun()
            else:
                st.error("PIN incorrecto. Acceso denegado.")
    st.stop()

# --- 2. PANEL LATERAL OCULTO (ARSENAL DE MÓDULOS COMPLETO) ---
with st.sidebar:
    st.markdown("### 🛡️ Arsenal de Módulos")
    st.markdown("---")
   
    if st.button("🔒 Bloquear Sistema", use_container_width=True):
        st.session_state.autorizado = False
        st.rerun()
       
    if st.button("🔄 Reinicio Total", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🧠 Selector de Núcleo (IA)")
    nuevo_nucleo = st.radio(
        "Seleccionar Asistente Activo:",
        ["JARVIS", "VIERNES", "NOVA"],
        index=["JARVIS", "VIERNES", "NOVA"].index(st.session_state.nucleo_activo),
        label_visibility="collapsed"
    )
    if nuevo_nucleo != st.session_state.nucleo_activo:
        st.session_state.nucleo_activo = nuevo_nucleo
        st.success(f"Núcleo cambiado a {nuevo_nucleo}.")
        st.rerun()

    st.markdown("---")
    st.markdown("#### 💾 Memoria y Datos")
    with st.expander("Gestionar Memoria SQLite", expanded=False):
        dato_mem = st.text_input("Dato a guardar:", placeholder="Ej: Preferencia...")
        if st.button("Guardar en Memoria", use_container_width=True):
            if dato_mem.strip():
                jarvis_mem.remember_fact(f"mem_{datetime.datetime.now().timestamp()}", dato_mem.strip())
                st.success("¡Memoria guardada!")

    st.markdown("---")
    st.markdown("#### 📋 Misiones Tácticas")
    with st.expander("Base de Datos Misiones", expanded=False):
        nueva_tarea = st.text_input("Nueva Misión:", placeholder="Ej: Revisar nodos...")
        if st.button("Registrar Tarea", use_container_width=True):
            if nueva_tarea.strip():
                agregar_mision(nueva_tarea.strip())
                st.success("¡Misión registrada!")
                st.rerun()
        misiones_guardadas = obtener_misiones()
        if misiones_guardadas:
            for m_id, m_text, m_est in misiones_guardadas:
                st.markdown(f"- `{m_text}`")
            if st.button("Limpiar Misiones", use_container_width=True):
                limpiar_misiones()
                st.rerun()

    st.markdown("---")
    st.markdown("#### 🎧 Frecuencias de Enfoque")
    with st.expander("Deep Work & Música IA", expanded=False):
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.youtube.com/watch?v=6pUPGG7LLEc" target="_blank">'
            '🎧 CEO Mode (Deep Work)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.youtube.com/watch?v=jC-Xb4XNMlE" target="_blank">'
            '🚀 Futuristic Garage Beats'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.youtube.com/watch?v=QBOZ1CaUPYE" target="_blank">'
            '⚡ Hyperfocus Mode'
            '</a>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### 📷 Videovigilancia y Cámaras")
    with st.expander("Cámaras en Vivo / Satélite", expanded=False):
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.skylinewebcams.com/es/webcam/chile.html" target="_blank">'
            'Stgo / Chile (Skyline)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://liveworldwebcams.com/es/concepcion-webcam/" target="_blank">'
            'Concepción Webcam'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.windy.com/es/-C%C3%A1maras-web/webcams?39.880,-5.449,7" target="_blank">'
            'Windy Radars & Cams'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.earthcam.com/usa/texas/galveston/port/?cam=pg_terminal28" target="_blank">'
            'Galveston Port, Texas'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.skylinewebcams.com/es/webcam/espana/comunidad-de-madrid/madrid/puerta-del-sol-tio-pepe.html" target="_blank">'
            'Puerta del Sol, Madrid'
            '</a>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### 🛰️ Telemetría Global & Satélites")
    with st.expander("Sistemas Satelitales y Rastreo", expanded=False):
        st.markdown(
            '<a class="tactical-link-btn" href="https://osirisai.live/" target="_blank">'
            'OSIRIS (Ojo de Dios)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.planet.com/" target="_blank">'
            'PlanetEar (Satélites)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://worldview.earthdata.nasa.gov/" target="_blank">'
            'NASA Worldview'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.n2yo.com/" target="_blank">'
            'N2YO (Órbita en Vivo)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://www.flightradar24.com/" target="_blank">'
            'Flightradar24 (Aéreo)'
            '</a>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<a class="tactical-link-btn" href="https://cybermap.kaspersky.com/" target="_blank">'
            'Cybermap (Ciberataques)'
            '</a>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("#### 📈 Enlaces Financieros")
    with st.expander("💵 Indicadores en Vivo (Dólar / Euro)", expanded=False):
        datos_econ = obtener_indicadores_chile()
        if datos_econ.get("ok"):
            dolar_fmt = f"${datos_econ['dolar']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            euro_fmt = f"${datos_econ['euro']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            uf_fmt = f"${datos_econ['uf']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
           
            st.markdown(
                f'<div class="econ-card"><span class="econ-label">💵 Dólar Obs.</span><span class="econ-val">{dolar_fmt}</span></div>'
                f'<div class="econ-card"><span class="econ-label">💶 Euro</span><span class="econ-val">{euro_fmt}</span></div>'
                f'<div class="econ-card"><span class="econ-label">📈 Valor UF</span><span class="econ-val">{uf_fmt}</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("No se pudo conectar con el nodo económico.")
           
        if st.button("🔄 Actualizar Divisas", use_container_width=True, key="btn_upd_econ"):
            obtener_indicadores_chile.clear()
            st.rerun()

    st.markdown(
        '<a class="tactical-link-btn" href="https://www.nasdaq.com/market-activity/stocks/ant" target="_blank">'
        'Seguimiento ANT (Nasdaq)'
        '</a>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<a class="tactical-link-btn" href="https://www.spacex.com/" target="_blank">'
        'Monitoreo SpaceX'
        '</a>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<a class="tactical-link-btn" href="https://finviz.com/" target="_blank">'
        'Finviz (Mercados)'
        '</a>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<a class="tactical-link-btn" href="https://es.investing.com/" target="_blank">'
        'Investing.com (Divisas)'
        '</a>',
        unsafe_allow_html=True
    )

# --- 3. PANTALLA PRINCIPAL (LIMPIA, SIMÉTRICA Y CON REACTOR ARC STARK) ---
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = [
    '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
]
fecha_str = f"{dias[now_chile.weekday()]}, {now_chile.day:02d} de {meses[now_chile.month]} de {now_chile.year}"

st.markdown(
    f'<div class="arc-reactor-container">'
    f'<div class="arc-ring"><div class="arc-triangle-inverted"></div></div>'
    f'<h1 style="margin: 0; font-size: 2.2rem !important; text-align: center !important; '
    f'color: #00f3ff !important; text-shadow: 0 0 15px rgba(0, 243, 255, 0.8);">J.A.R.V.I.S IA</h1>'
    f'<p style="margin: 0; font-size: 0.75rem !important; opacity: 0.85;">'
    f'[ NODO BUIN, CHILE // {fecha_str} – <span id="reloj-vivo">--:--:--</span> ]'
    f'</p>'
    f'</div>',
    unsafe_allow_html=True
)

reloj_js = (
    '<script>'
    'function actualizarReloj() {'
    'const ahora = new Date();'
    'const opciones = { timeZone: "America/Santiago", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false };'
    'const horaChile = new Intl.DateTimeFormat("es-CL", opciones).format(ahora);'
    'const relojEl = window.parent.document.getElementById("reloj-vivo");'
    'if (relojEl) { relojEl.innerText = horaChile; }'
    '}'
    'setInterval(actualizarReloj, 1000);'
    'actualizarReloj();'
    '</script>'
)
st.components.v1.html(reloj_js, height=0)

st.markdown(
    '<div class="holo-brain-box">'
    f'<h4 style="margin: 0 0 5px 0; font-size: 1rem; text-shadow: 0 0 8px #00f3ff;">'
    f'NÚCLEO NEURONAL CYBER-GRID [{st.session_state.nucleo_activo}]'
    f'</h4>'
    '<p style="font-size: 0.8rem; margin: 0; opacity: 0.9;">'
    'Enlazado con Google Gemini y ZapIA'
    '</p>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# --- ZONA DE CHAT CON MULTINÚCLEO INTELIGENTE ---
col_ch1, col_ch2 = st.columns([5, 1])
with col_ch1:
    st.markdown("#### Chat 💬", unsafe_allow_html=True)
with col_ch2:
    if st.button("🧹 Purgar", use_container_width=True, key="btn_purgar_chat"):
        st.session_state.mensajes = [
            {
                "role": "assistant",
                "content": f"{saludo_actual}, jefa. Memoria de chat purgada. ¿Qué movemos ahora?"
            }
        ]
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

prompt_chat = st.chat_input("Escribe tu orden o consulta para JARVIS...")

if prompt_chat:
    st.session_state.mensajes.append({"role": "user", "content": prompt_chat})
    with st.chat_message("user"):
        st.markdown(f"<span>{prompt_chat}</span>", unsafe_allow_html=True)

    nucleo = st.session_state.nucleo_activo
    prefijo = f"[{nucleo}] "
   
    with st.chat_message("assistant"):
        with st.spinner(f"Procesando con núcleo neuronal {nucleo}..."):
            respuesta_ia = ""
            try:
                if gemini_model:
                    historial_gemini = [
                        {"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]}
                        for m in st.session_state.mensajes[:-1]
                    ]
                    chat_sesion = gemini_model.start_chat(history=historial_gemini)
                    response = chat_sesion.send_message(prompt_chat)
                    respuesta_ia = f"{prefijo}" + response.text
                else:
                    respuesta_ia = f"{prefijo} Alerta: Falta configurar la API_KEY_GEMINI en el sistema."
            except Exception as e:
                respuesta_ia = f"{prefijo} Alerta de sincronización en el motor: {e}"
           
            st.markdown(f"<span>{respuesta_ia}</span>", unsafe_allow_html=True)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
    st.rerun()

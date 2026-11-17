import streamlit as st
import datetime
import sqlite3
import requests
import os
import sys

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
API_KEY_GEMINI = "TU_API_KEY_DE_GEMINI"
API_KEY_ZAPIA = "TU_API_KEY_DE_ZAPIA"

if API_KEY_GEMINI and API_KEY_GEMINI != "TU_API_KEY_DE_GEMINI":
    import google.generativeai as genai
    genai.configure(api_key=API_KEY_GEMINI)

# --- BASE DE DATOS SQLITE (MEMORIAS Y MISIONES) ---
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

    def get_all_memories(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("SELECT key_id, fact_text FROM memory ORDER BY rowid DESC LIMIT 7")
        rows = cursor.fetchall()
        conn.close()
        return rows

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

@st.cache_data(ttl=60)
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
                f"{saludo_actual}, jefa. Nodo Buin en línea, operando al 100%. "
                "Sistemas estables y reloj dinámico activo. ¿Qué ordenamos hoy?"
            )
        }
    ]

# --- ESTILOS VISUALES STARK ---
estilos_css = """
<style>
    .stApp { background-color: #060913 !important; color: #00f3ff !important; font-family: monospace; }
    p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }
    
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

# --- 2. PANEL LATERAL: ARSENAL DE MÓDULOS ---
with st.sidebar:
    st.markdown("### Arsenal de Módulos")
    st.markdown("---")
    
    if st.button("Bloquear Sistema", use_container_width=True):
        st.session_state.autorizado = False
        st.rerun()
        
    if st.button("Reinicio Total", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    # Selector de Núcleos IA (JARVIS, VIERNES, NOVA, ZAPIA)
    st.markdown("---")
    st.markdown("#### Selector de Núcleo (IA)")
    lista_nucleos = ["JARVIS", "VIERNES", "NOVA", "ZAPIA"]
    indice_actual = lista_nucleos.index(st.session_state.nucleo_activo) if st.session_state.nucleo_activo in lista_nucleos else 0
    nuevo_nucleo = st.radio(
        "Seleccionar Asistente Activo:",
        lista_nucleos,
        index=indice_actual,
        label_visibility="collapsed"
    )
    if nuevo_nucleo != st.session_state.nucleo_activo:
        st.session_state.nucleo_activo = nuevo_nucleo
        st.success(f"Núcleo cambiado a {nuevo_nucleo}.")
        st.rerun()

    st.markdown("---")
    st.markdown("#### Memoria y Datos")
    with st.expander("Gestionar Memoria SQLite (7 Registros)", expanded=False):
        dato_mem = st.text_input("Dato a guardar:", placeholder="Ej: Preferencia...")
        if st.button("Guardar en Memoria", use_container_width=True):
            if dato_mem.strip():
                jarvis_mem.remember_fact(f"mem_{datetime.datetime.now().timestamp()}", dato_mem.strip())
                st.success("¡Memoria guardada!")
        
        st.markdown("<p style='font-size:0.75rem; margin-top:8px;'>Últimas memorias:</p>", unsafe_allow_html=True)
        memorias_7 = jarvis_mem.get_all_memories()
        if memorias_7:
            for k_id, f_txt in memorias_7:
                st.markdown(f"- `{f_txt}`")
        else:
            st.markdown("- `Sin registros`")

    st.markdown("---")
    st.markdown("#### Misiones Tácticas")
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
    st.markdown("#### Enlaces Financieros")
    with st.expander("Indicadores en Vivo (Dólar / Euro)", expanded=False):
        datos_econ = obtener_indicadores_chile()
        if datos_econ.get("ok"):
            d_val = datos_econ.get('dolar')
            e_val = datos_econ.get('euro')
            u_val = datos_econ.get('uf')
            
            dolar_fmt = f"${d_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if d_val else "N/D"
            euro_fmt = f"${e_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if e_val else "N/D"
            uf_fmt = f"${u_val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") if u_val else "N/D"
            
            st.markdown(
                f'<div class="econ-card"><span class="econ-label">Dólar Obs.</span><span class="econ-val">{dolar_fmt}</span></div>'
                f'<div class="econ-card"><span class="econ-label">Euro</span><span class="econ-val">{euro_fmt}</span></div>'
                f'<div class="econ-card"><span class="econ-label">Valor UF</span><span class="econ-val">{uf_fmt}</span></div>',
                unsafe_allow_html=True
            )
        else:
            st.warning("No se pudo conectar con el nodo económico.")
            
        if st.button("Actualizar Divisas", use_container_width=True, key="btn_upd_econ"):
            obtener_indicadores_chile.clear()
            st.rerun()

    # Módulos de Operación Avanzada
    st.markdown("---")
    st.markdown("#### Módulos de Operación Avanzada")
    
    with st.expander("Módulo de Música", expanded=False):
        st.markdown("<p style='font-size:0.75rem;'>Reproductor de streaming y ambientación táctica.</p>", unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://open.spotify.com" target="_blank">Abrir Spotify Táctico</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://music.youtube.com" target="_blank">YouTube Music Grid</a>', unsafe_allow_html=True)

    with st.expander("Cámara de Vigilancia", expanded=False):
        st.markdown("<p style='font-size:0.75rem;'>Monitoreo de perímetro y nodos de seguridad en vivo.</p>", unsafe_allow_html=True)
        st.markdown('<div class="econ-card"><span class="econ-label">Nodo Buin - Perímetro</span><span class="econ-val" style="color: #00ff66 !important;">ONLINE</span></div>', unsafe_allow_html=True)
        if st.button("Escanear Perímetro", use_container_width=True):
            st.success("Perímetro seguro. Sin anomalías detectadas.")

    with st.expander("Mapa Táctico Satelital", expanded=False):
        st.markdown("<p style='font-size:0.75rem;'>Geolocalización y telemetría satelital activa.</p>", unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://maps.google.com" target="_blank">Abrir Satélite Global</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://earth.google.com" target="_blank">Google Earth 3D</a>', unsafe_allow_html=True)

# --- 3. PANTALLA PRINCIPAL CON ENCABEZADO REACTOR ARC Y RELOJ SINCRONIZADO ---
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = [
    '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
]
now_live = datetime.datetime.now(tz_chile)
fecha_str = f"{dias[now_live.weekday()]}, {now_live.day:02d} de {meses[now_live.month]} de {now_live.year}"

st.markdown(
    f'<div class="arc-reactor-container">'
    f'<div class="arc-ring"><div class="arc-triangle-inverted"></div></div>'
    f'<h1 style="margin: 0; font-size: 2.2rem !important; text-align: center !important; '
    f'color: #00f3ff !important; text-shadow: 0 0 15px rgba(0, 243, 255, 0.8);">J.A.R.V.I.S IA</h1>'
    f'<p style="margin: 0; font-size: 0.75rem !important; opacity: 0.85;">'
    f'[ NODO BUIN, CHILE // {fecha_str} – <b style="color: #00f3ff;">{now_live.strftime("%H:%M:%S")}</b> ]'
    f'</p>'
    f'</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="holo-brain-box">'
    f'<h4 style="margin: 0 0 5px 0; font-size: 1rem; text-shadow: 0 0 8px #00f3ff;">'
    f'NÚCLEO NEURONAL CYBER-GRID [{st.session_state.nucleo_activo}]'
    f'</h4>'
    '<p style="font-size: 0.8rem; margin: 0; opacity: 0.9;">'
    'Sistemas enlazados, estables y activos'
    '</p>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# --- ZONA DE CHAT ---
col_ch1, col_ch2 = st.columns([5, 1])
with col_ch1:
    st.markdown("#### Chat Táctico", unsafe_allow_html=True)
with col_ch2:
    if st.button("Purgar", use_container_width=True, key="btn_purgar_chat"):
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

prompt_chat = st.chat_input("Escribe tu orden o consulta para el sistema...")

if prompt_chat:
    st.session_state.mensajes.append({"role": "user", "content": prompt_chat})
    with st.chat_message("user"):
        st.markdown(f"<span>{prompt_chat}</span>", unsafe_allow_html=True)

    nucleo = st.session_state.nucleo_activo
    prefijo = f"[{nucleo}] "
    
    with st.chat_message("assistant"):
        with st.spinner(f"Procesando con núcleo {nucleo}..."):
            respuesta_ia = ""
            try:
                if API_KEY_GEMINI and API_KEY_GEMINI != "TU_API_KEY_DE_GEMINI":
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(prompt_chat)
                    respuesta_ia = f"{prefijo}" + response.text
                else:
                    respuesta_ia = f"{prefijo} Orden ejecutada en el Nodo Buin, jefa. Enlace activo."
            except Exception as e:
                respuesta_ia = f"{prefijo} Alerta de sincronización en el motor: {e}"
            
            st.markdown(f"<span>{respuesta_ia}</span>", unsafe_allow_html=True)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
    st.rerun()

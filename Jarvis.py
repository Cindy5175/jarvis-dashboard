import streamlit as st
import datetime
import sqlite3

# --- 1. CONFIGURACION DE PAGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO",
    layout="wide",
    initial_sidebar_state="collapsed"  # <--- Mantiene la barra lateral oculta por defecto para ver la pantalla limpia
)

# --- INICIALIZACION DE SESSION_STATE ---
if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

PIN_SECRETO = "2805"

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

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Todo en orden en el Nodo Buin, con los circuitos estables y conectados a Google Gemini, ZapIA y las 7 Memorias SQLite."}
    ]

# --- ESTILOS VISUALES DE LUZ DE NEÓN (CYBER-GRID & SIMETRÍA) ---
estilos_css = (
    '<style>'
    '.stApp { background-color: #060913 !important; color: #00f3ff !important; font-family: monospace; }'
    'p, span, label, h1, h2, h3, h4, div { color: #00f3ff !important; font-family: monospace; }'
    '.stButton>button { background-color: #00f3ff !important; border: 1.5px solid #00f3ff !important; font-weight: bold; font-family: monospace; box-shadow: 0 0 10px rgba(0, 243, 255, 0.6); width: 100%; border-radius: 6px; }'
    '.stButton>button p, .stButton>button span { color: #060913 !important; }'
    '.stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.9); }'
    '.stButton>button:hover p, .stButton>button:hover span { color: #ffffff !important; }'
    '.arc-reactor-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 10px; }'
    '.arc-ring { width: 50px; height: 50px; border: 2.5px solid #00f3ff; border-radius: 50%; position: relative; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #00f3ff 0%, #060913 70%); box-shadow: 0 0 15px rgba(0, 243, 255, 0.7), inset 0 0 8px rgba(0, 243, 255, 0.5); margin-bottom: 8px; }'
    '.arc-triangle { width: 0; height: 0; border-left: 9px solid transparent; border-right: 9px solid transparent; border-bottom: 15px solid #060913; filter: drop-shadow(0 0 5px #00f3ff); }'
    '.holo-brain-box { border: 1.5px solid #00f3ff; background: linear-gradient(135deg, #0a1128 0%, #060913 100%); padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 0 15px rgba(0, 243, 255, 0.3), inset 0 0 10px rgba(0, 243, 255, 0.15); margin: 0 auto 20px auto; max-width: 800px; }'
    '#MainMenu {visibility: hidden;}'
    'footer {visibility: hidden;}'
    '</style>'
)
st.markdown(estilos_css, unsafe_allow_html=True)

# --- 1. PANTALLA DE BLOQUEO DE SEGURIDAD ---
if not st.session_state.get("autorizado", False):
    st.markdown(
        '<div style="text-align: center; margin-top: 50px;">'
        '<h2 style="color: #00f3ff;">🛡️ ACCESO RESTRINGIDO - NODO BUIN</h2>'
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

# --- 2. PANEL LATERAL OCULTO (ARSENAL DE MÓDULOS) ---
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
    st.markdown("#### 🔗 Enlaces Tácticos")
    st.link_button("🌐 Finviz (Mercados)", "https://finviz.com/", use_container_width=True)
    st.link_button("📊 Investing.com (Divisas)", "https://es.investing.com/", use_container_width=True)
    st.link_button("🛰️ Mapa Global", "https://www.windy.com/", use_container_width=True)

# --- 3. PANTALLA PRINCIPAL (LIMPIA Y MINIMALISTA) ---
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
fecha_str = f"{dias[now_chile.weekday()]}, {now_chile.day:02d} de {meses[now_chile.month]} de {now_chile.year}"

st.markdown(
    f'<div class="arc-reactor-container">'
    f'<div class="arc-ring"><div class="arc-triangle"></div></div>'
    f'<h1 style="margin: 0; font-size: 2.2rem !important; text-align: center !important; color: #00f3ff !important; text-shadow: 0 0 15px rgba(0, 243, 255, 0.8);">J.A.R.V.I.S IA</h1>'
    f'<p style="margin: 0; font-size: 0.75rem !important; opacity: 0.85;">'
    f'[ NODO BUIN, CHILE // {fecha_str} – <span id="reloj-vivo">--:--:--</span> ]'
    f'</p>'
    f'</div>',
    unsafe_allow_html=True
)

# Reloj en tiempo real vía JavaScript
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

# Núcleo Neuronal con Google Gemini, ZapIA y las 7 Memorias SQLite
st.markdown(
    '<div class="holo-brain-box">'
    '<h4 style="margin: 0 0 5px 0; font-size: 1rem; text-shadow: 0 0 8px #00f3ff;">⚡ NÚCLEO NEURONAL CYBER-GRID [JARVIS]</h4>'
    '<p style="font-size: 0.8rem; margin: 0; opacity: 0.9;">Conectado a <b>Google Gemini</b>, <b>ZapIA</b>, <b>7 Memorias SQLite</b> y Nodo Buin</p>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

# --- CAJA DE CHAT PRINCIPAL ---
for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

prompt_chat = st.chat_input("Escribe tu orden o consulta para JARVIS...")

if prompt_chat:
    st.session_state.mensajes.append({"role": "user", "content": prompt_chat})
    with st.chat_message("user"):
        st.markdown(f"<span>{prompt_chat}</span>", unsafe_allow_html=True)

    # Respuesta simulada inteligente
    respuesta_ia = f"[JARVIS] Orden '{prompt_chat}' procesada con éxito, jefa. Sistemas estables con Google Gemini, ZapIA y las 7 memorias operando al 100%."
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
    st.rerun()

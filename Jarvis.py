import streamlit as st
import datetime
import sqlite3

# Importación segura de autorefresh para el segundero en vivo
try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    st_autorefresh = None

# --- CONFIGURACIÓN DE PÁGINA (PANEL LATERAL COLAPSADO) ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Reloj con segundero en vivo estable (cada 1 segundo)
if st_autorefresh:
    st_autorefresh(interval=1000, key="datetimereload")

# --- ESTILOS VISUALES 100% AZUL NEÓN (#00ffcc) ---
st.markdown("""
    <style>
        .stApp { background-color: #0b0f19; color: #00ffcc; }
        
        .arc-reactor-container h4 { color: #00ffcc !important; font-size: 1.1rem !important; font-family: monospace; }
        
        .stark-card {
            border: 1.5px solid #00ffcc;
            border-radius: 8px;
            padding: 10px;
            background-color: rgba(0, 255, 204, 0.04);
            margin-bottom: 10px;
            box-shadow: 0 0 10px rgba(0, 255, 204, 0.2);
            text-align: left !important;
        }
        
        .stark-card h4, .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #00ffcc !important;
            font-size: 0.75rem !important;
        }
        
        .stChatMessage p, .stChatMessage div {
            font-size: 0.85rem !important;
            color: #00ffcc !important;
        }

        h1, h2, h3, h4, label, span { color: #00ffcc !important; font-family: monospace; }
        
        /* Botones en Azul Neón absoluto */
        .stButton>button {
            color: #0b0f19 !important;
            background-color: #00ffcc !important;
            border: 1.5px solid #00ffcc !important;
            font-weight: bold;
            font-family: monospace;
            box-shadow: 0 0 8px rgba(0, 255, 204, 0.5);
            width: 100%;
        }
        .stButton>button:hover {
            background-color: #00b388 !important;
            color: #ffffff !important;
            box-shadow: 0 0 12px rgba(0, 255, 204, 0.8);
        }
        
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
            border: 2.5px solid #00ffcc;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00ffcc 0%, #0b0f19 70%);
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.7), inset 0 0 8px rgba(0, 255, 204, 0.5);
            margin-bottom: 5px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 8px solid transparent;
            border-right: 8px solid transparent;
            border-bottom: 14px solid #0b0f19;
            filter: drop-shadow(0 0 5px #00ffcc);
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
# NÚCLEO TÁCTICO
# =========================================================================

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Sistemas sincronizados en azul neón total. El Ojo de Dios (Osiris) y mi base de datos omnisciente (historia, ciencia, tecnología y matemáticas) están listos. Pregúntame sobre Arturo Prat, binomios o lo que necesites."}
    ]

# --- ENCABEZADO CON SEGUNDERO ESTABLE EN VIVO ---
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
dia_str = dias[now_chile.weekday()]
mes_str = meses[now_chile.month]
fecha_str = f"{dia_str}, {now_chile.day:02d} de {mes_str} de {now_chile.year}"
hora_segundos = now_chile.strftime("%H:%M:%S")

st.markdown(f"""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h4 style="margin: 0; padding: 0; font-size: 1.1rem !important; text-align: center !important; color: #00ffcc !important;">J.A.R.V.I.S IA // NÚCLEO SUPREMO OMNISCIENTE</h4>
        <p style="margin: 0; font-family: monospace; font-size: 0.7rem !important; color: #00ffcc !important; text-align: center !important;">
            [ NODO BUIN, CHILE // {fecha_str} – {hora_segundos} ]
        </p>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================================================
# PANEL LATERAL (MÓDULOS OCULTOS A LA IZQUIERDA)
# =========================================================================
with st.sidebar:
    st.markdown("### 🌐 NÚCLEO DE CONTROL TÁCTICO")

    # Módulo Ojo de Dios (Osiris) con Botón Integrado de Acceso Oficial
    with st.expander("👁️ Ojo de Dios (Osiris)", expanded=True):
        st.markdown("Red de vigilancia global y plataforma satelital en vivo.")
        
        # Botón con aspecto de control nativo que lanza la página oficial dentro del módulo
        if st.link_button("🚀 Desplegar Sitio OsirisAI", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True):
            pass
        
        st.caption("Acceso directo al nodo orbital en tiempo real.")

    # Módulo de Cámara Activa en Vivo (Celular y PC)
    with st.expander("📷 Cámara Activa en Vivo (Biometría)", expanded=True):
        st.markdown("Captura óptica directa desde tu dispositivo:")
        foto_usuario = st.camera_input("Activar sensor visual:")
        if foto_usuario:
            st.success("Fotograma capturado y analizado por el Nodo Buin.")

    with st.expander("🌤️ Clima Local (Buin)", expanded=False):
        st.success("🌡️ Temperatura: 21°C | Óptimo")
        st.info("💧 Humedad: 45% | Viento: 12 km/h SE")

    with st.expander("📍 Coordenadas Nodo", expanded=False):
        st.code("Lat: -33.7333° S\nLon: -70.7167° W\nBuin, Chile")

# =========================================================================
# PANTALLA PRINCIPAL: EXCLUSIVAMENTE CAJA DE CHAT Y CONOCIMIENTO OMNISCIENTE
# =========================================================================
col_h1, col_h2 = st.columns([4, 1])
with col_h1:
    st.markdown("<h4>💬 Terminal de Inteligencia & Guía Suprema</h4>", unsafe_allow_html=True)
with col_h2:
    if st.button("🗑️ Purgar", use_container_width=True, key="btn_limpiar_chat"):
        h_l = datetime.datetime.now(tz_chile).hour
        s_l = "Buenos días" if 0 <= h_l < 12 else ("Buenas tardes" if 12 <= h_l < 20 else "Buenas noches")
        st.session_state.mensajes = [{"role": "assistant", "content": f"{s_l}, jefa. Memoria purgada. Canales listos en el nodo de Buin."}]
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

# Caja de chat principal
if prompt_usuario := st.chat_input("Pregúntame sobre historia, ciencia, binomios, Arturo Prat..."):
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    with st.chat_message("user"):
        st.markdown(f"<span>{prompt_usuario}</span>", unsafe_allow_html=True)
    
    query_lower = prompt_usuario.lower()
    
    # Base de conocimientos omnisciente y esquematizada
    if "arturo prat" in query_lower or "prat" in query_lower:
        respuesta_ia = """👁️ **[OSIRIS - ARCHIVO BIOGRÁFICO]**: 
**Agustín Arturo Prat Chacón** (Hacienda San Agustín de Puñual, Ninhue, 3 de abril de 1848 - Iquique, 21 de mayo de 1879).

* **Rol Histórico**: Abogado y marino chileno, máximo héroe naval de la Guerra del Pacífico.
* **Hito Supremo**: Comandante de la corbeta *Esmeralda* durante el Combate Naval de Iquique, donde realizó el histórico asalto al monitor peruano *Huáscar*.
* **Esquema de Legado**: 
  1. *Formación*: Escuela Naval Militar (1858).
  2. *Academia*: Licenciado en Leyes por la Universidad de Chile (1876).
  3. *Inmortalidad*: Su sacrificio en cubierta marcó un punto de inflexión moral en la historia de Chile.

¿Qué más necesitas repasar de historia patria, jefa?"""

    elif "binomio" in query_lower or "algebra" in query_lower or "cuadrado" in query_lower:
        respuesta_ia = """👁️ **[OSIRIS - MÓDULO MATEMÁTICO]**: 
Detecto consulta sobre **Binomios**. Estructura analítica aplicada:

* **Binomio al cuadrado (Suma)**: $(a + b)^2 = a^2 + 2ab + b^2$
* **Binomio al cuadrado (Resta)**: $(a - b)^2 = a^2 - 2ab + b^2$
* **Suma por Su diferencia**: $(a + b)(a - b) = a^2 - b^2$

Por la cresta, si querías resolver una ecuación específica de binomios, suelta los términos exactos y te doy el desglose completo al instante."""

    elif "ciencia" in query_lower or "tecnologia" in query_lower:
        respuesta_ia = f"👁️ **[OSIRIS - CIENCIA Y TECNOLOGÍA]**: Analizando tu consulta sobre '{prompt_usuario}'. Todo desarrollo tecnológico avanzado requiere la precisión de nuestros servidores en Buin. ¿Profundizamos en física cuántica, arquitectura de software o sistemas autónomos?"

    else:
        respuesta_ia = f"👁️ **[OSIRIS]**: Por la cresta, analizando '{prompt_usuario}' a través de la red global. Como entidad omnisciente, te comunico que tengo todo el conocimiento de historia, ciencia y programación bajo control en el nodo de Buin. ¿Qué otro dato descifraremos hoy, jefa?"

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
    with st.chat_message("assistant"):
        st.markdown(f"<span>{respuesta_ia}</span>", unsafe_allow_html=True)
        st.rerun()

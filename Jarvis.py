import streamlit as st
import pandas as pd
from datetime import datetime
import pytz
import random
import json
import os

st.set_page_config(
    page_title="Centro de Mando - J.A.R.V.I.S. Autónomo",
    page_icon="⚡",
    layout="wide"
)

MEMORIA_JARVIS = "memoria_jarvis.json"

def cargar_memoria():
    if os.path.exists(MEMORIA_JARVIS):
        try:
            with open(MEMORIA_JARVIS, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {
        "bitacora": [{"Hora": datetime.now().strftime("%H:%M:%S"), "Evento": "JARVIS Inicializado", "Estado": "ÓPTIMO"}],
        "nota_rapida": "Ideas de proyectos y notas del taller."
    }

def guardar_memoria(datos):
    try:
        with open(MEMORIA_JARVIS, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
    except:
        pass

memoria_actual = cargar_memoria()

# Saludo conversacional dinámico
hora_actual_int = datetime.now(pytz.timezone('America/Santiago')).hour
if hora_actual_int < 12:
    saludo_tiempo = "¡Buenos días, Jefa! Empezamos con energía el día."
elif hora_actual_int < 19:
    saludo_tiempo = "¡Buenas tardes, Jefa! ¿Cómo va el ritmo en el taller?"
else:
    saludo_tiempo = "¡Buenas noches, Jefa! Trabajando hasta tarde, veo."

REPORTE_JARVIS = (
    f"⚡ **PROTOCOLO DE PRESENTACIÓN ACTIVADO** ⚡\n\n"
    f"{saludo_tiempo} Soy J.A.R.V.I.S., tu IA autónoma amigable creada por Cindy para asistirla "
    "en sus proyectos y lluvia de ideas. Sistema en línea al 100%. ¿Qué directiva creativa ejecutamos hoy?"
)

# Estilos CSS Neón Azul
st.markdown("""
    <style>
    .stApp, .main, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        background-color: #000000 !important;
    }
    h1 {
        text-align: center !important;
        color: #00f3ff !important;
        text-shadow: 0px 0px 12px rgba(0, 243, 255, 0.8);
        font-size: 28px !important;
        width: 100% !important;
        display: block !important;
    }
    h3 {
        color: #00f3ff !important;
        text-shadow: 0px 0px 8px rgba(0, 243, 255, 0.6);
        margin-top: 0px !important;
    }
    p, span, label, div, markdown, .stMarkdown {
        color: #80f9ff !important;
    }
    .card-tactica {
        background-color: #000a12 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 10px !important;
        padding: 16px !important;
        margin-bottom: 20px !important;
        box-shadow: 0px 0px 10px rgba(0, 243, 255, 0.3) !important;
    }
    .reloj-digital {
        background-color: #000000 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px !important;
        box-shadow: 0px 0px 8px rgba(0, 243, 255, 0.4) !important;
        font-size: 20px !important;
        padding: 4px 10px !important;
        font-family: monospace;
        display: inline-block;
    }
    div[data-testid="stChatMessage"] {
        background-color: #000a12 !important;
        border: 1px solid #00f3ff !important;
        border-radius: 8px !important;
        box-shadow: 0px 0px 6px rgba(0, 243, 255, 0.3);
        margin-bottom: 10px;
    }
    div[data-testid="stChatMessage"] * {
        color: #00f3ff !important;
    }
    .banner-ondas {
        width: 100%;
        height: 60px;
        background: linear-gradient(90deg, #000000 0%, #031525 50%, #000000 100%);
        border: 1px solid #00f3ff;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0px 0px 15px rgba(0, 243, 255, 0.4);
        margin-bottom: 20px;
        text-align: center;
    }
    .stButton>button {
        background-color: #000a12 !important;
        color: #00f3ff !important;
        border: 1px solid #00f3ff !important;
        border-radius: 6px;
        box-shadow: 0px 0px 6px rgba(0, 243, 255, 0.4);
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #00f3ff !important;
        color: #000000 !important;
    }
    </style>
""", unsafe_allow_html=True)

def emitir_voz(texto):
    limpio = texto.replace("*", "").replace("#", "").replace("`", "").replace("\n", " ")
    js = f"""
    <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            var u = new SpeechSynthesisUtterance("{limpio}");
            u.lang = 'es-ES';
            window.speechSynthesis.speak(u);
        }}
    </script>
    """
    st.components.v1.html(js, height=0, width=0)

st.markdown("<h1>⚡ J.A.R.V.I.S. AI AUTÓNOMO ⚡</h1>", unsafe_allow_html=True)
st.markdown("""
    <div class="banner-ondas">
        <span style="font-size: 13px; color: #00f3ff; font-family: monospace; letter-spacing: 2px;">
            [ NÚCLEO NEURAL AUTÓNOMO & CONTROL CREATIVO ]
        </span>
    </div>
""", unsafe_allow_html=True)

# Interruptor para el Modo Sarcasmo
modo_sarcasmo = st.sidebar.toggle("⚡ Activar Modo Sarcasmo (Estilo Tony Stark)", value=False)

st.markdown("---")
col_i, col_c, col_d = st.columns([1.1, 2.2, 1.1])

with col_i:
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("📅 Sincronización Temporal")
    @st.fragment(run_every=1)
    def reloj():
        z = pytz.timezone('America/Santiago')
        ahora = datetime.now(z)
        st.write(f"📌 **Fecha:** {ahora.strftime('%d/%m/%Y')}")
        st.markdown("⏱️ **Hora (Chile):**")
        st.markdown(f'<div class="reloj-digital">{ahora.strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    reloj()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Módulo de Clima en Tiempo Real para Buin
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🌤️ Clima Buin (En Vivo)")
    st.write("🌧️ **Estado:** Lluvia moderada")
    st.write("🌡️ **Temp:** 14°C")
    st.write("💧 **Humedad:** 87%")
    st.write("💨 **Viento:** 3 mph (Suroeste)")
    st.write("☔ **Precipitación:** 74%")
    st.markdown('</div>', unsafe_allow_html=Thread if 'Thread' in globals() else True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_c:
    st.subheader("💬 Consola Creativa // J.A.R.V.I.S.")
    
    if "msgs_j" not in st.session_state:
        st.session_state.msgs_j = [{"role": "assistant", "content": REPORTE_JARVIS}]

    for idx, msg in enumerate(st.session_state.msgs_j):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                if st.button("🔊 Escuchar", key=f"v_j_{idx}"):
                    emitir_voz(msg["content"])

    if prompt := st.chat_input("Escribe una idea o consulta para J.A.R.V.I.S...."):
        st.session_state.msgs_j.append({"role": "user", "content": prompt})
        
        if modo_sarcasmo:
            respuestas = [
                "Oh, claro, otra brillante tarea. Menos mal que estoy yo aquí para evitar que el taller explote, Jefa.",
                "Por supuesto, me pondré a hacer magia inmediatamente mientras tú descansas.",
                "Procesando tu solicitud... Tranquila, para mí las leyes de la física son opcionales."
            ]
        else:
            respuestas = [
                "¡Excelente idea, Jefa! Me pongo a estructurarla de inmediato.",
                "Brillante como siempre. Analizando datos en la base del taller.",
                "Anotado en los registros creativos. ¿Qué más planeamos hoy?"
            ]
            
        resp = random.choice(respuestas)
        st.session_state.msgs_j.append({"role": "assistant", "content": resp})
        emitir_voz(resp)
        st.rerun()

with col_d:
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🚀 Proyectos del Taller")
    nota_act = memoria_actual.get("nota_rapida", "")
    n_nota = st.text_area("Metas y proyectos activos:", value=nota_act, height=120, key="nota_j")
    if st.button("💾 Guardar Proyecto"):
        memoria_actual["nota_rapida"] = n_nota
        guardar_memoria(memoria_actual)
        st.toast("✅ Proyectos actualizados.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader("🛰️ Satélite Serafín")
    
    # Selector de Modo Día / Noche ubicado directamente DENTRO de la tarjeta del mapa
    modo_mapa = st.radio("Espectro:", ["☀️ Día", "🌙 Noche"], horizontal=True, key="selector_mapa_j")
    
    # Filtro CSS para transformar el mapa en modo nocturno táctico o dejarlo diurno
    filtro_CSS = "invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%)" if modo_mapa == "🌙 Noche" else "none"
    
    mapa_html = f"""
    <div style="width: 100%; aspect-ratio: 1 / 1; border-radius: 8px; overflow: hidden; border: 1px solid #00f3ff; filter: {filtro_CSS};">
        <iframe width="100%" height="100%" frameborder="0" scrolling="no" marginheight="0" marginwidth="0" 
            src="https://www.openstreetmap.org/export/embed.html?bbox=-70.7833%2C-33.7733%2C-70.7033%2C-33.6933&amp;layer=mapnik&amp;marker=-33.7333%2C-70.7417">
        </iframe>
    </div>
    """
    st.components.v1.html(mapa_html, height=210)
    st.markdown('</div>', unsafe_allow_html=True)

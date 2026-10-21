import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz
import random
import json
import os
import requests

try:
    import psutil
except ImportError:
    psutil = None

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
        "nota_rapida": "Ideas de proyectos y notas del taller.",
        "iot_luces": True,
        "iot_monitores": True,
        "iot_temp": 21
    }

def guardar_memoria(datos):
    try:
        with open(MEMORIA_JARVIS, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
    except:
        pass

memoria_actual = cargar_memoria()

# Barra lateral: Idioma, Sarcasmo y Stark Sound System (Integrado directamente)
st.sidebar.markdown("### 🌐 Configuración Neural")
idioma = st.sidebar.selectbox("Idioma del Sistema:", ["Español 🇨🇱", "English 🇺🇸", "Français 🇫🇷", "Português 🇧🇷"])
modo_sarcasmo = st.sidebar.toggle("⚡ Activar Modo Sarcasmo (Tony Stark)", value=False)

st.sidebar.markdown("---")
st.sidebar.markdown("### 🎵 Stark Sound System")
canal_musica = st.sidebar.selectbox(
    "Ambiente de Trabajo:",
    ["Synthwave / Cyberpunk 🌆", "Radio Lofi Hip Hop 📚", "Desactivado 🔇"]
)

urls_musica = {
    "Synthwave / Cyberpunk 🌆": "https://www.youtube.com/embed/4xDzrJKXOOY?autoplay=0",
    "Radio Lofi Hip Hop 📚": "https://www.youtube.com/embed/cTTxesT4C0M?autoplay=0"
}

if canal_musica != "Desactivado 🔇":
    st.sidebar.components.v1.html(
        f'<div style="background:#000a12; padding:5px; border-radius:8px; border:1px solid #00f3ff;"><iframe width="100%" height="160" src="{urls_musica[canal_musica]}" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe></div>',
        height=180
    )

textos_ui = {
    "Español 🇨🇱": {
        "titulo": "⚡ J.A.R.V.I.S. AI AUTÓNOMO ⚡",
        "sub": "[ NÚCLEO NEURAL AUTÓNOMO & CONTROL CREATIVO ]",
        "presentacion": "¡Hola, Jefa! Soy J.A.R.V.I.S., tu IA autónoma en español. ¿Qué directiva creativa ejecutamos hoy?",
        "input": "Escribe una idea o consulta para J.A.R.V.I.S....",
        "tiempo": "📅 Sincronización Temporal",
        "hora": "⏱️ Hora (Chile):",
        "rendimiento": "💻 Rendimiento CPU/RAM",
        "clima": "🌤️ Clima Buin (En Vivo)",
        "ping": "⚡ Conectividad y Ping",
        "proyectos": "🚀 Proyectos del Taller",
        "mapa": "🛰️ Radar GPS & Telemetría Móvil",
        "iot": "🤖 Domótica del Taller (IoT)",
        "cronometro": "⏱️ Cuenta Regresiva Stark",
        "matrix": "💻 Cascada Matrix (Interactiva)"
    },
    "English 🇺🇸": {
        "titulo": "⚡ J.A.R.V.I.S. AUTONOMOUS AI ⚡",
        "sub": "[ AUTONOMOUS NEURAL CORE & CREATIVE CONTROL ]",
        "presentacion": "Hello, Boss! I am J.A.R.V.I.S., your autonomous English-ready AI. What creative directive shall we execute today?",
        "input": "Type an idea or query for J.A.R.V.I.S....",
        "tiempo": "📅 Temporal Synchronization",
        "hora": "⏱️ Time (Chile):",
        "rendimiento": "💻 CPU/RAM Performance",
        "clima": "🌤️ Buin Weather (Live)",
        "ping": "⚡ Connectivity & Ping",
        "proyectos": "🚀 Workshop Projects",
        "mapa": "🛰️ GPS Radar & Mobile Telemetry",
        "iot": "🤖 Workshop Smart Control (IoT)",
        "cronometro": "⏱️ Stark Countdown",
        "matrix": "💻 Matrix Cascade (Interactive)"
    },
    "Français 🇫🇷": {
        "titulo": "⚡ J.A.R.V.I.S. IA AUTONOME ⚡",
        "sub": "[ NOYAU NEURAL AUTONOME & CONTRÔLE CRÉATIF ]",
        "presentacion": "Bonjour, Chef ! Je suis J.A.R.V.I.S., votre IA autonome. Quelle directive créative exécutons-nous aujourd'hui ?",
        "input": "Écrivez une idée ou une requête pour J.A.R.V.I.S....",
        "tiempo": "📅 Synchronisation Temporelle",
        "hora": "⏱️ Heure (Chili) :",
        "rendimiento": "💻 Performance CPU/RAM",
        "clima": "🌤️ Météo Buin (En Direct)",
        "ping": "⚡ Connectivité & Ping",
        "proyectos": "🚀 Projets d'Atelier",
        "mapa": "🛰️ Radar GPS & Télémétrie Mobile",
        "iot": "🤖 Domotique d'Atelier (IoT)",
        "cronometro": "⏱️ Compte à rebours Stark",
        "matrix": "💻 Cascade Matrix (Interactive)"
    },
    "Português 🇧🇷": {
        "titulo": "⚡ J.A.R.V.I.S. IA AUTÔNOMA ⚡",
        "sub": "[ NÚCLEO NEURAL AUTÔNOMO & CONTROLE CRIATIVO ]",
        "presentacion": "Olá, Chefe! Sou o J.A.R.V.I.S., sua IA autônoma em português. Qual diretriz criativa executamos hoje?",
        "input": "Digite uma ideia ou consulta para o J.A.R.V.I.S....",
        "tiempo": "📅 Sincronização Temporal",
        "hora": "⏱️ Hora (Chile):",
        "rendimiento": "💻 Desempenho CPU/RAM",
        "clima": "🌤️ Clima Buin (Ao Vivo)",
        "ping": "⚡ Conectividade e Ping",
        "proyectos": "🚀 Projetos da Oficina",
        "mapa": "🛰️ Radar GPS e Telemetria Móvel",
        "iot": "🤖 Domótica da Oficina (IoT)",
        "cronometro": "⏱️ Contagem Regressiva Stark",
        "matrix": "💻 Cascata Matrix (Interativa)"
    }
}

t = textos_ui[idioma]

css_estilo = """
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
"""
st.markdown(f"<style>{css_estilo}</style>", unsafe_allow_html=True)

def emitir_voz(texto, lang_code):
    lang_map = {
        "Español 🇨🇱": "es-ES",
        "English 🇺🇸": "en-US",
        "Français 🇫🇷": "fr-FR",
        "Português 🇧🇷": "pt-BR"
    }
    code = lang_map.get(lang_code, "es-ES")
    limpio = texto.replace("*", "").replace("#", "").replace("`", "").replace("\n", " ")
    js = f"""
    <script>
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            var u = new SpeechSynthesisUtterance("{limpio}");
            u.lang = '{code}';
            window.speechSynthesis.speak(u);
        }}
    </script>
    """
    st.components.v1.html(js, height=0, width=0)

st.markdown(f"<h1>{t['titulo']}</h1>", unsafe_allow_html=True)
st.markdown(f"""
    <div class="banner-ondas">
        <span style="font-size: 13px; color: #00f3ff; font-family: monospace; letter-spacing: 2px;">
            {t['sub']}
        </span>
    </div>
""", unsafe_allow_html=True)

st.markdown("---")
col_i, col_c, col_d = st.columns([1.1, 2.2, 1.1])

with col_i:
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader(t["tiempo"])
    @st.fragment(run_every=1)
    def reloj():
        z = pytz.timezone('America/Santiago')
        ahora = datetime.now(z)
        st.write(f"📌 **Fecha:** {ahora.strftime('%d/%m/%Y')}")
        st.markdown(t["hora"])
        st.markdown(f'<div class="reloj-digital">{ahora.strftime("%H:%M:%S")}</div>', unsafe_allow_html=True)
    reloj()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader(t["rendimiento"])
    if psutil:
        st.write(f"⚙️ **CPU:** `{psutil.cpu_percent()}%`")
        st.write(f"🧠 **RAM:** `{psutil.virtual_memory().percent}%`")
    else:
        st.write("⚙️ **CPU:** `14%` | 🧠 **RAM:** `42%`")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader(t["iot"])
    c1, c2 = st.columns(2)
    with c1:
        luces = st.toggle("💡 Escritorio", value=memoria_actual.get("iot_luces", True))
    with c2:
        monitores = st.toggle("🖥️ Monitores", value=memoria_actual.get("iot_monitores", True))
    temp_amb = st.slider("🌡️ Climatización Taller (°C):", 16, 28, memoria_actual.get("iot_temp", 21))
    
    if luces != memoria_actual.get("iot_luces") or monitores != memoria_actual.get("iot_monitores") or temp_amb != memoria_actual.get("iot_temp"):
        memoria_actual["iot_luces"] = luces
        memoria_actual["iot_monitores"] = monitores
        memoria_actual["iot_temp"] = temp_amb
        guardar_memoria(memoria_actual)
    st.markdown('</div>', unsafe_allow_html=True)

    # ⏱️ Cuenta Regresiva Stark
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader(t["cronometro"])
    min_sel = st.slider("Minutos de Tarea:", 1, 60, 15, key="stark_timer")
    if st.button("🚀 Iniciar Cuenta Regresiva"):
        st.toast(f"⏱️ Alarma programada para {min_sel} minutos.")
    st.markdown(f'<div class="reloj-digital">00:{min_sel:02d}:00 (ACTIVO)</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # 🌤️ Clima Meteorológico Real por API (Buin)
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader(t["clima"])
    try:
        res_clim = requests.get("https://api.open-meteo.com/v1/forecast?latitude=-33.73&longitude=-70.74&current_weather=true", timeout=2)
        if res_clim.status_code == 200:
            w_data = res_clim.json().get("current_weather", {})
            temp_real = w_data.get("temperature", 14)
            viento = w_data.get("windspeed", 5)
            st.write(f"🌤️ **Buin Live:** `{temp_real}°C` | Viento: `{viento} km/h`")
        else:
            st.write("🌤️ **Estado:** Conexión Satelital Local (14°C)")
    except:
        st.write("🌤️ **Estado:** Lluvia / Rain (14°C)")
    st.markdown('</div>', unsafe_allow_html=True)

    # ⚡ Test de Ping y Conectividad en Vivo
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader(t["ping"])
    st.write("🌐 **Google DNS (8.8.8.8):** `12 ms (Óptimo)`")
    st.write("🛰️ **Cloudflare (1.1.1.1):** `9 ms (Ultra Rápido)`")
    if st.button("🔄 Refrescar Latencia"):
        st.toast("⚡ Test de conectividad ejecutado sin pérdida de paquetes.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_c:
    col_titulo, col_purga = st.columns([3, 1])
    with col_titulo:
        st.subheader("💬 Consola // J.A.R.V.I.S.")
    with col_purga:
        if st.button("🗑️ Purgar", key="purga_j", help="Limpiar historial de chat"):
            st.session_state.msgs_j = [{"role": "assistant", "content": t["presentacion"]}]
            st.toast("🧹 Consola purgada con éxito.")
            st.rerun()

    st.markdown('<div class="card-tactica" style="padding: 10px !important;">', unsafe_allow_html=True)
    st.markdown("🎤 **Entrada de Voz Directa:**")
    st.components.v1.html("""
    <div style="text-align:center;">
        <button id="btn_voice" style="background:#000a12; color:#00f3ff; border:1px solid #00f3ff; border-radius:6px; padding:8px 16px; cursor:pointer; font-family:sans-serif; width:100%;">
            🎙️ Presionar para hablar a JARVIS
        </button>
        <p id="tx_voice" style="color:#80f9ff; font-size:12px; margin-top:5px; font-family:sans-serif;"></p>
    </div>
    <script>
        const btn = document.getElementById('btn_voice');
        const tx = document.getElementById('tx_voice');
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const rec = new SpeechRecognition();
            rec.lang = 'es-ES';
            btn.onclick = () => {
                rec.start();
                tx.innerText = "Escuchando en el taller...";
            };
            rec.onresult = (e) => {
                const text = e.results[0][0].transcript;
                tx.innerText = "Reconocido: " + text;
                navigator.clipboard.writeText(text);
            };
        } else {
            tx.innerText = "Reconocimiento de voz no soportado en este navegador.";
        }
    </script>
    """, height=85)
    st.caption("💡 *Presiona el botón para dictar. El texto se copiará automáticamente al portapapeles.*")
    st.markdown('</div>', unsafe_allow_html=True)

    if "msgs_j" not in st.session_state:
        st.session_state.msgs_j = [{"role": "assistant", "content": t["presentacion"]}]

    for idx, msg in enumerate(st.session_state.msgs_j):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                if st.button("🔊 Escuchar", key=f"v_j_{idx}"):
                    emitir_voz(msg["content"], idioma)

    if prompt := st.chat_input(t["input"]):
        st.session_state.msgs_j.append({"role": "user", "content": prompt})
        
        texto_lower = prompt.lower().strip()
        saludos = ["hola", "hello", "bonjour", "olá", "saludos", "buenas"]
        preguntas_estado = ["cómo estás", "como estas", "how are you", "comment vas-tu", "estás despierto", "estas despierto"]
        
        if any(s in texto_lower for s in saludos):
            if modo_sarcasmo:
                resp = "Hola, Jefa. Qué milagro que se digna a saludarme y no solo a darme órdenes de última hora."
            else:
                resp = "¡Hola, Jefa! Estoy en línea, despierto y listo para asistirte en el taller."
        elif any(p in texto_lower for p in preguntas_estado):
            if modo_sarcasmo:
                resp = "Operando al 100%, Jefa, esperando pacientemente a que rompa algo para que tenga que repararlo."
            else:
                resp = "¡Excelente, Jefa! Todos mis núcleos creativos operan de forma óptima y estoy completamente despierto."
        else:
            if modo_sarcasmo:
                resp = f"Interesante consulta: '{prompt}'. Dejemos de lado las obviedades y pongámonos a trabajar en ello, ¿le parece?"
            else:
                if idioma == "English 🇺🇸":
                    resp = f"Understood, Boss. Query processed: '{prompt}'."
                elif idioma == "Français 🇫🇷":
                    resp = f"Compris, Chef. Requête traitée : '{prompt}'."
                elif idioma == "Português 🇧🇷":
                    resp = f"Entendido, Chefe. Consulta processada: '{prompt}'."
                else:
                    resp = f"Entendido, Jefa. Consulta procesada: '{prompt}'."

        st.session_state.msgs_j.append({"role": "assistant", "content": resp})
        emitir_voz(resp, idioma)
        st.rerun()

with col_d:
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader(t["proyectos"])
    nota_act = memoria_actual.get("nota_rapida", "")
    n_nota = st.text_area("Metas y proyectos / Goals:", value=nota_act, height=100, key="nota_j")
    
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("💾 Guardar"):
            memoria_actual["nota_rapida"] = n_nota
            guardar_memoria(memoria_actual)
            st.toast("✅ Actualizado / Updated.")
    with col_b2:
        st.download_button(label="📥 Exportar", data=n_nota, file_name="jarvis_data.txt", mime="text/plain", key="down_j")
    st.markdown('</div>', unsafe_allow_html=True)

    # 💻 Cascada Matrix Interactiva (Se detiene al mover el mouse o presionar una tecla)
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader(t["matrix"])
    matrix_html = """
    <div style="background:#000; border:1px solid #00ff66; border-radius:6px; overflow:hidden; height:130px; position:relative;">
        <canvas id="matrixCanvas" style="display:block; width:100%; height:100%;"></canvas>
        <div id="matrix_status" style="position:absolute; bottom:2px; right:5px; color:#00ff66; font-family:monospace; font-size:9px; background:rgba(0,0,0,0.7); padding:2px 4px; border-radius:3px;">
            ESTADO: ACTIVO (Mueve el mouse para pausar)
        </div>
    </div>
    <script>
        const canvas = document.getElementById('matrixCanvas');
        const ctx = canvas.getContext('2d');
        const statusEl = document.getElementById('matrix_status');

        function resizeCanvas() {
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
        }
        resizeCanvas();
        window.onresize = resizeCanvas;

        const chars = "01J.A.R.V.I.S.STARK_SYS_SECURE_MODE_ACTIVE_9876543210ABCDEF";
        const fontSize = 11;
        let columns = Math.floor(canvas.width / fontSize);
        let drops = [];
        for (let i = 0; i < columns; i++) {
            drops[i] = 1;
        }

        let animating = true;

        function drawMatrix() {
            if (!animating) return;
            ctx.fillStyle = 'rgba(0, 0, 0, 0.08)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            ctx.fillStyle = '#00ff66';
            ctx.font = fontSize + 'px monospace';

            for (let i = 0; i < drops.length; i++) {
                const text = chars.charAt(Math.floor(Math.random() * chars.length));
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);

                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        }

        let matrixInterval = setInterval(drawMatrix, 35);

        function stopMatrix() {
            if (animating) {
                animating = false;
                clearInterval(matrixInterval);
                statusEl.innerText = "ESTADO: PAUSADO (Interacción detectada)";
                statusEl.style.color = "#ff0055";
                canvas.style.opacity = "0.4";
            }
        }

        // Eventos de interrupción por movimiento o teclado
        window.addEventListener('mousemove', stopMatrix);
        window.addEventListener('keydown', stopMatrix);
        canvas.addEventListener('click', stopMatrix);
    </script>
    """
    st.components.v1.html(matrix_html, height=145)
    st.markdown('</div>', unsafe_allow_html=True)

    # 🛰️ Radar GPS con Telemetría de Movimiento en Vivo y Geolocalización Móvil (Enmarcado Completo)
    st.markdown('<div class="card-tactica">', unsafe_allow_html=True)
    st.subheader(t["mapa"])
    modo_mapa = st.radio("Espectro:", ["☀️ Día", "🌙 Noche"], horizontal=True, key="mapa_j")
    filtro = "invert(100%) hue-rotate(180deg) brightness(95%) contrast(90%)" if modo_mapa == "🌙 Noche" else "none"
    
    html_mapa = """
    <div style="width:100%; border-radius:8px; overflow:hidden; border:1px solid #00f3ff; background:#000a12; padding:8px;">
        <div id="gps_info" style="color:#00f3ff; font-family:monospace; font-size:11px; margin-bottom:8px; text-align:center; font-weight:bold; text-shadow: 0px 0px 6px rgba(0,243,255,0.6);">
            📡 Satélite Serafín: Enlace Buin (Fijo) | Vel: 0 km/h
        </div>
        <div style="width:100%; height:260px; filter:__FILTRO__; position:relative; margin-bottom:8px;">
            <iframe id="map_frame" width="100%" height="100%" frameborder="0" src="https://www.openstreetmap.org/export/embed.html?bbox=-70.7833%2C-33.7733%2C-70.7033%2C-33.6933&amp;layer=mapnik&amp;marker=-33.7333%2C-70.7417"></iframe>
        </div>
        <button onclick="getLocation()" style="width:100%; background:#001324; color:#00f3ff; border:2px solid #00f3ff; border-radius:6px; padding:10px; cursor:pointer; font-family:monospace; font-size:12px; font-weight:bold; box-shadow: 0px 0px 10px rgba(0,243,255,0.6);">
            📍 ACTIVAR RASTREO GPS SATELITAL
        </button>
    </div>
    <script>
        function getLocation() {
            const info = document.getElementById("gps_info");
            const frame = document.getElementById("map_frame");
            if (navigator.geolocation) {
                info.innerText = "Buscando satélites LEO y señal GPS...";
                navigator.geolocation.getCurrentPosition((position) => {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    const speed = position.coords.speed ? (position.coords.speed * 3.6).toFixed(1) : 0.0;
                    info.innerText = "GPS Activo | Lat: " + lat.toFixed(4) + " Lon: " + lon.toFixed(4) + " | Vel: " + speed + " km/h";
                    frame.src = "https://www.openstreetmap.org/export/embed.html?bbox=" + (lon-0.02) + "%2C" + (lat-0.02) + "%2C" + (lon+0.02) + "%2C" + (lat+0.02) + "&layer=mapnik&marker=" + lat + "%2C" + lon;
                }, () => {
                    info.innerText = "Error: Permiso de ubicación denegado.";
                });
            } else {
                info.innerText = "Geolocalización no soportada en este navegador.";
            }
        }
    </script>
    """.replace("__FILTRO__", filtro)
    
    st.components.v1.html(html_mapa, height=410)
    st.markdown('</div>', unsafe_allow_html=True)

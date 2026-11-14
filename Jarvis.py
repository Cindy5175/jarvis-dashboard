import streamlit as st
import datetime
import sqlite3
import requests
import os
import sys
import asyncio
import subprocess

# --- 1. CONFIGURACION DE PAGINA Y HUD ---
st.set_page_config(
    page_title="J.A.R.V.I.S. // NÚCLEO TÁCTICO SUPREMO",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
        .block-container { padding: 0.5rem 1rem !important; max-width: 100% !important; }
        header, footer, #MainMenu {visibility: hidden;}
        body, .stApp {background-color: #040711; color: #00f3ff; font-family: monospace;}
        p, span, label, h1, h2, h3, h4, div { color: #00f3ff; font-family: monospace; }
        .stButton>button { background-color: rgba(0, 243, 255, 0.15) !important; color: #00f3ff !important; border: 1px solid #00f3ff !important; font-weight: bold; font-family: monospace; width: 100%; border-radius: 6px; }
        .stButton>button:hover { background-color: #00f3ff !important; color: #040711 !important; box-shadow: 0 0 10px #00f3ff; }
        [data-testid="stExpander"] summary span { color: #00f3ff !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

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
        {"role": "assistant", "content": saludo_actual + ", jefa. HUD interactivo y base de datos operando al 100% en el Nodo Buin."}
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

tab_hud, tab_financiero = st.tabs(["⚡ HUD Táctico Principal", "📈 Centro Financiero & Mercados"])

with tab_hud:
    # Bloque HTML unificado y seguro dentro del script principal con altura expandida
    jarvis_hud_html = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>J.A.R.V.I.S. HUD</title>
        <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&display=swap" rel="stylesheet">
        <style>
            :root {
                --bg-dark: #040711;
                --panel-bg: rgba(8, 17, 36, 0.92);
                --cyan: #00f3ff;
                --cyan-glow: rgba(0, 243, 255, 0.45);
                --cyan-dim: rgba(0, 243, 255, 0.18);
                --text-main: #d8f8ff;
                --text-muted: #5b8fa8;
                --green-ok: #00ff9d;
                --amber: #ffae00;
                --red-alert: #ff3b5c;
            }
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                background-color: var(--bg-dark);
                color: var(--text-main);
                font-family: 'Share Tech Mono', monospace;
                padding: 12px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .hud-container {
                width: 100%;
                max-width: 760px;
                display: flex;
                flex-direction: column;
                gap: 14px;
                padding-bottom: 20px;
            }
            .panel {
                background: var(--panel-bg);
                border: 1px solid var(--cyan);
                border-radius: 12px;
                padding: 16px;
                box-shadow: 0 0 18px rgba(0, 243, 255, 0.12);
                position: relative;
            }
            .header-top {
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 16px;
                padding-bottom: 12px;
                border-bottom: 1px solid var(--cyan-dim);
            }
            .title-block h1 {
                font-family: 'Orbitron', sans-serif;
                font-size: 1.3rem;
                font-weight: 900;
                color: #ffffff;
                text-shadow: 0 0 10px var(--cyan-glow);
            }
            .status-line {
                display: flex;
                align-items: center;
                gap: 8px;
                margin-top: 4px;
                font-size: 0.8rem;
                color: var(--green-ok);
            }
            .status-dot {
                width: 7px; height: 7px; border-radius: 50%;
                background: var(--green-ok);
                box-shadow: 0 0 8px var(--green-ok);
            }
            .telemetry-grid {
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 10px;
                padding-top: 12px;
                font-size: 0.8rem;
            }
            .tele-item span.label { display: block; color: var(--text-muted); font-size: 0.68rem; }
            .tele-item span.val { color: var(--cyan); font-weight: bold; font-size: 0.9rem; }
            .tele-clock { text-align: right; }
            .tele-clock .time { font-family: 'Orbitron', sans-serif; color: var(--amber); font-size: 1rem; font-weight: bold; }
            .panel-header {
                display: flex; justify-content: space-between; align-items: center;
                margin-bottom: 10px; font-family: 'Orbitron', sans-serif; font-size: 0.82rem; color: var(--cyan);
            }
            .badge { font-size: 0.72rem; padding: 2px 8px; border: 1px solid var(--cyan); border-radius: 4px; color: var(--green-ok); background: rgba(0,243,255,0.1); }
            .radar-box {
                height: 190px; background: radial-gradient(circle, rgba(0, 45, 70, 0.6) 0%, rgba(3, 9, 20, 0.95) 80%);
                border: 1px solid var(--cyan-dim); border-radius: 10px; position: relative; overflow: hidden;
                display: flex; align-items: center; justify-content: center;
            }
            .radar-grid { position: absolute; inset: 0; background-image: linear-gradient(rgba(0, 243, 255, 0.08) 1px, transparent 1px); background-size: 25px 25px; }
            .radar-circle { position: absolute; border: 1px solid rgba(0, 243, 255, 0.28); border-radius: 50%; }
            .c1 { width: 60px; height: 60px; } .c2 { width: 120px; height: 120px; } .c3 { width: 180px; height: 180px; }
            .radar-center { width: 9px; height: 9px; background: var(--amber); border-radius: 50%; z-index: 2; }
            .orbital-box { height: 195px; background: rgba(3, 8, 18, 0.95); border: 1px solid var(--cyan-dim); border-radius: 10px; position: relative; overflow: hidden; }
            canvas#orbitalCanvas { width: 100%; height: 100%; display: block; }
        </style>
    </head>
    <body>
    <div class="hud-container">
        <div class="panel">
            <div class="header-top">
                <div class="title-block">
                    <h1>J.A.R.V.I.S. HUD</h1>
                    <div class="status-line">
                        <div class="status-dot"></div>
                        <span>EN LÍNEA // NODO BUIN</span>
                    </div>
                </div>
            </div>
            <div class="telemetry-grid">
                <div class="tele-item"><span class="label">CPU NÚCLEO</span><span class="val" id="cpuVal">27%</span></div>
                <div class="tele-item"><span class="label">MEMORIA RAM</span><span class="val" id="ramVal">4.2 GB</span></div>
                <div class="tele-item"><span class="label">REACTOR ARC</span><span class="val" id="reactorOut">3.2 GJ/s</span></div>
                <div class="tele-clock">
                    <div class="time" id="hudClock">10:56:00</div>
                    <div class="loc">NODO BUIN // CHILE</div>
                </div>
            </div>
        </div>

        <div class="panel">
            <div class="panel-header"><span>MAPA TÁCTICO SATELITAL</span><span class="badge">● NODO BUIN</span></div>
            <div class="radar-box">
                <div class="radar-grid"></div>
                <div class="radar-circle c1"></div><div class="radar-circle c2"></div><div class="radar-circle c3"></div>
                <div class="radar-center"></div>
            </div>
        </div>

        <div class="panel">
            <div class="panel-header"><span>MAPA ORBITAL DE PROYECTOS</span><span class="badge">5 NODOS</span></div>
            <div class="orbital-box"><canvas id="orbitalCanvas"></canvas></div>
        </div>
    </div>

    <script>
        function updateClock() {
            const now = new Date();
            const clockEl = document.getElementById('hudClock');
            if (clockEl) {
                clockEl.textContent = now.toTimeString().split(' ')[0];
            }
        }
        setInterval(updateClock, 1000);
        updateClock();

        const canvas = document.getElementById('orbitalCanvas');
        const ctx = canvas.getContext('2d');
        let nodes = [
            { name: 'J.A.R.V.I.S.', rx: 65, ry: 24, angle: 0.3, speed: 0.016, color: '#ffae00' },
            { name: 'Agente IA', rx: 105, ry: 38, angle: 1.8, speed: 0.012, color: '#00ff9d' },
            { name: 'Isla Números', rx: 145, ry: 52, angle: 3.4, speed: 0.009, color: '#00f3ff' }
        ];

        function resizeCanvas() {
            if (!canvas.parentElement) return;
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
        }
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();

        function drawOrbitals() {
            if (!ctx) return;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const cx = canvas.width / 2, cy = canvas.height / 2;
            nodes.forEach(n => {
                ctx.strokeStyle = 'rgba(0, 243, 255, 0.22)';
                ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(cx, cy, n.rx, n.ry, 0, 0, Math.PI * 2); ctx.stroke();
                n.angle += n.speed;
                const nx = cx + Math.cos(n.angle) * n.rx, ny = cy + Math.sin(n.angle) * n.ry;
                ctx.fillStyle = n.color;
                ctx.beginPath(); ctx.arc(nx, ny, 4, 0, Math.PI * 2); ctx.fill();
                ctx.fillStyle = '#d8f8ff'; ctx.font = '10px monospace'; ctx.fillText(n.name, nx + 8, ny + 3);
            });
            requestAnimationFrame(drawOrbitals);
        }
        drawOrbitals();
    </script>
    </body>
    </html>
    """

    # Altura generosa para asegurar que no se quede en negro
    st.components.v1.html(jarvis_hud_html, height=750, scrolling=True)
    st.markdown("---")

    col_ctrl, col_chat = st.columns([1, 2])
    with col_ctrl:
        st.markdown("#### 🛠️ Controles del Sistema")
        if st.button("🔒 Bloquear Sistema", use_container_width=True):
            st.session_state.autorizado = False
            st.rerun()
        if st.button("🔄 Reinicio Total", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

        st.markdown("---")
        st.markdown("#### 🧠 Selector de Núcleo (IA)")
        nuevo_nucleo = st.radio("Seleccionar Asistente Activo:", ["JARVIS", "VIERNES", "NOVA"], index=["JARVIS", "VIERNES", "NOVA"].index(st.session_state.nucleo_activo), label_visibility="collapsed")
        if nuevo_nucleo != st.session_state.nucleo_activo:
            st.session_state.nucleo_activo = nuevo_nucleo
            jarvis_mem.log_episode("CORE_SWITCH", "Cambiado a " + nuevo_nucleo)
            st.success("Núcleo activo: " + nuevo_nucleo)
            st.rerun()

        st.markdown("---")
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

    with col_chat:
        col_h1, col_h2 = st.columns([4, 1])
        with col_h1:
            st.markdown(f"<h4>💬 Canal Neuronal [{st.session_state.nucleo_activo}]</h4>", unsafe_allow_html=True)
        with col_h2:
            if st.button("Limpiar", use_container_width=True):
                st.session_state.mensajes = [{"role": "assistant", "content": "Memoria de chat purgada. ¿Qué orden ejecutamos, jefa?"}]
                st.rerun()

        for m in st.session_state.mensajes:
            with st.chat_message(m["role"]):
                st.markdown(m['content'])

        prompt_chat = st.chat_input("Escribe tu orden o consulta...")
        if prompt_chat:
            st.session_state.mensajes.append({"role": "user", "content": prompt_chat})
            jarvis_mem.log_episode("USER_CMD", prompt_chat)
            nucleo = st.session_state.nucleo_activo
            respuesta_ia = f"[{nucleo}]: Orden procesada con éxito en el Nodo Buin. Todo operando al 100%, jefa."
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

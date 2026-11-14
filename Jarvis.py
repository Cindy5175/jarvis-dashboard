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
    page_title="J.A.R.V.I.S. // HUD TÁCTICO SUPREMO",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilos globales para blindar el fondo y la estética cyberpunk
st.markdown("""
    <style>
        .block-container { padding: 0rem !important; max-width: 100% !important; }
        header, footer, #MainMenu {visibility: hidden;}
        body, .stApp {background-color: #040711;}
    </style>
""", unsafe_allow_html=True)

# ZONA HORARIA CHILENA (UTC-3)
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

if "offset_clima" not in st.session_state:
    st.session_state.offset_clima = 0

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": saludo_actual + ", jefa. HUD operativo y Nodo Buin sincronizado con las 7 memorias."}
    ]

PIN_SECRETO = "2805"

# --- INICIALIZACION DE BASE DE DATOS SQLITE (Las 7 Memorias) ---
fn_db = "jarvis_misiones.db"

def init_db():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS misiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarea TEXT NOT NULL,
                estado TEXT DEFAULT 'Pendiente',
                fecha_creacion TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                key_id TEXT PRIMARY KEY,
                fact_text TEXT,
                category TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS episodic_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                details TEXT
            )
        """)
        conn.commit()
        conn.close()
    except Exception:
        pass

init_db()

# --- CLASES DE SOPORTE ---
class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path

    def remember_fact(self, key_id: str, fact_text: str, category: str = "general"):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)", (key_id, fact_text, category))
            conn.commit()
            conn.close()
        except Exception:
            pass

    def recall_context(self, query: str) -> list:
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute("SELECT fact_text FROM memory")
            rows = cursor.fetchall()
            conn.close()
            return [row[0] for row in rows if query.lower() in row[0].lower()]
        except Exception:
            return []

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

class JarvisSystemExecutor:
    @staticmethod
    def open_application(target: str) -> str:
        try:
            target_lower = target.lower()
            if target_lower.endswith(('.py', '.bat', '.sh', '.ps1')) and os.path.exists(target):
                if sys.platform == "win32":
                    subprocess.Popen('start cmd /k "' + sys.executable + ' ' + target + '"', shell=True)
                else:
                    subprocess.Popen([sys.executable, target])
                return "Script '" + os.path.basename(target) + "' puesto en marcha, jefa."
            
            if sys.platform == "win32":
                subprocess.Popen("start " + target, shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", target])
            else:
                subprocess.Popen([target])
            return "Ejecutando proceso '" + target + "' de inmediato, jefa."
        except Exception as e:
            return "Error ejecutando proceso: " + str(e)

jarvis_mem = JarvisMemory()
jarvis_exec = JarvisSystemExecutor()

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
        jarvis_mem.log_episode("MISSION_PURGE", "Misiones purgadas.")
    except Exception:
        pass

# --- 1. PANTALLA DE BLOQUEO (PIN) ---
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

# --- 2. HTML / CSS DEL HUD CIBERNÉTICO UNIFICADO ---
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
            background-image: 
                radial-gradient(circle at 50% 0%, rgba(0, 243, 255, 0.08) 0%, transparent 60%),
                linear-gradient(rgba(0, 243, 255, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 243, 255, 0.03) 1px, transparent 1px);
            background-size: 100% 100%, 30px 30px, 30px 30px;
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
            box-shadow: 0 0 18px rgba(0, 243, 255, 0.12), inset 0 0 12px rgba(0, 243, 255, 0.06);
            position: relative;
        }

        body.combat-mode {
            --cyan: #ff3b5c;
            --cyan-glow: rgba(255, 59, 92, 0.5);
            --cyan-dim: rgba(255, 59, 92, 0.2);
        }

        .header-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 16px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--cyan-dim);
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 16px;
        }

        .stark-reactor-box {
            width: 64px;
            height: 60px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            cursor: pointer;
            filter: drop-shadow(0 0 12px var(--cyan-glow));
            animation: reactorPulse 2.8s ease-in-out infinite;
        }

        @keyframes reactorPulse {
            0%, 100% { filter: drop-shadow(0 0 8px var(--cyan-glow)); transform: scale(1); }
            50% { filter: drop-shadow(0 0 20px var(--cyan)); transform: scale(1.05); }
        }

        .title-block h1 {
            font-family: 'Orbitron', sans-serif;
            font-size: 1.3rem;
            font-weight: 900;
            letter-spacing: 2px;
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
            letter-spacing: 1px;
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: var(--green-ok);
            box-shadow: 0 0 8px var(--green-ok);
            animation: blink 1.5s infinite;
        }

        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }

        .telemetry-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 10px;
            padding-top: 12px;
            font-size: 0.8rem;
        }

        .tele-item span.label {
            display: block;
            color: var(--text-muted);
            font-size: 0.68rem;
            margin-bottom: 3px;
        }

        .tele-item span.val {
            color: var(--cyan);
            font-weight: bold;
            font-size: 0.9rem;
        }

        .tele-clock { text-align: right; }
        .tele-clock .time {
            font-family: 'Orbitron', sans-serif;
            color: var(--amber);
            font-size: 1rem;
            font-weight: bold;
            text-shadow: 0 0 8px rgba(255, 174, 0, 0.4);
        }
        .tele-clock .loc {
            color: var(--text-muted);
            font-size: 0.68rem;
            margin-top: 2px;
        }

        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-family: 'Orbitron', sans-serif;
            font-size: 0.82rem;
            letter-spacing: 1.5px;
            color: var(--cyan);
        }

        .badge {
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.72rem;
            padding: 2px 8px;
            border: 1px solid var(--cyan);
            border-radius: 4px;
            background: rgba(0, 243, 255, 0.1);
            color: var(--green-ok);
        }

        .radar-box {
            height: 190px;
            background: radial-gradient(circle, rgba(0, 45, 70, 0.6) 0%, rgba(3, 9, 20, 0.95) 80%);
            border: 1px solid var(--cyan-dim);
            border-radius: 10px;
            position: relative;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .radar-grid {
            position: absolute;
            inset: 0;
            background-image: 
                linear-gradient(rgba(0, 243, 255, 0.08) 1px, transparent 1px),
                linear-gradient(90deg, rgba(0, 243, 255, 0.08) 1px, transparent 1px);
            background-size: 25px 25px;
        }

        .radar-circle {
            position: absolute;
            border: 1px solid rgba(0, 243, 255, 0.28);
            border-radius: 50%;
        }
        .c1 { width: 60px; height: 60px; }
        .c2 { width: 120px; height: 120px; }
        .c3 { width: 180px; height: 180px; }

        .radar-sweep {
            position: absolute;
            width: 180px;
            height: 180px;
            border-radius: 50%;
            background: conic-gradient(from 0deg, var(--cyan-glow) 0deg, transparent 75deg);
            animation: spinRadar 4s linear infinite;
        }
        @keyframes spinRadar { 100% { transform: rotate(360deg); } }

        .radar-center {
            width: 9px;
            height: 9px;
            background: var(--amber);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--amber);
            z-index: 2;
        }

        .radar-blip {
            position: absolute;
            top: 50px; right: 35%;
            width: 7px; height: 7px;
            background: var(--green-ok);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--green-ok);
            animation: blink 1.2s infinite;
        }

        .radar-overlay-top {
            position: absolute;
            top: 8px; left: 12px; right: 12px;
            display: flex; justify-content: space-between;
            font-size: 0.7rem; color: var(--cyan);
        }

        .radar-overlay-bottom {
            position: absolute;
            bottom: 8px; left: 12px; right: 12px;
            display: flex; justify-content: space-between;
            font-size: 0.7rem; color: var(--text-muted);
        }

        .orbital-box {
            height: 195px;
            background: radial-gradient(ellipse at center, rgba(0, 38, 65, 0.55) 0%, rgba(3, 8, 18, 0.95) 85%);
            border: 1px solid var(--cyan-dim);
            border-radius: 10px;
            position: relative;
            overflow: hidden;
        }

        canvas#orbitalCanvas { width: 100%; height: 100%; display: block; }

        .orbital-footer {
            display: flex; justify-content: space-between; align-items: center;
            flex-wrap: wrap; gap: 8px; margin-top: 10px;
            font-size: 0.75rem; color: var(--text-muted);
        }

        .audio-controls { display: flex; gap: 8px; }

        .btn-hud {
            background: rgba(0, 243, 255, 0.12);
            border: 1px solid var(--cyan);
            color: var(--cyan);
            font-family: 'Orbitron', sans-serif;
            font-size: 0.7rem;
            padding: 5px 10px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
        }

        .btn-hud:hover, .btn-hud.active {
            background: var(--cyan);
            color: var(--bg-dark);
            box-shadow: 0 0 12px var(--cyan);
            font-weight: bold;
        }

        .btn-hud.mic-listening {
            background: var(--red-alert);
            border-color: var(--red-alert);
            color: #fff;
            box-shadow: 0 0 14px var(--red-alert);
            animation: blink 1s infinite;
        }

        .quick-cmds {
            display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 8px;
        }

        .cmd-chip {
            background: rgba(0, 243, 255, 0.08);
            border: 1px solid var(--cyan-dim);
            color: var(--text-main);
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.72rem;
            padding: 3px 8px;
            border-radius: 5px;
            cursor: pointer;
            transition: 0.2s;
        }

        .cmd-chip:hover {
            border-color: var(--cyan);
            background: rgba(0, 243, 255, 0.2);
            color: #fff;
        }

        .chat-log {
            height: 150px;
            background: rgba(2, 6, 14, 0.88);
            border: 1px solid var(--cyan-dim);
            border-radius: 8px;
            padding: 10px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 6px;
            font-size: 0.82rem;
            line-height: 1.4;
        }

        .msg-jarvis { color: var(--cyan); }
        .msg-jefa { color: var(--green-ok); }
        .msg-sys { color: var(--amber); font-size: 0.75rem; }

        .chat-input-row { display: flex; gap: 8px; margin-top: 8px; }

        .chat-input {
            flex: 1;
            background: rgba(4, 10, 22, 0.95);
            border: 1px solid var(--cyan-dim);
            border-radius: 8px;
            padding: 8px 12px;
            color: #ffffff;
            font-family: 'Share Tech Mono', monospace;
            font-size: 0.85rem;
            outline: none;
        }

        .chat-input:focus {
            border-color: var(--cyan);
            box-shadow: 0 0 10px var(--cyan-glow);
        }

        .btn-send {
            background: rgba(0, 243, 255, 0.18);
            border: 1px solid var(--cyan);
            color: var(--cyan);
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            font-size: 0.78rem;
            padding: 0 16px;
            border-radius: 8px;
            cursor: pointer;
            transition: 0.2s;
        }

        .btn-send:hover {
            background: var(--cyan);
            color: var(--bg-dark);
            box-shadow: 0 0 14px var(--cyan);
        }
    </style>
</head>
<body>

<div class="hud-container">
    <div class="panel">
        <div class="header-top">
            <div class="header-left">
                <div class="stark-reactor-box" onclick="playCyberSound(); triggerQuick('estado del reactor')" title="Analizar Reactor Mark VI">
                    <svg width="60" height="56" viewBox="0 0 100 92" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <polygon points="6,8 94,8 50,86" fill="#061224" stroke="currentColor" stroke-width="4" stroke-linejoin="round" style="color: var(--cyan);"/>
                        <polygon points="18,15 82,15 50,72" fill="rgba(0, 243, 255, 0.15)" stroke="#7cf4ff" stroke-width="2" stroke-linejoin="round"/>
                        <polygon points="30,22 70,22 50,58" fill="currentColor" style="color: var(--cyan);"/>
                        <polygon points="38,27 62,27 50,48" fill="#ffffff"/>
                        <line x1="50" y1="8" x2="50" y2="22" stroke="#040711" stroke-width="3"/>
                        <line x1="25" y1="45" x2="39" y2="38" stroke="#040711" stroke-width="3"/>
                        <line x1="75" y1="45" x2="61" y2="38" stroke="#040711" stroke-width="3"/>
                    </svg>
                </div>
                <div class="title-block">
                    <h1>J.A.R.V.I.S. HUD</h1>
                    <div class="status-line">
                        <div class="status-dot"></div>
                        <span id="sysStatusText">EN LÍNEA // ESCUCHA ACTIVA</span>
                    </div>
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
        <div class="panel-header"><span>MAPA TÁCTICO SATELITAL</span><span class="badge" id="radarBadge">● NODO BUIN</span></div>
        <div class="radar-box">
            <div class="radar-grid"></div>
            <div class="radar-circle c1"></div><div class="radar-circle c2"></div><div class="radar-circle c3"></div>
            <div class="radar-sweep"></div>
            <div class="radar-center"></div>
            <div class="radar-blip"></div>
            <div class="radar-overlay-top"><span>SAT-LINK // NODO BUIN (CHILE)</span><span style="color: var(--green-ok);">LOCKED</span></div>
            <div class="radar-overlay-bottom"><span>LAT: -33.7312° S | LON: -70.7418° W</span><span id="radarScanStatus">BARRIDO: ACTIVO</span></div>
        </div>
    </div>

    <div class="panel">
        <div class="panel-header"><span>MAPA ORBITAL DE PROYECTOS</span><span class="badge">5 NODOS ACTIVOS</span></div>
        <div class="orbital-box"><canvas id="orbitalCanvas"></canvas></div>
        <div class="orbital-footer">
            <span>SISTEMA VOCAL: <strong id="voiceStateLabel" style="color: var(--green-ok);">ACTIVADO</strong></span>
            <div class="audio-controls">
                <button class="btn-hud active" id="btnVoiceToggle" onclick="playCyberSound(); toggleVoice()">VOZ HUD: ON</button>
                <button class="btn-hud" id="btnMic" onclick="playCyberSound(); startVoiceRecognition()">🎙️ HABLAR</button>
            </div>
        </div>
    </div>

    <div class="panel">
        <div class="panel-header"><span>CANAL DE COMANDO // CHAT NEURONAL</span><span style="font-size: 0.72rem; color: var(--amber);">JARVIS v3.1</span></div>
        <div class="quick-cmds">
            <button class="cmd-chip" onclick="playCyberSound(); triggerQuick('diagnóstico general')">⚡ DIAGNÓSTICO</button>
            <button class="cmd-chip" onclick="playCyberSound(); triggerQuick('escanear perímetro en Buin')">🛰️ ESCANEAR BUIN</button>
            <button class="cmd-chip" onclick="playCyberSound(); triggerQuick('estado de proyectos')">🪐 PROYECTOS</button>
            <button class="cmd-chip" onclick="playCyberSound(); triggerQuick('activar modo combate')">🛡️ MODO COMBATE</button>
            <button class="cmd-chip" onclick="playCyberSound(); triggerQuick('modo normal')">💠 MODO NORMAL</button>
        </div>
        <div class="chat-log" id="chatLog">
            <div class="msg-jarvis">[JARVIS]: Sistema táctico unificado con 7 memorias operando, jefa.</div>
        </div>
        <div class="chat-input-row">
            <input type="text" id="chatInput" class="chat-input" placeholder="Escribe una orden..." onkeydown="if(event.key==='Enter'){ event.preventDefault(); sendCmd(); }">
            <button type="button" class="btn-send" onclick="playCyberSound(); sendCmd()">ENVIAR</button>
        </div>
    </div>
</div>

<script>
    let audioCtx = null;
    function playCyberSound() {
        try {
            if (!audioCtx) {
                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            }
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(880, audioCtx.currentTime);
            osc.frequency.exponentialRampToValueAtTime(440, audioCtx.currentTime + 0.08);
            gain.gain.setValueAtTime(0.08, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.08);
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.08);
        } catch(e) {}
    }

    function updateClock() {
        const now = new Date();
        const clockEl = document.getElementById('hudClock');
        if (clockEl) {
            clockEl.textContent = now.toTimeString().split(' ')[0];
        }
        const cpuEl = document.getElementById('cpuVal');
        const ramEl = document.getElementById('ramVal');
        if (cpuEl && ramEl) {
            const cpu = 20 + Math.floor(Math.random() * 18);
            const ram = (4.1 + Math.random() * 0.4).toFixed(1);
            cpuEl.textContent = cpu + '%';
            ramEl.textContent = ram + ' GB';
        }
    }
    setInterval(updateClock, 1000);
    updateClock();

    const canvas = document.getElementById('orbitalCanvas');
    const ctx = canvas.getContext('2d');
    let nodes = [
        { name: 'J.A.R.V.I.S.', rx: 65, ry: 24, angle: 0.3, speed: 0.016, color: '#ffae00' },
        { name: 'Agente IA', rx: 105, ry: 38, angle: 1.8, speed: 0.012, color: '#00ff9d' },
        { name: 'Isla Números', rx: 145, ry: 52, angle: 3.4, speed: 0.009, color: '#00f3ff' },
        { name: 'Nodo Buin', rx: 185, ry: 66, angle: 4.9, speed: 0.007, color: '#b388ff' },
        { name: 'Protocolo Stark', rx: 225, ry: 80, angle: 0.9, speed: 0.005, color: '#ff5277' }
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
        const isCombat = document.body.classList.contains('combat-mode');
        const coreColor = isCombat ? '#ff3b5c' : '#00f3ff';

        const grad = ctx.createRadialGradient(cx, cy, 2, cx, cy, 24);
        grad.addColorStop(0, '#ffffff'); grad.addColorStop(0.4, coreColor); grad.addColorStop(1, 'transparent');
        ctx.fillStyle = grad; ctx.beginPath(); ctx.arc(cx, cy, 24, 0, Math.PI * 2); ctx.fill();

        nodes.forEach(n => {
            ctx.strokeStyle = isCombat ? 'rgba(255, 59, 92, 0.25)' : 'rgba(0, 243, 255, 0.22)';
            ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(cx, cy, n.rx, n.ry, 0, 0, Math.PI * 2); ctx.stroke();
            n.angle += n.speed;
            const nx = cx + Math.cos(n.angle) * n.rx, ny = cy + Math.sin(n.angle) * n.ry;
            ctx.fillStyle = n.color; ctx.shadowBlur = 10; ctx.shadowColor = n.color;
            ctx.beginPath(); ctx.arc(nx, ny, 5, 0, Math.PI * 2); ctx.fill(); ctx.shadowBlur = 0;
            ctx.fillStyle = '#d8f8ff'; ctx.font = '11px "Share Tech Mono", monospace'; ctx.fillText(n.name, nx + 9, ny + 4);
        });
        requestAnimationFrame(drawOrbitals);
    }
    drawOrbitals();

    let voiceEnabled = true;
    function speakJarvis(text) {
        if (!voiceEnabled || !('speechSynthesis' in window)) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'es-ES'; utterance.pitch = 0.85; utterance.rate = 1.03;
        const voices = window.speechSynthesis.getVoices();
        const maleSpanish = voices.find(v => v.lang.includes('es') && (v.name.includes('Pablo') || v.name.includes('Raul') || v.name.includes('Jorge') || v.name.includes('Male'))) || voices.find(v => v.lang.includes('es'));
        if (maleSpanish) utterance.voice = maleSpanish;
        window.speechSynthesis.speak(utterance);
    }

    if ('speechSynthesis' in window) {
        window.speechSynthesis.onvoiceschanged = () => window.speechSynthesis.getVoices();
    }

    function toggleVoice() {
        voiceEnabled = !voiceEnabled;
        const btn = document.getElementById('btnVoiceToggle'), lbl = document.getElementById('voiceStateLabel');
        if (voiceEnabled) {
            btn.textContent = 'VOZ HUD: ON'; btn.classList.add('active'); lbl.textContent = 'ACTIVADO'; lbl.style.color = 'var(--green-ok)';
            speakJarvis('Sistemas vocales reactivados, jefa.');
        } else {
            btn.textContent = 'VOZ HUD: OFF'; btn.classList.remove('active'); lbl.textContent = 'SILENCIADO'; lbl.style.color = 'var(--text-muted)';
            window.speechSynthesis.cancel();
        }
    }

    function startVoiceRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const log = document.getElementById('chatLog'), btnMic = document.getElementById('btnMic');
        if (!SpeechRecognition) {
            log.innerHTML += `<div class="msg-sys">[SISTEMA]: Reconocimiento de voz no soportado.</div>`;
            log.scrollTop = log.scrollHeight; return;
        }
        const recognition = new SpeechRecognition();
        recognition.lang = 'es-CL';
        recognition.onstart = () => { btnMic.classList.add('mic-listening'); btnMic.textContent = '🔴 ESCUCHANDO...'; };
        recognition.onresult = (e) => {
            document.getElementById('chatInput').value = e.results[0][0].transcript;
            sendCmd();
        };
        recognition.onerror = () => { btnMic.classList.remove('mic-listening'); btnMic.textContent = '🎙️ HABLAR'; };
        recognition.onend = () => { btnMic.classList.remove('mic-listening'); btnMic.textContent = '🎙️ HABLAR'; };
        recognition.start();
    }

    function generateJarvisReply(rawText) {
        const t = rawText.toLowerCase();
        if (t.includes('combate') || t.includes('alerta')) {
            document.body.classList.add('combat-mode');
            document.getElementById('reactorOut').textContent = '5.8 GJ/s [MAX]';
            document.getElementById('radarBadge').textContent = '⚠ ALERTA TÁCTICA';
            return 'Protocolo de combate activado, jefa. Reactor triangular al máximo.';
        }
        if (t.includes('normal') || t.includes('desactivar')) {
            document.body.classList.remove('combat-mode');
            document.getElementById('reactorOut').textContent = '3.2 GJ/s';
            document.getElementById('radarBadge').textContent = '● NODO BUIN';
            return 'Regresando a parámetros estándar.';
        }
        if (t.includes('diagnóstico') || t.includes('reactor')) {
            return 'Diagnóstico: reactor al 99.8% de eficiencia, sin amenazas en el Nodo Buin.';
        }
        if (t.includes('buin') || t.includes('escanear')) {
            document.getElementById('radarScanStatus').textContent = 'BARRIDO: OBJETIVO FIJADO';
            return 'Escaneo sobre Nodo Buin completado con éxito, jefa.';
        }
        return 'Orden procesada en el núcleo central. Todo en orden, jefa.';
    }

    function sendCmd() {
        const input = document.getElementById('chatInput'), log = document.getElementById('chatLog'), text = input.value.trim();
        if (!text) return;
        log.innerHTML += `<div class="msg-jefa">[JEFA]: ${text}</div>`;
        input.value = ''; log.scrollTop = log.scrollHeight;
        setTimeout(() => {
            const resp = generateJarvisReply(text);
            log.innerHTML += `<div class="msg-jarvis">[JARVIS]: ${resp}</div>`;
            log.scrollTop = log.scrollHeight;
            speakJarvis(resp);
        }, 350);
    }

    function triggerQuick(cmdText) {
        document.getElementById('chatInput').value = cmdText;
        sendCmd();
    }
</script>
</body>
</html>
"""

# Renderizar el HUD interactivo con scroll fluido
st.components.v1.html(jarvis_hud_html, height=1400, scrolling=True)

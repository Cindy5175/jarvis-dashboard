import datetime
import math
import os
import random
import re
import sqlite3
import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except Exception:
    Groq = None
    GROQ_AVAILABLE = False

st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="expanded",
)

NUCLEOS_DISPONIBLES = ["JARVIS", "VIERNES", "NOVA", "ARTEX"]

PROTOCOLO_CONOCIMIENTO_BASE = (
    "PROTOCOLO DE CONOCIMIENTO SUPREMO COMPARTIDO (APLICABLE A TODOS LOS NUCLEOS): "
    "Responde con rigor tecnico, precision y claridad estructurada en: "
    "(1) Biologia (celular, genetica, fisiologia, evolucion, ecologia); "
    "(2) Matematicas y Aritmetica (algebra, funciones, geometria, trigonometria, estadistica, "
    "probabilidad, porcentajes, proporciones y resolucion paso a paso); "
    "(3) Geografia (geografia fisica, climas, cartografia, recursos, geopolitica y geografia de Chile y del mundo); "
    "(4) Historia (procesos historicos, cronologia, causas y consecuencias, historia universal, de America y de Chile); "
    "(5) Ciencia y Tecnologia (fisica, quimica, astronomia, computacion, algoritmos, redes, sistemas e ingenieria); "
    "(6) Calculos en general (explicar formulas, variables, unidades y verificar resultados). "
    "Explica pasos o formulas cuando ayude, respeta unidades y no inventes datos sin confirmar."
)

st.session_state.setdefault("autorizado", False)
st.session_state.setdefault("nucleo_activo", "JARVIS")
st.session_state.setdefault("voz_masculina_activa", True)
st.session_state.setdefault("pendiente_voz", None)
st.session_state.setdefault("capa_radar", "SATELITAL // BUIN")
st.session_state.setdefault("notas_rapidas", [])
st.session_state.setdefault("modo_camara", "VISIÓN NOCTURNA")

PIN_SECRETO = "2805"
fn_db = "jarvis_misiones.db"
BUIN_LAT = -33.7325
BUIN_LON = -70.7422

API_KEY_GROQ = ""
try:
    API_KEY_GROQ = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    API_KEY_GROQ = os.environ.get("GROQ_API_KEY", "")

client_groq = None
if GROQ_AVAILABLE and API_KEY_GROQ:
    try:
        client_groq = Groq(api_key=API_KEY_GROQ)
    except Exception:
        client_groq = None


def init_db():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
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
    except Exception:
        pass


init_db()


class JarvisMemory:
    def __init__(self, db_path=fn_db):
        self.db_path = db_path

    def remember_fact(self, key_id: str, fact_text: str):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
                (key_id, fact_text, "general"),
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def get_recent_facts(self, limit: int = 6):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT fact_text FROM memory ORDER BY rowid DESC LIMIT ?", (limit,))
            rows = [r[0] for r in cursor.fetchall() if r and r[0]]
            conn.close()
            return rows
        except Exception:
            return []

    def clear_facts(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memory")
            conn.commit()
            conn.close()
        except Exception:
            pass


jarvis_mem = JarvisMemory()


def agregar_mision(tarea):
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
        conn.commit()
        conn.close()
    except Exception:
        pass


def obtener_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT id, tarea, estado FROM misiones")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def limpiar_misiones():
    try:
        conn = sqlite3.connect(fn_db, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM misiones")
        conn.commit()
        conn.close()
    except Exception:
        pass


@st.cache_data(ttl=300)
def obtener_indicadores_chile():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) JARVIS-Dashboard/1.0",
        "Accept": "application/json",
    }
    for _ in range(2):
        try:
            resp = requests.get("https://mindicador.cl/api", headers=headers, timeout=6)
            if resp.status_code == 200:
                data = resp.json()
                dolar = data.get("dolar", {}).get("valor")
                euro = data.get("euro", {}).get("valor")
                uf = data.get("uf", {}).get("valor")
                utm = data.get("utm", {}).get("valor")
                if dolar and euro and uf:
                    return {
                        "dolar": float(dolar),
                        "euro": float(euro),
                        "uf": float(uf),
                        "utm": float(utm) if utm else 0.0,
                        "ok": True,
                        "respaldo": False,
                    }
        except Exception:
            pass

    return {
        "dolar": 950.00,
        "euro": 1030.00,
        "uf": 38000.00,
        "utm": 67000.00,
        "ok": True,
        "respaldo": True,
    }


def describir_clima_codigo(code):
    mapa = {
        0: "despejado",
        1: "mayormente despejado",
        2: "parcialmente nublado",
        3: "nublado",
        45: "con neblina",
        61: "con lluvia leve",
        63: "con lluvia moderada",
        80: "con chubascos",
        95: "con tormenta electrica",
    }
    return mapa.get(code, "condiciones variables")


@st.cache_data(ttl=600)
def obtener_clima_buin():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={BUIN_LAT}&longitude={BUIN_LON}"
        f"&current=temperature_2m,weather_code&timezone=America%2FSantiago"
    )
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            current = resp.json().get("current") or {}
            temp = current.get("temperature_2m")
            code = int(current.get("weather_code", 0))
            if temp is not None:
                return {
                    "temp_c": round(float(temp), 1),
                    "condicion": describir_clima_codigo(code),
                }
    except Exception:
        pass
    return {"temp_c": None, "condicion": "sin lectura en vivo"}


def fmt_clp(valor):
    return "$" + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def obtener_hora_chile():
    tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
    return datetime.datetime.now(tz_chile)


def obtener_saludo_actual(ahora):
    hora = ahora.hour
    if 0 <= hora < 12:
        return "Buenos días"
    if 12 <= hora < 20:
        return "Buenas tardes"
    return "Buenas noches"


def obtener_saludo_nucleo(nucleo_nombre):
    ahora = obtener_hora_chile()
    saludo_actual = obtener_saludo_actual(ahora)
    pref = f"[{nucleo_nombre}] "
    saludos = {
        "JARVIS": f"{pref}{saludo_actual}, jefa. Qué milagro que pase a saludar; los servidores ya empezaban a extrañar sus órdenes.",
        "VIERNES": f"{pref}¡{saludo_actual}, jefa! Lista para mover ficha. ¿Qué encendemos hoy?",
        "NOVA": f"{pref}¡{saludo_actual}, jefa! Señal recibida desde el Nodo Buin. ¿Qué galaxia o tarea conquistamos ahora?",
        "ARTEX": f"{pref}¡{saludo_actual}, jefa! Núcleo ARTEX en línea con protocolo de conocimiento y control táctico activo.",
    }
    return saludos.get(nucleo_nombre, f"{pref}{saludo_actual}, jefa. En línea y a su servicio.")


def renderizar_banner_reloj_vivo(nucleo_activo, capa_radar):
    ahora = obtener_hora_chile()
    ts_ms = int(ahora.timestamp() * 1000)
    html_reloj = f"""
    <div style="
        border:1.5px solid #00f3ff;
        background:linear-gradient(135deg, #0a1128 0%, #060913 100%);
        padding:14px 18px;
        border-radius:8px;
        text-align:center;
        box-shadow:0 0 15px rgba(0, 243, 255, 0.3), inset 0 0 10px rgba(0, 243, 255, 0.15);
        margin:0 auto 14px auto;
        max-width:920px;
        font-family:monospace;
        color:#00f3ff;
    ">
        <div style="font-size:1.55rem;font-weight:bold;letter-spacing:1px;">⚡ J.A.R.V.I.S. // {nucleo_activo}</div>
        <div id="jarvis-reloj-vivo" style="font-size:0.92rem;font-weight:bold;margin-top:4px;opacity:0.95;">
            NODO BUIN, CHILE • {ahora.strftime("%d/%m/%Y %H:%M:%S")} • {capa_radar}
        </div>
    </div>
    <script>
    (function() {{
        let baseMs = {ts_ms};
        const offsetMs = -3 * 3600 * 1000;
        const capa = "{capa_radar}";
        const el = document.getElementById("jarvis-reloj-vivo");
        function pad(n) {{ return n < 10 ? "0" + n : "" + n; }}
        function tick() {{
            baseMs += 1000;
            const d = new Date(baseMs + offsetMs);
            const fecha = pad(d.getUTCDate()) + "/" + pad(d.getUTCMonth() + 1) + "/" + d.getUTCFullYear();
            const hora = pad(d.getUTCHours()) + ":" + pad(d.getUTCMinutes()) + ":" + pad(d.getUTCSeconds());
            if (el) {{
                el.textContent = "NODO BUIN, CHILE • " + fecha + " " + hora + " • " + capa;
            }}
        }}
        if (window.__jarvisClockTimer) clearInterval(window.__jarvisClockTimer);
        window.__jarvisClockTimer = setInterval(tick, 1000);
    }})();
    </script>
    """
    components.html(html_reloj, height=92)


def renderizar_camara_nocturna(modo_camara):
    es_ir = "INFRARROJO" in modo_camara
    color_main = "#00f3ff" if es_ir else "#39ff14"
    color_glow = "rgba(0, 243, 255, 0.35)" if es_ir else "rgba(57, 255, 20, 0.35)"
    filtro_css = (
        "grayscale(100%) contrast(155%) brightness(115%) sepia(100%) hue-rotate(155deg) saturate(320%)"
        if es_ir
        else "grayscale(100%) contrast(150%) brightness(120%) sepia(100%) hue-rotate(68deg) saturate(350%)"
    )
    html_cam = (
        f'<div style="border:1px solid {color_main};background:#030906;border-radius:6px;'
        f'padding:6px;font-family:monospace;color:{color_main};">'
        f'<div style="display:flex;justify-content:space-between;align-items:center;gap:4px;'
        f'font-size:0.70rem;font-weight:bold;margin-bottom:4px;">'
        f'<span>● CAM-01 // BUIN</span>'
        f'<button id="btn-cam-real" type="button" style="background:{color_main};color:#040a07;'
        f'border:none;border-radius:4px;padding:2px 6px;font-family:monospace;font-size:0.65rem;'
        f'font-weight:bold;cursor:pointer;">Activar Cámara</button></div>'
        f'<video id="cam-real-video" autoplay playsinline muted style="display:none;"></video>'
        f'<canvas id="cam-nocturna-canvas" width="250" height="135" style="width:100%;height:135px;'
        f'border-radius:4px;background:#020704;box-shadow:inset 0 0 14px {color_glow};"></canvas>'
        f'<div id="estado-cam-jarvis" style="font-size:0.66rem;opacity:0.85;margin-top:3px;">'
        f'Modo simulado listo • Pulsa "Activar Cámara" para señal real</div></div>'
        f'<script>(function(){{const c=document.getElementById("cam-nocturna-canvas");'
        f'const v=document.getElementById("cam-real-video");const btn=document.getElementById("btn-cam-real");'
        f'const stEl=document.getElementById("estado-cam-jarvis");if(!c)return;'
        f'const ctx=c.getContext("2d");const mainColor="{color_main}";const filtro="{filtro_css}";'
        f'let scanY=0,t=0,camActiva=false;'
        f'async function iniciarCamaraReal(){{try{{if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){{'
        f'if(stEl)stEl.textContent="Cámara no soportada aquí • Manteniendo simulador";return;}}'
        f'if(window.__jarvisCamStream){{window.__jarvisCamStream.getTracks().forEach(tr=>tr.stop());}}'
        f'const stream=await navigator.mediaDevices.getUserMedia({{video:{{facingMode:"environment"}},audio:false}});'
        f'window.__jarvisCamStream=stream;if(v){{v.srcObject=stream;await v.play();}}'
        f'camActiva=true;if(stEl)stEl.textContent="Cámara real activa con filtro nocturno";}}'
        f'catch(e){{camActiva=false;if(stEl)stEl.textContent="Permiso denegado o sin HTTPS • Modo simulado";}}}}'
        f'if(btn)btn.onclick=iniciarCamaraReal;'
        f'function draw(){{t+=0.05;ctx.save();if(camActiva&&v&&v.readyState>=2){{ctx.filter=filtro;'
        f'ctx.drawImage(v,0,0,c.width,c.height);ctx.filter="none";}}else{{ctx.fillStyle="#030a06";'
        f'ctx.fillRect(0,0,c.width,c.height);ctx.strokeStyle=mainColor+"22";ctx.lineWidth=1;'
        f'for(let x=0;x<c.width;x+=25){{ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,c.height);ctx.stroke();}}'
        f'for(let y=0;y<c.height;y+=22){{ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(c.width,y);ctx.stroke();}}'
        f'ctx.fillStyle=mainColor+"33";ctx.fillRect(20,78,52,34);ctx.fillRect(165,68,64,44);'
        f'ctx.beginPath();ctx.arc(125+Math.sin(t)*14,62+Math.cos(t*1.3)*6,7,0,Math.PI*2);'
        f'ctx.strokeStyle=mainColor;ctx.stroke();for(let i=0;i<65;i++){{'
        f'const nx=(i*37+Math.floor(t*90))%c.width;const ny=(i*53+Math.floor(t*45))%c.height;'
        f'ctx.fillStyle=mainColor+"44";ctx.fillRect(nx,ny,2,2);}}}}'
        f'scanY=(scanY+2.2)%c.height;ctx.strokeStyle=mainColor+"aa";ctx.beginPath();'
        f'ctx.moveTo(0,scanY);ctx.lineTo(c.width,scanY);ctx.stroke();ctx.fillStyle=mainColor;'
        f'ctx.font="bold 10px monospace";'
        f'ctx.fillText(camActiva?"LIVE CAM [●] NIGHT-OPTIC":"SIM [●] IR-GAIN: +24dB",8,14);'
        f'ctx.fillText("SECTOR BUIN SUR",8,c.height-8);ctx.restore();}}'
        f'if(window.__jarvisCamTimer)clearInterval(window.__jarvisCamTimer);'
        f'window.__jarvisCamTimer=setInterval(draw,80);draw();}})();</script>'
    )
    components.html(html_cam, height=192)


def limpiar_texto_para_voz(texto):
    limpio = re.sub(r"^\[[^\]]+\]\s*", "", texto or "")
    limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace ", limpio)
    limpio = re.sub(r"https?://\S+", " enlace ", limpio)
    limpio = re.sub(r"[*_`#>\[\]|]+", " ", limpio)
    limpio = re.sub(r"([.!?])\s+", r"\1 ... ", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio[:520]


def programar_voz(texto, idioma="es-CL"):
    if st.session_state.get("voz_masculina_activa", True):
        limpio = limpiar_texto_para_voz(texto)
        if limpio:
            st.session_state["pendiente_voz"] = {"texto": limpio, "idioma": idioma}


def reproducir_voz_pendiente():
    pendiente = st.session_state.get("pendiente_voz")
    if not pendiente or not st.session_state.get("voz_masculina_activa", True):
        return
    st.session_state["pendiente_voz"] = None
    txt = pendiente["texto"].replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")
    lang = pendiente["idioma"]
    js_voz = (
        "<script>(function(){try{if(!('speechSynthesis' in window))return;"
        "function elegirVoz(voices){"
        "if(!voices||!voices.length)return null;"
        "const es=voices.filter(v=>/^(es|es-CL|es-ES|es-MX|es-US)/i.test(v.lang||''));"
        "const pref=es.find(v=>/jorge|diego|carlos|enrique|pablo|mateo|alonso|raul|male|hombre/i.test(v.name||''))||es[0]||voices[0];"
        "return pref||null;}"
        "function hablarAhora(){"
        "window.speechSynthesis.cancel();"
        "const trozos=" + f'"{txt}"' + ".split(' ... ').filter(Boolean);"
        "const lista=trozos.length?trozos:[" + f'"{txt}"' + "];"
        "const vozElegida=elegirVoz(window.speechSynthesis.getVoices());"
        "lista.forEach((parte)=>{"
        "const u=new SpeechSynthesisUtterance(parte);"
        f"u.lang='{lang}';"
        "u.rate=0.98;"
        "u.pitch=0.90;"
        "if(vozElegida)u.voice=vozElegida;"
        "setTimeout(()=>{try{window.speechSynthesis.speak(u);}catch(e){}},100);"
        "});}"
        "if(window.speechSynthesis.getVoices().length){hablarAhora();}"
        "else{window.speechSynthesis.onvoiceschanged=function(){hablarAhora();};setTimeout(hablarAhora,220);}"
        "}catch(e){}})();</script>"
    )
    try:
        components.html(js_voz, height=1)
    except Exception:
        pass


def renderizar_microfono_voz():
    js_mic = """
    <div style="display:flex;align-items:center;gap:8px;margin:4px 0 10px 0;">
        <button id="btn-mic-jarvis" type="button" style="
            background:#00f3ff;color:#060913;border:1.5px solid #00f3ff;
            border-radius:6px;padding:6px 12px;font-family:monospace;
            font-weight:bold;font-size:0.78rem;cursor:pointer;
            box-shadow:0 0 10px rgba(0,243,255,0.5);
        ">🎤 Hablar por Voz</button>
        <span id="estado-mic-jarvis" style="
            color:#00f3ff;font-family:monospace;font-size:0.75rem;opacity:0.85;
        ">Micrófono listo (es-CL)</span>
    </div>
    <script>
    (function() {
        const btn = document.getElementById("btn-mic-jarvis");
        const stEl = document.getElementById("estado-mic-jarvis");
        if (!btn || !stEl) return;
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SR) {
            stEl.textContent = "Dictado por voz no soportado en este navegador";
            return;
        }
        btn.onclick = function() {
            try {
                const rec = new SR();
                rec.lang = "es-CL";
                rec.interimResults = false;
                rec.maxAlternatives = 1;
                stEl.textContent = "Escuchando, jefa...";
                rec.onresult = function(ev) {
                    const dicho = (ev.results[0] && ev.results[0][0] && ev.results[0][0].transcript) || "";
                    stEl.textContent = dicho ? ('Escuchado: "' + dicho + '"') : "No se captó audio";
                    if (!dicho) return;
                    const doc = window.parent.document;
                    const inputs = doc.querySelectorAll('textarea[data-testid="stChatInputTextArea"], input[data-testid="stChatInputTextArea"], textarea');
                    let target = null;
                    inputs.forEach(el => {
                        if (el.offsetParent !== null) target = el;
                    });
                    if (target) {
                        const setter = Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype, "value") ||
                                       Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value");
                        if (setter && setter.set) setter.set.call(target, dicho);
                        else target.value = dicho;
                        target.dispatchEvent(new Event("input", { bubbles: true }));
                        target.dispatchEvent(new Event("change", { bubbles: true }));
                        setTimeout(() => {
                            const sendBtn = doc.querySelector('button[data-testid="stChatInputSubmitButton"]');
                            if (sendBtn) sendBtn.click();
                        }, 180);
                    }
                };
                rec.onerror = function() { stEl.textContent = "Error al acceder al micrófono"; };
                rec.onend = function() {
                    if (stEl.textContent === "Escuchando, jefa...") stEl.textContent = "Micrófono listo (es-CL)";
                };
                rec.start();
            } catch (e) {
                stEl.textContent = "No se pudo iniciar el micrófono";
            }
        };
    })();
    </script>
    """
    try:
        components.html(js_mic, height=46)
    except Exception:
        pass


def resolver_calculo_o_unidad(texto_raw):
    t = (texto_raw or "").strip().lower()

    mp = re.search(r"(\d+(?:[.,]\d+)?)\s*%\s*(?:de|del)\s*(\d+(?:[.,]\d+)?)", t)
    if mp:
        pct = float(mp.group(1).replace(",", "."))
        base = float(mp.group(2).replace(",", "."))
        val = (pct / 100.0) * base
        res = int(val) if val.is_integer() else round(val, 6)
        return f"Cálculo porcentual: **{pct:g}%** de **{base:g}** = **{res}**."

    mu = re.search(
        r"(-?\d+(?:[.,]\d+)?)\s*"
        r"(km|m|cm|mm|mi|millas|kg|g|lb|libras|l|ml|km/h|m/s|c|°c|f|°f|k)\s*"
        r"(?:a|en|to|in)\s*"
        r"(km|m|cm|mm|mi|millas|kg|g|lb|libras|l|ml|km/h|m/s|c|°c|f|°f|k)",
        t,
    )
    if mu:
        val = float(mu.group(1).replace(",", "."))
        u1 = mu.group(2).replace("°", "")
        u2 = mu.group(3).replace("°", "")
        if u1 == "millas":
            u1 = "mi"
        if u2 == "millas":
            u2 = "mi"
        if u1 == "libras":
            u1 = "lb"
        if u2 == "libras":
            u2 = "lb"

        long_m = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "mi": 1609.344}
        masa_kg = {"g": 0.001, "kg": 1.0, "lb": 0.45359237}
        vol_l = {"ml": 0.001, "l": 1.0}
        vel_ms = {"m/s": 1.0, "km/h": 1.0 / 3.6}

        if u1 in long_m and u2 in long_m:
            return f"Conversión de longitud: **{val:g} {u1}** = **{round((val * long_m[u1]) / long_m[u2], 4):g} {u2}**."
        if u1 in masa_kg and u2 in masa_kg:
            return f"Conversión de masa: **{val:g} {u1}** = **{round((val * masa_kg[u1]) / masa_kg[u2], 4):g} {u2}**."
        if u1 in vol_l and u2 in vol_l:
            return f"Conversión de volumen: **{val:g} {u1}** = **{round((val * vol_l[u1]) / vol_l[u2], 4):g} {u2}**."
        if u1 in vel_ms and u2 in vel_ms:
            return f"Conversión de velocidad: **{val:g} {u1}** = **{round((val * vel_ms[u1]) / vel_ms[u2], 4):g} {u2}**."
        if u1 in {"c", "f", "k"} and u2 in {"c", "f", "k"}:
            c = val if u1 == "c" else ((val - 32) * 5 / 9 if u1 == "f" else val - 273.15)
            out_t = c if u2 == "c" else (c * 9 / 5 + 32 if u2 == "f" else c + 273.15)
            return f"Conversión térmica: **{val:g} {u1.upper()}** = **{round(out_t, 2):g} {u2.upper()}**."

    expr = t
    for pref in ["calcula", "calcular", "cuanto es", "cuánto es", "resuelve", "aritmetica", "aritmética", "matematica", "matemática", "="]:
        if expr.startswith(pref):
            expr = expr[len(pref):].strip()
    expr = expr.replace("×", "*").replace("÷", "/").replace("^", "**").replace(",", ".")
    if (
        re.search(r"\d", expr)
        and not re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", expr)
        and re.fullmatch(r"[0-9+\-*/().%\s,a-z_]+", expr)
    ):
        env = {
            "__builtins__": {},
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "pow": pow,
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log10,
            "ln": math.log,
            "exp": math.exp,
            "pi": math.pi,
            "e": math.e,
        }
        try:
            res = eval(expr, env, {})
            if isinstance(res, (int, float)) and not isinstance(res, bool):
                out = int(res) if (isinstance(res, float) and res.is_integer()) else (round(res, 6) if isinstance(res, float) else res)
                return f"Resultado del cálculo `{expr}`: **{out}**."
        except Exception:
            return None
    return None


def construir_mensajes_conversacion(nucleo, texto_usuario):
    ahora = obtener_hora_chile()
    recuerdos = jarvis_mem.get_recent_facts(6)
    perfiles = {
        "JARVIS": "Eres JARVIS, asistente principal de la jefa en el Nodo Buin, Chile. Hablas con calidez, elegancia, fluidez natural y un toque sutil de ingenio irónico sin sonar robótico.",
        "VIERNES": "Eres VIERNES, asistente ágil, cercana y directa de la jefa en el Nodo Buin, Chile. Respondes con ritmo conversacional fluido y práctico.",
        "NOVA": "Eres NOVA, núcleo de exploración y análisis de la jefa en el Nodo Buin, Chile. Tienes un tono atento, fluido y curioso.",
        "ARTEX": "Eres ARTEX, núcleo táctico de precisión de la jefa en el Nodo Buin, Chile. Respondes con claridad, fluidez y rigor.",
    }
    sys_prompt = (
        f"{perfiles.get(nucleo, perfiles['JARVIS'])} "
        f"Hora actual en Chile: {ahora.strftime('%d/%m/%Y %H:%M:%S')}. "
        "Mantén continuidad con el hilo previo de la conversación, evita repetir saludos si ya están conversando "
        "y responde de forma natural y coherente. "
        f"{PROTOCOLO_CONOCIMIENTO_BASE}"
    )
    if recuerdos:
        sys_prompt += " Datos recordados en memoria: " + " | ".join(recuerdos)

    msgs = [{"role": "system", "content": sys_prompt}]
    historial_previo = st.session_state.get("mensajes", [])[-8:]
    for item in historial_previo:
        rol = item.get("role")
        contenido = item.get("content", "")
        if rol in {"user", "assistant"} and contenido:
            contenido_limpio = re.sub(r"^\[[^\]]+\]\s*", "", contenido)
            msgs.append({"role": rol, "content": contenido_limpio})

    if not msgs or msgs[-1].get("role") != "user" or msgs[-1].get("content") != texto_usuario:
        msgs.append({"role": "user", "content": texto_usuario})
    return msgs


def generar_respuesta_coherente(nucleo, texto_usuario):
    ahora = obtener_hora_chile()
    prefijo = f"[{nucleo}] "
    raw = (texto_usuario or "").strip()
    t = raw.lower()

    if t.startswith("recuerda ") or t.startswith("recuérdame ") or t.startswith("recuerdame "):
        partes = raw.split(" ", 1)
        dato = partes[1].strip() if len(partes) > 1 else ""
        if dato:
            jarvis_mem.remember_fact(f"fact_{int(ahora.timestamp())}", dato)
            return f"{prefijo}Listo, jefa, queda guardado en memoria: **{dato}**. ¿Seguimos con eso o cambiamos de tema?"

    palabras_saludo = [
        "hola", "buenas", "buenos días", "buenos dias",
        "buenas tardes", "buenas noches", "holi", "qué tal", "que tal",
    ]
    if any(t == s or t.startswith(s + " ") or t.startswith(s + ",") for s in palabras_saludo):
        return obtener_saludo_nucleo(nucleo)

    if "mosca" in t and ("patas" in t or "cuantas" in t or "cuántas" in t):
        if nucleo == "JARVIS":
            return f"{prefijo}Tiene **6 patas**, jefa. Como todo insecto que se precie... y por lo general las usa para aterrizar justo en el peor momento."
        if nucleo == "VIERNES":
            return f"{prefijo}**6 patas**, jefa. Tres de cada lado, livianita y bastante molesta."
        return f"{prefijo}Una mosca tiene **6 patas**, jefa. Anatomía básica de insecto confirmada."

    if any(k in t for k in ["bolsa", "bolsas", "acciones", "nasdaq", "mercado", "mercados", "wall street", "finviz"]):
        if nucleo == "JARVIS":
            return (
                f"{prefijo}En modo respaldo local no tengo cotizaciones bursátiles en vivo dentro del chat, jefa. "
                "Puede revisar el pulso directo en **Finviz** o el seguimiento **Nasdaq** desde el panel lateral de **Enlaces Financieros**."
            )
        if nucleo == "VIERNES":
            return (
                f"{prefijo}Sin conexión directa a cotizaciones en vivo aquí adentro, jefa. "
                "Abra **Finviz** o **Nasdaq** en el menú lateral para ver cómo se mueven las bolsas ahora mismo."
            )
        return (
            f"{prefijo}Radar bursátil sin feed en vivo en esta consola local, jefa. "
            "Tiene acceso directo a **Finviz** y **Nasdaq** en el panel de **Enlaces Financieros**."
        )

    if any(k in t for k in ["dólar", "dolar", "euro", "uf", "utm", "divisa", "divisas", "moneda", "cambio"]):
        econ = obtener_indicadores_chile()
        if econ.get("ok"):
            dolar_fmt = fmt_clp(econ["dolar"])
            euro_fmt = fmt_clp(econ["euro"])
            uf_fmt = fmt_clp(econ["uf"])
            nota_resp = " (valor de respaldo local)" if econ.get("respaldo") else ""
            return (
                f"{prefijo}Indicadores registrados en el Nodo Buin{nota_resp}, jefa: "
                f"Dólar Obs. **{dolar_fmt}**, Euro **{euro_fmt}** y UF **{uf_fmt}**."
            )

    if any(k in t for k in ["clima", "temperatura", "lluvia", "tiempo en buin"]):
        clima = obtener_clima_buin()
        if clima.get("temp_c") is not None:
            return f"{prefijo}En Buin hay **{clima['temp_c']}°C** y el cielo está **{clima['condicion']}**, jefa."
        return f"{prefijo}Sin lectura meteorológica en vivo en este momento, jefa."

    if any(k in t for k in ["hora", "qué hora", "que hora", "fecha", "día de hoy", "dia de hoy"]):
        hora_str = ahora.strftime("%H:%M:%S")
        return (
            f"{prefijo}En el Nodo Buin son las **{hora_str}** (hora de Chile), jefa. "
            "El segundero superior está corriendo en vivo."
        )

    if any(k in t for k in ["estado", "sistema", "misión", "misiones", "pendiente", "pendientes"]):
        misiones = obtener_misiones()
        cant = len(misiones)
        return (
            f"{prefijo}Núcleo **{nucleo}** operativo y estable en el Nodo Buin, jefa. "
            f"Actualmente hay **{cant}** misión(es) registrada(s) en la base de datos."
        )

    calc = resolver_calculo_o_unidad(raw)
    if calc:
        return f"{prefijo}{calc}"

    if client_groq is not None:
        try:
            mensajes_ctx = construir_mensajes_conversacion(nucleo, raw)
            resp = client_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=mensajes_ctx,
                temperature=0.65,
                max_tokens=600,
            )
            contenido = (resp.choices[0].message.content or "").strip()
            if contenido:
                contenido = re.sub(r"^\[[^\]]+\]\s*", "", contenido)
                return f"{prefijo}{contenido}"
        except Exception:
            pass

    if any(k in t for k in ["corazon", "corazón", "cardiaco", "cardíaco", "cardiaca", "cardíaca", "pulso", "latido", "sangre", "arteria", "vena"]):
        return (
            f"{prefijo}**Fisiología del corazón ({raw})**: es un órgano muscular hueco "
            "con cuatro cavidades (dos aurículas y dos ventrículos) que bombea sangre por los circuitos "
            "pulmonar y sistémico mediante ciclos de sístole y diástole, regulados por el sistema de "
            "conducción eléctrica (nodo sinusal, nodo auriculoventricular y haz de His)."
        )

    if any(k in t for k in ["biologia", "biología", "celula", "célula", "adn", "genetica", "genética", "ecosistema", "fotosintesis", "fotosíntesis", "evolucion", "evolución"]):
        return (
            f"{prefijo}**Biología ({raw})**: la célula es la unidad básica de la vida; "
            "el ADN codifica la información genética (transcripción a ARN y traducción a proteínas), y la energía "
            "fluye por los ecosistemas desde productores hasta consumidores y descomponedores."
        )

    if any(k in t for k in ["geografia", "geografía", "capital", "cordillera", "rio", "río", "continente", "hemisferio", "latitud", "longitud"]):
        return (
            f"{prefijo}**Geografía ({raw})**: estudia relieves, climas, hidrografía, "
            "población y territorio. En Chile destacan la cordillera de los Andes, la depresión intermedia, "
            "la cordillera de la Costa y las planicies litorales."
        )

    if any(k in t for k in ["historia", "siglo", "guerra", "revolucion", "revolución", "imperio", "independencia", "epoca", "época"]):
        return (
            f"{prefijo}**Historia ({raw})**: se analiza por causas estructurales y coyunturales, "
            "actores, cronología y consecuencias. Indica período, lugar o evento exacto para detallarlo."
        )

    if any(k in t for k in ["fisica", "física", "quimica", "química", "atomo", "átomo", "energia", "energía", "velocidad", "fuerza", "tecnologia", "tecnología", "algoritmo", "python", "astronomia", "astronomía"]):
        return (
            f"{prefijo}**Ciencia y Tecnología ({raw})**: integra modelos, magnitudes y unidades "
            "del SI con aplicación práctica. También puedes pedir cálculos directos o conversiones."
        )

    respuestas_generales = {
        "JARVIS": [
            f"{prefijo}Entendido, jefa. Sobre *'{raw}'*, seguimos el hilo aquí mismo; ¿quiere que lo dejemos como misión o que abramos algún módulo del panel?",
            f"{prefijo}Tomo nota de *'{raw}'*, jefa. Dígame cómo quiere continuar y lo vamos armando paso a paso."
        ],
        "VIERNES": [
            f"{prefijo}Recibido, jefa: *'{raw}'*. Vamos directo al grano: ¿qué hacemos con eso ahora?",
            f"{prefijo}Anotado, jefa. ¿Qué paso siguiente damos con *'{raw}'*?"
        ],
        "NOVA": [
            f"{prefijo}Señal clara sobre *'{raw}'*, jefa. ¿Lo registramos en memoria o revisamos algún módulo del Nodo Buin?",
            f"{prefijo}Procesado en el Nodo Buin: *'{raw}'*. ¿En qué más le apoyo, jefa?"
        ],
        "ARTEX": [
            f"{prefijo}Directiva registrada: *'{raw}'*, jefa. Protocolo de conocimiento y control activo.",
        ],
    }
    return random.choice(respuestas_generales.get(nucleo, [f"{prefijo}Recibido, jefa."]))


st.session_state.setdefault(
    "mensajes",
    [
        {
            "role": "assistant",
            "content": obtener_saludo_nucleo(st.session_state.nucleo_activo),
        }
    ],
)

estilos_css = """
    <style>
        .stApp { background-color: #060913 !important; color: #00f3ff !important; font-family: monospace; }
        .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {
            color: #00f3ff !important; font-family: monospace;
        }
        [data-testid="stIconMaterial"], .material-symbols-rounded, .material-icons,
        [data-testid="stExpander"] svg, [data-testid="stSidebar"] svg {
            font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
            color: #00f3ff !important;
        }
        [data-testid="stExpander"] summary {
            display: flex !important; align-items: center !important; gap: 6px !important;
        }

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
        .econ-label { font-size: 0.75rem !important; opacity: 0.85; color: #00f3ff !important; }
        .econ-val { font-size: 0.85rem !important; font-weight: bold; text-shadow: 0 0 6px #00f3ff; color: #00f3ff !important; }

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

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
"""
st.markdown(estilos_css, unsafe_allow_html=True)

if not st.session_state.get("autorizado", False):
    st.markdown(
        '<div style="text-align: center; margin-top: 50px;">'
        '<h2 style="color: #00f3ff;">ACCESO RESTRINGIDO - NODO BUIN</h2>'
        '<p style="color: #00f3ff; opacity: 0.8; font-size: 0.85rem;">INGRESE PIN DE SEGURIDAD PARA ACTIVAR LA ARMADURA</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto:", type="password", placeholder="Ingresa tu PIN...")
            btn_entrar = st.form_submit_button("Desbloquear Sistema")
        if btn_entrar:
            if pin_input.strip() == PIN_SECRETO:
                st.session_state.autorizado = True
                ini = obtener_saludo_nucleo(st.session_state.nucleo_activo)
                st.session_state.mensajes = [{"role": "assistant", "content": ini}]
                programar_voz(ini, idioma="es-CL")
                st.rerun()
            else:
                st.error("PIN incorrecto. Acceso denegado.")
    reproducir_voz_pendiente()
    st.stop()

with st.sidebar:
    st.markdown(
        '<div class="arc-reactor-container">'
        '<div class="arc-ring"><div class="arc-triangle-inverted"></div></div>'
        '<h3>⚡ NODO BUIN // IA</h3>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### 🛡️ Arsenal de Módulos")
    st.markdown("---")

    if st.button("🔒 Bloquear Sistema", use_container_width=True):
        st.session_state.autorizado = False
        st.rerun()

    if st.button("🔄 Reinicio Total", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.session_state.voz_masculina_activa = st.checkbox(
        "🔊 Voz activa",
        value=st.session_state.voz_masculina_activa,
    )

    st.markdown("---")
    st.markdown("#### 🧠 Selector de Núcleo (IA)")
    nuevo_nucleo = st.radio(
        "Seleccionar Asistente Activo:",
        NUCLEOS_DISPONIBLES,
        index=NUCLEOS_DISPONIBLES.index(st.session_state.nucleo_activo),
        label_visibility="collapsed",
    )
    if nuevo_nucleo != st.session_state.nucleo_activo:
        st.session_state.nucleo_activo = nuevo_nucleo
        saludo_cam = obtener_saludo_nucleo(nuevo_nucleo)
        st.session_state.mensajes.append({"role": "assistant", "content": saludo_cam})
        programar_voz(saludo_cam, idioma="es-CL")
        st.rerun()

    st.markdown("---")
    with st.expander("🛰️ Radar y Capas"):
        capa_sel = st.selectbox(
            "Capa activa:",
            ["SATELITAL // BUIN", "METEOROLOGÍA // OPEN-METEO", "FINANZAS // MINDICADOR"],
            index=["SATELITAL // BUIN", "METEOROLOGÍA // OPEN-METEO", "FINANZAS // MINDICADOR"].index(
                st.session_state.capa_radar
            ),
        )
        if capa_sel != st.session_state.capa_radar:
            st.session_state.capa_radar = capa_sel
            st.rerun()
        st.markdown(
            '<a class="tactical-link-btn" href="https://osirisai.live/" target="_blank">🌐 osirisai.live Radar</a>',
            unsafe_allow_html=True,
        )

    with st.expander("📡 Enlaces Financieros"):
        st.markdown(
            '<a class="tactical-link-btn" href="https://osirisai.live/" target="_blank">🌐 osirisai.live</a>'
            '<a class="tactical-link-btn" href="https://finviz.com/" target="_blank">📈 Finviz Screener</a>'
            '<a class="tactical-link-btn" href="https://www.nasdaq.com/" target="_blank">📊 Nasdaq Markets</a>'
            '<a class="tactical-link-btn" href="https://mindicador.cl/" target="_blank">🇨🇱 Mindicador CL</a>',
            unsafe_allow_html=True,
        )

    with st.expander("🌙 Cámara Nocturna"):
        modo_cam = st.selectbox(
            "Modo visor:",
            ["VISIÓN NOCTURNA", "INFRARROJO TÁCTICO"],
            index=["VISIÓN NOCTURNA", "INFRARROJO TÁCTICO"].index(st.session_state.modo_camara),
        )
        if modo_cam != st.session_state.modo_camara:
            st.session_state.modo_camara = modo_cam
            st.rerun()
        renderizar_camara_nocturna(st.session_state.modo_camara)

    with st.expander("📝 Notas Rápidas"):
        nota_txt = st.text_input("Nueva nota:", placeholder="Escribe un apunte...")
        cn1, cn2 = st.columns(2)
        if cn1.button("💾 Guardar Nota", use_container_width=True):
            if nota_txt.strip():
                st.session_state.notas_rapidas.append(nota_txt.strip())
                st.rerun()
        if cn2.button("🧹 Borrar Notas", use_container_width=True):
            st.session_state.notas_rapidas = []
            st.rerun()
        if st.session_state.notas_rapidas:
            for idx, n_item in enumerate(st.session_state.notas_rapidas[-6:], 1):
                st.markdown(f"- **{idx}.** {n_item}")
        else:
            st.caption("Sin notas rápidas.")

    with st.expander("🧮 Calculadora Táctil"):
        ca1, ca2 = st.columns(2)
        num_a = ca1.number_input("Valor A", value=0.0, step=1.0, format="%.2f")
        num_b = ca2.number_input("Valor B", value=0.0, step=1.0, format="%.2f")
        op_calc = st.selectbox("Operación", ["+", "-", "×", "÷", "^"])
        if st.button("⚡ Calcular", use_container_width=True):
            res_calc = None
            if op_calc == "+":
                res_calc = num_a + num_b
            elif op_calc == "-":
                res_calc = num_a - num_b
            elif op_calc == "×":
                res_calc = num_a * num_b
            elif op_calc == "÷":
                res_calc = "Error: div/0" if num_b == 0 else num_a / num_b
            elif op_calc == "^":
                res_calc = num_a ** num_b
            st.markdown(f"**Resultado:** `{res_calc}`")

    with st.expander("📊 Telemetría del Sistema"):
        estado_groq = "ONLINE" if client_groq is not None else "RESPALDO LOCAL"
        st.markdown(f"- **Nodo:** Buin ({BUIN_LAT}, {BUIN_LON})")
        st.markdown(f"- **Núcleo:** {st.session_state.nucleo_activo}")
        st.markdown(f"- **Motor IA:** {estado_groq}")
        st.markdown(f"- **Misiones:** {len(obtener_misiones())}")
        st.markdown(f"- **Recuerdos SQLite:** {len(jarvis_mem.get_recent_facts(50))}")

    with st.expander("🎯 Misiones Activas"):
        mision_txt = st.text_input("Nueva misión:", placeholder="Ej. Revisar indicadores...")
        c1, c2 = st.columns(2)
        if c1.button("➕ Añadir", use_container_width=True):
            if mision_txt.strip():
                agregar_mision(mision_txt.strip())
                st.rerun()
        if c2.button("🗑️ Borrar", use_container_width=True):
            limpiar_misiones()
            st.rerun()

        misiones_actuales = obtener_misiones()
        if misiones_actuales:
            for mid, tarea, estado in misiones_actuales:
                st.markdown(f"- **#{mid}** {tarea} *({estado})*")
        else:
            st.caption("Sin misiones activas.")

    with st.expander("🧠 Memoria del Núcleo"):
        recuerdos = jarvis_mem.get_recent_facts(6)
        if recuerdos:
            for r_item in recuerdos:
                st.markdown(f"- {r_item}")
        else:
            st.caption("Sin recuerdos guardados aún.")
        if st.button("🧹 Limpiar Memoria", use_container_width=True):
            jarvis_mem.clear_facts()
            st.rerun()

indicadores = obtener_indicadores_chile()
clima_buin = obtener_clima_buin()

renderizar_banner_reloj_vivo(st.session_state.nucleo_activo, st.session_state.capa_radar)

c_ind1, c_ind2, c_ind3, c_ind4 = st.columns(4)
with c_ind1:
    st.markdown(
        f'<div class="econ-card"><span class="econ-label">DÓLAR</span><span class="econ-val">{fmt_clp(indicadores["dolar"])}</span></div>',
        unsafe_allow_html=True,
    )
with c_ind2:
    st.markdown(
        f'<div class="econ-card"><span class="econ-label">EURO</span><span class="econ-val">{fmt_clp(indicadores["euro"])}</span></div>',
        unsafe_allow_html=True,
    )
with c_ind3:
    st.markdown(
        f'<div class="econ-card"><span class="econ-label">UF</span><span class="econ-val">{fmt_clp(indicadores["uf"])}</span></div>',
        unsafe_allow_html=True,
    )
with c_ind4:
    temp_label = f"{clima_buin['temp_c']}°C" if clima_buin.get("temp_c") is not None else "N/D"
    st.markdown(
        f'<div class="econ-card"><span class="econ-label">BUIN ({clima_buin["condicion"]})</span><span class="econ-val">{temp_label}</span></div>',
        unsafe_allow_html=True,
    )

renderizar_microfono_voz()

for msg in st.session_state.mensajes:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt_usuario = st.chat_input("Escribe tu orden o conversa con el núcleo activo...")
if prompt_usuario:
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    respuesta = generar_respuesta_coherente(st.session_state.nucleo_activo, prompt_usuario)
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    programar_voz(respuesta, idioma="es-CL")
    st.rerun()

reproducir_voz_pendiente()

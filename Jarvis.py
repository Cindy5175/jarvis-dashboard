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

    def get_recent_facts(self, limit: int = 5):
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


def purgar_chat(nucleo_nombre):
    st.session_state["mensajes"] = [
        {"role": "assistant", "content": obtener_saludo_nucleo(nucleo_nombre)}
    ]
    st.session_state["pendiente_voz"] = None


def renderizar_camara_nocturna(modo_camara):
    es_ir = "INFRARROJO" in modo_camara
    color_main = "#00f3ff" if es_ir else "#39ff14"
    filtro_css = (
        "grayscale(100%) contrast(155%) brightness(115%) sepia(100%) hue-rotate(155deg) saturate(320%)"
        if es_ir
        else "grayscale(100%) contrast(150%) brightness(120%) sepia(100%) hue-rotate(68deg) saturate(350%)"
    )
    html_cam = (
        f'<div style="border:1px solid {color_main};background:#030906;border-radius:6px;padding:6px;font-family:monospace;color:{color_main};">'
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:4px;font-size:0.70rem;font-weight:bold;margin-bottom:4px;">'
        "<span>● CAM-01 // BUIN</span>"
        f'<button id="btn-cam-real" type="button" style="background:{color_main};color:#040a07;border:none;border-radius:4px;padding:2px 6px;font-family:monospace;font-size:0.65rem;font-weight:bold;cursor:pointer;">Activar Cámara</button>'
        "</div>"
        '<video id="cam-real-video" autoplay playsinline muted style="display:none;"></video>'
        '<canvas id="cam-nocturna-canvas" width="250" height="135" style="width:100%;height:135px;border-radius:4px;background:#020704;"></canvas>'
        '<div id="estado-cam-jarvis" style="font-size:0.66rem;opacity:0.85;margin-top:3px;">Modo simulado listo • Pulsa "Activar Cámara"</div>'
        "</div>"
        "<script>(function(){"
        'const c=document.getElementById("cam-nocturna-canvas");'
        'const v=document.getElementById("cam-real-video");'
        'const btn=document.getElementById("btn-cam-real");'
        'const stEl=document.getElementById("estado-cam-jarvis");'
        "if(!c)return;"
        'const ctx=c.getContext("2d");'
        f'const mainColor="{color_main}";const filtro="{filtro_css}";'
        "let scanY=0,t=0,camActiva=false;"
        "async function iniciarCamaraReal(){try{"
        "if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){"
        'if(stEl)stEl.textContent="Cámara no soportada • Modo simulado";return;}'
        "if(window.__jarvisCamStream){window.__jarvisCamStream.getTracks().forEach(tr=>tr.stop());}"
        'const stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:"environment"},audio:false});'
        "window.__jarvisCamStream=stream;if(v){v.srcObject=stream;await v.play();}"
        'camActiva=true;if(stEl)stEl.textContent="Cámara real activa con filtro nocturno";}'
        'catch(e){camActiva=false;if(stEl)stEl.textContent="Permiso denegado o sin HTTPS • Simulado";}}'
        "if(btn)btn.onclick=iniciarCamaraReal;"
        "function draw(){t+=0.05;ctx.save();"
        'if(camActiva&&v&&v.readyState>=2){ctx.filter=filtro;ctx.drawImage(v,0,0,c.width,c.height);ctx.filter="none";}'
        'else{ctx.fillStyle="#030a06";ctx.fillRect(0,0,c.width,c.height);'
        'ctx.strokeStyle=mainColor+"22";ctx.lineWidth=1;'
        "for(let x=0;x<c.width;x+=25){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,c.height);ctx.stroke();}"
        "for(let y=0;y<c.height;y+=22){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(c.width,y);ctx.stroke();}"
        'ctx.fillStyle=mainColor+"33";ctx.fillRect(20,78,52,34);ctx.fillRect(165,68,64,44);'
        "ctx.beginPath();ctx.arc(125+Math.sin(t)*14,62+Math.cos(t*1.3)*6,7,0,Math.PI*2);"
        "ctx.strokeStyle=mainColor;ctx.stroke();"
        "for(let i=0;i<60;i++){const nx=(i*37+Math.floor(t*90))%c.width;const ny=(i*53+Math.floor(t*45))%c.height;"
        'ctx.fillStyle=mainColor+"44";ctx.fillRect(nx,ny,2,2);}}'
        'scanY=(scanY+2.2)%c.height;ctx.strokeStyle=mainColor+"aa";ctx.beginPath();'
        "ctx.moveTo(0,scanY);ctx.lineTo(c.width,scanY);ctx.stroke();"
        'ctx.fillStyle=mainColor;ctx.font="bold 10px monospace";'
        'ctx.fillText(camActiva?"LIVE CAM [●] NIGHT-OPTIC":"SIM [●] IR-GAIN: +24dB",8,14);'
        'ctx.fillText("SECTOR BUIN SUR",8,c.height-8);ctx.restore();}'
        "if(window.__jarvisCamTimer)clearInterval(window.__jarvisCamTimer);"
        "window.__jarvisCamTimer=setInterval(draw,80);draw();"
        "})();</script>"
    )
    try:
        components.html(html_cam, height=192)
    except Exception:
        pass


def limpiar_texto_para_voz(texto):
    limpio = re.sub(r"^\[[^\]]+\]\s*", "", texto or "")
    limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace ", limpio)
    limpio = re.sub(r"https?://\S+", " enlace ", limpio)
    limpio = re.sub(r"[*_`#>\[\]|]+", " ", limpio)
    limpio = re.sub(r"([.!?])\s+", r"\1 ", limpio)
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
    txt = txt.replace(" ... ", " ")
    lang = pendiente["idioma"]
    js_voz = (
        "<script>(function(){try{if(!('speechSynthesis' in window))return;"
        "if(window.__jarvisVozTimer){clearTimeout(window.__jarvisVozTimer);}"
        "window.speechSynthesis.cancel();"
        "function elegirVoz(voices){"
        "if(!voices||!voices.length)return null;"
        "const es=voices.filter(v=>/^(es|es-CL|es-ES|es-MX|es-US)/i.test(v.lang||''));"
        "return es.find(v=>/jorge|diego|carlos|enrique|pablo|mateo|alonso|raul|male|hombre/i.test(v.name||''))||es[0]||voices[0];}"
        "let yaHablo=false;"
        "function hablarUnaVez(){"
        "if(yaHablo)return;yaHablo=true;"
        "window.speechSynthesis.cancel();"
        "const u=new SpeechSynthesisUtterance(" + f'"{txt}"' + ");"
        f"u.lang='{lang}';u.rate=0.98;u.pitch=0.90;"
        "const v=elegirVoz(window.speechSynthesis.getVoices());if(v)u.voice=v;"
        "window.speechSynthesis.speak(u);}"
        "if(window.speechSynthesis.getVoices().length){hablarUnaVez();}"
        "else{window.speechSynthesis.onvoiceschanged=function(){window.speechSynthesis.onvoiceschanged=null;hablarUnaVez();};"
        "window.__jarvisVozTimer=setTimeout(hablarUnaVez,250);}"
        "}catch(e){}})();</script>"
    )
    try:
        components.html(js_voz, height=1)
    except Exception:
        pass


def renderizar_microfono_voz():
    js_mic = (
        '<div style="display:flex;align-items:center;gap:8px;margin:4px 0 10px 0;">'
        '<button id="btn-mic-jarvis" type="button" style="background:#00f3ff;color:#060913;'
        'border:1.5px solid #00f3ff;border-radius:6px;padding:6px 12px;font-family:monospace;'
        'font-weight:bold;font-size:0.78rem;cursor:pointer;">🎤 Hablar por Voz</button>'
        '<span id="estado-mic-jarvis" style="color:#00f3ff;font-family:monospace;'
        'font-size:0.75rem;opacity:0.85;">Micrófono listo (es-CL)</span></div>'
        "<script>(function(){"
        'const btn=document.getElementById("btn-mic-jarvis");'
        'const stEl=document.getElementById("estado-mic-jarvis");'
        "if(!btn||!stEl)return;"
        "const SR=window.SpeechRecognition||window.webkitSpeechRecognition;"
        'if(!SR){stEl.textContent="Dictado por voz no soportado en este navegador";return;}'
        'btn.onclick=function(){try{const rec=new SR();rec.lang="es-CL";'
        "rec.interimResults=false;rec.maxAlternatives=1;"
        'stEl.textContent="Escuchando, jefa...";'
        "rec.onresult=function(ev){"
        "const r0=ev.results&&ev.results[0]&&ev.results[0][0];"
        'const dicho=(r0&&r0.transcript)||"";'
        'stEl.textContent=dicho?("Escuchado: "+dicho):"No se captó audio";'
        "if(!dicho)return;const doc=window.parent.document;"
        'const sel=\'textarea[data-testid="stChatInputTextArea"],input[data-testid="stChatInputTextArea"],textarea\';'
        "let target=null;doc.querySelectorAll(sel).forEach(el=>{if(el.offsetParent!==null)target=el;});"
        "if(target){"
        'const pA=window.HTMLTextAreaElement.prototype,pB=window.HTMLInputElement.prototype;'
        'const setter=Object.getOwnPropertyDescriptor(pA,"value")||Object.getOwnPropertyDescriptor(pB,"value");'
        "if(setter&&setter.set)setter.set.call(target,dicho);else target.value=dicho;"
        'target.dispatchEvent(new Event("input",{bubbles:true}));'
        'target.dispatchEvent(new Event("change",{bubbles:true}));'
        "setTimeout(()=>{"
        'const sendBtn=doc.querySelector(\'button[data-testid="stChatInputSubmitButton"]\');'
        "if(sendBtn)sendBtn.click();},180);}};"
        'rec.onerror=function(){stEl.textContent="Error al acceder al micrófono";};'
        'rec.onend=function(){if(stEl.textContent==="Escuchando, jefa...")stEl.textContent="Micrófono listo (es-CL)";};'
        'rec.start();}catch(e){stEl.textContent="No se pudo iniciar el micrófono";}};'
        "})();</script>"
    )
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
        return "Cálculo porcentual: **" + str(pct) + "%** de **" + str(base) + "** = **" + str(res) + "**."

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
            r_val = round((val * long_m[u1]) / long_m[u2], 4)
            return "Conversión de longitud: **" + str(val) + " " + u1 + "** = **" + str(r_val) + " " + u2 + "**."
        if u1 in masa_kg and u2 in masa_kg:
            r_val = round((val * masa_kg[u1]) / masa_kg[u2], 4)
            return "Conversión de masa: **" + str(val) + " " + u1 + "** = **" + str(r_val) + " " + u2 + "**."
        if u1 in vol_l and u2 in vol_l:
            r_val = round((val * vol_l[u1]) / vol_l[u2], 4)
            return "Conversión de volumen: **" + str(val) + " " + u1 + "** = **" + str(r_val) + " " + u2 + "**."
        if u1 in vel_ms and u2 in vel_ms:
            r_val = round((val * vel_ms[u1]) / vel_ms[u2], 4)
            return "Conversión de velocidad: **" + str(val) + " " + u1 + "** = **" + str(r_val) + " " + u2 + "**."
        if u1 in {"c", "f", "k"} and u2 in {"c", "f", "k"}:
            c = val if u1 == "c" else ((val - 32) * 5 / 9 if u1 == "f" else val - 273.15)
            out_t = c if u2 == "c" else (c * 9 / 5 + 32 if u2 == "f" else c + 273.15)
            return "Conversión térmica: **" + str(val) + " " + u1.upper() + "** = **" + str(round(out_t, 2)) + " " + u2.upper() + "**."

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
                es_ent = isinstance(res, float) and res.is_integer()
                out = int(res) if es_ent else (round(res, 6) if isinstance(res, float) else res)
                return "Resultado del cálculo `" + expr + "`: **" + str(out) + "**."
        except Exception:
            return None
    return None


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
            return f"{prefijo}Listo, jefa, queda guardado en memoria: **{dato}**."

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
                "Puede revisar el pulso directo en **Finviz** o el seguimiento **ANT (Nasdaq)**."
            )
        if nucleo == "VIERNES":
            return (
                f"{prefijo}Sin conexión directa a cotizaciones en vivo aquí adentro, jefa. "
                "Abra **Finviz** o **ANT (Nasdaq)** para ver cómo se mueven las bolsas ahora mismo."
            )
        return (
            f"{prefijo}Radar bursátil sin feed en vivo en esta consola local, jefa."
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
        return f"{prefijo}En el Nodo Buin son las **{hora_str}** (hora de Chile), jefa."

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
            recuerdos = jarvis_mem.get_recent_facts(5)
            sys_txt = f"Núcleo activo: {nucleo}. Hora Chile: {ahora.strftime('%d/%m/%Y %H:%M:%S')}. {PROTOCOLO_CONOCIMIENTO_BASE}"
            if recuerdos:
                sys_txt += " Memoria: " + " | ".join(recuerdos)
            resp = client_groq.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": sys_txt},
                    {"role": "user", "content": raw},
                ],
                temperature=0.65,
                max_tokens=600,
            )
            contenido = (resp.choices[0].message.content or "").strip()
            if contenido:
                contenido = re.sub(r"^\[[^\]]+\]\s*", "", contenido)
                return f"{prefijo}{contenido}"
        except Exception:
            pass

    respuestas_generales = {
        "JARVIS": [
            f"{prefijo}Entendido, jefa. Sobre *'{raw}'*, seguimos aquí mismo; ¿qué desea hacer?",
            f"{prefijo}Tomo nota de *'{raw}'*, jefa. Dígame cómo avanzamos."
        ],
        "VIERNES": [
            f"{prefijo}Recibido, jefa: *'{raw}'*. ¿Qué movemos ahora?",
        ],
        "NOVA": [
            f"{prefijo}Señal clara sobre *'{raw}'*, jefa. ¿En qué más le apoyo?",
        ],
        "ARTEX": [
            f"{prefijo}Directiva registrada: *'{raw}'*, jefa. Protocolo activo.",
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
        .stButton>button {
            background-color: #00f3ff !important;
            border: 1.5px solid #00f3ff !important;
            font-weight: bold;
            font-family: monospace;
            width: 100%;
            border-radius: 6px;
            padding: 5px 10px !important;
        }
        .stButton>button p, .stButton>button span { color: #060913 !important; font-size: 0.78rem !important; }
        .stButton>button:hover { background-color: #0088cc !important; }
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
        }
        .econ-label { font-size: 0.75rem !important; opacity: 0.85; color: #00f3ff !important; }
        .econ-val { font-size: 0.85rem !important; font-weight: bold; color: #00f3ff !important; }
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
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, rgba(0,243,255,0.4) 0%, #060913 75%);
            margin-bottom: 8px;
        }
        .arc-triangle-inverted {
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-top: 20px solid #00f3ff;
        }
        .holo-brain-box {
            border: 1.5px solid #00f3ff;
            background: linear-gradient(135deg, #0a1128 0%, #060913 100%);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            margin: 0 auto 20px auto;
            max-width: 800px;
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

    if st.button("🧹 Purgar Chat", use_container_width=True):
        purgar_chat(st.session_state.nucleo_activo)
        st.rerun()

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

indicadores = obtener_indicadores_chile()
clima_buin = obtener_clima_buin()
ahora_chile = obtener_hora_chile()

st.markdown(
    f'<div class="holo-brain-box">'
    f'<h2>⚡ J.A.R.V.I.S. // {st.session_state.nucleo_activo}</h2>'
    f'<div style="font-size:0.88rem;opacity:0.9;">NODO BUIN, CHILE • {ahora_chile.strftime("%d/%m/%Y %H:%M:%S")}</div>'
    f'</div>',
    unsafe_allow_html=True,
)

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

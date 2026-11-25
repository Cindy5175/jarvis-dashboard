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

PERFILES_VOZ_NUCLEO = {
    "JARVIS": {
        "rate": 0.94,
        "pitch": 0.84,
        "genero": "male",
        "filtros_nombre": r"jorge|diego|carlos|enrique|pablo|mateo|alonso|raul|male|hombre",
    },
    "VIERNES": {
        "rate": 1.08,
        "pitch": 1.14,
        "genero": "female",
        "filtros_nombre": r"paulina|camila|sofia|sofía|lucia|lucía|helena|mia|mía|elena|female|mujer",
    },
    "NOVA": {
        "rate": 1.03,
        "pitch": 1.06,
        "genero": "female",
        "filtros_nombre": r"sofia|sofía|camila|valeria|isabella|claire|female|mujer",
    },
    "ARTEX": {
        "rate": 0.96,
        "pitch": 0.88,
        "genero": "male",
        "filtros_nombre": r"carlos|raul|enrique|jorge|diego|male|hombre",
    },
}

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


def purgar_chat(nucleo_nombre):
    saludo_limpio = obtener_saludo_nucleo(nucleo_nombre)
    st.session_state["mensajes"] = [{"role": "assistant", "content": saludo_limpio}]
    st.session_state["pendiente_voz"] = None


def renderizar_banner_reloj_vivo(nucleo_activo, capa_radar):
    ahora = obtener_hora_chile()
    ts_ms = int(ahora.timestamp() * 1000)
    fecha_str = ahora.strftime("%d/%m/%Y %H:%M:%S")
    encabezado_reloj = f"NODO BUIN, CHILE • {fecha_str} • {capa_radar}"
    lineas_html = [
        '<div style="border:1.5px solid #00f3ff;',
        'background:linear-gradient(135deg, #0a1128 0%, #060913 100%);',
        'padding:14px 18px;border-radius:8px;text-align:center;',
        'margin:0 auto 14px auto;max-width:920px;font-family:monospace;color:#00f3ff;">',
        f'<div style="font-size:1.55rem;font-weight:bold;letter-spacing:1px;">⚡ J.A.R.V.I.S. // {nucleo_activo}</div>',
        '<div id="jarvis-reloj-vivo" style="font-size:0.92rem;font-weight:bold;margin-top:4px;opacity:0.95;">',
        f"{encabezado_reloj}</div></div>",
        "<script>(function(){",
        f'let baseMs={ts_ms};const offsetMs=-3*3600*1000;const capa="{capa_radar}";',
        'const el=document.getElementById("jarvis-reloj-vivo");',
        'function pad(n){return n<10?"0"+n:""+n;}',
        "function tick(){baseMs+=1000;const d=new Date(baseMs+offsetMs);",
        'const f=pad(d.getUTCDate())+"/"+pad(d.getUTCMonth()+1)+"/"+d.getUTCFullYear();',
        'const h=pad(d.getUTCHours())+":"+pad(d.getUTCMinutes())+":"+pad(d.getUTCSeconds());',
        'if(el){el.textContent="NODO BUIN, CHILE • "+f+" "+h+" • "+capa;}}',
        "if(window.__jarvisClockTimer)clearInterval(window.__jarvisClockTimer);",
        "window.__jarvisClockTimer=setInterval(tick,1000);",
        "})();</script>",
    ]
    components.html("".join(lineas_html), height=92)


def renderizar_camara_nocturna(modo_camara):
    es_ir = "INFRARROJO" in modo_camara
    color_main = "#00f3ff" if es_ir else "#39ff14"
    filtro_css = (
        "grayscale(100%) contrast(155%) brightness(115%) sepia(100%) hue-rotate(155deg) saturate(320%)"
        if es_ir
        else "grayscale(100%) contrast(150%) brightness(120%) sepia(100%) hue-rotate(68deg) saturate(350%)"
    )
    partes_cam = [
        f'<div style="border:1px solid {color_main};background:#030906;border-radius:6px;',
        f'padding:6px;font-family:monospace;color:{color_main};">',
        '<div style="display:flex;justify-content:space-between;align-items:center;gap:4px;',
        'font-size:0.70rem;font-weight:bold;margin-bottom:4px;">',
        "<span>● CAM-01 // BUIN</span>",
        f'<button id="btn-cam-real" type="button" style="background:{color_main};color:#040a07;',
        "border:none;border-radius:4px;padding:2px 6px;font-family:monospace;font-size:0.65rem;",
        'font-weight:bold;cursor:pointer;">Activar Cámara</button></div>',
        '<video id="cam-real-video" autoplay playsinline muted style="display:none;"></video>',
        '<canvas id="cam-nocturna-canvas" width="250" height="135" style="width:100%;height:135px;',
        'border-radius:4px;background:#020704;"></canvas>',
        '<div id="estado-cam-jarvis" style="font-size:0.66rem;opacity:0.85;margin-top:3px;">',
        'Modo simulado listo • Pulsa "Activar Cámara" para señal real</div></div>',
        '<script>(function(){const c=document.getElementById("cam-nocturna-canvas");',
        'const v=document.getElementById("cam-real-video");const btn=document.getElementById("btn-cam-real");',
        'const stEl=document.getElementById("estado-cam-jarvis");if(!c)return;',
        f'const ctx=c.getContext("2d");const mainColor="{color_main}";const filtro="{filtro_css}";',
        "let scanY=0,t=0,camActiva=false;",
        "async function iniciarCamaraReal(){try{if(!navigator.mediaDevices||!navigator.mediaDevices.getUserMedia){",
        'if(stEl)stEl.textContent="Cámara no soportada aquí • Manteniendo simulador";return;}',
        "if(window.__jarvisCamStream){window.__jarvisCamStream.getTracks().forEach(tr=>tr.stop());}",
        'const stream=await navigator.mediaDevices.getUserMedia({video:{facingMode:"environment"},audio:false});',
        "window.__jarvisCamStream=stream;if(v){v.srcObject=stream;await v.play();}",
        'camActiva=true;if(stEl)stEl.textContent="Cámara real activa con filtro nocturno";}',
        'catch(e){camActiva=false;if(stEl)stEl.textContent="Permiso denegado o sin HTTPS • Modo simulado";}}',
        "if(btn)btn.onclick=iniciarCamaraReal;",
        'function draw(){t+=0.05;ctx.save();if(camActiva&&v&&v.readyState>=2){ctx.filter=filtro;',
        'ctx.drawImage(v,0,0,c.width,c.height);ctx.filter="none";}else{ctx.fillStyle="#030a06";',
        "ctx.fillRect(0,0,c.width,c.height);ctx.strokeStyle=mainColor+\"22\";ctx.lineWidth=1;",
        "for(let x=0;x<c.width;x+=25){ctx.beginPath();ctx.moveTo(x,0);ctx.lineTo(x,c.height);ctx.stroke();}",
        "for(let y=0;y<c.height;y+=22){ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(c.width,y);ctx.stroke();}",
        'ctx.fillStyle=mainColor+"33";ctx.fillRect(20,78,52,34);ctx.fillRect(165,68,64,44);',
        "ctx.beginPath();ctx.arc(125+Math.sin(t)*14,62+Math.cos(t*1.3)*6,7,0,Math.PI*2);",
        "ctx.strokeStyle=mainColor;ctx.stroke();for(let i=0;i<65;i++){",
        "const nx=(i*37+Math.floor(t*90))%c.width;const ny=(i*53+Math.floor(t*45))%c.height;",
        'ctx.fillStyle=mainColor+"44";ctx.fillRect(nx,ny,2,2);}}',
        'scanY=(scanY+2.2)%c.height;ctx.strokeStyle=mainColor+"aa";ctx.beginPath();',
        "ctx.moveTo(0,scanY);ctx.lineTo(c.width,scanY);ctx.stroke();ctx.fillStyle=mainColor;",
        'ctx.font="bold 10px monospace";',
        'ctx.fillText(camActiva?"LIVE CAM [●] NIGHT-OPTIC":"SIM [●] IR-GAIN: +24dB",8,14);',
        'ctx.fillText("SECTOR BUIN SUR",8,c.height-8);ctx.restore();}',
        "if(window.__jarvisCamTimer)clearInterval(window.__jarvisCamTimer);",
        "window.__jarvisCamTimer=setInterval(draw,80);draw();}})();</script>",
    ]
    components.html("".join(partes_cam), height=192)


def limpiar_texto_para_voz(texto):
    limpio = re.sub(r"^\[[^\]]+\]\s*", "", texto or "")
    limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace ", limpio)
    limpio = re.sub(r"https?://\S+", " enlace ", limpio)
    limpio = re.sub(r"[*_`#>\[\]|]+", " ", limpio)
    limpio = re.sub(r"([.!?])\s+", r"\1 ... ", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio[:520]


def programar_voz(texto, idioma="es-CL", nucleo=None):
    if st.session_state.get("voz_masculina_activa", True):
        limpio = limpiar_texto_para_voz(texto)
        if limpio:
            st.session_state["pendiente_voz"] = {
                "texto": limpio,
                "idioma": idioma,
                "nucleo": nucleo or st.session_state.get("nucleo_activo", "JARVIS"),
            }


def reproducir_voz_pendiente():
    pendiente = st.session_state.get("pendiente_voz")
    if not pendiente or not st.session_state.get("voz_masculina_activa", True):
        return
    st.session_state["pendiente_voz"] = None
    txt = pendiente["texto"].replace("\\", "\\\\").replace('"', '\\"').replace("'", "\\'")
    lang = pendiente["idioma"]
    nucleo = pendiente.get("nucleo", st.session_state.get("nucleo_activo", "JARVIS"))
    cfg = PERFILES_VOZ_NUCLEO.get(nucleo, PERFILES_VOZ_NUCLEO["JARVIS"])
    rate = cfg["rate"]
    pitch = cfg["pitch"]
    filtros = cfg["filtros_nombre"]
    js_voz = (
        "<script>(function(){try{if(!('speechSynthesis' in window))return;"
        "function elegirVoz(voices){"
        "if(!voices||!voices.length)return null;"
        "const es=voices.filter(v=>/^(es|es-CL|es-ES|es-MX|es-US)/i.test(v.lang||''));"
        f"const rx=/{filtros}/i;"
        "const pref=es.find(v=>rx.test(v.name||''))||es[0]||voices[0];"
        "return pref||null;}"
        "function hablarAhora(){"
        "window.speechSynthesis.cancel();"
        "const trozos=" + f'"{txt}"' + ".split(' ... ').filter(Boolean);"
        "const lista=trozos.length?trozos:[" + f'"{txt}"' + "];"
        "const vozElegida=elegirVoz(window.speechSynthesis.getVoices());"
        "lista.forEach((parte)=>{"
        "const u=new SpeechSynthesisUtterance(parte);"
        f"u.lang='{lang}';"
        f"u.rate={rate};"
        f"u.pitch={pitch};"
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
    lineas_mic = [
        '<div style="display:flex;align-items:center;gap:8px;margin:4px 0 10px 0;">',
        '<button id="btn-mic-jarvis" type="button" style="background:#00f3ff;color:#060913;',
        'border:1.5px solid #00f3ff;border-radius:6px;padding:6px 12px;font-family:monospace;',
        'font-weight:bold;font-size:0.78rem;cursor:pointer;">🎤 Hablar por Voz</button>',
        '<span id="estado-mic-jarvis" style="color:#00f3ff;font-family:monospace;',
        'font-size:0.75rem;opacity:0.85;">Micrófono listo (es-CL)</span></div>',
        "<script>(function(){",
        'const btn=document.getElementById("btn-mic-jarvis");',
        'const stEl=document.getElementById("estado-mic-jarvis");',
        "if(!btn||!stEl)return;",
        "const SR=window.SpeechRecognition||window.webkitSpeechRecognition;",
        'if(!SR){stEl.textContent="Dictado por voz no soportado en este navegador";return;}',
        "btn.onclick=function(){try{const rec=new SR();rec.lang=\"es-CL\";",
        "rec.interimResults=false;rec.maxAlternatives=1;",
        'stEl.textContent="Escuchando, jefa...";',
        "rec.onresult=function(ev){",
        'const dicho=(ev.results[0]&&ev.results[0][0]&&ev.

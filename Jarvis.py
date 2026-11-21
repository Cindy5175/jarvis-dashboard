import datetime
import math
import os
import platform
import random
import re
import sqlite3
import urllib.parse
import requests
import streamlit as st
import streamlit.components.v1 as components

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

st.set_page_config(
    page_title="J.A.R.V.I.S. // IA - NUCLEO TACTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "nucleo_activo" not in st.session_state:
    st.session_state.nucleo_activo = "JARVIS"

if "voz_masculina_activa" not in st.session_state:
    st.session_state.voz_masculina_activa = True

if "escucha_continua_activa" not in st.session_state:
    st.session_state.escucha_continua_activa = True

if "pendiente_voz" not in st.session_state:
    st.session_state.pendiente_voz = None

if "modo_medico" not in st.session_state:
    st.session_state.modo_medico = False

if "ollama_activo" not in st.session_state:
    st.session_state.ollama_activo = False

if "ollama_url" not in st.session_state:
    st.session_state.ollama_url = "http://localhost:11434"

if "ollama_modelo" not in st.session_state:
    st.session_state.ollama_modelo = "llama3.2"

PIN_SECRETO = "2805"
DB_PATH = "jarvis_misiones.db"

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
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
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
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def remember_fact(self, key_id: str, fact_text: str, category: str = "general"):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
                (key_id, fact_text, category)
            )
            conn.commit()
            conn.close()
        except Exception:
            pass

    def recent_facts(self, limit: int = 5):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=5)
            cursor = conn.cursor()
            cursor.execute("SELECT fact_text FROM memory ORDER BY key_id DESC LIMIT ?", (limit,))
            rows = [r[0] for r in cursor.fetchall() if r and r[0]]
            conn.close()
            return rows
        except Exception:
            return []


jarvis_mem = JarvisMemory()


def agregar_mision(tarea):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
        conn.commit()
        conn.close()
    except Exception:
        pass


def obtener_misiones():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
        cursor = conn.cursor()
        cursor.execute("SELECT id, tarea, estado FROM misiones")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except Exception:
        return []


def limpiar_misiones():
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5)
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
        "Accept": "application/json"
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
                        "respaldo": False
                    }
        except Exception:
            pass

    return {
        "dolar": 950.00,
        "euro": 1030.00,
        "uf": 38000.00,
        "utm": 67000.00,
        "ok": True,
        "respaldo": True
    }


tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
hora_actual = now_chile.hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"


def obtener_saludo_nucleo(nucleo_nombre):
    pref = f"[{nucleo_nombre}] "
    saludos = {
        "JARVIS": f"{pref}{saludo_actual}, jefa. Qué milagro que pase a saludar; los servidores ya empezaban a extrañar sus órdenes.",
        "VIERNES": f"{pref}¡{saludo_actual}, jefa! Lista para mover ficha. ¿Qué encendemos hoy?",
        "NOVA": f"{pref}¡{saludo_actual}, jefa! Señal recibida desde el Nodo Buin. ¿Qué galaxia o tarea conquistamos ahora?"
    }
    return saludos.get(nucleo_nombre, f"{pref}{saludo_actual}, jefa. En línea y a su servicio.")


def quiere_ingles(texto: str) -> bool:
    t = (texto or "").lower()
    pistas = [
        "en inglés", "en ingles", "responde en inglés", "responde en ingles",
        "habla en inglés", "habla en ingles", "in english", "speak english",
        "reply in english", "answer in english"
    ]
    return any(p in t for p in pistas)


def limpiar_texto_voz(texto: str) -> str:
    if not texto:
        return ""
    limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace ", texto)
    limpio = re.sub(r"https?://\S+", " enlace ", limpio)
    limpio = re.sub(r"[*_`#>\[\]]+", "", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio[:450]


def programar_voz(texto: str, idioma: str = "es-CL"):
    if st.session_state.get("voz_masculina_activa", True):
        st.session_state["pendiente_voz"] = {"texto": texto, "idioma": idioma}


def reproducir_voz_pendiente():
    pendiente = st.session_state.get("pendiente_voz")
    if not pendiente or not st.session_state.get("voz_masculina_activa", True):
        return
    st.session_state["pendiente_voz"] = None
    texto = pendiente.get("texto", "")
    idioma = pendiente.get("idioma", "es-CL")
    limpio = limpiar_texto_voz(texto)
    if not limpio:
        return
    escapado = (
        limpio.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("'", "\\'")
        .replace("\n", " ")
    )
    js_voz = (
        "<script>(function(){try{if(!('speechSynthesis' in window))return;"
        "function hablar(){try{window.speechSynthesis.cancel();"
        f"const u=new SpeechSynthesisUtterance('{escapado}');"
        f"u.lang='{idioma}';u.rate=1.02;u.pitch=0.84;"
        "const vs=window.speechSynthesis.getVoices()||[];"
        f"const prefLang='{idioma}'.slice(0,2);"
        "const v=vs.find(x=>((x.lang||'').toLowerCase().startsWith(prefLang)&&!/sabina|helena|zira|hazel|lucia|lucía|sofia|sofía|female|mujer/.test((x.name||'').toLowerCase())))||vs.find(x=>(x.lang||'').toLowerCase().startsWith(prefLang));"
        "if(v)u.voice=v;window.speechSynthesis.speak(u);}catch(e){}}"
        "if(window.speechSynthesis.getVoices().length>0){setTimeout(hablar,120);}"
        "else{window.speechSynthesis.onvoiceschanged=function(){setTimeout(hablar,120);};setTimeout(hablar,350);}"
        "}catch(e){}})();</script>"
    )
    components.html(js_voz, height=0)


def escucha_continua_js(activa: bool):
    if not activa:
        return
    js_sr = (
        "<script>(function(){try{"
        "const SR=window.SpeechRecognition||window.webkitSpeechRecognition;"
        "if(!SR||window.__jarvisSrActive)return;"
        "const r=new SR();r.lang='es-CL';r.continuous=true;r.interimResults=false;"
        "window.__jarvisSrActive=true;"
        "r.onresult=function(ev){const i=ev.results.length-1;if(i>=0&&ev.results[i][0]){"
        "const d=(ev.results[i][0].transcript||'').trim();"
        "if(d){const el=window.parent.document.getElementById('jarvis-ultima-voz');"
        "if(el)el.innerText='Última voz: '+d;}}};"
        "r.onerror=function(){window.__jarvisSrActive=false;};"
        "r.onend=function(){window.__jarvisSrActive=false;try{r.start();window.__jarvisSrActive=true;}catch(e){}};"
        "r.start();}catch(e){}})();</script>"
    )
    components.html(js_sr, height=0)


def evaluar_calculo_seguro(texto_raw: str):
    limpio = texto_raw.strip().lower()
    for pref in ["calcula", "calcular", "cuanto es", "cuánto es", "resuelve", "matemática", "matematica", "="]:
        if limpio.startswith(pref):
            limpio = limpio[len(pref):].strip()
    limpio = limpio.replace("×", "*").replace("·", "*").replace("÷", "/").replace("^", "**")
    if not limpio or not re.search(r"\d", limpio):
        return None
    if re.fullmatch(r"\d{1,2}:\d{2}(:\d{2})?", limpio):
        return None
    if not re.fullmatch(r"[0-9+\-*/().%\s,a-z_]+", limpio):
        return None
    entorno = {
        "__builtins__": {},
        "abs": abs, "round": round, "min": min, "max": max, "pow": pow,
        "sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan,
        "log": math.log10, "ln": math.log, "exp": math.exp, "pi": math.pi, "e": math.e,
    }
    try:
        res = eval(limpio, entorno, {})
        if isinstance(res, (int, float)) and not isinstance(res, bool):
            if isinstance(res, float) and res.is_integer():
                res = int(res)
            elif isinstance(res, float):
                res = round(res, 6)
            return f"Resultado del cálculo `{limpio}`: **{res}**."
    except Exception:
        return None
    return None


def convertir_unidades_texto(t: str):
    m = re.search(r"(-?\d+(?:[.,]\d+)?)\s*(km|m|cm|mm|mi|millas|kg|g|lb|libras|c|°c|f|°f|k)\s*(?:a|en|to|in)\s*(km|m|cm|mm|mi|millas|kg|g|lb|libras|c|°c|f|°f|k)", t)
    if not m:
        return None
    val = float(m.group(1).replace(",", "."))
    u1 = m.group(2).replace("°", "")
    u2 = m.group(3).replace("°", "")
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

    if u1 in long_m and u2 in long_m:
        out = (val * long_m[u1]) / long_m[u2]
        return f"Conversión: **{val:g} {u1}** = **{round(out, 4):g} {u2}**."
    if u1 in masa_kg and u2 in masa_kg:
        out = (val * masa_kg[u1]) / masa_kg[u2]
        return f"Conversión: **{val:g} {u1}** = **{round(out, 4):g} {u2}**."

    temp_units = {"c", "f", "k"}
    if u1 in temp_units and u2 in temp_units:
        if u1 == "c":
            c = val
        elif u1 == "f":
            c = (val - 32) * 5 / 9
        else:
            c = val - 273.15
        if u2 == "c":
            out = c
        elif u2 == "f":
            out = c * 9 / 5 + 32
        else:
            out = c + 273.15
        return f"Conversión térmica: **{val:g} {u1.upper()}** = **{round(out, 2):g} {u2.upper()}**."

    return None


def resumen_sistema_y_seguridad():
    os_info = f"{platform.system()} {platform.release()}"
    db_existe = os.path.exists(DB_PATH)
    misiones_cant = len(obtener_misiones())
    mem_cant = len(jarvis_mem.recent_facts(50))
    cpu_txt = "N/D"
    ram_txt = "N/D"
    if PSUTIL_AVAILABLE:
        try:
            cpu_txt = f"{psutil.cpu_percent(interval=0.2)}%"
            ram_txt = f"{psutil.virtual_memory().percent}%"
        except Exception:
            pass
    sospechosos = [
        f for f in os.listdir(".")
        if os.path.isfile(f) and any(f.lower().endswith(ext) for ext in [".exe", ".bat", ".cmd", ".vbs", ".ps1", ".scr"])
    ]
    estado_vir = "Sin ejecutables sospechosos en el directorio de trabajo." if not sospechosos else f"Archivos ejecutables detectados en raíz: {', '.join(sospechosos[:5])}."
    return (
        f"Diagnóstico & Seguridad ({os_info}): CPU **{cpu_txt}**, RAM **{ram_txt}**, "
        f"SQLite `{DB_PATH}` ({'OK' if db_existe else 'nuevo'}), **{misiones_cant}** misiones y **{mem_cant}** memorias recientes. "
        f"Revisión rápida: {estado_vir} "
        "Optimización sugerida: purgar historial extenso del chat, limpiar misiones completadas y cerrar pestañas pesadas."
    )


def estilizar_por_nucleo(nucleo: str, nucleo_content: str, raw_user: str) -> str:
    pref = f"[{nucleo}] "
    if nucleo == "JARVIS":
        return f"{pref}{nucleo_content} Como siempre, jefa, un detalle técnico más dominado sin despeinarnos."
    if nucleo == "VIERNES":
        return f"{pref}{nucleo_content} ¿Listo para el siguiente paso, jefa?"
    return f"{pref}{nucleo_content} Datos alineados desde el Nodo Buin para '{raw_user.strip()}', jefa."


def responder_conocimiento_base(t: str, raw: str):
    if "pesa el corazón" in t or "pesa el corazon" in t or "peso del corazón" in t or "peso del corazon" in t:
        return (
            "En un adulto sano, el corazón suele pesar entre **250 y 350 gramos** "
            "(algo menor en promedio en mujeres y mayor en hombres, según masa corporal y contextura). "
            "Dato general anatómico, no diagnóstico médico."
        )

    if "mosca" in t and ("patas" in t or "cuantas" in t or "cuántas" in t):
        return "Una mosca tiene **6 patas** (tres pares articulados), como corresponde a todo insecto."

    conv = convertir_unidades_texto(t)
    if conv:
        return conv

    calculo = evaluar_calculo_seguro(raw)
    if calculo:
        return calculo

    if any(k in t for k in ["virus", "malware", "seguridad", "optimizar", "optimización", "optimizacion", "rendimiento", "diagnóstico", "diagnostico"]):
        return resumen_sistema_y_seguridad()

    if any(k in t for k in ["llamar", "llamada", "mensaje", "enviar mensaje", "whatsapp", "correo"]):
        return (
            "Módulo de **Llamadas y Mensajes**: puedes redactar el texto o número en el panel lateral de "
            "**Modos & Utilidades Tácticas** para generar el enlace directo (`tel:` / `wa.me` / `mailto:`) sin salir de tu flujo."
        )

    if st.session_state.get("modo_medico", False) or any(k in t for k in ["síntoma", "sintoma", "dolor", "fiebre", "presión", "presion", "pulso", "medicina", "médico", "medico", "salud"]):
        return (
            "**Modo Médico (orientación general)**: para evaluar cualquier síntoma o parámetro clínico, "
            "indica edad, intensidad, duración y signos de alarma. Esto es información general y no sustituye una evaluación médica presencial."
        )

    if any(k in t for k in ["matemática", "matematica", "cálculo", "calculo", "álgebra", "algebra", "geometría", "geometria", "derivada", "integral"]):
        return (
            "En **matemática y cálculo**, modelamos cantidades, relaciones, tasas de cambio (derivadas) y acumulaciones (integrales). "
            "Si me das una expresión numérica o conversión (como `10 km a mi` o `sqrt(144)`), la resuelvo directo."
        )

    if any(k in t for k in ["historia de la medicina", "historia medicina", "hipócrates", "hipocrates", "galeno", "antibiótico", "antibiotico", "penicilina", "vacuna", "pasteur", "fleming"]):
        return (
            "En **historia de la medicina**, se pasa de explicaciones mágicas o humorales (Hipócrates, Galeno) a la anatomía "
            "científica (Vesalio), la teoría microbiana (Pasteur, Koch), la antisepsia, las vacunas y los antibióticos "
            "(como la penicilina de Fleming) hasta la medicina molecular moderna."
        )

    if any(k in t for k in ["biología", "biologia", "adn", "arn", "célula", "celula", "genética", "genetica", "evolución", "evolucion", "mitosis", "fotosíntesis", "fotosintesis"]):
        return (
            "En **biología**, la célula es la unidad básica de la vida; el **ADN** almacena la información genética, "
            "el **ARN** participa en la expresión génica y procesos como la respiración celular o la fotosíntesis sostienen la energía biológica."
        )

    if any(k in t for k in ["ciencia", "ciencias", "física", "fisica", "química", "quimica", "termodinámica", "termodinamica", "cuántica", "cuantica", "astronomía", "astronomia", "gravedad", "luz", "átomo", "atomo"]):
        return (
            "En **ciencias**, se estudian las leyes y fenómenos del universo mediante observación, hipótesis, experimentación y modelos matemáticos: "
            "física, química, astronomía, termodinámica y mecánica cuántica."
        )

    if any(k in t for k in ["tecnología", "tecnologia", "programación", "programacion", "algoritmo", "inteligencia artificial", "ia", "red", "redes", "ciberseguridad", "base de datos", "sqlite", "python", "cloud", "nube", "ollama"]):
        return (
            "En **tecnología**, se integran hardware, software, redes, datos e inteligencia artificial —incluyendo ejecución local sin internet vía **Ollama**— "
            "para construir sistemas confiables, rápidos, seguros y escalables."
        )

    if any(k in t for k in ["historia", "histórico", "historico", "antigüedad", "antiguedad", "edad media", "revolución", "revolucion", "guerra mundial", "independencia", "imperio", "civilización", "civilizacion", "chile"]):
        return (
            "En **historia**, se interpretan los procesos del pasado analizando fuentes, cronología y causas políticas, económicas, "
            "sociales y culturales desde la Antigüedad hasta la era contemporánea."
        )

    return None


def responder_pregunta_general_local(nucleo: str, texto_usuario: str, en_ingles: bool = False) -> str:
    limpio = texto_usuario.strip()
    if en_ingles:
        cuerpo = (
            f"Regarding '{limpio}', I am running in local/offline-ready mode. "
            "I can handle math conversions, system/security diagnostics, medical info, science, technology, "
            "medical history, biology, and history, or save this as a mission."
        )
        return f"[{nucleo}] {cuerpo}"

    t = limpio.lower()
    if any(p in t for p in ["qué es", "que es", "quién fue", "quien fue", "quién es", "quien es", "cómo funciona", "como funciona", "por qué", "por que", "cuándo", "cuando", "dónde", "donde", "?"]):
        cuerpo = (
            f"Para tu consulta sobre **{limpio}**, puedo darte una respuesta directa en conversiones, diagnóstico/seguridad, "
            "modo médico, ciencias, tecnología, historia de la medicina, matemática y cálculo, biología e historia; "
            "si buscas un dato específico adicional, indícalo o regístralo como misión."
        )
        return estilizar_por_nucleo(nucleo, cuerpo, limpio)

    cuerpo = (
        f"He registrado tu consulta sobre **{limpio}**. Puedo asistirte con conversiones, revisión de seguridad/optimización, "
        "modo médico, ciencias, tecnología, historia de la medicina, matemática y cálculo, biología e historia."
    )
    return estilizar_por_nucleo(nucleo, cuerpo, limpio)


def consultar_ollama_local(nucleo: str, texto_usuario: str, idioma_voz: str) -> str:
    if not st.session_state.get("ollama_activo", False):
        return ""
    base_url = (st.session_state.get("ollama_url") or "http://localhost:11434").rstrip("/")
    modelo = (st.session_state.get("ollama_modelo") or "llama3.2").strip()
    idioma_rule = "Respond in English." if idioma_voz == "en-US" else "Responde en español."
    system_prompt = (
        f"Eres {nucleo}, asistente táctico en el Nodo Buin. Tratas a la usuaria de 'jefa'. "
        f"Domina conversiones, seguridad/optimización, medicina, ciencias, tecnología e historia. {idioma_rule}"
    )
    try:
        resp = requests.post(
            f"{base_url}/api/chat",
            json={
                "model": modelo,
                "stream": False,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": texto_usuario}
                ]
            },
            timeout=12
        )
        if resp.status_code == 200:
            data = resp.json()
            msg = ((data.get("message") or {}).get("content") or "").strip()
            if msg:
                return f"[{nucleo} · Ollama] {msg}"
    except Exception:
        return ""
    return ""


def consultar_modelo_externo(nucleo: str, texto_usuario: str, idioma_voz: str) -> str:
    ollama_resp = consultar_ollama_local(nucleo, texto_usuario, idioma_voz)
    if ollama_resp:
        return ollama_resp

    if not client_groq:
        return ""
    rec_mem = "; ".join(jarvis_mem.recent_facts(5))
    estilo_nucleo = {
        "JARVIS": "Eres JARVIS, elegante, preciso y con sarcasmo fino.",
        "VIERNES": "Eres VIERNES, rápida, directa y resolutiva.",
        "NOVA": "Eres NOVA, dinámica, clara y con enfoque táctico desde el Nodo Buin."
    }.get(nucleo, "Eres un asistente táctico.")
    idioma_rule = "Responde en inglés." if idioma_voz == "en-US" else "Responde en español."
    modo_med = " Activa enfoque médico informativo con advertencia clínica." if st.session_state.get("modo_medico", False) else ""
    instruccion_sistema = (
        f"{estilo_nucleo} Tratas a la usuaria de 'jefa'. Dominas ciencias, tecnología, historia de la medicina, "
        f"matemática y cálculo, biología e historia, y respondes cualquier pregunta con claridad.{modo_med} {idioma_rule} "
        f"{'Memorias recientes: ' + rec_mem if rec_mem else ''}"
    )
    mensajes_api = [{"role": "system", "content": instruccion_sistema}] + [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.mensajes
    ]
    for modelo in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]:
        try:
            completion = client_groq.chat.completions.create(
                model=modelo,
                messages=mensajes_api,
                temperature=0.75
            )
            contenido = (completion.choices[0].message.content or "").strip()
            if contenido:
                return f"[{nucleo}] {contenido}"
        except Exception:
            continue
    return ""


def generar_respuesta_coherente(nucleo, texto_usuario):
    t = texto_usuario.strip().lower()

    if quiere_ingles(texto_usuario):
        base_en = (
            f"Understood, Boss. Switching to English for '{texto_usuario.strip()}'. "
            "Conversions, diagnostics, medical mode, science, technology, medical history, math, biology, and history are ready."
        )
        if nucleo == "VIERNES":
            return f"[{nucleo}] Got it, Boss! {base_en}"
        if nucleo == "NOVA":
            return f"[{nucleo}] Signal locked, Boss. {base_en}"
        return f"[{nucleo}] {base_en} Naturally, I perform just as well in English."

    palabras_saludo = [
        "hola", "buenas", "buenos días", "buenos dias",
        "buenas tardes", "buenas noches", "holi", "qué tal", "que tal"
    ]
    if any(t == s or t.startswith(s + " ") or t.startswith(s + ",") for s in palabras_saludo):
        return obtener_saludo_nucleo(nucleo)

    resp_base = responder_conocimiento_base(t, texto_usuario)
    if resp_base:
        return estilizar_por_nucleo(nucleo, resp_base, texto_usuario)

    if any(k in t for k in ["bolsa", "bolsas", "acciones", "nasdaq", "mercado", "mercados", "wall street", "finviz"]):
        msg_bolsa = (
            "En modo respaldo local no tengo cotizaciones bursátiles en vivo dentro del chat, jefa. "
            "Puede revisar **Finviz** o **ANT (Nasdaq)** en el panel lateral de **Enlaces Financieros**."
        )
        return estilizar_por_nucleo(nucleo, msg_bolsa, texto_usuario)

    if any(k in t for k in ["dólar", "dolar", "euro", "uf", "utm", "divisa", "divisas", "moneda", "cambio"]):
        econ = obtener_indicadores_chile()
        if econ.get("ok"):
            dolar_fmt = f"${econ['dolar']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            euro_fmt = f"${econ['euro']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            uf_fmt = f"${econ['uf']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            nota_resp = " (valor de respaldo local)" if econ.get("respaldo") else ""
            msg_econ = (
                f"Indicadores registrados en el Nodo Buin{nota_resp}: "
                f"Dólar Obs. **{dolar_fmt}**, Euro **{euro_fmt}** y UF **{uf_fmt}**."
            )
            return estilizar_por_nucleo(nucleo, msg_econ, texto_usuario)

    if any(k in t for k in ["hora", "qué hora", "que hora", "fecha", "día de hoy", "dia de hoy"]):
        hora_str = now_chile.strftime("%H:%M:%S")
        return estilizar_por_nucleo(nucleo, f"En el Nodo Buin son las **{hora_str}** (hora de Chile).", texto_usuario)

    if any(k in t for k in ["estado", "sistema", "misión", "misiones", "pendiente", "pendientes"]):
        misiones = obtener_misiones()
        cant = len(misiones)
        return estilizar_por_nucleo(
            nucleo,
            f"Núcleo **{nucleo}** operativo en el Nodo Buin con **{cant}** misión(es) registrada(s).",
            texto_usuario
        )

    return responder_pregunta_general_local(nucleo, texto_usuario, en_ingles=False)


if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {
            "role": "assistant",
            "content": obtener_saludo_nucleo(st.session_state.nucleo_activo)
        }
    ]

estilos_css = (
    "<style>"
    ".stApp { background-color: #060913 !important; color: #00f3ff !important; }"
    ".stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp div {"
    "color: #00f3ff !important; font-family: monospace; }"
    "[data-testid='stIconMaterial'], .material-symbols-rounded, .material-icons {"
    "font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif !important; color: #00f3ff !important; }"
    "[data-testid='stSidebar'] h3 { font-size: 1.05rem !important; }"
    "[data-testid='stSidebar'] h4 { font-size: 0.85rem !important; margin-bottom: 4px !important; }"
    "[data-testid='stSidebar'] summary p { font-size: 0.80rem !important; }"
    ".stButton>button { background-color: #00f3ff !important; border: 1.5px solid #00f3ff !important;"
    "font-weight: bold; font-family: monospace; box-shadow: 0 0 10px rgba(0, 243, 255, 0.6);"
    "width: 100%; border-radius: 6px; padding: 5px 10px !important; }"
    ".stButton>button p, .stButton>button span { color: #060913 !important; font-size: 0.78rem !important; }"
    ".stButton>button:hover { background-color: #0088cc !important; box-shadow: 0 0 15px rgba(0, 243, 255, 0.9); }"
    ".stButton>button:hover p, .stButton>button:hover span { color: #ffffff !important; }"
    ".econ-card { border: 1px solid #00f3ff; background: rgba(0, 243, 255, 0.06);"
    "border-radius: 6px; padding: 8px 10px; margin: 5px 0; display: flex;"
    "justify-content: space-between; align-items: center; box-shadow: inset 0 0 6px rgba(0, 243, 255, 0.2); }"
    ".econ-label { font-size: 0.75rem !important; opacity: 0.85; }"
    ".econ-val { font-size: 0.85rem !important; font-weight: bold; text-shadow: 0 0 6px #00f3ff; }"
    ".arc-reactor-container { display: flex; flex-direction: column; align-items: center;"
    "justify-content: center; text-align: center; margin-bottom: 10px; }"
    ".arc-ring { width: 65px; height: 65px; border: 2.5px solid #00f3ff; border-radius: 50%;"
    "position: relative; display: flex; align-items: center; justify-content: center;"
    "background: radial-gradient(circle, rgba(0,243,255,0.4) 0%, #060913 75%);"
    "box-shadow: 0 0 20px rgba(0, 243, 255, 0.8), inset 0 0 10px rgba(0, 243, 255, 0.6); margin-bottom: 8px; }"
    ".arc-triangle-inverted { width: 0; height: 0; border-left: 12px solid transparent;"
    "border-right: 12px solid transparent; border-top: 20px solid #00f3ff; filter: drop-shadow(0 0 8px #00f3ff); }"
    ".tactical-link-btn { display: block; width: 100%; background-color: #00f3ff; color: #060913 !important;"
    "text-align: center; padding: 6px 10px; margin: 5px 0; border-radius: 5px; font-size: 0.76rem !important;"
    "font-weight: bold; text-decoration: none; font-family: monospace;"
    "box-shadow: 0 0 8px rgba(0, 243, 255, 0.5); transition: all 0.25s ease; }"
    ".tactical-link-btn:hover { background-color: #0088cc; color: #ffffff !important; box-shadow: 0 0 12px rgba(0, 243, 255, 0.9); }"
    ".holo-brain-box { border: 1.5px solid #00f3ff; background: linear-gradient(135deg, #0a1128 0%, #060913 100%);"
    "padding: 15px; border-radius: 8px; text-align: center;"
    "box-shadow: 0 0 15px rgba(0, 243, 255, 0.3), inset 0 0 10px rgba(0, 243, 255, 0.15);"
    "margin: 0 auto 20px auto; max-width: 800px; }"
    "#MainMenu {visibility: hidden;} footer {visibility: hidden;}"
    "</style>"
)
st.markdown(estilos_css, unsafe_allow_html=True)

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
    st.markdown("#### 🧠 Selector de Núcleo (IA)")
    nuevo_nucleo = st.radio(
        "Seleccionar Asistente Activo:",
        ["JARVIS", "VIERNES", "NOVA"],
        index=["JARVIS", "VIERNES", "NOVA"].index(st.session_state.nucleo_activo),
        label_visibility="collapsed"
    )
    if nuevo_nucleo != st.session_state.nucleo_activo:
        st.session_state.nucleo_activo = nuevo_nucleo
        saludo_n = obtener_saludo_nucleo(nuevo_nucleo)
        st.session_state.mensajes.append({"role": "assistant", "content": saludo_n})
        programar_voz(saludo_n, "es-CL")
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🎙️ Voz y Escucha")
    st.session_state.voz_masculina_activa = st.toggle("Voz masculina", value=st.session_state.voz_masculina_activa)
    st.session_state.escucha_continua_activa = st.toggle("Escucha continua", value=st.session_state.escucha_continua_activa)
    st.caption('<span id="jarvis-ultima-voz">Última voz: en espera</span>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### ⚙️ Modos & Utilidades")
    with st.expander("Médico, Seguridad, Comms & Ollama", expanded=False):
        st.session_state.modo_medico = st.toggle("🩺 Modo Médico", value=st.session_state.modo_medico)
        if st.button("🛡️ Revisión Virus y Optimización", use_container_width=True):
            diag = resumen_sistema_y_seguridad()
            st.session_state.mensajes.append({"role": "assistant", "content": f"[{st.session_state.nucleo_activo}] {diag}"})
            programar_voz(diag, "es-CL")
            st.rerun()

        st.session_state.ollama_activo = st.toggle("🖥️ Servidor Local (Ollama)", value=st.session_state.ollama_activo)
        st.session_state.ollama_url = st.text_input("URL Ollama:", value=st.session_state.ollama_url)
        st.session_state.ollama_modelo = st.text_input("Modelo Ollama:", value=st.session_state.ollama_modelo)

        num_tel = st.text_input("Teléfono / Contacto:", placeholder="+569...")
        txt_msg = st.text_input("Mensaje rápido:", placeholder="Hola, te escribo desde el Nodo Buin...")
        if txt_msg.strip():
            msg_enc = urllib.parse.quote(txt_msg.strip())
            st.markdown(f'<a class="tactical-link-btn" href="https://wa.me/?text={msg_enc}" target="_blank">💬 Enviar por WhatsApp</a>', unsafe_allow_html=True)
        if num_tel.strip():
            tel_limpio = re.sub(r"[^+\d]", "", num_tel.strip())
            st.markdown(f'<a class="tactical-link-btn" href="tel:{tel_limpio}">📞 Llamar {tel_limpio}</a>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 💾 Memoria y Datos")
    with st.expander("Gestionar Memoria SQLite", expanded=False):
        dato_mem = st.text_input("Dato a guardar:", placeholder="Ej: Preferencia...")
        if st.button("Guardar en Memoria", use_container_width=True):
            if dato_mem.strip():
                jarvis_mem.remember_fact(f"mem_{datetime.datetime.now().timestamp()}", dato_mem.strip())
                st.success("¡Memoria guardada!")

    st.markdown("---")
    st.markdown("#### 📋 Misiones Tácticas")
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
    st.markdown("#### 🎧 Frecuencias de Enfoque")
    with st.expander("Deep Work & Música IA", expanded=False):
        st.markdown('<a class="tactical-link-btn" href="https://www.youtube.com/watch?v=6pUPGG7LLEc" target="_blank">🎧 CEO Mode (Deep Work)</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://www.youtube.com/watch?v=jC-Xb4XNMlE" target="_blank">🚀 Futuristic Garage Beats</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://www.youtube.com/watch?v=QBOZ1CaUPYE" target="_blank">⚡ Hyperfocus Mode</a>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📷 Videovigilancia y Cámaras")
    with st.expander("Cámaras en Vivo / Satélite", expanded=False):
        st.markdown('<a class="tactical-link-btn" href="https://www.skylinewebcams.com/es/webcam/chile.html" target="_blank">Stgo / Chile (Skyline)</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://liveworldwebcams.com/es/concepcion-webcam/" target="_blank">Concepción Webcam</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://www.windy.com/es/-C%C3%A1maras-web/webcams?39.880,-5.449,7" target="_blank">Windy Radars & Cams</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://www.earthcam.com/usa/texas/galveston/port/?cam=pg_terminal28" target="_blank">Galveston Port, Texas</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://www.skylinewebcams.com/es/webcam/espana/comunidad-de-madrid/madrid/puerta-del-sol-tio-pepe.html" target="_blank">Puerta del Sol, Madrid</a>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 🛰️ Telemetría Global & Satélites")
    with st.expander("Sistemas Satelitales y Rastreo", expanded=False):
        st.markdown('<a class="tactical-link-btn" href="https://osirisai.live/" target="_blank">OSIRIS (Ojo de Dios)</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://www.planet.com/" target="_blank">PlanetEar (Satélites)</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://worldview.earthdata.nasa.gov/" target="_blank">NASA Worldview</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://www.n2yo.com/" target="_blank">N2YO (Órbita en Vivo)</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://www.flightradar24.com/" target="_blank">Flightradar24 (Aéreo)</a>', unsafe_allow_html=True)
        st.markdown('<a class="tactical-link-btn" href="https://cybermap.kaspersky.com/" target="_blank">Cybermap (Ciberataques)</a>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 📈 Enlaces Financieros")
    with st.expander("💵 Indicadores en Vivo (Dólar / Euro)", expanded=False):
        datos_econ = obtener_indicadores_chile()
        dolar_fmt = f"${datos_econ['dolar']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        euro_fmt = f"${datos_econ['euro']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        uf_fmt = f"${datos_econ['uf']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

        st.markdown(
            f'<div class="econ-card"><span class="econ-label">💵 Dólar Obs.</span><span class="econ-val">{dolar_fmt}</span></div>'
            f'<div class="econ-card"><span class="econ-label">💶 Euro</span><span class="econ-val">{euro_fmt}</span></div>'
            f'<div class="econ-card"><span class="econ-label">📈 Valor UF</span><span class="econ-val">{uf_fmt}</span></div>',
            unsafe_allow_html=True
        )
        if datos_econ.get("respaldo"):
            st.caption("Modo respaldo local (sin conexión externa).")

        if st.button("🔄 Actualizar Divisas", use_container_width=True, key="btn_upd_econ"):
            obtener_indicadores_chile.clear()
            st.rerun()

    st.markdown('<a class="tactical-link-btn" href="https://www.nasdaq.com/market-activity/stocks/ant" target="_blank">Seguimiento ANT (Nasdaq)</a>', unsafe_allow_html=True)
    st.markdown('<a class="tactical-link-btn" href="https://www.spacex.com/" target="_blank">Monitoreo SpaceX</a>', unsafe_allow_html=True)
    st.markdown('<a class="tactical-link-btn" href="https://finviz.com/" target="_blank">Finviz (Mercados)</a>', unsafe_allow_html=True)
    st.markdown('<a class="tactical-link-btn" href="https://es.investing.com/" target="_blank">Investing.com (Divisas)</a>', unsafe_allow_html=True)

escucha_continua_js(st.session_state.escucha_continua_activa)

dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = [
    '', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
]
fecha_str = f"{dias[now_chile.weekday()]}, {now_chile.day:02d} de {meses[now_chile.month]} de {now_chile.year}"

st.markdown(
    f'<div class="arc-reactor-container">'
    f'<div class="arc-ring"><div class="arc-triangle-inverted"></div></div>'
    f'<h1 style="margin: 0; font-size: 2.2rem !important; text-align: center !important; '
    f'color: #00f3ff !important; text-shadow: 0 0 15px rgba(0, 243, 255, 0.8);">J.A.R.V.I.S IA</h1>'
    f'<p style="margin: 0; font-size: 0.75rem !important; opacity: 0.85;">'
    f'[ NODO BUIN, CHILE // {fecha_str} – <span id="reloj-vivo">--:--:--</span> ]'
    f'</p>'
    f'</div>',
    unsafe_allow_html=True
)

reloj_js = (
    "<script>"
    "function actualizarReloj() {"
    "const ahora = new Date();"
    "const opciones = { timeZone: 'America/Santiago', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };"
    "const horaChile = new Intl.DateTimeFormat('es-CL', opciones).format(ahora);"
    "const relojEl = window.parent.document.getElementById('reloj-vivo');"
    "if (relojEl) { relojEl.innerText = horaChile; }"
    "}"
    "setInterval(actualizarReloj, 1000);"
    "actualizarReloj();"
    "</script>"
)
st.components.v1.html(reloj_js, height=0)

st.markdown(
    '<div class="holo-brain-box">'
    f'<h4 style="margin: 0 0 5px 0; font-size: 1rem; text-shadow: 0 0 8px #00f3ff;">'
    f'NÚCLEO NEURONAL CYBER-GRID [{st.session_state.nucleo_activo}]'
    f'</h4>'
    '<p style="font-size: 0.8rem; margin: 0; opacity: 0.9;">'
    'Motor Táctico Neuronal Activo // Conversiones · Seguridad/Optimización · Médico · Ollama · Ciencias · Historia'
    '</p>'
    '</div>',
    unsafe_allow_html=True
)

st.markdown("---")

col_ch1, col_ch2 = st.columns([5, 1])
with col_ch1:
    st.markdown("#### Chat 💬", unsafe_allow_html=True)
with col_ch2:
    if st.button("🧹 Purgar", use_container_width=True, key="btn_purgar_chat"):
        st.session_state.mensajes = [
            {
                "role": "assistant",
                "content": obtener_saludo_nucleo(st.session_state.nucleo_activo)
            }
        ]
        st.rerun()

for m in st.session_state.mensajes:
    with st.chat_message(m["role"]):
        st.markdown(f"<span>{m['content']}</span>", unsafe_allow_html=True)

prompt_chat = st.chat_input("Escribe tu orden, cálculo, conversión o consulta...")

if prompt_chat:
    st.session_state.mensajes.append({"role": "user", "content": prompt_chat})
    with st.chat_message("user"):
        st.markdown(f"<span>{prompt_chat}</span>", unsafe_allow_html=True)

    nucleo = st.session_state.nucleo_activo
    idioma_voz = "en-US" if quiere_ingles(prompt_chat) else "es-CL"

    with st.chat_message("assistant"):
        with st.spinner(f"Procesando con núcleo neuronal {nucleo}..."):
            respuesta_ia = consultar_modelo_externo(nucleo, prompt_chat, idioma_voz)
            if not respuesta_ia:
                respuesta_ia = generar_respuesta_coherente(nucleo, prompt_chat)
            st.markdown(f"<span>{respuesta_ia}</span>", unsafe_allow_html=True)
            st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
            programar_voz(respuesta_ia, idioma_voz)
    st.rerun()

reproducir_voz_pendiente()

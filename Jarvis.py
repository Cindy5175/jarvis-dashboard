import datetime
import os
import random
import re
import sqlite3
import streamlit as st
import streamlit.components.v1 as components

try:
    import requests
    REQUESTS_OK = True
except Exception:
    requests = None
    REQUESTS_OK = False

try:
    from groq import Groq
    GROQ_OK = True
except Exception:
    Groq = None
    GROQ_OK = False

try:
    from memoria_loader import obtener_memoria_completa
except Exception:
    def obtener_memoria_completa() -> str:
        return ""

try:
    from modulo_ingles import detectar_solicitud_idioma, responder_en_ingles
except Exception:
    def detectar_solicitud_idioma(texto: str) -> str:
        t = (texto or "").lower()
        pistas = ["in english", "speak english", "reply in english", "hello", "status", "check"]
        return "en" if any(p in t for p in pistas) else "es"

    def responder_en_ingles(texto: str) -> str:
        return (
            f"At your service, Boss. Handling '{texto}' in English—"
            "try not to make me switch back just because you run out of vocabulary."
        )


st.set_page_config(
    page_title="J.A.R.V.I.S. // NODO BUIN",
    layout="wide",
    initial_sidebar_state="expanded",
)

PIN_SECRETO = "2805"
DB_PATH = "jarvis_misiones.db"
OSIRIS_URL = "https://osirisai.live/"
TZ_CHILE = datetime.timezone(datetime.timedelta(hours=-3))


def hora_chile() -> datetime.datetime:
    return datetime.datetime.now(TZ_CHILE)


def fmt_clp(valor: float) -> str:
    return f"${valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def limpiar_voz(texto: str) -> str:
    if not texto:
        return ""
    limpio = re.sub(r"\[[^\]]+\]\([^)]+\)", " enlace táctico ", texto)
    limpio = re.sub(r"https?://\S+", " enlace táctico ", limpio)
    limpio = re.sub(r"[*_`#>\[\]]+", "", limpio)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    return limpio[:420]


def emitir_voz_masculina(texto: str, activa: bool = True):
    if not activa:
        return
    limpio = limpiar_voz(texto)
    if not limpio:
        return
    escapado = (
        limpio.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("'", "\\'")
        .replace("\n", " ")
    )
    js = f"""
    <script>
      (function() {{
        try {{
          if ("speechSynthesis" in window) {{
            window.speechSynthesis.cancel();
            const msg = new SpeechSynthesisUtterance("{escapado}");
            msg.lang = "es-CL";
            msg.rate = 1.02;
            msg.pitch = 0.85;
            const voices = window.speechSynthesis.getVoices() || [];
            const maleEs = voices.find(v => {{
              const n = (v.name || "").toLowerCase();
              const l = (v.lang || "").toLowerCase();
              const isEs = l.startsWith("es");
              const isFem = /sabina|helena|zira|hazel|lucia|lucía|sofia|sofía|female|mujer/.test(n);
              return isEs && !isFem;
            }}) || voices.find(v => (v.lang || "").toLowerCase().startsWith("es"));
            if (maleEs) msg.voice = maleEs;
            window.speechSynthesis.speak(msg);
          }}
        }} catch (err) {{}}
      }})();
    </script>
    """
    components.html(js, height=0)


def activar_escucha_continua_js(activa: bool):
    if not activa:
        return
    js = """
    <script>
      (function() {
        try {
          const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
          if (!SR || window.__jarvisSrRunning) return;
          const rec = new SR();
          rec.lang = "es-CL";
          rec.continuous = true;
          rec.interimResults = false;
          window.__jarvisSrRunning = true;
          rec.onresult = function(event) {
            const lastIdx = event.results.length - 1;
            if (lastIdx >= 0 && event.results[lastIdx][0]) {
              const dicho = (event.results[lastIdx][0].transcript || "").trim();
              if (dicho) {
                window.__jarvisUltimoDicho = dicho;
                const badge = window.parent.document.getElementById("jarvis-voz-capturada");
                if (badge) badge.innerText = "Voz detectada: " + dicho;
              }
            }
          };
          rec.onerror = function() { window.__jarvisSrRunning = false; };
          rec.onend = function() {
            window.__jarvisSrRunning = false;
            try { rec.start(); window.__jarvisSrRunning = true; } catch (e) {}
          };
          rec.start();
        } catch (e) {}
      })();
    </script>
    """
    components.html(js, height=0)


def init_db():
    try:
        with sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5) as conn:
            cur = conn.cursor()
            cur.execute(
                "CREATE TABLE IF NOT EXISTS misiones ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "tarea TEXT NOT NULL, "
                "estado TEXT DEFAULT 'Pendiente')"
            )
            cur.execute(
                "CREATE TABLE IF NOT EXISTS memory ("
                "key_id TEXT PRIMARY KEY, "
                "fact_text TEXT NOT NULL, "
                "category TEXT DEFAULT 'general')"
            )
            conn.commit()
    except Exception:
        pass


def guardar_memoria(fact_text: str, category: str = "general"):
    try:
        with sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5) as conn:
            key = f"mem_{datetime.datetime.now().timestamp()}"
            conn.execute(
                "INSERT OR REPLACE INTO memory (key_id, fact_text, category) VALUES (?, ?, ?)",
                (key, fact_text, category),
            )
            conn.commit()
    except Exception:
        pass


def listar_memorias(limite: int = 8) -> list:
    try:
        with sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5) as conn:
            rows = conn.execute(
                "SELECT fact_text, category FROM memory ORDER BY key_id DESC LIMIT ?",
                (limite,),
            ).fetchall()
            return rows
    except Exception:
        return []


def borrar_memoria(fragmento: str) -> int:
    try:
        with sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5) as conn:
            cur = conn.execute(
                "DELETE FROM memory WHERE LOWER(fact_text) LIKE ?",
                (f"%{fragmento.lower()}%",),
            )
            conn.commit()
            return cur.rowcount
    except Exception:
        return 0


def agregar_mision(tarea: str):
    try:
        with sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5) as conn:
            conn.execute("INSERT INTO misiones (tarea) VALUES (?)", (tarea,))
            conn.commit()
    except Exception:
        pass


def listar_misiones() -> list:
    try:
        with sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5) as conn:
            return conn.execute("SELECT id, tarea, estado FROM misiones ORDER BY id DESC").fetchall()
    except Exception:
        return []


def completar_mision(fragmento: str) -> int:
    try:
        with sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5) as conn:
            cur = conn.execute(
                "UPDATE misiones SET estado = 'Completada' WHERE LOWER(tarea) LIKE ?",
                (f"%{fragmento.lower()}%",),
            )
            conn.commit()
            return cur.rowcount
    except Exception:
        return 0


def limpiar_misiones():
    try:
        with sqlite3.connect(DB_PATH, check_same_thread=False, timeout=5) as conn:
            conn.execute("DELETE FROM misiones")
            conn.commit()
    except Exception:
        pass


init_db()


@st.cache_data(ttl=300)
def obtener_indicadores() -> dict:
    if REQUESTS_OK and requests is not None:
        try:
            resp = requests.get(
                "https://mindicador.cl/api",
                headers={"User-Agent": "Mozilla/5.0 JARVIS-Buin/2.0"},
                timeout=6,
            )
            if resp.status_code == 200:
                data = resp.json()
                dolar = data.get("dolar", {}).get("valor")
                euro = data.get("euro", {}).get("valor")
                uf = data.get("uf", {}).get("valor")
                if dolar and euro and uf:
                    return {
                        "dolar": float(dolar),
                        "euro": float(euro),
                        "uf": float(uf),
                        "respaldo": False,
                    }
        except Exception:
            pass
    return {
        "dolar": 965.00,
        "euro": 1045.00,
        "uf": 38250.00,
        "respaldo": True,
    }


def obtener_cliente_groq():
    api_key = ""
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        api_key = ""
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY", "")
    if GROQ_OK and Groq is not None and api_key:
        try:
            return Groq(api_key=api_key)
        except Exception:
            return None
    return None


def saludo_nucleo(nucleo: str) -> str:
    ahora = hora_chile()
    tramo = (
        "Buenos días"
        if ahora.hour < 12
        else ("Buenas tardes" if ahora.hour < 20 else "Buenas noches")
    )
    frases = {
        "JARVIS": (
            f"[{nucleo}] {tramo}, señorita. Sistema estabilizado sin parches milagrosos. "
            "¿Qué orden damos hoy o solo pasamos a supervisar?"
        ),
        "VIERNES": (
            f"[{nucleo}] ¡{tramo}, señorita! Todo en línea y listo para ejecutar. "
            "Diga cuándo empezamos."
        ),
        "NOVA": (
            f"[{nucleo}] ¡{tramo}, señorita! Enlace activo desde el Nodo Buin. "
            "¿Qué coordenada o misión revisamos ahora?"
        ),
    }
    return frases.get(nucleo, f"[{nucleo}] {tramo}, señorita. En línea.")


def responder_ia_externa(nucleo: str, mensaje: str) -> str:
    cliente = obtener_cliente_groq()
    if cliente is None:
        return ""
    mems = [m[0] for m in listar_memorias(5)]
    ctx_mem = f"Memorias guardadas: {'; '.join(mems)}." if mems else ""
    estilos = {
        "JARVIS": "Eres JARVIS, elegante, preciso y con sarcasmo fino. Trata a la usuaria como 'señorita' y responde en español breve.",
        "VIERNES": "Eres VIERNES, rápida, clara y resolutiva. Trata a la usuaria como 'señorita' y responde en español breve.",
        "NOVA": "Eres NOVA, directa y dinámica. Trata a la usuaria como 'señorita' y responde en español breve.",
    }
    prompt_sys = f"{estilos.get(nucleo, estilos['JARVIS'])} {ctx_mem}"
    for modelo in ["openai/gpt-oss-120b", "llama-3.3-70b-versatile"]:
        try:
            res = cliente.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": prompt_sys},
                    {"role": "user", "content": mensaje},
                ],
                temperature=0.65,
                max_tokens=280,
            )
            txt = (res.choices[0].message.content or "").strip()
            if txt:
                return f"[{nucleo}] {txt}"
        except Exception:
            continue
    return ""


def procesar_comando(nucleo: str, texto: str) -> str:
    raw = (texto or "").strip()
    t = raw.lower()
    pref = f"[{nucleo}] "

    if not raw:
        return f"{pref}¿Me habló, señorita? Porque el micrófono capta más silencio que órdenes."

    if detectar_solicitud_idioma(raw) == "en":
        return f"{pref}{responder_en_ingles(raw)}"

    if any(t == s or t.startswith(s + " ") or t.startswith(s + ",") for s in [
        "hola", "buenas", "buenos días", "buenos dias", "buenas tardes", "buenas noches", "qué tal", "que tal"
    ]):
        return saludo_nucleo(nucleo)

    if "mapa" in t or "planetear" in t:
        st.session_state.ver_mapa = True
        if "planetear" in t:
            st.session_state.ver_ojo_dios = True
        return f"{pref}Sí, señorita. **Mapa táctico satelital** desplegado sobre Nodo Buin."

    if "ojo de dios" in t or "cámara" in t or "camara" in t or "vigilancia" in t or "wendy" in t:
        st.session_state.ver_ojo_dios = True
        return (
            f"{pref}Sí, señorita. **Ojo de Dios** activo en "
            f"**{st.session_state.camara_seleccionada}** // Enlace: [{OSIRIS_URL}]({OSIRIS_URL})."
        )

    if "osiris" in t:
        return f"{pref}Sí, señorita. Enlace directo a **Osiris AI**: [{OSIRIS_URL}]({OSIRIS_URL})."

    if any(k in t for k in ["dólar", "dolar", "euro", "uf", "divisa", "moneda", "cambio"]):
        ind = obtener_indicadores()
        nota = " *(respaldo)*" if ind["respaldo"] else ""
        return (
            f"{pref}Indicadores actuales{nota}, señorita: "
            f"Dólar **{fmt_clp(ind['dolar'])}**, Euro **{fmt_clp(ind['euro'])}** y UF **{fmt_clp(ind['uf'])}**."
        )

    if t.startswith(("mision:", "misión:", "anota mision:", "anota misión:")):
        tarea = raw.split(":", 1)[1].strip()
        if tarea:
            agregar_mision(tarea)
            return f"{pref}Sí, señorita. Misión guardada: **{tarea}**."

    if t.startswith(("completa mision:", "completa misión:")):
        objetivo = raw.split(":", 1)[1].strip()
        if objetivo:
            n = completar_mision(objetivo)
            return f"{pref}Sí, señorita. Misiones completadas: **{n}**."

    if t.startswith(("recuerda:", "guarda:")):
        hecho = raw.split(":", 1)[1].strip()
        if hecho:
            guardar_memoria(hecho, "chat")
            return f"{pref}Sí, señorita. Guardado en memoria: *{hecho}*."

    if t.startswith(("olvida:", "borra memoria:")):
        frag = raw.split(":", 1)[1].strip()
        if frag:
            n = borrar_memoria(frag)
            return f"{pref}Sí, señorita. Memorias eliminadas: **{n}**."

    if any(k in t for k in ["memorias", "qué recuerdas", "que recuerdas"]):
        mems = listar_memorias(5)
        if not mems:
            return f"{pref}No hay memorias guardadas todavía, señorita."
        return f"{pref}Memorias recientes, señorita: {'; '.join(m[0] for m in mems)}."

    if any(k in t for k in ["resumen", "reporte", "estado", "misiones"]):
        misiones = listar_misiones()
        pend = sum(1 for _, _, est in misiones if est != "Completada")
        return (
            f"{pref}Reporte ({hora_chile().strftime('%H:%M:%S')} CLT), señorita: "
            f"Mapa táctico satelital **{'ACTIVO' if st.session_state.ver_mapa else 'EN ESPERA'}**, "
            f"Ojo de Dios **{'ACTIVO' if st.session_state.ver_ojo_dios else 'EN ESPERA'}**, "
            f"misiones pendientes **{pend}/{len(misiones)}**."
        )

    if "hora" in t:
        return f"{pref}Son las **{hora_chile().strftime('%H:%M:%S')}** (hora de Chile), señorita."

    ia_txt = responder_ia_externa(nucleo, raw)
    if ia_txt:
        return ia_txt

    opciones = [
        f"{pref}Recibido, señorita: *{raw}*. Puede pedirme `mapa`, `ojo de dios`, `dólar`, `resumen`, `misión: ...` o `recuerda: ...`.",
        f"{pref}Anotado, señorita: *{raw}*. Prometo procesarlo sin inventar errores de sintaxis.",
    ]
    return random.choice(opciones)


# --- ESTADO INICIAL ---
st.session_state.setdefault("autorizado", False)
st.session_state.setdefault("nucleo_activo", "JARVIS")
st.session_state.setdefault("ver_mapa", False)
st.session_state.setdefault("ver_ojo_dios", False)
st.session_state.setdefault("camara_seleccionada", "CAM-01 // PERÍMETRO NODO BUIN")
st.session_state.setdefault("stream_url", "")
st.session_state.setdefault("voz_activa", True)
st.session_state.setdefault("escucha_activa", True)
st.session_state.setdefault("mensajes", [{"role": "assistant", "content": saludo_nucleo("JARVIS")}])

# --- ESTILO OSCURO AZUL NEÓN ---
st.markdown(
    """
    <style>
      .stApp {
        background-color: #060913 !important;
        color: #00f3ff !important;
        font-family: "Courier New", Courier, monospace !important;
      }
      p, span, label, h1, h2, h3, h4, div, small {
        color: #00f3ff !important;
        font-family: "Courier New", Courier, monospace !important;
      }
      section[data-testid="stSidebar"] {
        background-color: #080d1a !important;
        border-right: 1px solid rgba(0, 243, 255, 0.35) !important;
      }
      .stButton > button {
        background-color: #00f3ff !important;
        color: #060913 !important;
        border: 1px solid #00f3ff !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        width: 100% !important;
      }
      .stButton > button p, .stButton > button span {
        color: #060913 !important;
      }
      .jarvis-panel {
        border: 1.5px solid #00f3ff;
        background: linear-gradient(135deg, rgba(10, 20, 46, 0.95) 0%, rgba(6, 9, 19, 0.98) 100%);
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
        box-shadow: 0 0 18px rgba(0, 243, 255, 0.14);
      }
      .arc-wrap {
        display: flex;
        justify-content: center;
        margin-bottom: 8px;
      }
      .arc-circle {
        width: 56px;
        height: 56px;
        border-radius: 50%;
        border: 2.5px solid #00f3ff;
        display: flex;
        align-items: center;
        justify-content: center;
        background: radial-gradient(circle, rgba(0, 243, 255, 0.35) 0%, #060913 75%);
        box-shadow: 0 0 16px rgba(0, 243, 255, 0.65);
      }
      .arc-tri {
        width: 0;
        height: 0;
        border-left: 10px solid transparent;
        border-right: 10px solid transparent;
        border-top: 17px solid #00f3ff;
      }
      .osiris-btn {
        display: block;
        width: 100%;
        text-align: center;
        background-color: #00f3ff;
        color: #060913 !important;
        font-weight: 700;
        padding: 8px 12px;
        border-radius: 6px;
        text-decoration: none;
      }
      .kpi-box {
        border: 1px solid rgba(0, 243, 255, 0.45);
        background: rgba(0, 243, 255, 0.05);
        border-radius: 8px;
        padding: 10px 12px;
      }
      #MainMenu, footer {
        visibility: hidden;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- BLOQUEO POR PIN ---
if not st.session_state.autorizado:
    st.markdown(
        '<div class="jarvis-panel" style="max-width:520px;margin:60px auto;text-align:center;">'
        "<h2>ACCESO RESTRINGIDO // NODO BUIN</h2>"
        "<p>Ingrese su PIN de seguridad para despertar el núcleo.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    _, col_pin, _ = st.columns([1, 1.4, 1])
    with col_pin:
        with st.form("login_jarvis"):
            pin_ingresado = st.text_input("PIN de acceso", type="password", placeholder="••••")
            if st.form_submit_button("Desbloquear Sistema"):
                if pin_ingresado.strip() == PIN_SECRETO:
                    st.session_state.autorizado = True
                    emitir_voz_masculina("Acceso concedido, señorita.", st.session_state.voz_activa)
                    st.rerun()
                else:
                    st.error("PIN incorrecto. Intente nuevamente.")
    st.stop()

# --- BARRA LATERAL IZQUIERDA ---
with st.sidebar:
    st.markdown("### 🛡️ Arsenal de Módulos")
    c_b1, c_b2 = st.columns(2)
    with c_b1:
        if st.button("🔒 Bloquear"):
            st.session_state.autorizado = False
            st.rerun()
    with c_b2:
        if st.button("🔄 Reiniciar"):
            st.session_state.mensajes = [{"role": "assistant", "content": saludo_nucleo(st.session_state.nucleo_activo)}]
            st.rerun()

    st.markdown("---")
    st.markdown("#### 🧠 Selector de Núcleo")
    nucleo_sel = st.radio(
        "Núcleo activo",
        ["JARVIS", "VIERNES", "NOVA"],
        index=["JARVIS", "VIERNES", "NOVA"].index(st.session_state.nucleo_activo),
        label_visibility="collapsed",
    )
    if nucleo_sel != st.session_state.nucleo_activo:
        st.session_state.nucleo_activo = nucleo_sel
        aviso = saludo_nucleo(nucleo_sel)
        st.session_state.mensajes.append({"role": "assistant", "content": aviso})
        emitir_voz_masculina(aviso, st.session_state.voz_activa)
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🎙️ Audio y Voz")
    st.session_state.voz_activa = st.toggle("Voz masculina activa", value=st.session_state.voz_activa)
    st.session_state.escucha_activa = st.toggle("Escucha continua", value=st.session_state.escucha_activa)
    st.markdown('<small id="jarvis-voz-capturada">Voz detectada: en espera</small>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 👁️ Ojo de Dios")
    with st.expander("Cámaras y vigilancia", expanded=False):
        cams = [
            "CAM-01 // PERÍMETRO NODO BUIN",
            "CAM-02 // ACCESO PRINCIPAL",
            "CAM-03 // PATIO Y SECTOR NORTE",
            "CAM-04 // ENLACE REMOTO / RTSP",
        ]
        idx_cam = cams.index(st.session_state.camara_seleccionada) if st.session_state.camara_seleccionada in cams else 0
        st.session_state.camara_seleccionada = st.selectbox("Feed de cámara", cams, index=idx_cam)
        st.session_state.stream_url = st.text_input("URL stream (opcional)", value=st.session_state.stream_url, placeholder="https://...")
        c_o1, c_o2 = st.columns(2)
        with c_o1:
            if st.button("Mostrar Ojo"):
                st.session_state.ver_ojo_dios = True
                st.rerun()
        with c_o2:
            if st.button("Ocultar Ojo"):
                st.session_state.ver_ojo_dios = False
                st.rerun()

    st.markdown("---")
    st.markdown("#### 💾 Memoria SQLite")
    with st.expander("Guardar o borrar notas", expanded=False):
        nota_nueva = st.text_input("Nueva memoria", placeholder="Ej: Revisar proyecto...")
        if st.button("Guardar memoria") and nota_nueva.strip():
            guardar_memoria(nota_nueva.strip())
            st.success("Guardado.")
            st.rerun()
        for mem_txt, _ in listar_memorias(5):
            st.caption(f"• {mem_txt}")

    st.markdown("---")
    st.markdown("#### 📋 Misiones Tácticas")
    with st.expander("Gestionar misiones", expanded=False):
        mision_txt = st.text_input("Nueva misión", placeholder="Ej: Configurar despliegue...")
        if st.button("Agregar misión") and mision_txt.strip():
            agregar_mision(mision_txt.strip())
            st.success("Misión añadida.")
            st.rerun()
        misiones_lista = listar_misiones()
        for _, tarea, estado in misiones_lista:
            st.caption(f"• [{estado}] {tarea}")
        if misiones_lista and st.button("Limpiar misiones"):
            limpiar_misiones()
            st.rerun()

activar_escucha_continua_js(st.session_state.escucha_activa)

# --- PANEL PRINCIPAL ---
st.markdown(
    f'<div class="jarvis-panel" style="text-align:center;">'
    f'<div class="arc-wrap"><div class="arc-circle"><div class="arc-tri"></div></div></div>'
    f"<h3>J.A.R.V.I.S. // NODO BUIN — NÚCLEO: {st.session_state.nucleo_activo}</h3>"
    f"<p>Hora local: {hora_chile().strftime('%H:%M:%S')} CLT | Estado: OPERATIVO</p>"
    f"</div>",
    unsafe_allow_html=True,
)

ind_chile = obtener_indicadores()
misiones_activas = listar_misiones()
pendientes_cnt = sum(1 for _, _, est in misiones_activas if est != "Completada")

k1, k2, k3, k4 = st.columns(4)
with k1:
    st.markdown(f'<div class="kpi-box"><small>DÓLAR OBS</small><br><b>{fmt_clp(ind_chile["dolar"])}</b></div>', unsafe_allow_html=True)
with k2:
    st.markdown(f'<div class="kpi-box"><small>EURO</small><br><b>{fmt_clp(ind_chile["euro"])}</b></div>', unsafe_allow_html=True)
with k3:
    st.markdown(f'<div class="kpi-box"><small>UF</small><br><b>{fmt_clp(ind_chile["uf"])}</b></div>', unsafe_allow_html=True)
with k4:
    st.markdown(f'<div class="kpi-box"><small>MISIONES PENDIENTES</small><br><b>{pendientes_cnt}/{len(misiones_activas)}</b></div>', unsafe_allow_html=True)

st.write("")
a1, a2, a3 = st.columns(3)
with a1:
    if st.button("🗺️ Mapa táctico satelital"):
        st.session_state.ver_mapa = not st.session_state.ver_mapa
        st.rerun()
with a2:
    if st.button("👁️ Ojo de Dios"):
        st.session_state.ver_ojo_dios = not st.session_state.ver_ojo_dios
        st.rerun()
with a3:
    st.markdown(f'<a class="osiris-btn" href="{OSIRIS_URL}" target="_blank">🌐 OSIRIS AI</a>', unsafe_allow_html=True)

if st.session_state.ver_mapa:
    st.markdown('<div class="jarvis-panel"><h4>🗺️ MAPA TÁCTICO SATELITAL — NODO BUIN</h4>', unsafe_allow_html=True)
    st.map({"lat": [-33.733], "lon": [-70.742]}, zoom=12)
    st.markdown("</div>", unsafe_allow_html=True)

if st.session_state.ver_ojo_dios:
    st.markdown(
        '<div class="jarvis-panel">'
        f"<h4>👁️ OJO DE DIOS — {st.session_state.camara_seleccionada}</h4>"
        "<p>Perímetro bajo observación. Sin alertas críticas en este ciclo.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    if st.session_state.stream_url.strip():
        st.image(st.session_state.stream_url.strip(), caption="Feed externo vinculado", use_container_width=True)

memoria_externa = obtener_memoria_completa()
if memoria_externa:
    with st.expander("Memoria externa cargada", expanded=False):
        st.markdown(memoria_externa)

st.markdown("#### 💬 Consola de Comando")
for msg in st.session_state.mensajes:
    with st.chat_message(msg.get("role", "assistant")):
        st.write(msg.get("content", ""))

entrada = st.chat_input("Escribe una orden para JARVIS (ej: 'mapa', 'dólar', 'misión: revisar servidores', 'resumen')...")
if entrada:
    st.session_state.mensajes.append({"role": "user", "content": entrada})
    respuesta = procesar_comando(st.session_state.nucleo_activo, entrada)
    st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
    emitir_voz_masculina(respuesta, st.session_state.voz_activa)
    st.rerun()

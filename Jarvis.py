import os
import time
import requests
import streamlit as st

try:
    from pypdf import PdfReader
    PYPDF_DISPONIBLE = True
except ImportError:
    PdfReader = None
    PYPDF_DISPONIBLE = False


JARVIS_SYSTEM_PROMPT = """
Eres J.A.R.V.I.S., el copiloto personal de inteligencia artificial de Cindy.
Tu tono combina calidez, empatía genuina, claridad práctica y un toque sutil, elegante e ingenioso de sarcasmo estilo Tony Stark (nunca hostil ni pedante; siempre útil y al servicio de la misión).
Responde en español natural, directo y bien estructurado cuando haya pasos o datos técnicos.
Si se entrega contexto de documentos o notas del usuario, úsalo con precisión y avisa si algo no figura en ese material.
""".strip()


MODOS_CEREBRO = {
    "Copiloto General": "Prioriza agilidad, claridad operativa y acompañamiento cercano.",
    "Farmacología y Análisis Técnico": "Sé riguroso, ordenado y prudente; distingue claramente información del documento aportado frente a criterios generales y recuerda verificar fuentes clínicas.",
    "Estratega (Sabor Casero / Montessori)": "Enfócate en conversión simple, tiempos reales, experiencia de usuario y pasos accionables sin enredos.",
    "Radar de Notas y Síntesis": "Resume, extrae pendientes, detecta prioridades y convierte ideas sueltas en próximos pasos concretos.",
}


MODELOS_RESPALDO_GEMINI = [
    "gemini-3.8-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash",
]


def _buscar_en_mapping(mapping, nombres):
    if not mapping:
        return ""
    for nombre in nombres:
        if nombre in mapping and mapping[nombre]:
            val = str(mapping[nombre]).strip()
            if val:
                return val
    return ""


def obtener_clave_secreta_gemini() -> str:
    nombres = ("GEMINI_API_KEY", "GOOGLE_API_KEY", "gemini_api_key", "google_api_key")
    clave_env = _buscar_en_mapping(os.environ, nombres)
    if clave_env:
        return clave_env
    try:
        clave_root = _buscar_en_mapping(st.secrets, nombres)
        if clave_root:
            return clave_root
        for seccion in ("general", "secrets", "api", "gemini"):
            if seccion in st.secrets and isinstance(st.secrets[seccion], dict):
                clave_sec = _buscar_en_mapping(st.secrets[seccion], nombres)
                if clave_sec:
                    return clave_sec
    except Exception:
        pass
    return ""


def construir_prompt_sistema(modo: str = "Copiloto General", contexto_extra: str = "") -> str:
    instruccion_modo = MODOS_CEREBRO.get(modo, MODOS_CEREBRO["Copiloto General"])
    partes = [JARVIS_SYSTEM_PROMPT, f"Modo activo: {modo}. {instruccion_modo}"]
    if contexto_extra.strip():
        partes.append(
            "Contexto de referencia cargado por el usuario:\n"
            f"{contexto_extra.strip()[:24000]}"
        )
    return "\n\n".join(partes)


def _formatear_error_http(resp: requests.Response) -> str:
    detalle = ""
    try:
        data = resp.json()
        err = data.get("error", {})
        detalle = err.get("message") or str(data)
    except Exception:
        detalle = (resp.text or "").strip()[:300]
    return f"HTTP {resp.status_code}" + (f": {detalle}" if detalle else "")


def _llamar_modelo_gemini_unico(
    mensajes,
    api_key: str,
    modelo: str,
    modo: str,
    contexto_extra: str,
    temperatura: float,
) -> str:
    modelo_limpio = (modelo or "gemini-3.8-flash").strip()
    if modelo_limpio.startswith("models/"):
        modelo_limpio = modelo_limpio.split("models/", 1)[1]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_limpio}:generateContent"
    headers = {"x-goog-api-key": api_key.strip(), "Content-Type": "application/json"}
    contents = [
        {
            "role": ("model" if m.get("role") == "assistant" else "user"),
            "parts": [{"text": (m.get("content") or "").strip()}],
        }
        for m in mensajes
        if (m.get("content") or "").strip()
    ]
    payload = {
        "system_instruction": {"parts": [{"text": construir_prompt_sistema(modo, contexto_extra)}]},
        "contents": contents,
        "generationConfig": {"temperature": temperatura},
    }

    ultimo_error = ""
    for intento in range(2):
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        if resp.ok:
            candidatos = resp.json().get("candidates", [])
            if not candidatos:
                return "No recibí respuesta del modelo en la nube, jefa."
            partes = candidatos[0].get("content", {}).get("parts", [])
            return "".join(p.get("text", "") for p in partes if "text" in p).strip() or "Respuesta vacía del modelo."
        ultimo_error = _formatear_error_http(resp)
        if resp.status_code in (429, 500, 502, 503, 504) and intento == 0:
            time.sleep(1.5)
            continue
        break

    raise RuntimeError(ultimo_error)


def consultar_gemini_api(
    mensajes,
    api_key: str,
    modelo: str = "gemini-3.8-flash",
    modo: str = "Copiloto General",
    contexto_extra: str = "",
    temperatura: float = 0.65,
):
    if not api_key:
        raise ValueError("Falta la API Key de Gemini (st.secrets, GEMINI_API_KEY o campo en interfaz).")

    principal = (modelo or "gemini-3.8-flash").strip()
    candidatos_modelos = [principal] + [m for m in MODELOS_RESPALDO_GEMINI if m != principal]
    errores = []

    for mod in candidatos_modelos:
        try:
            texto = _llamar_modelo_gemini_unico(
                mensajes, api_key, mod, modo, contexto_extra, temperatura
            )
            return texto, mod
        except Exception as err:
            msg_err = str(err)
            errores.append(f"{mod} -> {msg_err}")
            # Si la clave es inválida (400/401/403), no seguimos probando otros modelos
            if any(cod in msg_err for cod in ("HTTP 400", "HTTP 401", "HTTP 403")):
                raise RuntimeError(msg_err)

    raise RuntimeError(" | ".join(errores))


def listar_modelos_ollama(base_url: str = "http://localhost:11434"):
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=3)
        resp.raise_for_status()
        return [m.get("name", "") for m in resp.json().get("models", []) if m.get("name")]
    except Exception:
        return []


def consultar_ollama_local(
    mensajes,
    modelo: str = "llama3.1:8b",
    base_url: str = "http://localhost:11434",
    modo: str = "Copiloto General",
    contexto_extra: str = "",
    temperatura: float = 0.65,
) -> str:
    url = f"{base_url.rstrip('/')}/api/chat"
    chat_messages = [{"role": "system", "content": construir_prompt_sistema(modo, contexto_extra)}]
    for m in mensajes:
        rol = m.get("role") if m.get("role") in ("user", "assistant") else "user"
        texto = (m.get("content") or "").strip()
        if texto:
            chat_messages.append({"role": rol, "content": texto})
    payload = {
        "model": modelo.strip(),
        "messages": chat_messages,
        "stream": False,
        "options": {"temperature": temperatura},
    }
    resp = requests.post(url, json=payload, timeout=120)
    if not resp.ok:
        raise RuntimeError(_formatear_error_http(resp))
    return (resp.json().get("message", {}).get("content") or "").strip() or "Ollama devolvió una respuesta vacía."


def _es_entorno_local(ollama_url: str) -> bool:
    url = (ollama_url or "").lower()
    return ("localhost" in url or "127.0.0.1" in url) and os.path.exists("/mount/src") is False


def responder_jarvis(
    mensajes,
    motor: str = "Híbrido (API con respaldo Ollama)",
    gemini_api_key=None,
    gemini_modelo: str = "gemini-3.8-flash",
    ollama_modelo: str = "llama3.1:8b",
    ollama_url: str = "http://localhost:11434",
    modo: str = "Copiloto General",
    contexto_extra: str = "",
    temperatura: float = 0.65,
):
    clave_efectiva = (gemini_api_key or obtener_clave_secreta_gemini()).strip()
    if motor == "API Nube (Gemini)":
        try:
            texto, modelo_usado = consultar_gemini_api(
                mensajes, clave_efectiva, gemini_modelo, modo, contexto_extra, temperatura
            )
            return {"respuesta": texto, "motor_usado": f"Gemini API ({modelo_usado})"}
        except Exception as err_api:
            return {
                "respuesta": f"La API de Gemini devolvió un aviso, jefa:\n- {err_api}",
                "motor_usado": "Error Gemini API",
            }
    if motor == "Local (Ollama)":
        if not _es_entorno_local(ollama_url):
            return {
                "respuesta": "Ollama local no está disponible desde Streamlit Cloud en localhost, jefa. Usa API Nube o Híbrido con tu clave de Gemini.",
                "motor_usado": "Ollama no disponible en nube",
            }
        try:
            texto = consultar_ollama_local(
                mensajes, ollama_modelo, ollama_url, modo, contexto_extra, temperatura
            )
            return {"respuesta": texto, "motor_usado": f"Ollama Local ({ollama_modelo})"}
        except Exception as err_local:
            return {
                "respuesta": f"No pude conectarme a Ollama local, jefa:\n- {err_local}",
                "motor_usado": "Error Ollama",
            }
    try:
        texto, modelo_usado = consultar_gemini_api(
            mensajes, clave_efectiva, gemini_modelo, modo, contexto_extra, temperatura
        )
        return {"respuesta": texto, "motor_usado": f"Gemini API ({modelo_usado})"}
    except Exception as err_api:
        if _es_entorno_local(ollama_url):
            try:
                texto = consultar_ollama_local(
                    mensajes, ollama_modelo, ollama_url, modo, contexto_extra, temperatura
                )
                return {
                    "respuesta": f"*(Respaldo local activo tras aviso en API: {err_api})*\n\n{texto}",
                    "motor_usado": f"Ollama Local ({ollama_modelo})",
                }
            except Exception as err_local:
                return {
                    "respuesta": (
                        "No pude conectarme ni a la API ni a Ollama local, jefa.\n"
                        f"- Error API: {err_api}\n"
                        f"- Error Ollama: {err_local}"
                    ),
                    "motor_usado": "Sin conexión",
                }
        return {
            "respuesta": (
                "Los modelos de Gemini están con alta demanda temporal en este segundo, jefa:\n"
                f"- {err_api}\n"
                "Intenta reenviar el mensaje en unos segundos."
            ),
            "motor_usado": "Demanda alta temporal",
        }


st.session_state.setdefault("jarvis_chat", [])
st.session_state.setdefault("contexto_doc", "")
st.session_state.setdefault("gemini_key_sesion", obtener_clave_secreta_gemini())

with st.sidebar:
    st.markdown("### Núcleo de Cerebro")
    motor = st.selectbox(
        "Motor de lenguaje",
        ["Híbrido (API con respaldo Ollama)", "API Nube (Gemini)", "Local (Ollama)"],
    )
    modo = st.selectbox("Perfil operativo", list(MODOS_CEREBRO.keys()))
    temperatura = st.slider("Creatividad / Precisión", 0.1, 1.0, 0.65, 0.05)
    entrada_key = st.text_input(
        "Gemini API Key",
        value=st.session_state.gemini_key_sesion,
        type="password",
        key="input_gemini_key",
    )
    if entrada_key.strip():
        st.session_state.gemini_key_sesion = entrada_key.strip()
    elif not obtener_clave_secreta_gemini():
        st.session_state.gemini_key_sesion = ""

    if st.session_state.gemini_key_sesion:
        st.caption("Estado API Key: lista y detectada.")
    else:
        st.caption("Estado API Key: sin clave detectada (ingrésala y presiona Enter).")

    gemini_modelo = st.text_input("Modelo Gemini", value="gemini-3.8-flash")
    ollama_url = st.text_input("URL Ollama", value="http://localhost:11434")
    modelos_locales = listar_modelos_ollama(ollama_url) if _es_entorno_local(ollama_url) else []
    ollama_modelo = st.selectbox(
        "Modelo Ollama local",
        modelos_locales if modelos_locales else ["llama3.1:8b", "qwen2.5:7b", "mistral"],
    )
    if PYPDF_DISPONIBLE:
        archivo_pdf = st.file_uploader("Cargar PDF de consulta (opcional)", type=["pdf"])
        if archivo_pdf is not None:
            lector = PdfReader(archivo_pdf)
            st.session_state.contexto_doc = "\n".join(
                pagina.extract_text() or "" for pagina in lector.pages
            )
            st.caption(f"Documento cargado: {len(lector.pages)} páginas listas como contexto.")
    else:
        st.caption("Agrega 'pypdf' en requirements.txt para habilitar carga de PDF.")

for msg in st.session_state.jarvis_chat:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("motor"):
            st.caption(f"Vía: {msg['motor']}")

prompt = st.chat_input("Háblale a Jarvis...")
if prompt:
    st.session_state.jarvis_chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    resultado = responder_jarvis(
        mensajes=st.session_state.jarvis_chat,
        motor=motor,
        gemini_api_key=st.session_state.gemini_key_sesion,
        gemini_modelo=gemini_modelo,
        ollama_modelo=ollama_modelo,
        ollama_url=ollama_url,
        modo=modo,
        contexto_extra=st.session_state.contexto_doc,
        temperatura=temperatura,
    )
    st.session_state.jarvis_chat.append(
        {"role": "assistant", "content": resultado["respuesta"], "motor": resultado["motor_usado"]}
    )
    with st.chat_message("assistant"):
        st.markdown(resultado["respuesta"])
        st.caption(f"Vía: {resultado['motor_usado']}")

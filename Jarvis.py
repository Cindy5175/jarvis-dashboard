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


def _limpiar_clave(valor) -> str:
    if not valor:
        return ""
    limpia = "".join(str(valor).split()).strip()
    if (limpia.startswith('"') and limpia.endswith('"')) or (
        limpia.startswith("'") and limpia.endswith("'")
    ):
        limpia = limpia[1:-1].strip()
    return limpia


def _buscar_en_mapping(mapping, nombres):
    if not mapping:
        return ""
    for nombre in nombres:
        if nombre in mapping and mapping[nombre]:
            val = _limpiar_clave(mapping[nombre])
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


def _peticion_gemini_con_clave(
    url_base: str,
    clave: str,
    payload: dict,
    usar_query_key: bool = False,
) -> requests.Response:
    headers = {"Content-Type": "application/json"}
    params = None
    if usar_query_key:
        params = {"key": clave}
    else:
        headers["x-goog-api-key"] = clave
    return requests.post(url_base, headers=headers, params=params, json=payload, timeout=60)


def _llamar_modelo_gemini_unico(
    mensajes,
    api_key: str,
    modelo: str,
    modo: str,
    contexto_extra: str,
    temperatura: float,
) -> str:
    clave = _limpiar_clave(api_key)
    if not clave:
        raise ValueError("Falta la API Key de Gemini (st.secrets, GEMINI_API_KEY o campo en interfaz).")

    modelo_limpio = (modelo or "gemini-3.8-flash").strip()
    if modelo_limpio.startswith("models/"):
        modelo_limpio = modelo_limpio.split("models/", 1)[1]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_limpio}:generateContent"

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

    modos_envio = [True, False] if clave.startswith("AQ") else [False, True]
    ultimo_error = ""

    for usar_q in modos_envio:
        for intento in range(2):
            resp = _peticion_gemini_con_clave(url, clave, payload, usar_query_key=usar_q)
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
        if not any(cod in ultimo_error for cod in ("HTTP 400", "HTTP 401", "HTTP 403")):
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
    clave = _limpiar_clave(api_key)
    if not clave:
        raise ValueError("Falta la API Key de Gemini (st.secrets, GEMINI_API_KEY o campo en interfaz).")

    principal = (modelo or "gemini-3.8-flash").strip()
    candidatos_modelos = [principal] + [m for m in MODELOS_RESPALDO_GEMINI if m != principal]
    errores = []

    for mod in candidatos_modelos:
        try:
            texto = _llamar_modelo_gemini_unico(
                mensajes, clave, mod, modo, contexto_extra, temperatura
            )
            return texto, mod
        except Exception as err:
            msg_err = str(err)
            errores.append(f"{mod} -> {msg_err}")
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
    clave_efectiva = _limpiar_clave(gemini_api_key) or obtener_clave_secreta_gemini()

    if not clave_efectiva and motor in ("Híbrido (API con respaldo Ollama)", "API Nube (Gemini)"):
        return {
            "respuesta": (
                "No detecto una clave de Gemini activa en esta sesión, jefa.\n"
                "Pégala en el campo **Gemini API Key** de la barra lateral y presiona **Enter**, "
                "o guárdala en `Secrets` como `GEMINI_API_KEY`."
            ),
            "motor_usado": "Sin clave API",
        }

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
        msg_err = str(err_api)
        if "503" in msg_err or "high demand" in msg_err.lower() or "unavailable" in msg_err.lower():
            return {
                "respuesta": (
                    "Los modelos de Gemini están con alta demanda temporal en este segundo, jefa:\n"
                    f"- {msg_err}\n"
                    "Intenta reenviar el mensaje en unos segundos."
                ),
                "motor_usado": "Demanda alta temporal",
            }
        return {
            "respuesta": (
                "No pude conectarme a la API de Gemini, jefa:\n"
                f"- {msg_err

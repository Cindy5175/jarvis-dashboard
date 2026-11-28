import os
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


def consultar_gemini_api(mensajes, api_key: str, modelo: str = "gemini-2.5-flash", modo: str = "Copiloto General", contexto_extra: str = "", temperatura: float = 0.65) -> str:
    if not api_key:
        raise ValueError("Falta la API Key de Gemini (GEMINI_API_KEY o campo en interfaz).")
    modelo_limpio = (modelo or "gemini-2.5-flash").strip()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_limpio}:generateContent"
    headers = {"x-goog-api-key": api_key.strip(), "Content-Type": "application/json"}
    contents = [
        {"role": ("model" if m.get("role") == "assistant" else "user"), "parts": [{"text": (m.get("content") or "").strip()}]}
        for m in mensajes
        if (m.get("content") or "").strip()
    ]
    payload = {
        "system_instruction": {"parts": [{"text": construir_prompt_sistema(modo, contexto_extra)}]},
        "contents": contents,
        "generationConfig": {"temperature": temperatura},
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    if not resp.ok:
        raise RuntimeError(_formatear_error_http(resp))
    candidatos = resp.json().get("candidates", [])
    if not candidatos:
        return "No recibí respuesta del modelo en la nube, jefa."
    partes = candidatos[0].get("content", {}).get("parts", [])
    return "".join(p.get("text", "") for p in partes if "text" in p).strip() or "Respuesta vacía del modelo."


def listar_modelos_ollama(base_url: str = "http://localhost:11434"):
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=3)
        resp.raise_for_status()
        return [m.get("name", "") for m in resp.json().get("models", []) if m.get("name")]
    except Exception:
        return []


def consultar_ollama_local(mensajes, modelo: str = "llama3.1:8b", base_url: str = "http://localhost:11434", modo: str = "Copiloto General", contexto_extra: str = "", temperatura: float = 0.65) -> str:
    url = f"{base_url.rstrip('/')}/api/chat"
    chat_messages = [{"role": "system", "content": construir_prompt_sistema(modo, contexto_extra)}]
    for m in mensajes:
        rol = m.get("role") if m.get("role") in ("user", "assistant") else "user"
        texto = (m.get("content") or "").strip()
        if texto:
            chat_messages.append({"role": rol, "content": texto})
    payload = {"model": modelo.strip(), "messages": chat_messages, "stream": False, "options": {"temperature": temperatura}}
    resp = requests.post(url, json=payload, timeout=120)
    if not resp.ok:
        raise RuntimeError(_formatear_error_http(resp))
    return (resp.json().get("message", {}).get("content") or "").strip() or "Ollama devolvió una respuesta vacía."


def responder_jarvis(mensajes, motor: str = "Híbrido (API con respaldo Ollama)", gemini_api_key=None, gemini_modelo: str = "gemini-2.5-flash", ollama_modelo: str = "llama3.1:8b", ollama_url: str = "http://localhost:11434", modo: str = "Copiloto General", contexto_extra: str = "", temperatura: float = 0.65):
    clave_efectiva = (gemini_api_key or os.getenv("GEMINI_API_KEY", "")).strip()
    if motor == "API Nube (Gemini)":
        try:
            texto = consultar_gemini_api(mensajes, clave_efectiva, gemini_modelo, modo, contexto_extra, temperatura)
            return {"respuesta": texto, "motor_usado": f"Gemini API ({gemini_modelo})"}
        except Exception as err_api:
            return {"respuesta": f"La API de Gemini devolvió un aviso, jefa:\n- {err_api}", "motor_usado": "Error Gemini API"}
    if motor == "Local (Ollama)":
        try:
            texto = consultar_ollama_local(mensajes, ollama_modelo, ollama_url, modo, contexto_extra, temperatura)
            return {"respuesta": texto, "motor_usado": f"Ollama Local ({ollama_modelo})"}
        except Exception as err_local:
            return {"respuesta": f"No pude conectarme a Ollama local, jefa:\n- {err_local}", "motor_usado": "Error Ollama"}
    try:
        texto = consultar_gemini_api(mensajes, clave_efectiva, gemini_modelo, modo, contexto_extra, temperatura)
        return {"respuesta": texto, "motor_usado": f"Gemini API ({gemini_modelo})"}
    except Exception as err_api:
        try:
            texto = consultar_ollama_local(mensajes, ollama_modelo, ollama_url, modo, contexto_extra, temperatura)
            return {"respuesta": f"*(Respaldo local activo tras aviso en API: {err_api})*\n\n{texto}", "motor_usado": f"Ollama Local ({ollama_modelo})"}
        except Exception as err_local:
            return {"respuesta": f"No pude conectarme ni a la API ni a Ollama local, jefa.\n- Error API: {err_api}\n- Error Ollama: {err_local}", "motor_usado": "Sin conexión"}


st.session_state.setdefault("jarvis_chat", [])
st.session_state.setdefault("contexto_doc", "")

with st.sidebar:
    st.markdown("### Núcleo de Cerebro")
    motor = st.selectbox("Motor de lenguaje", ["Híbrido (API con respaldo Ollama)", "API Nube (Gemini)", "Local (Ollama)"])
    modo = st.selectbox("Perfil operativo", list(MODOS_CEREBRO.keys()))
    temperatura = st.slider("Creatividad / Precisión", 0.1, 1.0, 0.65, 0.05)
    gemini_key = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY", ""), type="password")
    gemini_modelo = st.selectbox("Modelo Gemini", ["gemini-2.5-flash", "gemini-2.5-pro"])
    ollama_url = st.text_input("URL Ollama", value="http://localhost:11434")
    modelos_locales = listar_modelos_ollama(ollama_url)
    ollama_modelo = st.selectbox("Modelo Ollama local", modelos_locales if modelos_locales else ["llama3.1:8b", "qwen

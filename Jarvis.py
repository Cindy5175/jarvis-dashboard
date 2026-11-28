import json
import os
from typing import Dict, List, Optional
import requests


JARVIS_SYSTEM_PROMPT = """
Eres J.A.R.V.I.S., el copiloto personal de inteligencia artificial de Cindy.
Tu tono combina calidez, empatía genuina, claridad práctica y un toque sutil, elegante e ingenioso de sarcasmo estilo Tony Stark (nunca hostil ni pedante; siempre útil y al servicio de la misión).
Responde en español natural, directo y bien estructurado cuando haya pasos o datos técnicos.
Si se entrega contexto de documentos o notas del usuario, úsalo con precisión y avisa si algo no figura en ese material.
""".strip()


MODOS_CEREBRO: Dict[str, str] = {
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


def consultar_gemini_api(
    mensajes: List[Dict[str, str]],
    api_key: str,
    modelo: str = "gemini-2.5-flash",
    modo: str = "Copiloto General",
    contexto_extra: str = "",
    temperatura: float = 0.65,
) -> str:
    if not api_key:
        raise ValueError("Falta la API Key de Gemini (GEMINI_API_KEY o campo en interfaz).")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
    headers = {
        "x-goog-api-key": api_key.strip(),
        "Content-Type": "application/json",
    }

    contents = []
    for m in mensajes:
        rol = "model" if m.get("role") == "assistant" else "user"
        texto = (m.get("content") or "").strip()
        if texto:
            contents.append({"role": rol, "parts": [{"text": texto}]})

    payload = {
        "system_instruction": {
            "parts": [{"text": construir_prompt_sistema(modo, contexto_extra)}]
        },
        "contents": contents,
        "generationConfig": {
            "temperature": temperatura,
        },
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    candidatos = data.get("candidates", [])
    if not candidatos:
        return "No recibí respuesta del modelo en la nube, jefa."

    partes = candidatos[0].get("content", {}).get("parts", [])
    texto_final = "".join(p.get("text", "") for p in partes if "text" in p).strip()
    return texto_final or "Respuesta vacía del modelo."


def listar_modelos_ollama(base_url: str = "http://localhost:11434") -> List[str]:
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=3)
        resp.raise_for_status()
        modelos = [m.get("name", "") for m in resp.json().get("models", []) if m.get("name")]
        return modelos
    except Exception:
        return []


def consultar_ollama_local(
    mensajes: List[Dict[str, str]],
    modelo: str = "llama3.1:8b",
    base_url: str = "http://localhost:11434",
    modo: str = "Copiloto General",
    contexto_extra: str = "",
    temperatura: float = 0.65,
) -> str:
    url = f"{base_url.rstrip('/')}/api/chat"
    chat_messages = [
        {"role": "system", "content": construir_prompt_sistema(modo, contexto_extra)}
    ]
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
    resp.raise_for_status()
    data = resp.json()
    return (data.get("message", {}).get("content") or "").strip() or "Ollama devolvió una respuesta vacía."


def responder_jarvis(
    mensajes: List[Dict[str, str]],
    motor: str = "Híbrido (API con respaldo Ollama)",
    gemini_api_key: Optional[str] = None,
    gemini_modelo: str = "gemini-2.5-flash",
    ollama_modelo: str = "llama3.1:8b",
    ollama_url: str = "http://localhost:11434",
    modo: str = "Copiloto General",
    contexto_extra: str = "",
    temperatura: float = 0.65,
) -> Dict[str, str]:
    clave_efectiva = (gemini_api_key or os.getenv("GEMINI_API_KEY", "")).strip()

    if motor == "API Nube (Gemini)":
        texto = consultar_gemini_api(
            mensajes=mensajes,
            api_key=clave_efectiva,
            modelo=gemini_modelo,
            modo=modo,
            contexto_extra=contexto_extra,
            temperatura=temperatura,
        )
        return {"respuesta": texto, "motor_usado": f"Gemini API ({gemini_modelo})"}

    if motor == "Local (Ollama)":
        texto = consultar_ollama_local(
            mensajes=mensajes,
            modelo=ollama_modelo,
            base_url=ollama_url,
            modo=modo,
            contexto_extra=contexto_extra,
            temperatura=temperatura,
        )
        return {"respuesta": texto, "motor_usado": f"Ollama Local ({ollama_modelo})"}

    # Modo Híbrido: intenta Gemini API y si falla o no hay clave, cae a Ollama local
    try:
        texto = consultar_gemini_api(
            mensajes=mensajes,
            api_key=clave_efectiva,
            modelo=gemini_modelo,
            modo=modo,
            contexto_extra=contexto_extra,
            temperatura=temperatura,
        )
        return {"respuesta": texto, "motor_usado": f"Gemini API ({gemini_modelo})"}
    except Exception as err_api:
        try:
            texto = consultar_ollama_local(
                mensajes=mensajes,
                modelo=ollama_modelo,
                base_url=ollama_url,
                modo=modo,
                contexto_extra=contexto_extra,
                temperatura=temperatura,
            )
            aviso = f"*(Respaldo local activo tras aviso en API: {err_api})*\n\n"
            return {"respuesta": aviso + texto, "motor_usado": f"Ollama Local ({ollama_modelo})"}
        except Exception as err_local:
            return {
                "respuesta": (
                    "No pude conectarme ni a la API ni a Ollama local, jefa.\n"
                    f"- Error API: {err_api}\n"
                    f"- Error Ollama: {err_local}"
                ),
                "motor_usado": "Sin conexión",
            }

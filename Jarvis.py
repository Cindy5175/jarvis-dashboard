import os
import re
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


def listar_modelos_ollama(base_url: str = "http://localhost:11434"):
    try:
        resp = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=3)
        resp.raise_for_status()
        return [m.get("name", "") for m in resp.json().get("models", []) if m.get("name")]
    except Exception:
        return []


def consultar_ollama(
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
    resp.raise_for_status()
    return (resp.json().get("message", {}).get("content") or "").strip() or "Ollama devolvió una respuesta vacía."


def cerebro_autonomo_sin_clave(prompt: str, modo: str, contexto_extra: str = "") -> str:
    texto = prompt.strip()
    lower = texto.lower()

    if contexto_extra.strip():
        palabras = [p for p in re.findall(r"\w+", lower) if len(p) > 3]
        oraciones = [s.strip() for s in re.split(r"(?<=[.!?])\s+", contexto_extra) if s.strip()]
        coincidencias = [
            s for s in oraciones if any(p in s.lower() for p in palabras[:6])
        ][:5]
        if coincidencias:
            hallazgos = "\n".join(f"- {c}" for c in coincidencias)
            return (
                f"Operando en **Modo Autónomo Sin Clave ({modo})**, jefa. "
                "Esto es lo más relevante que encontré en tu documento cargado:\n\n"
                f"{hallazgos}"
            )

    if any(k in lower for k in ("hola", "buenos dias", "buenas", "jarvis", "estas ahi")):
        return (
            "En línea y a tus órdenes, jefa. Sin depender de claves externas ni humores de servidores en la nube.\n\n"
            f"- **Perfil activo:** {modo}\n"
            "- **Frentes prioritarios:** 1) Sabor Casero (página y cobros), 2) Montessori, 3) Mejoras de Jarvis.\n"
            "- Si enciendes **Ollama** en local (o pegas una URL de túnel), activo al instante el modelo neuronal completo."
        )

    if "sabor casero" in lower:
        return (
            "Foco puesto en **Sabor Casero**, jefa:\n"
            "1. Validar que el botón de pago/Flow y la entrega digital en Netlify respondan sin fricción.\n"
            "2. Dejar clara la propuesta de valor y llamada a la acción arriba del pliegue.\n"
            "3. Probar una compra real de punta a punta antes de difundir."
        )

    if "montessori" in lower:
        return (
            "Foco puesto en **Montessori**, jefa:\n"
            "1. Definir el entregable concreto que debe quedar cerrado antes de Navidad.\n"
            "2. Dividirlo en bloques de 45 minutos sin multitarea.\n"
            "3. Dejar listo hoy el primer avance verificable."
        )

    return (
        f"Recibido en **Modo Autónomo Sin Clave ({modo})**, jefa: *\"{texto}\"*\n\n"
        "- Puedo buscar y extraer fragmentos si subes un **PDF** en la barra lateral.\n"
        "- Para conversación abierta con IA generativa sin claves API, enciende **Ollama** en tu PC "
        "y conecta su URL en la barra lateral."
    )


def responder_jarvis(
    mensajes,
    motor: str = "Automático (Ollama + Autónomo sin clave)",
    ollama_modelo: str = "llama3.1:8b",
    ollama_url: str = "http://localhost:11434",
    modo: str = "Copiloto General",
    contexto_extra: str = "",
    temperatura: float = 0.65,
):
    ultimo_prompt = mensajes[-1]["content"] if mensajes else ""

    if motor == "Autónomo Sin Clave (100% Offline)":
        resp = cerebro_autonomo_sin_clave(ultimo_prompt, modo, contexto_extra)
        return {"respuesta": resp, "motor_usado": "Núcleo Autónomo (Sin clave)"}

    if motor == "Ollama (Sin clave)":
        try:
            resp = consultar_ollama(
                mensajes, ollama_modelo, ollama_url, modo, contexto_extra, temperatura
            )
            return {"respuesta": resp, "motor_usado": f"Ollama ({ollama_modelo})"}
        except Exception as err:
            return {
                "respuesta": (
                    "No detecté Ollama activo en esa URL, jefa.\n"
                    f"- Detalle: {err}\n"
                    "- Asegúrate de tener Ollama abierto en tu PC o usa el modo **Automático**."
                ),
                "motor_usado": "Ollama desconectado",
            }

    try:
        resp = consultar_ollama(
            mensajes, ollama_modelo, ollama_url, modo, contexto_extra, temperatura
        )
        return {"respuesta": resp, "motor_usado": f"Ollama ({ollama_modelo})"}
    except Exception:
        resp = cerebro_autonomo_sin_clave(ultimo_prompt, modo, contexto_extra)
        return {"respuesta": resp, "motor_usado": "Núcleo Autónomo (Sin clave)"}


st.session_state.setdefault("jarvis_chat", [])
st.session_state.setdefault("contexto_doc", "")

with st.sidebar:
    st.markdown("### Núcleo de Cerebro")
    motor = st.selectbox(
        "Motor de lenguaje",
        [
            "Automático (Ollama + Autónomo sin clave)",
            "Ollama (Sin clave)",
            "Autónomo Sin Clave (100% Offline)",
        ],
    )
    modo = st.selectbox("Perfil operativo", list(MODOS_CEREBRO.keys()))
    temperatura = st.slider("Creatividad / Precisión", 0.1, 1.0, 0.65, 0.05)

    ollama_url = st.text_input("URL Ollama", value="http://localhost:11434")
    modelos_locales = listar_modelos_ollama(ollama_url)
    if modelos_locales:
        st.caption(f"Estado Ollama: conectado ({len(modelos_locales)} modelo(s)).")
    else:
        st.caption("Estado Ollama: en espera (activo respaldo autónomo sin clave).")

    ollama_modelo = st.selectbox(
        "Modelo Ollama",
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

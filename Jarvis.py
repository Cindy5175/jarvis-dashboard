import streamlit as st
import streamlit.components.v1 as components
import datetime
import random
import json
import os
import subprocess
import urllib.parse
import urllib.request
import urllib.error

# Configuración de página en modo ancho
st.set_page_config(
    page_title="J.A.R.V.I.S. // M.E.C.A. 4.0", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ARCHIVO DE MEMORIA PERSISTENTE LOCAL
MEMORY_FILE = "jarvis_memory.json"

def cargar_memoria():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "usuario": {
            "nombre": "Cindy",
            "titulo": "Jefa",
            "ubicacion": "Buin, Chile"
        },
        "notas": ["Búnker activado en Buin, Chile.", "Satélite Serafín en enlace estable."],
        "misiones": ["Verificar sistemas del búnker", "Sincronizar red táctica"],
        "preferencias_voz": {
            "voz_activa": "Español (Neutro)",
            "elevenlabs_api_key": "",
            "elevenlabs_voice_id": "21m00Tcm4TlvDq8ikWAM",
            "ai_api_key": ""
        }
    }

def guardar_memoria(memoria):
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, indent=4, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error guardando memoria: {e}")

if "memoria" not in st.session_state:
    st.session_state.memoria = cargar_memoria()

nombre_jefa = st.session_state.memoria.get("usuario", {}).get("nombre", "Cindy")
titulo_jefa = st.session_state.memoria.get("usuario", {}).get("titulo", "Jefa")
prefs_voz = st.session_state.memoria.get("preferencias_voz", {})
ai_api_key_guardada = prefs_voz.get("ai_api_key", "").strip()

# ARQUITECTURA OLLAMA LOCAL: DOBLE VÍA (FLUJO RÁPIDO + RAZONAMIENTO COMPLEJO)
def consultar_ollama_local(prompt_sistema, mensaje_usuario, modo_complejo=False):
    """Consulta al servidor local de Ollama (Llama 3 con doble motor: fluido o razonamiento profundo)"""
    url = "http://localhost:11434/api/generate"
    modelo_activo = "llama3:latest" if modo_complejo else "llama3"
    
    prompt_completo = f"{prompt_sistema}\n\nMensaje de la Jefa: {mensaje_usuario}"
    payload = {
        "model": modelo_activo,
        "prompt": prompt_completo,
        "stream": False,
        "options": {
            "temperature": 0.7 if modo_complejo else 0.4
        }
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            resultado = json.loads(response.read().decode('utf-8'))
            return resultado.get("response", "").strip()
    except Exception:
        try:
            payload["model"] = "llama3"
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
            with urllib.request.urlopen(req, timeout=10) as response:
                resultado = json.loads(response.read().decode('utf-8'))
                return resultado.get("response", "").strip()
        except Exception:
            return None

# FUNCIÓN PARA EJECUTAR ÓRDENES REALES EN EL SISTEMA
def ejecutar_orden_sistema(texto_comando):
    """Ejecuta comandos en Windows basados en la solicitud de la jefa"""
    texto = texto_comando.lower()
    try:
        if "bloc de notas" in texto or "notepad" in texto:
            subprocess.Popen(["notepad.exe"])
            return f"Abriendo el Bloc de notas de inmediato, {titulo_jefa} {nombre_jefa}. ¿Anotando otra genialidad?"
        elif "calculadora" in texto or "calc" in texto:
            subprocess.Popen(["calc.exe"])
            return f"Lanzando la calculadora, {titulo_jefa}. Supongo que verificar mis cálculos no está de más."
        elif "chrome" in texto or "navegador" in texto:
            subprocess.Popen(["start", "chrome"], shell=True)
            return f"Abriendo el navegador web, {titulo_jefa}. Despliéguese el internet ante ti."
        elif "explorador" in texto or "archivos" in texto:
            subprocess.Popen(["explorer.exe"])
            return f"Desplegando el explorador de archivos en pantalla, {titulo_jefa}."
        elif "terminal" in texto or "powershell" in texto or "consola" in texto:
            subprocess.Popen(["powershell.exe"])
            return f"Nueva terminal de comandos desplegada, {titulo_jefa}. Cuidado con romper el multiverso."
    except Exception as e:
        return f"Error ejecutando la orden física en el sistema: {e}"
    return None

cliente_ia = None
if ai_api_key_guardada:
    try:
        import google.generativeai as genai
        genai.configure(api_key=ai_api_key_guardada)
        cliente_ia = genai.GenerativeModel('gemini-1.5-flash')
    except Exception:
        pass

# INICIALIZAR ESTADOS
if "historial_chat" not in st.session_state:
    saludo_inicial = f"Sistema en línea, {titulo_jefa}. J.A.R.V.I.S. // IA Autónoma M.E.C.A 4.0 operando al 100% en Buin. Usa Win + H para dictar y presiona Enter para enviar."
    st.session_state.historial_chat = [
        {"remitente": "jarvis", "texto": saludo_inicial}
    ]

if "ultima_respuesta" not in st.session_state:
    st.session_state.ultima_respuesta = st.session_state.historial_chat[0]["texto"]

if "modo_central" not in st.session_state:
    st.session_state.modo_central = "multimedia"

# ESTILOS CSS TÁCTICOS NEÓN
st.markdown("""
    <style>
    .stApp, .main, [data-testid="stViewToolbar"], header { background-color: #000000 !important; color: #00d2ff !important; }
    .main-header { color: #00d2ff; font-family: 'Segoe UI', sans-serif; font-weight: 800; letter-spacing: 2px; text-align: center; margin-bottom: 0px; text-shadow: 0 0 10px rgba(0,210,255,0.5); }
    .holo-card { background-color: #000000; border: 1px solid #00d2ff; border-radius: 12px; padding: 12px; margin-bottom: 15px; box-shadow: 0 0 15px rgba(0, 210, 255, 0.3); }
    .holo-title { color: #00d2ff; font-size: 14px; font-weight: bold; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 6px; text-align: center; text-shadow: 0 0 8px rgba(0,210,255,0.4); }
    
    div[data-baseweb="select"], div[data-baseweb="select"] > div {
        background-color: #000000 !important;
        border-color: #00d2ff !important;
        color: #00d2ff !important;
        box-shadow: 0 0 10px rgba(0,210,255,0.3) !important;
    }
    div[data-baseweb="select"] span, div[data-baseweb="select"] div {
        background-color: #000000 !important;
        color: #00d2ff !important;
    }
    
    .stTextInput input, .stTextArea textarea { background-color: #000000 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; box-shadow: 0 0 8px rgba(0,210,255,0.3) !important; }
    label[data-testid="stWidgetLabel"] { color: #00d2ff !important; font-weight: bold !important; text-shadow: 0 0 5px rgba(0,210,255,0.4); }
    
    div.stButton > button, button[kind="secondaryFormSubmit"] { background-color: #000000 !important; color: #00d2ff !important; border: 1px solid #00d2ff !important; border-radius: 6px !important; font-weight: bold !important; width: 100% !important; box-shadow: 0 0 10px rgba(0, 210, 255, 0.3) !important; }
    div.stButton > button:hover, button[kind="secondaryFormSubmit"]:hover { background-color: #00d2ff !important; color: #000000 !important; box-shadow: 0 0 15px #00d2ff !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">J.A.R.V.I.S. // IA Autonoma ( M.E.C.A 4.0 )</h1>', unsafe_allow_html=True)
st.markdown("<hr style='margin: 5px 0 15px 0; border-color: rgba(0,210,255,0.3);'>", unsafe_allow_html=True)

# DEFINICIÓN DE COLUMNAS PRINCIPALES
col_telemetria, col_orbe, col_chat = st.columns([1, 1.4, 1.3])

with col_telemetria:
    st.markdown('<div class="holo-card"><div class="holo-title">⚙️ TELEMETRÍA DEL SISTEMA</div>', unsafe_allow_html=True)
    gauges_html = '<div style="display: flex; justify-content: space-around; align-items: center; padding: 5px 0; background: #000;"><div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">38%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">CPU</span></div><div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">57%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">RAM</span></div><div style="text-align: center;"><div style="width: 55px; height: 55px; border-radius: 50%; border: 3px solid #00d2ff; display: flex; align-items: center; justify-content: center; font-family: monospace; font-weight: bold; color: #00d2ff; box-shadow: 0 0 10px #00d2ff;">100%</div><span style="color: #00d2ff; font-size: 11px; margin-top: 4px; display: block;">PWR</span></div></div>'
    components.html(gauges_html, height=90)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="holo-card"><div class="holo-title">📍 BASE Y SATÉLITE</div>', unsafe_allow_html=True)
    globe_html = '<div

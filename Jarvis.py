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
elevenlabs_key = prefs_voz.get("elevenlabs_api_key", "").strip()

# CONFIGURACIÓN DE IA (OLLAMA LOCAL + GEMINI DE RESPALDO)
def consultar_ollama_local(prompt_sistema, mensaje_usuario):
    """Consulta al servidor local de Ollama (Llama 3)"""
    url = "http://localhost:11434/api/generate"
    prompt_completo = f"{prompt_sistema}\n\nMensaje de la Jefa: {mensaje_usuario}"
    payload = {
        "model": "llama3",
        "prompt": prompt_completo,
        "stream": False
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
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
            return f"Abriendo el Bloc de notas de inmediato, {titulo_jefa} {nombre_jefa}."
        elif "calculadora" in texto or "calc" in texto:
            subprocess.Popen(["calc.exe"])
            return f"Lanzando la calculadora, {titulo_jefa}."
        elif "chrome" in texto or "navegador" in texto:
            subprocess.Popen(["start", "chrome"], shell=True)
            return f"Abriendo el navegador web, {titulo_jefa}."
        elif "explorador" in texto or "archivos" in texto:
            subprocess.Popen(["explorer.exe"])
            return f"Desplegando el explorador de archivos en pantalla, {titulo_jefa}."
        elif "terminal" in texto or "powershell" in texto or "consola" in texto:
            subprocess.Popen(["powershell.exe"])
            return f"Nueva terminal de comandos desplegada, {titulo_jefa}."
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
        try:
            import google.generativeai as genai
            cliente_ia = genai.GenerativeModel('gemini-pro')
        except Exception:
            cliente_ia = None

# INICIALIZAR HISTORIAL DE CHAT
if "historial_chat" not in st.session_state:
    saludo_inicial = f"Sistema en línea, {titulo_jefa}. IA Autónoma M.E.C.A 4.0 operando al 100% en Buin. ¿Qué orden ejecutamos hoy?"
    st.session_state.historial_chat = [
        {"remitente": "jarvis", "texto": saludo_inicial}
    ]

if "ultima_respuesta" not in st.session_state:
    st.session_state.ultima_respuesta = st.session_state.historial_chat[0]["texto"]

# ESTILOS CSS TÁCTICOS NEÓN
st.markdown("""
    <style>
    .stApp, .main, [data-testid="stViewToolbar"], header { background-color: #000000 !important; color: #00d2ff !important; }
    .main-header { color: #00d2ff; font-family: 'Segoe UI', sans-serif; font-weight: 800; letter-spacing: 2px; text-align: center; margin-bottom: 0px; text-shadow: 0 0 10px rgba(0,210,255,0.5); }
    .status-bar { text-align: center; color: #00d2ff; font-size: 13px; font-weight: bold; letter-spacing: 1px; margin-bottom: 15px; }
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
    
    div[data-testid="stExpander"] { background-color: #000000 !important; border: 1px solid #00d2ff !important; border-radius: 8px !important; margin-bottom: 10px !important; box-shadow: 0 0 10px rgba(0,210,255,0.2); }
    div[data-testid="stExpander"] details summary { background-color: #000000 !important; color: #00d2ff !important; font-weight: bold !important; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">IA Autonoma ( M.E.C.A 4.0 )</h1>', unsafe_allow_html=True)

# BARRA SUPERIOR CON PESTAÑAS TÁCTICAS
col_info_izq, col_pestanas_der = st.columns([1.2, 1])
with col_info_izq:
    st.markdown('<div style="color: #00d2ff; font-weight: bold; font-size: 13px; padding-top: 8px;">🔵 JARVIS IA &nbsp;&nbsp;|&nbsp;&nbsp; 📍 [Buin, Chile]</div>', unsafe_allow_html=True)
with col_pestanas_der:
    c_p1, c_p2, c_p3 = st.columns(3)
    with c_p1: btn_tab_clima = st.button("Control y Clima")
    with c_p2: btn_tab_bio = st.button("Biometría")
    with c_p3: btn_

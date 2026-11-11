import streamlit as st
import os
import sys
import asyncio
import subprocess
import sqlite3
from datetime import datetime

# 1. Configuración de la página
st.set_page_config(page_title="JARVIS - Tactical Dashboard", layout="wide")

# 2. Estilos CSS (Misma estética limpia, simétrica y editorial)
st.markdown("""
<style>
    .stApp {
        background-color: #FAFAFA;
        color: #1A1A1A;
    }
    h1, h2, h3 {
        font-family: 'Georgia', serif;
        letter-spacing: -0.5px;
    }
    .stButton>button {
        background-color: #000000;
        color: #FFFFFF;
        border-radius: 2px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #C5A059;
        color: #FFFFFF;
    }
</style>
""", unsafe_allow_html=True)

# 3. Módulos de Backend de JARVIS (Los 3 puntos)
class JarvisMemory:
    def __init__(self, db_path="jarvis_memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                key_id TEXT PRIMARY KEY,
                fact_text TEXT,
                category TEXT
            )
        """)
        conn.commit()
        conn.close()

    def remember_fact(self, key_id: str, fact_text: str, category: str = "general"):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO memory (key_id, fact_text, category)
            VALUES (?, ?, ?)
        """, (key_id, fact_text, category))
        conn.commit()
        conn.close()

    def recall_context(self, query: str) -> list:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT fact_text FROM memory")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows if query.lower() in row[0].lower()]

class JarvisSystemExecutor:
    @staticmethod
    def open_application(app_name: str) -> str:
        try:
            if sys.platform == "win32":
                subprocess.Popen(f"start {app_name}", shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", app_name])
            else:
                subprocess.Popen([app_name])
            return f"Abriendo {app_name} de inmediato, señorita."
        except Exception as e:
            return f"No se pudo iniciar {app_name}: {str(e)}"

class JarvisCore:
    def __init__(self, name="JARVIS"):
        self.name = name

    async def process_voice_input(self, text_command: str) -> str:
        await asyncio.sleep(0.01) 
        return f"Procesado al instante. Ejecutando orden: '{text_command}'."

# Instancias de los motores
memory = JarvisMemory()
executor = JarvisSystemExecutor()
core = JarvisCore()

# 4. Encabezado principal simétrico y elegante
st.title("JARVIS — Tactical Assistant")
st.caption("Núcleo Operativo · Memoria Vectorial y Automatización de Alta Velocidad")
st.markdown("---")

# 5. Interfaz simétrica en 3 columnas (mismo aspecto visual editorial)
cols = st.columns(3)

with cols[0]:
    with st.container(border=True):
        st.subheader("1. Memoria Activa")
        st.write("Base de datos local para retener preferencias, rutinas y proyectos a largo plazo sin perder contexto histórico.")
        mem_input = st.text_input("Dato a recordar:", key="mem_input")
        if st.button("Guardar en Memoria", key="btn_mem"):
            memory.remember_fact(f"fact_{datetime.now().timestamp()}", mem_input)
            st.success("¡Dato registrado con éxito!")

with cols[1]:
    with st.container(border=True):
        st.subheader("2. Automatización")
        st.write("Control de comandos y ejecución de aplicaciones del sistema operativo de forma fluida y sin fricciones.")
        app_input = st.text_input("Aplicación/Comando:", "notepad", key="app_input")
        if st.button("Ejecutar Acción", key="btn_app"):
            res = executor.open_application(app_input)
            st.warning(res)

with cols[2]:
    with st.container(border=True):
        st.subheader("3. Núcleo de Latencia")
        st.write("Procesamiento de comandos de voz con respuesta instantánea y el tono afilado característico.")
        cmd_input = st.text_input("Comando de voz:", "Analizar sistema", key="cmd_input")
        if st.button("Procesar Comando", key="btn_core"):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            resp = loop.run_until_complete(core.process_voice_input(cmd_input))
            st.success(f"**JARVIS:** {resp}")

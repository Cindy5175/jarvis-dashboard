import streamlit as st
import os
import sys
import asyncio
import subprocess
import sqlite3
from datetime import datetime

# ==============================================================================
# CONFIGURACIÓN DE PÁGINA (STREAMLIT)
# ==============================================================================
st.set_page_config(page_title="JARVIS Dashboard", layout="wide")

# ==============================================================================
# ARCHITECTURAL MODULE: HIGH-SPEED & LOW LATENCY CORE (Punto 3)
# ==============================================================================
class JarvisCore:
    def __init__(self, name="JARVIS"):
        self.name = name

    async def process_voice_input(self, text_command: str) -> str:
        await asyncio.sleep(0.05) 
        return f"Procesado de inmediato, señorita. Ejecutando: '{text_command}'."


# ==============================================================================
# ARCHITECTURAL MODULE: LONG-TERM SQL MEMORY (Punto 1 - Compatible Cloud)
# ==============================================================================
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


# ==============================================================================
# ARCHITECTURAL MODULE: SYSTEM AUTOMATION & ACTIONS (Punto 2)
# ==============================================================================
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
            return f"Abriendo {app_name} de inmediato."
        except Exception as e:
            return f"No se pudo iniciar {app_name}: {str(e)}"


# ==============================================================================
# MAIN INTEGRATION ENGINE & UI
# ==============================================================================
st.title("🤖 JARVIS - Tactical Assistant")
st.caption("Sistema operativo local y control de comandos de alta velocidad")
st.markdown("---")

memory = JarvisMemory()
executor = JarvisSystemExecutor()
core = JarvisCore()

# Interfaz visual limpia en Streamlit
user_input = st.text_input("Ingrese comando para JARVIS:", "Analizar estado del sistema")

if st.button("Enviar Comando"):
    st.write(f"**Entrada:** {user_input}")
    
    # Memoria
    context = memory.recall_context(user_input)
    if context:
        st.info(f"Contexto recuperado: {context}")
        
    # Acciones
    if "abrir" in user_input.lower():
        app = user_input.lower().replace("abrir", "").strip()
        res_sys = executor.open_application(app)
        st.warning(res_sys)
        
    # Respuesta Core
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    response = loop.run_until_complete(core.process_voice_input(user_input))
    
    st.success(f"**JARVIS:** {response}")

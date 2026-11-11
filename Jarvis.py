import os
import sys
import asyncio
import subprocess
import sqlite3

# ==============================================================================
# MÓDULO 1: MEMORIA A LARGO PLAZO (SQLite liviano y compatible)
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
# MÓDULO 2: AUTONOMÍA Y EJECUCIÓN DE ACCIONES EN EL SISTEMA
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
            return f"Abriendo {app_name} de inmediato, señorita."
        except Exception as e:
            return f"No se pudo iniciar {app_name}: {str(e)}"


# ==============================================================================
# MÓDULO 3: NÚCLEO DE BAJA LATENCIA (Optimización de respuesta)
# ==============================================================================
class JarvisCore:
    def __init__(self, name="JARVIS"):
        self.name = name

    async def process_voice_input(self, text_command: str) -> str:
        # Simulación de respuesta inmediata optimizada
        await asyncio.sleep(0.01) 
        return f"Procesado al instante. Ejecutando orden: '{text_command}'."


# ==============================================================================
# CLASE INTEGRADORA UNIFICADA (Los 3 puntos en un solo bloque)
# ==============================================================================
class JarvisEngine:
    def __init__(self):
        self.memory = JarvisMemory()
        self.executor = JarvisSystemExecutor()
        self.core = JarvisCore()

    async def run_pipeline(self, user_input: str):
        # 1. Consulta en memoria
        context = self.memory.recall_context(user_input)
        
        # 2. Acciones del sistema si aplica
        action_result = None
        if "abrir" in user_input.lower():
            app = user_input.lower().replace("abrir", "").strip()
            action_result = self.executor.open_application(app)
            
        # 3. Respuesta rápida del núcleo
        response = await self.core.process_voice_input(user_input)
        
        return {
            "contexto": context,
            "accion": action_result,
            "respuesta": response
        }

import os
import sys
import asyncio
import subprocess
import chromadb
from chromadb.config import Settings

# ==============================================================================
# ARCHITECTURAL MODULE: HIGH-SPEED & LOW LATENCY CORE (Punto 3)
# ==============================================================================
class JarvisCore:
    def __init__(self, name="JARVIS"):
        self.name = name
        self.system_prompt = (
            "Eres JARVIS, un asistente de IA de alta precisión. "
            "Responde de forma concisa, fluida, eficiente y con un toque sutil "
            "de sarcasmo británico refinado."
        )

    async def process_voice_input(self, text_command: str) -> str:
        """
        Procesamiento de baja latencia simulado para respuesta inmediata.
        Aquí se conecta tu motor local (como Ollama/vLLM) o API directa.
        """
        # Flujo asíncrono para garantizar respuesta sin congelar la ejecución
        await asyncio.sleep(0.05) 
        return f"Procesado de inmediato, señorita. Ejecutando: '{text_command}'."


# ==============================================================================
# ARCHITECTURAL MODULE: LONG-TERM VECTOR MEMORY (Punto 1)
# ==============================================================================
class JarvisMemory:
    def __init__(self, db_path="./jarvis_memory_db"):
        # Base de datos vectorial local e independiente
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection(
            name="user_preferences_and_history"
        )

    def remember_fact(self, key_id: str, fact_text: str, metadata: dict = None):
        """Guarda preferencias, rutinas y datos de proyectos a largo plazo."""
        self.collection.upsert(
            documents=[fact_text],
            metadatas=[metadata or {"category": "general"}],
            ids=[key_id]
        )

    def recall_context(self, query: str, n_results: int = 2) -> list:
        """Recupera el contexto relevante antes de formular la respuesta."""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results.get("documents", [[]])[0]


# ==============================================================================
# ARCHITECTURAL MODULE: SYSTEM AUTOMATION & ACTIONS (Punto 2)
# ==============================================================================
class JarvisSystemExecutor:
    @staticmethod
    def open_application(app_name: str) -> str:
        """Ejecuta aplicaciones y procesos del sistema operativo por voz."""
        try:
            if sys.platform == "win32":
                # Comandos de ejecución rápida para Windows
                subprocess.Popen(f"start {app_name}", shell=True)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-a", app_name])
            else:
                subprocess.Popen([app_name])
            return f"Abriendo {app_name} de inmediato."
        except Exception as e:
            return f"No se pudo iniciar {app_name}: {str(e)}"

    @staticmethod
    def execute_custom_script(script_path: str) -> str:
        """Automatiza scripts o tareas locales en segundo plano."""
        if os.path.exists(script_path):
            subprocess.Popen([sys.executable, script_path])
            return f"Script {os.path.basename(script_path)} puesto en marcha."
        return "El archivo especificado no existe en el sistema."


# ==============================================================================
# MAIN INTEGRATION ENGINE (Estructura Simétrica y Limpia)
# ==============================================================================
class JarvisSystem:
    def __init__(self):
        self.core = JarvisCore()
        self.memory = JarvisMemory()
        self.executor = JarvisSystemExecutor()

    async def handle_pipeline(self, user_input: str):
        print(f"\n[ENTRADA DE VOZ]: {user_input}")

        # 1. Búsqueda en memoria vectorial (Punto 1)
        context = self.memory.recall_context(user_input)
        if context:
            print(f"[MEMORIA RETENIDA]: Contexto localizado -> {context}")

        # 2. Evaluación de comandos del sistema (Punto 2)
        lowered = user_input.lower()
        if "abrir" in lowered:
            app = lowered.replace("abrir", "").strip()
            status = self.executor.open_application(app)
            print(f"[ACCION EJECUTADA]: {status}")

        # 3. Respuesta de baja latencia con voz/sarcasmo (Punto 3)
        response = await self.core.process_voice_input(user_input)
        print(f"[JARVIS]: {response}")


# ==============================================================================
# PRUEBA DE EJECUCIÓN DEL MÓDULO UNIFICADO
# ==============================================================================
if __name__ == "__main__":
    jarvis = JarvisSystem()

    # Guardar preferencia inicial en memoria a largo plazo
    jarvis.memory.remember_fact(
        key_id="pref_01", 
        fact_text="A la usuaria le gusta la arquitectura limpia, simétrica y proyectos de alta velocidad.",
        metadata={"proyecto": "JARVIS"}
    )

    # Bucle asíncrono para respuesta instantánea
    async def main():
        await jarvis.handle_pipeline("Recordar mis preferencias y abrir notepad")

    asyncio.run(main())

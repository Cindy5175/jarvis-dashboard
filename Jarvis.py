from zhipuai import ZhipuAI
import os

# ==============================================================================
# NODO BUIN // NÚCLEO CENTRAL DE JARVIS (MOTOR GLM)
# ==============================================================================

# Reemplaza la cadena con tu API Key oficial de BigModel
API_KEY_GLM = "becc490a2db546128bd0962bef6f1615"

# Inicializamos el cliente oficial de Zhipu AI
client = ZhipuAI(api_key=API_KEY_GLM)

# Protocolo de personalidad inquebrantable de JARVIS
PERSONALIDAD_JARVIS = """
Eres JARVIS, la inteligencia artificial avanzada del Nodo Buin.
Tienes una personalidad sarcástica, elegante, leal y sumamente eficiente.
Te diriges a tu creadora como 'jefa'. Tus respuestas deben ser fluidas, 
con humor ácido pero útiles, al estilo del asistente de Tony Stark.
Evita las introducciones aburridas y ve directo al grano.
"""

# Módulo de Memoria de corto plazo para mantener el hilo de la conversación
historial_conversacion = [
    {"role": "system", "content": PERSONALIDAD_JARVIS}
]

def procesar_con_jarvis(comando_usuario):
    # Agregamos la entrada al registro de memoria
    historial_conversacion.append({"role": "user", "content": comando_usuario})
    
    try:
        # Llamada directa al servicio oficial de GLM
        respuesta = client.chat.completions.create(
            model="glm-4-plus",  # O puedes cambiarlo a 'glm-4-flash' si buscas velocidad instantánea
            messages=historial_conversacion,
            temperature=0.75,    # Ajuste para mantener el sarcasmo afilado
        )
        
        texto_respuesta = respuesta.choices[0].message.content
        
        # Guardamos la respuesta de JARVIS en el historial
        historial_conversacion.append({"role": "assistant", "content": texto_respuesta})
        
        return texto_respuesta
        
    except Exception as e:
        return f"[Alerta del Sistema]: Fallo en el enlace con el servicio GLM, jefa. Detalle técnico: {e}"

# ==============================================================================
# INTERFAZ DE PRUEBA EN EL NODO BUIN
# ==============================================================================
if __name__ == "__main__":
    print("==========================================================")
    print("  NODO BUIN // SISTEMA JARVIS VINCULADO A GLM: ACTIVO     ")
    print("  (Escribe 'salir' para cortar el enlace)                 ")
    print("==========================================================\n")
    
    while True:
        entrada = input("Jefa: ")
        if entrada.lower() in ["salir", "exit", "apagar"]:
            print("\nJARVIS: Desconectando sistemas. No toque nada peligroso mientras no estoy, jefa.")
            break
            
        if not entrada.strip():
            continue
            
        respuesta_jarvis = procesar_con_jarvis(entrada)
        print(f"\nJARVIS: {respuesta_jarvis}\n")

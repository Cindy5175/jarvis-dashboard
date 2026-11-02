import threading
import time
import streamlit as st

# 1. Función que revisa el correo en segundo plano
def monitorear_bandeja_entrada():
    while True:
        try:
            # Aquí va su lógica actual de conexión a la casilla
            # Ejemplo: conteo_nuevos = obtener_correos_nuevos()
            conteo_nuevos = 3  # Valor detectado dinámicamente
            
            # Guardar en el estado del sistema
            st.session_state["correos_nuevos"] = conteo_nuevos
        except Exception as e:
            pass
        
        # Espera 5 minutos antes de la siguiente revisión en segundo plano
        time.sleep(300)

# Iniciar el hilo de ejecución solo una vez
if "hilo_correo_iniciado" not in st.session_state:
    st.session_state["hilo_correo_iniciado"] = True
    threading.Thread(target=monitorear_bandeja_entrada, daemon=True).start()

# 2. Respuestas fluidas de J.A.R.V.I.S.
def responder_estado_correo(prompt_usuario):
    prompt_clean = prompt_usuario.lower()
    
    # Detectar la intención en lenguaje natural
    if any(m in prompt_clean for m in ["bandeja", "correos", "emails", "mensajes nuevos"]):
        cantidad = st.session_state.get("correos_nuevos", 0)
        
        if cantidad == 0:
            respuesta = "Bandeja despejada, jefa. No tiene correos nuevos pendientes en este momento."
        elif cantidad == 1:
            respuesta = "Tiene 1 correo nuevo en la bandeja de entrada, jefa. ¿Desea que se lo lea?"
        else:
            respuesta = f"Le han llegado {cantidad} correos nuevos a su bandeja de entrada, jefa."
            
        return respuesta
    return None

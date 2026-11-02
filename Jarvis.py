import threading
import time
import streamlit as st

# --- MONITOREO DE CORREO EN SEGUNDO PLANO ---
def monitorear_bandeja_entrada():
    while True:
        try:
            # Conexión/Conteo automático de correo
            # (Aquí va la lectura real de su bandeja)
            st.session_state["correos_nuevos"] = st.session_state.get("correos_nuevos", 3)
        except Exception:
            pass
        time.sleep(300) # Revisa cada 5 minutos

if "hilo_correo_iniciado" not in st.session_state:
    st.session_state["hilo_correo_iniciado"] = True
    threading.Thread(target=monitorear_bandeja_entrada, daemon=True).start()

# --- RESPUESTA FLUIDA DE J.A.R.V.I.S. ---
def procesar_mando_voz(comando_texto):
    cmd = comando_texto.lower()
    
    if any(palabra in cmd for palabra in ["bandeja", "correo", "correos", "mensajes"]):
        cantidad = st.session_state.get("correos_nuevos", 0)
        if cantidad == 0:
            return "Bandeja despejada, jefa. No tiene correos nuevos pendientes."
        elif cantidad == 1:
            return "Tiene 1 correo nuevo en la bandeja de entrada, jefa. ¿Se lo leo?"
        else:
            return f"Le han llegado {cantidad} correos nuevos a su bandeja de entrada, jefa."
            
    return "Comando recibido, jefa."

import streamlit as st

# --- SU DISEÑO ORIGINAL DE COLUMNAS ---
col_izq, col_der = st.columns(2)

with col_izq:
    # Aquí van sus módulos de la columna izquierda
    st.markdown("### Módulos Izquierda")
    # Ejemplo de su caja de entrada original
    orden_usuario = st.text_input("Escriba su orden...")

with col_der:
    # Aquí van sus módulos de la columna derecha
    st.markdown("### Módulos Derecha")
    
# Lógica síncrona para responder a su bandeja sin congelar la app
if orden_usuario:
    cmd = orden_usuario.lower()
    if any(p in cmd for p in ["bandeja", "correo", "correos", "mensajes", "email"]):
        cantidad_nuevos = 0  # Reemplazar con su lógica de lectura real
        if cantidad_nuevos == 0:
            st.success("Bandeja despejada, jefa. No tiene correos nuevos pendientes.")
        else:
            st.success(f"Le han llegado {cantidad_nuevos} correos nuevos a su bandeja.")
    else:
        st.info(f"Comando recibido: '{orden_usuario}'")

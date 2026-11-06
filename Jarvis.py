with st.expander("📷 Cámara en Vivo: Espacio (ISS)"):
            st.markdown("Transmisión óptica orbital de la Estación Espacial.")
            if "activar_iss" not in st.session_state:
                st.session_state.activar_iss = False
            
            if st.button("🔴 Conectar Feed ISS", key="btn_iss"):
                st.session_state.activar_iss = not st.session_state.activar_iss
            
            if st.session_state.activar_iss:
                st.success("Feed orbital enlazado.")
                st.video("https://www.youtube.com/watch?v=4QJEibrt9B8")
            else:
                st.info("Feed en espera de activación manual.")

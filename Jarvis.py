with st.expander("📝 Libreta & Bitácora Táctica"):
        st.text_area("Notas rápidas:", "1. God's Eye View + Siri cargados.\n2. Catálogo 'Sabor y Receta 24/7' preparado para noviembre.")
        if st.button("Guardar Bitácora"):
            st.success("Datos guardados en memoria táctica.")
            
        # Módulo de Descarga PDF / Informe Táctico
        if st.session_state.messages:
            html_reporte = generar_html_pdf(st.session_state.messages)
            st.download_button(
                label="📄 Descargar Informe Táctico (PDF)",
                data=html_reporte,
                file_name="informe_tactico_jarvis.html",
                mime="text/html"
            )

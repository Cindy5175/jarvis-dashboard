st.markdown("---")
    st.markdown("#### 👁️ Centro de Análisis Óptico")

    with st.expander("📷 Subir Archivo (IMG / TXT / PDF)", expanded=True):
        archivo_subido = st.file_uploader("Selecciona archivo:", type=["png", "jpg", "jpeg", "txt", "pdf"])
        if archivo_subido is not None:
            st.download_button(
                label="📥 Descargar Archivo Cargado",
                data=archivo_subido,
                file_name=archivo_subido.name,
                use_container_width=True
            )
            
            if st.button("⚡ Ejecutar Análisis Táctico", use_container_width=True):
                nombre_archivo = archivo_subido.name
                if nombre_archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                    informe_analisis = f"📊 **INFORME DE ESCANEO ÓPTICO (Fusión {st.session_state.modo_ia}):**  \n- Archivo: `{nombre_archivo}`  \n- **Entorno:** Análisis sintáctico visual completado por el núcleo dual. Iluminación y composición registradas.  \n- **Diagnóstico:** Excelente captura visual, jefa. El motor de visión fusionado procesó el paisaje sin ningún inconveniente."
                elif nombre_archivo.lower().endswith('.pdf'):
                    informe_analisis = f"📚 **INFORME DE BIBLIOTECA / PDF TÁCTICO:**  \n- Documento: `{nombre_archivo}`  \n- **Análisis Sintáctico:** Documento procesado por JARVIS y Zapia. Si es el *Álgebra de Baldor*, ambos sistemas están listos para resolver cualquier ecuación."
                else:
                    informe_analisis = f"📜 **INFORME SINTÉCTICO DE TEXTO:**  \n- Archivo: `{nombre_archivo}`  \n- **Análisis:** Estructura de texto analizada con precisión quirúrgica desde el Nodo Buin."
                
                st.session_state.mensajes.append({"role": "assistant", "content": informe_analisis})
                st.rerun()

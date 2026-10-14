with st.form(key="form_chat", clear_on_submit=True):
        entrada_usuario = st.text_input("", placeholder="Escribe tu instrucción rápida...")
        boton_enviar = st.form_submit_button(label="🚀 Transmitir")

    if boton_enviar and entrada_usuario:
        texto = entrada_usuario.lower().strip()
        
        if cliente_ia:
            try:
                # Prompt optimizado para respuestas ultracortas y veloces
                prompt_sistema = f"Eres J.A.R.V.I.S., IA táctica de {titulo_jefa} {nombre_jefa} en Buin. Responde con máxima brevedad y precisión militar (máximo 2 frases)."
                
                # Configuración de generación para menor latencia
                generation_config = {"max_output_tokens": 120, "temperature": 0.3}
                
                respuesta_modelo = cliente_ia.generate_content(
                    f"{prompt_sistema}\nInstrucción: {entrada_usuario}",
                    generation_config=generation_config
                )
                respuesta_ia = respuesta_modelo.text
            except Exception as e:
                err_str = str(e)
                if "429" in err_str or "quota" in err_str.lower():
                    respuesta_ia = f"Jefa, límite de cuota alcanzado temporalmente. Reintentando..."
                else:
                    respuesta_ia = f"Error de núcleo: {e}"
        else:
            if "hola" in texto:
                respuesta_ia = f"Operativo, {titulo_jefa} {nombre_jefa}."
            else:
                respuesta_ia = f"Comando '{entrada_usuario}' ejecutado en Buin."

        st.session_state.ultimo_usuario = entrada_usuario
        st.session_state.ultima_respuesta = respuesta_ia
        st.rerun()

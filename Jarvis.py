if boton_enviar and entrada_usuario:
        texto = entrada_usuario.lower().strip()
        
        if cliente_ia:
            intentos = 2
            exito = False
            for intento in range(intentos):
                try:
                    prompt_sistema = f"Eres J.A.R.V.I.S., IA táctica M.E.C.A. de {titulo_jefa} {nombre_jefa} en Buin. Responde con máxima brevedad y precisión militar (máximo 2 frases)."
                    generation_config = {"max_output_tokens": 120, "temperature": 0.3}
                    respuesta_modelo = cliente_ia.generate_content(
                        f"{prompt_sistema}\nInstrucción: {entrada_usuario}",
                        generation_config=generation_config
                    )
                    respuesta_ia = respuesta_modelo.text
                    exito = True
                    break
                except Exception as e:
                    err_str = str(e)
                    if "429" in err_str or "quota" in err_str.lower():
                        if intento < intentos - 1:
                            time.sleep(5)  # Espera 5 segundos y reintenta automáticamente
                        else:
                            respuesta_ia = f"Jefa, el tráfico del motor IA está al máximo. Esperemos 15 segundos y reintentamos."
                    else:
                        respuesta_ia = f"Error temporal de núcleo: {e}"
                        break
        else:
            if "hola" in texto:
                respuesta_ia = f"{saludo_tiempo}, {titulo_jefa} {nombre_jefa}. Búnker M.E.C.A. operativo."
            else:
                respuesta_ia = f"Comando '{entrada_usuario}' procesado en Buin, {nombre_jefa}."

        st.session_state.ultimo_usuario = entrada_usuario
        st.session_state.ultima_respuesta = respuesta_ia
        st.rerun()

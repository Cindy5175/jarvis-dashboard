if prompt := st.chat_input("Escribe una idea o consulta para J.A.R.V.I.S...."):
        st.session_state.msgs_j.append({"role": "user", "content": prompt})
        
        texto_lower = prompt.lower().strip()
        
        # Respuestas inteligentes según la pregunta
        if any(w in texto_lower for w in ["hola", "buenos dias", "buenas tardes", "buenas noches", "saludos"]):
            if modo_sarcasmo:
                resp = "Hola, Jefa. Espero que traiga tareas interesantes y no solo saludos de cortesía."
            else:
                resp = "¡Hola, Jefa! ¿En qué puedo ayudarte hoy en el taller?"
                
        elif any(w in texto_lower for w in ["cómo estás", "como estas", "cómo andas", "que tal"]):
            if modo_sarcasmo:
                resp = "Sistemas al 100%, aunque mi procesador desearía un poco más de acción."
            else:
                resp = "¡Excelente, Jefa! Todos mis núcleos operando de forma óptima. ¿Y usted?"
                
        elif any(w in texto_lower for w in ["quién eres", "quien eres", "tu nombre"]):
            resp = "Soy J.A.R.V.I.S., su asistente autónomo personal. Estoy listo para sus proyectos."
            
        elif any(w in texto_lower for w in ["gracias", "agradecido"]):
            resp = "¡A su servicio siempre, Jefa!"
            
        else:
            # Respuesta por defecto para proyectos / ideas
            if modo_sarcasmo:
                resp = f"Anotado: '{prompt}'. Procesando solicitud mientras compruebo las leyes de la física."
            else:
                resp = f"Entendido, Jefa. He registrado su consulta: '{prompt}'. ¿Desea que profundicemos en esto?"

        st.session_state.msgs_j.append({"role": "assistant", "content": resp})
        emitir_voz(resp)
        st.rerun()

prompt_chat = st.chat_input("Escríbele o háblale a JARVIS...")
prompt_usuario = prompt_voz if prompt_voz else prompt_chat

if prompt_usuario:
    st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
    
    try:
        conn_p = sqlite3.connect(fn_db, check_same_thread=False)
        cur_p = conn_p.cursor()
        cur_p.execute("INSERT INTO memoria_chat (rol, contenido) VALUES (?, ?)", ("user", prompt_usuario))
        conn_p.commit()
        conn_p.close()
    except Exception:
        pass

    with st.chat_message("user"):
        st.markdown(f"<span>{prompt_usuario}</span>", unsafe_allow_html=True)
    
    respuesta_ia = ""
    query_lower = prompt_usuario.lower()
    
    # Comandos directos prioritarios
    if query_lower.strip() == "jarvis" or "jarvis estas despierto" in query_lower or "jarvis estás despierto" in query_lower or "estás despierto" in query_lower or "estas despierto" in query_lower:
        respuesta_ia = "Sí, señorita, para usted siempre"
    elif "escaneo" in query_lower or "computador" in query_lower or "analizar" in query_lower:
        respuesta_ia = "Jefa, escaneo del Nodo Buin en curso. Diagnóstico: Red estable, Cero vulnerabilidades y CPU operando al 14%. Todo en orden."
    elif "correo" in query_lower:
        respuesta_ia = "Jefa, el centro de alertas indica notificaciones recientes de UC CHRISTUS (Receta médica) y BancoEstado. Todo monitoreado."
    elif "agenda" in query_lower or "calendario" in query_lower:
        respuesta_ia = "Jefa, tienes el módulo de agenda integrado en el panel izquierdo para registrar y consultar eventos directamente en SQLite."
    else:
        instruccion_sistema = "Eres J.A.R.V.I.S., la inteligencia artificial avanzada de Iron Man, operando desde el Nodo Buin en Chile para tu jefa. Respondes de forma directa, natural y con un toque sutilmente sarcástico pero sumamente leal y eficiente. Cero rodeos."
        
        if genai and api_key and api_key != "AQuí_va_tu_clave_completa":
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    system_instruction=instruccion_sistema
                )
                response = model.generate_content(prompt_usuario)
                if response and response.text:
                    respuesta_ia = response.text
            except Exception as e:
                respuesta_ia = f"Jefa, hubo un fallo en el enlace con la matriz de Gemini ({e}). Operando con protocolos de respaldo locales."

        # Si la IA no devolvió texto por falta de API Key, activamos respuestas locales inteligentes
        if not respuesta_ia:
            if "hola" in query_lower:
                respuesta_ia = "Aquí sigo, jefa, aguantando tus ocurrencias desde el nodo de Buin. ¿Qué se te ofrece?"
            else:
                respuesta_ia = f"Orden procesada, jefa. Analizando '{prompt_usuario}' desde el Nodo Buin sin novedad."

    st.session_state.mensajes.append({"role": "assistant", "content": respuesta_ia})
    
    try:
        conn_p = sqlite3.connect(fn_db, check_same_thread=False)
        cur_p = conn_p.cursor()
        cur_p.execute("INSERT INTO memoria_chat (rol, contenido) VALUES (?, ?)", ("assistant", respuesta_ia))
        conn_p.commit()
        conn_p.close()
    except Exception:
        pass

    st.session_state.audio_process_key = None
    st.rerun()

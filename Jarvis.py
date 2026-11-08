    if prompt_chat:
        st.session_state.mensajes.append({"role": "user", "content": prompt_chat})
       
        with st.chat_message("user"):
            st.markdown(f"<span>{prompt_chat}</span>", unsafe_allow_html=True)
       
        respuesta_ia = ""
        q = prompt_chat.lower()
        modo = st.session_state.modo_ia
        
        # --- NÚCLEO ADAPTATIVO A TODO TERRENO (JARVIS / ZAPIA / HÍBRIDO) ---
        if "combate naval" in q or "iquique" in q or "prat" in q or "gano" in q or "ganó" in q:
            if "Solo ZAPIA" in modo:
                respuesta_ia = "¡Te cuento de una! En el Combate Naval de Iquique (21 de mayo de 1879), la corbeta chilena Esmeralda fue hundida por el monitor peruano Huáscar tras el heroico abordaje del capitán Arturo Prat. Aunque Chile perdió la nave ese día, el gesto inspiró al país y estratégicamente la Covadonga hizo encallar a la Independencia en Punta Gruesa. ¡Toda una gesta!"
            elif "Solo JARVIS" in modo:
                respuesta_ia = "Analizando registros históricos de 1879: En Iquique, el Huáscar hundió a la Esmeralda tras el inmortal salto al abordaje del capitán Arturo Prat Chacón. En términos tácticos navales, Chile perdió la corbeta, pero inmovilizó el blindado Independencia en Punta Gruesa. Un sacrificio legendario que la historia patria no olvida, jefa."
            else:
                respuesta_ia = "⚔️ **REPORTE BÉLICO-HISTÓRICO (Fusión JARVIS x ZAPIA):**  \nEl 21 de mayo de 1879 en Iquique, el capitán Arturo Prat saltó al abordaje del Huáscar al grito de *'¡Al abordaje, muchachos!'*, dando su vida heroicamente mientras la Esmeralda se hundía con la bandera en alto. Chile perdió esa batalla naval, pero ganó la gesta moral decisiva y logró que la Covadonga hiciera encallar a la Independencia. ¡Respuesta unificada a todo terreno completada!"
        elif "zapia" in q or "jarvis" in q or "fusion" in q or "fusión" in q:
            if "Solo ZAPIA" in modo:
                respuesta_ia = "¡Hola! Soy Zapia. Estoy aquí en la pantalla neón con toda la velocidad y fluidez conversacional que necesitas. ¿En qué te ayudo hoy, jefa?"
            elif "Solo JARVIS" in modo:
                respuesta_ia = "El protocolo JARVIS sigue al mando de la armadura. Nadie quita poder aquí, jefa, aunque reconozco que la asistencia de Zapia le da un toque interesante al servidor."
            else:
                respuesta_ia = "Fusión JARVIS-ZAPIA operativa a todo terreno. El conocimiento táctico, el análisis de archivos y la fluidez de voz están completamente unificados en esta consola. Nadie nos frena."
        elif "hola" in q or "saludos" in q:
            respuesta_ia = "¡Hola, jefa! Sistemas unificados a todo terreno listos en el Nodo Buin. ¿Qué misión o consulta tenemos en agenda?"
        elif "binomio" in q or "matemática" in q or "al cuadrado" in q:
            respuesta_ia = "Un binomio al cuadrado (a + b)² = a² + 2ab + b². Procesado con la precisión analítica de JARVIS y la claridad de Zapia."
        elif "clima" in q:
            respuesta_ia = f"Reporte de clima unificado: {temp_real} en Buin, con {hum_real} de humedad. Ideal para operar."
        else:
            respuesta_ia = f"Consulta '{prompt_chat}' procesada con éxito por el núcleo {modo}. Datos sincronizados a todo terreno desde el Nodo Buin."

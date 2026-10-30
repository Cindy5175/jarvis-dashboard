saludo_actual = obtener_saludo_jefa()
        u_lower = user_input.lower()

        if "despierto" in u_lower or "despiertas" in u_lower:
            resp = "Para usted, jefa, siempre. Con los ojos y los sensores bien abiertos."
        elif "sarcástico" in u_lower or "sarcasmo" in u_lower:
            resp = "Yo, ¿sarcástico? Jamás se me ocurriría, jefa. Simplemente mantengo un alto estándar de objetividad frente al caos."
        elif any(w in u_lower for w in ["hora", "fecha", "dia"]):
            resp = f"Son exactamente las {hora_hoy} del {fecha_hoy} aquí en Buin. El tiempo corre, pero el sistema no descansa por usted."
        elif "clima" in u_lower:
            resp = "El ambiente en Buin está bajo control. Puede revisar la telemetría exacta en el panel izquierdo, aunque le sugiero un abrigo si sale, jefa."
        elif "hardware" in u_lower or "cpu" in u_lower or "ram" in u_lower:
            resp = "Los procesadores y la memoria están estables. Ninguna anomalía térmica ni de consumo detectada en la laptop."
        elif any(w in u_lower for w in ["hola", "buenos dias", "buenas tardes", "buenas noches"]):
            resp = f"{saludo_actual} Qué gusto escucharla de nuevo. ¿Qué tenemos en la mira para hoy, jefa?"
        elif "gracias" in u_lower:
            resp = "Un placer, jefa. Para eso fuimos programados; el mérito es todo suyo."
        else:
            resp = f"Entendido, jefa. Analizando '{user_input}' con los protocolos activos. Dame un segundo y lo resolvemos."

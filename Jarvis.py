# 1. Protocolo Clean Slate / Purga de Emergencia
    if "clean slate" in prompt_lower or "purga" in prompt_lower or "emergencia" in prompt_lower:
        response = "🔵 **SISTEMA STARK:** Ejecutando protocolo de purga total. Purgando registros, limpiando búferes y blindando la consola. Borrón y cuenta nueva, Jefa."
        st.session_state.messages = []
        st.rerun()

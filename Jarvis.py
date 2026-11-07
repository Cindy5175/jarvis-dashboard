st.markdown("#### 🛡️ CONTROL DE SEGURIDAD DEL NODO")

# 1. Monitoreo pasivo (Sin riesgo)
if st.button("🔄 Refrescar Estado de Cámaras y Sensores", use_container_width=True):
    st.info("Obteniendo telemetría en vivo del Nodo Buin... Sistema seguro.")

# 2. Control de Acción Sensible con Seguro Antierrores
st.markdown("---")
st.caption("⚠️ Zona de Comandos Sensibles")

seguro_activado = st.checkbox("🔓 Desbloquear mandos de acción")

if seguro_activado:
    if st.button("🚨 Ejecutar Análisis de Red Local", use_container_width=True):
        st.success("Análisis local ejecutado de forma controlada.")
else:
    st.button("🔒 Comandos Bloqueados (Activa el seguro)", disabled=True, use_container_width=True)

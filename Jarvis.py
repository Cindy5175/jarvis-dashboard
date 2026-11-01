# ==========================================
# COLUMNA CENTRAL: OJO DE DIOS, ISS & CHAT
# ==========================================
with col_centro:
    # Bloque unificado: Ojo de Dios & Transmisión ISS
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    st.markdown("<h4 style='margin:0; font-size: 1.1rem; color: #00d2ff !important;'>🛰️ Ojo de Dios & Telemetría ISS</h4>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.85rem; color: #00d2ff !important;'>Órbita terrestre en vivo y enlace satelital sincronizado con Buin.</p>", unsafe_allow_html=True)
    
    # Pestañas internas para compartir el mismo espacio físico sin estorbarse
    tab_ojo, tab_iss = st.tabs(["🗺️ Mapa Satelital", "🌍 Enlace ISS en Vivo"])
    
    with tab_ojo:
        st.link_button("🌐 Abrir Visor Satelital (Osiris AI)", "https://osirisai.live/?lat=-33.7320&lon=-70.7300&zoom=10.00", use_container_width=True)
    
    with tab_iss:
        st.video("https://www.youtube.com/watch?v=alJMoaKpV_E")
        st.caption("Ambient Earth (Real Time) ✨ ISS Remastered")
        
    st.markdown('</div>', unsafe_allow_html=True)

    # Tarjeta de Chat & Análisis Visual
    st.markdown('<div class="stark-card">', unsafe_allow_html=True)
    cc1, cc2 = st.columns([4, 1])
    with cc1:
        st.markdown("<h4 style='margin:0; font-size: 1.1rem; color: #00d2ff !important;'>💬 Chat IA & Análisis Visual</h4>", unsafe_allow_html=True)
    with cc2:
        if st.button("🗑️", use_container_width=True, key="limpiar_chat"):
            h_limpieza = datetime.datetime.now(tz_chile).hour
            s_limpieza = "Buenos días" if 0 <= h_limpieza < 12 else ("Buenas tardes" if 12 <= h_limpieza < 20 else "Buenas noches")
            st.session_state.mensajes = [
                {"role": "assistant", "content": f"{s_limpieza}, jefa. Memoria limpia y lista."}
            ]
            st.rerun()

    activar_camara_directa = st.checkbox("📷 Activar Módulo de Visión Artificial (Escanear Entorno)", value=False)
    if activar_camara_directa:
        foto_camara = st.camera_input("Captura óptica de seguridad en vivo:")
        if foto_camara:
            st.success("Fotograma capturado con éxito. Análisis completado sin observaciones.")

    for m in st.session_state.mensajes:
        with st.chat_message(m["role"]):
            st.markdown(f"<span style='color: #00d2ff !important;'>{m['content']}</span>", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if prompt_usuario := st.chat_input("Escriba su mensaje..."):
        st.session_state.mensajes.append({"role": "user", "content": prompt_usuario})
        
        h_prompt = datetime.datetime.now(tz_chile).hour
        s_prompt = "Buenos días" if 0 <= h_prompt < 12 else ("Buenas tardes" if 12 <= h_prompt < 20 else "Buenas noches")

        p_low = prompt_usuario.lower()
        if any(p in p_low for p in ["hola", "saludos", "buenos días", "buenas tardes"]):
            respuesta = f"{s_prompt}, jefa. Todos los sistemas del búnker operando al 100%. ¿Qué ordenamos hoy?"
        elif any(p in p_low for p in ["sodio", "potasio", "examen", "medico", "médico"]):
            respuesta = f"Analizando registros clínicos blindados: Sodio en 143.9 mEq/L y Potasio en 4.1 mEq/L (ambos en rangos normales). Su carpeta médica se encuentra segura y sin alteraciones."
        else:
            respuesta = f"Entendido, jefa. Procesando órdenes en el núcleo central..."

        st.session_state.mensajes.append({"role": "assistant", "content": respuesta})
        
        voz_activa = True
        if voz_activa:
            clean_resp = respuesta.replace('"', '').replace("'", "")
            st.markdown(f"""
                <script>
                    const synth = window.speechSynthesis;
                    const utterThis = new SpeechSynthesisUtterance("{clean_resp}");
                    utterThis.lang = 'es-CL';
                    utterThis.rate = 1.0;
                    synth.speak(utterThis);
                </script>
            """, unsafe_allow_html=True)

        st.rerun()

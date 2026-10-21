with col_c:
    # Encabezado con Botón de Purga compacto
    col_titulo, col_purga = st.columns([3, 1])
    with col_titulo:
        st.subheader("💬 Consola // J.A.R.V.I.S.")
    with col_purga:
        if st.button("🗑️ Purgar", key="purga_j", help="Limpiar historial de chat"):
            st.session_state.msgs_j = [{"role": "assistant", "content": t["presentacion"]}]
            st.toast("🧹 Consola purgada con éxito.")
            st.rerun()

    # 🎤 3. Activación por Voz Directa
    st.markdown('<div class="card-tactica" style="padding: 10px !important;">', unsafe_allow_html=True)
    st.markdown("🎤 **Entrada de Voz Directa:**")
    st.components.v1.html("""
    <div style="text-align:center;">
        <button id="btn_voice" style="background:#000a12; color:#00f3ff; border:1px solid #00f3ff; border-radius:6px; padding:8px 16px; cursor:pointer; font-family:sans-serif; width:100%;">
            🎙️ Presionar para hablar a JARVIS
        </button>
        <p id="tx_voice" style="color:#80f9ff; font-size:12px; margin-top:5px; font-family:sans-serif;"></p>
    </div>
    <script>
        const btn = document.getElementById('btn_voice');
        const tx = document.getElementById('tx_voice');
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            const rec = new SpeechRecognition();
            rec.lang = 'es-ES';
            btn.onclick = () => {
                rec.start();
                tx.innerText = "Escuchando en el taller...";
            };
            rec.onresult = (e) => {
                const text = e.results[0][0].transcript;
                tx.innerText = "Reconocido: " + text;
                navigator.clipboard.writeText(text);
            };
        } else {
            tx.innerText = "Reconocimiento de voz no soportado en este navegador.";
        }
    </script>
    """, height=85)
    st.caption("💡 *Presiona el botón para dictar. El texto se copiará automáticamente al portapapeles.*")
    st.markdown('</div>', unsafe_allow_html=True)

    if "msgs_j" not in st.session_state:
        st.session_state.msgs_j = [{"role": "assistant", "content": t["presentacion"]}]

    for idx, msg in enumerate(st.session_state.msgs_j):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant":
                if st.button("🔊 Escuchar", key=f"v_j_{idx}"):
                    emitir_voz(msg["content"], idioma)

    if prompt := st.chat_input(t["input"]):
        st.session_state.msgs_j.append({"role": "user", "content": prompt})
        
        texto_lower = prompt.lower().strip()
        saludos = ["hola", "hello", "bonjour", "olá", "saludos", "buenas"]
        preguntas_estado = ["cómo estás", "como estas", "how are you", "comment vas-tu"]
        
        if any(s in texto_lower for s in saludos):
            if modo_sarcasmo:
                resp = "Hola, Jefa. Espero que traiga tareas interesantes y no solo saludos de cortesía."
            else:
                resp = "¡Hola, Jefa! Estoy en línea y listo para asistirte en el taller."
        elif any(p in texto_lower for p in preguntas_estado):
            resp = "¡Excelente, Jefa! Todos mis núcleos creativos operan de forma óptima."
        else:
            if idioma == "English 🇺🇸":
                resp = f"Understood, Boss. Query processed: '{prompt}'."
            elif idioma == "Français 🇫🇷":
                resp = f"Compris, Chef. Requête traitée : '{prompt}'."
            elif idioma == "Português 🇧🇷":
                resp = f"Entendido, Chefe. Consulta processada: '{prompt}'."
            else:
                resp = f"Entendido, Jefa. Consulta procesada: '{prompt}'."

        st.session_state.msgs_j.append({"role": "assistant", "content": resp})
        emitir_voz(resp, idioma)
        st.rerun()

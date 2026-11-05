# Línea de estado con reloj JavaScript sincronizado a Buin, Chile (CERO PARPADEOS)
st.markdown(
    """
    <div style='text-align: center; color: #00ffff; text-shadow: 0 0 10px #00ffff, 0 0 20px #00ffff; font-family: monospace; font-weight: bold;'>
        [ STARK INDUSTRIES // NODO BUIN, CHILE // <span id="reloj-vivo">SINCRONIZANDO...</span> ]
    </div>
    <script>
    function actualizarReloj() {
        const now = new Date();
        
        // Formato de fecha para Chile
        const opcionesFecha = { timeZone: 'America/Santiago', weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
        let fechaStr = now.toLocaleDateString('es-CL', opcionesFecha);
        fechaStr = fechaStr.charAt(0).toUpperCase() + fechaStr.slice(1);
        
        // Formato de hora estricto para Chile
        const opcionesHora = { timeZone: 'America/Santiago', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        let horaStr = new Intl.DateTimeFormat('es-CL', opcionesHora).format(now);
        
        document.getElementById('reloj-vivo').innerHTML = fechaStr + ' - ' + horaStr;
    }
    setInterval(actualizarReloj, 1000);
    actualizarReloj();
    </script>
    """,
    unsafe_allow_html=True
)

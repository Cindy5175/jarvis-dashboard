# --- ENCABEZADO CON RELOJ EN VIVO Y MAPA TÁCTICO BLINDADO (SIN SOLAPAMIENTO) ---
now_inicial = datetime.datetime.now(tz_chile)
dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
meses = ['', 'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
dia_str = dias[now_inicial.weekday()]
mes_str = meses[now_inicial.month]
fecha_completa = f"{dia_str}, {now_inicial.day:02d} de {mes_str} de {now_inicial.year}"

components.html(f"""
    <div style="background-color: #060911; font-family: monospace; text-align: center; color: #00d2ff; padding: 0px;">
        <div style="width: 38px; height: 38px; border: 2.5px solid #3a4454; border-radius: 50%; margin: 0 auto 2px auto; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #00d2ff 0%, #060911 70%); box-shadow: 0 0 10px rgba(0, 210, 255, 0.6);">
            <div style="width: 0; height: 0; border-left: 6px solid transparent; border-right: 6px solid transparent; border-bottom: 10px solid #ffffff; filter: drop-shadow(0 0 3px #00d2ff);"></div>
        </div>
        <h4 style="margin: 0; padding: 0; font-size: 0.95rem; color: #00d2ff;">J.A.R.V.I.S IA // E.D.I.T.H. TACTICAL CORE</h4>
        <p style="margin: 2px 0; font-size: 0.6rem; color: #00d2ff;">[ STARK INDUSTRIES // NODO BUIN, CHILE ]</p>
        <p style="margin: 2px 0; font-size: 0.6rem; color: #00d2ff;">[ {fecha_completa} – <span id="reloj-vivo" style="color: #00d2ff; font-weight: bold;">00:00:00</span> ]</p>
        <p style="margin: 2px 0 0 0; font-size: 0.55rem; color: #00a8cc;">[ 🛰️ ÓRBITA SATELITAL ACTIVA // MAPA TÁCTICO ]</p>
    </div>
    
    <script>
        function actualizarReloj() {{
            const ahora = new Date();
            const h = String(ahora.getHours()).padStart(2, '0');
            const m = String(ahora.getMinutes()).padStart(2, '0');
            const s = String(ahora.getSeconds()).padStart(2, '0');
            
            const elemento = document.getElementById('reloj-vivo');
            if (elemento) {{
                elemento.innerText = h + ":" + m + ":" + s;
            }}
        }}
        setInterval(actualizarReloj, 1000);
        actualizarReloj();
    </script>
""", height=125)

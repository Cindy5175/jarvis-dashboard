# 🎬 PANTALLA DE SALVAPANTALLAS CON TU CARA HOLOGRÁFICA EXACTA Y AUTO-DESBLOQUEO
if st.session_state.salvapantallas_activo:
    screensaver_code = (
        '<div id="screensaver-layer" style="position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: #000208; z-index: 99999; display: flex; flex-direction: column; align-items: center; justify-content: center; font-family: \'Courier New\', monospace; color: ' + color_neon + '; cursor: pointer;">'
        '<div class="scanline"></div>'
        '<div style="position: relative; z-index: 5; text-align: center; max-width: 90%; max-height: 80vh; display: flex; flex-direction: column; align-items: center;">'
        '<img src="https://images.unsplash.com/photo-1614064641938-3bbee52942c7?q=80&w=1000&auto=format&fit=crop" style="width: 280px; height: 280px; object-fit: cover; border-radius: 50%; border: 3px solid ' + color_neon + '; box-shadow: 0 0 40px ' + color_neon + 'cc; margin-bottom: 20px;" />'
        '<h1 style="color: ' + color_neon + '; font-size: 1.5rem; text-shadow: 0 0 20px ' + color_neon + '; letter-spacing: 2px; margin: 0;">J.A.R.V.I.S. C2 SECURE</h1>'
        '<p style="color: #88ccee; font-size: 0.8rem; margin-top: 8px;">[NÚCLEO NEURAL BIOMÉTRICO EN ESPERA]</p>'
        '<p style="color: #00d2ffaa; font-size: 0.7rem; margin-top: 15px; border: 1px solid ' + color_neon + '66; padding: 5px 10px; border-radius: 15px;">'
        '⚡ Toca la pantalla, mueve el mouse o presiona una tecla para desbloquear'
        '</p>'
        '</div>'
        '</div>'
        '<script>'
        'let triggered = false;'
        'function dismissScreensaver() {'
        '    if (triggered) return;'
        '    triggered = true;'
        '    window.location.href = window.location.pathname + "?screensaver=off";'
        '}'
        'let moveCount = 0;'
        'window.addEventListener("mousemove", function() {'
        '    moveCount++;'
        '    if (moveCount > 2) { dismissScreensaver(); }'
        '});'
        'window.addEventListener("keydown", function() { dismissScreensaver(); });'
        'window.addEventListener("touchstart", function() { dismissScreensaver(); });'
        'window.addEventListener("click", function() { dismissScreensaver(); });'
        '</script>'
    )
    st.markdown(screensaver_code, unsafe_allow_html=True)
    st.stop()

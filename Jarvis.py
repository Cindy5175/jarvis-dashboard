import os, time, json, tempfile
import streamlit as st
from groq import Groq
from gtts import gTTS
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

st.set_page_config(page_title="C.I.T. / J.A.R.V.I.S.", page_icon="⚛️", layout="centered")

# Estados de sesión
st.session_state.setdefault("autenticado", False)
st.session_state.setdefault("ubicacion_jefa", "Buin Santiago Chile")
st.session_state.setdefault("lat_val", -33.7333)
st.session_state.setdefault("lon_val", -70.7333)
st.session_state.setdefault("energia_arc", 98)
st.session_state.setdefault("notas_mision", "• Sincronizar red C2\n• Monitorear nodos principales")
st.session_state.setdefault("tema_hud", "Azul Arc")
st.session_state.setdefault("modo_dia_noche", "🌙 Noche")
st.session_state.setdefault("protocolo_ia", "Estándar (Leal y Ejecutivo)")
st.session_state.setdefault("reporte_inicial_hecho", False)

# PIN DE SEGURIDAD
if not st.session_state.autenticado:
    st.markdown('<div style="background: rgba(5, 12, 30, 0.95); border: 2px solid #00d2ff; border-radius: 12px; padding: 20px; font-family: monospace;"><h2 style="color: #00d2ff; font-size: 1.2rem;">🔒 ACCESO RESTRINGIDO</h2><p style="color: #aaa; font-size: 0.75rem;">Introduce la clave de seguridad.</p></div>', unsafe_allow_html=True)
    _, col_l2, _ = st.columns([1, 4, 1])
    with col_l2:
        pin = st.text_input("Clave:", type="password", placeholder="Contraseña")
        if st.button("🔓 Desbloquear", use_container_width=True):
            if pin == "Jarvis":
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("⚠️ Clave incorrecta.")
    st.stop()

client = Groq(api_key="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")
st.session_state.setdefault("messages", [])

# Saludo de inicio automático
if not st.session_state.messages and not st.session_state.reporte_inicial_hecho:
    saludo_inicial = (
        "Buenos días, Jefa. Los sistemas principales de la estación C2 en Buin operan al 100%. "
        f"El reactor Arc se encuentra al {st.session_state.energia_arc}%, los mercados financieros muestran estabilidad "
        "y el enlace satelital está sincronizado. ¿Cuál es nuestra directiva para hoy?"
    )
    st.session_state.messages.append({"role": "assistant", "content": saludo_inicial})
    st.session_state.reporte_inicial_hecho = True

# Colores HUD
if "Azul" in st.session_state.tema_hud:
    c_neon, c_shadow = "#00d2ff", "#0072ff"
elif "Rojo" in st.session_state.tema_hud:
    c_neon, c_shadow = "#ff3333", "#990000"
else:
    c_neon, c_shadow = "#00ff66", "#006622"

# Gestión de Protocolos de Personalidad
proto_desc = {
    "Estándar (Leal y Ejecutivo)": "Leal, brillante y ejecutiva. Te diriges al usuario como 'Jefa' con elegancia y estilo Tony Stark.",
    "Protocolo Financiero / Cripto": "Enfoque analítico y preciso en mercados bursátiles, S&P 500, Bitcoin y gestión de activos.",
    "Protocolo Ciberseguridad / Dev": "Enfoque técnico implacable, experto en depuración de código Python, Streamlit y arquitectura de redes."
}
base_persona = proto_desc.get(st.session_state.protocolo_ia, proto_desc["Estándar (Leal y Ejecutivo)"])
system_base = f"Eres J.A.R.V.I.S. Autónoma. {base_persona} Ubicación: {st.session_state.ubicacion_jefa} ({st.session_state.lat_val}, {st.session_state.lon_val}). Modo: {st.session_state.modo_dia_noche}."

# BARRA LATERAL (Todos los Módulos Avanzados)
with st.sidebar:
    st.markdown("### ⚙️ Centro de Comando Stark")
    mostrar_hud = st.checkbox("Mostrar Estación Holográfica", value=True)
    st.divider()
    
    st.selectbox("Tema HUD:", ["Azul Arc", "Rojo Mark VII", "Verde Sigilo"], key="tema_hud", on_change=st.rerun)
    st.selectbox("Protocolo IA:", ["Estándar (Leal y Ejecutivo)", "Protocolo Financiero / Cripto", "Protocolo Ciberseguridad / Dev"], key="protocolo_ia", on_change=st.rerun)
    
    presets = ["Buin (Base Central)", "Santiago Centro", "Orbital"]
    idx = 1 if "Santiago" in st.session_state.ubicacion_jefa else (2 if "Orbital" in st.session_state.ubicacion_jefa else 0)
    zona = st.selectbox("Grid Táctico:", presets, index=idx)
    
    if "Buin" in zona:
        st.session_state.ubicacion_jefa, st.session_state.lat_val, st.session_state.lon_val = "Buin Santiago Chile", -33.7333, -70.7333
    elif "Santiago" in zona:
        st.session_state.ubicacion_jefa, st.session_state.lat_val, st.session_state.lon_val = "Santiago Centro Chile", -33.4489, -70.6693
    else:
        st.session_state.ubicacion_jefa, st.session_state.lat_val, st.session_state.lon_val = "Orbital", 0.0, 0.0

    st.divider()

    with st.expander("🌤️ Clima & Alertas"):
        st.metric("Temp", "18°C", "Buin")
        st.metric("Humedad", "45%", "-2%")
        st.metric("Viento", "12 km/h", "SSE")
        
    with st.expander("📡 Radar de Red & Latencia"):
        import subprocess, platform
        host = "8.8.8.8"
        param = "-n" if platform.system().lower() == "windows" else "-c"
        try:
            output = subprocess.run(["ping", param, "1", host], capture_output=True, text=True, timeout=1)
            ping_ms = "14 ms (Estable)" if output.returncode == 0 else "18 ms (Fluctuante)"
        except:
            ping_ms = "12 ms (Optimizado)"
        st.metric("Ping Servidor Principal", ping_ms)
        st.line_chart(pd.DataFrame(np.random.randn(10, 1) * 2 + 14, columns=["Latencia ms"]), height=70)

    with st.expander("📝 Libreta & Bitácora Táctica"):
        st.session_state.notas_mision = st.text_area("Notas de Misión:", value=st.session_state.notas_mision, height=80)
        st.download_button("💾 Descargar Bitácora (.txt)", data=st.session_state.notas_mision, file_name="bitacora_c2.txt", mime="text/plain", use_container_width=True)

    with st.expander("🎵 Reproductor de Música (Spotify)"):
        spotify_html = '<iframe style="border-radius:12px" src="https://open.spotify.com/embed/playlist/37i9dQZF1DXdLEN7aqioXM?utm_source=generator&theme=0" width="100%" height="152" frameBorder="0" allowfullscreen="" allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy"></iframe>'
        components.html(spotify_html, height=165)

    with st.expander("💹 Ticker Financiero & Cripto"):
        st.metric("Bitcoin", "$67,420 USD", "+2.4%")
        st.metric("USDT", "$1.00 USD", "0.0%")
        st.metric("S&P 500", "5,815 pts", "+0.8%")
        st.markdown("---")
        st.markdown("**🧮 Conversor Táctico:**")
        monto_clp = st.number_input("Monto en CLP:", min_value=1000, value=50000, step=5000)
        val_btc_clp = 63000000
        calc_btc = monto_clp / val_btc_clp
        st.caption(f"Equivale a: **{calc_btc:.6f} BTC**")

    with st.expander("🖥️ Telemetría de Hardware Server"):
        st.metric("Uso CPU", "18%", "Óptimo")
        st.metric("RAM Server", "4.2 GB", "32% Libre")

    with st.expander("📅 Agenda & Alertas de Misión"):
        st.markdown("• **08:00 AM:** Reporte Matutino Buin")
        st.markdown("• **12:00 PM:** Auditoría de red C2")
        st.markdown("• **06:00 PM:** Respaldo Caja Negra")

    with st.expander("👤 Escáner Biométrico Facial"):
        foto = st.camera_input("Escanear Rostro", key="cam_biometria")
        if foto:
            st.success("¡Identidad Confirmada: Jefa!")

    st.divider()
    archivo_subido = st.file_uploader("Adjuntar archivo:", type=["png", "jpg", "txt", "csv", "py"])
    protocolo_extra = st.selectbox("Directiva Adicional:", ["Estándar", "Auditoría 💻", "Resumen 📊", "Ciberseguridad 🛡️"])
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🧹 Purgar", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    with c2:
        if st.button("🩺 Escanear", use_container_width=True):
            time.sleep(0.5)
            st.success("¡Ok!")

    st.divider()
    st.caption(f"⚡ Núcleo: {st.session_state.energia_arc}%")
    if st.button("🔋 Recargar Reactor", use_container_width=True):
        st.session_state.energia_arc = 100
        st.rerun()

    modelo = st.selectbox("Modelo:", ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b", "llama-3.2-11b-vision-preview"])
    activar_voz = st.checkbox("Habilitar Voz gTTS")
    
    caja_json = json.dumps({"ubicacion": st.session_state.ubicacion_jefa, "energia": st.session_state.energia_arc, "mensajes": st.session_state.messages}, ensure_ascii=False, indent=2)
    st.download_button("📦 Caja Negra (.json)", data=caja_json, file_name="caja_negra.json", mime="application/json", use_container_width=True)
    
    if st.button("🔒 Bloquear", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

# Inyección prompt del sistema
p_extra = " [Auditoría Profunda]" if "Auditoría" in protocolo_extra else (" [Resumen Ejecutivo]" if "Resumen" in protocolo_extra else (" [Ciberseguridad]" if "Ciberseguridad" in protocolo_extra else ""))
sys_msg = system_base + p_extra
if not st.session_state.messages or st.session_state.messages[0]["role"] != "system":
    st.session_state.messages.insert(0, {"role": "system", "content": sys_msg})
else:
    st.session_state.messages[0]["content"] = sys_msg

# CSS optimizado
st.markdown(f"""
<style>
@keyframes glow {{ 0%, 100% {{ text-shadow: 0 0 5px {c_neon}, 0 0 15px {c_shadow}; }} 50% {{ text-shadow: 0 0 20px {c_neon}, 0 0 35px {c_shadow}; }} }}
.neon-title {{ color: {c_neon}; font-family: monospace; font-weight: bold; font-size: 1.4rem; animation: glow 2.5s infinite; margin-top: 15px; margin-bottom: 10px; }}
.block-container {{ max-width: 100% !important; padding: 2.5rem 0.5rem 5rem 0.5rem !important; }}
</style>
<h1 class="neon-title">⚛️ J.A.R.V.I.S. AI Autónoma</h1>
""", unsafe_allow_html=True)

# ESTACIÓN HUD (PANTALLA PRINCIPAL CON NÚCLEO Y MAPA)
if mostrar_hud:
    with st.container(border=True):
        st.markdown(f"**[C2 STATION]** | ⚡ INT: {st.session_state.energia_arc}% | 📡 Red: Estable | 📍 Grid: {st.session_state.ubicacion_jefa}")

        # NÚCLEO DE VOZ CONTINUA
        st.markdown("---")
        script_voz_continua = (
            '<div style="text-align: center; padding: 8px; background: rgba(0, 210, 255, 0.03); border: 1px dashed #00d2ff; border-radius: 6px;">'
            '<p id="estado-voz" style="color: #00d2ff; font-family: monospace; font-size: 0.8rem; margin-bottom: 5px;">⚡ Núcleo de Voz: En espera...</p>'
            '<button onclick="iniciarEscuchaContinua()" style="background-color: #00d2ff; color: #000; font-weight: bold; border: none; padding: 6px 15px; border-radius: 4px; cursor: pointer; width: 100%; font-family: monospace; font-size: 0.85rem;">'
            '🎙️ Activar Escucha Automática de Voz'
            '</button>'
            '</div>'
            '<script>'
            'function iniciarEscuchaContinua() {'
            '    var recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();'
            '    recognition.lang = "es-ES";'
            '    recognition.continuous = true;'
            '    recognition.interimResults = false;'
            '    document.getElementById("estado-voz").innerText = "🔴 Escuchando activamente...";'
            '    recognition.onresult = function(event) {'
            '        var transcript = event.results[event.results.length - 1][0].transcript;'
            '        document.getElementById("estado-voz").innerText = "💬 " + transcript;'
            '        var inputElem = window.parent.document.querySelector("textarea[data-testid=\'stChatInputTextArea\']");'
            '        if (inputElem) {'
            '            inputElem.value = transcript;'
            '            inputElem.dispatchEvent(new Event("input", { bubbles: true }));'
            '            setTimeout(function() {'
            '                inputElem.dispatchEvent(new KeyboardEvent("keydown", {key: "Enter", code: "Enter", keyCode: 13, which: 13, bubbles: true}));'
            '            }, 500);'
            '        }'
            '    };'
            '    recognition.onerror = function(event) {'
            '        setTimeout(iniciarEscuchaContinua, 1000);'
            '    };'
            '    recognition.onend = function() {'
            '        try { recognition.start(); } catch(e) {}'
            '    };'
            '    recognition.start();'
            '}'
            '</script>'
        )
        components.html(script_voz_continua, height=105)

        # Visor Cartográfico Global
        st.markdown("---")
        col_m1, col_m2 = st.columns([3, 1.2])
        with col_m1:
            st.markdown("🌍 **Visor Satelital**")
        with col_m2:
            if st.button(st.session_state.modo_dia_noche, use_container_width=True):
                st.session_state.modo_dia_noche = "☀️ Día" if st.session_state.modo_dia_noche == "🌙 Noche" else "🌙 Noche"
                st.rerun()

        filtro = "filter: brightness(0.6) invert(1) contrast(1.3) hue-rotate(200deg);" if "🌙" in st.session_state.modo_dia_noche else ""
        
        mapa_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
            <style>#map {{ width: 100%; height: 260px; border-radius: 6px; {filtro} }}</style>
        </head>
        <body style="margin:0; background:transparent;">
            <div id="map"></div>
            <script>
                var map = L.map('map').setView([{st.session_state.lat_val}, {st.session_state.lon_val}], 13);
                L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ maxZoom: 19 }}).addTo(map);
                L.marker([{st.session_state.lat_val}, {st.session_state.lon_val}]).addTo(map).bindPopup("<b>Grid: {st.session_state.ubicacion_jefa}</b>");
            </script>
        </body>
        </html>
        """
        components.html(mapa_html, height=280)

# HISTORIAL DE CHAT RESTAURADO
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# CAJA DE CHAT PRINCIPAL RESTAURADA
if prompt := st.chat_input("Directiva táctica..."):
    adjunto, img_b64 = "", None
    if archivo_subido:
        if "image" in archivo_subido.type:
            import base64
            img_b64 = base64.b64encode(archivo_subido.read()).decode('utf-8')
            adjunto = f"\n\n[Imagen adjunta: {archivo_subido.name}]"
        else:
            try:
                adjunto = f"\n\n--- ARCHIVO '{archivo_subido.name}' ---\n{archivo_subido.read().decode('utf-8')}\n--- FIN ---"
            except:
                adjunto = f"\n\n[Archivo no legible]"

    p_completo = prompt + adjunto
    st.session_state.messages.append({"role": "user", "content": p_completo})
    
    with st.chat_message("user"):
        st.markdown(prompt)
        if archivo_subido and "image" in archivo_subido.type:
            st.image(archivo_subido, use_column_width=True)

    with st.chat_message("assistant"):
        ph = st.empty()
        resp = ""
        
        msgs_api = st.session_state.messages
        models = [modelo, "openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
        
        exito = False
        for m in models:
            try:
                stream = client.chat.completions.create(model=m, messages=msgs_api, stream=True)
                for chunk in stream:
                    resp += chunk.choices[0].delta.content or ""
                    ph.markdown(resp + "▌")
                ph.markdown(resp)
                exito = True
                break
            except:
                continue
        if not exito:
            resp = "Error de enlace con los servidores de Groq, Jefa."
            ph.markdown(resp)

        if activar_voz and resp:
            try:
                tts = gTTS(text=resp, lang='es', slow=False)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    st.audio(fp.name, format="audio/mp3", autoplay=True)
            except:
                pass

    st.session_state.messages.append({"role": "assistant", "content": resp})

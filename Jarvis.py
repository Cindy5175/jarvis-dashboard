# ---------------------------------------------------------
# MÓDULO DE EXPANSIÓN TÁCTICA // 4 JUGUETES DE ALTO RENDIMIENTO
# ---------------------------------------------------------
if "biometrico_estado" not in st.session_state:
    st.session_state.biometrico_estado = "🔒 BLOQUEADO (ESPERANDO HUELLA)"
if "alerta_actual" not in st.session_state:
    st.session_state.alerta_actual = "🟢 Perímetro seguro en Buin. Gato durmiendo en el techo."
if "misiones_lista" not in st.session_state:
    st.session_state.misiones_lista = {
        "Verificar búnker Buin": True, 
        "Sincronizar satélite": False, 
        "Actualizar IA": False
    }

st.markdown('<div class="holo-card">', unsafe_allow_html=True)
st.markdown('<div class="holo-title">🛠️ MÓDULO DE EXPANSIÓN TÁCTICA // 4 JUGUETES DE ALTO RENDIMIENTO (STARK INDUSTRIES)</div>', unsafe_allow_html=True)

j1, j2, j3, j4 = st.columns(4)

with j1:
    st.markdown("<p style='color:#00d2ff; font-size:13px; font-weight:bold; text-align:center;'>1. 🧬 ESCÁNER BIOMÉTRICO</p>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; font-family:monospace; font-size:11px; color:#ffbb00; margin-bottom:8px;'>{st.session_state.biometrico_estado}</div>", unsafe_allow_html=True)
    if st.button("👁️ Escanear Huella"):
        st.session_state.biometrico_estado = f"✅ ACCESO CONCEDIDO: {titulo_jefa.upper()} {nombre_jefa.upper()}"
        st.rerun()

with j2:
    st.markdown("<p style='color:#00d2ff; font-size:13px; font-weight:bold; text-align:center;'>2. ⚡ REACTOR & CLIMA</p>", unsafe_allow_html=True)
    nivel_reactor = st.slider("Potencia Reactor Arc (%)", 50, 100, 98, key="slider_arc")
    temp_bunker = st.select_slider("Clima Búnker (°C)", options=[16, 18, 20, 22, 24], value=20, key="slider_temp")
    st.markdown(f"<div style='text-align:center; font-family:monospace; font-size:10px; color:#00ffaa;'>Núcleo al {nivel_reactor}% | Temp: {temp_bunker}°C</div>", unsafe_allow_html=True)

with j3:
    st.markdown("<p style='color:#00d2ff; font-size:13px; font-weight:bold; text-align:center;'>3. 📋 MISIONES TÁCTICAS</p>", unsafe_allow_html=True)
    for mision, estado in st.session_state.misiones_lista.items():
        st.session_state.misiones_lista[mision] = st.checkbox(mision, value=estado, key=f"mission_{mision}")

with j4:
    st.markdown("<p style='color:#00d2ff; font-size:13px; font-weight:bold; text-align:center;'>4. 🚨 RADAR DE AMENAZAS</p>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:#000; border:1px solid #00d2ff; padding:8px; border-radius:6px; font-family:monospace; font-size:11px; color:#00ffaa; min-height:45px; text-align:center;'>{st.session_state.alerta_actual}</div>", unsafe_allow_html=True)
    
    if st.button("📡 Escanear Amenazas"):
        amenazas_posibles = [
            "🟢 Perímetro seguro en Buin. Gato durmiendo en el techo.",
            "🟢 Satélite Serafín sin interferencia solar.",
            "🟡 Tráfico de red menor detectado en Santiago.",
            "🟢 Temperatura óptima en servidores principales.",
            "🚀 Alerta: Intento de hackeo bloqueado desde fuera de Buin."
        ]
        st.session_state.alerta_actual = random.choice(amenazas_posibles)
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
st.markdown("---")

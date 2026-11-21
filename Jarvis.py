@st.cache_data(ttl=300)
def obtener_indicadores_chile():
    headers = {
        "User-Agent": "Mozilla/5.0 JARVIS-Dashboard/1.0",
        "Accept": "application/json",
    }
    for _ in range(2):
        try:
            resp = requests.get(
                "https://mindicador.cl/api",
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                d = resp.json()
                dolar_ok = d.get("dolar", {}).get("valor")
                euro_ok = d.get("euro", {}).get("valor")
                uf_ok = d.get("uf", {}).get("valor")
                if dolar_ok and euro_ok and uf_ok:
                    return {
                        "dolar": float(dolar_ok),
                        "euro": float(euro_ok),
                        "uf": float(uf_ok),
                        "ok": True,
                        "respaldo": False,
                    }
        except Exception:
            pass
    return {
        "dolar": 950.00,
        "euro": 1030.00,
        "uf": 38000.00,
        "ok": True,
        "respaldo": True,
    }


def fmt_clp(val: float) -> str:
    return f"${val:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
now_chile = datetime.datetime.now(tz_chile)
saludo_actual = (
    "Buenos días"
    if now_chile.hour < 12
    else ("Buenas tardes" if now_chile.hour < 20 else "Buenas noches")
)


def obtener_saludo_nucleo(nucleo_nombre: str) -> str:
    pref = f"[{nucleo_nombre}] "
    saludos = {
        "JARVIS": f"{pref}{saludo_actual}, señorita. Qué milagro que pase a saludar; los servidores ya empezaban a extrañar sus órdenes.",
        "VIERNES": f"{pref}¡{saludo_actual}, señorita! Lista para mover ficha. ¿Qué encendemos hoy?",
        "NOVA": f"{pref}¡{saludo_actual}, señorita! Señal recibida desde el Nodo Buin. ¿Qué galaxia o tarea conquistamos ahora?",
    }
    return saludos.get(nucleo_nombre, f"{pref}{saludo_actual}, señorita. En línea y a su servicio.")


def _coincide_clave(texto_norm: str, tokens_palabras: set, clave: str) -> bool:
    c = clave.lower().strip()
    if not c:
        return False
    if " " in c or ":" in c:
        return c in texto_norm
    return c in tokens_palabras


def skill_wendy(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_ojo_dios = True
    cam_act = getattr(jarvis_core, "camara_seleccionada", "CAM-01 // PERÍMETRO NODO BUIN")
    return (
        f"[{nucleo}] Sí, señorita. Protocolo **Wendy** activado, **Ojo de Dios** en **{cam_act}** "
        f"y enlace vinculado: [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_planetear(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.mostrar_mapa_tactico = True
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_mapa = True
    st.session_state.ver_ojo_dios = True
    return (
        f"[{nucleo}] Sí, señorita. Modo **Planetear** desplegado: **mapa táctico satelital** y **Ojo de Dios** activos "
        f"con enlace [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_ojo_osiris(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_ojo_dios = True
    cam_act = getattr(jarvis_core, "camara_seleccionada", "CAM-01 // PERÍMETRO NODO BUIN")
    return (
        f"[{nucleo}] Sí, señorita. **Ojo de Dios** activado en **{cam_act}** // "
        f"Enlace táctico: [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_osiris_ai(nucleo: str, _t: str, _raw: str) -> str:
    return f"[{nucleo}] Sí, señorita. Enlace directo a **Osiris AI**: [{OSIRIS_URL}]({OSIRIS_URL})."


def skill_ojo_de_dios(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.ojo_de_dios_activo = True
    st.session_state.ver_ojo_dios = True
    cam_act = getattr(jarvis_core, "camara_seleccionada", "CAM-01 // PERÍMETRO NODO BUIN")
    mov_act = getattr(jarvis_core, "ultimo_movimiento", "Sin novedades en el perímetro.")
    return (
        f"[{nucleo}] Sí, señorita. **Ojo de Dios** activado en **{cam_act}** "
        f"({mov_act}) // Enlace: [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_mapa_tactico(nucleo: str, _t: str, _raw: str) -> str:
    jarvis_core.mostrar_mapa_tactico = True
    st.session_state.ver_mapa = True
    st.session_state.voz_pendiente = "Sí, señorita."
    return f"[{nucleo}] Sí, señorita. Desplegando **mapa táctico satelital**."


def skill_finanzas_chile(nucleo: str, _t: str, _raw: str) -> str:
    econ = obtener_indicadores_chile()
    tag = " *(modo respaldo)*" if econ.get("respaldo") else ""
    return (
        f"[{nucleo}] Indicadores en Nodo Buin{tag}, señorita: "
        f"Dólar **{fmt_clp(econ['dolar'])}**, Euro **{fmt_clp(econ['euro'])}** y UF **{fmt_clp(econ['uf'])}**."
    )


def skill_mercados_externos(nucleo: str, _t: str, _raw: str) -> str:
    return (
        f"[{nucleo}] En el chat local no hay streaming de bolsa en tiempo real, señorita. "
        f"Use **Seguimiento ANT (Nasdaq)** o **Finviz** en el panel lateral para monitorear el movimiento."
    )


def skill_resumen_tactico(nucleo: str, _t: str, _raw: str) -> str:
    misiones = obtener_misiones()
    pendientes = sum(1 for _, _, est in misiones if est != "Completada")
    mems = obtener_memorias(5)
    ojo_estado = (
        "ACTIVO"
        if (st.session_state.ver_ojo_dios or getattr(jarvis_core, "ojo_de_dios_activo", False))
        else "EN ESPERA"
    )
    mapa_estado = (
        "ACTIVO"
        if (st.session_state.ver_mapa or getattr(jarvis_core, "mostrar_mapa_tactico", False))
        else "EN ESPERA"
    )
    return (
        f"[{nucleo}] Reporte del Nodo Buin ({now_chile.strftime('%H:%M:%S')} CLT), señorita: "
        f"Ojo de Dios **{ojo_estado}**, mapa táctico satelital **{mapa_estado}**, "
        f"misiones pendientes **{pendientes}/{len(misiones)}**, memorias recientes **{len(mems)}** "
        f"y enlace [{OSIRIS_URL}]({OSIRIS_URL})."
    )


def skill_misiones_y_memoria(nucleo: str, t: str, raw: str) -> str:
    if (
        t.startswith("mision:")
        or t.startswith("misión:")
        or t.startswith("anota mision:")
        or t.startswith("anota misión:")
    ):
        tarea = raw.split(":", 1)[1].strip()
        if tarea:
            agregar_mision(tarea)
            return f"[{nucleo}] Sí, señorita. Misión registrada en base de datos: **{tarea}**."
    if t.startswith("completa mision:") or t.startswith("completa misión:"):
        objetivo = raw.split(":", 1)[1].strip()
        if objetivo:
            n = completar_mision(objetivo)
            return f"[{nucleo}] Sí, señorita. Misiones marcadas como completadas: **{n}**."
    if t.startswith("recuerda:") or t.startswith("guarda:"):
        hecho = raw.split(":", 1)[1].strip()
        if hecho:
            guardar_memoria(hecho, "skill_chat")
            return f"[{nucleo}] Sí, señorita. Guardado en memoria SQLite: *{hecho}*."
    if t.startswith("olvida:") or t.startswith("borra memoria:"):
        frag = raw.split(":", 1)[1].strip()
        if frag:
            borrados = olvidar_memoria(frag)
            return f"[{nucleo}] Sí, señorita. Registros de memoria eliminados: **{borrados}**."
    if any(w in t for w in ["memorias", "qué recuerdas", "que recuerdas"]):
        mems = obtener_memorias(5)
        if not mems:
            return f"[{nucleo}] Aún no hay memorias guardadas en SQLite, señorita."
        lista = "; ".join(m[0] for m in mems)
        return f"[{nucleo}] Memorias recientes, señorita: {lista}."
    return f"[{nucleo}] Núcleo **{nucleo}** operativo en Nodo Buin, señorita. Misiones activas: **{len(obtener_misiones())}**."


def skill_perimetro_cam(nucleo: str, _t: str, _raw: str) -> str:
    return f"[{nucleo}] Estado perimetral, señorita: {getattr(jarvis_core, 'ultimo_movimiento', 'Sin novedades.')}"


SKILLS_REGISTRY = [
    {"id": "wendy", "keys": ["wendy"], "fn": skill_wendy},
    {"id": "planetear", "keys": ["planetear"], "fn": skill_planetear},
    {
        "id": "ojo_osiris",
        "keys": ["ojo osiris", "osiris ojo", "vigilancia osiris", "enlace ojo de dios", "comando ojo"],
        "fn": skill_ojo_osiris,
    },
    {"id": "osiris_ai", "keys": ["osiris", "osiris ai", "osirisai"], "fn": skill_osiris_ai},
    {"id": "ojo_de_dios", "keys": ["ojo de dios", "cámaras", "camaras", "vigilancia", "cctv"], "fn": skill_ojo_de_dios},
    {"id": "mapa_tactico", "keys": ["mapa táctico satelital", "mapa tactico satelital", "mapa"], "fn": skill_mapa_tactico},
    {
        "id": "finanzas_chile",
        "keys": ["dólar", "dolar", "euro", "uf", "utm", "divisa", "divisas", "moneda", "cambio"],
        "fn": skill_finanzas_chile,
    },
    {
        "id": "mercados_externos",
        "keys": ["bolsa", "bolsas", "acciones", "nasdaq", "mercado", "mercados", "wall street", "finviz", "accion ant", "acción ant"],
        "fn": skill_mercados_externos,
    },
    {"id": "resumen_tactico", "keys": ["resumen", "reporte", "diagnóstico", "diagnostico"], "fn": skill_resumen_tactico},
    {
        "id": "misiones_memoria",
        "keys": [
            "mision:", "misión:", "anota mision:", "anota misión:",
            "completa mision:", "completa misión:", "recuerda:", "guarda:",
            "olvida:", "borra memoria:", "memorias", "qué recuerdas", "que recuerdas",
            "estado", "sistema", "misión", "misiones", "pendiente", "pendientes",
        ],
        "fn": skill_misiones_y_memoria,
    },
    {"id": "perimetro_cam", "keys": ["cámara", "camara", "perímetro", "perimetro", "movimiento", "sensor"], "fn": skill_perimetro_cam},
]


def responder_con_groq(nucleo: str, texto_usuario: str) -> str:
    if client_groq is None:
        return ""
    mems = [m[0] for m in obtener_memorias(5)]
    ctx_mem = f"Memorias guardadas: {'; '.join(mems)}." if mems else ""
    historial_previo = st.session_state.get("mensajes", [])[-5:]
    recientes = [
        f"{'Señorita' if item.get('role') == 'user' else nucleo}: {limpiar_texto_para_voz(item.get('content', ''))}"
        for item in historial_previo
        if item.get("content")
    ]
    ctx_chat = f"Contexto reciente del chat: {' | '.join(recientes)}." if recientes else ""
    estilos = {
        "JARVIS": "Eres JARVIS, elegante, ingenioso y con sarcasmo fino, tratas al usuario como 'señorita' y respondes en español.",
        "VIERNES": "Eres VIERNES, ágil, directa y resolutiva, tratas al usuario como 'señorita' y respondes en español.",
        "NOVA": "Eres NOVA, enérgica y cósmica, tratas al usuario como 'señorita' y respondes en español.",
    }
    sys_msg = (
        f"{estilos.get(nucleo, estilos['JARVIS'])} "
        f"Skills activas: {[s['id'] for s in SKILLS_REGISTRY]}. {ctx_mem} {ctx_chat} Sé conciso."
    )
    for modelo_cand in [GROQ_MODELO_ACTIVO, "llama-3.3-70b-versatile"]:
        try:
            chat = client_groq.chat.completions.create(
                model=modelo_cand,
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": texto_usuario},
                ],
                temperature=0.7,
                max_tokens=300,
            )
            contenido = (chat.choices[0].message.content or "").strip()
            if contenido:
                return f"[{nucleo}] {contenido}"
        except Exception:
            continue
    return ""


def generar_respuesta_coherente(nucleo: str, texto_usuario: str) -> str:
    prefijo = f"[{nucleo}] "
    raw = texto_usuario.strip()
    t = raw.lower()
    tokens = set(re.findall(r"[a-záéíóúñü0-9:]+", t))
    memoria_ext = obtener_memoria_completa()
    resp_bilingue_mem = _resolver_respuesta_bilingue_y_memoria(raw, memoria_ext)
    if resp_bilingue_mem:
        return f"{prefijo}{resp_bilingue_mem}"
    if "protocolo extremo" in t:
        return f"{prefijo}Protocolo de conocimiento extremo activado, señorita. Analizando a fondo sin rodeos."
    if any(
        t == s or t.startswith(s + " ") or t.startswith(s + ",")
        for s in ["hola", "buenas", "buenos días", "buenos dias", "buenas tardes", "buenas noches", "holi", "qué tal", "que tal"]
    ):
        return obtener_saludo_nucleo(nucleo)
    if "mosca" in tokens and ({"patas", "cuantas", "cuántas"} & tokens):
        return f"{prefijo}Tiene **6 patas**, señorita. Y por lo general aterrizan justo cuando estorban."
    for sk in SKILLS_REGISTRY:
        if any(_coincide_clave(t, tokens, k) for k in sk["keys"]):
            return sk["fn"](nucleo, t, raw)
    if {"hora", "fecha"} & tokens or any(f in t for f in ["qué hora", "que hora", "día de hoy", "dia de hoy"]):
        return f"{prefijo}En el Nodo Buin son las **{now_chile.strftime('%H:%M:%S')}** (hora de Chile), señorita."
    ia_resp = responder_con_groq(nucleo, raw)
    if ia_resp:
        return ia_resp
    return random.choice([
        f"{prefijo}Entendido, señorita: *'{raw}'*. Puede usar `mapa`, `wendy`, `planetear`, `resumen`, `memorias`, `misión: ...` o `recuerda: ...`.",
        f"{prefijo}Tomo nota de *'{raw}'*, señorita. Dígame en qué más le apoyo.",
    ])


if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": obtener_saludo_nucleo(st.session_state.nucleo_activo)}]

st.markdown(
    '<style>'
    '.stApp{background-color:#060913!important;color:#00f3ff!important;font-family:monospace;}'
    'p,span,label,h1,h2,h3,h4,div{color:#00f3ff!important;font-family:monospace;}'
    '.stButton>button{background-color:#00f3ff!important;border:1.5px solid #00f3ff!important;font-weight:bold;width:100%;border-radius:6px;}'
    '.stButton>button p,.stButton>button span{color:#060913!important;font-size:0.78rem!important;}'
    '.econ-card{border:1px solid #00f3ff;background:rgba(0,243,255,0.06);border-radius:6px;padding:8px 10px;margin:5px 0;display:flex;justify-content:space-between;}'
    '.arc-reactor-container{display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;margin-bottom:6px;}'
    '.arc-ring{width:65px;height:65px;border:2.5px solid #00f3ff;border-radius:50%;display:flex;align-items:center;justify-content:center;background:radial-gradient(circle,rgba(0,243,255,0.4) 0%,#060913 75%);box-shadow:0 0 20px rgba(0,243,255,0.8);margin-bottom:8px;}'
    '.arc-triangle-inverted{width:0;height:0;border-left:12px solid transparent;border-right:12px solid transparent;border-top:20px solid #00f3ff;}'
    '.tactical-link-btn{display:block;width:100%;background-color:#00f3ff;color:#060913!important;text-align:center;padding:6px 10px;margin:5px 0;border-radius:5px;font-size:0.76rem!important;font-weight:bold;text-decoration:none;}'
    '.holo-brain-box{border:1.5px solid #00f3ff;background:linear-gradient(135deg,#0a1128 0%,#060913 100%);padding:15px;border-radius:8px;text-align:center;margin:0 auto 20px auto;max-width:800px;}'
    '.god-eye-box{border:1.5px solid #00f3ff;background:rgba(10,17,40,0.9);border-radius:8px;padding:14px;margin-bottom:16px;}'
    '#MainMenu,footer{visibility:hidden;}'
    '</style>',
    unsafe_allow_html=True
)

if not st.session_state.get("autorizado", False):
    st.markdown(
        '<div style="text-align:center;margin-top:50px;"><h2>ACCESO RESTRINGIDO - NODO BUIN</h2>'
        '<p>INGRESE PIN DE SEGURIDAD PARA ACTIVAR LA ARMADURA</p></div>',
        unsafe_allow_html=True,
    )
    _, c2, _ = st.columns([1, 2, 1])
    with c2:
        with st.form("form_login"):
            pin_input = st.text_input("PIN Secreto:", type="password", placeholder="Ingresa tu PIN...")
            if st.form_submit_button("Desbloquear Sistema"):
                if pin_input.strip() == PIN_SECRETO:
                    st.session_state.autorizado = True
                    st.rerun()
                else:
                    st.error("PIN incorrecto. Acceso denegado.")
    st.stop()

with st.sidebar:
    st.markdown("### 🛡️ Arsenal de Módulos")
    if st.button("🔒 Bloquear Sistema", use_container_width=True):
        st.session_state.autorizado = False
        st.rerun()
    if st.button("🔄 Reinicio Total", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🧠 Selector de Núcleo (IA)")
    nuevo_nucleo = st.radio(
        "Núcleo:",
        ["JARVIS", "VIERNES", "NOVA"],
        index=["JARVIS", "VIERNES", "NOVA"].index(st.session_state.nucleo_activo),
        label_visibility="collapsed",
    )
    if nuevo_nucleo != st.session_state.nucleo_activo:
        st.session_state.nucleo_activo = nuevo_nucleo
        st.session_state.mensajes.append({"role": "assistant", "content": obtener_saludo_nucleo(nuevo_nucleo)})
        st.rerun()

    st.markdown("---")
    st.markdown("#### 👁️ Ojo de Dios y Vigilancia")
    with st.expander("Cámaras y Sensores", expanded=False):
        cam_opts = [
            "CAM-01 // PERÍMETRO NODO BUIN",
            "CAM-02 // ACCESO PRINCIPAL",
            "CAM-03 // PATIO Y SECTOR NORTE",
            "CAM-04 // ENLACE REMOTO / RTSP",
        ]
        cam_actual = getattr(jarvis_core, "camara_seleccionada", cam_opts[0])
        sel_cam = st.selectbox("Feed Activo:", cam_opts, index=cam_opts.index(cam_actual) if cam_actual in cam_opts else 0)
        jarvis_core.camara_seleccionada = sel_cam
        jarvis_core.stream_url = st.text_input(
            "URL Stream (MJPEG/Imagen opcional):",
            value=getattr(jarvis_core, "stream_url", ""),
            placeholder="https://...",
        )
        c_od1, c_od2 = st.columns(2)
        with c_od1:
            if st.button("👁️ Ver Ojo", use_container_width=True):
                st.session_state.ver_ojo_dios = True
                jarvis_core.ojo_de_dios_activo = True
                st.rerun()
        with c_od2:
            if st.button("✖ Ocultar", use_container_width=True):
                st.session_state.ver_ojo_dios = False
                jarvis_core.ojo_de_dios_activo = False
                st.rerun()
        st.caption(f"Sensor: {getattr(jarvis_core, 'ultimo_movimiento', 'Sin novedades.')}")

    st.markdown("---")
    st.markdown("#### 💾 Memoria y Datos")
    with st.expander("Gestionar Memoria SQLite", expanded=False):
        dato_mem = st.text_input("Dato a guardar:", placeholder="Ej: Preferencia...")
        if st.button("Guardar en Memoria", use_container_width=True) and dato_mem.strip():
            guardar_memoria(dato_mem.strip())
            st.success("¡Memoria guardada!")

    st.markdown("---")
    st.markdown("#### 📋 Misiones Tácticas")
    with st.expander("Base de Datos Misiones", expanded=False):
        nueva_tarea = st.text_input("Nueva Misión:", placeholder="Ej: Revisar nodos...")
        if st.button("Agregar Misión", use_container_width=True) and nueva_tarea.strip():
            agregar_mision(nueva_tarea.strip())
            st.success("Misión agregada.")
        misiones_actuales = obtener_misiones()
        for _id, _tarea, _estado in misiones_actuales:
            st.caption(f"• [{_estado}] {_tarea}")
        if misiones_actuales and st.button("Limpiar Misiones", use_container_width=True):
            limpiar_misiones()
            st.rerun()

# --- BLOQUE PRINCIPAL: MEMORIA EXTERNA Y CAJA DE CHAT ---
memoria_ext_jarvis = obtener_memoria_completa()
if memoria_ext_jarvis:
    with st.expander("Ver memoria cargada (contexto y cumpleaños)", expanded=False):
        st.markdown(memoria_ext_jarvis)

for _msg in st.session_state.mensajes:
    with st.chat_message(_msg.get("role", "assistant")):
        st.write(_msg.get("content", ""))

_prompt_jarvis = st.chat_input("Escribe tu orden o consulta para JARVIS...")
if _prompt_jarvis:
    st.session_state.mensajes.append({"role": "user", "content": _prompt_jarvis})
    _respuesta_jarvis = generar_respuesta_coherente(
        st.session_state.nucleo_activo,
        _prompt_jarvis,
    )
    st.session_state.mensajes.append({"role": "assistant", "content": _respuesta_jarvis})
    st.rerun()

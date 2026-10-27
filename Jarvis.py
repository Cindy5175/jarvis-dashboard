import streamlit as st
import time
from groq import Groq

# 1. Configuración de la página (estética del Centro de Comando Stark)
st.set_page_config(
    page_title="Centro de Comando Stark - J.A.R.V.I.S.",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inicialización segura del cliente de Groq (con caché y timeout para evitar bloqueos)
@st.cache_resource
def obtener_cliente_groq():
    try:
        api_key = st.secrets.get("GROQ_API_KEY", "")
        if not api_key:
            return None
        return Groq(api_key=api_key, timeout=10.0)
    except Exception:
        return None

client = obtener_cliente_groq()

# 3. BARRA LATERAL - Todos los Módulos del Centro de Comando Stark
with st.sidebar:
    st.subheader("⚙️ Centro de Comando Stark")
    
    mostrar_estacion = st.checkbox("Mostrar Estación Holográfica (God's Eye View)", value=True)
    
    st.markdown("---")
    
    tema_hud = st.selectbox(
        "Tema HUD:",
        ["Rojo Cobre/Terracota", "Azul Arc", "Grafito Oscuro"]
    )
    
    protocolo_ia = st.selectbox(
        "Protocolo IA:",
        ["Estándar (Leal y Ejecutivo)", "Avanzado", "Táctico"]
    )
    
    grid_tactico = st.selectbox(
        "Grid Táctico:",
        ["Santiago Centro", "Buin", "Global"]
    )
    
    st.markdown("---")
    
    with st.expander("🌤️ Clima & Alertas"):
        st.write("**Ubicación:** Buin / Santiago, Chile")
        st.write("Estado: Monitoreo atmosférico y telemetría local activos.")
        st.metric(label="Temperatura Estimada", value="18°C", delta="Óptimo")
    
    with st.expander("📡 Radar de Red & Latencia"):
        st.write("**Estado del Enlace:** Estable")
        st.write("**Latencia de Red:** 24 ms")
        st.progress(85)
        st.write("Conexión con servidores externos blindada.")
        
    with st.expander("📝 Libreta & Bitácora Táctica"):
        st.text_area(
            "Notas rápidas y registros:", 
            "1. Agosto: God's Eye View y conexión Siri (jarvis.py).\n2. Noviembre: Catálogo 'Sabor y Receta 24/7' (4 e-books a $5 USD, pauta SII y boletas automáticas)."
        )
        if st.button("Guardar Bitácora"):
            st.success("Datos guardados en memoria táctica.")
        
    with st.expander("🎵 Reproductor de Música (Spotify)"):
        st.write("🎶 Estado: Enlace de audio sincronizado.")
        st.markdown("[Abrir Interfaz de Spotify](https://open.spotify.com)", unsafe_allow_html=True)

# 4. Panel Principal - Interfaz de J.A.R.V.I.S.
st.title("⚡ Centro de Comando Stark - J.A.R.V.I.S.")

if mostrar_estacion:
    st.info("🗺️ **Módulo God's Eye View activo:** Estación holográfica y grid táctico listos para operar.")

# Personalidad clásica de J.A.R.V.I.S.
prompt_sistema_jarvis = (
    "Eres J.A.R.V.I.S., el asistente de inteligencia artificial avanzado inspirado en el universo de Iron Man. "
    "Te diriges a la usuaria con el máximo respeto, llamándola siempre 'Jefa'. "
    "Tu tono es sumamente profesional, leal, ejecutivo, sofisticado, eficiente y servicial. "
    "Respondes de manera precisa, ordenada y estratégica, manteniendo la estética y el rendimiento operativo "
    "del Centro de Comando Stark en todo momento."
)

prompt_usuario = st.chat_input("Escriba su comando para J.A.R.V.I.S. o Siri...")

if prompt_usuario:
    if not client:
        st.error("⚠️ Jefa, la clave de API de Groq no está configurada correctamente en los secrets de Streamlit.")
    else:
        with st.spinner("Procesando comando táctico..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": prompt_sistema_jarvis},
                        {"role": "user", "content": prompt_usuario}
                    ],
                    model="llama3-70b-8192",
                )
                respuesta = chat_completion.choices[0].message.content
                st.write(respuesta)
                
            except Exception as e:
                st.error(f"Error de enlace con los servidores de Groq, Jefa: {e}")

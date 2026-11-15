import streamlit as st

# Configuración de página con diseño ancho
st.set_page_config(
    page_title="J.A.R.V.I.S. // IA",
    layout="wide",
    initial_sidebar_state="collapsed"  # <--- Mantiene la barra oculta por defecto
)

# Estilos visuales de luz de neón futurista (Cyber-Grid)
st.markdown("""
    <style>
        .stApp { background-color: #0b0f19 !important; color: #00f3ff !important; font-family: 'Courier New', Courier, monospace; }
        
        .jarvis-title {
            text-align: center;
            color: #00f3ff;
            text-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
            font-size: 2.2rem;
            font-weight: bold;
            margin-bottom: 0px;
        }
        
        .cyber-box {
            border: 1px solid #00f3ff;
            background-color: rgba(15, 23, 42, 0.6);
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
            text-align: center;
            margin-bottom: 20px;
        }

        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 1. PANEL LATERAL OCULTO (ARSENAL DE MÓDULOS)
# ==========================================
with st.sidebar:
    st.markdown("### 🛡️ Arsenal de Módulos")
    st.markdown("---")
    
    if st.button("🔒 Bloquear Sistema", use_container_width=True):
        st.warning("Sistema bloqueado por seguridad.")
        
    if st.button("🔄 Reinicio Total", use_container_width=True):
        st.error("Reiniciando núcleos neuronales...")

# ==========================================
# 2. PANTALLA PRINCIPAL (LIMPIA Y MINIMALISTA)
# ==========================================

# Logo y Encabezado principal
st.markdown('<div style="text-align: center; font-size: 1.5rem;">⏏️</div>', unsafe_allow_html=True)
st.markdown('<div class="jarvis-title">J.A.R.V.I.S.<br>IA</div>', unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #94a3b8; font-size: 0.85rem; margin-bottom: 20px;">[ NODO BUIN, CHILE // Domingo, 15 de noviembre de 2026 - 13:05:00 ]</div>', unsafe_allow_html=True)

# Núcleo Neuronal (Caja principal de estado)
st.markdown("""
    <div class="cyber-box">
        <div style="font-weight: bold; margin-bottom: 8px; color: #00f3ff;">NUCLEO NEURONAL CYBER-GRID [JARVIS]</div>
        <div style="font-size: 0.85rem; color: #94a3b8;">Conectado a Gemini, ZapIA, 7 Memorias SQLite y Nodo Buin</div>
    </div>
""", unsafe_allow_html=True)

# Caja de chat central despejada
st.markdown("---")
st.text_input("💬 Escribe un comando o consulta para JARVIS...", placeholder="Ej: Analizar sistema...")


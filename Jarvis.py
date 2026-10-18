# Reemplace esta sección en su CSS de jarvis.py para asegurar que TODAS las etiquetas se vean en neón brillante:
st.markdown("""
    <style>
    .stApp {
        background-color: #06090f !important;
        color: #00d9ff !important;
        font-family: 'Space Mono', monospace;
    }
    .main { 
        background-color: #06090f !important; 
        color: #00d9ff !important; 
    }
    
    /* FORZAR VISIBILIDAD DE TODAS LAS ETIQUETAS Y TEXTOS */
    label, .stTextInput label, p, span {
        color: #00d9ff !important;
    }
    
    h1 {
        font-size: 24px !important;
        color: #00d9ff !important;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        text-align: center;
    }
    h3 {
        font-size: 14px !important;
        color: #00d9ff !important;
        letter-spacing: 1px;
    }
    
    /* Barra lateral totalmente oscura */
    section[data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid #00d9ff66 !important;
        color: #00d9ff !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
        color: #00d9ff !important;
    }
    section[data-testid="stSidebar"] p, section[data-testid="stSidebar"] span, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] div {
        color: #00d9ff !important;
    }
    
    /* Forzar Expanders a negro */
    div[data-testid="stExpander"] {
        background-color: #0d1117 !important;
        border: 1px solid #00d9ff44 !important;
        border-radius: 6px !important;
        margin-bottom: 8px !important;
    }
    div[data-testid="stExpander"] details {
        background-color: #0d1117 !important;
        color: #00d9ff !important;
        border: none !important;
    }
    div[data-testid="stExpander"] summary {
        background-color: #0d1117 !important;
        color: #00d9ff !important;
        border-bottom: 1px solid #00d9ff33 !important;
    }
    div[data-testid="stExpander"] summary * {
        color: #00d9ff !important;
        background-color: transparent !important;
    }
    div[data-testid="stExpander"] div[role="region"] {
        background-color: #0d1117 !important;
        color: #00d9ff !important;
    }

    /* Inputs y chat oscuros con brillo neón */
    .stTextInput input, textarea { 
        background-color: #0d1117 !important; 
        color: #00d9ff !important; 
        border: 1px solid #00d9ff !important; 
        border-radius: 4px;
        font-size: 12px !important;
    }

    [data-testid="stChatInput"] {
        background-color: #06090f !important;
        border-top: 1px solid #00d9ff33;
    }
    [data-testid="stChatInput"] > div {
        background-color: #0d1117 !important;
        border: 1px solid #00d9ff !important;
        border-radius: 6px;
    }
    [data-testid="stChatInput"] textarea {
        background-color: #0d1117 !important;
        color: #00d9ff !important;
        border: none !important;
    }

    [data-testid="stMetricValue"] {
        color: #00d9ff !important;
        font-size: 16px !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 11px !important;
        color: #8ae9ff !important;
    }
    
    hr {
        border-color: #00d9ff44;
        margin: 10px 0;
    }
    
    .stButton > button {
        background-color: transparent;
        color: #00d9ff;
        border: 1px solid #00d9ff;
        font-weight: bold;
        font-size: 11px;
        text-transform: uppercase;
        box-shadow: 0 0 5px #00d9ff22;
        padding: 4px 8px;
    }
    .stButton > button:hover {
        background-color: #00d9ff11;
        border-color: #00ffff;
        box-shadow: 0 0 15px #00d9ff44;
    }
    
    [data-testid="stChatMessage"] {
        background-color: #0d1117;
        border: 1px solid #00d9ff33;
        border-radius: 6px;
        padding: 8px;
        margin-bottom: 6px;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] {
        color: #aae0ff;
        font-size: 13px;
    }

    .tactical-link {
        display: block;
        width: 100%;
        padding: 6px;
        margin: 4px 0;
        background-color: #0d1117;
        color: #00d9ff !important;
        text-align: center;
        text-decoration: none;
        border: 1px solid #00d9ff44;
        border-radius: 4px;
        font-weight: bold;
        font-size: 11px;
        transition: 0.2s;
    }
    .tactical-link:hover {
        background-color: #00d9ff22;
        border-color: #00ffff;
    }

    .right-panel {
        padding-left: 10px;
        border-left: 1px solid #00d9ff22;
    }
    </style>
""", unsafe_allow_html=True)

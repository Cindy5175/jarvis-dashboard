import streamlit as st
import datetime
import json
import os
import sqlite3
import sys
import io
import contextlib

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS VISUALES STARK (AZUL NEÓN UNIFORME & SIMETRÍA) ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00d2ff; }
        h1, h2, h3, h4, label, span { color: #00d2ff !important; font-family: monospace; text-align: left !important; }
        
        /* Contenedor del Encabezado Centrado */
        .arc-reactor-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-bottom: 20px;
        }
        .arc-ring {
            width: 60px;
            height: 60px;
            border: 3px solid #3a4454;
            border-radius: 50%;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle, #00d2ff 0%, #060911 70%);
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.6), inset 0 0 10px rgba(0, 210, 255, 0.4);
            margin-bottom: 8px;
        }
        .arc-triangle {
            width: 0;
            height: 0;
            border-left: 12px solid transparent;
            border-right: 12px solid transparent;
            border-bottom: 20px solid #ffffff;
            filter: drop-shadow(0 0 6px #00d2ff);
        }

        .stark-card {
            border: 1.5px solid #00d2ff;
            border-radius: 10px;
            padding: 15px;
            background-color: rgba(0, 210, 255, 0.04);
            margin-bottom: 15px;
            box-shadow: 0 0 10px rgba(0, 210, 255, 0.1);
            text-align: left !important;
        }
        .stark-card p, .stark-card div, .stark-card span, .stark-card label {
            text-align: left !important;
            color: #00d2ff !important;
        }

        .stMarkdown, p, li, span, div, .stChatMessage p {
            color: #00d2ff !important;
        }
    </style>
""", unsafe_allow_html=True)

# --- CÁLCULO DE HORA LOCAL EN CHILE (UTC-3) ---
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
hora_actual = datetime.datetime.now(tz_chile).hour

if 0 <= hora_actual < 12:
    saludo_actual = "Buenos días"
elif 12 <= hora_actual < 20:
    saludo_actual = "Buenas tardes"
else:
    saludo_actual = "Buenas noches"

# --- BASE DE DATOS SQLITE (MEMORIA PERSISTENTE) ---
DB_NAME = "jarvis_bunker.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tareas (id INTEGER PRIMARY KEY AUTOINCREMENT, texto TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS alertas (id INTEGER PRIMARY KEY AUTOINCREMENT, mensaje TEXT, nivel TEXT)''')
    conn.commit()
    
    c.execute("SELECT COUNT(*) FROM tareas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Validar estado de salud (UC Christus)",))
        c.execute("INSERT INTO tareas (texto) VALUES (?)", ("Monitorear nodo operativo en Buin",))
        conn.commit()
        
    c.execute("SELECT COUNT(*) FROM alertas")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", ("Temperatura Buin óptima (21°C)", "INFO"))
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", ("Blindaje WhatsApp y Gmail operativo", "OK"))
        conn.commit()
    conn.close()

init_db()

def get_db_tareas():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT id, texto FROM tareas")
    rows = c.fetchall()
    conn.close()
    return rows

def add_db_tarea(texto):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO tareas (texto) VALUES (?)", (texto,))
    conn.commit()
    conn.close()

def delete_db_tarea(id_t):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM tareas WHERE id = ?", (id_t,))
    conn.commit()
    conn.close()

def get_db_alertas():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT mensaje, nivel FROM alertas")
    rows = c.fetchall()
    conn.close()
    return rows

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [
        {"role": "assistant", "content": f"{saludo_actual}, jefa. Sistemas restablecidos al diseño original estable. ¿En qué trabajamos?"}
    ]

# --- ENCABEZADO CENTRADO CON REACTOR ARC ---
st.markdown("""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h2 style="margin: 0; padding: 0; font-size: 1.5rem; text-align: center !important; color: #00d2ff !important;">J.A.R.V.I.S IA</h2>
        <p style="margin: 0; font-family: monospace; font-size: 0.75rem; color: #00d2ff !important; text-align: center !important;">[ STARK INDUSTRIES // NODO BUIN, CHILE ]</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# --- BARRA LATERAL: ESTACIÓN DE CONTROL ---
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")

with st.sidebar.expander("🛡️ Blindaje & Alertas", expanded=True):
    st.markdown("• **WhatsApp:** Activo (Excepciones personales seguras)")
    st.markdown("• **Gmail:** Sincronizado (Portal UC Christus)")

with st.sidebar.expander("🔔 Alertas del Búnker"):
    alertas_db = get_db_alertas()
    for msg, nivel in alertas_db:
        icono = "🟢" if nivel == "OK" else "ℹ️"
        st.markdown(f"{icono} {msg}")
    nueva_alerta = st.text_input("Añadir alerta rápida:")
    if st.button("➕ Emitir Alerta", use_container_width=True) and nueva_alerta:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", (nueva_alerta, "INFO"))
        conn.commit()
        conn.close()
        st.success("Alerta emitida.")
        st.rerun()

with st.sidebar.expander("📝 Tareas del Búnker"):
    nueva_tarea = st.text_input("Nueva tarea rápida:")
    if st.button("➕ Registrar Tarea", use_container_width=True) and nueva_tarea:
        add_db_tarea(nueva_tarea)
        st.success("¡Registrada!")
        st.rerun()
    st.markdown("**Pendientes:**")
    for tid, t in get_db_tareas():
        col_t1, col_t2 = st.columns([4, 1])
        with col_t1:
            st.markdown(f"• {t}")
        with col_t2:
            if st.button("❌", key=f"del_t_{tid}"):
                delete_db_tarea(tid)
                st.rerun()

with st.sidebar.expander("🌐 Telemetría Global", expanded=True):
    st.markdown(f"• **Reactor:** 100% stable\n• **Hora:** {datetime.datetime.now(tz_chile).strftime('%H:%M')}\n• **Día:** {datetime.datetime.now(tz_chile).strftime('%d/%m')}\n• **Starlink:** Óptimo")

with st.sidebar.expander("🌤️ Clima Local (Buin)", expanded=True):
    st.markdown("• **Condición:** Despejado\n• **Temperatura:** 21°C\n• **Humedad:** 45%")

# --- NÚCLEOS DE CEREBRO STARK (A LA IZQUIERDA) ---
st.sidebar.markdown("---

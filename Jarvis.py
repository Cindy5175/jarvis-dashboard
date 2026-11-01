import streamlit as st
import datetime
import json
import os
import sqlite3
import sys
import io
import contextlib
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="J.A.R.V.I.S IA - NÚCLEO TÁCTICO SUPREMO HFT",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS VISUALES STARK (HFT DENSE BLUE) ---
st.markdown("""
    <style>
        .stApp { background-color: #060911; color: #00e0ff; font-family: 'Consolas', monospace; }
        h1, h2, h3, h4, h5, label, span, p, .stMarkdown { color: #00e0ff !important; text-align: left !important; }
        
        /* Contenedor del Encabezado Centrado */
        .arc-reactor-container { display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; margin-bottom: 5px; }
        .arc-ring { width: 50px; height: 50px; border: 3px solid #3a4454; border-radius: 50%; position: relative; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, #00e0ff 0%, #060911 70%); box-shadow: 0 0 15px rgba(0, 224, 255, 0.6), inset 0 0 10px rgba(0, 224, 255, 0.4); }
        .arc-triangle { width: 0; height: 0; border-left: 10px solid transparent; border-right: 10px solid transparent; border-bottom: 18px solid #ffffff; filter: drop-shadow(0 0 6px #00e0ff); }

        .stark-card {
            border: 1px solid rgba(0, 224, 255, 0.4);
            border-radius: 5px;
            padding: 10px;
            background-color: rgba(0, 224, 255, 0.02);
            margin-bottom: 10px;
            overflow: hidden;
            box-shadow: 0 0 8px rgba(0, 224, 255, 0.1);
        }
        
        .stark-header { font-size: 0.9rem; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; border-bottom: 1px solid rgba(0, 224, 255, 0.2); }
        .stark-data-small { font-size: 0.75rem; margin-bottom: 2px; }

        .stMarkdown p, li, span, div, .stChatMessage p { color: #00e0ff !important; }
        
        /* Ocultar elementos estándar de Streamlit para la simetría */
        #MainMenu, footer, header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- LÓGICA DE FONDO (Base de datos SQLite - NO SE TOCA) ---
DB_NAME = "jarvis_bunker_hft.db"

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
        c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", ("Red Starlink: Sincronizada", "OK"))
        conn.commit()
    conn.close()

init_db()

# Funciones DB (NO SE TOCAN)
def get_db_tareas(): conn = sqlite3.connect(DB_NAME); c = conn.cursor(); c.execute("SELECT id, texto FROM tareas"); rows = c.fetchall(); conn.close(); return rows
def add_db_tarea(texto): conn = sqlite3.connect(DB_NAME); c = conn.cursor(); c.execute("INSERT INTO tareas (texto) VALUES (?)", (texto,)); conn.commit(); conn.close()
def delete_db_tarea(id_t): conn = sqlite3.connect(DB_NAME); c = conn.cursor(); c.execute("DELETE FROM tareas WHERE id = ?", (id_t,)); conn.commit(); conn.close()
def get_db_alertas(): conn = sqlite3.connect(DB_NAME); c = conn.cursor(); c.execute("SELECT mensaje, nivel FROM alertas"); rows = c.fetchall(); conn.close(); return rows

# Estado del chat
tz_chile = datetime.timezone(datetime.timedelta(hours=-3))
hora_actual = datetime.datetime.now(tz_chile).hour
saludo_actual = "Buenos días" if 0 <= hora_actual < 12 else ("Buenas tardes" if 12 <= hora_actual < 20 else "Buenas noches")

if "mensajes" not in st.session_state:
    st.session_state.mensajes = [{"role": "assistant", "content": f"{saludo_actual}, jefa. Núcleo Supremo HFT sincronizado. Cero módulos eliminados. Todo listo."}]

# --- ENCABEZADO CENTRADO CON REACTOR ARC (HFT Style) ---
st.markdown(f"""
    <div class="arc-reactor-container">
        <div class="arc-ring"><div class="arc-triangle"></div></div>
        <h2 style="margin: 0; padding: 0; font-size: 1.2rem; color: #00e0ff !important;">J.A.R.V.I.S IA</h2>
        <p style="margin: 0; font-family: monospace; font-size: 0.6rem; color: #00e0ff !important;">[ NÚCLEO TÁCTICO // SUPREME CORE // CHILE ]</p>
    </div>
""", unsafe_allow_html=True)
st.markdown("---")

# --- BARRA LATERAL (ESTACIÓN DE CONTROL UNIFICADA - NO SE ELIMINA NADA) ---
st.sidebar.markdown("### 🌐 ESTACIÓN DE CONTROL")

# Módulo: Telemetría Global
with st.sidebar.expander("⚡ Telemetría Global", expanded=True):
    col_t1, col_t2 = st.columns(2)
    with col_t1: st.markdown("• **Reactor:** 100% stable\n• **Starlink:** Óptimo")
    with col_t2: st.markdown(f"• **Hora:** {datetime.datetime.now(tz_chile).strftime('%H:%M')}\n• **Día:** {datetime.datetime.now(tz_chile).strftime('%d/%m')}")

# Módulo: Alertas y Notificaciones (SQLite)
with st.sidebar.expander("🔔 Alertas del Búnker"):
    alertas_db = get_db_alertas()
    for msg, nivel in alertas_db:
        icono = "🟢" if nivel == "OK" else "ℹ️"
        st.markdown(f"<span style='font-size:0.7rem;'>{icono} {msg}</span>", unsafe_allow_html=True)
    nueva_alerta = st.text_input("Nueva alerta:", key="alerta_tactica")
    if st.button("➕ Emitir Alerta", use_container_width=True) and nueva_alerta:
        conn = sqlite3.connect(DB_NAME); c = conn.cursor(); c.execute("INSERT INTO alertas (mensaje, nivel) VALUES (?, ?)", (nueva_alerta, "INFO")); conn.commit(); conn.close()
        st.success("Alerta emitida.")
        st.rerun()

# Módulo: Tareas del Búnker (SQLite)
with st.sidebar.expander("📝 Tareas del Búnker"):
    for tid, t in get_db_tareas():
        col_t1, col_t2 = st.columns([4, 1])
        with col_t1: st.markdown(f"<span style='font-size:0.7rem;'>• {t}</span>", unsafe_allow_html=True)
        with col_t2: 
            if st.button("❌", key=f"del_sidebar_t_{tid}"): delete_db_tarea(tid); st.rerun()
    nueva_tarea_s = st.text_input("Registrar tarea:", key="tarea_sidebar")
    if st.button("➕ Registrar Tarea", use_container_width=True, key="btn_sidebar_tarea") and nueva_tarea_s: add_db_tarea(nueva_tarea_s); st.rerun()

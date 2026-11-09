import streamlit as st
import sqlite3
import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Recetas 24/7 | Colección de Libros & Guías",
    page_icon="📚",
    layout="centered"
)

# --- 2. BASE DE DATOS PROPIA ---
DB_RECETAS = "recetas_247.db"

def init_db():
    conn = sqlite3.connect(DB_RECETAS)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            cliente_nombre TEXT,
            cliente_email TEXT,
            items TEXT,
            total INTEGER,
            formato TEXT,
            estado TEXT DEFAULT 'Pagado / Boleta Emitida'
        )
    """)
    conn.commit()
    conn.close()

init_db()

def guardar_pedido(nombre, email, items_str, total, formato):
    conn = sqlite3.connect(DB_RECETAS)
    cursor = conn.cursor()
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO pedidos (fecha, cliente_nombre, cliente_email, items, total, formato) VALUES (?, ?, ?, ?, ?, ?)",
        (fecha_actual, nombre, email, items_str, total, formato)
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id

# --- 3. ESTILOS VISUALES ARTESANALES (TONOS CREMA / MINIMALISTA) ---
st.markdown("""
<style>
    .stApp {
        background-color: #f7f4ed !important;
        color: #36322e !important;
        font-family: 'Georgia', serif;
    }
    
    h1, h2, h3, h4, p, span, label {
        color: #36322e !important;
    }

    /* Cápsulas de filtro */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        background-color: #ebdcd0 !important;
        color: #36322e !important;
        border-radius: 20px !important;
        border: 1px solid #d4c3b5 !important;
        font-weight: 500;
        box-shadow: none !important;
    }

    /* Botones primarios */
    .stButton > button {
        background-color: #556b2f !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: bold;
        width: 100%;
        padding: 10px;
    }

    .stButton > button p, .stButton > button span {
        color: #ffffff !important;
    }

    /* Tarjeta de Libro */
    .book-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 15px;
        border: 1px solid #e8e2d8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    .price-tag {
        font-size: 1.2rem;
        font-weight: bold;
        color: #8b4513 !important;
    }
    
    .badge-format {
        background-color: #e2d7c5;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
        color: #5c4d3c !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. CATALOGO REAL DE LIBROS DE COCINA ---
LIBROS = [
    {
        "id": 1,
        "titulo": "El Arte de la Masa Madre & Panadería",
        "categoria": "Panadería",
        "autor": "Taller Gastronómico",
        "precio_digital": 9900,
        "precio_fisico": 18900,
        "paginas": "180 págs.",
        "descripcion": "Guía definitiva con tiempos de fermentación paso a paso, hidrataciones avanzadas y 25 recetas de panes artesanales.",
        "img": "https://images.unsplash.com/photo-1549931319-a545dcf3bc73?w=500"
    },
    {
        "id": 2,
        "titulo": "Repostería Minimalista & Alta Pastelería",
        "categoria": "Repostería",
        "autor": "Taller Gastronómico",
        "precio_digital": 11900,
        "precio_fisico": 22900,
        "paginas": "210 págs.",
        "descripcion": "Técnicas de horneado preciso, tartas de autor, rellenos artesanales y secretos de la masa quebrada.",
        "img": "https://images.unsplash.com/photo-1517433670267-08bbd4be890f?w=500"
    },
    {
        "id": 3,
        "titulo": "Cocina de Origen & Sabores del Sur",
        "categoria": "Cocina Chilena",
        "autor": "Ediciones Recetas 24/7",
        "precio_digital": 8900,
        "precio_fisico": 16900,
        "paginas": "150 págs.",
        "descripcion": "Recetario rescatado de guisos tradicionales, curantos en olla, empanadas de pino perfecto y postres típicos.",
        "img": "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?w=500"
    },
    {
        "id": 4,
        "titulo": "Pastas Frescas & Salsas de Cocción Lenta",
        "categoria": "Técnicas",
        "autor": "Taller Gastronómico",
        "precio_digital": 10500,
        "precio_fisico": 19900,
        "paginas": "165 págs.",
        "descripcion": "Aprende a dominar el amasado manual, cortes de pastas largas y estofados tradicionales explicados al detalle.",
        "img": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=500"
    }
]

if "carrito" not in st.session_state:
    st.session_state.carrito = {}

# --- 5. CABECERA ---
st.markdown("<h1 style='text-align: center; font-family: serif; margin-bottom: 5px;'>Biblioteca Recetas 24/7</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777; font-style: italic;'>Libros y recetarios de autor. Conocimiento gastronómico a tu alcance 24/7.</p>", unsafe_allow_html=True)
st.markdown("---

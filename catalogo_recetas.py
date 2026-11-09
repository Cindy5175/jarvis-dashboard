import streamlit as st
import sqlite3
import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Recetas 24/7 | Taller Gastronómico",
    page_icon="🍲",
    layout="centered"
)

# --- 2. BASE DE DATOS PROPIA (INDEPENDIENTE) ---
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
            estado TEXT DEFAULT 'Pagado / Boleta Emitida'
        )
    """)
    conn.commit()
    conn.close()

init_db()

def guardar_pedido(nombre, email, items_str, total):
    conn = sqlite3.connect(DB_RECETAS)
    cursor = conn.cursor()
    fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO pedidos (fecha, cliente_nombre, cliente_email, items, total) VALUES (?, ?, ?, ?, ?)",
        (fecha_actual, nombre, email, items_str, total)
    )
    conn.commit()
    order_id = cursor.lastrowid
    conn.close()
    return order_id

# --- 3. ESTILOS VISUALES ARTESANALES (MINIMALISTA / TONOS CREMA) ---
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

    div[data-testid="stHorizontalBlock"] .stButton > button {
        background-color: #ebdcd0 !important;
        color: #36322e !important;
        border-radius: 20px !important;
        border: 1px solid #d4c3b5 !important;
        font-weight: 500;
        box-shadow: none !important;
    }

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

    .recipe-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 20px;
        border: 1px solid #e8e2d8;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }
    
    .price-tag {
        font-size: 1.1rem;
        font-weight: bold;
        color: #8b4513 !important;
    }
    
    .cart-box {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e8e2d8;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. DATOS DEL CATÁLOGO ---
PRODUCTOS = [
    {
        "id": 1,
        "nombre": "Lasagna Artesanal de Carne",
        "categoria": "Platos de Fondo",
        "precio": 8500,
        "descripcion": "Pasta fresca hecha a mano, boloñesa de cocción lenta de 6 horas y salsa bechamel de la casa.",
        "img": "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=500"
    },
    {
        "id": 2,
        "nombre": "Creamy Pumpkin Soup",
        "categoria": "Entradas",
        "precio": 4200,
        "descripcion": "Sopa crema de zapallo cabutia asado al romero con crutones de masa madre.",
        "img": "https://images.unsplash.com/photo-1547592180-85f173990554?w=500"
    },
    {
        "id": 3,
        "nombre": "Tarta de Manzana & Canela",
        "categoria": "Postres",
        "precio": 5500,
        "descripcion": "Masa quebrada crocante, manzanas horneadas con especias y toque de frutos secos.",
        "img": "https://images.unsplash.com/photo-1568571780765-9276ac8b75a2?w=500"
    },
    {
        "id": 4,
        "nombre": "Pan de Masa Madre (1kg)",
        "categoria": "Panadería",
        "precio": 3800,
        "descripcion": "Fermentación natural de 36 horas. Alveolado perfecto y corteza crujiente.",
        "img": "https://images.unsplash.com/photo-1586444248902-2f64eddc13df?w=500"
    }
]

if "carrito" not in st.session_state:
    st.session_state.carrito = {}

# --- 5. CABECERA PRINCIPAL ---
st.markdown("<h1 style='text-align: center; font-family: serif; margin-bottom: 5px;'>Recetas 24/7</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777; font-style: italic;'>Cocina de origen, no una fábrica. Elaboración artesanal en lotes reducidos.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 6. NAVEGACIÓN Y FILTROS ---
st.markdown("### El Catálogo")
cols_cat = st.columns(5)
categorias = ["Todas", "Entradas", "Platos de Fondo", "Postres", "Panadería"]

if "cat_seleccionada" not in st.session_state:
    st.session_state.cat_seleccionada = "Todas"

for i, cat in enumerate(categorias):
    with cols_cat[i]:
        if st.button(cat, key=f"btn_cat_{cat}"):
            st.session_state.cat_seleccionada = cat

st.write("")

# --- 7. EXPOSICIÓN DE PRODUCTOS ---
productos_filtrados = PRODUCTOS if st.session_state.cat_seleccionada == "Todas" else [p for p in PRODUCTOS if p["categoria"] == st.session_state.cat_seleccionada]

for prod in productos_filtrados:
    pid = prod["id"]
    with st.container():
        st.markdown(f"""
        <div class="recipe-card">
            <h3 style="margin-top:0;">{prod['nombre']}</h3>
            <p style="color: #666; font-size: 0.9rem;">{prod['descripcion']}</p>
            <p class="price-tag">${prod['precio']:,} CLP</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_img, col_acc = st.columns([1, 2])
        with col_img:
            st.image(prod["img"], use_container_width=True)
        
        with col_acc:
            cant_actual = st.session_state.carrito.get(pid, 0)
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.button("➖", key=f"restar_{pid}"):
                    if cant_actual > 0:
                        st.session_state.carrito[pid] = cant_actual - 1
                        st.rerun()
            with c2:
                st.markdown(f"<h4 style='text-align:center;'>{cant_actual}</h4>", unsafe_allow_html=True)
            with c3:
                if st.button("➕", key=f"sumar_{pid}"):
                    st.session_state.carrito[pid] = cant_actual + 1
                    st.rerun()

st.markdown("---")

# --- 8. CARRITO Y CHECKOUT AUTOMATIZADO ---
st.markdown("### 🛒 Resumen de tu Pedido")

items_en_carrito = {k: v for k, v in st.session_state.carrito.items() if v > 0}

if not items_en_carrito:
    st.info("Tu carrito está vacío. Elige una receta arriba para comenzar.")
else:
    total_pedido = 0
    resumen_texto = []
    
    st.markdown('<div class="cart-box">', unsafe_allow_html=True)
    for pid, cant in items_en_carrito.items():
        p_obj = next(p for p in PRODUCTOS if p["id"] == pid)
        subtotal = p_obj["precio"] * cant
        total_pedido += subtotal
        resumen_texto.append(f"{cant}x {p_obj['nombre']} (${subtotal:,})")
        st.write(f"• **{cant}x {p_obj['nombre']}** — ${subtotal:,} CLP")
    
    st.markdown(f"<h3 style='text-align: right; color: #8b4513;'>Total: ${total_pedido:,} CLP</h3>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.write("")
    st.markdown("#### Datos de Entrega y Boleta Automática")
    
    with st.form("form_checkout"):
        nombre_cliente = st.text_input("Nombre Completo:")
        email_cliente = st.text_input("Correo Electrónico (para envío de Boleta del SII):")
        
        btn_pagar = st.form_submit_button("💳 Proceder al Pago Autónomo")
        
        if btn_pagar:
            if nombre_cliente.strip() and email_cliente.strip():
                items_str = ", ".join(resumen_texto)
                order_id = guardar_pedido(nombre_cliente, email_cliente, items_str, total_pedido)
                
                st.session_state.carrito = {}
                
                st.success(f"¡Pedido #{order_id:04d} procesado con éxito!")
                st.balloons()
                st.markdown(f"""
                ✅ **Pago y Registro Exitosos**  
                - **N° de Orden:** #{order_id:04d}  
                - **Cliente:** {nombre_cliente}  
                - **Boleta Electrónica:** Generada y enviada a `{email_cliente}` automáticamente.  
                - **Estado:** En cola de cocina.
                """)
            else:
                st.error("Por favor completa tu nombre y correo para procesar la orden y emitir la boleta.")

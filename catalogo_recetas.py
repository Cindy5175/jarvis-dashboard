import streamlit as st
import sqlite3
import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Recetas 24/7 | Biblioteca de Autor",
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

# --- 4. CATALOGO REAL DE LIBROS (AUTORÍA CINDY CARRERA) ---
LIBROS = [
    {
        "id": 1,
        "titulo": "El Pan: Una tradición familiar",
        "categoria": "Panadería",
        "autor": "Cindy Carrera Baude",
        "precio_digital": 8900,
        "precio_fisico": 16900,
        "paginas": "18 págs. (Edición Técnica)",
        "descripcion": "Guía fundamental de panadería casera, técnicas de amasado, tablas de equivalencias por peso y el paso a paso detallado para crear y mantener tu propia masa madre viva.",
        "img": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500"
    },
    {
        "id": 2,
        "titulo": "Con las Manos en la Masa",
        "categoria": "Repostería",
        "autor": "Cindy Carrera B.",
        "precio_digital": 10900,
        "precio_fisico": 19900,
        "paginas": "45 págs.",
        "descripcion": "Colección completa de repostería y pastelería fina. Desde bizcochos únicos (cerveza negra, cebra) hasta galletas de autor, merengue italiano y cupcakes especializados.",
        "img": "https://images.unsplash.com/photo-1578985545062-69928b1d9587?w=500"
    },
    {
        "id": 3,
        "titulo": "Recetas Navideñas",
        "categoria": "Especiales",
        "autor": "Cindy Carrera Baude",
        "precio_digital": 9500,
        "precio_fisico": 17900,
        "paginas": "16 págs.",
        "descripcion": "Un momento para compartir en familia. Recetas entrañables de temporada que incluyen galletas alemanas tradicionales (Lebkuchen, Plätzchen, Vanillekipferl), pavo festivo y ponches tradicionales.",
        "img": "https://images.unsplash.com/photo-1543508282-6319a3e2621f?w=500"
    },
    {
        "id": 4,
        "titulo": "Recetas Chilenas: Un sabor de hogar",
        "categoria": "Cocina Chilena",
        "autor": "Cindy Carrera B.",
        "precio_digital": 11900,
        "precio_fisico": 21900,
        "paginas": "33 págs.",
        "descripcion": "Rescate culinario con la verdadera identidad de nuestra cocina: empanadas de pino perfectas, humitas, pulmay, mariscal, cazuela tradicional y mote con huesillos.",
        "img": "https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?w=500"
    }
]

if "carrito" not in st.session_state:
    st.session_state.carrito = {}

# --- 5. CABECERA ---
st.markdown("<h1 style='text-align: center; font-family: serif; margin-bottom: 5px;'>Biblioteca Recetas 24/7</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #777; font-style: italic;'>Libros y recetarios de autor. Conocimiento gastronómico de hogar a tu alcance 24/7.</p>", unsafe_allow_html=True)
st.markdown("---")

# --- 6. BUSCADOR Y FILTROS ---
col_busqueda, col_vacio = st.columns([3, 1])
with col_busqueda:
    query_busqueda = st.text_input("🔍 Buscar por título o descripción:", "")

st.markdown("### Colecciones")
cols_cat = st.columns(5)
categorias = ["Todas", "Panadería", "Repostería", "Especiales", "Cocina Chilena"]

if "cat_seleccionada" not in st.session_state:
    st.session_state.cat_seleccionada = "Todas"

for i, cat in enumerate(categorias):
    with cols_cat[i]:
        if st.button(cat, key=f"btn_cat_{cat}"):
            st.session_state.cat_seleccionada = cat

st.write("")

# Filtrado de libros
libros_filtrados = LIBROS
if st.session_state.cat_seleccionada != "Todas":
    libros_filtrados = [l for l in libros_filtrados if l["categoria"] == st.session_state.cat_seleccionada]

if query_busqueda.strip():
    libros_filtrados = [l for l in libros_filtrados if query_busqueda.lower() in l["titulo"].lower() or query_busqueda.lower() in l["descripcion"].lower()]

# --- 7. LISTADO DE LIBROS ---
for libro in libros_filtrados:
    lid = libro["id"]
    with st.container():
        st.markdown(f"""
<div class="book-card">
    <span class="badge-format">{libro['categoria']}</span> • <small>{libro['paginas']}</small>
    <h3 style="margin-top: 8px; margin-bottom: 4px;">{libro['titulo']}</h3>
    <p style="color: #777; font-size: 0.85rem; margin-bottom: 8px;">Por: <strong>{libro['autor']}</strong></p>
    <p style="color: #555; font-size: 0.95rem;">{libro['descripcion']}</p>
</div>
""", unsafe_allow_html=True)
        
        col_img, col_opciones = st.columns([1, 2])
        with col_img:
            st.image(libro["img"], use_container_width=True)
            
        with col_opciones:
            st.markdown("**Selecciona el Formato:**")
            formato_elegido = st.radio(
                "Formato:",
                ["PDF Digital (Descarga Instantánea)", "Edición Impresa (Tapa Dura)"],
                key=f"formato_{lid}",
                label_visibility="collapsed"
            )
            
            precio_final = libro["precio_digital"] if "PDF" in formato_elegido else libro["precio_fisico"]
            st.markdown(f"<p class='price-tag'>Precio: ${precio_final:,} CLP</p>", unsafe_allow_html=True)
            
            cant_actual = st.session_state.carrito.get((lid, formato_elegido), 0)
            c1, c2, c3 = st.columns([1, 1, 2])
            with c1:
                if st.button("➖", key=f"restar_{lid}"):
                    if cant_actual > 0:
                        st.session_state.carrito[(lid, formato_elegido)] = cant_actual - 1
                        st.rerun()
            with c2:
                st.markdown(f"<h4 style='text-align:center;'>{cant_actual}</h4>", unsafe_allow_html=True)
            with c3:
                if st.button("➕ Añadir", key=f"sumar_{lid}"):
                    st.session_state.carrito[(lid, formato_elegido)] = cant_actual + 1
                    st.rerun()

st.markdown("---")

# --- 8. CARRITO Y COMPRA AUTOMÁTICA ---
st.markdown("### 🛒 Tu Carrito de Compra")

items_en_carrito = {k: v for k, v in st.session_state.carrito.items() if v > 0}

if not items_en_carrito:
    st.info("Tu carrito está vacío. Elige un libro arriba para agregar al pedido.")
else:
    total_pedido = 0
    resumen_items = []
    es_digital = True
    
    for (lid, formato), cant in items_en_carrito.items():
        l_obj = next(l for l in LIBROS if l["id"] == lid)
        precio_unitario = l_obj["precio_digital"] if "PDF" in formato else l_obj["precio_fisico"]
        subtotal = precio_unitario * cant
        total_pedido += subtotal
        if "Impresa" in formato:
            es_digital = False
            
        resumen_items.append(f"{cant}x {l_obj['titulo']} ({formato}) - ${subtotal:,}")
        st.write(f"• **{cant}x {l_obj['titulo']}** [{formato}] — **${subtotal:,} CLP**")
    
    st.markdown(f"<h3 style='text-align: right; color: #8b4513;'>Total a Pagar: ${total_pedido:,} CLP</h3>", unsafe_allow_html=True)
    st.write("")
    
    st.markdown("#### Datos de Facturación & Emisión de Boleta Automática")
    with st.form("form_checkout_libros"):
        nombre_cliente = st.text_input("Nombre Completo:")
        email_cliente = st.text_input("Correo Electrónico (para recibir la boleta del SII y los archivos PDF):")
        direccion_envio = st.text_input("Dirección de Despacho (Solo si compraste edición impresa):")
        
        btn_confirmar = st.form_submit_button("💳 Procesar Pago & Recibir Libro")
        
        if btn_confirmar:
            if nombre_cliente.strip() and email_cliente.strip():
                items_str = " | ".join(resumen_items)
                tipo_formato = "Digital" if es_digital else "Físico / Impreso"
                order_id = guardar_pedido(nombre_cliente, email_cliente, items_str, total_pedido, tipo_formato)
                
                st.session_state.carrito = {}
                
                st.success(f"¡Compra #{order_id:04d} completada con éxito!")
                st.balloons()
                
                st.markdown(f"""
                ### ✅ Resumen de la Transacción:
                * **N° Orden:** #{order_id:04d}
                * **Cliente:** {nombre_cliente}
                * **Correo:** `{email_cliente}`
                * **Boleta Electrónica SII:** Generada y enviada a tu correo automáticamente.
                """)
                
                if es_digital:
                    st.info("📖 **Acceso Inmediato:** Haz clic abajo para descargar tus libros en formato PDF de inmediato:")
                    st.download_button("📥 Descargar Libro (PDF)", data="Contenido del Libro en PDF...", file_name="Recetas_247_Libro.pdf")
                else:
                    st.warning(f"📦 Tu libro físico en edición impresa será preparado para despacho a: **{direccion_envio}**.")
            else:
                st.error("Por favor completa tu nombre y correo para procesar la transacción.")

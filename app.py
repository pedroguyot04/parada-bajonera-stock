# python3 -m streamlit run app.py

import streamlit as st
from db import get_productos, insertar_producto, actualizar_stock, create_tables
from datetime import date

create_tables()

st.title("Control de Stock - Parada Bajonera")

# Inicializar en sesión
if 'ultimo_movimiento' not in st.session_state:
    st.session_state['ultimo_movimiento'] = None

# Función para guardar movimiento
def guardar_movimiento(producto_id, cantidad):
    st.session_state['ultimo_movimiento'] = {
        'producto_id': producto_id,
        'cantidad': cantidad
    }

# Función para deshacer último movimiento
def deshacer_ultimo_movimiento():
    mov = st.session_state['ultimo_movimiento']
    if mov:
        # Revertir sumando la cantidad inversa
        actualizar_stock(mov['producto_id'], -mov['cantidad'])
        st.success("Último movimiento deshecho correctamente.")
        st.session_state['ultimo_movimiento'] = None
    else:
        st.info("No hay movimientos para deshacer.")

# ENTRADA DE STOCK
st.subheader("ENTRADA DE STOCK")
with st.form("form_entrada", clear_on_submit=True):
    productos = get_productos()
    opciones = {f"{p[1]} (Stock: {p[2]})": p[0] for p in productos}  
    producto_entrada = st.selectbox("Producto", list(opciones.keys()))
    cantidad_entrada = st.number_input("Cantidad a ingresar", min_value=1, step=1)
    if st.form_submit_button("Agregar entrada"):
        prod_id = opciones[producto_entrada]
        actualizar_stock(prod_id, cantidad_entrada)  # suma stock
        guardar_movimiento(prod_id, cantidad_entrada)
        st.success(f"Se agregó {cantidad_entrada} unidades a {producto_entrada}")

# SALIDA DE STOCK
st.subheader("SALIDA DE STOCK")
with st.form("form_salida", clear_on_submit=True):
    productos = get_productos()
    opciones = {f"{p[1]} (Stock: {p[2]})": p[0] for p in productos}
    producto_salida = st.selectbox("Producto", list(opciones.keys()))
    cantidad_salida = st.number_input("Cantidad a retirar", min_value=1, step=1)
    if st.form_submit_button("Registrar salida"):
        prod_id = opciones[producto_salida]
        stock_actual = next(p[2] for p in productos if p[0] == prod_id)
        if cantidad_salida > stock_actual:
            st.error("No hay stock suficiente para esta salida.")
        else:
            actualizar_stock(prod_id, -cantidad_salida)  # resta stock
            guardar_movimiento(prod_id, -cantidad_salida)
            st.success(f"Se retiraron {cantidad_salida} unidades de {producto_salida}")

# Botón para deshacer último movimiento
if st.button("Deshacer último movimiento"):
    deshacer_ultimo_movimiento()

# Tabla actualizada
st.write("### Productos y stock actuales:")
productos = get_productos()
if productos:
    st.table(
        {
            "ID": [p[0] for p in productos],
            "Nombre": [p[1] for p in productos],
            "Stock": [p[2] for p in productos],
            "Precio ($)": [p[3] for p in productos],
            "Última Reposición": [p[4] for p in productos],
        }
    )
else:
    st.info("No hay productos cargados.")

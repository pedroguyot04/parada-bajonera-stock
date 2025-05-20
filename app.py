# python3 -m streamlit run app.py

import streamlit as st
from db import (
    get_productos,
    insertar_producto,
    actualizar_stock,
    create_tables,
    eliminar_producto,
)
from datetime import date
import pandas as pd

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

# Función para deshacer último movimiento (incluye creación y eliminación)
def deshacer_ultimo_movimiento():
    mov = st.session_state['ultimo_movimiento']
    if mov:
        tipo = mov.get('tipo', 'stock')
        if tipo == 'eliminacion':
            insertar_producto(
                mov['nombre'],
                mov['cantidad'],
                mov['precio'],
                mov['fecha_reposicion']
            )
            st.success(f"Se revirtió eliminación del producto '{mov['nombre']}'")
        elif tipo == 'creacion':
            eliminar_producto(mov['producto_id'])
            st.success(f"Se revirtió creación del producto '{mov['nombre']}'")
        else:
            actualizar_stock(mov['producto_id'], -mov['cantidad'])
            st.success("Último movimiento deshecho correctamente.")
        st.session_state['ultimo_movimiento'] = None
    else:
        st.info("No hay movimientos para deshacer.")

# ENTRADA DE STOCK
st.subheader("ENTRADA DE STOCK")

productos = get_productos()
nombres_productos = [p[1] for p in productos]

if 'producto_seleccionado' not in st.session_state:
    st.session_state['producto_seleccionado'] = None

with st.form("form_buscar_producto"):
    nombre_producto = st.text_input("Nombre del producto")
    buscar = st.form_submit_button("Buscar / Crear producto")
    if buscar:
        if nombre_producto.strip() == "":
            st.error("Por favor, ingresá el nombre del producto.")
        else:
            st.session_state['producto_seleccionado'] = nombre_producto.strip()

if st.session_state['producto_seleccionado']:
    prod_name = st.session_state['producto_seleccionado']
    if prod_name in nombres_productos:
        st.write(f"Producto existente: **{prod_name}**")
        with st.form("form_reponer_stock"):
            cantidad = st.number_input("Cantidad a ingresar", min_value=1, step=1)
            submit_reponer = st.form_submit_button("Agregar stock")
            if submit_reponer:
                prod_id = next(p[0] for p in productos if p[1] == prod_name)
                actualizar_stock(prod_id, cantidad)
                guardar_movimiento(prod_id, cantidad)
                st.success(f"Se agregó {cantidad} unidades a '{prod_name}'.")
                st.session_state['producto_seleccionado'] = None
    else:
        st.write(f"Producto nuevo: **{prod_name}**")
        with st.form("form_nuevo_producto"):
            cantidad = st.number_input("Cantidad inicial", min_value=1, step=1)
            precio = st.number_input("Precio unitario (opcional)", min_value=0.0, step=0.1)
            fecha_reposicion = st.date_input("Fecha de ingreso", value=date.today())
            submit_nuevo = st.form_submit_button("Crear producto")
            if submit_nuevo:
                insertar_producto(prod_name, cantidad, precio, fecha_reposicion)
                prod_id = next(p[0] for p in get_productos() if p[1] == prod_name)
                st.session_state['ultimo_movimiento'] = {
                    'tipo': 'creacion',
                    'producto_id': prod_id,
                    'nombre': prod_name,
                    'cantidad': cantidad,
                    'precio': precio,
                    'fecha_reposicion': fecha_reposicion
                }
                st.success(f"Producto '{prod_name}' creado con {cantidad} unidades.")
                st.session_state['producto_seleccionado'] = None

# SALIDA DE STOCK
st.subheader("SALIDA DE STOCK")

productos = get_productos()
if productos:
    opciones = {f"{p[1]} (Stock: {p[2]})": p[0] for p in productos}
    with st.form("form_salida", clear_on_submit=True):
        producto_salida = st.selectbox("Producto", list(opciones.keys()))
        cantidad_salida = st.number_input("Cantidad a retirar", min_value=1, step=1)
        if st.form_submit_button("Registrar salida"):
            prod_id = opciones[producto_salida]
            stock_actual = next(p[2] for p in productos if p[0] == prod_id)
            if cantidad_salida > stock_actual:
                st.error("No hay stock suficiente para esta salida.")
            else:
                actualizar_stock(prod_id, -cantidad_salida)
                guardar_movimiento(prod_id, -cantidad_salida)
                st.success(f"Se retiraron {cantidad_salida} unidades de {producto_salida}")
else:
    st.info("No hay productos disponibles. Agregá uno primero.")

# ELIMINAR PRODUCTO
st.subheader("ELIMINAR PRODUCTO")

productos = get_productos()
if productos:
    opciones = {f"{p[1]} (Stock: {p[2]})": p[0] for p in productos}
    producto_eliminar = st.selectbox("Seleccioná el producto a eliminar", list(opciones.keys()))
    if st.button("Eliminar producto seleccionado"):
        prod_id = opciones[producto_eliminar]
        prod = next(p for p in productos if p[0] == prod_id)
        st.session_state['ultimo_movimiento'] = {
            'tipo': 'eliminacion',
            'producto_id': prod_id,
            'nombre': prod[1],
            'cantidad': prod[2],
            'precio': prod[3],
            'fecha_reposicion': prod[4],
        }
        eliminar_producto(prod_id)
        st.success(f"Producto '{producto_eliminar}' eliminado correctamente.")
else:
    st.info("No hay productos para eliminar.")

# Botón para deshacer último movimiento
if st.button("Deshacer último movimiento"):
    deshacer_ultimo_movimiento()

# Tabla de productos sin la columna ID
st.write("### Productos y stock actuales:")
productos = get_productos()
if productos:
    data = {
        "Nombre": [p[1] for p in productos],
        "Stock": [p[2] for p in productos],
        "Precio ($)": [p[3] for p in productos],
        "Última Reposición": [p[4] for p in productos],
    }
    df = pd.DataFrame(data)
    st.dataframe(df)
else:
    st.info("No hay productos cargados.")

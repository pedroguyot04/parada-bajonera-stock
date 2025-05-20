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

# Cargar y aplicar estilos CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

create_tables()

st.title("Control de Stock - Parada Bajonera")

# Inicializar en sesión
if 'ultimo_movimiento' not in st.session_state:
    st.session_state['ultimo_movimiento'] = None

# Función para guardar movimiento
def guardar_movimiento(producto_id, cantidad, fue_creado=False, fue_eliminado=False):
    st.session_state['ultimo_movimiento'] = {
        'producto_id': producto_id,
        'cantidad': cantidad,
        'fue_creado': fue_creado,
        'fue_eliminado': fue_eliminado
    }

# Función para deshacer último movimiento
def deshacer_ultimo_movimiento():
    mov = st.session_state['ultimo_movimiento']
    if mov:
        if mov.get("fue_eliminado"):
            st.warning("No se puede deshacer la eliminación de productos todavía.")
        elif mov.get("fue_creado"):
            eliminar_producto(mov['producto_id'])
            st.success("Se eliminó el producto recientemente creado.")
        else:
            actualizar_stock(mov['producto_id'], -mov['cantidad'])
            st.success("Último movimiento deshecho correctamente.")
        st.session_state['ultimo_movimiento'] = None
    else:
        st.info("No hay movimientos para deshacer.")

# ENTRADA DE STOCK (nuevo + reposición)
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
                nuevo_prod = get_productos()
                prod_id = next(p[0] for p in nuevo_prod if p[1] == prod_name)
                guardar_movimiento(prod_id, cantidad, fue_creado=True)
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
        eliminar_producto(prod_id)
        guardar_movimiento(prod_id, 0, fue_eliminado=True)
        st.success(f"Producto '{producto_eliminar}' eliminado correctamente.")
else:
    st.info("No hay productos para eliminar.")

# Botón para deshacer último movimiento
if st.button("Deshacer último movimiento"):
    deshacer_ultimo_movimiento()

# Actualizar productos
productos = get_productos()

# MÉTRICAS
if productos:
    costo_total = sum([p[2] * p[3] for p in productos if p[2] and p[3]])
    total_unidades = sum([p[2] for p in productos if p[2]])
    st.metric("Costo total actual en stock ($)", f"{costo_total:,.2f}")
    st.metric("Total de unidades en stock", f"{total_unidades}")

# TABLA
st.write("### Productos y stock actuales:")
if productos:
    data = {
        "Nombre": [p[1] for p in productos],
        "Stock": [p[2] for p in productos],
        "Precio ($)": [p[3] for p in productos],
        "Última Reposición": [p[4] for p in productos],
    }
    st.dataframe(data)
else:
    st.info("No hay productos cargados.")

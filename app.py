import streamlit as st
from db import get_productos, insertar_producto

st.title("Control de Stock - Panchería")

# Mostrar productos
productos = get_productos()
st.write("### Productos y stock actuales:")
for prod in productos:
    st.write(f"{prod[1]} - Stock: {prod[2]} - Precio: ${prod[3]}")

# Formulario para agregar producto nuevo
st.write("### Agregar producto nuevo")
with st.form("form_producto"):
    nombre = st.text_input("Nombre")
    stock = st.number_input("Stock", min_value=0, step=1)
    precio = st.number_input("Precio", min_value=0.0, step=0.01, format="%.2f")
    submitted = st.form_submit_button("Agregar")
    if submitted:
        insertar_producto(nombre, stock, precio)
        st.success(f"Producto {nombre} agregado correctamente.")
        # Para que el usuario vea el cambio, recargá la página manualmente.

st.write("AAAAAAA")
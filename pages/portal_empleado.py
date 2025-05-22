import streamlit as st
from datetime import datetime
from db_modules.dbStock import get_productos, actualizar_stock
from db_modules.dbResumenDiario import insertar_venta

st.title("📋 Portal para Empleados - Registro de Ventas")

# Fecha y turno
fecha_hoy = datetime.today().date()
turno = st.selectbox("Turno", ["mañana", "tarde"])

# Productos
productos = get_productos()

if not productos:
    st.warning("⚠️ No hay productos cargados en el sistema.")
    st.stop()

producto_nombres = [f"{p[1]} (Stock: {p[2]})" for p in productos]
producto_seleccionado = st.selectbox("Producto vendido", producto_nombres)

# Obtener ID y stock del producto seleccionado
producto_index = producto_nombres.index(producto_seleccionado)
producto_id = productos[producto_index][0]
stock_actual = productos[producto_index][2]

# Cantidad vendida
cantidad = st.number_input("Cantidad", min_value=1, max_value=stock_actual, step=1)

# Forma de pago
forma_pago = st.selectbox("Forma de pago", ["Efectivo", "Mercado Pago"])

# Monto total
monto = st.number_input("Monto total ($)", min_value=0.0, format="%.2f")

# Botón para registrar
if st.button("Registrar venta"):
    if cantidad > stock_actual:
        st.error("❌ No hay suficiente stock disponible.")
    else:
        insertar_venta(fecha_hoy, turno, producto_id, cantidad, forma_pago, monto)
        actualizar_stock(producto_id, -cantidad)
        st.success("✅ Venta registrada correctamente.")

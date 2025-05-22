import streamlit as st
import pandas as pd
from datetime import date

#Import productos
from db import (
    get_productos,
    insertar_producto,
    eliminar_producto,
    editar_producto
)

#----------------------------------------------------------   ARRANCA SECCION PRODUCTOS   ----------------------------------------------------------

st.write("---")
st.header("STOCK")

# Inicializar en sesión
if 'producto_editando' not in st.session_state:
    st.session_state['producto_editando'] = None
if 'ultimo_movimiento' not in st.session_state:
    st.session_state['ultimo_movimiento'] = None

# Función para forzar recarga
def recargar_app():
    st.rerun()

# Obtener productos actualizados
productos = get_productos()

# Métricas de stock
if productos:
    costo_total = sum([p[2] * p[3] for p in productos if p[2] and p[3]])
    total_unidades = sum([p[2] for p in productos if p[2]])

    col1, col2 = st.columns(2)
    col1.metric("Costo total actual en stock ($)", f"{costo_total:,.2f}")
    col2.metric("Total de unidades en stock", f"{total_unidades:,}")

# --- FORMULARIO AGREGAR PRODUCTO FIJO ---
with st.expander("Agregar nuevo producto"):
    with st.form("form_agregar_producto"):
        nombre = st.text_input("Nombre del producto")
        cantidad = st.number_input("Cantidad inicial", min_value=1, step=1)
        precio = st.number_input("Precio unitario ($)", min_value=0.0, step=0.01, format="%.2f")
        fecha_reposicion = st.date_input("Fecha de ingreso", value=date.today())
        submit_producto = st.form_submit_button("Agregar producto")

        if submit_producto:
            if not nombre.strip():
                st.error("Por favor, ingresá el nombre del producto.")
            elif cantidad <= 0:
                st.error("La cantidad debe ser mayor a 0.")
            else:
                insertar_producto(nombre.strip(), cantidad, precio, fecha_reposicion)
                st.success(f"Producto '{nombre.strip()}' agregado.")
                recargar_app()

# --- MOSTRAR TABLA Y FORMULARIOS DE EDICIÓN/ELIMINACIÓN ---
if productos:
    import pandas as pd

    df_prod = pd.DataFrame(productos, columns=["ID", "Nombre", "Stock", "Precio", "Última Reposición"])
    df_display = df_prod.copy()
    df_display["Precio"] = df_display["Precio"].apply(lambda x: f"${x:,.2f}")
    df_display["Última Reposición"] = df_display["Última Reposición"].fillna("-")

    st.dataframe(df_display[["Nombre", "Stock", "Precio", "Última Reposición"]], height=300)

    with st.expander("Editar o eliminar un producto"):
        opciones = {row['Nombre']: row['ID'] for _, row in df_prod.iterrows()}
        seleccionado = st.selectbox("Seleccioná un producto", [""] + list(opciones.keys()))

        if seleccionado:
            id_sel = opciones[seleccionado]
            producto_sel = df_prod[df_prod["ID"] == id_sel].iloc[0]

            def parse_fecha(fecha_str):
                try:
                    return date.fromisoformat(str(fecha_str))
                except:
                    return date.today()

            with st.form("form_editar_eliminar"):
                nombre_edit = st.text_input("Nombre", value=producto_sel["Nombre"])
                stock_edit = st.number_input("Stock", min_value=0, step=1, value=producto_sel["Stock"])
                precio_edit = st.number_input("Precio unitario ($)", min_value=0.0, step=0.01, value=producto_sel["Precio"], format="%.2f")
                fecha_edit = st.date_input("Última reposición", value=parse_fecha(producto_sel["Última Reposición"]))

                col_ed, col_el = st.columns(2)
                submit_editar = col_ed.form_submit_button("Guardar cambios")
                submit_eliminar = col_el.form_submit_button("Eliminar producto")

                if submit_editar:
                    if not nombre_edit.strip():
                        st.error("El nombre no puede estar vacío.")
                    else:
                        editar_producto(id_sel, nombre_edit.strip(), stock_edit, precio_edit, fecha_edit)
                        st.success(f"Producto '{nombre_edit.strip()}' actualizado.")
                        recargar_app()

                if submit_eliminar:
                    eliminar_producto(id_sel)
                    st.success(f"Producto '{producto_sel['Nombre']}' eliminado.")
                    recargar_app()

else:
    st.info("No hay productos registrados.")
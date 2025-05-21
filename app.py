# python3 -m streamlit run app.py

import streamlit as st
#Import productos
from db import (
    get_productos,
    insertar_producto,
    actualizar_stock,
    create_tables,
    eliminar_producto,
    editar_producto
)
#Import costos
from db import (
    insertar_gasto_fijo,
    get_gastos_fijos,
    editar_gasto_fijo,
    eliminar_gasto_fijo
)

import pandas as pd
import time
from datetime import date


# Cargar y aplicar estilos CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Parada Bajonera</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Dashboard del Negocio</h3>", unsafe_allow_html=True)

#----------------------------------------------------------   ARRANCA SECCION PRODUCTOS   ----------------------------------------------------------
create_tables()

st.write("---")
st.header("STOCK")

# Inicializar en sesión
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

# --- MOSTRAR PRODUCTOS Y BOTONES EDITAR/ELIMINAR ---
if productos:
    import pandas as pd

    df_prod = pd.DataFrame(productos, columns=["ID", "Nombre", "Stock", "Precio", "Última Reposición"])
    df_display = df_prod.copy()
    df_display["Precio"] = df_display["Precio"].apply(lambda x: f"${x:,.2f}")
    df_display["Última Reposición"] = df_display["Última Reposición"].fillna("-")

    st.dataframe(df_display[["Nombre", "Stock", "Precio", "Última Reposición"]], height=300)

    if 'producto_editando' not in st.session_state:
        st.session_state['producto_editando'] = None

    for idx, prod in df_prod.iterrows():
        cols = st.columns([4, 1, 1])
        cols[0].write(f"{prod['Nombre']} (Stock: {prod['Stock']})")
        if cols[1].button("Editar", key=f"editar_prod_{prod['ID']}"):
            st.session_state['producto_editando'] = prod.to_dict()
            recargar_app()
        if cols[2].button("Eliminar", key=f"eliminar_prod_{prod['ID']}"):
            eliminar_producto(prod["ID"])
            st.success(f"Producto '{prod['Nombre']}' eliminado.")
            recargar_app()

    # Formulario edición producto
    if st.session_state['producto_editando']:
        prod = st.session_state['producto_editando']

        def parse_fecha_prod(fecha_str):
            try:
                return date.fromisoformat(fecha_str)
            except:
                return date.today()

        st.write("---")
        st.subheader(f"Editar producto")

        with st.form("form_editar_producto"):
            nombre_edit = st.text_input("Nombre", value=prod['Nombre'])
            stock_edit = st.number_input("Stock", min_value=0, step=1, value=prod['Stock'])
            precio_edit = st.number_input("Precio unitario ($)", min_value=0.0, step=0.01, value=prod['Precio'], format="%.2f")
            fecha_edit = st.date_input("Última reposición", value=parse_fecha_prod(prod['Última Reposición']))

            submit_editar_prod = st.form_submit_button("Guardar cambios")
            if submit_editar_prod:
                if not nombre_edit.strip():
                    st.error("El nombre no puede estar vacío.")
                else:
                    editar_producto(prod['ID'], nombre_edit.strip(), stock_edit, precio_edit, fecha_edit)
                    st.success(f"Producto '{nombre_edit.strip()}' actualizado.")
                    st.session_state['producto_editando'] = None
                    recargar_app()

else:
    st.info("No hay productos registrados.")





#----------------------------------------------------------   ARRANCA SECCION COSTOS   ----------------------------------------------------------
st.write("---")
st.header("COSTOS")



# Total costos abajo del título
gastos = get_gastos_fijos()
total_gastos = sum(g[3] for g in gastos) if gastos else 0
st.metric("Total gastos fijos ($)", f"{total_gastos:,.2f}")

# --- FORMULARIO AGREGAR GASTO FIJO ---
with st.expander("Agregar nuevo gasto fijo"):
    with st.form("form_agregar_gasto"):
        mes = st.text_input("Mes")
        concepto = st.text_input("Concepto")
        monto = st.number_input("Monto ($)", min_value=0.0, step=0.01, format="%.2f")
        fecha_venc = st.date_input("Fecha de vencimiento", value=None)
        fecha_pago = st.date_input("Fecha de pago (opcional)", value=None)
        submit_gasto = st.form_submit_button("Agregar gasto fijo")
        if submit_gasto:
            if not mes.strip() or not concepto.strip() or monto <= 0:
                st.error("Por favor, completá Mes, Concepto y un monto mayor a 0.")
            else:
                fecha_venc_str = fecha_venc.strftime("%Y-%m-%d") if fecha_venc else None
                fecha_pago_str = fecha_pago.strftime("%Y-%m-%d") if fecha_pago else None
                insertar_gasto_fijo(mes.strip(), concepto.strip(), monto, fecha_venc_str, fecha_pago_str)
                st.success(f"Gasto fijo '{concepto.strip()}' agregado.")
                st.rerun()

# --- MOSTRAR GASTOS FIJOS Y BOTONES ---
if gastos:
    df = pd.DataFrame(gastos, columns=["ID", "Mes", "Concepto", "Monto", "Fecha Vencimiento", "Fecha Pago"])
    df_display = df.copy()
    df_display["Monto"] = df_display["Monto"].apply(lambda x: f"${x:,.2f}")
    df_display["Fecha Vencimiento"] = df_display["Fecha Vencimiento"].fillna("-")
    df_display["Fecha Pago"] = df_display["Fecha Pago"].fillna("-")

    st.dataframe(df_display[["Mes", "Concepto", "Monto", "Fecha Vencimiento", "Fecha Pago"]], height=300)

    if 'gasto_editando' not in st.session_state:
        st.session_state['gasto_editando'] = None

    # Mostrar botones para editar y eliminar por cada gasto (fuera del dataframe)
    for idx, gasto in df.iterrows():
        cols = st.columns([4,1,1])
        cols[0].write(f"{gasto['Concepto']} ({gasto['Mes']})")
        if cols[1].button("Editar", key=f"editar_{gasto['ID']}"):
            st.session_state['gasto_editando'] = gasto.to_dict()
        if cols[2].button("Eliminar", key=f"eliminar_{gasto['ID']}"):
            eliminar_gasto_fijo(gasto["ID"])
            st.success(f"Gasto '{gasto['Concepto']}' eliminado.")
            st.rerun()

    # Formulario simple de edición igual al de producto
    if st.session_state['gasto_editando']:
        gasto = st.session_state['gasto_editando']

        def parse_fecha(fecha_str):
            try:
                return date.strptime(fecha_str, "%Y-%m-%d").date()
            except:
                return None

        st.write("---")
        st.subheader(f"Editar gasto fijo")
        with st.form("form_editar_gasto"):
            mes_edit = st.text_input("Mes", value=gasto['Mes'])
            concepto_edit = st.text_input("Concepto", value=gasto['Concepto'])
            monto_edit = st.number_input("Monto ($)", min_value=0.0, step=0.01, value=gasto['Monto'], format="%.2f")
            fecha_venc_edit = st.date_input("Fecha de vencimiento", value=parse_fecha(gasto['Fecha Vencimiento']))
            fecha_pago_edit = st.date_input("Fecha de pago (opcional)", value=parse_fecha(gasto['Fecha Pago']))
            submit_editar = st.form_submit_button("Guardar cambios")
            if submit_editar:
                if not mes_edit.strip() or not concepto_edit.strip() or monto_edit <= 0:
                    st.error("Por favor, completá Mes, Concepto y un monto mayor a 0.")
                else:
                    fecha_venc_edit_str = fecha_venc_edit.strftime("%Y-%m-%d") if fecha_venc_edit else None
                    fecha_pago_edit_str = fecha_pago_edit.strftime("%Y-%m-%d") if fecha_pago_edit else None
                    editar_gasto_fijo(gasto['ID'], mes_edit.strip(), concepto_edit.strip(), monto_edit, fecha_venc_edit_str, fecha_pago_edit_str)
                    st.success(f"Gasto fijo '{concepto_edit.strip()}' actualizado.")
                    st.session_state['gasto_editando'] = None
                    st.rerun()
else:
    st.info("No hay gastos fijos registrados.")

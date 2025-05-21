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

#Import ingresos
from db import (
    get_ingresos,
    editar_ingreso,
    eliminar_ingreso,
    insertar_ingreso_manual
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

    # Estado para formulario activo
    if 'gasto_seleccionado' not in st.session_state:
        st.session_state['gasto_seleccionado'] = None

    with st.expander("Editar o eliminar un gasto fijo"):
        opciones_gastos = {f"{row['Concepto']} ({row['Mes']})": row['ID'] for _, row in df.iterrows()}
        seleccionado = st.selectbox("Seleccioná un gasto fijo", [""] + list(opciones_gastos.keys()))

        if seleccionado:
            st.session_state['gasto_seleccionado'] = opciones_gastos[seleccionado]

    if st.session_state['gasto_seleccionado']:
        gasto_sel = df[df["ID"] == st.session_state['gasto_seleccionado']].iloc[0]

        def parse_fecha(fecha_str):
            try:
                return date.fromisoformat(str(fecha_str))
            except:
                return None

        with st.form("form_editar_eliminar_gasto"):
            mes_edit = st.text_input("Mes", value=gasto_sel["Mes"])
            concepto_edit = st.text_input("Concepto", value=gasto_sel["Concepto"])
            monto_edit = st.number_input("Monto ($)", min_value=0.0, step=0.01, value=gasto_sel["Monto"], format="%.2f")
            fecha_venc_edit = st.date_input("Fecha de vencimiento", value=parse_fecha(gasto_sel["Fecha Vencimiento"]))
            fecha_pago_edit = st.date_input("Fecha de pago (opcional)", value=parse_fecha(gasto_sel["Fecha Pago"]))

            col1, col2 = st.columns(2)
            submit_edit = col1.form_submit_button("Guardar cambios")
            submit_delete = col2.form_submit_button("Eliminar gasto")

            if submit_edit:
                if not mes_edit.strip() or not concepto_edit.strip() or monto_edit <= 0:
                    st.error("Por favor, completá Mes, Concepto y un monto mayor a 0.")
                else:
                    fecha_venc_str = fecha_venc_edit.strftime("%Y-%m-%d") if fecha_venc_edit else None
                    fecha_pago_str = fecha_pago_edit.strftime("%Y-%m-%d") if fecha_pago_edit else None
                    editar_gasto_fijo(gasto_sel["ID"], mes_edit.strip(), concepto_edit.strip(), monto_edit, fecha_venc_str, fecha_pago_str)
                    st.success(f"Gasto fijo '{concepto_edit.strip()}' actualizado.")
                    st.session_state['gasto_seleccionado'] = None
                    st.rerun()

            if submit_delete:
                eliminar_gasto_fijo(gasto_sel["ID"])
                st.success(f"Gasto fijo '{gasto_sel['Concepto']}' eliminado.")
                st.session_state['gasto_seleccionado'] = None
                st.rerun()
else:
    st.info("No hay gastos fijos registrados.")

#----------------------------------------------------------   ARRANCA SECCION INGRESOS   ----------------------------------------------------------

st.write("---")
st.header("INGRESOS")

ingresos = get_ingresos()
total_ingresos = sum(i[2] * i[3] for i in ingresos) if ingresos else 0
st.metric("Total ingresos ($)", f"{total_ingresos:,.2f}")

# --- FORMULARIO AGREGAR INGRESO ---
with st.expander("Agregar nuevo ingreso"):
    with st.form("form_agregar_ingreso"):
        concepto = st.text_input("Concepto (ej: Venta producto X)")
        cantidad = st.number_input("Cantidad", min_value=1, step=1)
        precio_unitario = st.number_input("Precio unitario ($)", min_value=0.01, step=0.01, format="%.2f")
        fecha = st.date_input("Fecha del ingreso", value=date.today())
        submit_ingreso = st.form_submit_button("Agregar ingreso")
        if submit_ingreso:
            if not concepto.strip() or cantidad <= 0 or precio_unitario <= 0:
                st.error("Por favor, completá todos los campos correctamente.")
            else:
                insertar_ingreso_manual(concepto.strip(), cantidad, precio_unitario, fecha.strftime("%Y-%m-%d"))
                st.success(f"Ingreso '{concepto.strip()}' registrado correctamente.")
                st.rerun()

# --- MOSTRAR INGRESOS Y BOTONES ---
if ingresos:
    df_ingresos = pd.DataFrame(ingresos, columns=["ID", "Concepto", "Cantidad", "Precio Unitario", "Fecha"])
    df_ingresos["Total"] = df_ingresos["Cantidad"] * df_ingresos["Precio Unitario"]
    df_display = df_ingresos.copy()
    df_display["Precio Unitario"] = df_display["Precio Unitario"].apply(lambda x: f"${x:,.2f}")
    df_display["Total"] = df_display["Total"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(df_display[["Concepto", "Cantidad", "Precio Unitario", "Fecha", "Total"]], height=300)

    if 'ingreso_seleccionado' not in st.session_state:
        st.session_state['ingreso_seleccionado'] = None

    with st.expander("Editar o eliminar un ingreso"):
        opciones_ingresos = {f"{row['Concepto']} ({row['Fecha']})": row['ID'] for _, row in df_ingresos.iterrows()}
        seleccionado = st.selectbox("Seleccioná un ingreso", [""] + list(opciones_ingresos.keys()))

        if seleccionado:
            st.session_state['ingreso_seleccionado'] = opciones_ingresos[seleccionado]

    if st.session_state['ingreso_seleccionado']:
        ingreso_sel = df_ingresos[df_ingresos["ID"] == st.session_state['ingreso_seleccionado']].iloc[0]

        with st.form("form_editar_eliminar_ingreso"):
            concepto_edit = st.text_input("Concepto", value=ingreso_sel["Concepto"])
            cantidad_edit = st.number_input("Cantidad", min_value=1, step=1, value=ingreso_sel["Cantidad"])
            precio_edit = st.number_input("Precio unitario ($)", min_value=0.01, step=0.01, value=ingreso_sel["Precio Unitario"], format="%.2f")
            fecha_edit = st.date_input("Fecha del ingreso", value=date.fromisoformat(str(ingreso_sel["Fecha"])))

            col1, col2 = st.columns(2)
            submit_edit = col1.form_submit_button("Guardar cambios")
            submit_delete = col2.form_submit_button("Eliminar ingreso")

            if submit_edit:
                if not concepto_edit.strip() or cantidad_edit <= 0 or precio_edit <= 0:
                    st.error("Por favor, completá todos los campos correctamente.")
                else:
                    editar_ingreso(ingreso_sel["ID"], concepto_edit.strip(), cantidad_edit, precio_edit, fecha_edit.strftime("%Y-%m-%d"))
                    st.success("Ingreso actualizado correctamente.")
                    st.session_state['ingreso_seleccionado'] = None
                    st.rerun()

            if submit_delete:
                eliminar_ingreso(ingreso_sel["ID"])
                st.success("Ingreso eliminado correctamente.")
                st.session_state['ingreso_seleccionado'] = None
                st.rerun()
else:
    st.info("No hay ingresos registrados.")
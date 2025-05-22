import streamlit as st
import pandas as pd
from datetime import date

#Import ingresos
from db import (
    get_ingresos,
    editar_ingreso,
    eliminar_ingreso,
    insertar_ingreso_manual
)

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

    with st.expander("Editar o eliminar un ingreso"):
        opciones_ingresos = {f"{row['Concepto']} ({row['Fecha']})": row['ID'] for _, row in df_ingresos.iterrows()}
        seleccionado = st.selectbox("Seleccioná un ingreso", [""] + list(opciones_ingresos.keys()))

        if seleccionado:
            ingreso_id = opciones_ingresos[seleccionado]
            ingreso_sel = df_ingresos[df_ingresos["ID"] == ingreso_id].iloc[0]

            with st.form(f"form_editar_eliminar_ingreso_{ingreso_id}"):
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
                        editar_ingreso(ingreso_id, concepto_edit.strip(), cantidad_edit, precio_edit, fecha_edit.strftime("%Y-%m-%d"))
                        st.success("Ingreso actualizado correctamente.")
                        st.rerun()

                if submit_delete:
                    eliminar_ingreso(ingreso_id)
                    st.success("Ingreso eliminado correctamente.")
                    st.rerun()
else:
    st.info("No hay ingresos registrados.")
import streamlit as st
import pandas as pd
from datetime import date

#Import costos
from db import (
    insertar_gasto_fijo,
    get_gastos_fijos,
    editar_gasto_fijo,
    eliminar_gasto_fijo
)

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
        fecha_venc = st.date_input("Fecha de vencimiento")
        fecha_pago = st.date_input("Fecha de pago (opcional)", value=date.today())
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

    with st.expander("Editar o eliminar un gasto fijo"):
        opciones_gastos = {f"{row['Concepto']} ({row['Mes']})": row['ID'] for _, row in df.iterrows()}
        seleccionado = st.selectbox("Seleccioná un gasto fijo", [""] + list(opciones_gastos.keys()))

        if seleccionado:
            gasto_id = opciones_gastos[seleccionado]
            gasto_sel = df[df["ID"] == gasto_id].iloc[0]

            def parse_fecha(fecha_str):
                try:
                    return date.fromisoformat(str(fecha_str))
                except:
                    return date.today()

            with st.form(f"form_editar_eliminar_{gasto_id}"):
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
                        editar_gasto_fijo(gasto_id, mes_edit.strip(), concepto_edit.strip(), monto_edit, fecha_venc_str, fecha_pago_str)
                        st.success(f"Gasto fijo '{concepto_edit.strip()}' actualizado.")
                        st.rerun()

                if submit_delete:
                    eliminar_gasto_fijo(gasto_id)
                    st.success(f"Gasto fijo '{gasto_sel['Concepto']}' eliminado.")
                    st.rerun()
else:
    st.info("No hay gastos fijos registrados.")
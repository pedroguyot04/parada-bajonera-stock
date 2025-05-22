# python3 -m streamlit run app.py

import streamlit as st

#Import productos
from db_modules.dbStock import (
    get_productos    
)
#Import costos
from db_modules.dbCostos import (
    get_gastos_fijos,
)

#Import ingresos
from db_modules.dbIngresos import (
    get_ingresos,
)

# Cargar y aplicar estilos CSS
with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>Parada Bajonera</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Dashboard del Negocio</h3>", unsafe_allow_html=True)

#----------------------------------------------------------   ARRANCA SECCION METRICAS   ----------------------------------------------------------
st.write("---")
st.header("MÉTRICAS GENERALES")

# Obtener datos actualizados de la base o funciones
productos = get_productos()  # lista de productos
ingresos = get_ingresos()    # lista de ingresos
gastos = get_gastos_fijos()  # lista de gastos

# Actualizar variables según datos reales
total_ingresos = sum(i[2] * i[3] for i in ingresos) if ingresos else 0
total_gastos = sum(g[3] for g in gastos) if gastos else 0
costo_total = sum(p[2] * p[3] for p in productos if p[2] and p[3]) if productos else 0
total_unidades = sum(p[2] for p in productos if p[2]) if productos else 0

ganancia_neta = total_ingresos - total_gastos
margen_neto = (ganancia_neta / total_ingresos * 100) if total_ingresos else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total ingresos ($)", f"{total_ingresos:,.2f}")
col2.metric("Total gastos fijos ($)", f"{total_gastos:,.2f}")
col3.metric("Ganancia neta ($)", f"{ganancia_neta:,.2f}", delta=f"{margen_neto:.2f}%")

col4, col5 = st.columns(2)
col4.metric("Costo total en stock ($)", f"{costo_total:,.2f}")
col5.metric("Total unidades en stock", f"{total_unidades:,}")

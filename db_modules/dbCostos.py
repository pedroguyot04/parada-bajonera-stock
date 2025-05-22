from db import get_connection

#----------------------------------------------------------   ARRANCA SECCION COSTOS   ----------------------------------------------------------

def insertar_gasto_fijo(mes, concepto, monto, fecha_vencimiento=None, fecha_pago=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO gastos_fijos (mes, concepto, monto, fecha_vencimiento, fecha_pago)
        VALUES (?, ?, ?, ?, ?)
    """, (mes, concepto, monto, fecha_vencimiento, fecha_pago))
    conn.commit()
    conn.close()

def get_gastos_fijos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM gastos_fijos ORDER BY id")
    gastos = cursor.fetchall()
    conn.close()
    return gastos

def editar_gasto_fijo(gasto_id, mes, concepto, monto, fecha_vencimiento=None, fecha_pago=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE gastos_fijos
        SET mes = ?, concepto = ?, monto = ?, fecha_vencimiento = ?, fecha_pago = ?
        WHERE id = ?
    """, (mes, concepto, monto, fecha_vencimiento, fecha_pago, gasto_id))
    conn.commit()
    conn.close()

def eliminar_gasto_fijo(gasto_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM gastos_fijos WHERE id = ?", (gasto_id,))
    conn.commit()
    conn.close()

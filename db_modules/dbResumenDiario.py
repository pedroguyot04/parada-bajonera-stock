from db import get_connection

def insertar_venta(fecha, turno, producto_id, cantidad, forma_pago, monto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resumen_diario (fecha, turno, producto_id, cantidad, forma_pago, monto)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (fecha, turno, producto_id, cantidad, forma_pago, monto))
    conn.commit()
    conn.close()

def get_ventas_por_dia_turno(fecha, turno):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, producto_id, cantidad, forma_pago, monto
        FROM resumen_diario
        WHERE fecha = ? AND turno = ?
    """, (fecha, turno))
    resultados = cursor.fetchall()
    conn.close()
    return resultados

def get_resumen_diario(fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            SUM(cantidad) AS total_cantidad,
            SUM(monto) AS total_monto,
            SUM(CASE WHEN forma_pago = 'efectivo' THEN monto ELSE 0 END) AS total_efectivo,
            SUM(CASE WHEN forma_pago = 'mercado_pago' THEN monto ELSE 0 END) AS total_mercado_pago,
            SUM(CASE WHEN forma_pago = 'digital' THEN monto ELSE 0 END) AS total_digital
        FROM resumen_diario
        WHERE fecha = ?
    """, (fecha,))
    resumen = cursor.fetchone()
    conn.close()
    return resumen

def editar_venta(venta_id, producto_id, cantidad, forma_pago, monto):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE resumen_diario
        SET producto_id = ?, cantidad = ?, forma_pago = ?, monto = ?
        WHERE id = ?
    """, (producto_id, cantidad, forma_pago, monto, venta_id))
    conn.commit()
    conn.close()

def eliminar_venta(venta_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM resumen_diario WHERE id = ?", (venta_id,))
    conn.commit()
    conn.close()

def deshacer_ultimo_movimiento():
    conn = get_connection()
    cursor = conn.cursor()
    # Obtener el último id insertado
    cursor.execute("SELECT id FROM resumen_diario ORDER BY id DESC LIMIT 1")
    ultimo = cursor.fetchone()
    if ultimo:
        cursor.execute("DELETE FROM resumen_diario WHERE id = ?", (ultimo[0],))
        conn.commit()
    conn.close()

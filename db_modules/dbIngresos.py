from db import get_connection

#----------------------------------------------------------   ARRANCA SECCION INGRESOS   ----------------------------------------------------------
def insertar_ingreso_manual(concepto, cantidad, precio_unitario, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ingresos (concepto, cantidad, precio_unitario, fecha)
        VALUES (?, ?, ?, ?)
    """, (concepto, cantidad, precio_unitario, fecha))
    conn.commit()
    conn.close()

def get_ingresos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ingresos ORDER BY fecha DESC")
    ingresos = cursor.fetchall()
    conn.close()
    return ingresos

def editar_ingreso(ingreso_id, concepto, cantidad, precio_unitario, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE ingresos
        SET concepto = ?, cantidad = ?, precio_unitario = ?, fecha = ?
        WHERE id = ?
    """, (concepto, cantidad, precio_unitario, fecha, ingreso_id))
    conn.commit()
    conn.close()

def eliminar_ingreso(ingreso_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM ingresos WHERE id = ?", (ingreso_id,))
    conn.commit()
    conn.close()
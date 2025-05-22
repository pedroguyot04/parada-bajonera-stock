from db import get_connection

#----------------------------------------------------------   ARRANCA SECCION PRODUCTOS   ----------------------------------------------------------

# Insertar producto
def insertar_producto(nombre, stock, precio, ultima_reposicion):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO productos (nombre, stock, precio, ultima_reposicion) VALUES (?, ?, ?, ?)",
        (nombre, stock, precio, ultima_reposicion)
    )
    conn.commit()
    conn.close()

# Obtener productos
def get_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

# Actualizar stock sumando (cantidad puede ser negativa)
def actualizar_stock(producto_id, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE productos SET stock = stock + ? WHERE id = ?", (cantidad, producto_id))
    conn.commit()
    conn.close()

# Eliminar producto completo
def eliminar_producto(producto_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = ?", (producto_id,))
    conn.commit()
    conn.close()

# Insertar movimiento (entrada o salida)
def insertar_movimiento(producto_id, tipo, cantidad, fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO movimientos (producto_id, tipo, cantidad, fecha)
        VALUES (?, ?, ?, ?)
    """, (producto_id, tipo, cantidad, fecha))
    conn.commit()
    conn.close()

# Obtener todos los movimientos
def get_movimientos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movimientos")
    movs = cursor.fetchall()
    conn.close()
    return movs

# Editar un producto
def editar_producto(producto_id, nuevo_nombre, nuevo_stock, nuevo_precio, nueva_fecha):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE productos
        SET nombre = ?, stock = ?, precio = ?, ultima_reposicion = ?
        WHERE id = ?
    """, (nuevo_nombre, nuevo_stock, nuevo_precio, nueva_fecha, producto_id))
    conn.commit()
    conn.close()
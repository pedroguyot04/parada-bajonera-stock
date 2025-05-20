import sqlite3

# Conexión a la base de datos
def get_connection():
    return sqlite3.connect("stock.db")

# Crear tablas si no existen
def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            stock INTEGER NOT NULL,
            precio REAL,
            ultima_reposicion DATE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            tipo TEXT CHECK(tipo IN ('entrada', 'salida')) NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha DATE NOT NULL,
            FOREIGN KEY(producto_id) REFERENCES productos(id)
        )
    """)
    conn.commit()
    conn.close()

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

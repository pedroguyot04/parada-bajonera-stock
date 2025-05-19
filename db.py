import sqlite3

# Conexión a la base de datos
def get_connection():
    return sqlite3.connect("stock.db")

# Crear la tabla si no existe
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

def actualizar_stock(producto_id, cantidad):
    conn = get_connection()
    cursor = conn.cursor()
    # actualizar stock sumando (cantidad puede ser negativa)
    cursor.execute("UPDATE productos SET stock = stock + ? WHERE id = ?", (cantidad, producto_id))
    conn.commit()
    conn.close()

import sqlite3

# Conexión a la base de datos
def get_connection():
    return sqlite3.connect("stock.db")

# Crear la tabla si no existe
def create_tables():
    conn = get_connection()         #Abre la conexion a la base de datos stock.db
    cursor = conn.cursor()          #Crea un cursor, que es como un 'puntero' que se usa para ejecutar comandos SQL
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            stock INTEGER NOT NULL,
            precio REAL
        )
    """)
    conn.commit()           #Guarda los cambios en la base de datos
    conn.close()            #Cierra la conexión a la base de datos

# Insertar producto inicial (ejemplo)
def insertar_producto(nombre, stock, precio):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO productos (nombre, stock, precio) VALUES (?, ?, ?)", (nombre, stock, precio))
    conn.commit()
    conn.close()

# Ver productos
def get_productos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos")
    productos = cursor.fetchall()
    conn.close()
    return productos

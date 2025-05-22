import sqlite3
from datetime import date

# Nombre de la base de datos
DB_NAME = "stock.db"

# Conexión a la base de datos
def get_connection():
    return sqlite3.connect(DB_NAME)

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
        CREATE TABLE IF NOT EXISTS gastos_fijos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mes TEXT NOT NULL,
            concepto TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha_vencimiento TEXT,
            fecha_pago TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingresos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            concepto TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            fecha DATE NOT NULL
        );
    """)
    
    conn.commit()
    conn.close()
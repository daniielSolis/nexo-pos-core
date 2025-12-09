import sqlite3
import os

# --- CONFIGURACIÓN DE RUTA 
CARPETA_DATA = os.path.dirname(os.path.abspath(__file__))
CARPETA_RAIZ = os.path.dirname(CARPETA_DATA)
RUTA_DB = os.path.join(CARPETA_RAIZ, "nexo.db")

def crear_conexion():
    try:
        conn = sqlite3.connect(RUTA_DB)
        return conn
    except Exception as e:
        print(f"❌ Error BD: {e}")
        return None

def inicializar_tablas():
    conn = crear_conexion()
    if conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                nombre TEXT,
                rol TEXT DEFAULT 'cajero'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                stock INTEGER DEFAULT 0
            )
        """)
        
        # Admin por defecto
        cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios (usuario, password, nombre, rol) VALUES (?, ?, ?, ?)",
                           ("admin", "1234", "Administrador Principal", "admin"))
            
        conn.commit()
        conn.close()

# --- FUNCIONES PARA EL INVENTARIO 

def registrar_producto(codigo, nombre, precio, stock):
    """Guarda un producto nuevo en la base de datos"""
    conn = crear_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
                           (codigo, nombre, precio, stock))
            conn.commit()
            conn.close()
            return True # ¡Se guardó bien!
        except sqlite3.IntegrityError:
            return False # Error: El código ya existe
        except Exception as e:
            print(f"Error: {e}")
            return False

def obtener_productos():
    """Devuelve la lista completa de productos"""
    conn = crear_conexion()
    lista = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre, precio, stock FROM productos")
        lista = cursor.fetchall()
        conn.close()
    return lista

if __name__ == "__main__":
    inicializar_tablas()
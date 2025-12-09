import sqlite3
import os
import datetime

# --- CONFIGURACIÓN DE RUTA ---
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total REAL NOT NULL,
                usuario_nombre TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_venta INTEGER,
                producto_nombre TEXT,
                cantidad INTEGER,
                precio_unitario REAL,
                subtotal REAL,
                FOREIGN KEY(id_venta) REFERENCES ventas(id)
            )
        """)
        
        cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios (usuario, password, nombre, rol) VALUES (?, ?, ?, ?)",
                           ("admin", "1234", "Administrador Principal", "admin"))
            
        conn.commit()
        conn.close()

# --- FUNCIONES DEL SISTEMA ---

def registrar_producto(codigo, nombre, precio, stock):
    conn = crear_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)",
                           (codigo, nombre, precio, stock))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
        except Exception as e:
            return False

def obtener_productos():
    conn = crear_conexion()
    lista = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre, precio, stock FROM productos")
        lista = cursor.fetchall()
        conn.close()
    return lista

# --- MEJORA AQUÍ: BÚSQUEDA HÍBRIDA ---
def buscar_producto(criterio):
    """Busca por código exacto O por nombre parecido"""
    conn = crear_conexion()
    producto = None
    if conn:
        cursor = conn.cursor()
        
        # 1. Intentamos buscar por CÓDIGO exacto
        cursor.execute("SELECT codigo, nombre, precio, stock FROM productos WHERE codigo = ?", (criterio,))
        producto = cursor.fetchone()
        
        # 2. Si no existe ese código, buscamos por NOMBRE (que contenga el texto)
        if not producto:
            cursor.execute("SELECT codigo, nombre, precio, stock FROM productos WHERE nombre LIKE ?", (f"%{criterio}%",))
            producto = cursor.fetchone() # Trae el primer resultado que coincida
            
        conn.close()
    return producto

def realizar_venta(lista_carrito, total, usuario_nombre):
    conn = crear_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ventas (total, usuario_nombre) VALUES (?, ?)", (total, usuario_nombre))
            id_venta = cursor.lastrowid
            
            for item in lista_carrito:
                subtotal = item['precio'] * item['cantidad']
                cursor.execute("""
                    INSERT INTO detalle_ventas (id_venta, producto_nombre, cantidad, precio_unitario, subtotal)
                    VALUES (?, ?, ?, ?, ?)
                """, (id_venta, item['nombre'], item['cantidad'], item['precio'], subtotal))

                cursor.execute("UPDATE productos SET stock = stock - ? WHERE codigo = ?", 
                               (item['cantidad'], item['codigo']))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error en venta: {e}")
            conn.rollback()
            return False

if __name__ == "__main__":
    inicializar_tablas()
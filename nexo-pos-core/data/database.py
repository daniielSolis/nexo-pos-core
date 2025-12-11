import sqlite3
import os

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

# --- FUNCIONES DE SEGURIDAD ---
def validar_admin(password_intento):
    conn = crear_conexion()
    es_valido = False
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario='admin' AND password=?", (password_intento,))
        if cursor.fetchone():
            es_valido = True
        conn.close()
    return es_valido

# --- FUNCIONES DE PRODUCTOS ---
def registrar_producto(codigo, nombre, precio, stock):
    conn = crear_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO productos (codigo, nombre, precio, stock) VALUES (?, ?, ?, ?)", (codigo, nombre, precio, stock))
            conn.commit(); conn.close()
            return True
        except: return False

def obtener_productos():
    conn = crear_conexion()
    lista = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre, precio, stock FROM productos")
        lista = cursor.fetchall(); conn.close()
    return lista

def buscar_producto(criterio):
    conn = crear_conexion()
    producto = None
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nombre, precio, stock FROM productos WHERE codigo = ?", (criterio,))
        producto = cursor.fetchone()
        if not producto:
            cursor.execute("SELECT codigo, nombre, precio, stock FROM productos WHERE nombre LIKE ?", (f"%{criterio}%",))
            producto = cursor.fetchone()
        conn.close()
    return producto

# --- FUNCIONES DE GESTIÓN (CRUD) ---

def sumar_stock(codigo, cantidad_extra):
    conn = crear_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE productos SET stock = MAX(0, stock) + ? WHERE codigo = ?", (cantidad_extra, codigo))
            conn.commit(); conn.close()
            return True
        except: return False

def editar_producto(codigo, nuevo_nombre, nuevo_precio):
    """Actualiza nombre y precio de un producto existente"""
    conn = crear_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE productos SET nombre = ?, precio = ? WHERE codigo = ?", (nuevo_nombre, nuevo_precio, codigo))
            conn.commit(); conn.close()
            return True
        except: return False

def eliminar_producto(codigo):
    conn = crear_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
            conn.commit(); conn.close()
            return True
        except: return False

# --- FUNCIONES DE VENTAS ---
def realizar_venta(lista_carrito, total, usuario_nombre):
    conn = crear_conexion()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ventas (total, usuario_nombre) VALUES (?, ?)", (total, usuario_nombre))
            id_venta = cursor.lastrowid
            
            for item in lista_carrito:
                subtotal = item['precio'] * item['cantidad']
                cursor.execute("INSERT INTO detalle_ventas (id_venta, producto_nombre, cantidad, precio_unitario, subtotal) VALUES (?, ?, ?, ?, ?)", 
                               (id_venta, item['nombre'], item['cantidad'], item['precio'], subtotal))
                cursor.execute("UPDATE productos SET stock = stock - ? WHERE codigo = ?", (item['cantidad'], item['codigo']))

            conn.commit(); conn.close()
            return True
        except: conn.rollback(); return False

# --- FUNCIONES PARA REPORTES ---
def obtener_ventas():
    conn = crear_conexion()
    lista = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, datetime(fecha, 'localtime'), total, usuario_nombre FROM ventas ORDER BY id DESC")
        lista = cursor.fetchall(); conn.close()
    return lista

def obtener_detalle_venta(id_venta):
    conn = crear_conexion()
    lista = []
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT producto_nombre, cantidad, precio_unitario, subtotal FROM detalle_ventas WHERE id_venta = ?", (id_venta,))
        lista = cursor.fetchall(); conn.close()
    return lista

if __name__ == "__main__":
    inicializar_tablas()
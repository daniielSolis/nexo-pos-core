"""
Módulo de Base de Datos - NEXO POS
Capa de Persistencia - Solo operaciones SQL
"""
import sqlite3
from datetime import datetime

DB_NAME = "nexo.db"

def crear_conexion():
    """Crea y retorna una conexión a la base de datos"""
    try:
        conexion = sqlite3.connect(DB_NAME)
        return conexion
    except Exception as e:
        print(f"Error al conectar con la base de datos: {e}")
        return None

def inicializar_base_datos():
    """
    Crea las tablas si no existen y ejecuta migraciones
    SE EJECUTA AL INICIO DEL SISTEMA
    """
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        
        # Tabla usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                nombre_completo TEXT NOT NULL,
                rol TEXT DEFAULT 'vendedor'
            )
        """)
        
        # Tabla productos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                codigo TEXT PRIMARY KEY,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                stock_minimo INTEGER DEFAULT 5
            )
        """)
        
        # Tabla ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                total REAL NOT NULL,
                vendedor TEXT NOT NULL
            )
        """)
        
        # Tabla detalle_venta
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_venta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                venta_id INTEGER NOT NULL,
                producto_codigo TEXT NOT NULL,
                producto_nombre TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                precio_unitario REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (venta_id) REFERENCES ventas(id)
            )
        """)
        
        # Insertar usuario admin por defecto
        cursor.execute("SELECT COUNT(*) FROM usuarios WHERE usuario = 'admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO usuarios (usuario, password, nombre_completo, rol)
                VALUES ('admin', 'admin123', 'Administrador', 'admin')
            """)
        
        conexion.commit()
        
        # Ejecutar migraciones
        migrar_db()
        
        return True
    except Exception as e:
        print(f"Error al inicializar base de datos: {e}")
        return False
    finally:
        conexion.close()

def migrar_db():
    """
    🔧 MIGRACIÓN: Agrega columna stock_minimo si no existe
    Verifica la estructura de la tabla productos y actualiza si es necesario
    """
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        
        # Verificar si la columna stock_minimo existe
        cursor.execute("PRAGMA table_info(productos)")
        columnas = [columna[1] for columna in cursor.fetchall()]
        
        if 'stock_minimo' not in columnas:
            print("⚙️ [MIGRACIÓN] Agregando columna 'stock_minimo' a tabla productos...")
            cursor.execute("ALTER TABLE productos ADD COLUMN stock_minimo INTEGER DEFAULT 5")
            conexion.commit()
            print("✅ [MIGRACIÓN] Columna 'stock_minimo' agregada exitosamente")
        
        return True
    except Exception as e:
        print(f"❌ [MIGRACIÓN] Error: {e}")
        return False
    finally:
        conexion.close()

# ==========================================
# FUNCIONES DE PRODUCTOS
# ==========================================

def registrar_producto(codigo, nombre, precio, stock, stock_minimo=5):
    """
    Registra un nuevo producto en la base de datos
    
    Args:
        codigo (str): Código único del producto
        nombre (str): Nombre del producto
        precio (float): Precio unitario
        stock (int): Stock inicial
        stock_minimo (int): Stock mínimo para alertas (default: 5)
    
    Returns:
        bool: True si se registró correctamente, False si código ya existe
    """
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            INSERT INTO productos (codigo, nombre, precio, stock, stock_minimo)
            VALUES (?, ?, ?, ?, ?)
        """, (codigo, nombre, precio, stock, stock_minimo))
        conexion.commit()
        return True
    except sqlite3.IntegrityError:
        # Código duplicado
        return False
    except Exception as e:
        print(f"Error al registrar producto: {e}")
        return False
    finally:
        conexion.close()

def obtener_productos():
    """
    Obtiene todos los productos de la base de datos
    
    Returns:
        list: Lista de tuplas (codigo, nombre, precio, stock, stock_minimo)
    """
    conexion = crear_conexion()
    if not conexion:
        return []
    
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT codigo, nombre, precio, stock, stock_minimo 
            FROM productos 
            ORDER BY nombre
        """)
        productos = cursor.fetchall()
        return productos
    except Exception as e:
        print(f"Error al obtener productos: {e}")
        return []
    finally:
        conexion.close()

def buscar_producto(busqueda):
    """
    Busca un producto por código o nombre
    
    Args:
        busqueda (str): Código o nombre del producto
    
    Returns:
        tuple: (codigo, nombre, precio, stock, stock_minimo) o None
    """
    conexion = crear_conexion()
    if not conexion:
        return None
    
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT codigo, nombre, precio, stock, stock_minimo 
            FROM productos 
            WHERE codigo = ? OR nombre LIKE ?
        """, (busqueda, f"%{busqueda}%"))
        producto = cursor.fetchone()
        return producto
    except Exception as e:
        print(f"Error al buscar producto: {e}")
        return None
    finally:
        conexion.close()

def editar_producto(codigo, nombre, precio, stock_minimo=None):
    """
    Edita un producto existente
    
    Args:
        codigo (str): Código del producto a editar
        nombre (str): Nuevo nombre
        precio (float): Nuevo precio
        stock_minimo (int, optional): Nuevo stock mínimo
    
    Returns:
        bool: True si se editó correctamente
    """
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        
        if stock_minimo is not None:
            cursor.execute("""
                UPDATE productos 
                SET nombre = ?, precio = ?, stock_minimo = ?
                WHERE codigo = ?
            """, (nombre, precio, stock_minimo, codigo))
        else:
            cursor.execute("""
                UPDATE productos 
                SET nombre = ?, precio = ?
                WHERE codigo = ?
            """, (nombre, precio, codigo))
        
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al editar producto: {e}")
        return False
    finally:
        conexion.close()

def sumar_stock(codigo, cantidad):
    """
    Suma stock a un producto existente
    
    Args:
        codigo (str): Código del producto
        cantidad (int): Cantidad a sumar
    
    Returns:
        bool: True si se actualizó correctamente
    """
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE productos 
            SET stock = stock + ?
            WHERE codigo = ?
        """, (cantidad, codigo))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al sumar stock: {e}")
        return False
    finally:
        conexion.close()

def eliminar_producto(codigo):
    """
    Elimina un producto de la base de datos
    
    Args:
        codigo (str): Código del producto a eliminar
    
    Returns:
        bool: True si se eliminó correctamente
    """
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM productos WHERE codigo = ?", (codigo,))
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        return False
    finally:
        conexion.close()

def obtener_productos_bajo_stock():
    """
    🚨 NUEVA FUNCIÓN: Obtiene productos con stock por debajo del mínimo
    
    Returns:
        list: Lista de tuplas (codigo, nombre, precio, stock, stock_minimo, faltante)
              Ordenados por criticidad (faltante DESC)
    """
    conexion = crear_conexion()
    if not conexion:
        return []
    
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT 
                codigo, 
                nombre, 
                precio, 
                stock, 
                stock_minimo,
                (stock_minimo - stock) as faltante
            FROM productos 
            WHERE stock <= stock_minimo
            ORDER BY faltante DESC, stock ASC
        """)
        productos = cursor.fetchall()
        return productos
    except Exception as e:
        print(f"Error al obtener productos bajo stock: {e}")
        return []
    finally:
        conexion.close()

# ==========================================
# FUNCIONES DE VENTAS
# ==========================================

def realizar_venta(carrito, total, vendedor):
    """
    Registra una venta y descuenta el stock
    
    Args:
        carrito (list): Lista de diccionarios con productos vendidos
        total (float): Total de la venta
        vendedor (str): Nombre del vendedor
    
    Returns:
        bool: True si se registró correctamente
    """
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insertar venta
        cursor.execute("""
            INSERT INTO ventas (fecha, total, vendedor)
            VALUES (?, ?, ?)
        """, (fecha_actual, total, vendedor))
        
        venta_id = cursor.lastrowid
        
        # Insertar detalle y descontar stock
        for item in carrito:
            cursor.execute("""
                INSERT INTO detalle_venta 
                (venta_id, producto_codigo, producto_nombre, cantidad, precio_unitario, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (venta_id, item['codigo'], item['nombre'], item['cantidad'], 
                  item['precio'], item['precio'] * item['cantidad']))
            
            cursor.execute("""
                UPDATE productos 
                SET stock = stock - ?
                WHERE codigo = ?
            """, (item['cantidad'], item['codigo']))
        
        conexion.commit()
        return True
    except Exception as e:
        print(f"Error al realizar venta: {e}")
        conexion.rollback()
        return False
    finally:
        conexion.close()

def obtener_ventas():
    """
    Obtiene todas las ventas registradas
    
    Returns:
        list: Lista de tuplas (id, fecha, total)
    """
    conexion = crear_conexion()
    if not conexion:
        return []
    
    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT id, fecha, total FROM ventas ORDER BY id DESC")
        ventas = cursor.fetchall()
        return ventas
    except Exception as e:
        print(f"Error al obtener ventas: {e}")
        return []
    finally:
        conexion.close()

def obtener_detalle_venta(venta_id):
    """
    Obtiene el detalle de una venta específica
    
    Args:
        venta_id (int): ID de la venta
    
    Returns:
        list: Lista de tuplas (producto_nombre, cantidad, precio_unitario, subtotal)
    """
    conexion = crear_conexion()
    if not conexion:
        return []
    
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT producto_nombre, cantidad, precio_unitario, subtotal
            FROM detalle_venta
            WHERE venta_id = ?
        """, (venta_id,))
        detalle = cursor.fetchall()
        return detalle
    except Exception as e:
        print(f"Error al obtener detalle de venta: {e}")
        return []
    finally:
        conexion.close()

# ==========================================
# FUNCIONES DE AUTENTICACIÓN
# ==========================================

def validar_admin(password):
    """
    Valida si una contraseña es de administrador
    
    Args:
        password (str): Contraseña a validar
    
    Returns:
        bool: True si la contraseña es correcta
    """
    conexion = crear_conexion()
    if not conexion:
        return False
    
    try:
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM usuarios 
            WHERE password = ? AND rol = 'admin'
        """, (password,))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        print(f"Error al validar admin: {e}")
        return False
    finally:
        conexion.close()

# ==========================================
# INICIALIZACIÓN AUTOMÁTICA
# ==========================================
inicializar_base_datos()
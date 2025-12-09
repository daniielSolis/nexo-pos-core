import sqlite3
import os
#configuracion de ruta 
#identifica donde esta el archivo (dentro de la carpeta data)
CARPETA_ACTUAL = os.path.dirname(os.path.abspath(__file__))
#subimos un nivel para llegar a la carpeta principal del proyecto
CARPETA_PROYECTO = os.path.dirname(CARPETA_ACTUAL) 
#guardamos la base de datos en la carpeta principal, no en data
RUTA_DB = os.path.join(CARPETA_PROYECTO, "nexo.db")

def crear_conexion():
    """Conecta con la memoria del sistema (SQLite)"""
    try:
        conn = sqlite3.connect(RUTA_DB)
        return conn
    except Exception as e:
        print(f"❌ Error crítico en base de datos: {e}")
        return None

def inicializar_tablas():
    """Construye las tablas si es la primera vez que se usa"""
    print(f"🔄 Conectando a base de datos en: {RUTA_DB}")
    
    conn = crear_conexion()
    if conn:
        cursor = conn.cursor()

        # 1. TABLA DE USUARIOS (Para iniciar sesión)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                nombre TEXT,
                rol TEXT DEFAULT 'cajero'
            )
        """)

        # 2. TABLA DE PRODUCTOS (Tu inventario)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE NOT NULL,
                nombre TEXT NOT NULL,
                precio REAL NOT NULL,
                stock INTEGER DEFAULT 0
            )
        """)

        # 3. CREAR EL PRIMER JEFE (ADMIN)
        cursor.execute("SELECT * FROM usuarios WHERE usuario='admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO usuarios (usuario, password, nombre, rol) VALUES (?, ?, ?, ?)",
                           ("admin", "1234", "Administrador Principal", "admin"))
            print("👤 Usuario 'admin' creado por defecto (Clave: 1234)")

        conn.commit()
        conn.close()
        print("✅ ¡Base de datos inicializada y lista para trabajar!")

# Este bloque permite probar el archivo directamente
if __name__ == "__main__":
    inicializar_tablas()
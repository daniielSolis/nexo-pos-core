# 🛒 NEXO POS - Sistema de Punto de Venta

**NEXO POS** solución de escritorio diseñada para la gestión de ventas e inventarios en pequeños y medianos negocios. Desarrollado en **Python** utilizando el framework **Flet** para una interfaz moderna y reactiva.

##  Características Principales

### 1.  Seguridad y Acceso
* Sistema de Login integrado con validación de credenciales en Base de Datos.
* Protección de funciones administrativas (Inventario) mediante contraseña secundaria.

### 2.  Gestión de Inventario
* **CRUD Completo:** Crear, Leer, Actualizar y Eliminar productos.
* **Validación Anti-Fantasmas:** Impide la creación de productos con campos vacíos.
* **Control de Stock:** Visualización en tiempo real de existencias.

### 3.  Punto de Venta (POS)
* **Búsqueda Inteligente:** Filtrado por nombre o código de barras.
* **Catálogo Visual:** Ventana emergente con listado rápido para agregar productos con un clic.
* **Carrito Interactivo:** Ajuste de cantidades y eliminación de ítems antes de cobrar.
* **Validación de Stock:** El sistema impide vender más unidades de las disponibles (validación silenciosa sin interrupciones).

### 4.  Facturación y Reportes
* **Tickets Automáticos:** Generación de archivos `.txt` con formato de ticket de venta (Fecha, desglose, total, vendedor).
* **Historial de Ventas:** Visualización de todas las transacciones realizadas.
* **Detalle de Venta:** Botón "Ojo" para inspeccionar qué productos se vendieron en cada ticket.
* **Exportación a Excel:** Descarga de reporte financiero en formato `.csv` compatible con Excel.

---

##  Tecnologías Utilizadas

* **Lenguaje:** Python 3.x
* **GUI Framework:** Flet (Flutter para Python)
* **Base de Datos:** SQLite3 (Local, archivo `nexo.db`)
* **Reportes:** CSV nativo

---

##  Instalación y Uso

Sigue estos pasos para ejecutar el proyecto en tu máquina local:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/TU_USUARIO/nexo-pos-core.git](https://github.com/TU_USUARIO/nexo-pos-core.git)
    cd nexo-pos-core
    ```

2.  **Instalar dependencias:**
    Solo necesitas instalar Flet.
    ```bash
    pip install flet
    ```

3.  **Ejecutar la aplicación:**
    ```bash
    python main.py
    ```

---

## Estructura del Proyecto

* `main.py`: Núcleo de la aplicación (Interfaz y Lógica).
* `data/database.py`: Módulo de conexión y consultas SQL.
* `nexo.db`: Base de datos SQLite (se genera automáticamente si no existe).
* `tickets/`: Carpeta donde se guardan los recibos generados.
* `reportes/`: Carpeta para las exportaciones de Excel.

---
# 📘 Documentación Técnica - NEXO POS

Este documento detalla la estructura, lógica y funcionamiento del sistema **NEXO POS**. 
---

##  Arquitectura General

El sistema está construido en **Python** utilizando **Flet** (un wrapper de Flutter) para la interfaz gráfica y **SQLite** para la persistencia de datos.

### Estructura de Archivos
* `main.py`: Controlador principal. Maneja la UI, la navegación y la lógica de negocio del frontend.
* `data/database.py`: Capa de persistencia. Contiene todas las sentencias SQL y la conexión a la BD.
* `tickets/`: Directorio de salida para los comprobantes de venta (.txt).
* `reportes/`: Directorio de salida para exportaciones financieras (.csv).

---

##  Lógica del Núcleo (`main.py`)

El archivo `main.py` contiene la función `main(page: ft.Page)`, que actúa como el punto de entrada de la aplicación. A continuación se desglosan sus bloques principales:

### 1.  Generador de Tickets (`generar_ticket`)
* **Función:** Crea un archivo de texto plano (`.txt`) con el resumen de la venta.
* **Lógica:**
    1.  Verifica/Crea la carpeta `tickets`.
    2.  Genera un nombre único usando `datetime.now()` para evitar sobreescrituras.
    3.  Escribe el contenido con formato de alineación manual para impresoras térmicas.
    4.  **Impresión:** Utiliza `os.startfile()` para abrir el ticket con el visor predeterminado del sistema (Windows), simulando el envío a impresora.

### 2.  Módulo de Ventas (`mostrar_ventas`)
Este es el corazón transaccional del sistema.
* **Gestión de Estado:** Usa una lista global `carrito_compras` (en memoria RAM) para almacenar los productos antes de confirmar la venta.
* **Búsqueda (`procesar_producto`):**
    * Consulta la BD por código de barras o nombre.
    * **Validación de Stock (Silenciosa):** Si `stock <= 0`, la función retorna inmediatamente sin agregar el producto y sin mostrar alertas invasivas (UX mejorada).
    * **Control de Duplicados:** Si el producto ya existe en el carrito, suma +1 a la cantidad, respetando siempre el límite de stock real.
* **Catálogo Rápido (`abrir_catalogo`):**
    * Muestra un `DataTable` dentro de un `AlertDialog`.
    * **Data Binding:** Los botones de agregar usan la propiedad `data=p[0]` para pasar el ID del producto al evento `on_click` sin errores de referencia en el bucle.
* **Finalización (`finalizar_venta`):** Realiza el cálculo total, invoca a `realizar_venta` (BD) y `generar_ticket`, y limpia el carrito.

### 3.  Módulo de Inventario (`mostrar_inventario`)
Gestión CRUD (Create, Read, Update, Delete) de productos.
* **Renderizado de Tabla (`cargar`):**
    * Itera sobre los productos de la BD.
    * **IMPORTANTE:** Convierte todos los valores numéricos a `str()` antes de pasarlos a `ft.Text()`. *Esto previene el error crítico "int object is not iterable" de Flet.*
* **Botones de Acción:**
    * Se utiliza **Data Binding** (`btn.data = id_producto`). Al hacer clic, leemos `e.control.data` para saber qué producto editar o borrar. Esto soluciona el problema de "botones muertos" o que todos apunten al último ítem.
* **Validación Anti-Fantasmas (`crear`):**
    * Antes de guardar, verifica `if not txt.value.strip():`. Si los campos están vacíos, muestra un `SnackBar` rojo y detiene la ejecución. Esto impide ensuciar la base de datos con registros nulos.

### 4.  Módulo de Reportes (`mostrar_reportes`)
Visualización de historial financiero.
* **Tabla Histórica:** Muestra ID, Fecha y Total.
* **Drill-Down (`ver_detalle`):** Al hacer clic en el "ojo", consulta la tabla `detalle_ventas` y muestra los productos específicos de esa transacción en un diálogo modal.
* **Exportación Excel (`exportar_excel`):** Utiliza la librería estándar `csv` con codificación `utf-8-sig` (para compatibilidad con Excel) para volcar la base de datos a un archivo.

### 5. 🖥️ Navegación y Login
* **Dashboard:** Menú principal con botones grandes (`Container` con evento `on_click`).
* **Login:** Validación simple contra la tabla `usuarios` en SQLite.

---

##  Decisiones Técnicas Clave 

**P: ¿Por qué usamos `page.dialog` en lugar de `page.overlay`?**
R: En versiones recientes de Flet, el manejo manual del `overlay` causaba que, al cerrar una alerta, la pantalla quedara bloqueada (efecto "pantalla blanca"). Asignar el diálogo a `page.dialog` es la práctica recomendada y estable.

**P: ¿Por qué usamos `data=...` en los botones?**
R: Al crear botones dentro de un bucle `for`, usar funciones `lambda` simples a veces captura la referencia equivocada de la variable iteradora (closure tardío). Asignar el ID a la propiedad `data` del control garantiza que cada botón transporte su propia información de manera segura.

**P: ¿Por qué convertimos todo a `str()` en las tablas?**
R: El control `ft.Text()` de Flet es estricto con los tipos. Si pasamos un `int` (como el stock) directamente, el framework intenta iterar sobre él internamente y falla. `str(valor)` sanitiza la entrada para la UI.

---

## 🗄️ Esquema de Base de Datos (`nexo.db`)

* **productos:** `codigo` (PK), `nombre`, `precio`, `cantidad`.
* **usuarios:** `usuario` (PK), `password`, `nombre`.
* **ventas:** `id` (PK), `fecha`, `total`, `usuario`.
* **detalle_ventas:** `id_venta` (FK), `id_producto`, `cantidad`, `precio_unitario`.

---
*Documentación actualizada para la versión Estable 1.0*
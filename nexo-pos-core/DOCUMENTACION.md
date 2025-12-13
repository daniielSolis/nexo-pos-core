# 📘 Documentación Técnica - NEXO POS

**Versión:** Estable (con correcciones de UI y Lógica)
**Tecnologías:** Python, Flet, SQLite
---

##  Arquitectura del Sistema

El sistema opera como una aplicación de escritorio monolítica gestionada por `main.py`, que orquesta la interfaz gráfica y la lógica de negocio, comunicándose con una capa de datos local.

### Estructura de Ficheros
* **`main.py`**: Controlador principal. Contiene toda la lógica de UI, eventos y navegación.
* **`data/database.py`**: Módulo de persistencia (SQL). Maneja la conexión a `nexo.db` y ejecuta las sentencias CRUD.
* **`tickets/`**: Directorio donde se generan los recibos de venta en formato `.txt`.
* **`reportes/`**: Directorio para la exportación de datos en formato `.csv`.

---

##  Lógica de Negocio por Módulos

### 1. Módulo de Ventas (`mostrar_ventas`)
Encargado de la facturación y salida de productos.

* **Gestión de Estado (`carrito_compras`):** Utiliza una lista en memoria volátil para manipular los productos antes de la transacción final.
* **Validación de Stock Silenciosa:**
    * En la función `procesar_producto`, se verifica `if stock_real <= 0`.
    * **Comportamiento:** Si no hay stock, la función retorna (`return`) inmediatamente. **No se muestra alerta ni ventana emergente** para no interrumpir el flujo de trabajo del cajero (Mejora de UX).
* **Catálogo Rápido:**
    * Implementado mediante un `DataTable` dentro de un `AlertDialog`.
    * Se utiliza `page.overlay.extend` para manejar las ventanas modales.
* **Manejo de Tipos (`str`):**
    * Al renderizar la tabla, se utiliza `ft.Text(str(p[0]))` para convertir enteros a cadenas. *Esto previene el error crítico "int object is not iterable".*

### 2. Módulo de Inventario (`mostrar_inventario`)
Gestión administrativa de productos (CRUD).

* **Seguridad:** Requiere validación de contraseña (`validar_admin`) para acciones sensibles (Agregar stock, Eliminar, Editar).
* **Botones Interactivos (Solución "Botones Muertos"):**
    * **Problema anterior:** El uso de `lambda` simples dentro de bucles `for` perdía la referencia del índice.
    * **Solución actual:** Se utiliza la propiedad `data` del control (`btn.data = p[0]`). Al hacer clic, se recupera el ID exacto usando `e.control.data`.
* **Validación Anti-Fantasmas:**
    * Antes de guardar (`guardar`), se verifica que los campos no estén vacíos usando `.strip()` y que los valores numéricos sean positivos. Esto evita la corrupción de la base de datos con registros vacíos.

### 3. Módulo de Reportes (`mostrar_reportes`)
Visualización y exportación de datos históricos.

* **Drill-Down (Ver Detalle):**
    * El botón "Ojo" (`IconButton`) permite ver el desglose de productos de una venta específica mediante un diálogo modal.
* **Exportación:**
    * Función `exportar_excel`: Genera un archivo CSV compatible con Excel (codificación `utf-8-sig`) en la carpeta `reportes/`.

### 4. Generación de Tickets (`generar_ticket`)
* Crea archivos de texto plano diseñados para impresoras térmicas.
* Utiliza `os.startfile` para invocar al visor predeterminado del sistema operativo y facilitar la impresión inmediata.

---

## 🛠️Notas para Desarrolladores (Mantenimiento)

### Sobre el Manejo de Errores Visuales
1.  **Pantalla Roja (Crash):** Flet no puede renderizar tipos `int` o `float` directamente en un control `Text`. **Regla:** Siempre envolver los datos numéricos de la BD en `str()`.
    * *Correcto:* `ft.Text(str(precio))`
    * *Incorrecto:* `ft.Text(precio)`

2.  **Bloqueo de UI (Pantalla Blanca):**
    * Se ha optimizado el uso de alertas. En lugar de lanzar pop-ups invasivos para errores menores (como stock 0), se opta por validaciones silenciosas o mensajes no bloqueantes (`SnackBar`), manteniendo la interfaz fluida.

### Sobre la Base de Datos
* Las consultas SQL están aisladas en `data/database.py`. Cualquier cambio en la estructura de tablas (`nexo.db`) debe reflejarse primero en ese archivo antes de modificar `main.py`.

---
*Documentación generada para la versión actual del repositorio.*
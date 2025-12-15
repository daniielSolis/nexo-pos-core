# Documentación Técnica — NEXO POS

## 1. Visión general

NEXO POS es un sistema de punto de venta desarrollado en Python que implementa una arquitectura modular, separando claramente la interfaz gráfica, la lógica de negocio y el acceso a datos.

El objetivo principal del proyecto es ofrecer un POS funcional, mantenible y fácilmente escalable, aplicando buenas prácticas de organización de código.

---

## 2. Estructura del proyecto

### 📁 screens/

Contiene todas las pantallas de la aplicación. Cada archivo representa una vista independiente:

* `login.py` → Autenticación de usuarios
* `dashboard.py` → Menú principal
* `ventas.py` → Punto de venta
* `inventario.py` → Gestión de productos
* `reportes.py` → Reportes y estadísticas

Las pantallas manejan únicamente lógica de UI y navegación.

---

### 📁 services/

Contiene la lógica de negocio que no depende directamente de la interfaz:

* `ticket_service.py` → Generación de tickets de venta

Esta separación permite reutilizar y probar la lógica sin depender de Flet.

---

### 📁 data/

Capa de acceso a datos:

* `database.py` → Conexión SQLite y consultas SQL

Centralizar la base de datos evita duplicación de consultas y facilita cambios futuros de motor.

---

### 📁 utils/

Funciones auxiliares reutilizables:

* `validators.py` → Validaciones de entrada
* `constants.py` → Constantes del sistema

---

### 📁 scripts/

Scripts de mantenimiento y verificación:

* `check_db.py`
* `check_products.py`

Pensados para ejecución manual.

---

## 3. Flujo general del sistema

1. Inicio en pantalla de **login**
2. Validación de credenciales contra base de datos
3. Acceso al **dashboard**
4. Navegación hacia:

   * Ventas
   * Inventario
   * Reportes

Cada módulo funciona de forma independiente, compartiendo únicamente servicios y base de datos.

---

## 4. Decisiones técnicas importantes

* Uso de `data` en controles de Flet para evitar closures incorrectos
* Separación UI / lógica / persistencia
* Base de datos SQLite por simplicidad y portabilidad
* Generación de archivos locales (tickets y reportes)

Estas decisiones permiten mantener el proyecto simple pero profesional.

---

## 5. Escalabilidad futura

El sistema está preparado para:

* Roles de usuario
* Módulo de clientes
* Historial avanzado de ventas
* Pruebas unitarias sobre `services`
* Migración a otro framework UI si es necesario

---

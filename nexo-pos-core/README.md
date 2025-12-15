# NEXO POS

Sistema de Punto de Venta (POS) desarrollado en Python utilizando **Flet** como framework de interfaz gráfica y **SQLite** como motor de base de datos.

NEXO POS está pensado como un sistema funcional, modular y escalable para la gestión de ventas, inventario y reportes, enfocado en buenas prácticas de organización y arquitectura de software.

---

##  Características principales

* 🔐 Sistema de **login de usuarios**
* 🛒 **Punto de venta** con carrito dinámico
* 📦 **Gestión de inventario** (alta, edición, stock y eliminación)
* 📊 **Reportes de ventas** con detalle por ticket
* 🧾 Generación automática de **tickets de venta**
* 📁 Exportación de reportes a **CSV (Excel)**
* 🗃️ Persistencia de datos con **SQLite**

---

##  Arquitectura del proyecto

El proyecto está organizado de forma modular para facilitar su mantenimiento y escalabilidad:

```
nexo-pos-core/
│
├── screens/        # Pantallas (UI y navegación)
├── services/       # Lógica de negocio
├── data/           # Acceso a base de datos
├── utils/          # Utilidades y validaciones
├── scripts/        # Scripts auxiliares
├── reports/        # Archivos CSV generados
├── tickets/        # Tickets de venta
├── main.py         # Punto de entrada de la aplicación
└── nexo.db         # Base de datos SQLite
```

---

##  Tecnologías utilizadas

* **Python 3**
* **Flet** (UI)
* **SQLite** (Base de datos)
* **CSV** (Exportación de reportes)

---

## ▶ Ejecución del proyecto

1. Clona el repositorio:

   ```bash
   git clone https://github.com/tu-usuario/nexo-pos-core.git
   ```

2. Crea y activa un entorno virtual:

   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   ```

3. Instala dependencias:

   ```bash
   pip install flet
   ```

4. Ejecuta la aplicación:

   ```bash
   python main.py
   ```

---

## 📌 Estado del proyecto

Proyecto funcional y estable.

Pensado como base sólida para:

* agregar roles de usuario
* manejo de clientes/proveedores
* mejoras visuales
* pruebas unitarias sobre la lógica de negocio

---
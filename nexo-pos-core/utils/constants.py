"""Constantes del sistema NEXO POS"""

WINDOW_TITLE = "NEXO POS"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
THEME_MODE = "dark"
WINDOW_PADDING = 20

class Colors:
    PRIMARY = "blue"
    SUCCESS = "green"
    WARNING = "orange"
    DANGER = "red"
    INFO = "purple"
    VENTAS = "green"
    INVENTARIO = "orange"
    REPORTES = "purple"
    TEXT_PRIMARY = "white"
    TEXT_SECONDARY = "grey"
    BACKGROUND_CARD = "#1A2E20"

class Icons:
    BACK = "arrow_back"
    LOGOUT = "logout"
    VENTAS = "shopping_cart"
    INVENTARIO = "inventory"
    REPORTES = "assessment"
    AGREGAR = "add_circle_outline"
    ELIMINAR = "delete"
    EDITAR = "edit"
    GUARDAR = "save"
    BUSCAR = "search"
    VER = "visibility"
    INCREMENTAR = "add_circle_outline"
    DECREMENTAR = "remove_circle_outline"
    CARRITO = "add_shopping_cart"
    ALERTA = "warning"
    LOGIN = "lock_person"
    USUARIO = "person"
    PASSWORD = "key"

class Sizes:
    TITULO_GRANDE = 30
    TITULO_MEDIO = 20
    TITULO_PEQUEÑO = 16
    BOTON_ALTO = 50
    BOTON_ANCHO_GRANDE = 200
    BOTON_ANCHO_MENU = 200
    BOTON_ALTO_MENU = 200
    INPUT_CODIGO = 150
    INPUT_NOMBRE = 300
    INPUT_NUMERO = 100
    INPUT_BUSQUEDA = 400
    INPUT_LOGIN = 300
    ICONO_GRANDE = 80
    ICONO_MEDIO = 50
    MODAL_DIALOGO_ALTO = 300
    TABLA_CATALOGO_ALTO = 300
    TABLA_REPORTES_ALTO = 400

class Messages:
    PRODUCTO_CREADO = "✅ Producto Creado"
    PRODUCTO_EDITADO = "✅ Producto Editado"
    PRODUCTO_ELIMINADO = "🗑️ Producto Eliminado"
    STOCK_ACTUALIZADO = "✅ Stock Actualizado"
    DATOS_INCORRECTOS = "❌ Datos incorrectos"
    PRODUCTO_NO_ENCONTRADO = "❌ Producto no encontrado"
    ERROR_GUARDAR_VENTA = "❌ Error al guardar venta"
    PASSWORD_INCORRECTA = "❌ Contraseña Incorrecta"
    COMPLETAR_CAMPOS = "⚠️ Completa todos los campos"
    CODIGO_REPETIDO = "⚠️ Código repetido"
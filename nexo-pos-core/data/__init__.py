"""Paquete de Base de Datos"""
from .database import (
    crear_conexion, registrar_producto, obtener_productos,
    buscar_producto, realizar_venta, obtener_ventas,
    obtener_detalle_venta, sumar_stock, eliminar_producto,
    validar_admin, editar_producto
)

__all__ = [
    'crear_conexion', 'registrar_producto', 'obtener_productos',
    'buscar_producto', 'realizar_venta', 'obtener_ventas',
    'obtener_detalle_venta', 'sumar_stock', 'eliminar_producto',
    'validar_admin', 'editar_producto'
]
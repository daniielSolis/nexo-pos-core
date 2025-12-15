"""Paquete de Pantallas"""
from .login import LoginScreen
from .dashboard import DashboardScreen
from .ventas import VentasScreen
from .inventario import InventarioScreen
from .reportes import ReportesScreen

__all__ = [
    'LoginScreen',
    'DashboardScreen',
    'VentasScreen',
    'InventarioScreen',
    'ReportesScreen',
]
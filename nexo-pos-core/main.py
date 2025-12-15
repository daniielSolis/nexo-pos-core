"""
NEXO POS - Sistema de Punto de Venta
Entry Point Principal
"""
import flet as ft
from utils.constants import WINDOW_TITLE, WINDOW_WIDTH, WINDOW_HEIGHT, THEME_MODE, WINDOW_PADDING
from screens import LoginScreen, DashboardScreen, VentasScreen, InventarioScreen, ReportesScreen


class NexoPOS:
    """Clase principal de la aplicación"""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.usuario_actual = None
        self._configurar_ventana()
        
        # Pantallas
        self.pantalla_login = None
        self.pantalla_dashboard = None
        self.pantalla_ventas = None
        self.pantalla_inventario = None
        self.pantalla_reportes = None
    
    def _configurar_ventana(self):
        """Configura las propiedades de la ventana"""
        self.page.title = WINDOW_TITLE
        self.page.theme_mode = THEME_MODE
        self.page.padding = WINDOW_PADDING
        self.page.window_width = WINDOW_WIDTH
        self.page.window_height = WINDOW_HEIGHT
    
    def iniciar(self):
        """Inicia la aplicación mostrando el login"""
        self.mostrar_login()
    
    def mostrar_login(self):
        """Muestra la pantalla de login"""
        self.usuario_actual = None
        self.pantalla_login = LoginScreen(
            self.page,
            on_login_success=self.mostrar_dashboard
        )
        self.pantalla_login.mostrar()
    
    def mostrar_dashboard(self, nombre_usuario: str):
        """Muestra el dashboard principal"""
        self.usuario_actual = nombre_usuario
        self.pantalla_dashboard = DashboardScreen(
            self.page,
            nombre_usuario,
            on_ventas=lambda: self.mostrar_ventas(nombre_usuario),
            on_inventario=lambda: self.mostrar_inventario(nombre_usuario),
            on_reportes=lambda: self.mostrar_reportes(nombre_usuario),
            on_logout=self.mostrar_login
        )
        self.pantalla_dashboard.mostrar()
    
    def mostrar_ventas(self, nombre_usuario: str):
        """Muestra la pantalla de punto de venta"""
        self.pantalla_ventas = VentasScreen(
            self.page,
            nombre_usuario,
            on_volver=lambda: self.mostrar_dashboard(nombre_usuario)
        )
        self.pantalla_ventas.mostrar()
    
    def mostrar_inventario(self, nombre_usuario: str):
        """Muestra la pantalla de gestión de inventario"""
        self.pantalla_inventario = InventarioScreen(
            self.page,
            nombre_usuario,
            on_volver=lambda: self.mostrar_dashboard(nombre_usuario)
        )
        self.pantalla_inventario.mostrar()
    
    def mostrar_reportes(self, nombre_usuario: str):
        """Muestra la pantalla de reportes"""
        self.pantalla_reportes = ReportesScreen(
            self.page,
            nombre_usuario,
            on_volver=lambda: self.mostrar_dashboard(nombre_usuario)
        )
        self.pantalla_reportes.mostrar()


def main(page: ft.Page):
    """Función principal de la aplicación"""
    app = NexoPOS(page)
    app.iniciar()


if __name__ == "__main__":
    ft.app(target=main)
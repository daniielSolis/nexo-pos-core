"""Pantalla Dashboard"""
import flet as ft
from utils import Colors, Icons, Sizes

class DashboardScreen:
    
    def __init__(self, page, nombre_usuario, on_ventas, on_inventario, on_reportes, on_logout):
        self.page = page
        self.nombre_usuario = nombre_usuario
        self.on_ventas = on_ventas
        self.on_inventario = on_inventario
        self.on_reportes = on_reportes
        self.on_logout = on_logout
    
    def mostrar(self):
        self.page.clean()
        
        header = ft.AppBar(
            title=ft.Text(f"Bienvenido, {self.nombre_usuario}", weight="bold"),
            bgcolor=Colors.PRIMARY,
            center_title=False,
            actions=[
                ft.IconButton(
                    icon=Icons.LOGOUT,
                    tooltip="Cerrar Sesión",
                    on_click=lambda _: self.on_logout()
                )
            ]
        )
        
        btn_ventas = self._crear_boton_menu(
            "NUEVA VENTA",
            Icons.VENTAS,
            Colors.VENTAS,
            lambda e: self.on_ventas()
        )
        
        btn_inventario = self._crear_boton_menu(
            "INVENTARIO",
            Icons.INVENTARIO,
            Colors.INVENTARIO,
            lambda e: self.on_inventario()
        )
        
        btn_reportes = self._crear_boton_menu(
            "REPORTES",
            Icons.REPORTES,
            Colors.REPORTES,
            lambda e: self.on_reportes()
        )
        
        contenedor_botones = ft.Row(
            [btn_ventas, btn_inventario, btn_reportes],
            alignment="center",
            wrap=True
        )
        
        self.page.add(
            header,
            ft.Divider(height=50, color="transparent"),
            contenedor_botones
        )
    
    def _crear_boton_menu(self, texto, icono, color_fondo, on_click):
        return ft.Container(
            content=ft.Column([
                ft.Icon(name=icono, size=Sizes.ICONO_MEDIO, color=Colors.TEXT_PRIMARY),
                ft.Text(texto, size=Sizes.TITULO_MEDIO, weight="bold", color=Colors.TEXT_PRIMARY)
            ], alignment="center", horizontal_alignment="center"),
            width=Sizes.BOTON_ANCHO_MENU,
            height=Sizes.BOTON_ALTO_MENU,
            bgcolor=color_fondo,
            border_radius=20,
            on_click=on_click,
            padding=20,
            ink=True
        )
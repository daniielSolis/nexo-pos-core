"""Pantalla de Reportes"""
import flet as ft
from data import obtener_ventas, obtener_detalle_venta
from utils import Colors, Icons, Sizes

class ReportesScreen:
    
    def __init__(self, page, nombre_usuario, on_volver):
        self.page = page
        self.nombre_usuario = nombre_usuario
        self.on_volver = on_volver
        self.tabla_detalle = None
        self.dialogo_detalle = None
    
    def mostrar(self):
        self.page.clean()
        self.page.overlay.clear()
        
        self._crear_dialogo()
        self._crear_tabla_ventas()
    
    def _crear_dialogo(self):
        self.tabla_detalle = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Prod")),
                ft.DataColumn(ft.Text("Cant")),
                ft.DataColumn(ft.Text("Total"))
            ],
            rows=[]
        )
        
        self.dialogo_detalle = ft.AlertDialog(
            title=ft.Text("Detalle del Ticket"),
            content=ft.Column([self.tabla_detalle], height=300, scroll="auto"),
            actions=[
                ft.TextButton("Cerrar", on_click=self._cerrar_dialogo)
            ]
        )
        
        self.page.overlay.append(self.dialogo_detalle)
    
    def _crear_tabla_ventas(self):
        tabla_ventas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Total")),
                ft.DataColumn(ft.Text("Ver"))
            ],
            rows=[]
        )
        
        ventas = obtener_ventas()
        total_ingresos = 0
        
        for v in ventas:
            total_ingresos += v[2]
            
            btn_ver = ft.IconButton(
                icon=Icons.VER,
                icon_color=Colors.PRIMARY,
                data=v[0],
                on_click=lambda e: self._ver_detalle(e.control.data)
            )
            
            tabla_ventas.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(v[0]))),
                    ft.DataCell(ft.Text(str(v[1]))),
                    ft.DataCell(ft.Text(
                        f"${v[2]:.2f}",
                        color=Colors.SUCCESS,
                        weight="bold"
                    )),
                    ft.DataCell(btn_ver)
                ])
            )
        
        card_total = ft.Container(
            content=ft.Column([
                ft.Text("TOTAL INGRESOS", size=15),
                ft.Text(
                    f"${total_ingresos:.2f}",
                    size=40,
                    weight="bold",
                    color=Colors.SUCCESS
                )
            ], alignment="center"),
            padding=20,
            border=ft.border.all(1, Colors.SUCCESS),
            border_radius=15,
            bgcolor=Colors.BACKGROUND_CARD
        )
        
        header = ft.Row([
            ft.IconButton(
                icon=Icons.BACK,
                on_click=lambda _: self.on_volver()
            ),
            ft.Text("Reportes Financieros", size=Sizes.TITULO_GRANDE, weight="bold")
        ])
        
        self.page.add(
            header,
            ft.Divider(),
            ft.Row([card_total], alignment="center"),
            ft.Divider(),
            ft.Column([tabla_ventas], scroll="auto", height=400)
        )
    
    def _ver_detalle(self, id_venta):
        productos = obtener_detalle_venta(id_venta)
        self.tabla_detalle.rows.clear()
        
        for p in productos:
            self.tabla_detalle.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(p[0]))),
                    ft.DataCell(ft.Text(str(p[1]))),
                    ft.DataCell(ft.Text(f"${p[3]:.2f}"))
                ])
            )
        
        self.dialogo_detalle.open = True
        self.page.update()
    
    def _cerrar_dialogo(self, e):
        self.dialogo_detalle.open = False
        self.page.update()
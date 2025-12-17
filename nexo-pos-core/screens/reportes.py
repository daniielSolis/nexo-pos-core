"""Pantalla de Reportes - NEXO POS"""
import flet as ft
from data.database import obtener_ventas, obtener_detalle_venta, obtener_productos_bajo_stock
from utils.constants import Colors, Icons, Sizes

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
        
        self._crear_dialogo_detalle()
        self._crear_interfaz()
    
    def _crear_dialogo_detalle(self):
        """Crea el diálogo para mostrar detalle de venta"""
        
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
    
    def _crear_interfaz(self):
        """Crea la interfaz principal con pestañas"""
        
        header = ft.Row([
            ft.IconButton(
                icon=Icons.BACK,
                on_click=lambda _: self.on_volver()
            ),
            ft.Text("Reportes", size=Sizes.TITULO_GRANDE, weight="bold")
        ])
        
        # 🆕 Sistema de Pestañas
        tabs = ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="💰 Ventas",
                    icon=Icons.REPORTES,
                    content=self._crear_tab_ventas()
                ),
                ft.Tab(
                    text="⚠️ Por Comprar",  # 🆕 NUEVA PESTAÑA
                    icon="shopping_bag",
                    content=self._crear_tab_reabastecimiento()  # 🆕 NUEVO CONTENIDO
                )
            ],
            expand=1
        )
        
        self.page.add(
            header,
            ft.Divider(),
            tabs
        )
    
    def _crear_tab_ventas(self):
        """Crea la pestaña de ventas (contenido original)"""
        
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
        
        # 🔧 ARREGLADO: Agregar scroll vertical con altura fija
        return ft.Column([
            ft.Row([card_total], alignment="center"),
            ft.Divider(),
            ft.Container(
                content=ft.Column([tabla_ventas], scroll=ft.ScrollMode.AUTO),
                alignment=ft.alignment.center,
                height=400  # 🆕 Altura fija para activar scroll
            )
        ], horizontal_alignment="center")
    
    def _crear_tab_reabastecimiento(self):
        """🆕 NUEVA PESTAÑA: Productos que necesitan reabastecimiento"""
        
        # Tabla de productos bajo stock
        tabla_reabasto = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Stock Actual")),
                ft.DataColumn(ft.Text("Stock Mínimo")),
                ft.DataColumn(ft.Text("Faltante")),
            ],
            rows=[]
        )
        
        # Obtener productos bajo stock desde BD
        productos_bajo_stock = obtener_productos_bajo_stock()
        total_productos_criticos = len(productos_bajo_stock)
        productos_agotados = sum(1 for p in productos_bajo_stock if p[3] == 0)
        
        # Llenar tabla
        for p in productos_bajo_stock:
            # p = (codigo, nombre, precio, stock, stock_minimo, faltante)
            codigo = p[0]
            nombre = p[1]
            stock_actual = p[3]
            stock_minimo = p[4]
            faltante = p[5]
            
            # 🆕 Determinar color según criticidad
            if stock_actual == 0:
                # AGOTADO - Rojo intenso
                color_stock = Colors.DANGER
                peso = "bold"
                icono_alerta = "⛔"
            elif stock_actual <= stock_minimo / 2:
                # MUY CRÍTICO - Naranja
                color_stock = Colors.WARNING
                peso = "bold"
                icono_alerta = "⚠️"
            else:
                # CRÍTICO - Gris
                color_stock = Colors.TEXT_SECONDARY
                peso = None
                icono_alerta = "📦"
            
            # 🆕 Agregar fila con colores condicionales
            tabla_reabasto.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(codigo), size=12)),
                        ft.DataCell(ft.Row([
                            ft.Text(icono_alerta),
                            ft.Text(str(nombre)[:30])  # Truncar nombres largos
                        ])),
                        ft.DataCell(ft.Text(
                            str(stock_actual),
                            color=color_stock,  # 🔴 Color según stock
                            weight=peso,
                            size=16
                        )),
                        ft.DataCell(ft.Text(str(stock_minimo), size=12)),
                        ft.DataCell(ft.Text(
                            f"+{faltante}",
                            color=Colors.WARNING,
                            weight="bold"
                        ))
                    ]
                )
            )
        
        # 🆕 Cards informativos (KPIs)
        card_criticos = ft.Container(
            content=ft.Column([
                ft.Icon("warning", color=Colors.WARNING, size=30),
                ft.Text("Productos Críticos", size=12, text_align="center"),
                ft.Text(
                    str(total_productos_criticos),
                    size=30,
                    weight="bold",
                    color=Colors.WARNING
                )
            ], alignment="center", horizontal_alignment="center"),
            padding=15,
            border=ft.border.all(2, Colors.WARNING),
            border_radius=10,
            width=150
        )
        
        card_agotados = ft.Container(
            content=ft.Column([
                ft.Icon("cancel", color=Colors.DANGER, size=30),
                ft.Text("Agotados", size=12, text_align="center"),
                ft.Text(
                    str(productos_agotados),
                    size=30,
                    weight="bold",
                    color=Colors.DANGER
                )
            ], alignment="center", horizontal_alignment="center"),
            padding=15,
            border=ft.border.all(2, Colors.DANGER),
            border_radius=10,
            width=150
        )
        
        # 🆕 Mensaje cuando NO hay productos críticos
        if total_productos_criticos == 0:
            contenido = ft.Column([
                ft.Row([card_criticos, card_agotados], alignment="center"),
                ft.Divider(),
                ft.Container(
                    content=ft.Column([
                        ft.Icon("check_circle", color=Colors.SUCCESS, size=60),
                        ft.Text(
                            "✅ Todos los productos tienen stock suficiente",
                            size=18,
                            weight="bold",
                            color=Colors.SUCCESS,
                            text_align="center"
                        ),
                        ft.Text(
                            "No hay productos que requieran reabastecimiento",
                            size=14,
                            color=Colors.TEXT_SECONDARY,
                            text_align="center"
                        )
                    ], alignment="center", horizontal_alignment="center"),
                    padding=40
                )
            ])
        else:
            # 🆕 Mostrar tabla con productos críticos
            contenido = ft.Column([
                ft.Row([card_criticos, card_agotados], alignment="center", spacing=20),
                ft.Divider(),
                ft.Row([
                    ft.Icon("info", color=Colors.INFO),
                    ft.Text(
                        "Productos que requieren reabastecimiento urgente:",
                        size=14,
                        weight="bold"
                    )
                ], alignment="center"),
                ft.Container(
                    content=ft.Column([tabla_reabasto], scroll=ft.ScrollMode.AUTO),
                    alignment=ft.alignment.center,
                    height=320  # Altura fija para scroll
                )
            ], horizontal_alignment="center")
        
        return contenido
    
    def _ver_detalle(self, id_venta):
        """Muestra el detalle de una venta específica"""
        
        productos = obtener_detalle_venta(id_venta)
        self.tabla_detalle.rows.clear()
        
        # 🔧 ARREGLADO: Verificar si hay productos
        if not productos:
            self.tabla_detalle.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text("Sin datos", color=Colors.TEXT_SECONDARY)),
                    ft.DataCell(ft.Text("-")),
                    ft.DataCell(ft.Text("-"))
                ])
            )
        else:
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
        """Cierra el diálogo de detalle"""
        self.dialogo_detalle.open = False
        self.page.update()
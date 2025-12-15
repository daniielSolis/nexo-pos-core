"""Pantalla de Punto de Venta"""
import flet as ft
from data.database import obtener_productos, buscar_producto, realizar_venta
from services.ticket_service import ticket_service
from utils.constants import Colors, Icons, Sizes, Messages

class VentasScreen:
    
    def __init__(self, page, nombre_usuario, on_volver):
        self.page = page
        self.nombre_usuario = nombre_usuario
        self.on_volver = on_volver
        self.carrito_compras = []
        
        # Componentes UI
        self.txt_total = None
        self.txt_codigo = None
        self.tabla_ventas = None
        self.tabla_catalogo = None
        
        # Diálogos
        self.dialogo_alerta = None
        self.dialogo_catalogo = None
        self.txt_mensaje_alerta = None
    
    def mostrar(self):
        self.page.clean()
        self.page.overlay.clear()
        self.carrito_compras.clear()
        
        self._crear_dialogos()
        self._crear_componentes()
        self._agregar_a_pagina()
    
    def _crear_dialogos(self):
        # Diálogo de Alerta
        self.txt_mensaje_alerta = ft.Text("", size=18)
        
        self.dialogo_alerta = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(Icons.ALERTA, color=Colors.DANGER),
                ft.Text("¡ATENCIÓN!")
            ]),
            content=self.txt_mensaje_alerta,
            actions=[
                ft.TextButton("ENTENDIDO", on_click=self._cerrar_alerta)
            ],
            actions_alignment="center"
        )
        
        # Catálogo Rápido
        self.tabla_catalogo = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cód")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("+")),
            ],
            rows=[]
        )
        
        self.dialogo_catalogo = ft.AlertDialog(
            title=ft.Text("Catálogo de Productos 📖"),
            content=ft.Column([
                ft.Text("Selecciona para agregar al carrito:", size=12, color=Colors.TEXT_SECONDARY),
                ft.Container(content=self.tabla_catalogo, height=Sizes.TABLA_CATALOGO_ALTO, padding=10)
            ], height=350, width=600, scroll="auto"),
            actions=[ft.TextButton("Cerrar", on_click=self._cerrar_catalogo)]
        )
        
        self.page.overlay.extend([self.dialogo_alerta, self.dialogo_catalogo])
    
    def _crear_componentes(self):
        self.txt_total = ft.Text("$0.00", size=40, weight="bold", color=Colors.SUCCESS)
        
        self.tabla_ventas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Subtotal")),
                ft.DataColumn(ft.Text("Borrar")),
            ],
            rows=[]
        )
        
        self.txt_codigo = ft.TextField(
            label="Buscar producto (Código o Nombre)...",
            width=Sizes.INPUT_BUSQUEDA,
            autofocus=True,
            on_submit=self._agregar_desde_input,
            border_radius=10,
            prefix_icon=Icons.BUSCAR
        )
    
    def _agregar_a_pagina(self):
        header = ft.Row([
            ft.IconButton(icon=Icons.BACK, on_click=lambda _: self.on_volver()),
            ft.Text("Punto de Venta", size=Sizes.TITULO_GRANDE, weight="bold")
        ], alignment="start")
        
        btn_catalogo = ft.ElevatedButton(
            "Ver Productos",
            icon="list",
            bgcolor=Colors.PRIMARY,
            color=Colors.TEXT_PRIMARY,
            height=Sizes.BOTON_ALTO,
            on_click=self._abrir_catalogo
        )
        
        btn_cobrar = ft.ElevatedButton(
            "COBRAR TICKET",
            icon=Icons.EXITO,
            bgcolor=Colors.SUCCESS,
            color=Colors.TEXT_PRIMARY,
            height=Sizes.BOTON_ALTO,
            width=Sizes.BOTON_ANCHO_GRANDE,
            on_click=self._finalizar_venta
        )
        
        panel_total = ft.Container(
            content=ft.Column([
                ft.Text("Total a Pagar:", size=16),
                self.txt_total
            ], alignment="center", horizontal_alignment="end"),
            padding=10,
            border=ft.border.all(1, Colors.SUCCESS),
            border_radius=10
        )
        
        self.page.add(
            header,
            ft.Divider(),
            ft.Row([
                ft.Row([self.txt_codigo, btn_catalogo]),
                panel_total
            ], alignment="spaceBetween"),
            ft.Divider(),
            self.tabla_ventas,
            ft.Divider(height=20, color="transparent"),
            ft.Row([btn_cobrar], alignment="end")
        )
    
    def _actualizar_tabla(self):
        self.tabla_ventas.rows.clear()
        total_general = 0
        
        for i, item in enumerate(self.carrito_compras):
            subtotal = item['precio'] * item['cantidad']
            total_general += subtotal
            
            btn_restar = ft.IconButton(
                icon=Icons.DECREMENTAR,
                icon_color=Colors.DANGER,
                data=i,
                on_click=self._restar_cantidad
            )
            
            btn_sumar = ft.IconButton(
                icon=Icons.INCREMENTAR,
                icon_color=Colors.SUCCESS,
                data=i,
                on_click=self._sumar_cantidad
            )
            
            btn_eliminar = ft.IconButton(
                icon=Icons.ELIMINAR,
                icon_color=Colors.TEXT_SECONDARY,
                data=i,
                on_click=self._eliminar_item
            )
            
            celda_cantidad = ft.Row(
                [
                    btn_restar,
                    ft.Text(str(item['cantidad']), weight="bold", size=16),
                    btn_sumar,
                ],
                alignment="center"
            )
            
            self.tabla_ventas.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(item['nombre'])),
                    ft.DataCell(ft.Text(f"${item['precio']}")),
                    ft.DataCell(celda_cantidad),
                    ft.DataCell(ft.Text(f"${subtotal:.2f}")),
                    ft.DataCell(btn_eliminar)
                ])
            )
        
        self.txt_total.value = f"${total_general:.2f}"
        self.txt_codigo.focus()
        self.page.update()
    
    def _sumar_cantidad(self, e):
        indice = e.control.data
        item = self.carrito_compras[indice]
        if item['cantidad'] < item['stock_max']:
            item['cantidad'] += 1
            self._actualizar_tabla()
        else:
            self._lanzar_alerta(f"Límite de stock alcanzado ({item['stock_max']} disponibles).")
    
    def _restar_cantidad(self, e):
        indice = e.control.data
        if self.carrito_compras[indice]['cantidad'] > 1:
            self.carrito_compras[indice]['cantidad'] -= 1
        self._actualizar_tabla()
    
    def _eliminar_item(self, e):
        indice = e.control.data
        del self.carrito_compras[indice]
        self._actualizar_tabla()
    
    def _procesar_producto(self, codigo_input):
        if not codigo_input:
            return
        
        producto_db = buscar_producto(codigo_input)
        
        if producto_db:
            stock_real = producto_db[3]
            
            # UX discreta cuando no hay stock
            if stock_real <= 0:
                self.txt_codigo.value = ""
                self.page.update()
                return
            
            encontrado = False
            for item in self.carrito_compras:
                if item['codigo'] == producto_db[0]:
                    if item['cantidad'] + 1 <= stock_real:
                        item['cantidad'] += 1
                        encontrado = True
                    else:
                        self._lanzar_alerta(f"Stock insuficiente para agregar más '{producto_db[1]}'.")
                        encontrado = True
                    break
            
            if not encontrado:
                self.carrito_compras.append({
                    "codigo": producto_db[0],
                    "nombre": producto_db[1],
                    "precio": producto_db[2],
                    "cantidad": 1,
                    "stock_max": stock_real
                })
            
            self.txt_codigo.value = ""
            self._actualizar_tabla()
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(Messages.PRODUCTO_NO_ENCONTRADO),
                bgcolor=Colors.WARNING,
                open=True
            )
            self.page.update()
    
    def _agregar_desde_input(self, e):
        self._procesar_producto(self.txt_codigo.value)
    
    def _abrir_catalogo(self, e):
        productos = obtener_productos()
        self.tabla_catalogo.rows.clear()
        
        for p in productos:
            btn_add = ft.IconButton(
                icon=Icons.CARRITO,
                icon_color=Colors.SUCCESS,
                tooltip="Agregar al Ticket",
                data=p[0],
                on_click=lambda e: [
                    self._procesar_producto(e.control.data),
                    self._cerrar_catalogo(None)
                ]
            )
            
            self.tabla_catalogo.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(p[0]))),
                    ft.DataCell(ft.Text(str(p[1]))),
                    ft.DataCell(ft.Text(f"${p[2]}")),
                    ft.DataCell(ft.Text(str(p[3]))),
                    ft.DataCell(btn_add)
                ])
            )
        
        self.dialogo_catalogo.open = True
        self.page.update()
    
    def _finalizar_venta(self, e):
        if not self.carrito_compras:
            return
        
        total_final = sum(item['precio'] * item['cantidad'] for item in self.carrito_compras)
        
        if realizar_venta(self.carrito_compras, total_final, self.nombre_usuario):
            ticket_service.generar_ticket(self.carrito_compras, total_final, self.nombre_usuario)
            self.page.snack_bar = ft.SnackBar(
                ft.Text(f"✅ Venta registrada: ${total_final:.2f}"),
                bgcolor=Colors.SUCCESS,
                open=True
            )
            self.carrito_compras.clear()
            self._actualizar_tabla()
        else:
            self.page.snack_bar = ft.SnackBar(
                ft.Text(Messages.ERROR_GUARDAR_VENTA),
                bgcolor=Colors.DANGER,
                open=True
            )
        self.page.update()
    
    def _lanzar_alerta(self, mensaje):
        self.txt_mensaje_alerta.value = mensaje
        self.dialogo_alerta.open = True
        self.page.update()
    
    def _cerrar_alerta(self, e):
        self.dialogo_alerta.open = False
        self.page.update()
    
    def _cerrar_catalogo(self, e):
        self.dialogo_catalogo.open = False
        self.page.update()
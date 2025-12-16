"""Pantalla de Inventario - NEXO POS"""
import flet as ft
from data.database import (obtener_productos, registrar_producto, sumar_stock, 
                            eliminar_producto, editar_producto, validar_admin)
from utils.validators import Validators, ValidationError
from utils.constants import Colors, Icons, Sizes, Messages

class InventarioScreen:
    
    def __init__(self, page, nombre_usuario, on_volver):
        self.page = page
        self.nombre_usuario = nombre_usuario
        self.on_volver = on_volver
        self.codigo_seleccionado = [""]
        
        # Componentes UI - Formulario Principal
        self.tabla = None
        self.txt_codigo = None
        self.txt_nombre = None
        self.txt_precio = None
        self.txt_stock = None
        self.txt_stock_minimo = None  # 🆕 NUEVO CAMPO
        
        # Diálogos
        self.dialogo_stock = None
        self.dialogo_eliminar = None
        self.dialogo_editar = None
        
        # Inputs de diálogos
        self.input_pass_stock = None
        self.input_cant_stock = None
        self.input_pass_eliminar = None
        self.input_edit_nombre = None
        self.input_edit_precio = None
        self.input_edit_stock_minimo = None  # 🆕 NUEVO CAMPO EDICIÓN
        self.input_pass_edit = None
    
    def mostrar(self):
        self.page.clean()
        self.page.overlay.clear()
        
        self._crear_dialogos()
        self._crear_componentes()
        self._agregar_a_pagina()
        self.cargar()
    
    def _crear_dialogos(self):
        """Crea todos los diálogos modales"""
        
        # Inputs para diálogo de stock
        self.input_pass_stock = ft.TextField(
            label="Contraseña Admin", 
            password=True, 
            can_reveal_password=True
        )
        self.input_cant_stock = ft.TextField(
            label="Cantidad a Agregar", 
            keyboard_type="number"
        )
        
        # Inputs para diálogo de eliminación
        self.input_pass_eliminar = ft.TextField(
            label="Contraseña Admin", 
            password=True, 
            can_reveal_password=True
        )
        
        # Inputs para diálogo de edición
        self.input_edit_nombre = ft.TextField(label="Nuevo Nombre")
        self.input_edit_precio = ft.TextField(
            label="Nuevo Precio", 
            keyboard_type="number"
        )
        
        # 🆕 NUEVO: Campo para stock mínimo en edición
        self.input_edit_stock_minimo = ft.TextField(
            label="Stock Mínimo",
            keyboard_type="number",
            hint_text="Ej: 5 unidades"
        )
        
        self.input_pass_edit = ft.TextField(
            label="Contraseña Admin", 
            password=True, 
            can_reveal_password=True
        )
        
        # Diálogo de Stock
        self.dialogo_stock = ft.AlertDialog(
            title=ft.Text("Rellenar Stock"),
            content=ft.Column([
                self.input_cant_stock, 
                self.input_pass_stock
            ], height=150),
            actions=[
                ft.ElevatedButton(
                    "CONFIRMAR",
                    bgcolor=Colors.PRIMARY,
                    color=Colors.TEXT_PRIMARY,
                    on_click=self._confirmar_stock
                )
            ]
        )
        
        # Diálogo de Eliminación
        self.dialogo_eliminar = ft.AlertDialog(
            title=ft.Text("⚠️ Eliminar Producto"),
            content=ft.Column([
                ft.Text("¿Seguro que deseas eliminarlo?"),
                self.input_pass_eliminar
            ], height=100),
            actions=[
                ft.ElevatedButton(
                    "ELIMINAR",
                    bgcolor=Colors.DANGER,
                    color=Colors.TEXT_PRIMARY,
                    on_click=self._confirmar_eliminar
                )
            ]
        )
        
        # 🆕 Diálogo de Edición - ACTUALIZADO con campo stock_minimo
        self.dialogo_editar = ft.AlertDialog(
            title=ft.Text("Editar Producto ✏️"),
            content=ft.Column([
                self.input_edit_nombre,
                self.input_edit_precio,
                self.input_edit_stock_minimo,  # 🆕 NUEVO CAMPO
                self.input_pass_edit
            ], height=280, scroll="auto"),  # Altura aumentada para nuevo campo
            actions=[
                ft.ElevatedButton(
                    "GUARDAR CAMBIOS",
                    bgcolor=Colors.SUCCESS,
                    color=Colors.TEXT_PRIMARY,
                    on_click=self._confirmar_edicion
                )
            ]
        )
        
        self.page.overlay.extend([
            self.dialogo_stock,
            self.dialogo_eliminar,
            self.dialogo_editar
        ])
    
    def _crear_componentes(self):
        """Crea los componentes de la interfaz principal"""
        
        self.txt_codigo = ft.TextField(
            label="Código",
            width=Sizes.INPUT_CODIGO,
            border_radius=10
        )
        self.txt_nombre = ft.TextField(
            label="Nombre",
            width=Sizes.INPUT_NOMBRE,
            border_radius=10
        )
        self.txt_precio = ft.TextField(
            label="Precio",
            width=Sizes.INPUT_NUMERO,
            keyboard_type="number",
            border_radius=10
        )
        self.txt_stock = ft.TextField(
            label="Stock Inicial",
            width=Sizes.INPUT_NUMERO,
            keyboard_type="number",
            border_radius=10
        )
        
        # 🆕 NUEVO: Campo para stock mínimo en formulario principal
        self.txt_stock_minimo = ft.TextField(
            label="Stock Mínimo",
            width=Sizes.INPUT_NUMERO,
            keyboard_type="number",
            border_radius=10,
            hint_text="Ej: 5",
            value="5"  # Valor por defecto
        )
        
        # 🆕 Tabla actualizada con columna "Mín"
        self.tabla = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("Mín")),  # 🆕 NUEVA COLUMNA
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=[]
        )
    
    def _agregar_a_pagina(self):
        """Agrega los componentes a la página"""
        
        header = ft.Row([
            ft.IconButton(
                icon=Icons.BACK,
                on_click=lambda _: self.on_volver()
            ),
            ft.Text("Gestión de Inventario", size=Sizes.TITULO_GRANDE, weight="bold")
        ])
        
        btn_guardar = ft.ElevatedButton(
            "GUARDAR",
            icon=Icons.GUARDAR,
            on_click=self._guardar,
            bgcolor=Colors.SUCCESS,
            color=Colors.TEXT_PRIMARY
        )
        
        self.page.add(
            header,
            ft.Divider(),
            ft.Text("Agregar Nuevo Producto:", size=Sizes.TITULO_PEQUEÑO, weight="bold"),
            ft.Row([
                self.txt_codigo,
                self.txt_nombre,
                self.txt_precio,
                self.txt_stock,
                self.txt_stock_minimo,  # 🆕 NUEVO CAMPO EN FILA
                btn_guardar
            ], wrap=True),
            ft.Divider(),
            self.tabla
        )
    
    def cargar(self):
        """Carga los productos desde la base de datos"""
        
        datos = obtener_productos()
        self.tabla.rows.clear()
        
        for p in datos:
            # p = (codigo, nombre, precio, stock, stock_minimo)
            codigo = p[0]
            nombre = p[1]
            precio = p[2]
            stock = p[3]
            stock_minimo = p[4] if len(p) > 4 else 5  # Seguridad por si no existe
            
            # 🆕 Preparar datos para edición (incluyendo stock_minimo)
            btn_editar = ft.IconButton(
                icon=Icons.EDITAR,
                icon_color=Colors.PRIMARY,
                tooltip="Editar",
                data={
                    "cod": codigo, 
                    "nom": nombre, 
                    "prec": precio, 
                    "min": stock_minimo  # 🆕 INCLUIR stock_minimo
                },
                on_click=lambda e: self._abrir_editar(
                    e.control.data["cod"],
                    e.control.data["nom"],
                    e.control.data["prec"],
                    e.control.data["min"]  # 🆕 PASAR stock_minimo
                )
            )
            
            btn_stock = ft.IconButton(
                icon=Icons.AGREGAR,
                icon_color=Colors.SUCCESS,
                tooltip="Sumar Stock",
                data=codigo,
                on_click=lambda e: self._abrir_stock(e.control.data)
            )
            
            btn_eliminar = ft.IconButton(
                icon=Icons.ELIMINAR,
                icon_color=Colors.DANGER,
                tooltip="Eliminar",
                data=codigo,
                on_click=lambda e: self._abrir_eliminar(e.control.data)
            )
            
            # 🆕 Determinar color según criticidad del stock
            if stock == 0:
                color_stock = Colors.DANGER
                peso_stock = "bold"
            elif stock <= stock_minimo:
                color_stock = Colors.WARNING
                peso_stock = "bold"
            else:
                color_stock = None
                peso_stock = None
            
            self.tabla.rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(str(codigo))),
                    ft.DataCell(ft.Text(str(nombre))),
                    ft.DataCell(ft.Text(f"${precio}")),
                    ft.DataCell(ft.Text(
                        str(stock), 
                        color=color_stock, 
                        weight=peso_stock
                    )),
                    ft.DataCell(ft.Text(str(stock_minimo), size=12)),  # 🆕 NUEVA CELDA
                    ft.DataCell(ft.Row([btn_editar, btn_stock, btn_eliminar]))
                ])
            )
        
        self.page.update()
    
    def _guardar(self, e):
        """Guarda un nuevo producto"""
        
        try:
            codigo = Validators.validar_campo_vacio(self.txt_codigo.value, "Código")
            nombre = Validators.validar_campo_vacio(self.txt_nombre.value, "Nombre")
            precio = Validators.validar_numero_positivo(self.txt_precio.value, "Precio")
            stock = Validators.validar_entero_positivo(self.txt_stock.value, "Stock")
            
            # 🆕 Validar stock mínimo
            stock_minimo = Validators.validar_entero_positivo(
                self.txt_stock_minimo.value or "5", 
                "Stock Mínimo"
            )
            
            # 🆕 Pasar stock_minimo a la función de base de datos
            if registrar_producto(codigo, nombre, precio, stock, stock_minimo):
                self._mostrar_exito(Messages.PRODUCTO_CREADO)
                # Limpiar campos
                self.txt_codigo.value = ""
                self.txt_nombre.value = ""
                self.txt_precio.value = ""
                self.txt_stock.value = ""
                self.txt_stock_minimo.value = "5"
                self.cargar()
            else:
                self._mostrar_error(Messages.CODIGO_REPETIDO)
        except ValidationError as ve:
            self._mostrar_error(str(ve))
    
    def _abrir_stock(self, cod):
        """Abre diálogo para agregar stock"""
        self.codigo_seleccionado[0] = cod
        self.input_pass_stock.value = ""
        self.input_cant_stock.value = ""
        self.dialogo_stock.open = True
        self.page.update()
    
    def _confirmar_stock(self, e):
        """Confirma y ejecuta la adición de stock"""
        try:
            cantidad = Validators.validar_entero_positivo(
                self.input_cant_stock.value,
                "Cantidad"
            )
            if cantidad == 0:
                raise ValidationError("La cantidad debe ser mayor a 0")
            
            if validar_admin(self.input_pass_stock.value):
                sumar_stock(self.codigo_seleccionado[0], cantidad)
                self._mostrar_exito(Messages.STOCK_ACTUALIZADO)
                self._cerrar_dialogos(None)
                self.cargar()
            else:
                self._mostrar_error(Messages.PASSWORD_INCORRECTA)
        except ValidationError as ve:
            self._mostrar_error(str(ve))
    
    def _abrir_eliminar(self, cod):
        """Abre diálogo de eliminación"""
        self.codigo_seleccionado[0] = cod
        self.input_pass_eliminar.value = ""
        self.dialogo_eliminar.open = True
        self.page.update()
    
    def _confirmar_eliminar(self, e):
        """Confirma y ejecuta la eliminación"""
        if validar_admin(self.input_pass_eliminar.value):
            eliminar_producto(self.codigo_seleccionado[0])
            self._mostrar_exito(Messages.PRODUCTO_ELIMINADO)
            self._cerrar_dialogos(None)
            self.cargar()
        else:
            self._mostrar_error(Messages.PASSWORD_INCORRECTA)
    
    def _abrir_editar(self, cod, nom, prec, stock_min):
        """🆕 Abre diálogo de edición (ahora recibe stock_minimo)"""
        self.codigo_seleccionado[0] = cod
        self.input_edit_nombre.value = nom
        self.input_edit_precio.value = str(prec)
        self.input_edit_stock_minimo.value = str(stock_min)  # 🆕 CARGAR VALOR ACTUAL
        self.input_pass_edit.value = ""
        self.dialogo_editar.open = True
        self.page.update()
    
    def _confirmar_edicion(self, e):
        """🆕 Confirma y ejecuta la edición (ahora incluye stock_minimo)"""
        try:
            nombre = Validators.validar_campo_vacio(
                self.input_edit_nombre.value,
                "Nombre"
            )
            precio = Validators.validar_numero_positivo(
                self.input_edit_precio.value,
                "Precio"
            )
            
            # 🆕 Validar stock mínimo en edición
            stock_minimo = Validators.validar_entero_positivo(
                self.input_edit_stock_minimo.value or "5",
                "Stock Mínimo"
            )
            
            if validar_admin(self.input_pass_edit.value):
                # 🆕 Pasar stock_minimo a la función de edición
                if editar_producto(self.codigo_seleccionado[0], nombre, precio, stock_minimo):
                    self._mostrar_exito(Messages.PRODUCTO_EDITADO)
                    self._cerrar_dialogos(None)
                    self.cargar()
                else:
                    self._mostrar_error("⚠️ Error al editar")
            else:
                self._mostrar_error(Messages.PASSWORD_INCORRECTA)
        except ValidationError as ve:
            self._mostrar_error(str(ve))
    
    def _cerrar_dialogos(self, e):
        """Cierra todos los diálogos"""
        self.dialogo_stock.open = False
        self.dialogo_eliminar.open = False
        self.dialogo_editar.open = False
        self.page.update()
    
    def _mostrar_error(self, mensaje: str):
        """Muestra mensaje de error"""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(mensaje),
            bgcolor=Colors.DANGER,
            open=True
        )
        self.page.update()
    
    def _mostrar_exito(self, mensaje: str):
        """Muestra mensaje de éxito"""
        self.page.snack_bar = ft.SnackBar(
            ft.Text(mensaje),
            bgcolor=Colors.SUCCESS,
            open=True
        )
        self.page.update()
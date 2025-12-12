import flet as ft
import os
import datetime
from data.database import (crear_conexion, registrar_producto, obtener_productos, 
                           buscar_producto, realizar_venta, obtener_ventas, 
                           obtener_detalle_venta, sumar_stock, eliminar_producto, 
                           validar_admin, editar_producto)

def main(page: ft.Page):
    # --- Configuración Visual General ---
    page.title = "NEXO POS"
    page.theme_mode = "dark"
    page.padding = 20
    page.window_width = 1000
    page.window_height = 700

    carrito_compras = []

    # --- FUNCIÓN: GENERAR TICKET (Impresora Virtual) ---
    def generar_ticket(items, total, vendedor):
        if not os.path.exists("tickets"):
            os.makedirs("tickets")

        fecha_actual = datetime.datetime.now()
        nombre_archivo = f"tickets/ticket_{fecha_actual.strftime('%Y%m%d_%H%M%S')}.txt"

        linea = "="*32 + "\n"
        texto = linea
        texto += "          NEXO POS\n"
        texto += "     Tu Tienda de Confianza\n"
        texto += linea
        texto += f"Fecha: {fecha_actual.strftime('%d/%m/%Y %H:%M:%S')}\n"
        texto += f"Le atendió: {vendedor}\n"
        texto += linea
        texto += "CANT  PRODUCTO          TOTAL\n"
        texto += "-"*32 + "\n"

        for item in items:
            subtotal = item['precio'] * item['cantidad']
            texto += f"{item['cantidad']} x {item['nombre'][:15]:<15} ${subtotal:.2f}\n"

        texto += "-"*32 + "\n"
        texto += f"TOTAL A PAGAR:      ${total:.2f}\n"
        texto += linea
        texto += "    ¡GRACIAS POR SU COMPRA!\n"
        texto += linea
        texto += "\n"
        texto += "      Sistema Punto de Venta\n"
        texto += "           *** NEXO ***\n"
        texto += "="*32

        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(texto)

        try:
            os.startfile(nombre_archivo)
        except:
            pass

    # ---------------------------------------------------------
    # PANTALLA 4: PUNTO DE VENTA 
    # ---------------------------------------------------------
    def mostrar_ventas(usuario_nombre):
        page.clean()
        page.overlay.clear()
        carrito_compras.clear()
        
        # Alertas Visuales
        txt_mensaje_alerta = ft.Text("", size=18)
        
        def cerrar_alerta(e):
            dialogo_alerta.open = False
            page.update()

        dialogo_alerta = ft.AlertDialog(
            title=ft.Row([ft.Icon("warning", color="red"), ft.Text("¡ATENCIÓN!")]),
            content=txt_mensaje_alerta,
            actions=[ft.TextButton("ENTENDIDO", on_click=cerrar_alerta)],
            actions_alignment="center"
        )
        
        # --- CATÁLOGO RÁPIDO (Pop-up) ---
        tabla_catalogo = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Cód")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("+")), 
            ],
            rows=[]
        )
        
        def cerrar_catalogo(e):
            dialogo_catalogo.open = False
            page.update()

        dialogo_catalogo = ft.AlertDialog(
            title=ft.Text("Catálogo de Productos 📖"),
            content=ft.Column([
                ft.Text("Selecciona para agregar al carrito:", size=12, color="grey"),
                ft.Container(content=tabla_catalogo, height=300, padding=10) 
            ], height=350, width=600, scroll="auto"),
            actions=[ft.TextButton("Cerrar", on_click=cerrar_catalogo)]
        )
        
        page.overlay.extend([dialogo_alerta, dialogo_catalogo])

        def lanzar_alerta(mensaje):
            txt_mensaje_alerta.value = mensaje
            dialogo_alerta.open = True
            page.update()

        # Componentes UI
        txt_total = ft.Text("$0.00", size=40, weight="bold", color="green")
        
        tabla_ventas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Producto")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Cantidad")),
                ft.DataColumn(ft.Text("Subtotal")),
                ft.DataColumn(ft.Text("Borrar")),
            ],
            rows=[]
        )

        def actualizar_tabla():
            tabla_ventas.rows.clear()
            total_general = 0
            
            for i, item in enumerate(carrito_compras):
                subtotal = item['precio'] * item['cantidad']
                total_general += subtotal
                
                celda_cantidad = ft.Row(
                    [
                        ft.IconButton(icon="remove_circle_outline", icon_color="red", on_click=lambda e, x=i: restar_cantidad(x)),
                        ft.Text(str(item['cantidad']), weight="bold", size=16),
                        ft.IconButton(icon="add_circle_outline", icon_color="green", on_click=lambda e, x=i: sumar_cantidad(x)),
                    ],
                    alignment="center"
                )

                tabla_ventas.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(item['nombre'])),
                        ft.DataCell(ft.Text(f"${item['precio']}")),
                        ft.DataCell(celda_cantidad),
                        ft.DataCell(ft.Text(f"${subtotal:.2f}")),
                        ft.DataCell(ft.IconButton(icon="delete", icon_color="grey", on_click=lambda e, x=i: eliminar_item(x)))
                    ])
                )
            
            txt_total.value = f"${total_general:.2f}"
            txt_codigo.focus()
            page.update()

        def sumar_cantidad(indice):
            item = carrito_compras[indice]
            if item['cantidad'] < item['stock_max']:
                item['cantidad'] += 1
                actualizar_tabla()
            else:
                lanzar_alerta(f"Límite de stock alcanzado ({item['stock_max']} disponibles).")

        def restar_cantidad(indice):
            if carrito_compras[indice]['cantidad'] > 1:
                carrito_compras[indice]['cantidad'] -= 1
            actualizar_tabla()

        def eliminar_item(indice):
            del carrito_compras[indice]
            actualizar_tabla()

        def procesar_producto(codigo_input):
            if not codigo_input: return

            producto_db = buscar_producto(codigo_input)
            
            if producto_db:
                stock_real = producto_db[3]
                
                # --- AQUÍ ESTÁ EL CAMBIO ---
                if stock_real <= 0:
                    # Si no hay stock, simplemente limpiamos y nos salimos en silencio.
                    # NO lanzamos alerta.
                    txt_codigo.value = ""
                    page.update()
                    return
                # ---------------------------

                encontrado = False
                for item in carrito_compras:
                    if item['codigo'] == producto_db[0]:
                        if item['cantidad'] + 1 <= stock_real:
                            item['cantidad'] += 1
                            encontrado = True
                        else:
                            lanzar_alerta(f"Stock insuficiente para agregar más '{producto_db[1]}'.")
                            encontrado = True
                        break
                
                if not encontrado:
                    carrito_compras.append({
                        "codigo": producto_db[0],
                        "nombre": producto_db[1],
                        "precio": producto_db[2],
                        "cantidad": 1,
                        "stock_max": stock_real
                    })
                
                txt_codigo.value = ""
                actualizar_tabla()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ Producto no encontrado"), bgcolor="orange", open=True)
                page.update()

        def agregar_desde_input(e):
            procesar_producto(txt_codigo.value)

        def abrir_catalogo(e):
            productos = obtener_productos()
            tabla_catalogo.rows.clear()
            
            for p in productos:
                btn_add = ft.IconButton(
                    icon="add_shopping_cart", 
                    icon_color="green", 
                    tooltip="Agregar al Ticket",
                    on_click=lambda e, cod=p[0]: [procesar_producto(cod), cerrar_catalogo(None)] 
                )

                tabla_catalogo.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(p[0])), 
                        ft.DataCell(ft.Text(p[1])), 
                        ft.DataCell(ft.Text(f"${p[2]}")),
                        ft.DataCell(ft.Text(str(p[3]))),
                        ft.DataCell(btn_add)
                    ])
                )
            
            dialogo_catalogo.open = True
            page.update()

        def finalizar_venta(e):
            if not carrito_compras: return
            total_final = sum(item['precio'] * item['cantidad'] for item in carrito_compras)
            
            if realizar_venta(carrito_compras, total_final, usuario_nombre):
                generar_ticket(carrito_compras, total_final, usuario_nombre)
                page.snack_bar = ft.SnackBar(ft.Text(f"✅ Venta registrada: ${total_final}"), bgcolor="green", open=True)
                carrito_compras.clear()
                actualizar_tabla()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ Error al guardar venta"), bgcolor="red", open=True)
            page.update()

        txt_codigo = ft.TextField(
            label="Buscar producto (Código o Nombre)...", 
            width=400, 
            autofocus=True, 
            on_submit=agregar_desde_input,
            border_radius=10,
            prefix_icon="search"
        )
        
        btn_catalogo = ft.ElevatedButton(
            "Ver Productos",
            icon="list",
            bgcolor="blue",
            color="white",
            height=50,
            on_click=abrir_catalogo
        )
        
        btn_cobrar = ft.ElevatedButton(
            "COBRAR TICKET", 
            icon="check", 
            bgcolor="green", 
            color="white", 
            height=50, 
            width=200, 
            on_click=finalizar_venta
        )

        header = ft.Row([ft.IconButton(icon="arrow_back", on_click=lambda _: mostrar_dashboard(usuario_nombre)), ft.Text("Punto de Venta", size=30, weight="bold")], alignment="start")
        
        panel_total = ft.Container(
            content=ft.Column([ft.Text("Total a Pagar:", size=16), txt_total], alignment="center", horizontal_alignment="end"),
            padding=10, border=ft.border.all(1, "green"), border_radius=10
        )

        page.add(
            header, 
            ft.Divider(),
            ft.Row([
                ft.Row([txt_codigo, btn_catalogo]), 
                panel_total
            ], alignment="spaceBetween"),
            ft.Divider(), 
            tabla_ventas,
            ft.Divider(height=20, color="transparent"),
            ft.Row([btn_cobrar], alignment="end")
        )

    # ---------------------------------------------------------
    # PANTALLA 3: INVENTARIO 
    # ---------------------------------------------------------
    def mostrar_inventario(usuario_nombre):
        page.clean()
        page.overlay.clear()
        
        input_pass_stock = ft.TextField(label="Contraseña Admin", password=True, can_reveal_password=True)
        input_cant_stock = ft.TextField(label="Cantidad a Agregar", keyboard_type="number")
        input_pass_eliminar = ft.TextField(label="Contraseña Admin", password=True, can_reveal_password=True)
        input_edit_nombre = ft.TextField(label="Nuevo Nombre")
        input_edit_precio = ft.TextField(label="Nuevo Precio", keyboard_type="number")
        input_pass_edit = ft.TextField(label="Contraseña Admin", password=True, can_reveal_password=True)
        codigo_seleccionado = [""]

        def cerrar_dialogos(e):
            dialogo_stock.open = False
            dialogo_eliminar.open = False
            dialogo_editar.open = False
            page.update()

        def confirmar_stock(e):
            if validar_admin(input_pass_stock.value):
                sumar_stock(codigo_seleccionado[0], int(input_cant_stock.value or 0))
                page.snack_bar = ft.SnackBar(ft.Text("✅ Stock Actualizado"), bgcolor="green", open=True); cerrar_dialogos(None); cargar()
            else: page.snack_bar = ft.SnackBar(ft.Text("❌ Contraseña Incorrecta"), bgcolor="red", open=True); page.update()

        def confirmar_eliminar(e):
            if validar_admin(input_pass_eliminar.value):
                eliminar_producto(codigo_seleccionado[0])
                page.snack_bar = ft.SnackBar(ft.Text("🗑️ Producto Eliminado"), bgcolor="green", open=True); cerrar_dialogos(None); cargar()
            else: page.snack_bar = ft.SnackBar(ft.Text("❌ Contraseña Incorrecta"), bgcolor="red", open=True); page.update()

        def confirmar_edicion(e):
            if validar_admin(input_pass_edit.value):
                if editar_producto(codigo_seleccionado[0], input_edit_nombre.value, float(input_edit_precio.value or 0)):
                    page.snack_bar = ft.SnackBar(ft.Text("✅ Producto Editado"), bgcolor="green", open=True); cerrar_dialogos(None); cargar()
                else: page.snack_bar = ft.SnackBar(ft.Text("⚠️ Error al editar"), bgcolor="orange", open=True); page.update()
            else: page.snack_bar = ft.SnackBar(ft.Text("❌ Contraseña Incorrecta"), bgcolor="red", open=True); page.update()

        dialogo_stock = ft.AlertDialog(title=ft.Text("Rellenar Stock"), content=ft.Column([input_cant_stock, input_pass_stock], height=150), actions=[ft.ElevatedButton("CONFIRMAR", bgcolor="blue", color="white", on_click=confirmar_stock)])
        dialogo_eliminar = ft.AlertDialog(title=ft.Text("⚠️ Eliminar Producto"), content=ft.Column([ft.Text("¿Seguro que deseas eliminarlo?"), input_pass_eliminar], height=100), actions=[ft.ElevatedButton("ELIMINAR", bgcolor="red", color="white", on_click=confirmar_eliminar)])
        dialogo_editar = ft.AlertDialog(title=ft.Text("Editar Producto ✏️"), content=ft.Column([input_edit_nombre, input_edit_precio, input_pass_edit], height=220), actions=[ft.ElevatedButton("GUARDAR CAMBIOS", bgcolor="green", color="white", on_click=confirmar_edicion)])
        page.overlay.extend([dialogo_stock, dialogo_eliminar, dialogo_editar])

        def abrir_stock(cod): codigo_seleccionado[0] = cod; input_pass_stock.value = ""; input_cant_stock.value = ""; dialogo_stock.open = True; page.update()
        def abrir_eliminar(cod): codigo_seleccionado[0] = cod; input_pass_eliminar.value = ""; dialogo_eliminar.open = True; page.update()
        def abrir_editar(cod, nom, prec): codigo_seleccionado[0] = cod; input_edit_nombre.value = nom; input_edit_precio.value = str(prec); input_pass_edit.value = ""; dialogo_editar.open = True; page.update()

        txt_codigo = ft.TextField(label="Código", width=150, border_radius=10)
        txt_nombre = ft.TextField(label="Nombre", width=300, border_radius=10)
        txt_precio = ft.TextField(label="Precio", width=100, keyboard_type="number", border_radius=10)
        txt_stock = ft.TextField(label="Stock", width=100, keyboard_type="number", border_radius=10)
        
        tabla = ft.DataTable(columns=[ft.DataColumn(ft.Text("Código")), ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Precio")), ft.DataColumn(ft.Text("Stock")), ft.DataColumn(ft.Text("Acciones"))], rows=[])

        def cargar():
            datos = obtener_productos(); tabla.rows.clear()
            for p in datos:
                btn_editar = ft.IconButton(icon="edit", icon_color="blue", tooltip="Editar", on_click=lambda e, c=p[0], n=p[1], pr=p[2]: abrir_editar(c, n, pr))
                btn_stock = ft.IconButton(icon="add_circle", icon_color="green", tooltip="Sumar Stock", on_click=lambda e, c=p[0]: abrir_stock(c))
                btn_eliminar = ft.IconButton(icon="delete", icon_color="red", tooltip="Eliminar", on_click=lambda e, c=p[0]: abrir_eliminar(c))
                tabla.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(p[0])), ft.DataCell(ft.Text(p[1])), ft.DataCell(ft.Text(f"${p[2]}")), ft.DataCell(ft.Text(str(p[3]))), ft.DataCell(ft.Row([btn_editar, btn_stock, btn_eliminar]))]))
            page.update()

        def guardar(e):
            if registrar_producto(txt_codigo.value, txt_nombre.value, float(txt_precio.value or 0), int(txt_stock.value or 0)): page.snack_bar = ft.SnackBar(ft.Text("✅ Producto Creado"), bgcolor="green", open=True); txt_codigo.value=""; txt_nombre.value=""; txt_precio.value=""; txt_stock.value=""; cargar()
            else: page.snack_bar = ft.SnackBar(ft.Text("⚠️ Código repetido"), bgcolor="orange", open=True); page.update()

        page.add(ft.Row([ft.IconButton(icon="arrow_back", on_click=lambda _: mostrar_dashboard(usuario_nombre)), ft.Text("Gestión de Inventario", size=30, weight="bold")]), ft.Divider(), ft.Text("Agregar Nuevo Producto:", size=16, weight="bold"), ft.Row([txt_codigo, txt_nombre, txt_precio, txt_stock, ft.ElevatedButton("GUARDAR", icon="save", on_click=guardar, bgcolor="green", color="white")], wrap=True), ft.Divider(), tabla); cargar()

    # ---------------------------------------------------------
    # PANTALLA 5: REPORTES 
    # ---------------------------------------------------------
    def mostrar_reportes(usuario_nombre):
        page.clean(); page.overlay.clear()
        tabla_detalle = ft.DataTable(columns=[ft.DataColumn(ft.Text("Prod")), ft.DataColumn(ft.Text("Cant")), ft.DataColumn(ft.Text("Total"))], rows=[])
        def cerrar_dialogo(e): dialogo_detalle.open = False; page.update()
        dialogo_detalle = ft.AlertDialog(title=ft.Text("Detalle del Ticket"), content=ft.Column([tabla_detalle], height=300, scroll="auto"), actions=[ft.TextButton("Cerrar", on_click=cerrar_dialogo)])
        page.overlay.append(dialogo_detalle)

        def ver_detalle(id_venta):
            productos = obtener_detalle_venta(id_venta); tabla_detalle.rows.clear()
            for p in productos: tabla_detalle.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(p[0])), ft.DataCell(ft.Text(str(p[1]))), ft.DataCell(ft.Text(f"${p[3]:.2f}"))]))
            dialogo_detalle.open = True; page.update()

        tabla_ventas = ft.DataTable(columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Total")), ft.DataColumn(ft.Text("Ver"))], rows=[])
        ventas = obtener_ventas(); total_ingresos = 0
        for v in ventas:
            total_ingresos += v[2]
            tabla_ventas.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(v[0]))), ft.DataCell(ft.Text(v[1])), ft.DataCell(ft.Text(f"${v[2]:.2f}", color="green", weight="bold")), ft.DataCell(ft.IconButton(icon="visibility", icon_color="blue", on_click=lambda e, x=v[0]: ver_detalle(x)))]))
        
        card_total = ft.Container(content=ft.Column([ft.Text("TOTAL INGRESOS", size=15), ft.Text(f"${total_ingresos:.2f}", size=40, weight="bold", color="green")], alignment="center"), padding=20, border=ft.border.all(1, "green"), border_radius=15, bgcolor="#1A2E20")
        page.add(ft.Row([ft.IconButton(icon="arrow_back", on_click=lambda _: mostrar_dashboard(usuario_nombre)), ft.Text("Reportes Financieros", size=30, weight="bold")]), ft.Divider(), ft.Row([card_total], alignment="center"), ft.Divider(), ft.Column([tabla_ventas], scroll="auto", height=400))

    # ---------------------------------------------------------
    # PANTALLA 2: DASHBOARD 
    # ---------------------------------------------------------
    def mostrar_dashboard(usuario_nombre):
        page.clean()
        def crear_boton_menu(texto, icono, color_fondo, funcion):
            return ft.Container(content=ft.Column([ft.Icon(name=icono, size=50, color="white"), ft.Text(texto, size=20, weight="bold", color="white")], alignment="center", horizontal_alignment="center"), width=200, height=200, bgcolor=color_fondo, border_radius=20, on_click=funcion, padding=20, ink=True)
        header = ft.AppBar(title=ft.Text(f"Bienvenido, {usuario_nombre}", weight="bold"), bgcolor="blue", center_title=False, actions=[ft.IconButton(icon="logout", tooltip="Cerrar Sesión", on_click=lambda _: mostrar_login())])
        contenedor_botones = ft.Row([crear_boton_menu("NUEVA VENTA", "shopping_cart", "green", lambda e: mostrar_ventas(usuario_nombre)), crear_boton_menu("INVENTARIO", "inventory", "orange", lambda e: mostrar_inventario(usuario_nombre)), crear_boton_menu("REPORTES", "assessment", "purple", lambda e: mostrar_reportes(usuario_nombre))], alignment="center", wrap=True)
        page.add(header, ft.Divider(height=50, color="transparent"), contenedor_botones)

    # ---------------------------------------------------------
    # PANTALLA 1: LOGIN 
    # ---------------------------------------------------------
    def mostrar_login():
        page.clean(); page.vertical_alignment = "center"; page.horizontal_alignment = "center"
        def validar_login(e):
            con = crear_conexion()
            if con:
                cursor = con.cursor()
                cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND password = ?", (campo_usuario.value, campo_password.value))
                res = cursor.fetchone(); con.close()
                if res: mostrar_dashboard(res[3])
                else: page.snack_bar = ft.SnackBar(ft.Text("❌ Datos incorrectos"), bgcolor="red", open=True); page.update()
        campo_usuario = ft.TextField(label="Usuario", width=300, icon="person", border_radius=10)
        campo_password = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True, icon="key", border_radius=10)
        boton_ingresar = ft.ElevatedButton(text="INGRESAR", width=300, height=50, on_click=validar_login, style=ft.ButtonStyle(bgcolor="blue", color="white", shape=ft.RoundedRectangleBorder(radius=10)))
        tarjeta_login = ft.Container(content=ft.Column([ft.Icon(name="lock_person", size=80, color="blue"), ft.Text("Iniciar Sesión", size=30, weight="bold"), ft.Divider(height=20, color="transparent"), campo_usuario, campo_password, ft.Divider(height=20, color="transparent"), boton_ingresar], alignment="center", horizontal_alignment="center"), width=400, height=500, padding=30, border_radius=20, border=ft.border.all(1, "grey"), bgcolor="#1AFFFFFF")
        page.add(tarjeta_login)

    mostrar_login()

ft.app(target=main)
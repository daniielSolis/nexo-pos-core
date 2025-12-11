import flet as ft
import os
import datetime
from data.database import (crear_conexion, registrar_producto, obtener_productos, 
                           buscar_producto, realizar_venta, obtener_ventas, 
                           obtener_detalle_venta, sumar_stock, eliminar_producto, validar_admin)

def main(page: ft.Page):
    page.title = "NEXO POS"
    page.theme_mode = "dark"
    page.padding = 20

    carrito_compras = []

    # --- FUNCIÓN NUEVA: IMPRESORA DE TICKETS  ---
    def generar_ticket(items, total, vendedor):
        # 1. Crear carpeta si no existe
        if not os.path.exists("tickets"):
            os.makedirs("tickets")

        # 2. Definir nombre del archivo (con fecha y hora exacta)
        fecha_actual = datetime.datetime.now()
        nombre_archivo = f"tickets/ticket_{fecha_actual.strftime('%Y%m%d_%H%M%S')}.txt"

        # 3. Diseñar el contenido del ticket
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
            # Formato: 2 de CocaCola... $30.00
            # Usamos trucos de texto para alinear columnas
            texto += f"{item['cantidad']} x {item['nombre'][:15]:<15} ${subtotal:.2f}\n"

        texto += "-"*32 + "\n"
        texto += f"TOTAL A PAGAR:      ${total:.2f}\n"
        texto += linea
        texto += "    ¡GRACIAS POR SU COMPRA!\n"
        texto += linea

        # 4. Guardar el archivo
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(texto)

        # 5. ¡ABRIR EL TICKET AUTOMÁTICAMENTE! (Simular impresión)
        try:
            os.startfile(nombre_archivo) # Funciona en Windows
        except:
            pass # Si falla en Mac/Linux no importa, el archivo ya se guardó

    # ---------------------------------------------------------
    # PANTALLA 4: PUNTO DE VENTA
    # ---------------------------------------------------------
    def mostrar_ventas(usuario_nombre):
        page.clean()
        page.overlay.clear()
        carrito_compras.clear()
        
        # Alertas
        txt_mensaje_alerta = ft.Text("", size=18)
        def cerrar_alerta(e): dialogo_alerta.open = False; page.update()
        dialogo_alerta = ft.AlertDialog(title=ft.Row([ft.Icon("warning", color="red"), ft.Text("¡STOCK INSUFICIENTE!")]), content=txt_mensaje_alerta, actions=[ft.TextButton("ENTENDIDO", on_click=cerrar_alerta)], actions_alignment="center")
        page.overlay.append(dialogo_alerta)
        def lanzar_alerta(msg): txt_mensaje_alerta.value = msg; dialogo_alerta.open = True; page.update()

        txt_total = ft.Text("$0.00", size=40, weight="bold", color="green")
        tabla_ventas = ft.DataTable(columns=[ft.DataColumn(ft.Text("Producto")), ft.DataColumn(ft.Text("Precio")), ft.DataColumn(ft.Text("Cantidad")), ft.DataColumn(ft.Text("Subtotal")), ft.DataColumn(ft.Text("Borrar"))], rows=[])

        def actualizar_tabla():
            tabla_ventas.rows.clear(); total_general = 0
            for i, item in enumerate(carrito_compras):
                subtotal = item['precio'] * item['cantidad']; total_general += subtotal
                celda_cantidad = ft.Row([ft.IconButton(icon="remove_circle_outline", icon_color="red", on_click=lambda e, x=i: restar_cantidad(x)), ft.Text(str(item['cantidad']), weight="bold", size=16), ft.IconButton(icon="add_circle_outline", icon_color="green", on_click=lambda e, x=i: sumar_cantidad(x))], alignment="center")
                tabla_ventas.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(item['nombre'])), ft.DataCell(ft.Text(f"${item['precio']}")), ft.DataCell(celda_cantidad), ft.DataCell(ft.Text(f"${subtotal:.2f}")), ft.DataCell(ft.IconButton(icon="delete", icon_color="grey", on_click=lambda e, x=i: eliminar_item(x)))]))
            txt_total.value = f"${total_general:.2f}"; txt_codigo.focus(); page.update()

        def sumar_cantidad(i):
            item = carrito_compras[i]
            if item['cantidad'] < item['stock_max']: item['cantidad'] += 1; actualizar_tabla()
            else: lanzar_alerta(f"Solo tienes {item['stock_max']} unidades de '{item['nombre']}' en el inventario.")
        def restar_cantidad(i):
            if carrito_compras[i]['cantidad'] > 1: carrito_compras[i]['cantidad'] -= 1; actualizar_tabla()
        def eliminar_item(i): del carrito_compras[i]; actualizar_tabla()

        def agregar_producto(e):
            criterio = txt_codigo.value; 
            if not criterio: return
            prod = buscar_producto(criterio)
            if prod:
                stock_real = prod[3]
                if stock_real <= 0: lanzar_alerta(f"¡El producto '{prod[1]}' está AGOTADO!"); txt_codigo.value=""; page.update(); return
                
                encontrado = False
                for item in carrito_compras:
                    if item['codigo'] == prod[0]:
                        if item['cantidad'] + 1 <= stock_real: item['cantidad'] += 1; encontrado = True
                        else: lanzar_alerta(f"No puedes agregar más '{prod[1]}'. Stock: {stock_real}"); encontrado = True; txt_codigo.value=""; page.update()
                        break
                if not encontrado: carrito_compras.append({"codigo": prod[0], "nombre": prod[1], "precio": prod[2], "cantidad": 1, "stock_max": stock_real})
                txt_codigo.value=""; actualizar_tabla()
            else: page.snack_bar = ft.SnackBar(ft.Text("❌ No encontrado"), bgcolor="orange", open=True); page.update()

        def finalizar_venta(e):
            if not carrito_compras: return
            total_final = sum(item['precio'] * item['cantidad'] for item in carrito_compras)
            
            if realizar_venta(carrito_compras, total_final, usuario_nombre):
                # --- AQUÍ GENERAMOS EL TICKET ---
                generar_ticket(carrito_compras, total_final, usuario_nombre)
                # --------------------------------
                
                page.snack_bar = ft.SnackBar(ft.Text(f"✅ Venta Exitosa: ${total_final}"), bgcolor="green", open=True)
                carrito_compras.clear()
                actualizar_tabla()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ Error al procesar venta"), bgcolor="red", open=True)
            page.update()

        txt_codigo = ft.TextField(label="Buscar producto...", width=400, autofocus=True, on_submit=agregar_producto, border_radius=10, prefix_icon="search")
        btn_cobrar = ft.ElevatedButton("COBRAR TICKET", icon="check", bgcolor="green", color="white", height=50, width=200, on_click=finalizar_venta)
        page.add(ft.Row([ft.IconButton(icon="arrow_back", on_click=lambda _: mostrar_dashboard(usuario_nombre)), ft.Text("Punto de Venta", size=30, weight="bold")]), ft.Divider(), ft.Row([txt_codigo, ft.Container(content=ft.Column([ft.Text("Total:"), txt_total]), padding=10, border=ft.border.all(1, "green"), border_radius=10)], alignment="spaceBetween"), ft.Divider(), tabla_ventas, ft.Divider(height=20, color="transparent"), ft.Row([btn_cobrar], alignment="end"))

    # ---------------------------------------------------------
    # PANTALLA 3: INVENTARIO (CON SEGURIDAD)
    # ---------------------------------------------------------
    def mostrar_inventario(usuario_nombre):
        page.clean(); page.overlay.clear() 
        input_pass_stock = ft.TextField(label="Contraseña Admin", password=True, can_reveal_password=True)
        input_cant_stock = ft.TextField(label="Cantidad a Agregar", keyboard_type="number")
        codigo_seleccionado = [""] 
        input_pass_eliminar = ft.TextField(label="Contraseña Admin", password=True, can_reveal_password=True)

        def cerrar_dialogos(e): dialogo_stock.open = False; dialogo_eliminar.open = False; page.update()
        def confirmar_stock(e):
            if not validar_admin(input_pass_stock.value): input_pass_stock.error_text = "Incorrecto"; page.update(); return
            if sumar_stock(codigo_seleccionado[0], int(input_cant_stock.value or 0)): page.snack_bar = ft.SnackBar(ft.Text("✅ Stock Actualizado"), bgcolor="green", open=True); dialogo_stock.open = False; input_pass_stock.value = ""; input_cant_stock.value = ""; input_pass_stock.error_text = None; cargar()
            else: page.snack_bar = ft.SnackBar(ft.Text("❌ Error"), bgcolor="red", open=True); page.update()
        def confirmar_eliminar(e):
            if not validar_admin(input_pass_eliminar.value): input_pass_eliminar.error_text = "Incorrecto"; page.update(); return
            if eliminar_producto(codigo_seleccionado[0]): page.snack_bar = ft.SnackBar(ft.Text("🗑️ Eliminado"), bgcolor="green", open=True); dialogo_eliminar.open = False; input_pass_eliminar.value = ""; input_pass_eliminar.error_text = None; cargar()
            else: page.snack_bar = ft.SnackBar(ft.Text("❌ Error"), bgcolor="red", open=True); page.update()

        dialogo_stock = ft.AlertDialog(title=ft.Text("Rellenar Stock"), content=ft.Column([input_cant_stock, input_pass_stock], height=150), actions=[ft.TextButton("Cancelar", on_click=cerrar_dialogos), ft.ElevatedButton("CONFIRMAR", bgcolor="blue", color="white", on_click=confirmar_stock)])
        dialogo_eliminar = ft.AlertDialog(title=ft.Text("⚠️ Eliminar"), content=ft.Column([ft.Text("Esta acción no se puede deshacer."), input_pass_eliminar], height=100), actions=[ft.TextButton("Cancelar", on_click=cerrar_dialogos), ft.ElevatedButton("ELIMINAR", bgcolor="red", color="white", on_click=confirmar_eliminar)])
        page.overlay.append(dialogo_stock); page.overlay.append(dialogo_eliminar)
        def abrir_dialogo_stock(codigo): codigo_seleccionado[0] = codigo; input_pass_stock.value = ""; input_cant_stock.value = ""; input_pass_stock.error_text = None; dialogo_stock.open = True; page.update()
        def abrir_dialogo_eliminar(codigo): codigo_seleccionado[0] = codigo; input_pass_eliminar.value = ""; input_pass_eliminar.error_text = None; dialogo_eliminar.open = True; page.update()

        txt_codigo = ft.TextField(label="Código", width=150); txt_nombre = ft.TextField(label="Nombre", width=300); txt_precio = ft.TextField(label="Precio", width=100, keyboard_type="number"); txt_stock = ft.TextField(label="Stock Inicial", width=100, keyboard_type="number")
        tabla = ft.DataTable(columns=[ft.DataColumn(ft.Text("Código")), ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Precio")), ft.DataColumn(ft.Text("Stock")), ft.DataColumn(ft.Text("Acciones"))], rows=[])
        def cargar():
            datos = obtener_productos(); tabla.rows.clear()
            for p in datos:
                btn_sumar = ft.IconButton(icon="add_circle", icon_color="blue", on_click=lambda e, c=p[0]: abrir_dialogo_stock(c))
                btn_eliminar = ft.IconButton(icon="delete", icon_color="red", on_click=lambda e, c=p[0]: abrir_dialogo_eliminar(c))
                tabla.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(p[0])), ft.DataCell(ft.Text(p[1])), ft.DataCell(ft.Text(f"${p[2]}")), ft.DataCell(ft.Text(str(p[3]))), ft.DataCell(ft.Row([btn_sumar, btn_eliminar]))]))
            page.update()
        def guardar(e):
            if registrar_producto(txt_codigo.value, txt_nombre.value, float(txt_precio.value or 0), int(txt_stock.value or 0)): page.snack_bar = ft.SnackBar(ft.Text("✅ Creado"), bgcolor="green", open=True); txt_codigo.value=""; txt_nombre.value=""; txt_precio.value=""; txt_stock.value=""; cargar()
            else: page.snack_bar = ft.SnackBar(ft.Text("⚠️ Código repetido"), bgcolor="orange", open=True); page.update()
        page.add(ft.Row([ft.IconButton(icon="arrow_back", on_click=lambda _: mostrar_dashboard(usuario_nombre)), ft.Text("Inventario", size=30, weight="bold")]), ft.Divider(), ft.Text("Crear Nuevo:", weight="bold"), ft.Row([txt_codigo, txt_nombre, txt_precio, txt_stock, ft.ElevatedButton("Crear", on_click=guardar, bgcolor="green", color="white")], wrap=True), ft.Divider(), ft.Text("Lista:", weight="bold"), tabla); cargar()

    # ---------------------------------------------------------
    # PANTALLA 5: REPORTES
    # ---------------------------------------------------------
    def mostrar_reportes(usuario_nombre):
        page.clean()
        tabla_detalle = ft.DataTable(columns=[ft.DataColumn(ft.Text("Prod")), ft.DataColumn(ft.Text("Cant")), ft.DataColumn(ft.Text("Total"))], rows=[])
        def cerrar_dialogo(e): dialogo_detalle.open = False; page.update()
        dialogo_detalle = ft.AlertDialog(title=ft.Text("Detalle del Ticket"), content=ft.Column([tabla_detalle], height=300, scroll="auto"), actions=[ft.TextButton("Cerrar", on_click=cerrar_dialogo)])
        page.overlay.append(dialogo_detalle)
        def ver_detalle(id_venta):
            productos = obtener_detalle_venta(id_venta); tabla_detalle.rows.clear()
            for p in productos: tabla_detalle.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(p[0])), ft.DataCell(ft.Text(str(p[1]))), ft.DataCell(ft.Text(f"${p[3]:.2f}"))]))
            dialogo_detalle.open = True; page.update() 
        tabla_ventas = ft.DataTable(columns=[ft.DataColumn(ft.Text("ID")), ft.DataColumn(ft.Text("Fecha")), ft.DataColumn(ft.Text("Vendedor")), ft.DataColumn(ft.Text("Total")), ft.DataColumn(ft.Text("Ver"))], rows=[])
        ventas = obtener_ventas(); total_ingresos = 0
        for v in ventas:
            total_ingresos += v[2]
            tabla_ventas.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(str(v[0]))), ft.DataCell(ft.Text(v[1])), ft.DataCell(ft.Text(v[3])), ft.DataCell(ft.Text(f"${v[2]:.2f}", color="green", weight="bold")), ft.DataCell(ft.IconButton(icon="visibility", icon_color="blue", on_click=lambda e, x=v[0]: ver_detalle(x)))]))
        card_total = ft.Container(content=ft.Column([ft.Text("VENTAS TOTALES", size=15, color="white"), ft.Text(f"${total_ingresos:.2f}", size=40, weight="bold", color="green")], alignment="center"), padding=20, border=ft.border.all(1, "green"), border_radius=15, bgcolor="#1A2E20")
        page.add(ft.Row([ft.IconButton(icon="arrow_back", on_click=lambda _: mostrar_dashboard(usuario_nombre)), ft.Text("Historial de Ventas", size=30, weight="bold")]), ft.Divider(), ft.Row([card_total], alignment="center"), ft.Divider(), ft.Column([tabla_ventas], scroll="auto", height=400))

    # ---------------------------------------------------------
    # PANTALLA 2: DASHBOARD
    # ---------------------------------------------------------
    def mostrar_dashboard(usuario_nombre):
        page.clean()
        def crear_boton(texto, icono, color, accion): return ft.Container(content=ft.Column([ft.Icon(icono, size=50, color="white"), ft.Text(texto, color="white", weight="bold")], alignment="center", horizontal_alignment="center"), width=180, height=180, bgcolor=color, border_radius=20, padding=20, ink=True, on_click=accion)
        page.add(ft.AppBar(title=ft.Text(f"Hola, {usuario_nombre}"), bgcolor="blue", actions=[ft.IconButton(icon="logout", on_click=lambda _: mostrar_login())]), ft.Divider(height=20, color="transparent"), ft.Row([crear_boton("NUEVA VENTA", "shopping_cart", "green", lambda e: mostrar_ventas(usuario_nombre)), crear_boton("INVENTARIO", "inventory", "orange", lambda e: mostrar_inventario(usuario_nombre)), crear_boton("REPORTES", "assessment", "purple", lambda e: mostrar_reportes(usuario_nombre))], alignment="center", wrap=True))

    # ---------------------------------------------------------
    # PANTALLA 1: LOGIN
    # ---------------------------------------------------------
    def mostrar_login():
        page.clean(); page.vertical_alignment = "center"; page.horizontal_alignment = "center"
        def validar(e):
            con = crear_conexion()
            if con:
                cursor = con.cursor()
                cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND password = ?", (user.value, pwd.value))
                res = cursor.fetchone(); con.close()
                if res: mostrar_dashboard(res[3])
                else: page.snack_bar = ft.SnackBar(ft.Text("❌ Error"), bgcolor="red", open=True); page.update()
        user = ft.TextField(label="Usuario", width=300); pwd = ft.TextField(label="Contraseña", width=300, password=True)
        page.add(ft.Container(content=ft.Column([ft.Icon("lock", size=60, color="blue"), ft.Text("NEXO POS", size=25), user, pwd, ft.ElevatedButton("ENTRAR", width=300, on_click=validar, bgcolor="blue", color="white")], alignment="center"), padding=30, border=ft.border.all(1, "grey"), border_radius=20, bgcolor="#1AFFFFFF"))

    mostrar_login()

ft.app(target=main)
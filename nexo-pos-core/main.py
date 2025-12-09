import flet as ft
from data.database import crear_conexion, registrar_producto, obtener_productos, buscar_producto, realizar_venta

def main(page: ft.Page):
    page.title = "NEXO POS"
    page.theme_mode = "dark"
    page.padding = 20

    carrito_compras = []

    # ---------------------------------------------------------
    # PANTALLA 4: PUNTO DE VENTA 
    # ---------------------------------------------------------
    def mostrar_ventas(usuario_nombre):
        page.clean()
        carrito_compras.clear()

        txt_total = ft.Text("$0.00", size=40, weight="bold", color="green")
        
        # Tabla con columna de CANTIDAD editable
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
                
                # Celdas con botones de + y -
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
                        ft.DataCell(celda_cantidad), # La celda especial
                        ft.DataCell(ft.Text(f"${subtotal:.2f}")),
                        ft.DataCell(ft.IconButton(icon="delete", icon_color="grey", on_click=lambda e, x=i: eliminar_item(x)))
                    ])
                )
            
            txt_total.value = f"${total_general:.2f}"
            txt_codigo.focus()
            page.update()

        # --- Lógica de los botones ---
        def sumar_cantidad(indice):
            carrito_compras[indice]['cantidad'] += 1
            actualizar_tabla()

        def restar_cantidad(indice):
            if carrito_compras[indice]['cantidad'] > 1:
                carrito_compras[indice]['cantidad'] -= 1
            else:
                # Si llega a 0, ¿lo borramos? Mejor preguntamos o lo dejamos en 1
                # Por ahora dejémoslo en 1 para no borrar por error
                pass 
            actualizar_tabla()

        def eliminar_item(indice):
            del carrito_compras[indice]
            actualizar_tabla()

        def agregar_producto(e):
            criterio = txt_codigo.value
            if not criterio: return

            producto_db = buscar_producto(criterio) # Busca por Código O Nombre
            
            if producto_db:
                # Lógica: Si ya existe, sumamos 1. Si no, agregamos.
                encontrado = False
                for item in carrito_compras:
                    if item['codigo'] == producto_db[0]:
                        item['cantidad'] += 1
                        encontrado = True
                        break
                
                if not encontrado:
                    carrito_compras.append({
                        "codigo": producto_db[0],
                        "nombre": producto_db[1],
                        "precio": producto_db[2],
                        "cantidad": 1
                    })
                
                txt_codigo.value = ""
                actualizar_tabla()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ No encontrado (Intenta con código o nombre)"), bgcolor="orange", open=True)
                page.update()

        def finalizar_venta(e):
            if not carrito_compras: return
            total_final = sum(item['precio'] * item['cantidad'] for item in carrito_compras)
            
            if realizar_venta(carrito_compras, total_final, usuario_nombre):
                page.snack_bar = ft.SnackBar(ft.Text(f"✅ Venta: ${total_final}"), bgcolor="green", open=True)
                carrito_compras.clear()
                actualizar_tabla()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("❌ Error al guardar"), bgcolor="red", open=True)
            page.update()

        txt_codigo = ft.TextField(
            label="Buscar por Código o Nombre...", 
            width=400, 
            autofocus=True, 
            on_submit=agregar_producto,
            border_radius=10,
            prefix_icon="search"
        )
        
        btn_cobrar = ft.ElevatedButton("COBRAR", icon="check", bgcolor="green", color="white", height=50, width=200, on_click=finalizar_venta)
        
        page.add(
            ft.Row([ft.IconButton(icon="arrow_back", on_click=lambda _: mostrar_dashboard(usuario_nombre)), ft.Text("Punto de Venta", size=30, weight="bold")]), 
            ft.Divider(),
            ft.Row([txt_codigo, ft.Container(content=ft.Column([ft.Text("Total:", size=15), txt_total]), padding=10, border=ft.border.all(1, "green"), border_radius=10)], alignment="spaceBetween"),
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
        
        txt_codigo = ft.TextField(label="Código", width=150)
        txt_nombre = ft.TextField(label="Nombre", width=300)
        txt_precio = ft.TextField(label="Precio", width=100, keyboard_type="number")
        txt_stock = ft.TextField(label="Stock", width=100, keyboard_type="number")

        tabla_productos = ft.DataTable(columns=[ft.DataColumn(ft.Text("Código")), ft.DataColumn(ft.Text("Nombre")), ft.DataColumn(ft.Text("Precio")), ft.DataColumn(ft.Text("Stock"))], rows=[])

        def cargar_datos_tabla():
            datos = obtener_productos()
            tabla_productos.rows.clear()
            for prod in datos:
                tabla_productos.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text(prod[0])), ft.DataCell(ft.Text(prod[1])), ft.DataCell(ft.Text(f"${prod[2]}")), ft.DataCell(ft.Text(str(prod[3])))]))
            page.update()

        def guardar_producto(e):
            if registrar_producto(txt_codigo.value, txt_nombre.value, float(txt_precio.value or 0), int(txt_stock.value or 0)):
                page.snack_bar = ft.SnackBar(ft.Text("✅ Guardado"), bgcolor="green", open=True)
                txt_codigo.value = ""; txt_nombre.value = ""; txt_precio.value = ""; txt_stock.value = ""
                cargar_datos_tabla()
            else:
                page.snack_bar = ft.SnackBar(ft.Text("⚠️ Código repetido"), bgcolor="orange", open=True)
            page.update()

        page.add(
            ft.Row([ft.IconButton(icon="arrow_back", on_click=lambda _: mostrar_dashboard(usuario_nombre)), ft.Text("Inventario", size=30, weight="bold")]),
            ft.Divider(),
            ft.Row([txt_codigo, txt_nombre, txt_precio, txt_stock, ft.ElevatedButton("Guardar", on_click=guardar_producto, bgcolor="green", color="white")], wrap=True),
            ft.Divider(),
            tabla_productos
        )
        cargar_datos_tabla()

    # ---------------------------------------------------------
    # PANTALLA 2: DASHBOARD
    # ---------------------------------------------------------
    def mostrar_dashboard(usuario_nombre):
        page.clean()
        def crear_boton(texto, icono, color, accion):
            return ft.Container(content=ft.Column([ft.Icon(icono, size=50, color="white"), ft.Text(texto, color="white", weight="bold")], alignment="center", horizontal_alignment="center"), width=180, height=180, bgcolor=color, border_radius=20, padding=20, ink=True, on_click=accion)
        
        page.add(
            ft.AppBar(title=ft.Text(f"Hola, {usuario_nombre}"), bgcolor="blue", actions=[ft.IconButton(icon="logout", on_click=lambda _: mostrar_login())]),
            ft.Divider(height=20, color="transparent"),
            ft.Row([crear_boton("NUEVA VENTA", "shopping_cart", "green", lambda e: mostrar_ventas(usuario_nombre)), crear_boton("INVENTARIO", "inventory", "orange", lambda e: mostrar_inventario(usuario_nombre)), crear_boton("CLIENTES", "people", "blue", lambda e: print("Clientes"))], alignment="center", wrap=True)
        )

    # ---------------------------------------------------------
    # PANTALLA 1: LOGIN
    # ---------------------------------------------------------
    def mostrar_login():
        page.clean()
        page.vertical_alignment = "center"; page.horizontal_alignment = "center"
        def validar_login(e):
            con = crear_conexion()
            if con:
                cursor = con.cursor()
                cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND password = ?", (user.value, pwd.value))
                res = cursor.fetchone()
                con.close()
                if res: mostrar_dashboard(res[3])
                else: page.snack_bar = ft.SnackBar(ft.Text("❌ Error"), bgcolor="red", open=True); page.update()
        user = ft.TextField(label="Usuario", width=300); pwd = ft.TextField(label="Contraseña", width=300, password=True)
        page.add(ft.Container(content=ft.Column([ft.Icon("lock", size=60, color="blue"), ft.Text("NEXO POS", size=25), user, pwd, ft.ElevatedButton("ENTRAR", width=300, on_click=validar_login, bgcolor="blue", color="white")], alignment="center"), padding=30, border=ft.border.all(1, "grey"), border_radius=20, bgcolor="#1AFFFFFF"))

    mostrar_login()

ft.app(target=main)
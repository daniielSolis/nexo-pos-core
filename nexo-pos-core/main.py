import flet as ft
from data.database import crear_conexion, registrar_producto, obtener_productos

def main(page: ft.Page):
    page.title = "NEXO POS"
    page.theme_mode = "dark"
    page.padding = 20

    
    # PANTALLA 3: INVENTARIO 
    def mostrar_inventario(usuario_nombre):
        page.clean()
        
        # 1. Formulario para agregar producto
        txt_codigo = ft.TextField(label="Código", width=150, border_radius=10)
        txt_nombre = ft.TextField(label="Nombre Producto", width=300, border_radius=10)
        txt_precio = ft.TextField(label="Precio", width=100, keyboard_type="number", border_radius=10)
        txt_stock = ft.TextField(label="Stock", width=100, keyboard_type="number", border_radius=10)

        # Tabla de datos
        tabla_productos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Precio ($)")),
                ft.DataColumn(ft.Text("Stock")),
            ],
            rows=[] # Aquí se llenarán los datos
        )

        def cargar_datos_tabla():
            """Consulta la BD y rellena la tabla"""
            datos = obtener_productos() # Traemos la lista de la BD
            tabla_productos.rows.clear()
            for prod in datos:
                tabla_productos.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(prod[0])), # Código
                        ft.DataCell(ft.Text(prod[1])), # Nombre
                        ft.DataCell(ft.Text(f"${prod[2]}")), # Precio
                        ft.DataCell(ft.Text(str(prod[3]))), # Stock
                    ])
                )
            page.update()

        def guardar_producto(e):
            """Toma los datos de las cajas y los manda a la BD"""
            if not txt_codigo.value or not txt_nombre.value:
                page.snack_bar = ft.SnackBar(ft.Text("❌ Faltan datos"), bgcolor="red")
                page.snack_bar.open = True
                page.update()
                return

            # Intentamos guardar
            exito = registrar_producto(
                txt_codigo.value, 
                txt_nombre.value, 
                float(txt_precio.value or 0), 
                int(txt_stock.value or 0)
            )

            if exito:
                page.snack_bar = ft.SnackBar(ft.Text("✅ Producto Agregado"), bgcolor="green")
                # Limpiar cajas
                txt_codigo.value = ""
                txt_nombre.value = ""
                txt_precio.value = ""
                txt_stock.value = ""
                cargar_datos_tabla() # Refrescar la tabla
            else:
                page.snack_bar = ft.SnackBar(ft.Text("⚠️ Error: Código repetido"), bgcolor="orange")
            
            page.snack_bar.open = True
            page.update()

        btn_guardar = ft.ElevatedButton("Guardar Producto", icon="save", on_click=guardar_producto, bgcolor="green", color="white")
        btn_volver = ft.IconButton(icon="arrow_back", tooltip="Volver al Menú", on_click=lambda _: mostrar_dashboard(usuario_nombre))

        # Título y Cabecera
        header = ft.Row([btn_volver, ft.Text("Gestión de Inventario", size=30, weight="bold")], alignment="start")
        
        # Fila del formulario
        fila_form = ft.Row([txt_codigo, txt_nombre, txt_precio, txt_stock, btn_guardar], wrap=True)

        # Armado final
        page.add(header, ft.Divider(), fila_form, ft.Divider(), tabla_productos)
        
        # Cargamos los datos al iniciar la pantalla
        cargar_datos_tabla()

    # PANTALLA 2: DASHBOARD
    def mostrar_dashboard(usuario_nombre):
        page.clean()
        
        header = ft.AppBar(
            title=ft.Text(f"Bienvenido, {usuario_nombre}", weight="bold"),
            bgcolor="blue",
            center_title=False,
            actions=[ft.IconButton(icon="logout", on_click=lambda _: mostrar_login())]
        )

        def crear_boton_menu(texto, icono, color_fondo, funcion_navegacion):
            return ft.Container(
                content=ft.Column(
                    [ft.Icon(name=icono, size=50, color="white"), ft.Text(texto, size=20, weight="bold", color="white")],
                    alignment="center", horizontal_alignment="center"
                ),
                width=200, height=200, bgcolor=color_fondo, border_radius=20, padding=20, ink=True,
                on_click=funcion_navegacion 
            )

        contenedor_botones = ft.Row(
            [
                # El botón Inventario ahora llama a mostrar_inventario
                crear_boton_menu("NUEVA VENTA", "shopping_cart", "green", lambda e: print("Ir a Venta")),
                crear_boton_menu("INVENTARIO", "inventory", "orange", lambda e: mostrar_inventario(usuario_nombre)),
                crear_boton_menu("CLIENTES", "people", "blue", lambda e: print("Ir a Clientes")),
                crear_boton_menu("REPORTES", "assessment", "purple", lambda e: print("Ir a Reportes")),
            ],
            alignment="center", wrap=True
        )

        page.add(header, ft.Divider(height=50, color="transparent"), contenedor_botones)

    # PANTALLA 1: LOGIN
    def mostrar_login():
        page.clean()
        page.vertical_alignment = "center"
        page.horizontal_alignment = "center"

        def validar_login(e):
            con = crear_conexion()
            if con:
                cursor = con.cursor()
                cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND password = ?", (campo_usuario.value, campo_password.value))
                usuario_encontrado = cursor.fetchone()
                con.close()

                if usuario_encontrado:
                    mostrar_dashboard(usuario_encontrado[3])
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("❌ Datos incorrectos"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()

        campo_usuario = ft.TextField(label="Usuario", width=300, icon="person")
        campo_password = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True, icon="key")
        boton_ingresar = ft.ElevatedButton(text="ENTRAR", width=300, height=50, on_click=validar_login, style=ft.ButtonStyle(bgcolor="blue", color="white"))
        
        page.add(ft.Container(
            content=ft.Column([ft.Icon(name="lock_person", size=80, color="blue"), ft.Text("NEXO POS", size=30, weight="bold"), campo_usuario, campo_password, boton_ingresar], alignment="center", horizontal_alignment="center"),
            width=400, height=450, padding=30, border_radius=20, border=ft.border.all(1, "grey"), bgcolor="#1AFFFFFF"
        ))

    mostrar_login()

ft.app(target=main)
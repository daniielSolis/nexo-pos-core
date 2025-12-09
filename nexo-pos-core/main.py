import flet as ft
from data.database import crear_conexion

def main(page: ft.Page):
    # --- Configuración Global 
    page.title = "NEXO POS - Sistema Profesional"
    page.theme_mode = "dark"
    page.padding = 20

    # PANTALLA 2: EL DASHBOARD (PANEL DE CONTROL)
    def mostrar_dashboard(usuario_nombre):
        page.clean() # Borramos el login
        
        # Barra superior (Header)
        header = ft.AppBar(
            title=ft.Text(f"Bienvenido, {usuario_nombre}", weight="bold"),
            bgcolor="blue",
            center_title=False,
            actions=[
                ft.IconButton(icon="logout", tooltip="Cerrar Sesión", on_click=lambda _: mostrar_login())
            ]
        )

        # Botones del Menú (Tarjetas Grandes)
        def crear_boton_menu(texto, icono, color_fondo):
            return ft.Container(
                content=ft.Column(
                    [
                        ft.Icon(name=icono, size=50, color="white"),
                        ft.Text(texto, size=20, weight="bold", color="white")
                    ],
                    alignment="center",
                    horizontal_alignment="center"
                ),
                width=200,
                height=200,
                bgcolor=color_fondo,
                border_radius=20,
                on_click=lambda e: print(f"Click en {texto}"), # Aquí luego pondremos la lógica
                padding=20,
                ink=True 
            )

        # Fila de botones
        contenedor_botones = ft.Row(
            [
                crear_boton_menu("NUEVA VENTA", "shopping_cart", "green"),
                crear_boton_menu("INVENTARIO", "inventory", "orange"),
                crear_boton_menu("CLIENTES", "people", "blue"),
                crear_boton_menu("REPORTES", "assessment", "purple"),
            ],
            alignment="center",
            wrap=True # Si no caben, bajan a la siguiente línea
        )

        page.add(header, ft.Divider(height=50, color="transparent"), contenedor_botones)

    # PANTALLA 1: EL LOGIN
    def mostrar_login():
        page.clean()
        page.vertical_alignment = "center"
        page.horizontal_alignment = "center"

        def validar_login(e):
            user = campo_usuario.value
            pwd = campo_password.value

            con = crear_conexion()
            if con:
                cursor = con.cursor()
                cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND password = ?", (user, pwd))
                usuario_encontrado = cursor.fetchone()
                con.close()

                if usuario_encontrado:
                    #  Vamos al Dashboard pasando el nombre real del usuario
                    nombre_real = usuario_encontrado[3] # Columna 'nombre' en la BD
                    mostrar_dashboard(nombre_real)
                else:
                    page.snack_bar = ft.SnackBar(ft.Text("❌ Datos incorrectos"), bgcolor="red")
                    page.snack_bar.open = True
                    page.update()

        # Elementos del Login
        logo = ft.Icon(name="lock_person", size=80, color="blue")
        campo_usuario = ft.TextField(label="Usuario", width=300, icon="person", border_radius=10)
        campo_password = ft.TextField(label="Contraseña", width=300, password=True, can_reveal_password=True, icon="key", border_radius=10)
        boton_ingresar = ft.ElevatedButton(text="ENTRAR", width=300, height=50, on_click=validar_login, style=ft.ButtonStyle(bgcolor="blue", color="white"))

        tarjeta = ft.Container(
            content=ft.Column([logo, ft.Text("Iniciar Sesión", size=25, weight="bold"), ft.Divider(height=10, color="transparent"), campo_usuario, campo_password, ft.Divider(height=20, color="transparent"), boton_ingresar], alignment="center", horizontal_alignment="center"),
            width=400, height=450, padding=30, border_radius=20, border=ft.border.all(1, "grey"), bgcolor="#1AFFFFFF"
        )
        page.add(tarjeta)

    # Arrancamos mostrando el login
    mostrar_login()

ft.app(target=main)
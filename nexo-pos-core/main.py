import flet as ft
from data.database import crear_conexion

def main(page: ft.Page):
    # --- 1. Configuración de la Ventana 
    page.title = "NEXO POS - Acceso Seguro"
    page.theme_mode = "dark"
    page.window_width = 800
    page.window_height = 600
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    # --- 2. Lógica: Función para validar usuario 
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
                # ÉXITO
                page.snack_bar = ft.SnackBar(ft.Text(f"¡Bienvenido, {usuario_encontrado[3]}! 🚀"), bgcolor="green")
                page.snack_bar.open = True
                boton_ingresar.text = "¡ACCESO CONCEDIDO!"
                boton_ingresar.disabled = True
                page.update()
            else:
                # ERROR
                page.snack_bar = ft.SnackBar(ft.Text("❌ Usuario o contraseña incorrectos"), bgcolor="red")
                page.snack_bar.open = True
                page.update()

    # --- 3. Diseño: Los elementos (Usando solo TEXTO para colores)
    logo = ft.Icon(name="lock_person", size=80, color="blue")
    titulo = ft.Text("Iniciar Sesión", size=30, weight="bold")

    campo_usuario = ft.TextField(
        label="Usuario", 
        width=300, 
        icon="person",
        border_radius=10
    )
    
    campo_password = ft.TextField(
        label="Contraseña", 
        width=300, 
        password=True, 
        can_reveal_password=True, 
        icon="key",
        border_radius=10
    )

    boton_ingresar = ft.ElevatedButton(
        text="INGRESAR",
        width=300,
        height=50,
        style=ft.ButtonStyle(
            color="white",
            bgcolor="blue",
            shape=ft.RoundedRectangleBorder(radius=10),
        ),
        on_click=validar_login
    )

    # --- 4. Armado: Tarjeta central
    tarjeta_login = ft.Container(
        content=ft.Column(
            [
                logo,
                titulo,
                ft.Divider(height=20, color="transparent"),
                campo_usuario,
                campo_password,
                ft.Divider(height=20, color="transparent"),
                boton_ingresar
            ],
            alignment="center",
            horizontal_alignment="center",
        ),
        width=400,
        height=500,
        padding=30,
        border_radius=20,
        border=ft.border.all(1, "grey"),
        bgcolor="#1AFFFFFF"
    )

    page.add(tarjeta_login)

ft.app(target=main)
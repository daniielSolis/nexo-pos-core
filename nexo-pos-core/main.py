import flet as ft

def main(page: ft.Page):
    # Configuración de la ventana
    page.title = "NEXO POS - Sistema de Punto de Venta"
    page.theme_mode = "dark"  # Cambio a texto simple
    page.window_width = 1000
    page.window_height = 700
    page.padding = 50

    # Diseño de la pantalla
    logo = ft.Icon(name="token", size=80, color="blue")
    
    titulo = ft.Text("NEXO", size=60, weight="bold")
    subtitulo = ft.Text("Tu sistema inteligente de gestión", color="grey", size=20)

    boton_inicio = ft.ElevatedButton(
        text="INICIAR SISTEMA",
        icon="rocket_launch", 
        height=50,
        width=200,
        style=ft.ButtonStyle(
            color="white",
            bgcolor="blue", # Azul estándar
            shape=ft.RoundedRectangleBorder(radius=10),
        )
    )

    
    contenido = ft.Column(
        [
            logo,
            titulo,
            subtitulo,
            ft.Divider(height=40, color="transparent"),
            boton_inicio
        ],
        alignment="center",
        horizontal_alignment="center"
    )

    page.add(contenido)

ft.app(target=main)
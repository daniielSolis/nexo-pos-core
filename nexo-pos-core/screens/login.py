"""Pantalla de Login"""
import flet as ft
from data import crear_conexion
from utils import Validators, ValidationError, Colors, Icons, Sizes, Messages

class LoginScreen:
    
    def __init__(self, page: ft.Page, on_login_success):
        self.page = page
        self.on_login_success = on_login_success
        self.campo_usuario = None
        self.campo_password = None
    
    def mostrar(self):
        self.page.clean()
        self.page.vertical_alignment = "center"
        self.page.horizontal_alignment = "center"
        
        self.campo_usuario = ft.TextField(
            label="Usuario",
            width=Sizes.INPUT_LOGIN,
            icon=Icons.USUARIO,
            border_radius=10,
            autofocus=True
        )
        
        self.campo_password = ft.TextField(
            label="Contraseña",
            width=Sizes.INPUT_LOGIN,
            password=True,
            can_reveal_password=True,
            icon=Icons.PASSWORD,
            border_radius=10,
            on_submit=self._validar_login
        )
        
        boton_ingresar = ft.ElevatedButton(
            text="INGRESAR",
            width=Sizes.INPUT_LOGIN,
            height=Sizes.BOTON_ALTO,
            on_click=self._validar_login,
            style=ft.ButtonStyle(
                bgcolor=Colors.PRIMARY,
                color=Colors.TEXT_PRIMARY,
                shape=ft.RoundedRectangleBorder(radius=10)
            )
        )
        
        tarjeta = ft.Container(
            content=ft.Column([
                ft.Icon(name=Icons.LOGIN, size=Sizes.ICONO_GRANDE, color=Colors.PRIMARY),
                ft.Text("Iniciar Sesión", size=Sizes.TITULO_GRANDE, weight="bold"),
                ft.Divider(height=20, color="transparent"),
                self.campo_usuario,
                self.campo_password,
                ft.Divider(height=20, color="transparent"),
                boton_ingresar
            ], alignment="center", horizontal_alignment="center"),
            width=400,
            height=500,
            padding=30,
            border_radius=20,
            border=ft.border.all(1, "grey"),
            bgcolor="#1AFFFFFF"
        )
        
        self.page.add(tarjeta)
    
    def _validar_login(self, e):
        try:
            usuario = Validators.validar_campo_vacio(self.campo_usuario.value, "Usuario")
            password = self.campo_password.value.strip() if self.campo_password.value else ""
            
            con = crear_conexion()
            if con:
                cursor = con.cursor()
                cursor.execute(
                    "SELECT * FROM usuarios WHERE usuario = ? AND password = ?",
                    (usuario, password)
                )
                resultado = cursor.fetchone()
                con.close()
                
                if resultado:
                    self.on_login_success(resultado[3])
                else:
                    self._mostrar_error(Messages.DATOS_INCORRECTOS)
        except ValidationError as ve:
            self._mostrar_error(str(ve))
        except Exception as ex:
            self._mostrar_error(f"Error: {str(ex)}")
    
    def _mostrar_error(self, mensaje: str):
        self.page.snack_bar = ft.SnackBar(
            ft.Text(mensaje),
            bgcolor=Colors.DANGER,
            open=True
        )
        self.page.update()
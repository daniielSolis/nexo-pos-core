"""Validadores reutilizables"""

class ValidationError(Exception):
    """Excepción para errores de validación"""
    pass

class Validators:
    
    @staticmethod
    def validar_campo_vacio(valor: str, nombre_campo: str) -> str:
        """Valida que un campo no esté vacío"""
        valor_limpio = valor.strip() if valor else ""
        if not valor_limpio:
            raise ValidationError(f"El campo '{nombre_campo}' no puede estar vacío")
        return valor_limpio
    
    @staticmethod
    def validar_numero_positivo(valor: str, nombre_campo: str) -> float:
        """Valida que un valor sea número positivo"""
        try:
            numero = float(valor or 0)
            if numero < 0:
                raise ValidationError(f"El campo '{nombre_campo}' no puede ser negativo")
            return numero
        except ValueError:
            raise ValidationError(f"El campo '{nombre_campo}' debe ser un número válido")
    
    @staticmethod
    def validar_entero_positivo(valor: str, nombre_campo: str) -> int:
        """Valida que un valor sea entero positivo"""
        try:
            numero = int(valor or 0)
            if numero < 0:
                raise ValidationError(f"El campo '{nombre_campo}' no puede ser negativo")
            return numero
        except ValueError:
            raise ValidationError(f"El campo '{nombre_campo}' debe ser un número entero válido")
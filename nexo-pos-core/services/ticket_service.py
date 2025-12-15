"""Servicio de Generación de Tickets"""
import os
import datetime

class TicketService:
    
    TICKETS_DIR = "tickets"
    ANCHO_TICKET = 32
    
    def __init__(self):
        self._crear_carpeta_tickets()
    
    def _crear_carpeta_tickets(self):
        if not os.path.exists(self.TICKETS_DIR):
            os.makedirs(self.TICKETS_DIR)
    
    def generar_ticket(self, items: list, total: float, vendedor: str) -> str:
        fecha_actual = datetime.datetime.now()
        nombre_archivo = f"{self.TICKETS_DIR}/ticket_{fecha_actual.strftime('%Y%m%d_%H%M%S')}.txt"
        
        linea = "=" * self.ANCHO_TICKET + "\n"
        texto = linea
        texto += "          NEXO POS\n"
        texto += "     Tu Tienda de Confianza\n"
        texto += linea
        texto += f"Fecha: {fecha_actual.strftime('%d/%m/%Y %H:%M:%S')}\n"
        texto += f"Le atendió: {vendedor}\n"
        texto += linea
        texto += "CANT  PRODUCTO          TOTAL\n"
        texto += "-" * self.ANCHO_TICKET + "\n"
        
        for item in items:
            subtotal = item['precio'] * item['cantidad']
            texto += f"{item['cantidad']} x {item['nombre'][:15]:<15} ${subtotal:.2f}\n"
        
        texto += "-" * self.ANCHO_TICKET + "\n"
        texto += f"TOTAL A PAGAR:      ${total:.2f}\n"
        texto += linea
        texto += "    ¡GRACIAS POR SU COMPRA!\n"
        texto += linea
        texto += "\n"
        texto += "      Sistema Punto de Venta\n"
        texto += "           *** NEXO ***\n"
        texto += "=" * self.ANCHO_TICKET
        
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(texto)
        
        try:
            os.startfile(nombre_archivo)
        except:
            pass
        
        return nombre_archivo

# Instancia global (Singleton pattern)
ticket_service = TicketService()
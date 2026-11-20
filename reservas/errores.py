class ErrorReserva(Exception):
    """Excepción base para errores del sistema de reservas."""
    pass

class ErrorValidacion(ErrorReserva):
    """Error en los datos de entrada o reglas de validación."""
    pass

class ErrorSolape(ErrorReserva):
    """Conflicto por superposición de horarios en reservas de la misma unidad."""
    pass

class ErrorNoEncontrado(ErrorReserva):
    """Elemento no encontrado en el sistema."""
    pass

class ErrorEstado(ErrorReserva):
    """Operación no válida para el estado actual de la reserva."""
    pass

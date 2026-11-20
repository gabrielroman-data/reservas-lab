from dataclasses import dataclass
from datetime import datetime

from reservas.errores import ErrorValidacion

@dataclass
class Reserva:
    id: int
    unidad: str
    solicitante: str
    inicio: datetime
    fin: datetime
    estado: str

def se_solapan(a_ini: datetime, a_fin: datetime, b_ini: datetime, b_fin: datetime) -> bool:
    """
    Determina si dos intervalos semiabiertos [inicio, fin) se superponen.
    Regla: inicio_a < fin_b and inicio_b < fin_a (nunca usar <=).
    """
    return a_ini < b_fin and b_ini < a_fin

def parsear_fecha(texto: str) -> datetime:
    """
    Convierte una cadena de fecha con formato 'YYYY-MM-DDTHH:MM' a datetime.
    Lanza ErrorValidacion si el formato o la fecha son inválidos.
    """
    try:
        return datetime.strptime(texto, "%Y-%m-%dT%H:%M")
    except (ValueError, TypeError):
        raise ErrorValidacion(f"Formato de fecha u hora inválido: '{texto}'. Debe ser 'YYYY-MM-DDTHH:MM'.")

def validar_solicitud(
    unidad: str,
    solicitante: str,
    inicio: str | datetime,
    fin: str | datetime,
    ahora: datetime,
    unidades_validas: set[str]
) -> tuple[str, datetime, datetime]:
    """
    Valida los datos de una solicitud de reserva.
    Retorna una tupla: (solicitante_limpio, inicio_dt, fin_dt).
    """
    if unidad not in unidades_validas:
        raise ErrorValidacion(f"Unidad desconocida: '{unidad}'. Unidades válidas: {sorted(unidades_validas)}")

    if not isinstance(solicitante, str) or not solicitante.strip():
        raise ErrorValidacion("El solicitante no puede ser vacío ni contener solo espacios.")
    
    solicitante_limpio = solicitante.strip()

    inicio_dt = parsear_fecha(inicio) if isinstance(inicio, str) else inicio
    fin_dt = parsear_fecha(fin) if isinstance(fin, str) else fin

    if inicio_dt >= fin_dt:
        raise ErrorValidacion("La fecha/hora de inicio debe ser estrictamente anterior a la fecha/hora de fin.")

    if inicio_dt < ahora:
        raise ErrorValidacion("La fecha/hora de inicio no puede ser anterior a la fecha/hora actual ('ahora').")

    return solicitante_limpio, inicio_dt, fin_dt

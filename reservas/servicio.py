from datetime import datetime
from typing import Callable, List, Dict, Any

from reservas.dominio import se_solapan, validar_intervalo, validar_solicitud, Reserva
from reservas.errores import ErrorSolape
from reservas.persistencia import AlmacenSQLite

class ServicioReservas:
    def __init__(
        self,
        ruta_db: str,
        inventario: List[Dict[str, Any]],
        ahora: Callable[[], datetime] = datetime.now
    ):
        self.almacen = AlmacenSQLite(ruta_db)
        self.inventario = inventario
        self._ahora_fn = ahora
        self.unidades_validas = {item["id"] for item in inventario}

    def _obtener_ahora(self) -> datetime:
        return self._ahora_fn()

    def _verificar_solape_unidad(self, unidad: str, inicio_dt: datetime, fin_dt: datetime) -> bool:
        activas = self.almacen.obtener_activas_por_unidad(unidad)
        for _, ini_act, fin_act in activas:
            if se_solapan(inicio_dt, fin_dt, ini_act, fin_act):
                return True
        return False

    def disponible(self, unidad: str, inicio: str | datetime, fin: str | datetime) -> bool:
        ahora_dt = self._obtener_ahora()
        inicio_dt, fin_dt = validar_intervalo(unidad, inicio, fin, ahora_dt, self.unidades_validas)
        hay_solape = self._verificar_solape_unidad(unidad, inicio_dt, fin_dt)
        return not hay_solape

    def reservar(self, unidad: str, solicitante: str, inicio: str | datetime, fin: str | datetime) -> Reserva:
        ahora_dt = self._obtener_ahora()
        solicitante_limpio, inicio_dt, fin_dt = validar_solicitud(
            unidad, solicitante, inicio, fin, ahora_dt, self.unidades_validas
        )

        if self._verificar_solape_unidad(unidad, inicio_dt, fin_dt):
            raise ErrorSolape(f"La unidad '{unidad}' ya se encuentra reservada en el intervalo especificado.")

        return self.almacen.insertar_reserva(unidad, solicitante_limpio, inicio_dt, fin_dt)

    def listar(self, estado: str | None = None) -> List[Reserva]:
        return self.almacen.listar(estado)

    def listar_inventario(self) -> List[Dict[str, Any]]:
        return self.inventario

    def cerrar(self):
        if self.almacen:
            self.almacen.cerrar()

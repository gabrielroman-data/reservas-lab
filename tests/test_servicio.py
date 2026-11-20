from datetime import datetime
import json
from pathlib import Path
import tempfile
import unittest

from reservas.errores import ErrorSolape, ErrorValidacion
from reservas.servicio import ServicioReservas

AHORA = datetime(2026, 12, 1, 8, 0)

def obtener_inventario():
    ruta = Path(__file__).parent.parent / "data" / "inventario.json"
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

class TestServicio(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_reservas.db"
        self.inventario = obtener_inventario()
        self.servicio = ServicioReservas(
            ruta_db=str(self.db_path),
            inventario=self.inventario,
            ahora=lambda: AHORA
        )

    def tearDown(self):
        if hasattr(self, 'servicio') and self.servicio:
            self.servicio.cerrar()
        self.temp_dir.cleanup()

    def test_ca01_crear_reserva_mic01_exitosa(self):
        reserva = self.servicio.reservar("MIC-01", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00")
        self.assertEqual(reserva.id, 1)
        self.assertEqual(reserva.unidad, "MIC-01")
        self.assertEqual(reserva.solicitante, "Ana Prueba")
        self.assertEqual(reserva.inicio, datetime(2026, 12, 1, 10, 0))
        self.assertEqual(reserva.fin, datetime(2026, 12, 1, 11, 0))
        self.assertEqual(reserva.estado, "activa")

    def test_rf03_segunda_reserva_id_creciente(self):
        r1 = self.servicio.reservar("MIC-01", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00")
        r2 = self.servicio.reservar("MIC-02", "Juan Pedro", "2026-12-01T10:00", "2026-12-01T11:00")
        self.assertEqual(r1.id, 1)
        self.assertEqual(r2.id, 2)

    def test_ca02_solape_rechazado_y_sin_filas(self):
        self.servicio.reservar("MIC-01", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00")
        with self.assertRaises(ErrorSolape):
            self.servicio.reservar("MIC-01", "Pedro Solo", "2026-12-01T10:30", "2026-12-01T11:30")
        reservas = self.servicio.listar()
        self.assertEqual(len(reservas), 1)

    def test_ca03_consecutivos_ambas_activas(self):
        r1 = self.servicio.reservar("MIC-01", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00")
        r2 = self.servicio.reservar("MIC-01", "Pedro Solo", "2026-12-01T11:00", "2026-12-01T12:00")
        self.assertEqual(r1.estado, "activa")
        self.assertEqual(r2.estado, "activa")

    def test_ca04_distintas_unidades_mismo_horario(self):
        r1 = self.servicio.reservar("MIC-01", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00")
        r2 = self.servicio.reservar("MIC-02", "Pedro Solo", "2026-12-01T10:00", "2026-12-01T11:00")
        self.assertEqual(r1.estado, "activa")
        self.assertEqual(r2.estado, "activa")

    def test_rn06_misma_unidad_mismo_horario_distinto_solicitante(self):
        self.servicio.reservar("MIC-01", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00")
        with self.assertRaises(ErrorSolape):
            self.servicio.reservar("MIC-01", "Carlos Otro", "2026-12-01T10:00", "2026-12-01T11:00")

    def test_rf02_disponible_respuestas_correctas(self):
        self.servicio.reservar("MIC-01", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00")
        self.assertFalse(self.servicio.disponible("MIC-01", "2026-12-01T10:30", "2026-12-01T11:30"))
        self.assertTrue(self.servicio.disponible("MIC-01", "2026-12-01T11:00", "2026-12-01T12:00"))
        self.assertTrue(self.servicio.disponible("MIC-02", "2026-12-01T10:00", "2026-12-01T11:00"))

    def test_ca08_consistencia_disponible_y_reservar(self):
        self.servicio.reservar("MIC-01", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00")
        intervalos_prueba = [
            ("2026-12-01T10:30", "2026-12-01T11:30"),  # solapa
            ("2026-12-01T11:00", "2026-12-01T12:00"),  # no solapa
            ("2026-12-01T09:00", "2026-12-01T10:15"),  # solapa
            ("2026-12-01T08:00", "2026-12-01T09:00"),  # no solapa
        ]
        for ini, fin in intervalos_prueba:
            disp = self.servicio.disponible("MIC-01", ini, fin)
            if not disp:
                with self.assertRaises(ErrorSolape):
                    self.servicio.reservar("MIC-01", "Test Consistencia", ini, fin)
            else:
                r = self.servicio.reservar("MIC-01", "Test Consistencia", ini, fin)
                self.assertEqual(r.estado, "activa")

    def test_rn09_disponible_valida_entradas(self):
        with self.assertRaises(ErrorValidacion):
            self.servicio.disponible("XXX-99", "2026-12-01T10:00", "2026-12-01T11:00")
        with self.assertRaises(ErrorValidacion):
            self.servicio.disponible("MIC-01", "2026-12-01T11:00", "2026-12-01T10:00")

    def test_rf03_reservar_invalido_sin_filas(self):
        with self.assertRaises(ErrorValidacion):
            self.servicio.reservar("XXX-99", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00")
        self.assertEqual(len(self.servicio.listar()), 0)

    def test_ca07_persistencia_y_recuperacion_tras_reinicio(self):
        self.servicio.reservar("MIC-01", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00")
        self.servicio.reservar("MIC-02", "Juan Pedro", "2026-12-01T12:00", "2026-12-01T13:00")
        self.servicio.cerrar()

        nuevo_servicio = ServicioReservas(
            ruta_db=str(self.db_path),
            inventario=self.inventario,
            ahora=lambda: AHORA
        )
        try:
            reservas = nuevo_servicio.listar()
            self.assertEqual(len(reservas), 2)
            self.assertEqual(reservas[0].id, 1)
            self.assertEqual(reservas[0].unidad, "MIC-01")
            self.assertEqual(reservas[1].id, 2)
            self.assertEqual(reservas[1].unidad, "MIC-02")
        finally:
            nuevo_servicio.cerrar()

    def test_rf06_autoincrement_mantiene_contador_tras_reinicio(self):
        self.servicio.reservar("MIC-01", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00")
        self.servicio.reservar("MIC-02", "Juan Pedro", "2026-12-01T12:00", "2026-12-01T13:00")
        self.servicio.cerrar()

        nuevo_servicio = ServicioReservas(
            ruta_db=str(self.db_path),
            inventario=self.inventario,
            ahora=lambda: AHORA
        )
        try:
            r3 = nuevo_servicio.reservar("OSC-01", "Carlos Tres", "2026-12-01T14:00", "2026-12-01T15:00")
            self.assertEqual(r3.id, 3)
        finally:
            nuevo_servicio.cerrar()

    def test_rf01_listar_inventario_devuelve_5_unidades(self):
        inv = self.servicio.listar_inventario()
        self.assertEqual(len(inv), 5)
        ids = [item["id"] for item in inv]
        self.assertIn("MIC-01", ids)
        self.assertIn("FUE-01", ids)

if __name__ == "__main__":
    unittest.main()

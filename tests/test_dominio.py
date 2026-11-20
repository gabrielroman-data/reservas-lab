from datetime import datetime
import unittest

from reservas.dominio import se_solapan, parsear_fecha, validar_solicitud
from reservas.errores import ErrorValidacion

AHORA = datetime(2026, 12, 1, 8, 0)
UNIDADES_VALIDAS = {"MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"}

class TestDominio(unittest.TestCase):
    # --- se_solapan ---
    def test_rn06_solape_parcial(self):
        a_ini = datetime(2026, 12, 1, 10, 0)
        a_fin = datetime(2026, 12, 1, 11, 0)
        b_ini = datetime(2026, 12, 1, 10, 30)
        b_fin = datetime(2026, 12, 1, 11, 30)
        self.assertTrue(se_solapan(a_ini, a_fin, b_ini, b_fin))

    def test_rn07_consecutivos_permitidos_orden_1(self):
        a_ini = datetime(2026, 12, 1, 10, 0)
        a_fin = datetime(2026, 12, 1, 11, 0)
        b_ini = datetime(2026, 12, 1, 11, 0)
        b_fin = datetime(2026, 12, 1, 12, 0)
        self.assertFalse(se_solapan(a_ini, a_fin, b_ini, b_fin))

    def test_rn07_consecutivos_permitidos_orden_2(self):
        a_ini = datetime(2026, 12, 1, 11, 0)
        a_fin = datetime(2026, 12, 1, 12, 0)
        b_ini = datetime(2026, 12, 1, 10, 0)
        b_fin = datetime(2026, 12, 1, 11, 0)
        self.assertFalse(se_solapan(a_ini, a_fin, b_ini, b_fin))

    def test_rn06_intervalos_identicos(self):
        a_ini = datetime(2026, 12, 1, 10, 0)
        a_fin = datetime(2026, 12, 1, 11, 0)
        self.assertTrue(se_solapan(a_ini, a_fin, a_ini, a_fin))

    def test_rn06_intervalo_contenido(self):
        a_ini = datetime(2026, 12, 1, 9, 0)
        a_fin = datetime(2026, 12, 1, 12, 0)
        b_ini = datetime(2026, 12, 1, 10, 0)
        b_fin = datetime(2026, 12, 1, 11, 0)
        self.assertTrue(se_solapan(a_ini, a_fin, b_ini, b_fin))

    def test_rn06_intervalos_separados(self):
        a_ini = datetime(2026, 12, 1, 10, 0)
        a_fin = datetime(2026, 12, 1, 11, 0)
        b_ini = datetime(2026, 12, 1, 12, 0)
        b_fin = datetime(2026, 12, 1, 13, 0)
        self.assertFalse(se_solapan(a_ini, a_fin, b_ini, b_fin))

    # --- validar_solicitud / parsear_fecha ---
    def test_rf03_solicitud_valida_devuelve_datos(self):
        sol, ini, fin = validar_solicitud("MIC-01", "  Ana Prueba  ", "2026-12-01T10:00", "2026-12-01T11:00", AHORA, UNIDADES_VALIDAS)
        self.assertEqual(sol, "Ana Prueba")
        self.assertEqual(ini, datetime(2026, 12, 1, 10, 0))
        self.assertEqual(fin, datetime(2026, 12, 1, 11, 0))

    def test_supuestos_inicio_igual_a_ahora_es_valido(self):
        sol, ini, fin = validar_solicitud("MIC-01", "Ana Prueba", "2026-12-01T08:00", "2026-12-01T09:00", AHORA, UNIDADES_VALIDAS)
        self.assertEqual(sol, "Ana Prueba")
        self.assertEqual(ini, AHORA)
        self.assertEqual(fin, datetime(2026, 12, 1, 9, 0))

    def test_rn02_unidad_desconocida(self):
        with self.assertRaises(ErrorValidacion):
            validar_solicitud("XXX-99", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T11:00", AHORA, UNIDADES_VALIDAS)

    def test_rn03_solicitante_vacio(self):
        with self.assertRaises(ErrorValidacion):
            validar_solicitud("MIC-01", "", "2026-12-01T10:00", "2026-12-01T11:00", AHORA, UNIDADES_VALIDAS)

    def test_rn03_solicitante_solo_espacios(self):
        with self.assertRaises(ErrorValidacion):
            validar_solicitud("MIC-01", "   \t ", "2026-12-01T10:00", "2026-12-01T11:00", AHORA, UNIDADES_VALIDAS)

    def test_rn03_solicitante_espacios_alrededor_recorta(self):
        sol, ini, fin = validar_solicitud("MIC-01", "  Ana Prueba  ", "2026-12-01T10:00", "2026-12-01T11:00", AHORA, UNIDADES_VALIDAS)
        self.assertEqual(sol, "Ana Prueba")

    def test_rn04_fechas_invalidas(self):
        fechas_malas = ["2026-13-01T10:00", "2026-12-01 10:00", "hola", "2026-02-30T10:00"]
        for f in fechas_malas:
            with self.subTest(fecha=f):
                with self.assertRaises(ErrorValidacion):
                    parsear_fecha(f)

    def test_rn05_inicio_igual_fin(self):
        with self.assertRaises(ErrorValidacion):
            validar_solicitud("MIC-01", "Ana Prueba", "2026-12-01T10:00", "2026-12-01T10:00", AHORA, UNIDADES_VALIDAS)

    def test_rn05_inicio_posterior_fin(self):
        with self.assertRaises(ErrorValidacion):
            validar_solicitud("MIC-01", "Ana Prueba", "2026-12-01T11:00", "2026-12-01T10:00", AHORA, UNIDADES_VALIDAS)

    def test_supuestos_inicio_anterior_ahora(self):
        with self.assertRaises(ErrorValidacion):
            validar_solicitud("MIC-01", "Ana Prueba", "2026-12-01T07:59", "2026-12-01T10:00", AHORA, UNIDADES_VALIDAS)

if __name__ == "__main__":
    unittest.main()

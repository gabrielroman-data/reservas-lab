from io import StringIO
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from reservas.cli import main

def obtener_inventario_path():
    return Path(__file__).parent.parent / "data" / "inventario.json"

class TestCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "test_cli.db")

    def tearDown(self):
        self.temp_dir.cleanup()

    def run_cli(self, argv):
        full_argv = ["--db", self.db_path] + argv
        out_buf = StringIO()
        err_buf = StringIO()
        with patch("sys.stdout", out_buf), patch("sys.stderr", err_buf):
            code = main(full_argv)
        return code, out_buf.getvalue(), err_buf.getvalue()

    def test_cli_inventario_muestra_5_unidades(self):
        code, out, err = self.run_cli(["inventario"])
        self.assertEqual(code, 0)
        self.assertIn("MIC-01", out)
        self.assertIn("MIC-02", out)
        self.assertIn("OSC-01", out)
        self.assertIn("MUL-01", out)
        self.assertIn("FUE-01", out)

    def test_cli_reservar_valido_imprime_id(self):
        code, out, err = self.run_cli(["reservar", "MIC-01", "Ana Prueba", "2099-12-01T10:00", "2099-12-01T11:00"])
        self.assertEqual(code, 0)
        self.assertIn("1", out)

    def test_cli_reservar_solape_codigo_1_y_stderr(self):
        self.run_cli(["reservar", "MIC-01", "Ana Prueba", "2099-12-01T10:00", "2099-12-01T11:00"])
        code, out, err = self.run_cli(["reservar", "MIC-01", "Pedro Solo", "2099-12-01T10:30", "2099-12-01T11:30"])
        self.assertEqual(code, 1)
        self.assertTrue(len(err) > 0)
        
        _, list_out, _ = self.run_cli(["listar"])
        self.assertNotIn("Pedro Solo", list_out)

    def test_cli_reservar_solicitante_espacios_codigo_1(self):
        code, out, err = self.run_cli(["reservar", "MIC-01", "   ", "2099-12-01T10:00", "2099-12-01T11:00"])
        self.assertEqual(code, 1)
        self.assertTrue(len(err) > 0)

    def test_cli_turnos_consecutivos_y_unidades_distintas(self):
        code1, _, _ = self.run_cli(["reservar", "MIC-01", "Ana Prueba", "2099-12-01T10:00", "2099-12-01T11:00"])
        code2, _, _ = self.run_cli(["reservar", "MIC-01", "Pedro Solo", "2099-12-01T11:00", "2099-12-01T12:00"])
        code3, _, _ = self.run_cli(["reservar", "MIC-02", "Juan Tres", "2099-12-01T10:00", "2099-12-01T11:00"])
        self.assertEqual(code1, 0)
        self.assertEqual(code2, 0)
        self.assertEqual(code3, 0)

    def test_cli_disponibilidad_respuestas(self):
        self.run_cli(["reservar", "MIC-01", "Ana Prueba", "2099-12-01T10:00", "2099-12-01T11:00"])
        
        c1, out1, _ = self.run_cli(["disponibilidad", "MIC-01", "2099-12-01T10:30", "2099-12-01T11:30"])
        self.assertEqual(c1, 0)
        self.assertIn("no disponible", out1.lower())

        c2, out2, _ = self.run_cli(["disponibilidad", "MIC-01", "2099-12-01T11:00", "2099-12-01T12:00"])
        self.assertEqual(c2, 0)
        self.assertIn("disponible", out2.lower())
        self.assertNotIn("no disponible", out2.lower())

    def test_cli_cancelar_y_libera_horario(self):
        self.run_cli(["reservar", "MIC-01", "Ana Prueba", "2099-12-01T10:00", "2099-12-01T11:00"])
        code_c, out_c, _ = self.run_cli(["cancelar", "1"])
        self.assertEqual(code_c, 0)

        _, out_l, _ = self.run_cli(["listar"])
        self.assertIn("cancelada", out_l)

        c_disp, out_disp, _ = self.run_cli(["disponibilidad", "MIC-01", "2099-12-01T10:00", "2099-12-01T11:00"])
        self.assertEqual(c_disp, 0)
        self.assertIn("disponible", out_disp.lower())

    def test_cli_cancelar_inexistente_y_repetido(self):
        code1, _, err1 = self.run_cli(["cancelar", "999"])
        self.assertEqual(code1, 1)
        self.assertTrue(len(err1) > 0)

        self.run_cli(["reservar", "MIC-01", "Ana Prueba", "2099-12-01T10:00", "2099-12-01T11:00"])
        self.run_cli(["cancelar", "1"])
        code2, _, err2 = self.run_cli(["cancelar", "1"])
        self.assertEqual(code2, 1)
        self.assertTrue(len(err2) > 0)

    def test_cli_listar_filtrar_estado(self):
        self.run_cli(["reservar", "MIC-01", "Ana Prueba", "2099-12-01T10:00", "2099-12-01T11:00"])
        self.run_cli(["reservar", "MIC-02", "Pedro Solo", "2099-12-01T12:00", "2099-12-01T13:00"])
        self.run_cli(["cancelar", "1"])

        _, out_act, _ = self.run_cli(["listar", "--estado", "activa"])
        self.assertNotIn("MIC-01", out_act)
        self.assertIn("MIC-02", out_act)

        _, out_canc, _ = self.run_cli(["listar", "--estado", "cancelada"])
        self.assertIn("MIC-01", out_canc)
        self.assertNotIn("MIC-02", out_canc)

    def test_cli_reiniciar_datos(self):
        self.run_cli(["reservar", "MIC-01", "Ana Prueba", "2099-12-01T10:00", "2099-12-01T11:00"])
        
        # Sin --confirmar -> debe fallar (código != 0)
        code_sin, _, _ = self.run_cli(["reiniciar-datos"])
        self.assertNotEqual(code_sin, 0)

        _, out_before, _ = self.run_cli(["listar"])
        self.assertIn("MIC-01", out_before)

        # Con --confirmar -> borra todo
        code_con, _, _ = self.run_cli(["reiniciar-datos", "--confirmar"])
        self.assertEqual(code_con, 0)

        _, out_after, _ = self.run_cli(["listar"])
        self.assertEqual(out_after.strip(), "")

    def test_cli_persistencia_entre_procesos(self):
        cmd_res = [
            sys.executable, "-m", "reservas",
            "--db", self.db_path,
            "reservar", "MIC-01", "Ana Proceso", "2099-12-01T10:00", "2099-12-01T11:00"
        ]
        res1 = subprocess.run(cmd_res, capture_output=True, text=True)
        self.assertEqual(res1.returncode, 0)

        cmd_list = [
            sys.executable, "-m", "reservas",
            "--db", self.db_path,
            "listar"
        ]
        res2 = subprocess.run(cmd_list, capture_output=True, text=True)
        self.assertEqual(res2.returncode, 0)
        self.assertIn("Ana Proceso", res2.stdout)

if __name__ == "__main__":
    unittest.main()

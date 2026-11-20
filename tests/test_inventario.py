import json
from pathlib import Path
import unittest

class TestInventario(unittest.TestCase):
    def test_inventario_json_valido(self):
        ruta = Path(__file__).parent.parent / "data" / "inventario.json"
        self.assertTrue(ruta.exists(), f"El archivo {ruta} no existe")
        
        with open(ruta, "r", encoding="utf-8") as f:
            inventario = json.load(f)
            
        # 1. Verificación de 5 unidades
        self.assertEqual(len(inventario), 5, "El inventario debe contener exactamente 5 unidades")
        
        # 2. Verificación de IDs únicos
        ids = [item["id"] for item in inventario]
        self.assertEqual(len(ids), len(set(ids)), "Los IDs del inventario deben ser únicos")
        
        # 3. Verificación de MIC-01 y MIC-02 como unidades distintas
        mic_01 = next((item for item in inventario if item["id"] == "MIC-01"), None)
        mic_02 = next((item for item in inventario if item["id"] == "MIC-02"), None)
        
        self.assertIsNotNone(mic_01, "MIC-01 debe existir en el inventario")
        self.assertIsNotNone(mic_02, "MIC-02 debe existir en el inventario")
        self.assertNotEqual(mic_01, mic_02, "MIC-01 y MIC-02 deben ser unidades distintas")

if __name__ == "__main__":
    unittest.main()

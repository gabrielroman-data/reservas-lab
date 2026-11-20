Lee AGENTS.md, README.md (sección 1, en especial 1.5, 1.6 y 1.7) y PROMPTS.md (sección "Contrato común" y tarea T2). Tarea T2, parte A, solo las pruebas:

1\. Crea tests/test\_dominio.py con pruebas unittest para el contrato de PROMPTS.md: se\_solapan, parsear\_fecha y validar\_solicitud. Usa AHORA = datetime(2026, 12, 1, 8, 0) y unidades\_validas = {"MIC-01", "MIC-02", "OSC-01", "MUL-01", "FUE-01"}.

2\. Cubre estos casos: solape parcial, intervalos consecutivos (10:00-11:00 y 11:00-12:00 NO se solapan, en ambos órdenes), intervalos idénticos, uno contenido en otro, intervalos separados, unidad desconocida, solicitante vacío, solicitante de solo espacios, solicitante con espacios alrededor (se recorta), fechas inválidas, inicio igual al fin, inicio posterior al fin e inicio anterior a AHORA.

3\. IMPORTANTE: NO pruebes límites de duración ni de anticipación. Fueron eliminados de la especificación (README 1.6): no existe límite máximo.

4\. Nombra cada prueba con el requisito que cubre (por ejemplo test\_rn07\_consecutivos\_permitidos).

5\. NO crees dominio.py ni errores.py todavía. Ejecuta python -m unittest -v y muestra la salida real: las pruebas deben FALLAR porque el código aún no existe.

No ejecutes git push ni comandos fuera de esta carpeta. No actualices la lista de tareas. Usa la menor cantidad posible de llamadas.


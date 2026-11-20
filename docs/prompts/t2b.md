Tarea T2, parte B. Lee AGENTS.md y PROMPTS.md (sección "Contrato común"). El paquete está en reservas/ (raíz del proyecto, no en src/). Las pruebas de tests/test\_dominio.py ya existen.

Paso 1, antes de implementar: agrega a tests/test\_dominio.py dos pruebas más. (a) test\_rf03\_solicitud\_valida\_devuelve\_datos: validar\_solicitud con datos válidos devuelve (solicitante recortado, datetime de inicio, datetime de fin) correctos. (b) test\_supuestos\_inicio\_igual\_a\_ahora\_es\_valido: un inicio exactamente igual a AHORA es válido.

Paso 2: implementa reservas/errores.py y reservas/dominio.py con el contrato de PROMPTS.md para que TODAS las pruebas pasen.

Reglas: intervalos semiabiertos \[inicio, fin); se\_solapan usa solo comparaciones estrictas, nunca <=, con a\_ini < b\_fin and b\_ini < a\_fin. parsear\_fecha usa datetime.strptime con el formato exacto "%Y-%m-%dT%H:%M" (no uses fromisoformat). validar\_solicitud valida: unidad conocida, solicitante no vacío ni solo espacios (con strip), fechas válidas, inicio estrictamente anterior al fin e inicio no anterior a ahora. Cada error lleva un mensaje claro en español. No uses datetime.now(): "ahora" llega por parámetro. No hay límites de duración ni de anticipación.

No toques persistencia ni consola. Ejecuta python -m unittest -v y muestra la salida real. Actualiza PROGRESS.md con fecha 2026-11-20 al terminar. No ejecutes git push ni comandos fuera de esta carpeta. No actualices la lista de tareas. Usa la menor cantidad posible de llamadas.


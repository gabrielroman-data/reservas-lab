Lee AGENTS.md, README.md (sección 1) y PROMPTS.md (sección "Contrato común" y tarea T3). Archivos relevantes: reservas/dominio.py, reservas/errores.py y data/inventario.json. No explores el repositorio con find ni ls.

Tarea T3, parte A, solo las pruebas:

1\. Crea tests/test\_servicio.py con pruebas unittest para ServicioReservas(ruta\_db, inventario, ahora) del contrato de PROMPTS.md. Cada prueba usa una base SQLite en un archivo dentro de un directorio temporal (tempfile.TemporaryDirectory), nunca data/reservas.db. Reloj fijo: AHORA = datetime(2026, 12, 1, 8, 0), pasado como ahora=lambda: AHORA. El inventario se lee de data/inventario.json con json.load (lista de {"id", "nombre"}).

2\. Casos a cubrir:

&#x20;  - reservar MIC-01 para "Ana Prueba" de 10:00 a 11:00: devuelve una Reserva con id 1, estado "activa", y los datos recibidos.

&#x20;  - una segunda reserva válida recibe id 2 (ids únicos y crecientes).

&#x20;  - MIC-01 10:00-11:00 y luego 10:30-11:30: lanza ErrorSolape y no se crea ninguna fila.

&#x20;  - MIC-01 10:00-11:00 y luego 11:00-12:00: ambas activas (turnos consecutivos).

&#x20;  - MIC-01 y MIC-02 en el mismo horario: ambas activas.

&#x20;  - misma unidad y mismo horario con otro solicitante: ErrorSolape.

&#x20;  - disponible() da False con solape, True con turno consecutivo y True para otra unidad.

&#x20;  - consistencia: para varios intervalos, disponible() es False exactamente cuando reservar() lanzaría ErrorSolape.

&#x20;  - disponible() con unidad desconocida o inicio >= fin lanza ErrorValidacion (no devuelve False).

&#x20;  - reservar() con entrada inválida no deja ninguna fila en la base.

&#x20;  - persistencia: crear 2 reservas, llamar a cerrar(), abrir un ServicioReservas nuevo sobre el mismo archivo: listar() devuelve las 2 con los mismos ids y datos.

&#x20;  - después de reabrir, la siguiente reserva recibe id 3 (el contador no se reinicia).

&#x20;  - listar\_inventario() devuelve las 5 unidades.

3\. Nombra cada prueba con el requisito o criterio que cubre (por ejemplo test\_ca02\_solape\_rechazado).

4\. NO crees servicio.py ni persistencia.py. No toques tests/test\_dominio.py ni reservas/dominio.py. Ejecuta python -m unittest -v y muestra la salida real: las pruebas nuevas deben FALLAR porque el código aún no existe.

No ejecutes git push ni comandos fuera de esta carpeta. No actualices la lista de tareas ni PROGRESS.md. Usa la menor cantidad posible de llamadas.


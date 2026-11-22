# Procedimiento manual de persistencia

Objetivo: comprobar que las reservas activas y canceladas se recuperan tras detener y reiniciar la aplicación sin borrar datos. Cada comando de la consola es un proceso nuevo: al terminar, el programa se detiene; el siguiente comando lo "reinicia" sobre el mismo archivo de base de datos.

Se usa una base temporal (`/tmp/demo.db`) para no tocar `data/reservas.db`.

| # | Comando | Resultado esperado | Resultado observado |
|---|---|---|---|
| 1 | `python -m reservas --db /tmp/demo.db init` | Sin salida, código 0 | Sin salida |
| 2 | `python -m reservas --db /tmp/demo.db reservar MIC-01 "Ana Prueba" 2099-12-01T10:00 2099-12-01T11:00` | Reserva creada con ID 1 | `Reserva creada exitosamente con ID 1.` |
| 3 | `python -m reservas --db /tmp/demo.db reservar MIC-01 "Bruno Prueba" 2099-12-01T10:30 2099-12-01T11:30` | Rechazada por superposición | `Error: La unidad 'MIC-01' ya se encuentra reservada en el intervalo especificado.` |
| 4 | `python -m reservas --db /tmp/demo.db cancelar 1` | Reserva 1 cancelada | `Reserva 1 cancelada exitosamente.` |
| 5 | `python -m reservas --db /tmp/demo.db listar` | La reserva 1 sigue listada, estado cancelada | `ID 1 \| MIC-01 \| Ana Prueba \| 2099-12-01T10:00 \| 2099-12-01T11:00 \| cancelada` |
| 6 | `python -m reservas --db /tmp/demo.db disponibilidad MIC-01 2099-12-01T10:00 2099-12-01T11:00` | Horario libre (la cancelada no bloquea) | `DISPONIBLE: la unidad MIC-01 se puede reservar en el intervalo 2099-12-01T10:00 - 2099-12-01T11:00.` |

Conclusión: los resultados observados coinciden con los esperados; la reserva cancelada se conservó entre procesos y dejó de bloquear el horario.

Limpieza: `rm /tmp/demo.db`.

Fecha de ejecución: 2026-11-22. Ejecutado por mí en Git Bash.

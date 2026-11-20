# PROGRESS.md — progreso y decisiones (versionado)

El agente lee este archivo al iniciar y lo actualiza al terminar cada tarea.
Registrar solo resultados realmente ejecutados.

## Plan
- [x] T1 Esqueleto del repo + inventario (`data/inventario.json`) + `.gitignore` (excluir `data/reservas.db`)
- [ ] T2 Dominio: validaciones y solape + pruebas (CA-01..CA-05, CA-08)
- [ ] T3 Persistencia SQLite + pruebas de reinicio (CA-07)
- [ ] T4 Cancelación + pruebas (CA-06, RN-10)
- [ ] T5 CLI + ejemplo real de entrada/salida
- [ ] T6 Completar README (secciones 2, 3, 4) con evidencia

## Bitácora
| Fecha | Tarea | Comando ejecutado | Resultado real | Decisión humana |
|---|---|---|---|---|
| 2025-05-18 | T1 | `python -m unittest -v` | Ran 1 test in 0.000s - OK | Creación del esqueleto, inventario.json, .gitignore y test de inventario |

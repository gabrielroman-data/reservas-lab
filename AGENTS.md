# AGENTS.md — instrucciones para el agente de programación

Contexto: sistema de reservas de equipos de laboratorio (desafío "Challenge IA").
La fuente de verdad de los requisitos es la sección "Especificación" de `README.md`.

## Reglas de trabajo
1. Antes de escribir código, lee `README.md` (Especificación) y `PROGRESS.md`.
2. Trabaja en pasos pequeños: un requisito (RF-xx / RN-xx) por vez, con su prueba.
3. Escribe primero la prueba y confirma que falla; luego implementa.
4. Solo biblioteca estándar de Python 3.11+ (sin dependencias externas). Pruebas con `unittest`.
5. Toda regla de negocio vive en `src/reservas/dominio.py`; la CLI y el almacenamiento no la duplican.
6. La disponibilidad y la creación de reservas usan la MISMA función de solape.
7. Hora actual inyectable (parámetro `ahora`), nunca `datetime.now()` dentro de las reglas.
8. Al terminar cada tarea: ejecuta `python -m unittest -v`, pega el resultado real en `PROGRESS.md` y haz commit.
9. No inventes resultados: si un comando no se ejecutó, escríbelo como "no ejecutado".

## Adaptación específica (turnos consecutivos)
Intervalos semiabiertos [inicio, fin): dos reservas se solapan si `inicio_a < fin_b and inicio_b < fin_a`.
Nunca uses `<=`. Toda prueba de borde debe incluir 10:00–11:00 seguido de 11:00–12:00 (permitido).

## Permisos
- Permitido: leer/editar archivos del repo, ejecutar `python -m unittest`, `python -m reservas ...`, `git add/commit/diff/log`.
- Requiere aprobación humana: borrar archivos, `git push`, `git reset --hard`, instalar paquetes, tocar fuera del repo.
- Prohibido: secretos, tokens, datos reales de estudiantes.

## Datos
- Persistencia: SQLite en `data/reservas.db` (ignorado por Git). Inventario inicial en `data/inventario.json` (versionado).
- `reset-datos` borra todas las reservas: pedir confirmación explícita (`--confirmar`).

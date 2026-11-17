# PROMPTS.md — prompts por tarea y pruebas a pedir al agente

Uso: pegá cada prompt en Pi (Orca) en orden. Después de cada tarea hacé el **checklist humano**, pegá la
salida REAL en `PROGRESS.md` y hacé commit. Los prompts son tu evidencia de "extracto de instrucción":
guardá el texto exacto que uses.

Contrato común (se fija en T2 y todas las pruebas lo usan):

```
src/reservas/errores.py   ErrorReserva > ErrorValidacion, ErrorSolape, ErrorNoEncontrado, ErrorEstado
src/reservas/dominio.py   Reserva (dataclass: id, unidad, solicitante, inicio, fin, estado)
                          se_solapan(a_ini, a_fin, b_ini, b_fin) -> bool   # a_ini < b_fin and b_ini < a_fin
                          parsear_fecha(texto) -> datetime                 # 'YYYY-MM-DDTHH:MM'
                          validar_solicitud(unidad, solicitante, inicio, fin, ahora, unidades_validas)
                              -> (solicitante_limpio, inicio_dt, fin_dt)
src/reservas/servicio.py  ServicioReservas(ruta_db, inventario, ahora=callable)
                          .listar_inventario() / .disponible(u, ini, fin) -> bool
                          .reservar(u, solicitante, ini, fin) -> Reserva
                          .cancelar(id) -> Reserva / .listar(estado=None) -> list[Reserva]
                          .cerrar()
```
Reloj fijo en pruebas: `AHORA = datetime(2026, 12, 1, 8, 0)`; fechas de prueba el `2026-12-01`.

---

## T1 — Esqueleto, inventario y .gitignore

**Prompt**
```
Lee AGENTS.md, README.md (sección 1) y PROGRESS.md. Tarea T1, solo esto:
1. Crea la estructura src/reservas/ (con __init__.py y __main__.py vacío), tests/ (con __init__.py), data/.
2. Crea data/inventario.json con exactamente estas 5 unidades: MIC-01 y MIC-02 (Microscopio digital),
   OSC-01 (Osciloscopio), MUL-01 (Multímetro), FUE-01 (Fuente de alimentación).
3. Crea .gitignore que excluya data/reservas.db, __pycache__/ y *.pyc.
4. Una prueba tests/test_inventario.py que cargue el JSON y verifique: 5 unidades, IDs únicos,
   y que MIC-01 y MIC-02 existen como unidades distintas.
No implementes reglas de negocio. Ejecuta python -m unittest -v y muestra la salida real.
```
**Pruebas a pedir:** 5 unidades; IDs únicos; MIC-01 ≠ MIC-02; cada unidad tiene `id` y `equipo` no vacíos.
**Checklist humano:** ¿los 5 IDs coinciden con la consigna? ¿`.gitignore` excluye la base? ¿corriste las pruebas vos?

---

## T2 — Dominio: validaciones y solape (Episodio 1)

**Prompt**
```
Tarea T2 (RN-02..RN-09, CA-01..CA-05, CA-08). Primero escribe las pruebas y confirma que FALLAN
(muestra la salida). Luego implementa errores.py y dominio.py con el contrato definido en PROMPTS.md.
Reglas: intervalos semiabiertos [inicio, fin); se_solapan usa SOLO comparaciones estrictas (nunca <=).
Validaciones: unidad conocida; solicitante no vacío ni solo espacios (strip); formato YYYY-MM-DDTHH:MM;
inicio < fin estricto; inicio no anterior a 'ahora'; duración máxima 8 h; anticipación máxima 90 días.
'ahora' se recibe por parámetro. Cada error lleva un mensaje claro en español.
No toques persistencia ni CLI. Ejecuta python -m unittest -v al final y pega la salida real.
```
**Pruebas a pedir** (`tests/test_dominio.py`):
| Caso | Esperado |
|---|---|
| 10:00–11:00 vs 10:30–11:30 | solapan |
| 10:00–11:00 vs 11:00–12:00 (y a la inversa) | NO solapan |
| 10:00–11:00 vs 10:00–11:00 idéntico | solapan |
| 09:00–12:00 vs 10:00–11:00 (contenido) | solapan |
| 10:00–11:00 vs 12:00–13:00 | NO solapan |
| unidad `XXX-99` | ErrorValidacion |
| solicitante `""`, `"   "`, `"\t"` | ErrorValidacion |
| solicitante `"  Ana Prueba  "` | válido, devuelve `"Ana Prueba"` |
| fecha `"2026-13-01T10:00"`, `"2026-12-01 10:00"`, `"hola"`, `"2026-02-30T10:00"` | ErrorValidacion |
| inicio == fin; inicio > fin | ErrorValidacion |
| inicio anterior a AHORA | ErrorValidacion |
| duración 8 h exactas | válido; 8 h 1 min → ErrorValidacion |
| inicio a 90 días exactos | válido; 90 días + 1 min → ErrorValidacion |

**Checklist humano:** ¿hay `<=` en el código? (buscalo con `grep`). **Prueba de mutación manual:** cambiá una
comparación de `<` a `<=` en `se_solapan` y confirmá que las pruebas fallan; revertí. Anotá el resultado.

---

## T3 — Servicio y persistencia SQLite (Episodio 2)

**Prompt**
```
Tarea T3 (RF-01, RF-02, RF-03, RF-05, RF-06, CA-01..CA-04, CA-07, CA-08). Pruebas primero, deben fallar.
Implementa servicio.py (ServicioReservas) y almacén SQLite con la biblioteca estándar.
- Tabla reservas: id INTEGER PK AUTOINCREMENT, unidad, solicitante, inicio, fin, estado ('activa'|'cancelada').
- reservar() valida con dominio.validar_solicitud, busca solapes SOLO contra reservas activas de la
  misma unidad usando dominio.se_solapan, y inserta dentro de una transacción.
- disponible() usa EXACTAMENTE las mismas validaciones y la misma función de solape que reservar().
- Debe poder cerrarse y reabrirse sobre el mismo archivo y recuperar todo.
- La inicialización carga el inventario desde data/inventario.json; reabrir NO borra reservas.
No implementes cancelar ni CLI todavía. Pega la salida real de python -m unittest -v.
```
**Pruebas a pedir** (`tests/test_servicio.py`, base en archivo temporal):
| Caso | Esperado |
|---|---|
| CA-01 crear MIC-01 10:00–11:00 "Ana Prueba" | id=1, estado `activa` |
| segundo reservar válido | id=2 (ids únicos y crecientes) |
| CA-02 MIC-01 10:00–11:00 y luego 10:30–11:30 | ErrorSolape; no se crea fila |
| CA-03 MIC-01 10:00–11:00 y luego 11:00–12:00 | ambas activas |
| CA-04 MIC-01 y MIC-02 el mismo 10:00–11:00 | ambas activas |
| reserva misma unidad, mismo horario distinto solicitante | ErrorSolape |
| `disponible` con solape / consecutivo / otra unidad | False / True / True |
| CA-08 para 20 intervalos, `disponible()` coincide con "reservar no lanza ErrorSolape" | coinciden |
| `disponible` con entrada inválida (unidad desconocida, inicio ≥ fin) | ErrorValidacion (no False) |
| reservar con entrada inválida | no deja filas en la base |
| CA-07 crear 2 reservas, `cerrar()`, nuevo `ServicioReservas` sobre el mismo archivo | `listar()` devuelve las 2 con mismos ids y datos |
| reabrir no reinicia el contador de ids | la nueva reserva tiene id=3 |

**Checklist humano:** ¿la comparación de solape está solo en `dominio`? ¿el servicio filtra por `estado='activa'`?
Ejecutá además el procedimiento manual de persistencia (ver T6) y anotá esperado vs observado.

---

## T4 — Cancelación (Episodio 3)

**Prompt**
```
Tarea T4 (RF-04, RN-01, RN-10, CA-06). Pruebas primero, deben fallar.
Implementa ServicioReservas.cancelar(id): cambia estado a 'cancelada' SIN borrar la fila ni alterar
id, unidad, solicitante, inicio, fin. Cancelar id inexistente -> ErrorNoEncontrado; cancelar una ya
cancelada -> ErrorEstado; en ambos casos no cambia ningún dato. Las canceladas no bloquean disponibilidad.
Pega la salida real de python -m unittest -v.
```
**Pruebas a pedir:**
| Caso | Esperado |
|---|---|
| cancelar reserva activa | estado `cancelada`, mismo id y mismos datos |
| `listar()` tras cancelar | la reserva sigue presente |
| `listar(estado="activa")` / `listar(estado="cancelada")` | filtran correctamente |
| tras cancelar MIC-01 10:00–11:00 → `disponible` 10:00–11:00 | True |
| tras cancelar → reservar 10:30–11:30 misma unidad | permitido |
| cancelar id 999 | ErrorNoEncontrado |
| cancelar dos veces | segundo intento ErrorEstado; datos intactos |
| cancelar, `cerrar()`, reabrir | la cancelada persiste como `cancelada` y sigue sin bloquear |
| cancelar una de dos reservas de unidades distintas | la otra queda `activa` |

**Checklist humano:** ¿el SQL hace `UPDATE` y no `DELETE`? Revisá el diff antes de aceptar.

---

## T5 — CLI

**Prompt**
```
Tarea T5. Implementa src/reservas/cli.py (argparse) y __main__.py con los subcomandos:
init, inventario, disponibilidad U INI FIN, reservar U "SOLICITANTE" INI FIN, cancelar ID,
listar [--estado activa|cancelada], reset-datos --confirmar.
La CLI NO contiene reglas de negocio: solo llama a ServicioReservas. Ruta de base por defecto
data/reservas.db, sobrescribible con --db. Errores de negocio: mensaje claro por stderr y código de
salida 1; éxito: 0. reset-datos sin --confirmar no borra nada y sale con error.
Pruebas con subprocess o llamando a main(argv). Pega salida real de las pruebas y de un ejemplo de
uso completo (init, reservar, solape rechazado, cancelar, listar).
```
**Pruebas a pedir** (`tests/test_cli.py`, `--db` temporal):
| Caso | Esperado |
|---|---|
| `init` + `inventario` | muestra 5 unidades, código 0 |
| `reservar` válido | imprime id, código 0 |
| `reservar` solapado | código 1, mensaje en stderr, nada nuevo en `listar` |
| `reservar` con solicitante `"   "` | código 1 |
| `cancelar` inexistente | código 1 |
| `reset-datos` sin `--confirmar` | código ≠ 0, reservas intactas |
| `reset-datos --confirmar` | reservas borradas, inventario intacto |

**Checklist humano:** ejecutá el ejemplo vos y copiá la salida real al README (sección 2).

---

## T6 — README, persistencia manual y cierre

**Prompt**
```
Tarea T6. Completa SOLO los hechos verificables en las secciones 2 de README.md: estructura real del
repo, versión de Python (salida de python --version), comandos reales, ejemplo real de entrada/salida,
dónde persisten los datos, advertencia de reset-datos, pendientes y limitaciones. Crea
docs/persistencia.md con un procedimiento manual reproducible (comandos, resultado esperado). No
inventes resultados: deja "no ejecutado" donde corresponda. No toques la sección 3 ni 4.
```
**Procedimiento manual de persistencia** (`docs/persistencia.md`; ejecutalo vos y completá "observado"):
1. `python -m reservas --db /tmp/p.db init`
2. `reservar MIC-01 "Ana Prueba" 2026-12-01T10:00 2026-12-01T11:00` → esperado: id 1.
3. `reservar OSC-01 "Beto Prueba" 2026-12-01T10:00 2026-12-01T11:00` → id 2.
4. `cancelar 2`.
5. (Proceso terminado = "reinicio".) `listar` → esperado: id 1 `activa`, id 2 `cancelada`.
6. `disponible OSC-01 10:00–11:00` → sí; `reservar MIC-01 10:30–11:30` → rechazado.

**Checklist final:** pruebas verdes ejecutadas por vos; `git log` con la especificación inicial y cambios;
rama y commit anotados; secciones 3 y 4 con evidencia real; sin secretos; repo accesible; email enviado con
asunto exacto «Challenge IA».

---

## Plantilla para registrar cada episodio (sección 4.2)

```
Objetivo/requisito: <RF/RN/CA>
Contexto e instrucción: <archivos dados al agente> + extracto del prompt de arriba
Resultado del agente: <qué produjo, pruebas que pasaron/fallaron>
Decisión humana: aceptar | corregir | rechazar — motivo: <...>
Evidencia: <commit hash / tests/archivo::prueba / salida>
```
Registrá una corrección solo si ocurrió. Si el agente acertó a la primera, escribilo así.

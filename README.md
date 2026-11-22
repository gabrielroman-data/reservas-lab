# Sistema de reservas de laboratorio con agentes (Challenge IA)

Proyecto individual. Solución local pequeña y verificable, construida con un agente de programación bajo revisión humana. Este README explica qué se construyó y cómo se comprobó; la evidencia de uso del agente está en `docs/`.

---

## 1. Especificación breve

### 1.1 Problema
La coordinación de un laboratorio registra pedidos en mensajes y una planilla. A veces confirma la misma unidad en horarios superpuestos; otras veces una cancelación sigue bloqueando el horario. Necesita consultar disponibilidad, reservar y cancelar sin perder el historial.

### 1.2 Alcance
**Dentro:** leer el inventario precargado, consultar disponibilidad por unidad e intervalo, crear reservas (una unidad por reserva), cancelar conservando el registro, persistir y recuperar tras reiniciar.

**Fuera:** autenticación y roles, notificaciones, pagos, integraciones externas, despliegue, interfaz gráfica, concurrencia distribuida, administración del inventario.

### 1.3 Inventario (cada ID es una unidad física distinta)
| ID | Equipo |
|---|---|
| MIC-01 | Microscopio digital |
| MIC-02 | Microscopio digital |
| OSC-01 | Osciloscopio |
| MUL-01 | Multímetro |
| FUE-01 | Fuente de alimentación |

### 1.4 Requisitos funcionales
| ID | Requisito |
|---|---|
| RF-01 | Listar el inventario precargado. |
| RF-02 | Consultar si una unidad está disponible en un intervalo [inicio, fin). |
| RF-03 | Crear una reserva con unidad, solicitante, inicio y fin; devuelve un identificador único. |
| RF-04 | Cancelar una reserva por identificador: conserva id y datos, pasa a estado `cancelada`, libera el intervalo. |
| RF-05 | Listar reservas (activas y canceladas) con su estado. |
| RF-06 | Persistir reservas y estados; recuperarlos al reiniciar la aplicación. |

### 1.5 Reglas de negocio
| ID | Regla |
|---|---|
| RN-01 | Una reserva **activa** ocupa su intervalo; una **cancelada** no bloquea. |
| RN-02 | La unidad debe existir en el inventario. |
| RN-03 | El solicitante no puede ser vacío ni solo espacios (se recorta con `strip`). |
| RN-04 | Fechas y horas válidas en formato `YYYY-MM-DDTHH:MM`. |
| RN-05 | Inicio estrictamente anterior al fin. |
| RN-06 | Se rechazan superposiciones de reservas activas de la **misma** unidad. |
| RN-07 | Intervalos semiabiertos: los límites consecutivos se permiten (10:00–11:00 y 11:00–12:00). |
| RN-08 | Unidades distintas pueden reservarse simultáneamente. |
| RN-09 | La consulta de disponibilidad aplica exactamente las mismas validaciones y la misma regla de solape que la creación. |
| RN-10 | Cancelar una reserva ya cancelada o inexistente es un error explícito y no altera datos. |

### 1.6 Supuestos (decisiones no especificadas)
- Zona horaria: America/Argentina/Buenos_Aires (UTC-03:00). Las horas se guardan sin zona, en hora local, sin conversión.
- Formato: ISO 8601 sin zona, `YYYY-MM-DDTHH:MM` (precisión de minutos).
- Fechas pasadas: se **rechazan** (inicio anterior a "ahora"). El reloj es inyectable para poder probar.
- Límites: sin límite de duración ni de anticipación. La única condición es que el inicio sea estrictamente anterior al fin.
- Identificador de reserva: entero autoincremental.
- Solicitantes ficticios únicamente.

### 1.7 Criterios de aceptación
| ID | Dado / Cuando / Entonces | Cubre |
|---|---|---|
| CA-01 | Dado MIC-01 libre, cuando reservo 10:00–11:00 para "Ana Prueba", entonces se crea con id y estado `activa`. | RF-03 |
| CA-02 | Dado MIC-01 reservado 10:00–11:00, cuando reservo 10:30–11:30, entonces se rechaza. | RN-06 |
| CA-03 | Dado MIC-01 reservado 10:00–11:00, cuando reservo 11:00–12:00, entonces se permite. | RN-07 |
| CA-04 | Dado MIC-01 reservado 10:00–11:00, cuando reservo MIC-02 10:00–11:00, entonces se permite. | RN-08 |
| CA-05 | Unidad desconocida, solicitante vacío o "   ", fecha inválida, inicio ≥ fin o inicio en el pasado: rechazo con mensaje claro. | RN-02 a RN-05, supuestos |
| CA-06 | Dada una reserva activa, cuando la cancelo, entonces sigue listada con estado `cancelada` y su intervalo vuelve a estar disponible. | RF-04, RN-01 |
| CA-07 | Dadas reservas activas y canceladas, cuando detengo y reinicio la aplicación sin borrar datos, entonces se recuperan con los mismos ids y estados. | RF-06 |
| CA-08 | La consulta de disponibilidad devuelve lo mismo que habría decidido la creación para el mismo intervalo (incluidas las validaciones). | RN-09 |

### 1.8 Evolución de la especificación
- Versión inicial: tag `spec-v1` (commit `5ccee8e`).
- Cambio: se quitan los límites de 8 horas de duración y 90 días de anticipación (supuestos 1.6 y criterio CA-05). Motivo: simplificar el alcance y reducir pruebas. Commit `673fc18`.
- Los ajustes de diseño posteriores (D-05 a D-09) están en la sección 4.

---

## 2. Solución

### Estructura
```
reservas/              paquete de la aplicación
  dominio.py           fechas, validaciones y regla de solape (única función se_solapan)
  errores.py           errores de negocio
  persistencia.py      almacenamiento SQLite
  servicio.py          casos de uso (reservar, disponible, cancelar, listar)
  cli.py, __main__.py  interfaz de consola
tests/                 pruebas automáticas (inventario, dominio, servicio, consola)
data/inventario.json   inventario precargado (5 unidades)
docs/prompts/          prompts exactos dados al agente, por tarea
docs/evidencia/        salidas de pruebas, mutaciones e incidentes
docs/persistencia.md   procedimiento manual de persistencia
AGENTS.md              instrucciones del agente
PROGRESS.md            progreso y bitácora
PROMPTS.md             plan de prompts y pruebas (es un plan, no evidencia de uso)
```

### Decisiones técnicas
Python con biblioteca estándar (sin dependencias, por eso no hay archivo de bloqueo), SQLite local, consola con argparse y pruebas con unittest. Una única función de dominio para la superposición (`se_solapan`). El detalle está en la sección 4.

### Requisitos previos y versiones
- Python 3.11 o superior. Probado con Python 3.14.3.
- Git.
- No hace falta ninguna cuenta de modelo de IA para ejecutar la aplicación ni las pruebas.

### Instalación y carga inicial
```
git clone https://github.com/gabrielroman-data/reservas-lab.git
cd reservas-lab
python -m reservas init
```
El inventario de 5 unidades se lee de `data/inventario.json`. `init` crea la base de datos si no existe.

### Comandos de la aplicación
Comandos disponibles (según `python -m reservas --help`): `init`, `inventario`, `disponibilidad`, `reservar`, `cancelar`, `listar` y `reiniciar-datos`, más la opción global `--db`.
```
python -m reservas init
python -m reservas inventario
python -m reservas disponibilidad UNIDAD INICIO FIN
python -m reservas reservar UNIDAD "SOLICITANTE" INICIO FIN
python -m reservas cancelar ID
python -m reservas listar [--estado activa|cancelada]
python -m reservas reiniciar-datos --confirmar
python -m reservas --db OTRA_RUTA.db listar
```
Formato de fecha: `YYYY-MM-DDTHH:MM`. Códigos de salida: 0 éxito; 1 rechazo por regla o validación (mensaje en stderr); 2 uso incorrecto.

### Ejemplo de entrada y salida (ejecución real)
```
$ python -m reservas --db /tmp/demo.db init
$ python -m reservas --db /tmp/demo.db reservar MIC-01 "Ana Prueba" 2099-12-01T10:00 2099-12-01T11:00
Reserva creada exitosamente con ID 1.
$ python -m reservas --db /tmp/demo.db reservar MIC-01 "Bruno Prueba" 2099-12-01T10:30 2099-12-01T11:30
Error: La unidad 'MIC-01' ya se encuentra reservada en el intervalo especificado.
$ python -m reservas --db /tmp/demo.db cancelar 1
Reserva 1 cancelada exitosamente.
$ python -m reservas --db /tmp/demo.db listar
ID 1 | MIC-01 | Ana Prueba | 2099-12-01T10:00 | 2099-12-01T11:00 | cancelada
$ python -m reservas --db /tmp/demo.db disponibilidad MIC-01 2099-12-01T10:00 2099-12-01T11:00
DISPONIBLE: la unidad MIC-01 se puede reservar en el intervalo 2099-12-01T10:00 - 2099-12-01T11:00.
```
`init` no imprime nada. Los ejemplos usan fechas de 2099 porque la consola usa la hora real de la computadora y se rechazan las fechas pasadas.

### Pruebas
```
python -m unittest -v
```
Resultado de mi ejecución con Python 3.14.3: 48 pruebas, OK (salida en `docs/evidencia/t5-pruebas-pasan.txt`). Cubren creación válida, rechazo de superposición, turnos consecutivos, unidades distintas simultáneas, entradas inválidas, cancelación que conserva el registro y libera el horario, y persistencia entre procesos.

### Dónde persisten los datos
En `data/reservas.db` (SQLite), o en la ruta indicada con `--db`. El archivo no se versiona (`.gitignore`). **Advertencia: `reiniciar-datos --confirmar` borra todas las reservas, activas y canceladas.** Sin `--confirmar` no borra nada.

### Registro de verificaciones
| Qué | Comando o procedimiento | Resultado | Quién |
|---|---|---|---|
| Prueba de lectura de AGENTS.md | prompt en Pi y `git status` después | `docs/evidencia/prueba-agents.md` | agente y yo |
| Mutación T1 (ID repetido en el inventario) | `python -m unittest -v` | FAIL esperado y OK al restaurar: `t1-mutacion-falla.txt` y `t1-mutacion-restaurado.txt` | yo |
| Mutación T2 (comparación de `se_solapan`) | `python -m unittest -v` | FAIL en `test_rn07_consecutivos_permitidos_orden_2`: `t2-mutacion-falla.txt` | yo |
| Mutación T3, T4 y T5 | no ejecutada | no ejecutada | no ejecutada |
| Pruebas finales | `python -m unittest -v` | 48 pruebas, OK | yo |
| Persistencia tras reiniciar | `docs/persistencia.md` | esperado y observado coinciden | yo |
| Clon limpio en otra carpeta | `git clone`, pruebas y consola | no ejecutado | no ejecutado |

### Pendientes y limitaciones
- Un solo proceso a la vez: no hay control de concurrencia entre procesos ni equipos (fuera de alcance).
- No verifiqué que la comprobación de superposición y la inserción ocurran dentro de la misma transacción SQLite; `BEGIN IMMEDIATE` está presente en la inserción. Queda como limitación.
- Las horas son hora local sin zona. Por defecto el reloj es el de la computadora; la especificación supone Argentina UTC-3 y no hay conversión de zona.
- Las pruebas de consola usan fechas de 2099 porque la consola usa la hora real y se rechazan las fechas pasadas. Las pruebas de dominio y servicio inyectan un reloj fijo.
- `strptime` puede aceptar números sin cero inicial (por ejemplo `2026-12-1T10:00`); no hay prueba para ese caso.
- No hay límites de duración ni de anticipación (decisión D-08).
- Se puede cancelar una reserva aunque su horario ya haya pasado.
- La prueba de consola del caso libre busca el texto "disponible", que también aparece en "NO DISPONIBLE"; esa comprobación es débil.
- No hay prueba de mutación para el filtro de reservas activas ni para la consola.
- En una prueba de consola capturada en Windows se perdió una tilde ("no est disponible"); no investigué la causa.

---

## 3. Preparación del agente

### Entorno y modelo
- Agente (harness): Pi 1.5.0 con la extensión gentle-pi activa, ejecutado desde Git Bash en Windows. Pi estaba instalado antes de empezar, fuera de npm (probablemente con el instalador de PowerShell). La barra de Pi mostraba el nivel de razonamiento `low`.
- gentle-pi: se vio su panel (agentes, cambios e integraciones) y una integración de memoria con el estado `ready`. No usé sus flujos de especificación y no verifiqué qué guarda esa memoria.
- Orca: se evaluó y no se usó.
- Modelo: gemini-3.6-flash (API de Gemini, plan gratuito, clave propia) en la prueba de lectura, T1, T3, T4 y T5. En T2a y T2b el modelo no quedó registrado.
- Intentos descartados: OpenRouter con `google/gemma-4-26b-a4b-it:free` (error 429) y gemini-3.8-flash (error 503 por alta demanda). Ver `docs/evidencia/incidentes.md`.
- Motivo de la elección: es gratuito y funciona dentro de Pi sin suscripción. Su límite es el cupo del plan gratuito (por minuto, por tokens y por día), que cortó el trabajo varias veces.
- Claude (chat gratuito de claude.ai) se usó fuera del repositorio como ayuda para redactar borradores de la especificación, de `AGENTS.md`, del plan de prompts y de los pasos de verificación. No actuó sobre el repositorio; revisé y apliqué lo que usé.

### Instrucciones y configuración
`AGENTS.md` en la raíz, leído por Pi (la prueba de lectura lo confirma). Extracto:
```
- Escribe primero la prueba y confirma que falla; luego implementa.
- Solo biblioteca estándar de Python 3.11+.
- Toda regla de negocio vive en reservas/dominio.py; la CLI y el almacenamiento no la duplican.
- La disponibilidad y la creación usan la MISMA función de solape.
- Hora actual inyectable (parámetro ahora), nunca datetime.now() dentro de las reglas.
- Intervalos semiabiertos: se_solapan usa solo comparaciones estrictas, nunca <=.
- Requiere aprobación humana: borrar archivos, git push, git reset --hard, instalar paquetes, tocar fuera del repo.
```
La configuración de Pi y gentle-pi está fuera del repositorio, en `C:\Users\gabri\.pi\agent\`. No la modifiqué y no incluyo credenciales.

### Contexto suministrado y excluido
Suministrado: `AGENTS.md`, la especificación (sección 1 de este README), `PROMPTS.md`, el inventario, el código existente y un prompt por tarea (`docs/prompts/`). Excluido: credenciales, la carpeta de configuración de Pi y datos reales.

### Herramientas, permisos y aprobaciones
Pi puede leer y escribir archivos y ejecutar comandos en mi computadora. No configuré un bloqueo técnico: el control fue la instrucción de `AGENTS.md`, el aviso explícito en cada prompt ("No ejecutes git push ni comandos fuera de esta carpeta"), la lectura de los comandos que ejecutaba y que los commits y el `git push` los hice yo. Antes de aceptar cada tarea revisé los diffs y corrí las pruebas yo mismo.

### Adaptación específica con evidencia
Regla de turnos consecutivos (intervalos semiabiertos, nunca `<=`), escrita en `AGENTS.md`. Evidencia: las pruebas `test_rn07_consecutivos_permitidos_orden_1` y `_orden_2`, y la mutación de T2, donde el cambio a `<=` hizo fallar `test_rn07_consecutivos_permitidos_orden_2` (`docs/evidencia/t2-mutacion-falla.txt`).

### Retención del progreso
`PROGRESS.md` (versionado) y `docs/prompts/`. El agente escribió parte de `PROGRESS.md`, incluidas las columnas "Decisión humana", y en una fila puso una fecha inventada (corregida). Las decisiones humanas válidas son las de la sección 4 de este README.

---

## 4. Registro de decisiones y delegación

### Decisiones significativas
| # | Decisión | Motivo | Alternativas | Consecuencias |
|---|---|---|---|---|
| D-01 | SQLite como almacenamiento | Transaccional y de la biblioteca estándar | Archivo JSON | Algo más de código; más robusto |
| D-02 | Intervalos semiabiertos [inicio, fin) | Permiten turnos consecutivos | Intervalos cerrados | Una sola comparación estricta |
| D-03 | Reloj inyectable (`ahora`) | Pruebas deterministas | `datetime.now()` dentro de las reglas | Parámetro extra |
| D-04 | Rechazar inicio anterior a "ahora" | Evita registros incoherentes | Permitir fechas pasadas | Las pruebas fijan el reloj |
| D-05 | Paquete en `reservas/` en la raíz | El import desde `src/` fallaba | Configurar PYTHONPATH | `python -m` funciona sin configuración. Commit `a5f07a7` |
| D-06 | Separar `validar_intervalo` de `validar_solicitud` | `disponible()` no tiene solicitante y debe usar las mismas validaciones | Pasar un solicitante falso | Cambia el orden de validación: ahora se revisa antes el solicitante. Commit `a937e7c` |
| D-07 | Mensajes `DISPONIBLE:` y `NO DISPONIBLE:` en la consola | Mensaje claro y fácil de comprobar | Cambiar el texto que esperaba la prueba | Commit de T5 |
| D-08 | Sin límites de 8 h ni de 90 días | Reducir alcance y pruebas | Mantenerlos | Se aceptan reservas muy largas. Commit `673fc18` |
| D-09 | Pi ejecutado desde Git Bash, sin Orca | Un solo entorno para correr las verificaciones | Usar Orca | Sin la vista de diffs de Orca |

### Episodio 1: reglas de dominio y solapes (T2, RN-02 a RN-07)
- **Objetivo y requisito:** validaciones y regla de superposición.
- **Contexto e instrucción:** `AGENTS.md`, la sección 1 de este README y `PROMPTS.md`. Prompts exactos en `docs/prompts/t2a.md` (solo pruebas, deben fallar) y `docs/prompts/t2b.md` (código). Extracto: "se_solapan usa solo comparaciones estrictas, nunca <="; "parsear_fecha usa strptime".
- **Resultado del agente:** `tests/test_dominio.py` (14 pruebas) y después `reservas/dominio.py` y `errores.py`, con 17 pruebas en OK según su informe.
- **Revisión y decisión humana:** acepté con correcciones. (1) El agente informó que las pruebas fallaban porque faltaba `dominio.py`; el error real era `No module named 'reservas'`, porque el paquete estaba en `src/`. Moví el paquete (D-05). (2) Con `grep` encontré en un comentario una fórmula con `<=` que contradecía `AGENTS.md`; el código real era correcto. Corregí el comentario. (3) Mi primera mutación se aplicó por error al comentario y las pruebas siguieron en OK; la repetí sobre la línea de código y falló `test_rn07_consecutivos_permitidos_orden_2`. Corrí las pruebas yo mismo: OK.
- **Evidencia:** commits `a5f07a7`, `490035d`, `c165af3`, `b08460b` y `1607c23`; `docs/prompts/t2a.md`, `docs/prompts/t2b.md` y `docs/evidencia/t2-mutacion-falla.txt`.

### Episodio 2: servicio y persistencia (T3, RF-03, RF-06, RN-09)
- **Objetivo y requisito:** reservar, consultar disponibilidad con las mismas reglas y persistir.
- **Contexto e instrucción:** `docs/prompts/t3a.md` (pruebas primero) y `docs/prompts/t3b.md`. Extracto: "disponible() usa la MISMA verificación de solape que reservar() (una función interna compartida)".
- **Resultado del agente:** 13 pruebas de servicio que fallaban por el motivo correcto (`No module named 'reservas.servicio'`); después `servicio.py`, `persistencia.py` y `validar_intervalo`, con 30 pruebas en OK según su informe.
- **Revisión y decisión humana:** acepté con observaciones. Revisé los diffs de `tests/test_servicio.py` y `reservas/dominio.py`: en las pruebas solo se agregaron las comprobaciones permitidas y `se_solapan` no se tocó. Con `grep` comprobé que `se_solapan` se usa una sola vez (en una función compartida por `reservar()` y `disponible()`), que existe `BEGIN IMMEDIATE` y que la consulta filtra por unidad y por estado `activa`. El informe de Pi tenía un nombre de prueba reescrito (`interval_contenido`), por eso confié solo en mis corridas. La corrida final de 48 pruebas, que incluye estas 30, la hice yo: OK. La mutación de T3 no se ejecutó.
- **Evidencia:** commits `813bfdd`, `a92946f` y `a937e7c`; `docs/prompts/t3a.md`, `docs/prompts/t3b.md` y `docs/evidencia/t3a-pruebas-fallan.txt`.

### Episodio 3: cancelación y consola (T4 y T5, RF-04, RN-10 y consola)
- **Objetivo y requisito:** cancelar conservando el registro y liberando el horario; interfaz de consola.
- **Contexto e instrucción:** `docs/prompts/t4.md` y `docs/prompts/t5.md`. Extracto: "UPDATE del estado a 'cancelada' (nunca DELETE)"; "La consola NO contiene reglas de negocio: solo llama a ServicioReservas".
- **Resultado del agente:** T4: 7 pruebas nuevas y `cancelar()`, con 37 pruebas en OK según su informe. T5: `tests/test_cli.py`, `cli.py` y cambios en `servicio.py` y `persistencia.py`; el trabajo se cortó por el límite de tokens por minuto.
- **Revisión y decisión humana:** T4 aceptada tras mis corridas de pruebas. T5 aceptada con correcciones: (1) `cli.py` usaba `Path` en la línea 2 antes de importarlo (línea sobrante, la borré); (2) `__main__.py` quedó vacío y escribí yo su contenido; (3) la prueba de disponibilidad no coincidía con el mensaje y decidí D-07; (4) la comprobación del caso libre es débil (queda en las limitaciones). El ejemplo real de la sección 2 y la corrida de 48 pruebas (OK) las ejecuté yo.
- **Evidencia:** commits `7422d74`, `ac9fa5e` y `32e8c4a` (prompts y T4), y el commit de T5 que le sigue en `git log`; `docs/prompts/t4.md`, `docs/prompts/t5.md` y `docs/evidencia/t5-pruebas-pasan.txt`.

### Otros registros
- El agente escribió la fecha `2025-05-18` en `PROGRESS.md` (T1); la fecha real era 2026-11-19, y la corregí.
- En la prueba de mutación de T1 copié el respaldo del inventario después de romperlo y reescribí `data/inventario.json` a mano. Error mío, no del agente.
- Errores 429 y 503 del proveedor en varias tareas: `docs/evidencia/incidentes.md`.

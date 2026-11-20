# Sistema de reservas de laboratorio con agentes (Challenge IA)

Proyecto individual. Solución local pequeña y verificable construida con un agente de programación.
Los apartados marcados con `TODO` se completan con evidencia real durante el trabajo.

\---

## 1\. Especificación breve

### 1.1 Problema

La coordinación de un laboratorio registra pedidos en mensajes y una planilla. A veces confirma la misma
unidad en horarios superpuestos; otras veces una cancelación sigue bloqueando el horario. Necesita consultar
disponibilidad, reservar y cancelar sin perder el historial.

### 1.2 Alcance

**Dentro:** leer inventario precargado, consultar disponibilidad por unidad e intervalo, crear reservas
(una unidad por reserva), cancelar conservando el registro, persistir y recuperar tras reiniciar.
**Fuera:** autenticación/roles, notificaciones, pagos, integraciones externas, despliegue, interfaz gráfica,
concurrencia distribuida, administración del inventario.

### 1.3 Inventario (cada ID es una unidad física distinta)

|ID|Equipo|
|-|-|
|MIC-01|Microscopio digital|
|MIC-02|Microscopio digital|
|OSC-01|Osciloscopio|
|MUL-01|Multímetro|
|FUE-01|Fuente de alimentación|

### 1.4 Requisitos funcionales

|ID|Requisito|
|-|-|
|RF-01|Listar el inventario precargado.|
|RF-02|Consultar si una unidad está disponible en un intervalo \[inicio, fin).|
|RF-03|Crear una reserva con unidad, solicitante, inicio y fin; devuelve un identificador único.|
|RF-04|Cancelar una reserva por identificador: conserva id y datos, pasa a estado `cancelada`, libera el intervalo.|
|RF-05|Listar reservas (activas y canceladas) con su estado.|
|RF-06|Persistir reservas y estados; recuperarlos al reiniciar la aplicación.|

### 1.5 Reglas de negocio

|ID|Regla|
|-|-|
|RN-01|Una reserva **activa** ocupa su intervalo; una **cancelada** no bloquea.|
|RN-02|La unidad debe existir en el inventario.|
|RN-03|El solicitante no puede ser vacío ni solo espacios (se recorta con `strip`).|
|RN-04|Fechas/horas válidas en formato `YYYY-MM-DDTHH:MM`.|
|RN-05|Inicio estrictamente anterior al fin.|
|RN-06|Se rechazan superposiciones de reservas activas de la **misma** unidad.|
|RN-07|Intervalos semiabiertos: límites consecutivos permitidos (10:00–11:00 y 11:00–12:00).|
|RN-08|Unidades distintas pueden reservarse simultáneamente.|
|RN-09|La consulta de disponibilidad aplica exactamente las mismas validaciones y la misma regla de solape que la creación.|
|RN-10|Cancelar una reserva ya cancelada o inexistente es un error explícito; no altera datos.|

### 1.6 Supuestos (decisiones no especificadas)

* Zona horaria: America/Argentina/Buenos\_Aires (UTC-03:00). Las horas se guardan "naive" en hora local, sin conversión.
* Formato: ISO 8601 sin zona, `YYYY-MM-DDTHH:MM` (precisión de minutos).
* Fechas pasadas: se **rechazan** (inicio anterior a "ahora"). El reloj es inyectable para poder probar.
* Límites: sin límite de duración ni de anticipación. La única condición es que el inicio sea estrictamente anterior al fin.
* Identificador de reserva: entero autoincremental.
* Solicitantes ficticios únicamente.

### 1.7 Criterios de aceptación

|ID|Dado / Cuando / Entonces|Cubre|
|-|-|-|
|CA-01|Dado MIC-01 libre, cuando reservo 10:00–11:00 para "Ana Prueba", entonces se crea con id y estado `activa`.|RF-03|
|CA-02|Dado MIC-01 reservado 10:00–11:00, cuando reservo 10:30–11:30, entonces se rechaza.|RN-06|
|CA-03|Dado MIC-01 reservado 10:00–11:00, cuando reservo 11:00–12:00, entonces se permite.|RN-07|
|CA-04|Dado MIC-01 reservado 10:00–11:00, cuando reservo MIC-02 10:00–11:00, entonces se permite.|RN-08|
|CA-05|Unidad desconocida, solicitante vacío o "   ", fecha inválida, inicio ≥ fin, pasado → rechazo con mensaje claro.|RN-02..05, supuestos|
|CA-06|Dada una reserva activa, cuando la cancelo, entonces sigue listada con estado `cancelada` y su intervalo vuelve a estar disponible.|RF-04, RN-01|
|CA-07|Dadas reservas activas y canceladas, cuando detengo y reinicio la aplicación sin borrar datos, entonces se recuperan con los mismos ids y estados.|RF-06|
|CA-08|La consulta de disponibilidad devuelve lo mismo que habría decidido la creación para el mismo intervalo (incluidas validaciones).|RN-09|

### 1.8 Evolución de la especificación

TODO: enlazar commits de la versión inicial y de cada cambio significativo, con el motivo.

\---

## 2\. Solución

TODO (completar con lo realmente construido):

* Estructura del repositorio (`src/reservas/`, `tests/`, `data/`).
* Decisiones técnicas: Python 3.11+, solo biblioteca estándar, SQLite, CLI con `argparse`.
* Requisitos previos y versiones (registrar salida real de `python --version`).
* Instalación y carga inicial: comando de inicialización desde `data/inventario.json`.
* Comandos de la aplicación y de pruebas (`python -m unittest -v`).
* Ejemplo de entrada y salida (copiar una ejecución real).
* Dónde persisten los datos: `data/reservas.db`. **Advertencia: `reset-datos` borra todas las reservas.**
* Pendientes y limitaciones conocidas.

Comandos previstos de la CLI:

```
python -m reservas init
python -m reservas inventario
python -m reservas disponibilidad MIC-01 2026-12-01T10:00 2026-12-01T11:00
python -m reservas reservar MIC-01 "Ana Prueba" 2026-12-01T10:00 2026-12-01T11:00
python -m reservas cancelar 1
python -m reservas listar
python -m reservas reset-datos --confirmar
```

### Verificación (registro de ejecución real)

|Qué|Comando / procedimiento|Versión|Resultado|Quién lo ejecutó|
|-|-|-|-|-|
|Pruebas automáticas|`python -m unittest -v`|TODO|TODO|humano|
|Persistencia tras reinicio|procedimiento manual reproducible (ver `docs/persistencia.md`)|TODO|TODO|humano|

\---

## 3\. Preparación del agente

TODO (solo datos reales y visibles; si un dato no es visible, escribir "no visible"):

* Entorno: Orca (versión: TODO). Agente: Pi (versión: TODO). Modelo: Claude (identificador exacto: TODO o "no visible"). Gentle AI: TODO función.
* Función de cada pieza y motivo de la elección.
* Instrucciones usadas: `AGENTS.md` (extracto en este repo). Si hay configuración externa, incluir extracto y cómo se aplicó.
* Contexto suministrado: README (Especificación), `PROGRESS.md`, inventario. Excluido: secretos, datos reales, conversaciones privadas.
* Permisos: ver `AGENTS.md`. Aprobaciones humanas previstas y aplicadas: TODO.
* Adaptación específica: regla de intervalos semiabiertos / turnos consecutivos (en `AGENTS.md`). Evidencia de uso: TODO enlace a commit/prueba.
* Retención de progreso: `PROGRESS.md`, versionado en Git.

\---

## 4\. Registro de decisiones y delegación

### 4.1 Decisiones significativas

|#|Decisión|Motivo|Alternativas|Consecuencias|
|-|-|-|-|-|
|D-01|SQLite como almacenamiento|Transaccional, stdlib, sin dependencias|JSON plano|Algo más de código; más robusto|
|D-02|Intervalos semiabiertos \[inicio, fin)|Permite turnos consecutivos|Cerrados|Una sola comparación estricta|
|D-03|Reloj inyectable|Pruebas deterministas con fechas pasadas/futuras|`datetime.now()` directo|Parámetro extra|
|D-04|Rechazar fechas pasadas|Evita registros incoherentes|Permitirlas|Pruebas necesitan reloj fijo|

### 4.2 Episodios de delegación

Para cada uno: objetivo/requisito → contexto + extracto de instrucción → acción/resultado del agente →
decisión humana (aceptar/corregir/rechazar + motivo) → enlace verificable. Registrar correcciones solo si ocurrieron.

**Episodio 1 — Reglas de dominio y solapes (RN-02..RN-09)**

* Objetivo/requisito: TODO
* Contexto y extracto de instrucción: TODO
* Acción/resultado del agente: TODO
* Decisión humana y motivo: TODO
* Evidencia (commit / prueba): TODO

**Episodio 2 — Persistencia y reinicio (RF-06, CA-07)**

* Objetivo/requisito: TODO
* Contexto y extracto de instrucción: TODO
* Acción/resultado del agente: TODO
* Decisión humana y motivo: TODO
* Evidencia (commit / prueba): TODO

**Episodio 3 — Cancelación y CLI (RF-04, RN-10, CA-06)**

* Objetivo/requisito: TODO
* Contexto y extracto de instrucción: TODO
* Acción/resultado del agente: TODO
* Decisión humana y motivo: TODO
* Evidencia (commit / prueba): TODO

> Versión entregada: rama `TODO`, commit `TODO`.


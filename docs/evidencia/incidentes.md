\# Incidentes y límites de acceso



Registro de errores y problemas reales del trabajo con el agente. Cada entrada indica fecha, herramienta, modelo, qué pasó y qué decidí.



\## 2026-11-17 \~22:41 - Error 429 con OpenRouter

\- Herramienta: Pi 1.5.0 (gentle-pi activo)

\- Modelo: google/gemma-4-26b-a4b-it:free, vía OpenRouter (clave de API)

\- Qué intenté: prueba de solo lectura sobre AGENTS.md

\- Resultado: error 429 tras 3 reintentos; límite temporal del proveedor, en un cupo compartido.

\- Decisión: dejar OpenRouter y usar una clave propia de la API de Gemini.



\## 2026-11-18 \~19:54 - Error 503 con Gemini

\- Modelo: gemini-3.8-flash (API de Gemini, plan gratuito)

\- Resultado: error 503 por alta demanda, tras 3 reintentos.

\- Decisión: cambiar a gemini-3.6-flash. La prueba de lectura funcionó con ese modelo (ver prueba-agents.md).



\## 2026-11-19 - Errores durante la tarea T1

\- Modelo: gemini-3.6-flash

\- Resultado: dos errores 503 y varios 429 por el límite de 5 solicitudes por minuto del plan gratuito. Completé T1 pidiéndole al agente que continuara sin repetir lo hecho.

\- Observación: el agente escribió la fecha 2025-05-18 en PROGRESS.md; la fecha real era 2026-11-19. COMPLETAR: anotar cuándo y cómo lo corregí.

\- Error mío: en la prueba de mutación de T1 copié el respaldo del inventario después de romperlo, así que ambos archivos quedaron con un ID repetido. Reescribí data/inventario.json a mano y confirmé OK.



\## 2026-11-20 - T2a: causa del fallo mal informada

\- El agente dijo que las pruebas fallaban porque dominio.py no existía. El error real era "No module named 'reservas'": el paquete estaba en src/ y Python no lo encontraba.

\- Decisión mía: mover el paquete a reservas/ en la raíz (D-05).

\- El agente no actualizó PROGRESS.md al terminar T2a.



\## 2026-11-20 \~01:15 - Cupo diario agotado

\- Modelo: gemini-3.6-flash

\- Resultado: error 429 por el límite de 20 solicitudes por día; reintento sugerido en 3 h 40 min. La tarea T2b quedó bloqueada en ese momento.

\- Decisión: COMPLETAR (qué hice después: cambiar de modelo, de agente o esperar).

\- Modelo o agente que completó T2b: COMPLETAR.



\## 2026-11-20 - T2b: comentario con la fórmula equivocada

\- Modelo: gemini-3.8-flash

\- Con grep encontré en dominio.py un comentario con "inicio\_a <= fin\_b and inicio\_b < fin\_a", que contradice AGENTS.md. El código real (return a\_ini < b\_fin and b\_ini < a\_fin) era correcto y las 17 pruebas pasaban.

\- Decisión mía: corregir el comentario a mano.

\- Mi primera mutación se aplicó por error al comentario y no al código, por lo que las pruebas seguían en OK. La repetí sobre la línea de código (resultado en t2-mutacion-falla.txt).


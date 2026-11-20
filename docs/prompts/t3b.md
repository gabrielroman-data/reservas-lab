Tarea T3, parte B. Lee AGENTS.md, PROMPTS.md (sección "Contrato común"), README.md (secciones 1.5 y 1.7), reservas/dominio.py, reservas/errores.py y tests/test\_servicio.py. No explores el repositorio con find ni ls.



Paso 0, antes de implementar: en tests/test\_servicio.py puedes modificar SOLO estas dos pruebas, y solo agregando comprobaciones: (a) test\_ca07\_persistencia\_y\_recuperacion\_tras\_reinicio debe comprobar también solicitante, inicio, fin y estado de cada reserva recuperada; (b) test\_rf03\_reservar\_invalido\_sin\_filas debe cubrir además un solicitante vacío ("   ") y un inicio igual al fin, verificando que no quedan filas. No cambies ninguna otra prueba.



Paso 1: en reservas/dominio.py agrega la función validar\_intervalo(unidad, inicio, fin, ahora, unidades\_validas) que valida unidad conocida, formato de fechas, inicio estrictamente anterior al fin e inicio no anterior a ahora, y devuelve (inicio\_dt, fin\_dt). Haz que validar\_solicitud la use y además valide el solicitante (strip, no vacío). No cambies el comportamiento: las 17 pruebas actuales deben seguir pasando. No toques tests/test\_dominio.py.



Paso 2: crea reservas/persistencia.py (SQLite de la biblioteca estándar; tabla reservas con id INTEGER PRIMARY KEY AUTOINCREMENT, unidad, solicitante, inicio, fin, estado 'activa' o 'cancelada'; fechas guardadas como texto 'YYYY-MM-DDTHH:MM') y reservas/servicio.py con la clase ServicioReservas(ruta\_db, inventario, ahora=datetime.now). La función ahora solo se usa como valor por defecto; las reglas la reciben por parámetro.

\- reservar(): valida con validar\_solicitud, busca solapes SOLO contra reservas activas de la misma unidad usando dominio.se\_solapan, e inserta, todo en una sola transacción (BEGIN IMMEDIATE). Lanza ErrorSolape si hay solape y no deja ninguna fila.

\- disponible(): usa validar\_intervalo y la MISMA verificación de solape que reservar() (una función interna compartida). Devuelve True o False; ante entrada inválida lanza ErrorValidacion.

\- listar(estado=None) ordenado por id; listar\_inventario() devuelve la misma lista de diccionarios recibida (con claves "id" y "nombre"); cerrar() puede llamarse más de una vez sin error.

\- Reabrir el mismo archivo conserva las reservas y no reinicia los ids.



No implementes cancelar ni la consola. No toques otras pruebas. Ejecuta python -m unittest -v y muestra la salida real. No edites PROGRESS.md. No ejecutes git push ni comandos fuera de esta carpeta. No actualices la lista de tareas. Usa la menor cantidad posible de llamadas.


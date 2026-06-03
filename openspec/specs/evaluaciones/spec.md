## ADDED Requirements

### Requirement: Crear convocatoria de coloquio (F7.3)

El sistema SHALL permitir a COORDINADOR/ADMIN crear una convocatoria de coloquio especificando materia, cohorte, instancia (nombre), tipo (Coloquio), y los turnos disponibles (fecha, hora_inicio, hora_fin, cupo).

Al crear la convocatoria se genera el registro en `Evaluacion` y los turnos en `TurnoColoquio`. El campo `dias_disponibles` se calcula como la cantidad de fechas únicas entre los turnos.

#### Scenario: Creación exitosa de convocatoria con 3 turnos
- **WHEN** un COORDINADOR crea una convocatoria para "Programación I" con instancia "Coloquio Final", tipo Coloquio, y 3 turnos (2026-07-15 14:00-18:00 cupo 20, 2026-07-16 14:00-18:00 cupo 15, 2026-07-17 09:00-13:00 cupo 10)
- **THEN** el sistema crea la Evaluacion con estado Activa, crea 3 registros en TurnoColoquio, y retorna la convocatoria con sus turnos

#### Scenario: Creación sin turnos falla
- **WHEN** un COORDINADOR crea una convocatoria sin turnos
- **THEN** el sistema rechaza con 422

### Requirement: Importar alumnos a convocatoria (F7.2)

El sistema SHALL permitir a COORDINADOR/ADMIN cargar o actualizar el listado de alumnos habilitados para una convocatoria específica, enviando un array de `usuario_id` con rol ALUMNO.

La operación es upsert: reemplaza completamente la lista de alumnos asociados.

#### Scenario: Importar alumnos a convocatoria existente
- **WHEN** un COORDINADOR envía [uuid1, uuid2, uuid3] para asociar a una convocatoria activa
- **THEN** el sistema registra los 3 alumnos en `coloquio_alumnos` asociados a la Evaluacion

#### Scenario: Importar con usuario inexistente falla
- **WHEN** un COORDINADOR envía un uuid que no corresponde a ningún Usuario
- **THEN** el sistema rechaza con 422

### Requirement: Listar convocatorias (F7.4)

El sistema SHALL exponer un listado paginado de todas las convocatorias activas del tenant, con métricas por convocatoria: total alumnos convocados, reservas activas, cupos libres (suma de cupos por turno - reservas activas).

COORDINADOR/ADMIN ve todas las convocatorias. ALUMNO ve solo las convocatorias donde está habilitado (registrado en `coloquio_alumnos`) y que tienen al menos un turno con cupo disponible.

#### Scenario: COORDINADOR lista convocatorias con métricas
- **WHEN** un COORDINADOR solicita el listado de convocatorias
- **THEN** el sistema retorna todas las convocatorias del tenant con total_convocados, reservas_activas, cupos_libres

#### Scenario: ALUMNO lista solo convocatorias habilitadas
- **WHEN** un ALUMNO solicita el listado de convocatorias
- **THEN** el sistema retorna solo las convocatorias donde el alumno está en `coloquio_alumnos`

### Requirement: Panel de métricas de coloquios (F7.1)

El sistema SHALL exponer un endpoint de métricas globales para COORDINADOR/ADMIN: total de alumnos cargados en convocatorias, cantidad de instancias activas, reservas activas, notas registradas.

#### Scenario: Métricas globales
- **WHEN** un COORDINADOR solicita métricas de coloquios
- **THEN** el sistema retorna total_convocatorias_activas, total_alumnos_convocados, total_reservas_activas, total_resultados_registrados

### Requirement: Reservar turno de coloquio (FL-07)

El sistema SHALL permitir a un ALUMNO habilitado reservar un turno disponible dentro de una convocatoria donde esté registrado. La reserva incrementa atómicamente el contador `ocupados` del turno. Un ALUMNO solo puede tener **una** reserva activa a la vez por convocatoria.

#### Scenario: Reserva exitosa resta cupo
- **WHEN** un ALUMNO habilitado reserva un turno con cupo=20 y ocupados=15
- **THEN** el sistema crea la ReservaEvaluacion con estado Activa, el turno queda con ocupados=16, y retorna la reserva creada

#### Scenario: Sin cupo disponible rechaza
- **WHEN** un ALUMNO reserva un turno con cupo=20 y ocupados=20
- **THEN** el sistema rechaza con 409 Conflict y mensaje "Turno sin cupo disponible"

#### Scenario: ALUMNO no habilitado rechaza
- **WHEN** un ALUMNO no registrado en `coloquio_alumnos` intenta reservar
- **THEN** el sistema rechaza con 403

#### Scenario: Doble reserva activa en misma convocatoria rechaza
- **WHEN** un ALUMNO ya tiene una reserva Activa en la convocatoria e intenta reservar otro turno
- **THEN** el sistema rechaza con 409 Conflict

### Requirement: Cancelar reserva propia

El sistema SHALL permitir a un ALUMNO cancelar su propia reserva activa. La cancelación decrementa `ocupados` del turno y marca la reserva con estado Cancelada.

#### Scenario: Cancelación exitosa libera cupo
- **WHEN** un ALUMNO cancela su reserva Activa en un turno con ocupados=16
- **THEN** el sistema marca la reserva como Cancelada y el turno queda con ocupados=15

#### Scenario: Cancelar reserva de otro usuario falla
- **WHEN** un ALUMNO intenta cancelar una reserva que pertenece a otro usuario
- **THEN** el sistema rechaza con 404

### Requirement: Administración global de coloquios (F7.5)

El sistema SHALL permitir a ADMIN editar o cerrar una convocatoria. Al cerrar una convocatoria, no se pueden crear nuevas reservas ni registrar nuevos resultados.

#### Scenario: Cerrar convocatoria
- **WHEN** un ADMIN cierra una convocatoria activa
- **THEN** el sistema marca la Evaluacion como estado Cerrada y las reservas Activas pendientes quedan sin efecto

### Requirement: Registrar resultado de coloquio

El sistema SHALL permitir a COORDINADOR/ADMIN registrar o actualizar la nota final de un alumno en una convocatoria mediante `ResultadoEvaluacion`.

#### Scenario: Registrar nota final
- **WHEN** un COORDINADOR registra nota_final="Aprobado" para un alumno en una convocatoria
- **THEN** el sistema crea o actualiza el ResultadoEvaluacion

#### Scenario: Resultados consolidados por convocatoria
- **WHEN** un COORDINADOR solicita los resultados de una convocatoria
- **THEN** el sistema retorna todos los ResultadoEvaluacion de esa convocatoria agrupados por alumno

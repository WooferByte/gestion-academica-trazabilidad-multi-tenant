## 1. Modelos y Migración

- [ ] 1.1 Crear modelo `Evaluacion` con campos: materia_id, cohorte_id, tipo (enum: Parcial/TP/Coloquio/Recuperatorio), instancia, estado (enum: Activa/Cerrada), dias_disponibles. Hereda BaseModelMixin.
- [ ] 1.2 Crear modelo `TurnoColoquio` con campos: evaluacion_id, fecha, hora_inicio, hora_fin, cupo (int), ocupados (int, default 0). CHECK ocupados <= cupo.
- [ ] 1.3 Crear modelo `ReservaEvaluacion` con campos: evaluacion_id, turno_id, alumno_id (FK Usuario), estado (enum: Activa/Cancelada).
- [ ] 1.4 Crear modelo `ResultadoEvaluacion` con campos: evaluacion_id, alumno_id (FK Usuario), nota_final (text).
- [ ] 1.5 Crear modelo `ColoquioAlumno` (tabla puente N:M entre Evaluacion y Usuario): evaluacion_id, alumno_id.
- [ ] 1.6 Generar migración Alembic 011: tablas `evaluaciones`, `turnos_coloquio`, `reservas_evaluacion`, `resultados_evaluacion`, `coloquio_alumnos`. Incluir índices, FKs, unique constraints.
- [ ] 1.7 Agregar seed de permisos: `coloquios:gestionar` (asignado a COORDINADOR, ADMIN) y `coloquios:reservar` (asignado a ALUMNO).

## 2. Schemas Pydantic

- [ ] 2.1 Crear `schemas/evaluaciones.py`: `EvaluacionCreate` (materia_id, cohorte_id, instancia, tipo, turnos[] con fecha/hora/cupo), `EvaluacionResponse`, `TurnoColoquioCreate`, `TurnoColoquioResponse`.
- [ ] 2.2 Agregar `ReservaCreate` (turno_id), `ReservaResponse`, `ReservaCancelResponse`.
- [ ] 2.3 Agregar `ResultadoCreate` (alumno_id, nota_final), `ResultadoUpdate`, `ResultadoResponse`, `ResultadosListResponse`.
- [ ] 2.4 Agregar `MetricasColoquiosResponse` (total_convocatorias_activas, total_alumnos_convocados, total_reservas_activas, total_resultados).
- [ ] 2.5 Agregar `AlumnosImportRequest` (alumno_ids: list[uuid.UUID]).

## 3. Repositories

- [ ] 3.1 Crear `EvaluacionRepository` con métodos: list_filtered (por materia, cohorte, tipo, estado; con métricas por convocatoria via subquery), get_with_turnos.
- [ ] 3.2 Crear `TurnoColoquioRepository` con: atomic_reserve (UPDATE SET ocupados=ocupados+1 WHERE id=X AND ocupados < cupo, retorna rowcount), atomic_cancel (UPDATE SET ocupados=ocupados-1).
- [ ] 3.3 Crear `ReservaEvaluacionRepository` con: list_by_alumno, count_activas_por_convocatoria, get_activa_por_alumno.
- [ ] 3.4 Crear `ResultadoEvaluacionRepository` con: upsert (por evaluacion_id + alumno_id), list_by_evaluacion.
- [ ] 3.5 Crear `ColoquioAlumnoRepository` con: replace_alumnos (delete + insert), list_alumnos_by_evaluacion, exists.

## 4. Services

- [ ] 4.1 Implementar `EvaluacionService.create_convocatoria`: crea Evaluacion + TurnosColoquio en una transacción. Valida materias existentes, al menos 1 turno.
- [ ] 4.2 Implementar `EvaluacionService.listar_convocatorias`: listado con métricas (convocados, reservas activas, cupos libres). Filtra por tenant y por alumno según rol.
- [ ] 4.3 Implementar `EvaluacionService.obtener_metricas`: totales globales de convocatorias activas, alumnos convocados, reservas, resultados.
- [ ] 4.4 Implementar `EvaluacionService.importar_alumnos`: reemplaza lista de alumnos habilitados. Valida que los IDs existan en Usuario con rol ALUMNO.
- [ ] 4.5 Implementar `EvaluacionService.cerrar_convocatoria`: cambia estado a Cerrada.
- [ ] 4.6 Implementar `ReservaService.reservar`: valida alumno habilitado, sin reserva activa previa en la misma convocatoria, llama a atomic_reserve del repo. Si rowcount=0 → 409.
- [ ] 4.7 Implementar `ReservaService.cancelar`: valida que la reserva pertenezca al alumno (o sea COORDINADOR/ADMIN), llama a atomic_cancel.
- [ ] 4.8 Implementar `ResultadoService.registrar`: upsert de nota_final para alumno en evaluación. Listar resultados por convocatoria.

## 5. Router API

- [ ] 5.1 Crear `api/v1/routers/coloquios.py` con prefix `/api/v1/coloquios`:
  - `POST /` — crear convocatoria (`coloquios:gestionar`)
  - `GET /` — listar convocatorias (`coloquios:gestionar` para full, `coloquios:reservar` para alumno)
  - `GET /metricas` — panel de métricas (`coloquios:gestionar`)
  - `GET /{id}` — detalle de convocatoria con turnos
  - `POST /{id}/alumnos` — importar alumnos (`coloquios:gestionar`)
  - `POST /{id}/reservas` — reservar turno (`coloquios:reservar`)
  - `DELETE /reservas/{id}` — cancelar reserva propia (`coloquios:reservar`)
  - `PUT /{id}/resultados/{alumno_id}` — registrar/actualizar resultado (`coloquios:gestionar`)
  - `GET /{id}/resultados` — listar resultados consolidados (`coloquios:gestionar`)
  - `PATCH /{id}/cerrar` — cerrar convocatoria (`coloquios:gestionar`)
- [ ] 5.2 Registrar el router en `api/v1/__init__.py` y `main.py`.
- [ ] 5.3 Agregar audit logging en acciones clave: crear convocatoria, importar alumnos, reservar, cancelar, registrar resultado, cerrar convocatoria.

## 6. Tests

- [ ] 6.1 Safety Net: ejecutar tests existentes y capturar baseline verde.
- [ ] 6.2 Test: crear convocatoria exitosa con turnos (1.1).
- [ ] 6.3 Test: crear convocatoria sin turnos falla (1.2).
- [ ] 6.4 Test: importar alumnos a convocatoria (2.1).
- [ ] 6.5 Test: importar alumnos con ID inexistente falla (2.2).
- [ ] 6.6 Test: COORDINADOR lista convocatorias con métricas (3.1).
- [ ] 6.7 Test: ALUMNO lista solo sus convocatorias habilitadas (3.2).
- [ ] 6.8 Test: métricas globales de coloquios (panel).
- [ ] 6.9 Test: reserva exitosa resta cupo atómicamente (5.1).
- [ ] 6.10 Test: reserva sin cupo rechaza 409 (5.2).
- [ ] 6.11 Test: alumno no habilitado rechaza 403 (5.3).
- [ ] 6.12 Test: doble reserva activa en misma convocatoria rechaza 409 (5.4).
- [ ] 6.13 Test: cancelación exitosa libera cupo (6.1).
- [ ] 6.14 Test: cancelar reserva ajena falla 404 (6.2).
- [ ] 6.15 Test: cerrar convocatoria (7.1).
- [ ] 6.16 Test: registrar nota final de alumno (8.1).
- [ ] 6.17 Test: listar resultados consolidados por convocatoria (8.2).
- [ ] 6.18 Test: race condition en último cupo (dos reservas simultáneas, una falla).
- [ ] 6.19 Test: aislamiento multi-tenant (tenant A no ve datos de tenant B).
- [ ] 6.20 Test: soft delete de evaluacion (cascade a turnos/reservas vía deleted_at check).

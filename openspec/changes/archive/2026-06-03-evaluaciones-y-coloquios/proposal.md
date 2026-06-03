## Why

Actualmente el sistema gestiona encuentros, guardias, calificaciones y comunicaciones, pero no existe soporte para el flujo de **evaluaciones orales finales (coloquios)** que los alumnos deben rendir para aprobar una materia. Cada cuatrimestre, los coordinadores crean convocatorias manualmente, los alumnos reservan turnos informalmente, y el registro de resultados se pierde. Sin trazabilidad ni métricas.

Este change incorpora el modelo de evaluaciones formales (parcial, coloquio, TP, recuperatorio) con el flujo completo de **convocatoria → reserva de turno con cupo → registro de resultado**, cubriendo las funcionalidades F7.1–F7.5 y el flujo FL-07.

## What Changes

- Modelos `Evaluacion`, `ReservaEvaluacion`, `ResultadoEvaluacion` con soft delete, multi-tenancy row-level y UUID como PK.
- Endpoints `/api/v1/coloquios/*` con permisos diferenciados:
  - COORDINADOR/ADMIN: CRUD de convocatorias, importar alumnos, panel de métricas, admin global, registro de resultados.
  - ALUMNO: listar convocatorias habilitadas, reservar turno (día con cupo), cancelar reserva propia.
- Validación de cupo: reservar resta un cupo disponible; sin cupo → rechazo 409.
- Migración Alembic **011**: tablas `evaluaciones`, `reservas_evaluacion`, `resultados_evaluacion`.
- Audit logging de acciones significativas (crear convocatoria, importar alumnos, reservar, cancelar, registrar resultado).

## Capabilities

### New Capabilities

- `evaluaciones`: Gestión completa de evaluaciones formales y coloquios — modelos, convocatorias, reserva de turnos con cupo y registro de resultados académicos. Cubre F7.1–F7.5 y FL-07.

### Modified Capabilities

*(none — no existing specs are affected)*

## Impact

- **Backend**: 3 nuevos modelos, repository, service, schema y router en `api/v1/routers/coloquios.py`.
- **DB**: Migración 011 con tablas `evaluaciones`, `reservas_evaluacion`, `resultados_evaluacion`.
- **Permisos**: Nuevos permisos `coloquios:gestionar` (COORDINADOR/ADMIN), `coloquios:reservar` (ALUMNO). Seed en migración.
- **Registra en**: `CHANGES.md` C-14 completado.

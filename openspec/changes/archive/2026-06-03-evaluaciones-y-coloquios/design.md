## Context

El sistema actual tiene ~22 tablas con Encuentros y Guardias funcionales (C-13 completado). No existe soporte para evaluaciones formales. Activia-trace necesita modelar las instancias de evaluación (parcial, coloquio, TP, recuperatorio) con el flujo completo de convocatoria → reserva de turno con cupo → registro de resultado, específicamente para coloquios (Épica 7, FL-07).

Dependencias cumplidas: C-07 (Usuarios + Asignaciones) provee las identidades de ALUMNO, PROFESOR, COORDINADOR, ADMIN con sus permisos. No hay dependencia directa de C-13 (Encuentros).

## Goals / Non-Goals

**Goals:**
- Modelar `Evaluacion`, `ReservaEvaluacion`, `ResultadoEvaluacion` según E14 con soft delete y multi-tenancy row-level.
- Agregar `TurnoColoquio` para representar días/horarios específicos dentro de una convocatoria con cupos máximos por turno.
- Endpoints `/api/v1/coloquios/*`:
  - COORDINADOR/ADMIN: CRUD convocatorias, importar alumnos, panel de métricas, admin global, registro de resultados.
  - ALUMNO: listar convocatorias habilitadas, reservar turno (día con cupo), cancelar reserva propia.
- Migración Alembic **011** con tablas `evaluaciones`, `turnos_coloquio`, `reservas_evaluacion`, `resultados_evaluacion`.
- Auditoría: crear/cerrar convocatoria, importar alumnos, reservar, cancelar, registrar resultado.

**Non-Goals:**
- No se modelan calendarios de evaluaciones (E15 FechaAcademica) — eso es C-17.
- No se integra con Moodle para coloquios (sync manual).
- No hay frontend en este change (solo API).
- No hay notificaciones push/email al alumno al crear/cancelar reserva.
- No hay límite de reservas por alumno (puede reservar 1 turno activo a la vez — validación soft).

## Decisions

### 1. Tabla `turnos_coloquio` separada (no JSONB)
- **Problema**: Los cupos por día/horario deben ser consultables eficientemente y validables en reserva.
- **Opción A**: JSONB en `Evaluacion` con array de turnos. Simple pero difícil de indexar, consultar y auditar.
- **Opción B**: Tabla separada `TurnoColoquio` con `cupo` (entero) y columna denormalizada `ocupados` con actualización atómica.
- **Decisión**: **Opción B**. `ocupados` se incrementa/decrementa en la misma transacción que crea/cancela la reserva. CHECK constraint `cupo >= 0` y `ocupados <= cupo`. Esto da ACID, queries simples, y el contador evita COUNT(*) en cada reserva.
- **`ReservaEvaluacion`** referencia `turno_id` (no `fecha_hora` directo).

### 2. Permisos: `coloquios:gestionar` y `coloquios:reservar`
- **Problema**: COORDINADOR/ADMIN gestionan; ALUMNO solo reserva sobre convocatorias que le fueron asignadas.
- **Opción A**: Un solo permiso `coloquios:*` con validación por rol en service.
- **Opción B**: Dos permisos separados con guards en router.
- **Decisión**: **Opción B**. `coloquios:gestionar` para COORDINADOR/ADMIN (CRUD convocatorias, importar, registrar resultado). `coloquios:reservar` para ALUMNO (listar propias, reservar, cancelar). Esto sigue el patrón `modulo:accion` de RBAC ya existente.

### 3. Importación de alumnos: bidireccional
- **Problema**: F7.2 requiere cargar/actualizar el padrón de alumnos habilitados para una convocatoria.
- **Decisión**: `POST /api/v1/coloquios/{id}/alumnos` acepta un array de `usuario_id`. Cada alumno se asocia a la convocatoria mediante la tabla puente `ConvocatoriaAlumno` (o reusa `EntradaPadron` filtrada). Se crea la tabla `coloquio_alumnos` para la relación N:M entre `Evaluacion` y `Usuario` (ALUMNO). Esto permite que no todos los alumnos del padrón estén en el coloquio.

### 4. Migración única 011
- Todas las tablas de este change (`evaluaciones`, `turnos_coloquio`, `reservas_evaluacion`, `resultados_evaluacion`, `coloquio_alumnos`) se empaquetan en una sola migración Alembic.

### 5. Soft delete y tenant scope
- Todos los modelos heredan de `BaseModelMixin` (UUID PK, `tenant_id`, `created_at`, `updated_at`, `deleted_at`).
- Repository base filtra por `tenant_id` y `deleted_at IS NULL` por defecto.

### 6. Resultados consolidados
- `GET /api/v1/coloquios/{id}/resultados` devuelve todos los resultados registrados para una convocatoria, agrupados por alumno. COORDINADOR/ADMIN puede cargar o actualizar `nota_final` mediante `PUT`.

## Risks / Trade-offs

- **[Riesgo] Contador `ocupados` desincronizado**: Si una reserva se cancela sin decrementar o una creación falla tras incrementar. **Mitigación**: todo ocurre en la misma transacción (misma sesión y flush). No hay operaciones asincrónicas en este flujo.
- **[Riesgo] Race condition en reserva del último cupo**: Dos alumnos reservan simultáneamente cuando queda 1 cupo. **Mitigación**: `UPDATE turnos_coloquio SET ocupados = ocupados + 1 WHERE id = :id AND ocupados < cupo` como operación atómica. Si `rowcount = 0`, la reserva falla con 409. No se necesita SERIALIZABLE.
- **[Trade-off] `coloquio_alumnos` vs reuso de `EntradaPadron`**: Crear una tabla específica es más mantenible que filtrar el padrón general (que incluye alumnos no habilitados para coloquio). El costo es una tabla extra.

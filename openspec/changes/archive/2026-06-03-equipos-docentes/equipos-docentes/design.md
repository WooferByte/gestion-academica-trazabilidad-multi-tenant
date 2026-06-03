## Context

El modelo `Asignacion` existe desde C-07 con endpoints CRUD individuales en `/api/v1/asignaciones`. C-08 expone nuevas operaciones de gestión de equipos docentes sobre el mismo modelo, sin cambios de schema. El permiso `equipos:asignar` ya existe y se utiliza en el router existente. El código de auditoría `ASIGNACION_MODIFICAR` ya existe.

La coexistencia con `user_roles` mencionada en el docstring de `AsignacionService` continúa vigente; C-08 no la resuelve (eso queda para un change futuro). Las operaciones de C-08 operan exclusivamente sobre la tabla `asignaciones`.

## Goals / Non-Goals

**Goals:**
- Endpoints de consulta: mis-equipos del docente (F4.2) y gestión de asignaciones con filtros (F4.3)
- Asignación masiva en una transacción (F4.4, RN-30)
- Clonado de equipo entre cohortes duplicando asignaciones vigentes (F4.5, RN-12)
- Modificación de vigencia en bloque para un equipo (F4.6)
- Exportación CSV del equipo docente (F4.7)
- Tests para las 5 operaciones principales
- Auditoría con `ASIGNACION_MODIFICAR` para operaciones de escritura

**Non-Goals:**
- NO cambiar el modelo `Asignacion` ni crear nuevas tablas
- NO resolver la coexistencia con `user_roles` (se depreca en change futuro)
- NO implementar búsqueda con autocompletado del lado servidor (RN-30 se cubre parcialmente con filtros)
- NO incluir UI frontend (solo API)

## Decisions

1. **Router separado `/api/v1/equipos`** en lugar de mezclar en `asignaciones.py`. Las operaciones de equipo son de alto nivel (masiva, clonar, exportar) vs CRUD individual. Un router dedicado mantiene cada archivo bajo 500 LOC.

2. **`GET /api/v1/equipos/mis-equipos` sin permiso** (solo autenticación). Cualquier usuario autenticado puede ver sus propias asignaciones. Los endpoints de gestión requieren `equipos:asignar`.

3. **Asignación masiva en una transacción** usando `AsyncSession.begin_nested()` (savepoint) para atomicidad. Si falla una asignación, no se persiste ninguna. Se retorna lista de `AsignacionResponse`.

4. **Clonado por lote**: el service recibe `origen` (materia_id, carrera_id, cohorte_id) y `destino` (materia_id, carrera_id, cohorte_id, desde, hasta). Busca asignaciones vigentes en origen, las duplica con nuevos ids y fechas del destino. Una sola transacción.

5. **Modificación de vigencia en bloque**: PATCH que recibe `materia_id`, `carrera_id`, `cohorte_id`, `desde`, `hasta`. Actualiza todas las asignaciones del equipo. Se audita una sola vez como operación batch.

6. **Exportación CSV**: el service genera un iterable de diccionarios que el router serializa como `StreamingResponse` con `text/csv`. Sin archivos temporales.

7. **Auditoría centralizada**: se crea un helper `_emit_audit` en el router o se usa el `AuditService` existente (si existe). Cada operación de escritura registra un evento `ASIGNACION_MODIFICAR` con metadata de la operación.

## Risks / Trade-offs

- [Rendimiento] Asignación masiva con N grande (100+ docentes): la transacción única puede ser pesada. Si se necesita en el futuro, se puede particionar. Por ahora, 50 docentes es el máximo esperado.
- [Coexistencia] Las nuevas asignaciones via masiva/clonado no crean entradas en `user_roles`. Esto es correcto porque `user_roles` se depreca más adelante, pero hasta entonces las queries JWT no verán estos nuevos roles. Se documenta en el service.
- [CSRF] La exportación CSV expone datos del equipo. Solo accesible con `equipos:asignar` y session auth.
- [Idempotencia] Clonar dos veces el mismo origen→destino genera duplicados. Es responsabilidad del COORDINADOR no re-clonar. Se podría agregar validación en el futuro.

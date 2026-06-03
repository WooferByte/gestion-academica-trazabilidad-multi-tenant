## Why

El modelo `Asignacion` ya existe desde C-07 pero solo tiene endpoints CRUD básicos. El COORDINADOR necesita herramientas de gestión de equipos docentes: asignación masiva al inicio del cuatrimestre, clonado entre períodos, modificación de vigencias en bloque y exportación. Los docentes necesitan ver sus propias asignaciones. Sin esto, la plataforma tiene datos de equipos pero no puede operarlos.

## What Changes

- Endpoint `GET /api/equipos/mis-equipos` para que un docente vea sus asignaciones activas (F4.2)
- Endpoint `GET /api/equipos` con filtros para gestión de asignaciones por COORDINADOR/ADMIN (F4.3)
- Endpoint `POST /api/equipos/asignacion-masiva` para crear N asignaciones en una transacción (F4.4, RN-30)
- Endpoint `POST /api/equipos/clonar` para duplicar asignaciones vigentes entre cohortes (F4.5, RN-12)
- Endpoint `PATCH /api/equipos/vigencia` para modificar fechas `desde`/`hasta` en bloque (F4.6)
- Endpoint `GET /api/equipos/exportar` para generar CSV del equipo (F4.7)
- Nuevos schemas específicos para cada operación masiva
- Nuevos métodos en `AsignacionService` y `AsignacionRepository`
- Permiso `equipos:asignar` existente desde C-07 como guard del router
- Auditoría con `audit_codes.ASIGNACION_MODIFICAR`
- Tests para clonado entre cohortes, asignación masiva, modificación de vigencia en bloque y exportación

## Capabilities

### New Capabilities
- `mis-equipos`: Vista personal de asignaciones del docente autenticado con filtros (F4.2)
- `asignacion-masiva`: Creación batch de asignaciones docente × materia × carrera × cohorte × rol con vigencia (F4.4, RN-30)
- `clonar-equipo`: Duplicación de asignaciones vigentes entre cohortes con ajuste de fechas (F4.5, RN-12)
- `vigencia-equipo`: Modificación en bloque de fechas `desde`/`hasta` de un equipo (F4.6)
- `exportar-equipo`: Generación de CSV con asignaciones del equipo (F4.7)

### Modified Capabilities
- *(ninguna — es la primera vez que se expone `Asignacion` via endpoints de equipos)*

## Impact

- `backend/app/routers/equipos.py` — nuevo router con guard `equipos:asignar`
- `backend/app/services/asignacion.py` — nuevos métodos: `mis_equipos`, `asignacion_masiva`, `clonar_equipo`, `modificar_vigencia`, `exportar_equipo`
- `backend/app/repositories/asignacion.py` — nuevos métodos: `create_bulk`, `clone_vigentes`, `update_vigencia_bulk`, `list_for_export`
- `backend/app/schemas/asignacion.py` — nuevos schemas: `AsignacionMasivaRequest`, `ClonarEquipoRequest`, `VigenciaEquipoRequest`, `ExportRow`
- `backend/app/core/audit_codes.py` — verificar que `ASIGNACION_MODIFICAR` existe
- `backend/app/routers/__init__.py` — registrar nuevo router
- Tests nuevos en `backend/tests/`
- No requiere migraciones ni nuevos modelos

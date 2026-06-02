## Why

El sistema debe cumplir con su premisa fundacional de que "todo audita" (trace). Sin un audit log funcional, no hay trazabilidad de acciones críticas como importaciones de calificaciones, modificación de equipos docentes o cierre de liquidaciones. Además, la impersonación (ya requerida por el dominio) no puede existir sin un registro de auditoría que distinga al actor real del impersonado. Este cambio introduce la infraestructura base de auditoría antes de que comiencen los cambios de dominio que la consumen (C-06 en adelante).

## What Changes

- Nuevo modelo `AuditLog` append-only en base de datos (sin update ni delete)
- Migración Alembic 004: tabla `audit_log`
- Servicio de auditoría inyectable como dependency FastAPI para registrar acciones con código estandarizado
- Catálogo inicial de códigos de acción (`CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, `IMPERSONACION_INICIAR`, `IMPERSONACION_FINALIZAR`, etc.)
- Modificación de `UserContext` para soportar `impersonator_id` (sesión distinguible)
- Nuevo permiso `impersonacion:usar` en el catálogo RBAC
- Endpoint `POST /api/v1/auth/impersonate` para iniciar impersonación
- Endpoint `POST /api/v1/auth/impersonate/stop` para finalizar impersonación
- Middleware/dependency de auditoría que endpoints puedan inyectar para registrar acciones
- Tests: append-only enforcement, atribución bajo impersonación, registro de código + filas afectadas

## Capabilities

### New Capabilities
- `audit-log`: Registro inmutable de acciones significativas con actor, código, detalle JSON, IP y user-agent
- `impersonation`: Suplantación legítima con sesión distinguible, permiso específico y auditoría obligatoria

### Modified Capabilities
- `current-user-dependency`: UserContext debe exponer `impersonator_id` opcional para sesiones bajo impersonación
- `rbac-core`: Agregar permiso `impersonacion:usar` al catálogo base

## Impact

- **Modelos**: nuevo `backend/app/models/audit_log.py` (NO hereda de BaseModelMixin)
- **Core**: modificar `backend/app/core/dependencies.py` (UserContext con impersonator_id)
- **Core**: nuevo `backend/app/core/audit.py` (servicio/dependency de auditoría)
- **Schemas**: modificar `backend/app/schemas/auth.py` (UserContext.impersonator_id)
- **Routers**: nuevo `backend/app/routers/auth_impersonation.py`
- **Servicios**: nuevo `backend/app/services/audit_service.py`
- **Repositorios**: nuevo `backend/app/repositories/audit_repository.py` (solo insert + query, sin update/delete)
- **Migración**: `backend/alembic/versions/004_audit_log.py`
- **Seed data**: agregar `impersonacion:usar` a permisos y asignarlo a rol ADMIN
- **Tests**: nuevos tests de audit log (append-only, impersonación, códigos de acción)

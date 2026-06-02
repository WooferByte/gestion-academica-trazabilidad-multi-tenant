## Context

C-05 es el primer cambio que toca auditoría e impersonación. El sistema ya tiene auth funcional (C-03) y RBAC (C-04) con 7 roles, 21 permisos y asignaciones seed. Hasta ahora no existe ningún registro de auditoría: las acciones en endpoints protegidos no quedan trazadas.

Este cambio introduce el modelo `AuditLog` append-only, un servicio de auditoría inyectable, soporte de impersonación en `UserContext`, y los endpoints de impersonación. Es prerrequisito para todos los cambios de dominio que vienen (C-06 en adelante) porque necesitan registrar acciones significativas.

## Goals / Non-Goals

**Goals:**
- Tabla `audit_log` append-only (sin update, sin delete, sin soft delete) con actor, impersonado, materia, accion, detalle JSON, filas_afectadas, IP, user-agent, fecha_hora
- Servicio/dependency de auditoría `AuditService` para que cualquier endpoint registre acciones con código estandarizado
- Catálogo inicial de códigos de acción (`CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, etc.)
- `UserContext` modificado para incluir `impersonator_id: UUID | None`
- Permiso `impersonacion:usar` agregado al catálogo RBAC y asignado a ADMIN
- Endpoints `POST /api/v1/auth/impersonate` y `POST /api/v1/auth/impersonate/stop`
- Registro automático de `IMPERSONACION_INICIAR` / `IMPERSONACION_FINALIZAR` en audit log
- Migración Alembic 004

**Non-Goals:**
- No se construye el panel de consulta de auditoría (eso es C-19)
- No se definen códigos de acción para módulos que aún no existen (se agregan en sus respectivos changes)
- No se implementa rate limiting ni rotación de audit log (la tabla es append-only sin límite de retención)

## Decisions

### D1 — AuditLog NO hereda de BaseModelMixin
**Decisión**: Modelo SQLAlchemy independiente sin `created_at`, `updated_at`, `deleted_at`. Solo tiene `fecha_hora` (timestamp del evento, no de creación del registro).
**Razón**: BaseModelMixin impone soft delete y timestamps de modificación. AuditLog no se modifica ni se borra. Tener `updated_at` y `deleted_at` en una tabla append-only sería misleading y permitiría errores de implementación.

### D2 — Servicio de auditoría como dependency FastAPI
**Decisión**: `AuditService` es una clase inyectable via FastAPI dependency que recibe `UserContext` y `AsyncSession` y expone un método `log(accion: str, detalle: dict | None = None, filas_afectadas: int = 0, materia_id: UUID | None = None)`.
**Razón**: Sigue el patrón existente de `dependencies.py`. Permite que cualquier endpoint registre auditoría sin acoplar la lógica de negocio al modelo de auditoría. También permite tests unitarios con mock.

Alternativa considerada: decorador `@audit_log(accion="...")`. Se descarta porque no permite registrar dinámicamente filas_afectadas ni detalle variable sin romper la firma del handler.

### D3 — Impersonación vía endpoints específicos (no query param)
**Decisión**: Endpoints dedicados `POST /impersonate` (body: `{target_user_id}`) y `POST /impersonate/stop`. Devuelven un JWT especial con claim `impersonator_id`.
**Razón**: La regla de seguridad #1 dice que la identidad jamás se deriva de un parámetro de la petición. Pasar un `?impersonate=UUID` en query string viola esa regla. Usar endpoints dedicados hace la acción explícita, permisada y auditable.

### D4 — Impersonator en el JWT, no en sesión server-side
**Decisión**: El JWT bajo impersonación lleva `sub` = target (quien va a operar) y `impersonator_id` = quien inició la impersonación.
**Razón**: Es stateless, no requiere almacenamiento de sesión, y funciona con el sistema de refresh rotation existente. El `get_current_user` construye un `UserContext` con ambos campos.

### D5 — `impersonacion:usar` como permiso seed en migración 004
**Decisión**: La migración 004 crea la tabla `audit_log` Y agrega el permiso `impersonacion:usar` + lo asigna a ADMIN.
**Razón**: La migración 004 ya crea el schema de auditoría. Agregar el permiso en la misma migración evita una migración 005 separada solo para seed data. Esto NO es mezclar responsabilidades porque la impersonación depende de este change para existir.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|------------|
| **R1 — Tabla append-only sin límite crece indefinidamente** | El diseño deliberadamente no tiene límite por ahora (premisa "todo audita"). En C-19 (panel auditoría) se puede evaluar una política de retención o archivado |
| **R2 — Impersonación mal implementada expone datos ajenos** | Solo usuarios con `impersonacion:usar` pueden usarla. El `get_current_user` siempre verifica el permiso antes de permitir el impersonate. Falla cerrada: sin permiso → 403 |
| **R3 — El AuditService como dependency se vuelve ruidoso en cada endpoint** | Opcional por diseño. Solo los endpoints que registran acciones significativas lo inyectan. La decisión de qué registrar es del desarrollador, no forzada por el framework |

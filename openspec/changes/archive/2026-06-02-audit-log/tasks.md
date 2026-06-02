## 1. AuditLog Model

- [x] 1.1 Crear modelo `AuditLog` en `backend/app/models/audit_log.py` — NO hereda de BaseModelMixin, solo define tabla append-only con campos: id, tenant_id, fecha_hora, actor_id, impersonado_id, materia_id, accion, detalle (JSONB), filas_afectadas, ip, user_agent
- [x] 1.2 Registrar `AuditLog` en `backend/app/models/__init__.py`

## 2. Migration 004

- [x] 2.1 Generar migración Alembic 004 con tabla `audit_log`, FKs a tenants, users (actor_id), users (impersonado_id)
- [x] 2.2 Agregar seed del permiso `impersonacion:usar` (modulo="impersonacion", accion="usar") en la misma migración
- [x] 2.3 Asignar `impersonacion:usar` al rol ADMIN en la migración

## 3. Audit Codes Catalog

- [x] 3.1 Crear `backend/app/core/audit_codes.py` con constantes tipadas: `CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, `ASIGNACION_MODIFICAR`, `LIQUIDACION_CERRAR`, `IMPERSONACION_INICIAR`, `IMPERSONACION_FINALIZAR`

## 4. Audit Repository

- [x] 4.1 Crear `backend/app/repositories/audit_repository.py` con método `create(entry) -> AuditLog` — solo insert, sin update/delete/list expuestos, filtro por tenant_id automático

## 5. Audit Service

- [x] 5.1 Crear `backend/app/services/audit_service.py` con clase `AuditService` que recibe `UserContext`, `AsyncSession` y expone `log(accion, detalle=None, filas_afectadas=0, materia_id=None, ip=None, user_agent=None)`
- [x] 5.2 El método `log()` debe detectar si `UserContext.impersonator_id` está presente y registrar `impersonado_id` en ese caso

## 6. Audit Dependency

- [x] 6.1 Crear factory function `get_audit_service` en `backend/app/core/audit_dependency.py` que inyecte `AuditService` como dependency FastAPI, extrayendo IP y user-agent del request

## 7. UserContext with Impersonation Support

- [x] 7.1 Agregar campo `impersonator_id: uuid.UUID | None = None` al schema `UserContext` en `backend/app/schemas/auth.py`
- [x] 7.2 Modificar `get_current_user` en `backend/app/core/dependencies.py` para parsear `impersonator_id` del JWT si existe

## 8. Impersonation Endpoints

- [x] 8.1 Crear `backend/app/api/v1/routers/auth_impersonation.py` con endpoint `POST /api/v1/auth/impersonate` que verifique permiso `impersonacion:usar`, valide target user, genere JWT con `impersonator_id`, registre `IMPERSONACION_INICIAR`
- [x] 8.2 Crear endpoint `POST /api/v1/auth/impersonate/stop` que valide que hay impersonación activa, genere nuevo JWT sin `impersonator_id`, registre `IMPERSONACION_FINALIZAR`
- [x] 8.3 Registrar los routers impersonation en `backend/app/main.py`

## 9. Tests

- [x] 9.1 Test: append-only enforcement — intentar update/delete sobre AuditLog debe fallar
- [x] 9.2 Test: atribución bajo impersonación — `actor_id` es el impersonador, `impersonado_id` es el target
- [x] 9.3 Test: registro de acción con código + filas_afectadas + detalle JSON
- [x] 9.4 Test: `IMPERSONACION_INICIAR` se registra al iniciar impersonación
- [x] 9.5 Test: `IMPERSONACION_FINALIZAR` se registra al finalizar impersonación
- [x] 9.6 Test: UserContext sin impersonación tiene `impersonator_id=None`
- [x] 9.7 Test: UserContext bajo impersonación tiene `impersonator_id` poblado
- [x] 9.8 Test: permiso `impersonacion:usar` existe y ADMIN lo tiene
- [x] 9.9 Test: usuario sin `impersonacion:usar` recibe 403 al intentar impersonar

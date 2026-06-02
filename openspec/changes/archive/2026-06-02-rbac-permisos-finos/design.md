## Context

El RBAC actual (C-03) almacena roles como lista JSONB en `User.roles`. Esto es insuficiente para permisos finos: no hay granularidad, no hay catálogo administrable, no hay vigencia. El placeholder `core/permissions.py` espera llenarse desde C-03. La KB define la matriz rol×permiso en `03_actores_y_roles.md §3.3` con 7 roles y ~20 capacidades atómicas.

## Goals / Non-Goals

**Goals:**
- Tablas normalizadas: `roles`, `permisos`, `rol_permiso`, `user_roles` con soft delete y tenant scope
- Resolver permisos efectivos server-side como unión de roles del usuario, acotada por tenant y vigencia
- `require_permission(modulo:accion)` como FastAPI dependency reutilizable en cualquier endpoint
- Seeding automático de la matriz base del dominio en migración 003
- CRUD administrable del catálogo (roles, permisos, asignaciones)
- Data migration: conservar roles de usuarios existentes (C-03) en la nueva tabla `user_roles`
- Cobertura ≥90% de reglas de negocio en tests

**Non-Goals:**
- Vigencia temporal por asignación (feat `desde`/`hasta` en `user_roles`) — se implementa la columna pero sin lógica de expiración activa hasta C-10 (equipos docentes)
- UI de administración de permisos — solo API
- Impersonación (`impersonacion:usar`) — es C-05 (audit log)

## Decisions

| Decisión | Alternativas | Rationale |
|----------|-------------|-----------|
| **Permisos como strings `modulo:accion`** vs IDs numéricos | IDs numéricos más rápidos en JOIN | Strings son autodocumentados, más fáciles de debuggear y seedear. La tabla `rol_permiso` usa FK a `permisos.id` para integridad referencial |
| **Resolver permisos desde DB en cada request** vs cachear en Redis o JWT | Cache en JWT (C-03 style), Redis si hay latencia | DB por request es aceptable: ~2 queries (user_roles + rol_permiso) con índices. Los roles se cachean en JWT por 15 min. Para permisos finos, DB es correcta por ahora |
| **Tabla `user_roles` separada** vs migrar JSONB a una sola tabla pivot | JSONB actual como trampolín | Separar User de Role via `user_roles` permite soft delete, vigencia, auditoría y consultas eficientes |
| **Seeder en migración Alembic** vs script separado | Script separado más flexible | Seeder en migración asegura que los datos base existen desde el primer deploy. Se usa `op.execute` con INSERT condicional (upsert) |
| **`require_permission` como clase** vs función factory | Función factory (`require_permission(modulo:accion)`) | Más idiomática en FastAPI. Retorna `Depends()` para inyección directa |
| **NEXO con matriz propia** vs posponer | Matriz parcial hasta que se cierre semántica (PA-25) | Se incluye con los permisos actuales de la KB. Si cambia, es data migration, no schema |
| **Fail-closed** | Si el permiso no existe en DB, denegar | Consistente con principios de seguridad del proyecto |

## Risks / Trade-offs

- **[R1] Carga de query**: 2 queries extra por request con authz → Mitigación: índices en `(user_id, tenant_id, deleted_at)` y en `(role_id, permiso_id)`. Si es bottleneck futuro, cache temporal TTL 60s.
- **[R2] Data migration de JSONB**: usuarios existentes pierden roles si la migración falla → Mitigación: migración en dos pasos (schema + data), todo en una transacción, con rollback explícito.
- **[R3] JWT con roles desactualizados**: el token de 15 min puede tener roles que ya no aplican → Mitigación: los roles en JWT son solo hint para el resolver; la DB es la fuente de verdad. Si hay cambio de roles, se refleja en el próximo refresh.

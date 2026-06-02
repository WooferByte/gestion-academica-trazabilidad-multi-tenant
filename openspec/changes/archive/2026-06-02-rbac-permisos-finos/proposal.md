## Why

El modelo de autorización actual usa roles como JSONB en el modelo User, sin un sistema de permisos finos. Cada acción protegida necesita un mecanismo explícito y auditable. Este change implementa el RBAC con permisos `modulo:accion` definido en `03_actores_y_roles.md §3`, reemplazando el placeholder en `core/permissions.py` y migrando los roles de JSONB a tablas normalizadas con catálogo administrable y vigencia temporal.

## What Changes

- Migrar `User.roles` (JSONB) a tabla `user_roles` con FK a `roles`
- Crear tablas `roles`, `permisos`, `rol_permiso` con catálogo seedeable y administrable
- Implementar `require_permission("modulo:accion")` como dependency de FastAPI
- Resolver permisos efectivos server-side como unión de permisos de todos los roles del usuario, acotados por tenant y vigencia
- Seeding de la matriz rol×permiso base (`03_actores_y_roles.md §3.3`) para los 7 roles del dominio
- CRUD de catálogo para administrar roles, permisos y asignaciones
- Migración 003 con tablas + seed data

## Capabilities

### New Capabilities
- `rbac-core`: Modelos, migración, repositorios y lógica central de roles, permisos y su resolución
- `rbac-guard`: Dependency `require_permission` para proteger endpoints FastAPI
- `rbac-admin`: CRUD administrable del catálogo de roles, permisos y matriz rol×permiso

### Modified Capabilities
- *(Ninguna — es el primer spec del proyecto)*

## Impact

- **Modelos**: Nuevos modelos `Role`, `Permission`, `RolePermission`, `UserRole`. Migración de `User.roles` JSONB a tabla normalizada.
- **Auth**: El JWT sigue llevando roles (para compatibilidad C-03) pero los permisos se resuelven desde DB. `get_current_user` se actualiza para cargar `UserRole` en lugar de solo `User.roles`.
- **API**: Nuevos endpoints bajo `/api/v1/roles` y `/api/v1/permisos` para administración del catálogo.
- **Dependencies**: Nueva `require_permission()` en `core/dependencies.py`. `core/permissions.py` se completa con el resolver de permisos.
- **DB**: Migración Alembic 003. Seed data obligatorio para el tenant inicial.
- **Breaking**: `User.roles` JSONB queda deprecado; todos los endpoints que usaban `user.roles` deben migrar a la nueva resolución.

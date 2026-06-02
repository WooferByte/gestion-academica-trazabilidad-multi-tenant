## 1. Modelos (rbac-core)

- [x] 1.1 Crear modelo `Role` en `backend/app/models/role.py`: name, codigo único por tenant, soft delete
- [x] 1.2 Crear modelo `Permission` en `backend/app/models/permission.py`: codigo (`modulo:accion`), descripcion, modulo, accion, unique por tenant
- [x] 1.3 Crear modelo `RolePermission` en `backend/app/models/role_permission.py`: role_id, permiso_id, propio bool, soft delete
- [x] 1.4 Crear modelo `UserRole` en `backend/app/models/user_role.py`: user_id, role_id, desde (opcional), hasta (opcional), soft delete
- [x] 1.5 Exportar todos los nuevos modelos en `backend/app/models/__init__.py`

## 2. Schemas Pydantic (rbac-core + rbac-admin)

- [x] 2.1 Crear `backend/app/schemas/role.py`: RoleCreate, RoleUpdate, RoleResponse, RoleList
- [x] 2.2 Crear `backend/app/schemas/permission.py`: PermissionCreate, PermissionUpdate, PermissionResponse, PermissionList
- [x] 2.3 Crear `backend/app/schemas/role_permission.py`: RolePermissionAssign, RolePermissionResponse
- [x] 2.4 Crear `backend/app/schemas/user_role.py`: UserRoleAssign, UserRoleResponse
- [x] 2.5 Todos los schemas con `model_config = ConfigDict(extra='forbid')`

## 3. Repositorios (rbac-core)

- [x] 3.1 Crear `backend/app/repositories/role.py`: RoleRepository con CRUD + soft delete + tenant scope
- [x] 3.2 Crear `backend/app/repositories/permission.py`: PermissionRepository con CRUD + unique codigo por tenant
- [x] 3.3 Crear `backend/app/repositories/role_permission.py`: RolePermissionRepository con assign/unassign + list por role
- [x] 3.4 Crear `backend/app/repositories/user_role.py`: UserRoleRepository con assign/unassign + list por user + resolver permisos efectivos
- [x] 3.5 Actualizar `backend/app/repositories/__init__.py`

## 4. Resolver de permisos y guard (rbac-core + rbac-guard)

- [x] 4.1 Implementar `PermissionResolver` en `backend/app/core/permissions.py`: método `get_effective_permissions(user_id, tenant_id)` que une permisos de todos los roles activos
- [x] 4.2 Implementar `require_permission(permiso: str)` como función factory en `backend/app/core/dependencies.py` que retorna `Depends()`
- [x] 4.3 El guard debe llamar al resolver, verificar pertenencia y levantar `HTTPException(403)` si falta el permiso
- [x] 4.4 Manejar fail-closed: permiso inexistente en DB → 403

## 5. Servicios (rbac-admin)

- [x] 5.1 Crear `backend/app/services/role_service.py`: orquesta CRUD de roles con validaciones de unicidad y tenant
- [x] 5.2 Crear `backend/app/services/permission_service.py`: orquesta CRUD de permisos con validación de duplicados
- [x] 5.3 Crear `backend/app/services/role_permission_service.py`: orquesta assign/unassign con validación de existencias
- [x] 5.4 Crear `backend/app/services/user_role_service.py`: orquesta assign/unassign con migración desde JSONB si aplica

## 6. Routers API (rbac-admin)

- [x] 6.1 Crear `backend/app/api/v1/routers/roles.py`: GET /roles, POST /roles, PUT /roles/{id}, DELETE /roles/{id}
- [x] 6.2 Crear `backend/app/api/v1/routers/permisos.py`: GET /permisos, POST /permisos, PUT /permisos/{id}, DELETE /permisos/{id}
- [x] 6.3 Crear `backend/app/api/v1/routers/role_permisos.py`: POST /roles/{role_id}/permisos, DELETE /roles/{role_id}/permisos/{permiso_id}, GET /roles/{role_id}/permisos
- [x] 6.4 Crear `backend/app/api/v1/routers/user_roles.py`: POST /users/{user_id}/roles, DELETE /users/{user_id}/roles/{role_id}, GET /users/{user_id}/roles
- [x] 6.5 Registrar todos los routers en `backend/app/api/v1/routers/__init__.py`
- [x] 6.6 Proteger todos los endpoints rbac-admin con `require_permission("rbac:gestionar")`

## 7. Migración Alembic 003

- [x] 7.1 Crear migración `003_rbac` con creación de tablas: roles, permisos, rol_permiso, user_roles
- [x] 7.2 Agregar migración de datos: copiar `User.roles` JSONB → `user_roles` usando los roles seed
- [x] 7.3 Agregar seed data: inserts de los 7 roles del dominio con `op.execute`
- [x] 7.4 Agregar seed de la matriz rol×permiso completa desde `03_actores_y_roles.md §3.3`
- [x] 7.5 Verificar rollback: migración down debe dropear tablas

## 8. Tests

- [x] 8.1 Crear test de modelo Role: creación, soft delete, tenant isolation, unique codigo
- [x] 8.2 Crear test de modelo Permission: creación, unique codigo por tenant
- [x] 8.3 Crear test de resolver de permisos: rol único, unión de roles, exclusión de soft-delete, tenant scope
- [x] 8.4 Crear test de require_permission: usuario con permiso pasa, sin permiso 403, fail-closed
- [x] 8.5 Crear test de CRUD roles API: list, create, update, soft-delete
- [x] 8.6 Crear test de CRUD permisos API: list, create, update, duplicate rejection
- [x] 8.7 Crear test de assign/unassign rol↔permiso: assign, remove, list por role
- [x] 8.8 Crear test de assign/unassign user↔rol: assign, remove, list por user
- [x] 8.9 Crear test de cobertura de seed data: roles existentes, matriz completa, data migration desde JSONB
- [x] 8.10 Crear test de seguridad: non-ADMIN 403 en endpoints admin

## 9. Limpieza y compatibilidad

- [x] 9.1 Verificar que `get_current_user` sigue funcionando con la nueva estructura (sigue leyendo JWT roles)
- [x] 9.2 Actualizar `core/permissions.py` — remover placeholder y dejar solo el resolver y referencias
- [x] 9.3 Verificar que C-03 auth tests siguen pasando (no romper auth existente)

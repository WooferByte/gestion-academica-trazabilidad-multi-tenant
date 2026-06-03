## 1. Migración y Modelos

- [x] 1.1 Crear migración 006: agregar columnas a `users` (cuil_cifrado, cbu_cifrado, alias_cbu_cifrado, email_cifrado, email_hash, banco, regional, legajo, legajo_profesional, facturador, estado), migrar emails existentes a email_cifrado + email_hash
- [x] 1.2 Crear migración 006: tabla `asignaciones` con columnas (id, tenant_id, usuario_id, rol, materia_id, carrera_id, cohorte_id, comisiones JSONB, responsable_id, desde, hasta, created_at, updated_at, deleted_at) y FKs
- [x] 1.3 Agregar seed de nuevos permisos (`usuarios:gestionar`, `equipos:asignar`) en migración 006
- [x] 1.4 Actualizar modelo `User` en `backend/app/models/user.py` con nuevos campos cifrados y email_hash
- [x] 1.5 Crear modelo `Asignacion` en `backend/app/models/asignacion.py` con FKs y unique constraints

## 2. Schemas Pydantic

- [x] 2.1 Crear schemas de request/response para Usuario: `UsuarioCreate`, `UsuarioUpdate`, `UsuarioResponse` (sin PII en texto plano), `UsuarioListResponse`
- [x] 2.2 Crear schemas de request/response para Asignacion: `AsignacionCreate`, `AsignacionUpdate`, `AsignacionResponse`, `AsignacionListResponse`

## 3. Repositorios

- [x] 3.1 Crear `UsuarioRepository` en `backend/app/repositories/usuario.py`: métodos create, get_by_id, list (tenant-scoped, con filtros), update, soft_delete, buscar por email_hash
- [x] 3.2 Crear `AsignacionRepository` en `backend/app/repositories/asignacion.py`: métodos create, get_by_id, list con filtros (tenant-scoped, vigencia opcional), update, soft_delete, get_vigentes

## 4. Servicios

- [x] 4.1 Crear `UsuarioService` en `backend/app/services/usuario.py`: ABM con cifrado PII, validación unicidad email, legajo como atributo de negocio
- [x] 4.2 Crear `AsignacionService` en `backend/app/services/asignacion.py`: CRUD con validación de vigencia, contexto nullable, jerarquía responsable, derivación de estado_vigencia

## 5. Routers

- [x] 5.1 Crear router `/api/admin/usuarios` en `backend/app/api/v1/routers/admin_usuarios.py` con guard `usuarios:gestionar`
- [x] 5.2 Crear router `/api/asignaciones` en `backend/app/api/v1/routers/asignaciones.py` con guard `equipos:asignar`
- [x] 5.3 Registrar routers y modelos en `backend/app/main.py` y `backend/app/models/__init__.py`

## 6. Tests

- [x] 6.1 Test: PII cifrada no se expone en respuestas API (verificar que cuil/cbu/alias_cbu/dni/email no aparecen en texto plano)
- [x] 6.2 Test: unicidad (tenant_id, email) — mismo email en distinto tenant sí se permite
- [x] 6.3 Test: creación y consulta de asignación vigente vs vencida
- [x] 6.4 Test: multi-rol (mismo usuario con dos asignaciones distintas)
- [x] 6.5 Test: jerarquía responsable_id
- [x] 6.6 Test: aislamiento multi-tenant (tenant A no ve asignaciones de tenant B)
- [x] 6.7 Test: soft delete en usuario y asignación
- [x] 6.8 Test: 403 sin permiso `usuarios:gestionar` o `equipos:asignar`
- [x] 6.9 Test: contexto nullable — asignación global sin materia/carrera/cohorte

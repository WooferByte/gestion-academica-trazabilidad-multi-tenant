## Context

Activia-trace necesita las entidades raíz del dominio académico. C-05 (audit-log) ya completó la tabla `audit_log` y la migración 004. La migración 003 (RBAC) ya incluye el permiso `estructura:gestionar` en el seed, asociado al rol ADMIN. No hay cambios en RBAC.

El stack actual: Python 3.13, FastAPI async, SQLAlchemy 2.0 async, Pydantic v2 con `extra='forbid'`, repositories con scope tenant, soft delete, Clean Architecture.

## Goals / Non-Goals

**Goals:**
- Implementar modelos Carrera, Cohorte, Materia con herencia de `BaseModelMixin` (tenant_id, soft delete, timestamps)
- ABM completo con endpoints REST protegidos bajo `/api/v1/admin/`
- Migración Alembic 005 con las 3 tablas + constraints de unicidad
- Tests de CRUD, unicidad por tenant, aislamiento multi-tenant, regla carrera inactiva

**Non-Goals:**
- No incluir Dictado (instancia Materia × Carrera × Cohorte) — vendrá en C-14
- No incluir Asignación (equipos docentes) — vendrá en C-07
- No modificar RBAC ni seeds existentes — el permiso `estructura:gestionar` ya está disponible
- No incluir endpoints de frontend

## Decisions

### D1 — Unicidad compuesta con tenant_id
Siguiendo ADR-002 (row-level multi-tenancy), los unique constraints incluyen `tenant_id`:
- `Carrera`: `UNIQUE (tenant_id, codigo)`
- `Cohorte`: `UNIQUE (tenant_id, carrera_id, nombre)`
- `Materia`: `UNIQUE (tenant_id, codigo)`

**Alternativa**: unique global + validación en service. Se descarta porque PostgreSQL no impone la restricción a nivel DB, dejando ventana para duplicados en concurrencia.

### D2 — Estado como string, no enum de base de datos
Se usa `String(20)` con validación a nivel Pydantic, mismo patrón que `Tenant.estado` y `User.estado`.

**Alternativa**: ENUM nativo de PostgreSQL. Se descarta por consistencia con el modelo existente y para evitar migrations adicionales al agregar nuevos estados.

### D3 — Router único por entidad bajo `/api/v1/admin/`
Mismo patrón que `roles.py`: cada entidad tiene su propio archivo de router con prefijo.

**Endpoints por entidad:**
```
GET    /api/v1/admin/carreras       → listar
POST   /api/v1/admin/carreras       → crear
GET    /api/v1/admin/carreras/{id}   → obtener
PUT    /api/v1/admin/carreras/{id}   → actualizar
DELETE /api/v1/admin/carreras/{id}   → soft delete
```

### D4 — Regla carrera inactiva en service layer
Al crear o actualizar una cohorte, el service verifica que `carrera.estado == 'Activa'`. Si la carrera es inactiva, rechaza la operación con 422.

**Alternativa**: trigger de BD. Se descarta porque la regla cruza dos tablas y es más legible y testeable en Python.

### D5 — No exponer deleted_at en responses de listado
Los endpoints de listado retornan solo registros activos (`deleted_at IS NULL`). El soft delete es interno del repository.

## Risks / Trade-offs

| Riesgo | Mitigación |
|--------|-----------|
| [Unicidad débil en concurrencia] → Dos requests simultáneos con mismo código podrían pasar validación antes de insertar | El unique constraint a nivel DB es la defensa final; la excepción de integridad se captura en service y se mapea a 409 |
| [Cohorte sin FK explícita a carrera activa] → Si se inactiva una carrera con cohortes abiertas, no hay cascade | Validar al inactivar carrera: si tiene cohortes con `vig_hasta IS NULL`, rechazar con 422 |
| [Nombres de tablas en plural vs singular] → inconsistencias con el modelo existente | Usar plural (`carreras`, `cohortes`, `materias`) siguiendo el patrón de `tenants`, `users`, `roles` |

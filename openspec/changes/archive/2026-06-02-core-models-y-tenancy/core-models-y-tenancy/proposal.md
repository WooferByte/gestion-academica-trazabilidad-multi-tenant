## Why

activia-trace es multi-tenant desde el día 0 (ADR-002), pero hoy no existe el modelo `Tenant`, ni el mixin base que toda entidad del dominio hereda, ni el repository genérico que filtra por `tenant_id` por defecto. Sin estas piezas ningún cambio de dominio (C-03 auth, C-04 RBAC, C-06 estructura académica) puede persistir datos correctamente. C-01 dejó el esqueleto y los placeholders de `core/tenancy.py` y `core/exceptions.py` — este change los llena con implementación real. También establece la base técnica para cumplir RNF-08 (PII cifrada en reposo).

## What Changes

- **Modelo `Tenant`**: entidad SQLAlchemy con `id` (UUID, PK), `nombre`, `codigo`, `estado` (Activo/Inactivo), `created_at`, `updated_at`, `deleted_at`. Raíz del aislamiento multi-tenant.
- **Mixin base `BaseModelMixin`**: todo modelo hereda `id` (UUID v4 auto-generado), `tenant_id` (FK → Tenant, nullable solo para el modelo Tenant), `created_at`, `updated_at`, `deleted_at` (soft delete). Mixin aplicado a `Base` declarativa (o como mixin explícito en cada modelo).
- **Soft delete transversal**: overwrite de `filter_by` / `where` en queries para excluir `deleted_at IS NOT NULL` por defecto. Repository incorpora método `exists()` y `soft_delete()` (setea `deleted_at`, no borra).
- **Repository genérico** `BaseRepository[T]`: CRUD básico (get, get_multi, create, update, soft_delete) donde **toda query filtra por `tenant_id` por defecto**. El tenant se recibe como dependencia inyectada.
  - `get(uuid: UUID) → T | None` — busca por id + tenant scope.
  - `get_multi(*, skip, limit) → list[T]` — paginado con tenant scope.
  - `create(obj_in: CreateSchemaType) → T` — asigna tenant_id y setea timestamps.
  - `update(db_obj, obj_in: UpdateSchemaType) → T` — merge parcial, setea `updated_at`.
  - `soft_delete(db_obj) → T` — setea `deleted_at`, no borra.
  - `exists(**kwargs) → bool` — chequea existencia dentro del tenant.
- **Utilidad AES-256** en `core/security.py`: funciones `encrypt(plaintext: str) -> str` y `decrypt(ciphertext: str) -> str` usando la `ENCRYPTION_KEY` de Settings (32 bytes, configurable vía `.env`). Cifrado autenticado (AEAD: AES-256-GCM). Helper `encrypt_field()` / `decrypt_field()` para atributos `[cifrado]` en modelos.
- **Migración Alembic 001**: crea tabla `tenants`, configura UUID extension si no existe.
- **Tenancy layer** en `core/tenancy.py`: clase/resolvedor que extrae el `tenant_id` del contexto (JWT en C-03+, pero la capa ya acepta un `tenant_id` inyectado). Dependency `get_tenant()` que provee el tenant activo.
- **Tests**:
  - Aislamiento multi-tenant: tenant A no ve datos de tenant B en get/get_multi.
  - Soft delete: `soft_delete()` marca `deleted_at`, get ya no lo encuentra, get_multi lo excluye.
  - Cifrado round-trip: `encrypt(decrypt(text)) == text`, valores distintos cifran distinto.
  - Mixin timestamps: `created_at` y `updated_at` se setean en create/update.

No hay cambios BREAKING: C-01 no creó tablas ni migraciones, solo el esqueleto.

## Capabilities

### New Capabilities

- `tenant-model`: modelo Tenant raíz con ciclo de vida (activo/inactivo), soft delete y timestamps.
- `base-model-mixin`: mixin SQLAlchemy con UUID PK, tenant_id FK, created_at, updated_at, deleted_at.
- `soft-delete`: eliminación lógica transversal con filtro automático en queries.
- `base-repository`: repository genérico CRUD con scope de tenant siempre activo.
- `aes-encryption`: cifrado autenticado AES-256-GCM para atributos PII y secretos.
- `tenancy-layer`: resolvedor de tenant y dependency get_tenant para inyección en repos.
- `alembic-migration-001`: migración inicial que crea la tabla tenants.

### Modified Capabilities

- `app-scaffold` (de C-01): los módulos reservados `core/tenancy.py`, `core/security.py`, `core/exceptions.py` se llenan con implementación real. `core/dependencies.py` gana `get_tenant()`.
- `app-configuration` (de C-01): `Settings` ahora valida que `ENCRYPTION_KEY` tenga exactamente 32 chars (AES-256).

## Impact

- **Nuevo código**: `backend/app/models/tenant.py`, `backend/app/models/mixins.py`, `backend/app/repositories/base.py`, `backend/app/schemas/tenant.py`, `backend/app/services/tenant.py` (opcional — crud simple), actualización de `core/security.py`, `core/tenancy.py`, `core/exceptions.py`, `core/dependencies.py`, migración Alembic 001.
- **Tests**: `backend/tests/test_tenant_isolation.py`, `backend/tests/test_soft_delete.py`, `backend/tests/test_encryption.py`, `backend/tests/test_mixin_timestamps.py`, `backend/tests/test_base_repository.py`.
- **Dependencias**: se agrega `cryptography` a `pyproject.toml` (AES-256-GCM via `cryptography.fernet` o cifrado directo con `Cipher`).
- **Habilita** a C-03 (`auth`) que necesita `Tenant` para el modelo `User` y la tenancy layer existente. También a C-04 (RBAC) y C-06 (estructura académica).
- **Governance**: CRÍTICO — multi-tenancy es el cimiento de seguridad del proyecto. Nivel row-level con tenant_id en toda tabla. Requiere review antes de implementar.

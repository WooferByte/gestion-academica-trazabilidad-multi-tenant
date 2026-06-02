## ADDED Requirements

### Requirement: Modelo Tenant

El sistema SHALL tener un modelo `Tenant` como entidad raíz del multi-tenancy. Representa una institución aislada dentro del sistema. Ningún dato cruza entre tenants.

#### Scenario: Creación de un tenant

- **GIVEN** un payload válido con `nombre` y `codigo`
- **WHEN** se crea un tenant vía repository
- **THEN** el tenant se persiste con `id` UUID v4, `codigo` único, `estado` = "Activo", y timestamps `created_at`/`updated_at` no nulos

#### Scenario: Código único entre tenants

- **GIVEN** un tenant con `codigo` "TUPAD"
- **WHEN** se intenta crear otro tenant con el mismo `codigo`
- **THEN** el sistema rechaza la operación con error de integridad (unique constraint violation)

#### Scenario: Tenant con estado Inactivo

- **GIVEN** un tenant en estado "Activo"
- **WHEN** se actualiza su estado a "Inactivo"
- **THEN** el tenant se marca como Inactivo y `updated_at` se actualiza

#### Scenario: Soft delete de tenant

- **GIVEN** un tenant existente
- **WHEN** se ejecuta soft_delete sobre el tenant
- **THEN** el campo `deleted_at` se setea con timestamp actual
- **AND** el tenant ya no aparece en queries default

### Requirement: Tabla tenants con migración

La tabla `tenants` SHALL ser creada por la migración Alembic 001 con los campos: `id` (UUID PK), `nombre`, `codigo` (unique), `estado`, `created_at`, `updated_at`, `deleted_at`.

#### Scenario: Migración ejecutada

- **GIVEN** una base de datos vacía (sin migraciones)
- **WHEN** se ejecuta `alembic upgrade head`
- **THEN** existe la tabla `tenants` con las columnas esperadas
- **AND** existe un índice único sobre `codigo`
- **AND** la extensión `uuid-ossp` fue creada (si no existía)

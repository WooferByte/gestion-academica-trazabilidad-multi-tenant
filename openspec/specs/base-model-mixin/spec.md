## ADDED Requirements

### Requirement: Mixin base para modelos del dominio

Todo modelo del dominio SHALL heredar de `BaseModelMixin` que provee: `id` (UUID v4 PK), `tenant_id` (FK → tenants.id), `created_at`, `updated_at`, `deleted_at`.

#### Scenario: Mixin asigna UUID automático

- **GIVEN** cualquier modelo que herede de `BaseModelMixin`
- **WHEN** se crea una instancia sin especificar `id`
- **THEN** se asigna un UUID v4 automáticamente

#### Scenario: tenant_id es FK a tenants

- **GIVEN** un modelo que hereda de `BaseModelMixin`
- **WHEN** se persiste con un `tenant_id` que no existe en la tabla `tenants`
- **THEN** el sistema rechaza con error de integridad referencial (FK violation)

#### Scenario: Tenant no tiene tenant_id (nullable)

- **GIVEN** el modelo `Tenant`
- **WHEN** se inspecciona su schema
- **THEN** `tenant_id` es nullable (no hay FK circular a sí mismo)

#### Scenario: created_at se setea automáticamente

- **GIVEN** un nuevo registro de cualquier modelo
- **WHEN** se persiste
- **THEN** `created_at` contiene un timestamp no nulo

#### Scenario: updated_at se actualiza en modificación

- **GIVEN** un registro existente
- **WHEN** se modifica un campo
- **THEN** `updated_at` se actualiza al timestamp de la modificación

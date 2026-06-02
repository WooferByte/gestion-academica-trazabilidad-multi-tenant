## ADDED Requirements

### Requirement: Migración 002 — tablas users, refresh_tokens, password_reset_tokens

El sistema SHALL tener una migración Alembic 002 que cree las tablas `users`, `refresh_tokens` y `password_reset_tokens`.

#### Scenario: Tabla users creada

- **GIVEN** una base de datos con migración 001 ejecutada
- **WHEN** se ejecuta `alembic upgrade head` (migración 002)
- **THEN** existe la tabla `users` con columnas: `id` (UUID PK), `tenant_id` (UUID FK → tenants.id, NOT NULL), `email` (VARCHAR 255, NOT NULL), `password_hash` (VARCHAR 255, NOT NULL), `nombre_cifrado` (TEXT, nullable), `apellido_cifrado` (TEXT, nullable), `dni_cifrado` (TEXT, nullable), `roles` (JSONB, NOT NULL, default '[]'), `totp_secret_cifrado` (TEXT, nullable), `is_active` (BOOLEAN, NOT NULL, default TRUE), `created_at`, `updated_at`, `deleted_at`
- **AND** existe unique constraint `uq_users_email_tenant` sobre `(email, tenant_id)`
- **AND** existe índice `ix_users_email` sobre `email`

#### Scenario: Tabla refresh_tokens creada

- **GIVEN** migración 002 ejecutada
- **THEN** existe la tabla `refresh_tokens` con columnas: `id` (UUID PK), `user_id` (UUID FK → users.id, NOT NULL), `token_hash` (VARCHAR 128, NOT NULL, UNIQUE), `family_id` (UUID, NOT NULL), `expires_at` (TIMESTAMPTZ, NOT NULL), `revoked_at` (TIMESTAMPTZ, nullable), `created_at`, `updated_at`, `deleted_at`

#### Scenario: Tabla password_reset_tokens creada

- **GIVEN** migración 002 ejecutada
- **THEN** existe la tabla `password_reset_tokens` con columnas: `id` (UUID PK), `token_hash` (VARCHAR 128, NOT NULL, UNIQUE), `user_id` (UUID FK → users.id, NOT NULL), `expires_at` (TIMESTAMPTZ, NOT NULL), `used_at` (TIMESTAMPTZ, nullable), `created_at`, `updated_at`, `deleted_at`

#### Scenario: Rollback de migración 002

- **GIVEN** migración 002 ejecutada
- **WHEN** se ejecuta `alembic downgrade -1`
- **THEN** las tablas `password_reset_tokens`, `refresh_tokens` y `users` son eliminadas en ese orden
- **AND** la tabla `tenants` (de migración 001) sigue existiendo

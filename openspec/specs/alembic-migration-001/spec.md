## ADDED Requirements

### Requirement: Migración 001 — create tenants table

La migración 001 SHALL ser la primera migración Alembic del proyecto (revises: None) y SHALL crear la tabla `tenants` con soporte UUID.

#### Scenario: Migración 001 es la primera

- **GIVEN** el historial de migraciones
- **WHEN** se inspecciona la migración 001
- **THEN** `revises` es `None` (no depende de migraciones previas)
- **AND** `down_revision` apunta a `None`

#### Scenario: Upgrade crea estructura esperada

- **GIVEN** una base de datos vacía
- **WHEN** se ejecuta `alembic upgrade 001`
- **THEN** existe la tabla `tenants`
- **AND** la tabla tiene las columnas: `id` (UUID PK), `nombre` (varchar 255), `codigo` (varchar 50), `estado` (varchar 20), `created_at` (timestamptz), `updated_at` (timestamptz), `deleted_at` (timestamptz nullable)
- **AND** existe un unique constraint sobre `codigo`

#### Scenario: Downgrade revierte la migración

- **GIVEN** una base de datos con migración 001 aplicada
- **WHEN** se ejecuta `alembic downgrade -1`
- **THEN** la tabla `tenants` ya no existe

#### Scenario: uuid-ossp extension creada

- **GIVEN** una base de datos sin la extensión uuid-ossp
- **WHEN** se ejecuta la migración 001
- **THEN** la extensión `uuid-ossp` está disponible en la base de datos

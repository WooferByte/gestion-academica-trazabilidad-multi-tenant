## ADDED Requirements

### Requirement: Core role model
The system SHALL maintain a `roles` table with tenant isolation and soft delete.

#### Scenario: Create a role
- **WHEN** an ADMIN creates a role `rol` with name `"Supervisor"` and codigo `"SUPERVISOR"`
- **THEN** the role SHALL be persisted with `tenant_id`, `id`, `created_at`, `updated_at`, `deleted_at=NULL`

#### Scenario: Tenant isolation of roles
- **WHEN** tenant A has a role `PROFESOR` and tenant B has no roles
- **THEN** tenant B SHALL NOT see or access tenant A's role `PROFESOR`

#### Scenario: Soft delete a role
- **WHEN** an ADMIN soft-deletes a role
- **THEN** the role SHALL have `deleted_at` set and SHALL NOT appear in active queries

### Requirement: Core permission model
The system SHALL maintain a `permisos` table storing atomic permissions as `modulo:accion` strings.

#### Scenario: Create a permission
- **WHEN** an ADMIN creates a permission `calificaciones:importar`
- **THEN** the permission SHALL be stored with `codigo="calificaciones:importar"`, `descripcion`, `modulo="calificaciones"`, `accion="importar"`

#### Scenario: Unique permission code
- **WHEN** an ADMIN attempts to create a duplicate permission `calificaciones:importar` for the same tenant
- **THEN** the system SHALL reject with a conflict error

### Requirement: Role-permission matrix
The system SHALL maintain a `rol_permiso` table mapping roles to permissions.

#### Scenario: Assign permission to role
- **WHEN** an ADMIN assigns permission `calificaciones:importar` to role `PROFESOR`
- **THEN** the system SHALL store the association with `role_id`, `permiso_id` and `tenant_id`

#### Scenario: Permission property scoping
- **WHEN** a permission is assigned with `propio=True` (scoped to own data)
- **THEN** the system SHALL store the `propio` flag indicating the permission applies only to the user's own resources

### Requirement: User-role assignment
The system SHALL store user→role assignments in a `user_roles` table with tenant scope, timestamps and soft delete.

#### Scenario: Assign role to user
- **WHEN** an ADMIN assigns role `PROFESOR` to user X
- **THEN** the system SHALL store the assignment with `user_id`, `role_id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at=NULL`

#### Scenario: Multiple roles for one user
- **WHEN** user X has roles `PROFESOR` and `COORDINADOR`
- **THEN** the system SHALL store two separate `user_roles` rows

#### Scenario: Soft-delete a role assignment
- **WHEN** an ADMIN removes a role from a user
- **THEN** the `user_roles` row SHALL be soft-deleted (`deleted_at` set)

### Requirement: Effective permission resolver
The system SHALL resolve effective permissions for a user as the union of all permissions from all their active (non-deleted) roles.

#### Scenario: Resolve permissions from single role
- **WHEN** user X has role `ALUMNO` and role `ALUMNO` has permissions `[ver_estado_academico_propio, reservar_evaluacion]`
- **THEN** the resolver SHALL return `[ver_estado_academico_propio, reservar_evaluacion]`

#### Scenario: Resolve permissions from multiple roles
- **WHEN** user X has roles `PROFESOR` and `COORDINADOR` with distinct permission sets
- **THEN** the resolver SHALL return the UNION of all permissions from both roles

#### Scenario: Tenant-scoped resolution
- **WHEN** resolving permissions for user X in tenant A
- **THEN** the resolver SHALL ONLY consider user_roles and permissions scoped to tenant A

#### Scenario: Exclude soft-deleted assignments
- **WHEN** user X had role `PROFESOR` but the assignment was soft-deleted
- **THEN** the resolver SHALL NOT include permissions from the deleted assignment

### Requirement: Seed data for roles
The system SHALL seed the 7 domain roles from `03_actores_y_roles.md`.

#### Scenario: Seed domain roles
- **WHEN** migration 003 runs
- **THEN** the system SHALL insert roles: `ALUMNO`, `TUTOR`, `PROFESOR`, `COORDINADOR`, `NEXO`, `ADMIN`, `FINANZAS` for the default tenant

### Requirement: Seed data for role-permission matrix
The system SHALL seed the role-permission matrix defined in `03_actores_y_roles.md §3.3`.

#### Scenario: ALUMNO permissions
- **WHEN** the seed runs
- **THEN** role `ALUMNO` SHALL have permissions `[ver_estado_academico_propio, reservar_evaluacion, confirmar_avisos]`

#### Scenario: PROFESOR permissions (scoped)
- **WHEN** the seed runs
- **THEN** role `PROFESOR` SHALL have permission `calificaciones:importar` with `propio=True`

#### Scenario: ADMIN permissions (full)
- **WHEN** the seed runs
- **THEN** role `ADMIN` SHALL have all non-finance permissions, including `gestionar_estructura_academica`, `gestionar_usuarios`, `configurar_tenant`

#### Scenario: FINANZAS permissions (isolated)
- **WHEN** the seed runs
- **THEN** role `FINANZAS` SHALL have permissions `[ver_auditoria, operar_grilla_salarial, calcular_liquidaciones, gestionar_facturas]`

### Requirement: Data migration from User.roles JSONB
The system SHALL migrate existing `User.roles` (JSONB list of strings) to `user_roles` table.

#### Scenario: Migrate single role
- **WHEN** a user has `roles=["ALUMNO"]` in JSONB
- **THEN** the migration SHALL create one `user_roles` row linking the user to the seeded `ALUMNO` role

#### Scenario: Migrate multiple roles
- **WHEN** a user has `roles=["PROFESOR", "COORDINADOR"]` in JSONB
- **THEN** the migration SHALL create two `user_roles` rows for that user

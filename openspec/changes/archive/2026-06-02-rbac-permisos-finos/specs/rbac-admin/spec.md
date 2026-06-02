## ADDED Requirements

### Requirement: CRUD roles catalog
The system SHALL expose endpoints for managing the roles catalog (tenant-scoped).

#### Scenario: List active roles
- **WHEN** an ADMIN requests `GET /api/v1/roles`
- **THEN** the system SHALL return all non-deleted roles for the current tenant

#### Scenario: Create a role
- **WHEN** an ADMIN sends `POST /api/v1/roles` with `{nombre: "Supervisor", codigo: "SUPERVISOR"}`
- **THEN** the system SHALL create and return the new role

#### Scenario: Update a role
- **WHEN** an ADMIN sends `PUT /api/v1/roles/{id}` with updated fields
- **THEN** the system SHALL update and return the role

#### Scenario: Soft-delete a role
- **WHEN** an ADMIN sends `DELETE /api/v1/roles/{id}`
- **THEN** the system SHALL soft-delete the role and return 204

### Requirement: CRUD permissions catalog
The system SHALL expose endpoints for managing permissions.

#### Scenario: List permissions
- **WHEN** an ADMIN requests `GET /api/v1/permisos`
- **THEN** the system SHALL return all non-deleted permissions for the current tenant

#### Scenario: Create a permission
- **WHEN** an ADMIN sends `POST /api/v1/permisos` with `{codigo: "nuevo_modulo:accion", descripcion: "...", modulo: "nuevo_modulo", accion: "accion"}`
- **THEN** the system SHALL create and return the new permission

#### Scenario: Reject duplicate permission code
- **WHEN** an ADMIN attempts to create a permission with an existing `codigo` for the same tenant
- **THEN** the system SHALL return 409 Conflict

### Requirement: Manage role-permission assignments
The system SHALL expose endpoints for assigning and removing permissions from roles.

#### Scenario: Assign permission to role
- **WHEN** an ADMIN sends `POST /api/v1/roles/{role_id}/permisos` with `{permiso_id: "...", propio: false}`
- **THEN** the system SHALL create the `rol_permiso` association and return 201

#### Scenario: Remove permission from role
- **WHEN** an ADMIN sends `DELETE /api/v1/roles/{role_id}/permisos/{permiso_id}`
- **THEN** the system SHALL soft-delete the `rol_permiso` association and return 204

#### Scenario: List permissions for a role
- **WHEN** an ADMIN requests `GET /api/v1/roles/{role_id}/permisos`
- **THEN** the system SHALL return all active permissions assigned to that role

### Requirement: Manage user-role assignments
The system SHALL expose endpoints for managing user role assignments.

#### Scenario: Assign role to user
- **WHEN** an ADMIN sends `POST /api/v1/users/{user_id}/roles` with `{role_id: "..."}`
- **THEN** the system SHALL create the `user_roles` association and return 201

#### Scenario: Remove role from user
- **WHEN** an ADMIN sends `DELETE /api/v1/users/{user_id}/roles/{role_id}`
- **THEN** the system SHALL soft-delete the `user_roles` association and return 204

#### Scenario: List roles for a user
- **WHEN** an ADMIN requests `GET /api/v1/users/{user_id}/roles`
- **THEN** the system SHALL return all active roles assigned to that user

#### Scenario: Non-ADMIN cannot manage catalog
- **WHEN** a non-ADMIN user (e.g., PROFESOR) tries to access any rbac-admin endpoint
- **THEN** the system SHALL return 403 Forbidden

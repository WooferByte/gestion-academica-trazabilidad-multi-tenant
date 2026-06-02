## ADDED Requirements

### Requirement: require_permission dependency
The system SHALL provide a FastAPI dependency `require_permission(permiso: str)` that checks if the current user has the specified permission.

#### Scenario: User has the required permission
- **WHEN** an endpoint requires `calificaciones:importar` and the current user has that permission
- **THEN** the dependency SHALL pass and the endpoint SHALL execute

#### Scenario: User lacks the required permission
- **WHEN** an endpoint requires `liquidaciones:cerrar` and the current user does NOT have that permission
- **THEN** the dependency SHALL raise `HTTPException(403)` with detail `"Permiso insuficiente: liquidaciones:cerrar"`

#### Scenario: Multiple permissions (AND logic)
- **WHEN** an endpoint requires `[comunicacion:enviar, comunicacion:aprobar]` using multiple `require_permission` dependencies
- **THEN** the user SHALL have ALL permissions, else 403

#### Scenario: Permission guard as reusable callable
- **WHEN** a developer applies `require_permission("modulo:accion")` to any endpoint
- **THEN** the function SHALL return a `Depends()` callable that can be used as a path/endpoint dependency

### Requirement: Permission check uses effective resolver
The `require_permission` dependency SHALL use the effective permission resolver from the rbac-core capability.

#### Scenario: Resolution from single role
- **WHEN** user has role `ALUMNO` with permission `reservar_evaluacion`
- **THEN** `require_permission("reservar_evaluacion")` SHALL pass

#### Scenario: Resolution from union of roles
- **WHEN** user lacks a permission in role A but has it in role B
- **THEN** `require_permission` SHALL still pass (union semantics)

### Requirement: Fail-closed behavior
The system SHALL deny access when the permission scope is ambiguous or the permission code does not exist.

#### Scenario: Non-existent permission code
- **WHEN** a developer declares `require_permission("modulo:inexistente")` and the permission code does not exist in the DB
- **THEN** the system SHALL return 403

#### Scenario: No permissions at all
- **WHEN** an authenticated user has no roles assigned
- **THEN** `require_permission` for any permission SHALL return 403

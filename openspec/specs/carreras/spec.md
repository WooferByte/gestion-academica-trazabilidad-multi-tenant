## ADDED Requirements

### Requirement: Administrar carreras
El sistema SHALL permitir a usuarios con permiso `estructura:gestionar` administrar las carreras del tenant (alta, lectura, edición, cambio de estado y eliminación lógica).

#### Scenario: Crear carrera exitosamente
- **WHEN** un ADMIN envía POST `/api/v1/admin/carreras` con `codigo` y `nombre` válidos
- **THEN** el sistema retorna 201 con los datos de la carrera creada, estado `Activa` por defecto

#### Scenario: Crear carrera con código duplicado
- **WHEN** un ADMIN envía POST `/api/v1/admin/carreras` con un `codigo` ya existente en el mismo tenant
- **THEN** el sistema retorna 409 con mensaje indicando código duplicado

#### Scenario: Crear carrera con código duplicado en otro tenant
- **WHEN** un ADMIN del tenant A crea una carrera con `codigo` que ya existe en tenant B
- **THEN** el sistema retorna 201 exitosamente (aislamiento multi-tenant)

#### Scenario: Listar carreras
- **WHEN** un ADMIN envía GET `/api/v1/admin/carreras`
- **THEN** el sistema retorna 200 con lista paginada de carreras activas del tenant

#### Scenario: Obtener carrera por ID
- **WHEN** un ADMIN envía GET `/api/v1/admin/carreras/{id}` con un ID válido
- **THEN** el sistema retorna 200 con los datos de la carrera

#### Scenario: Obtener carrera inexistente
- **WHEN** un ADMIN envía GET `/api/v1/admin/carreras/{id}` con un ID que no existe
- **THEN** el sistema retorna 404

#### Scenario: Actualizar carrera
- **WHEN** un ADMIN envía PUT `/api/v1/admin/carreras/{id}` con `nombre` actualizado
- **THEN** el sistema retorna 200 con los datos actualizados

#### Scenario: Actualizar carrera a código duplicado
- **WHEN** un ADMIN envía PUT `/api/v1/admin/carreras/{id}` con un `codigo` ya usado por otra carrera
- **THEN** el sistema retorna 409

#### Scenario: Inactivar carrera con cohortes abiertas
- **WHEN** un ADMIN envía PUT `/api/v1/admin/carreras/{id}` con `estado: "Inactiva"` y la carrera tiene cohortes con `vig_hasta IS NULL`
- **THEN** el sistema retorna 422 indicando que no se puede inactivar una carrera con cohortes abiertas

#### Scenario: Soft delete carrera
- **WHEN** un ADMIN envía DELETE `/api/v1/admin/carreras/{id}`
- **THEN** el sistema retorna 204 y la carrera queda con `deleted_at` asignado

#### Scenario: Acceso sin permiso estructura:gestionar
- **WHEN** un usuario sin permiso `estructura:gestionar` intenta acceder a cualquier endpoint de carreras
- **THEN** el sistema retorna 403

#### Scenario: Aislamiento multi-tenant en carreras
- **WHEN** un ADMIN del tenant A lista carreras
- **THEN** el sistema retorna solo carreras del tenant A, nunca del tenant B

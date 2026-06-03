## ADDED Requirements

### Requirement: Administrar materias
El sistema SHALL permitir a usuarios con permiso `estructura:gestionar` administrar el catálogo único de materias del tenant (alta, lectura, edición, cambio de estado y eliminación lógica). Cada materia es una definición única; la instanciación por carrera/cohorte se modela en el change de Dictado (C-14).

#### Scenario: Crear materia exitosamente
- **WHEN** un ADMIN envía POST `/api/v1/admin/materias` con `codigo` y `nombre` válidos
- **THEN** el sistema retorna 201 con los datos de la materia creada, estado `Activa` por defecto

#### Scenario: Crear materia con código duplicado
- **WHEN** un ADMIN envía POST `/api/v1/admin/materias` con un `codigo` ya existente en el mismo tenant
- **THEN** el sistema retorna 409

#### Scenario: Crear materia con código duplicado en otro tenant
- **WHEN** un ADMIN del tenant A crea una materia con `codigo` que ya existe en tenant B
- **THEN** el sistema retorna 201 exitosamente (aislamiento multi-tenant)

#### Scenario: Listar materias
- **WHEN** un ADMIN envía GET `/api/v1/admin/materias`
- **THEN** el sistema retorna 200 con lista de materias activas del tenant

#### Scenario: Obtener materia por ID
- **WHEN** un ADMIN envía GET `/api/v1/admin/materias/{id}` con un ID válido
- **THEN** el sistema retorna 200 con los datos de la materia

#### Scenario: Actualizar materia
- **WHEN** un ADMIN envía PUT `/api/v1/admin/materias/{id}` actualizando `nombre`
- **THEN** el sistema retorna 200 con los datos actualizados

#### Scenario: Actualizar materia a código duplicado
- **WHEN** un ADMIN envía PUT `/api/v1/admin/materias/{id}` con un `codigo` ya usado por otra materia
- **THEN** el sistema retorna 409

#### Scenario: Soft delete materia
- **WHEN** un ADMIN envía DELETE `/api/v1/admin/materias/{id}`
- **THEN** el sistema retorna 204

#### Scenario: Aislamiento multi-tenant en materias
- **WHEN** un ADMIN del tenant A lista materias
- **THEN** el sistema retorna solo materias del tenant A

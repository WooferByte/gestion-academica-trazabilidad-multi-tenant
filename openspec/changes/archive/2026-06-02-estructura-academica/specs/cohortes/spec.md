## ADDED Requirements

### Requirement: Administrar cohortes
El sistema SHALL permitir a usuarios con permiso `estructura:gestionar` administrar las cohortes del tenant, vinculadas a una carrera y con vigencia temporal.

#### Scenario: Crear cohorte exitosamente
- **WHEN** un ADMIN envía POST `/api/v1/admin/cohortes` con `carrera_id`, `nombre`, `anio` y `vig_desde` válidos
- **THEN** el sistema retorna 201 con los datos de la cohorte creada

#### Scenario: Crear cohorte con nombre duplicado en misma carrera
- **WHEN** un ADMIN envía POST `/api/v1/admin/cohortes` con `nombre` ya existente para la misma `carrera_id` en el mismo tenant
- **THEN** el sistema retorna 409

#### Scenario: Crear cohorte con nombre duplicado en distinta carrera
- **WHEN** un ADMIN envía POST `/api/v1/admin/cohortes` con `nombre` que ya existe pero para otra `carrera_id`
- **THEN** el sistema retorna 201 exitosamente

#### Scenario: Crear cohorte en carrera inactiva
- **WHEN** un ADMIN envía POST `/api/v1/admin/cohortes` referenciando una carrera con `estado: "Inactiva"`
- **THEN** el sistema retorna 422 indicando que la carrera no está activa

#### Scenario: Crear cohorte con carrera inexistente
- **WHEN** un ADMIN envía POST `/api/v1/admin/cohortes` con un `carrera_id` que no existe
- **THEN** el sistema retorna 404

#### Scenario: Listar cohortes
- **WHEN** un ADMIN envía GET `/api/v1/admin/cohortes`
- **THEN** el sistema retorna 200 con lista de cohortes activas del tenant, incluyendo datos de la carrera asociada

#### Scenario: Obtener cohorte por ID
- **WHEN** un ADMIN envía GET `/api/v1/admin/cohortes/{id}` con un ID válido
- **THEN** el sistema retorna 200 con los datos de la cohorte

#### Scenario: Actualizar cohorte
- **WHEN** un ADMIN envía PUT `/api/v1/admin/cohortes/{id}` actualizando `vig_hasta`
- **THEN** el sistema retorna 200 con los datos actualizados

#### Scenario: Soft delete cohorte
- **WHEN** un ADMIN envía DELETE `/api/v1/admin/cohortes/{id}`
- **THEN** el sistema retorna 204

#### Scenario: Aislamiento multi-tenant en cohortes
- **WHEN** un ADMIN del tenant B lista cohortes
- **THEN** el sistema retorna solo cohortes del tenant B, aunque compartan nombre con cohortes de otro tenant

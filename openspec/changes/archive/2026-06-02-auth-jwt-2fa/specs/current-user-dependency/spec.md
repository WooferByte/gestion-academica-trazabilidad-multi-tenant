## ADDED Requirements

### Requirement: Dependency get_current_user

El sistema SHALL proveer una dependency `get_current_user` que extraiga la identidad y el tenant desde el JWT verificado y los inyecte en las capas inferiores.

#### Scenario: Token válido devuelve UserContext

- **GIVEN** un JWT válido (firma correcta, no expirado) con `sub`, `tenant_id`, `roles`
- **WHEN** la dependency `get_current_user` procesa el token
- **THEN** retorna un `UserContext` con `user_id`, `tenant_id`, `roles`

#### Scenario: Token expirado

- **GIVEN** un JWT cuya fecha `exp` ya pasó
- **WHEN** la dependency procesa el token
- **THEN** lanza `HTTPException 401 Unauthorized`
- **AND** el detail es `"Token expirado"`

#### Scenario: Token con firma inválida

- **GIVEN** un JWT firmado con una clave distinta a `SECRET_KEY`
- **WHEN** la dependency procesa el token
- **THEN** lanza `HTTPException 401 Unauthorized`

#### Scenario: Token sin tenant_id

- **GIVEN** un JWT válido pero sin claim `tenant_id`
- **WHEN** la dependency procesa el token
- **THEN** lanza `HTTPException 401 Unauthorized`

#### Scenario: Token con tenant inactivo

- **GIVEN** un JWT válido con `tenant_id` de un tenant en estado "Inactivo" o soft-deleteado
- **WHEN** la dependency procesa el token
- **THEN** lanza `HTTPException 401 Unauthorized`

#### Scenario: Identidad no suplantable por parámetros

- **GIVEN** un JWT válido para usuario A con tenant T1
- **WHEN** se envía un request a cualquier endpoint protegido con ese JWT
- **AND** el body/query/header contiene un parámetro con otro user_id o tenant_id
- **THEN** la identidad y tenant resueltos por `get_current_user` son los del JWT, no los del parámetro

### Requirement: UserContext DTO

El sistema SHALL proveer un DTO `UserContext` con `user_id` (UUID), `tenant_id` (UUID) y `roles` (list[str]) para ser usado en Services y Repositories.

#### Scenario: UserContext disponible en capas inferiores

- **GIVEN** un usuario autenticado
- **WHEN** se ejecuta un service que recibe `UserContext` como dependencia
- **THEN** el service puede acceder a `user_id`, `tenant_id` y `roles`
- **AND** el repository subyacente filtra por `tenant_id` automáticamente

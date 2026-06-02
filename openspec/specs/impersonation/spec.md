## ADDED Requirements

### Requirement: Impersonation permission
El sistema SHALL requerir el permiso `impersonacion:usar` para iniciar una sesión de impersonación.

#### Scenario: Grant impersonacion:usar to ADMIN
- **WHEN** la migración 004 se ejecuta
- **THEN** el permiso `impersonacion:usar` SHALL ser insertado en la tabla `permisos`
- **AND** el rol `ADMIN` SHALL tener este permiso asignado en `rol_permiso`

#### Scenario: Impersonation without permission
- **WHEN** un usuario SIN permiso `impersonacion:usar` intenta acceder a `POST /impersonate`
- **THEN** el sistema SHALL retornar `403 Forbidden`

### Requirement: Start impersonation
El sistema SHALL proveer un endpoint `POST /api/v1/auth/impersonate` que inicie una sesión de impersonación.

#### Scenario: Successful impersonation start
- **WHEN** un usuario con `impersonacion:usar` envía `POST /impersonate` con `{"target_user_id": "<UUID>"}`
- **AND** el target user existe y está activo
- **THEN** el sistema SHALL retornar un nuevo par access+refresh token
- **AND** el access token SHALL tener `sub=target_user_id` y `impersonator_id=actor_user_id`
- **AND** el sistema SHALL registrar un evento `IMPERSONACION_INICIAR` en audit log

#### Scenario: Impersonation of non-existent user
- **WHEN** un usuario intenta impersonar a un `target_user_id` que no existe o está inactivo
- **THEN** el sistema SHALL retornar `404 Not Found`

#### Scenario: Impersonation of self
- **WHEN** un usuario intenta impersonarse a sí mismo (`target_user_id = current_user.user_id`)
- **THEN** el sistema SHALL retornar `400 Bad Request`

### Requirement: Stop impersonation
El sistema SHALL proveer un endpoint `POST /api/v1/auth/impersonate/stop` que finalice la impersonación y retorne al token original del actor.

#### Scenario: Successful impersonation stop
- **WHEN** un usuario bajo impersonación envía `POST /impersonate/stop`
- **THEN** el sistema SHALL retornar un nuevo par access+refresh token para el actor real
- **AND** el access token SHALL tener `sub=impersonator_id` y NO tener `impersonator_id`
- **AND** el sistema SHALL registrar un evento `IMPERSONACION_FINALIZAR` en audit log

#### Scenario: Stop without impersonation
- **WHEN** un usuario NO bajo impersonación envía `POST /impersonate/stop`
- **THEN** el sistema SHALL retornar `400 Bad Request`

### Requirement: Distinguished session under impersonation
El sistema SHALL distinguir una sesión bajo impersonación de una sesión normal.

#### Scenario: UserContext shows impersonation
- **WHEN** un access token contiene `impersonator_id`
- **THEN** `get_current_user` SHALL retornar un `UserContext` con `impersonator_id` poblado
- **AND** `UserContext.user_id` SHALL ser el usuario impersonado (target)
- **AND** `UserContext.roles` SHALL ser los roles del usuario impersonado

#### Scenario: Normal session has no impersonator_id
- **WHEN** un access token NO contiene `impersonator_id`
- **THEN** `get_current_user` SHALL retornar un `UserContext` con `impersonator_id=None`

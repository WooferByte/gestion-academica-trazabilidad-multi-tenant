## ADDED Requirements

### Requirement: Refresh token con rotación

El sistema SHALL implementar refresh token con rotación: cada uso del refresh token invalida el anterior y emite uno nuevo.

#### Scenario: Refresh exitoso

- **GIVEN** un par access+refresh válido
- **WHEN** se envía `POST /api/v1/auth/refresh` con el refresh token
- **THEN** la respuesta es `200 OK`
- **AND** el body contiene un nuevo `access_token` y un nuevo `refresh_token`
- **AND** el refresh token anterior queda revocado en DB

#### Scenario: Refresh con token revocado

- **GIVEN** un refresh token ya usado (revocado)
- **WHEN** se envía `POST /api/v1/auth/refresh` con ese token
- **THEN** la respuesta es `401 Unauthorized`
- **AND** el body contiene `detail: "Token inválido o revocado"`

#### Scenario: Reuso de refresh token revocado invalida toda la familia

- **GIVEN** un refresh token T1 que fue usado y generó T2 (misma familia)
- **WHEN** se envía T1 nuevamente a refresh
- **THEN** la respuesta es `401 Unauthorized`
- **AND** T2 también queda revocado
- **AND** la familia completa queda invalidada

#### Scenario: Refresh con token expirado

- **GIVEN** un refresh token cuya `expires_at` ya pasó
- **WHEN** se envía a refresh
- **THEN** la respuesta es `401 Unauthorized`

### Requirement: Logout con revocación

El sistema SHALL exponer `POST /api/v1/auth/logout` que revoque el refresh token activo.

#### Scenario: Logout exitoso

- **GIVEN** un usuario autenticado con sesión activa
- **WHEN** se envía `POST /api/v1/auth/logout` con el refresh token en el body
- **THEN** la respuesta es `200 OK`
- **AND** el refresh token queda marcado como revocado en DB
- **AND** el access token actual sigue siendo válido hasta su expiración natural (no se puede revocar un JWT)

#### Scenario: Logout sin autenticación

- **WHEN** se envía `POST /api/v1/auth/logout` sin token de acceso
- **THEN** la respuesta es `401 Unauthorized`

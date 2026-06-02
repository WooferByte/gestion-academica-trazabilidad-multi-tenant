## ADDED Requirements

### Requirement: Login con email y password

El sistema SHALL exponer `POST /api/v1/auth/login` que autentique un usuario por email + password y emita credenciales de sesión.

#### Scenario: Login exitoso sin 2FA

- **GIVEN** un usuario activo con email "docente@test.com" y password "pass123"
- **WHEN** se envía `POST /api/v1/auth/login` con `{"email": "docente@test.com", "password": "pass123"}`
- **THEN** la respuesta es `200 OK`
- **AND** el body contiene `access_token` (string JWT), `refresh_token` (string UUID), `token_type: "bearer"`, `expires_in` (segundos hasta expiración del access token)

#### Scenario: Login con credenciales incorrectas

- **GIVEN** un usuario con email "docente@test.com" y password "pass123"
- **WHEN** se envía `POST /api/v1/auth/login` con `{"email": "docente@test.com", "password": "wrong_pass"}`
- **THEN** la respuesta es `401 Unauthorized`
- **AND** el body contiene `detail: "Credenciales inválidas"`

#### Scenario: Login de usuario soft-deleteado

- **GIVEN** un usuario soft-deleteado
- **WHEN** se intenta login con sus credenciales
- **THEN** la respuesta es `401 Unauthorized`

#### Scenario: Login de usuario inactivo

- **GIVEN** un usuario con `is_active=False`
- **WHEN** se intenta login con sus credenciales correctas
- **THEN** la respuesta es `401 Unauthorized`

#### Scenario: Login con email inexistente

- **GIVEN** ningún usuario con email "noexiste@test.com"
- **WHEN** se envía `POST /api/v1/auth/login` con ese email
- **THEN** la respuesta es `401 Unauthorized` (mismo mensaje que credencial incorrecta, para no revelar existencia)

#### Scenario: Transaccionalidad en login

- **WHEN** ocurre login exitoso
- **THEN** se persiste el refresh token en la tabla `refresh_tokens`
- **AND** el token de acceso JWT contiene `sub` (user_id), `tenant_id`, `roles`, `exp`, `iat`
- **AND** el JWT NO contiene permisos

### Requirement: Claims mínimos en JWT

El sistema SHALL emitir JWT con claims mínimos. Los permisos nunca se almacenan en el token.

#### Scenario: Claims del JWT

- **GIVEN** un login exitoso
- **WHEN** se decodifica el `access_token` (sin verificar firma, solo para inspeccionar claims)
- **THEN** el payload contiene únicamente: `sub`, `tenant_id`, `roles`, `exp`, `iat`
- **AND** no contiene campos como `permissions`, `is_admin`, `scope`

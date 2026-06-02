## ADDED Requirements

### Requirement: Solicitud de recuperación de contraseña

El sistema SHALL exponer `POST /api/v1/auth/forgot` que genere un token de un solo uso para recuperar la contraseña.

#### Scenario: Solicitud exitosa

- **GIVEN** un usuario existente con email "docente@test.com"
- **WHEN** se envía `POST /api/v1/auth/forgot` con `{"email": "docente@test.com"}`
- **THEN** la respuesta es `200 OK`
- **AND** el body contiene `token` (string UUID) y `expires_in` (segundos)

#### Scenario: Solicitud con email inexistente

- **GIVEN** ningún usuario con el email solicitado
- **WHEN** se envía `POST /api/v1/auth/forgot`
- **THEN** la respuesta es `200 OK` (mismo código que éxito, para no revelar existencia de cuentas)
- **AND** el body contiene `detail: "Si el email existe, recibirás un enlace de recuperación"`

### Requirement: Reseteo de contraseña

El sistema SHALL exponer `POST /api/v1/auth/reset` que permita cambiar la contraseña usando un token de recuperación válido.

#### Scenario: Reseteo exitoso

- **GIVEN** un token de recuperación válido y no expirado
- **WHEN** se envía `POST /api/v1/auth/reset` con `{"token": "<token>", "new_password": "nueva_pass_123"}`
- **THEN** la respuesta es `200 OK`
- **AND** el password del usuario se actualiza al hash de "nueva_pass_123"
- **AND** el token queda marcado como usado
- **AND** todos los refresh tokens del usuario quedan revocados

#### Scenario: Reseteo con token expirado

- **GIVEN** un token de recuperación con `expires_at` en el pasado
- **WHEN** se envía `POST /api/v1/auth/reset`
- **THEN** la respuesta es `401 Unauthorized`

#### Scenario: Reseteo con token ya usado

- **GIVEN** un token de recuperación ya utilizado
- **WHEN** se envía `POST /api/v1/auth/reset`
- **THEN** la respuesta es `401 Unauthorized`

#### Scenario: Token de un solo uso

- **GIVEN** un reseteo exitoso realizado
- **WHEN** se intenta usar el mismo token nuevamente
- **THEN** la respuesta es `401 Unauthorized`

## ADDED Requirements

### Requirement: Enrolamiento TOTP

El sistema SHALL exponer `POST /api/v1/auth/2fa/enroll` (autenticado) para generar un secreto TOTP.

#### Scenario: Enrolamiento exitoso

- **GIVEN** un usuario autenticado sin 2FA activo
- **WHEN** se envía `POST /api/v1/auth/2fa/enroll`
- **THEN** la respuesta es `200 OK`
- **AND** el body contiene `secret` (base32 string) y `uri` (otpauth URI para generar QR)

#### Scenario: Re-enrolamiento

- **GIVEN** un usuario autenticado con 2FA ya activo
- **WHEN** se envía `POST /api/v1/auth/2fa/enroll`
- **THEN** la respuesta es `409 Conflict`
- **AND** el body contiene `detail: "2FA ya está activo. Desactivelo primero para re-enrolar."`

### Requirement: Verificación de código TOTP

El sistema SHALL exponer `POST /api/v1/auth/2fa/verify` (autenticado) para verificar un código TOTP y activar 2FA.

#### Scenario: Verificación exitosa

- **GIVEN** un usuario que llamó a enroll y tiene un `secret` generado
- **WHEN** se envía `POST /api/v1/auth/2fa/verify` con `{"code": "123456"}` (código TOTP válido para ese secreto)
- **THEN** la respuesta es `200 OK`
- **AND** el secreto TOTP se persiste cifrado en `User.totp_secret_cifrado`
- **AND** el usuario ahora tiene 2FA activo

#### Scenario: Código TOTP inválido

- **GIVEN** un usuario que llamó a enroll
- **WHEN** se envía código incorrecto
- **THEN** la respuesta es `400 Bad Request`
- **AND** el secreto NO se persiste

### Requirement: Validación 2FA en login

El sistema SHALL integrar el 2FA como gate en el flujo de login: si el usuario tiene 2FA activo, la sesión no se emite hasta validar el código TOTP.

#### Scenario: Login requiere 2FA

- **GIVEN** un usuario con 2FA activo
- **WHEN** se envía `POST /api/v1/auth/login` con credenciales correctas
- **THEN** la respuesta es `200 OK`
- **AND** el body contiene `{"2fa_required": true, "2fa_token": "<token JWT temporal>"}`
- **AND** no contiene `access_token` ni `refresh_token`

#### Scenario: Validación 2FA completa login

- **GIVEN** un usuario con 2FA activo que obtuvo un `2fa_token` válido
- **WHEN** se envía `POST /api/v1/auth/2fa/validate` con el `2fa_token` y un `code` TOTP válido
- **THEN** la respuesta es `200 OK`
- **AND** contiene `access_token`, `refresh_token` y `token_type: "bearer"`

#### Scenario: Validación 2FA con código incorrecto

- **GIVEN** un `2fa_token` válido
- **WHEN** se envía `POST /api/v1/auth/2fa/validate` con código TOTP incorrecto
- **THEN** la respuesta es `401 Unauthorized`

#### Scenario: 2fa_token expirado

- **GIVEN** un `2fa_token` emitido hace más de 5 minutos
- **WHEN** se envía a validate
- **THEN** la respuesta es `401 Unauthorized`

#### Scenario: 2fa_token no puede acceder a otros endpoints

- **GIVEN** un `2fa_token` válido
- **WHEN** se usa para acceder a cualquier otro endpoint protegido
- **THEN** la respuesta es `401 Unauthorized`

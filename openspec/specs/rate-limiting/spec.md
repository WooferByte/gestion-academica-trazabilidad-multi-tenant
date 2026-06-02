## ADDED Requirements

### Requirement: Rate limiting en login

El sistema SHALL limitar los intentos de login a 5 por minuto por combinación IP+email.

#### Scenario: 5 intentos exitosos, el 6to es bloqueado

- **GIVEN** la misma IP y el mismo email
- **WHEN** se envían 6 requests de login en menos de 1 minuto
- **THEN** los primeros 5 retornan `200 OK` o `401 Unauthorized` según las credenciales
- **AND** el 6to retorna `429 Too Many Requests`

#### Scenario: Ventana de rate limit se reinicia tras 1 minuto

- **GIVEN** una IP+email que fueron rate-limited
- **WHEN** se espera 1 minuto
- **AND** se envía un nuevo login request
- **THEN** la respuesta es normal (no bloqueada)

#### Scenario: Distintas IPs no comparten rate limit

- **GIVEN** un email con 5 intentos fallidos desde IP_A
- **WHEN** se envía login desde IP_B con el mismo email
- **THEN** el intento desde IP_B NO está rate-limited

#### Scenario: Distintos emails no comparten rate limit

- **GIVEN** una IP con 5 intentos fallidos para email_A
- **WHEN** se envía login desde la misma IP para email_B
- **THEN** el intento para email_B NO está rate-limited

### Requirement: Rate limiter como middleware/dependency

El rate limiter SHALL ser configurable como dependency de FastAPI y aplicarse únicamente al endpoint de login.

#### Scenario: Rate limiter no afecta otros endpoints

- **GIVEN** una IP rate-limited en login
- **WHEN** se accede a cualquier otro endpoint (ej. health)
- **THEN** la respuesta es normal (no bloqueada)

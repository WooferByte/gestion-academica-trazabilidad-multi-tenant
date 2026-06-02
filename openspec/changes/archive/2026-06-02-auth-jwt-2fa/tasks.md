## TDD Obligatorio

Strict TDD aplica a TODAS las tareas: RED (test que falla) → GREEN (código mínimo) → TRIANGULATE (múltiples casos) → REFACTOR.

## Antes de empezar

- Cargar skills: `fastapi-templates`, `python-testing-patterns`, `test-driven-development`, `api-security-best-practices`.
- Leer: `knowledge-base/03_actores_y_roles.md`, `knowledge-base/07_flujos_principales.md`, `docs/ARQUITECTURA.md §5`, `openspec/changes/auth-jwt-2fa/proposal.md`, `openspec/changes/auth-jwt-2fa/design.md`.
- Verificar baseline: `pytest backend/tests/` debe pasar verde con los tests de C-01 + C-02.

---

## 1. Agregar dependencias y preparar infra

- [x] 1.1 Agregar `pyjwt`, `passlib[argon2]`, `pyotp` a `backend/pyproject.toml`
- [x] 1.2 Ejecutar install para confirmar resolución de dependencias
- [x] 1.3 Agregar `REFRESH_TOKEN_EXPIRE_DAYS` a `core/config.py` (INT, default 30)
- [x] 1.4 Agregar `DEBUG` a `core/config.py` (BOOL, default false) — controla si el token de recuperación se expone en la respuesta
- [x] 1.5 Agregar `DEBUG=true` a `.env.example` y al `.env` de desarrollo
- [x] 1.6 Verificar que la suite de C-01/C-02 sigue verde tras nuevas dependencias

## 2. Funciones de seguridad en core/security.py

- [x] 2.1 (RED) Escribir test de `hash_password()`: resultado comienza con `$argon2id$`, no es igual al input
- [x] 2.2 (GREEN) Implementar `hash_password()` y `verify_password()` usando `passlib.context.CryptContext` con esquema `argon2`
- [x] 2.3 (RED) Escribir test de JWT: `create_access_token()` emite token decodificable, `decode_token()` valida firma y exp
- [x] 2.4 (GREEN) Implementar `create_access_token()` y `decode_token()` usando `PyJWT` con HS256 y `SECRET_KEY`
- [x] 2.5 (RED) Escribir test de JWT expirado lanza `ExpiredSignatureError`
- [x] 2.6 (RED) Escribir test de JWT con firma inválida lanza `InvalidSignatureError`
- [x] 2.7 (TRIANGULATE) Probar claims exactos del JWT: contiene `sub`, `tenant_id`, `roles`, `exp`, `iat` y no contiene permisos

## 3. Modelo User

- [x] 3.1 (RED) Escribir test que cree un usuario con todos los campos, verifique UUID, email, password hash Argon2id, cifrado PII, roles default
- [x] 3.2 (GREEN) Implementar modelo `User` en `models/user.py` con columnas: `email`, `password_hash`, `nombre_cifrado`, `apellido_cifrado`, `dni_cifrado`, `roles` (JSONB), `totp_secret_cifrado`, `is_active`
- [x] 3.3 (TRIANGULATE) Verificar unique constraint compuesto `(email, tenant_id)`
- [x] 3.4 (TRIANGULATE) Verificar que mismo email en distintos tenants es válido

## 4. UserRepository

- [x] 4.1 (RED) Escribir test de `get_by_email()` que busca usuario por email dentro del tenant
- [x] 4.2 (GREEN) Implementar `UserRepository` con `get_by_email(email)`, hereda de `BaseRepository`
- [x] 4.3 (RED) Escribir test de `create()` que asigna tenant_id y persiste correctamente
- [x] 4.4 (TRIANGULATE) Verificar que `get_by_email()` respeta tenant scope (mismo email en otro tenant no se encuentra)

## 5. Rate limiter

- [x] 5.1 (RED) Escribir test: 5 intentos OK, 6to da 429 (misma IP+email)
- [x] 5.2 (GREEN) Implementar `LoginRateLimiter` con diccionario en memoria, método `check(ip, email) -> bool` y `record(ip, email)`
- [x] 5.3 (RED) Escribir test de ventana: esperar 1 minuto → rate limit reset
- [x] 5.4 (TRIANGULATE) Verificar que distintas IPs no comparten rate limit
- [x] 5.5 (TRIANGULATE) Verificar que distintos emails no comparten rate limit
- [x] 5.6 (TRIANGULATE) Verificar que rate limiter solo aplica a login, no a otros endpoints

## 6. Login endpoint (sin 2FA)

- [x] 6.1 (RED) Escribir test de login exitoso: credenciales correctas → `200 OK` con `access_token`, `refresh_token`, `token_type`, `expires_in`
- [x] 6.2 (GREEN) Implementar `POST /api/v1/auth/login` en `routers/auth.py`: validar credenciales, emitir JWT, persistir refresh token
- [x] 6.3 (RED) Escribir test de login con credencial incorrecta → `401`
- [x] 6.4 (RED) Escribir test de login con email inexistente → `401` (mismo mensaje)
- [x] 6.5 (RED) Escribir test de login de usuario soft-deleteado → `401`
- [x] 6.6 (RED) Escribir test de login de usuario inactivo → `401`
- [x] 6.7 (TRIANGULATE) Verificar claims del JWT emitido (sub, tenant_id, roles, exp, iat — sin permisos)

## 7. Refresh token con rotación

- [x] 7.1 (RED) Escribir test de refresh exitoso: refresh token válido → nuevo par access+refresh, anterior revocado
- [x] 7.2 (GREEN) Implementar `POST /api/v1/auth/refresh` con rotación: verificar token en DB, revocar anterior, crear nuevo, devolver par
- [x] 7.3 (RED) Escribir test de refresh con token revocado → `401`
- [x] 7.4 (RED) Escribir test de reuso de refresh token → invalida toda la familia
- [x] 7.5 (RED) Escribir test de refresh con token expirado → `401`

## 8. Logout

- [x] 8.1 (RED) Escribir test de logout exitoso: marca refresh token como revocado
- [x] 8.2 (GREEN) Implementar `POST /api/v1/auth/logout`: recibe refresh token en body, lo revoca en DB
- [x] 8.3 (RED) Escribir test de logout sin autenticación → `401`

## 9. RefreshTokenRepository

- [x] 9.1 (RED) Escribir test de `create_refresh_token()` persiste token con token_hash, family_id, expires_at
- [x] 9.2 (GREEN) Implementar `RefreshTokenRepository` con métodos: `create()`, `get_by_token_hash()`, `revoke()`, `revoke_family()`
- [x] 9.3 (RED) Escribir test de `revoke_family()` revoca todos los tokens de una family_id
- [x] 9.4 (TRIANGULATE) Verificar que token_hash es SHA-256 del UUID emitido (no almacena el valor plano)

## 10. 2FA TOTP — Enrolamiento y verificación

- [x] 10.1 (RED) Escribir test de `enroll()`: genera secreto, devuelve secret y URI
- [x] 10.2 (GREEN) Implementar `POST /api/v1/auth/2fa/enroll` usando `pyotp`
- [x] 10.3 (RED) Escribir test de `verify()`: activa 2FA con código TOTP válido
- [x] 10.4 (GREEN) Implementar `POST /api/v1/auth/2fa/verify`: verifica código, persiste secreto cifrado en User
- [x] 10.5 (RED) Escribir test de `verify()` con código inválido → `400`
- [x] 10.6 (RED) Escribir test de re-enrolamiento con 2FA ya activo → `409`

## 11. 2FA TOTP — Gate en login

- [x] 11.1 (RED) Escribir test de login con 2FA activo → `2fa_required: true` + `2fa_token`
- [x] 11.2 (GREEN) Modificar login para detectar 2FA activo y emitir `2fa_token` en lugar de sesión
- [x] 11.3 (RED) Escribir test de `2fa/validate` con código válido → sesión emitida
- [x] 11.4 (GREEN) Implementar `POST /api/v1/auth/2fa/validate`: verifica 2fa_token + código TOTP, emite sesión
- [x] 11.5 (RED) Escribir test de `2fa/validate` con código inválido → `401`
- [x] 11.6 (RED) Escribir test de `2fa_token` expirado → `401`
- [x] 11.7 (RED) Escribir test que `2fa_token` no otorga acceso a otros endpoints → `401`

## 12. Recuperación de contraseña

- [x] 12.1 (RED) Escribir test de `forgot()`: genera token único, retorna token + expires_in
- [x] 12.2 (GREEN) Implementar `POST /api/v1/auth/forgot`: busca usuario por email, genera token UUID con hash SHA-256, expiración 15 min
- [x] 12.3 (RED) Escribir test de `forgot()` con email inexistente → `200` (mismo mensaje, no revelar existencia)
- [x] 12.4 (RED) Escribir test de `reset()`: token válido → password actualizado, token marcado usado, refresh tokens revocados
- [x] 12.5 (GREEN) Implementar `POST /api/v1/auth/reset`: verifica token (no expirado, no usado), actualiza password_hash, revoca refresh tokens
- [x] 12.6 (RED) Escribir test de `reset()` con token expirado → `401`
- [x] 12.7 (RED) Escribir test de `reset()` con token ya usado → `401`
- [x] 12.8 (TRIANGULATE) Verificar que token es de un solo uso

## 13. Dependency get_current_user

- [x] 13.1 (RED) Escribir test de `get_current_user` con token válido → retorna `UserContext`
- [x] 13.2 (GREEN) Implementar `get_current_user` en `core/dependencies.py`: decode JWT, verificar tenant activo, verificar usuario no soft-deleteado, retornar `UserContext`
- [x] 13.3 (RED) Escribir test de `get_current_user` con token expirado → `401`
- [x] 13.4 (RED) Escribir test de `get_current_user` con firma inválida → `401`
- [x] 13.5 (RED) Escribir test de `get_current_user` con tenant inactivo → `401`
- [x] 13.6 (RED) Escribir test de identidad NO suplantable por parámetros (body/query/header)
- [x] 13.7 (TRIANGULATE) Verificar que `UserContext` está disponible en services y repositories

## 14. Migración Alembic 002

- [x] 14.1 Crear migración Alembic `002_create_users_and_auth_tables` con `revises = "001"`
- [x] 14.2 La migración debe crear tablas: `users`, `refresh_tokens`, `password_reset_tokens`
- [x] 14.3 Ejecutar `alembic upgrade head` en DB de desarrollo → confirmar tablas creadas
- [x] 14.4 Ejecutar `alembic downgrade -1` → confirmar tablas eliminadas
- [x] 14.5 Ejecutar `alembic upgrade head` nuevamente → confirmar re-creación

## 15. Tests de integración multi-tenant y seguridad

- [x] 15.1 (RED) Escribir test de aislamiento de login: usuario del tenant A no puede hacer login en tenant B
- [x] 15.2 (GREEN) Asegurar que el flujo login verifica tenant_id del JWT vs tenant_id del usuario
- [x] 15.3 (RED) Escribir test de rate limiting con múltiples IPs en paralelo
- [x] 15.4 (TRIANGULATE) Probar que JWT de tenant A no permite acceder a datos del tenant B

## 16. Verificación final

- [x] 16.1 Ejecutar suite completa de tests (`pytest backend/tests/`) → verde
- [x] 16.2 Confirmar cobertura ≥80% líneas, ≥90% reglas de negocio en el código nuevo
- [x] 16.3 Confirmar que ningún archivo `.py` nuevo supera 500 LOC
- [x] 16.4 Confirmar que todos los schemas Pydantic nuevos usan `extra='forbid'`
- [x] 16.5 Confirmar snake_case en funciones, variables, columnas de BD
- [x] 16.6 Confirmar que el JWT nunca contiene permisos (solo `sub`, `tenant_id`, `roles`, `exp`, `iat`)
- [x] 16.7 Confirmar que no hay rutas protegidas que acepten identidad desde parámetros de request

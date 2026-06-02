## Why

activia-trace no tiene autenticación. Hoy el sistema expone endpoints públicos sin identidad ni sesión. Sin un modelo `User`, sin JWT, sin hashing de passwords, sin rate limiting ni 2FA, el sistema no puede identificar quién ejecuta cada acción — y eso rompe el principio fundacional del producto: *todo audita*. C-02 dejó la tenancy layer y el modelo `Tenant` listos; C-03 los completa con autenticación real: login con email+password (Argon2id), sesión JWT con access token corto + refresh rotation, 2FA TOTP opcional, recuperación de contraseña, y la dependency `get_current_user` que toda request futura necesita. Sin este change, ningún otro change de dominio (C-04 RBAC, C-05 audit, C-06 estructura académica) puede operar con identidad.

## What Changes

- **Modelo `User`**: entidad SQLAlchemy con `email` (único por tenant), password hasheado (Argon2id), PII cifrada (nombre, apellido, DNI), referencia a `Tenant` vía `tenant_id`, timestamps y soft delete desde `BaseModelMixin`. Roles asignados como lista de strings (pre-RBAC, se migra a tabla separada en C-04).
- **Login**: `POST /api/v1/auth/login` — recibe `email` + `password`, valida contra Argon2id, si el usuario tiene 2FA activo responde con `2fa_required: true` y un token temporal (`2fa_token`) para el segundo paso; si no tiene 2FA, emite par JWT (access + refresh con rotación).
- **2FA TOTP**: `POST /api/v1/auth/2fa/enroll` — genera secreto TOTP y lo devuelve como QR URI. `POST /api/v1/auth/2fa/verify` — verifica el código TOTP y completa la activación. `POST /api/v1/auth/2fa/validate` — valida el código TOTP post-login con el `2fa_token` temporal y emite la sesión definitiva.
- **Refresh**: `POST /api/v1/auth/refresh` — recibe refresh token válido, rota (invalida el anterior), emite nuevo par access+refresh. Reuso de un refresh token ya rotado invalida toda la familia de refresh tokens del usuario.
- **Logout**: `POST /api/v1/auth/logout` — revoca el refresh token activo (elimina o marca como revocado).
- **Recuperación de contraseña**: `POST /api/v1/auth/forgot` — genera token de un solo uso con expiración (15 min) y lo devuelve (mock de email en esta fase). `POST /api/v1/auth/reset` — valida token y actualiza password.
- **Rate limiting**: middleware/dependency que limita 5 intentos por minuto por combinación IP+email en login.
- **Dependency `get_current_user`**: extrae y verifica el JWT (firma, expiración, tenant activo), resuelve `User` desde DB, inyecta `UserContext` (user_id, tenant_id, roles) en las capas inferiores. La identidad/tenant SOLO se deriva del JWT verificado, nunca de parámetros de request.
- **Migración Alembic 002**: crea tabla `users`, tabla `refresh_tokens`, tabla `password_reset_tokens`.
- **No es BREAKING**: el código existente de C-01/C-02 no cambia; C-02 ya tiene `get_tenant()` y placeholders para `get_current_user`.

## Capabilities

### New Capabilities

- `user-model`: modelo `User` con email único por tenant, password Argon2id, PII cifrada, roles como lista de strings.
- `user-auth`: endpoints de login con email+password, con y sin 2FA, validación de credenciales Argon2id, emisión de JWT.
- `jwt-tokens`: emisión y verificación de JWT (access 15 min, claims mínimos), refresh token con rotación, revocación.
- `two-factor-auth`: enrolamiento TOTP, verificación, gate 2FA en login.
- `password-recovery`: token de un solo uso con expiración, cambio de contraseña.
- `rate-limiting`: limitador 5 req/min por IP+email en login.
- `current-user-dependency`: `get_current_user` que resuelve identidad y tenant desde el JWT.
- `alembic-migration-002`: migración que crea tablas users, refresh_tokens, password_reset_tokens.

### Modified Capabilities

- `tenancy-layer` (de C-02): `get_tenant()` ahora se resuelve automáticamente desde el JWT vía `get_current_user`, no necesita tenant_id inyectado manualmente.
- `app-scaffold` (de C-01): `core/dependencies.py` implementa `get_current_user` (antes era placeholder). `core/security.py` gana funciones JWT y Argon2id. `core/config.py` gana settings para JWT (SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS).

## Impact

- **Nuevo código**: `backend/app/models/user.py`, `backend/app/schemas/auth.py`, `backend/app/services/auth_service.py`, `backend/app/services/totp_service.py`, `backend/app/repositories/user_repository.py`, `backend/app/repositories/refresh_token_repository.py`, `backend/app/api/v1/routers/auth.py`, `backend/app/core/rate_limiter.py`, migración Alembic 002.
- **Modificaciones**: `core/security.py` (agregar JWT + Argon2id), `core/config.py` (agregar settings JWT), `core/dependencies.py` (implementar `get_current_user`), `core/tenancy.py` (vincular a JWT).
- **Dependencias nuevas**: `pyotp` (TOTP), `passlib` (wrapper Argon2id — o usar `argon2-cffi` directamente).
- **Tests**: `backend/tests/test_auth_login.py`, `backend/tests/test_auth_refresh.py`, `backend/tests/test_auth_2fa.py`, `backend/tests/test_auth_recovery.py`, `backend/tests/test_rate_limit.py`, `backend/tests/test_get_current_user.py`.
- **Habilita** a C-04 (RBAC, necesita `get_current_user`), C-05 (audit log, necesita identidad), C-06 (estructura académica, necesita identidad), C-07 (grading, necesita auth).
- **Governance**: CRÍTICO — auth es el dominio de seguridad #1 del proyecto. Identidad, sesión y 2FA son la base de todo el control de acceso. Requiere revisión antes de implementar.

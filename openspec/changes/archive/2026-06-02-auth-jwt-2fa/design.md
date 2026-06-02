## Context

C-01 dejó el esqueleto FastAPI con health endpoint. C-02 agregó el modelo `Tenant`, el mixin `BaseModelMixin`, `BaseRepository` con scope de tenant, el cifrado AES-256-GCM en `core/security.py`, la tenancy layer en `core/tenancy.py`, y la migración 001 (tabla `tenants`). También dejó placeholders en `core/dependencies.py` para `get_current_user` y `require_permission`.

Sin embargo, el sistema no puede identificar quién ejecuta cada acción. No hay modelo `User`, no hay login, no hay sesión. Cada request es anónima. C-03 construye la capa completa de autenticación sobre los cimientos de C-01/C-02.

Este es governance CRÍTICO: auth es el dominio de seguridad #1 del proyecto. Cada decisión de diseño está orientada a la regla de oro "identidad SOLO del JWT verificado, nunca de parámetros de request".

## Goals / Non-Goals

**Goals:**

- Modelo `User` con email único por tenant, password hasheado (Argon2id), PII cifrada (nombre, apellido, DNI), roles como lista de strings (pre-RBAC).
- Login `POST /api/v1/auth/login` con validación de credenciales y emisión de JWT.
- 2FA TOTP opcional: enrolar, verificar, gate entre validación de credenciales y emisión de sesión.
- Refresh token con rotación: `POST /api/v1/auth/refresh`.
- Logout: `POST /api/v1/auth/logout` con revocación del refresh token.
- Recuperación de contraseña: `POST /api/v1/auth/forgot` + `POST /api/v1/auth/reset`.
- Rate limiting: 5 intentos/minuto por IP+email en login.
- Dependency `get_current_user` que resuelve identidad + tenant desde JWT verificado.
- Claims JWT mínimos: `sub` (user_id), `tenant_id`, `roles`, `exp`, `iat`. NUNCA permisos en el token.
- Migración Alembic 002: tablas `users`, `refresh_tokens`, `password_reset_tokens`.

**Non-Goals:**

- RBAC con matriz rol×permiso administrable (→ C-04). Los roles se almacenan como lista de strings en `User.roles`; la validación de permisos granular será en C-04.
- Audit log de acciones (→ C-05). Solo se registran eventos de auth como login/logout en logs estructurados.
- Frontend de login (→ C-21). Este change provee la API REST; el frontend se conecta en C-21.
- Impersonación (→ módulo dedicado post-MVP).
- OAuth2 / SSO con Moodle (→ Fase 2, ADR-001).
- Envío real de email de recuperación (mock OK en este change; integración con N8N/mail service en C-XX).
- Roles como tabla administrable (→ C-04). Usamos `roles: list[str]` como campo JSONB en User.

## Decisions

### D1 — Argon2id vía `passlib[bcrypt]` + `argon2-cffi`

El password se hashea con Argon2id usando `passlib` con el backend `argon2`:

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

- `passlib` abstrae el backend concreto y permite cambiar de algoritmo sin modificar el código de negocio.
- La configuración Argon2id usa parámetros por defecto de `passlib` (time_cost=2, memory_cost=19456, parallelism=1, hash_len=32, salt_len=16).

**Alternativa descartada**: `bcrypt` solo. Argon2id es el ganador del PHC (Password Hashing Competition) y es resistente a ataques con GPU/ASIC. Es el estándar recomendado por OWASP.

### D2 — JWT con `PyJWT` (librería `jose` o `PyJWT`)

Se usa la librería `PyJWT` (`import jwt`) con algoritmo HS256 (HMAC-SHA256):

```python
import jwt
from datetime import datetime, timedelta, timezone
from app.core.config import Settings

def create_access_token(user_id: str, tenant_id: str, roles: list[str]) -> str:
    settings = Settings()
    payload = {
        "sub": user_id,
        "tenant_id": tenant_id,
        "roles": roles,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def decode_token(token: str) -> dict:
    settings = Settings()
    return jwt.decode(token, settings.secret_key, algorithms=["HS256"])
```

- Claims mínimos: `sub` (UUID user_id como string), `tenant_id` (UUID como string), `roles` (`list[str]`), `exp`, `iat`.
- **NUNCA permisos en el token**: los permisos se resuelven server-side en C-04.
- Firma HMAC-SHA256 con `SECRET_KEY` de Settings (mín. 32 chars, misma variable que usa AES, pero distinto propósito).

**Alternativa descartada**: RS256 (asymmetric). Para un sistema single-service sin microservicios, la complejidad de key management no se justifica. HS256 es suficiente; si en el futuro se necesita RS256 (por ej. para compartir verificación con otros servicios), migrar es un cambio de algoritmo.

### D3 — Refresh token con rotación y detección de reuso (token family)

El refresh token se almacena en DB (tabla `refresh_tokens`) con los siguientes campos:

```python
class RefreshToken(Base, BaseModelMixin):
    __tablename__ = "refresh_tokens"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False)  # SHA-256 del token JIT
    family_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)  # familia de refresh
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

- Cada refresh token pertenece a una `family_id`. Cuando se usa un refresh, se crea uno nuevo con la misma `family_id` y se revoca el anterior.
- **Detección de reuso**: si un refresh token ya revocado se presenta nuevamente, se revoca TODA la familia (todos los tokens con esa `family_id`). Esto invalida todas las sesiones del usuario.
- El token JIT (Just-In-Time) que se envía al cliente es un UUID v4. En DB se guarda `SHA-256(token)` para no almacenar el valor secreto en texto plano.
- Expiración del refresh token: 30 días (configurable vía `Settings.refresh_token_expire_days`).

**Alternativa descartada**: refresh token como JWT sin persistencia. No permite revocación por logout ni detección de reuso. La tabla en DB es la forma correcta de implementar refresh rotation con seguridad.

### D4 — 2FA TOTP con `pyotp`

```python
import pyotp

def generate_totp_secret() -> str:
    return pyotp.random_base32()

def get_totp_uri(secret: str, email: str, issuer: str = "activia-trace") -> str:
    return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer)

def verify_totp(secret: str, code: str) -> bool:
    totp = pyotp.TOTP(secret)
    return totp.verify(code)
```

- El secreto TOTP se almacena **cifrado con AES-256** (usando `encrypt()` de `core/security.py`) en el modelo `User`.
- Si el usuario tiene `totp_secret` no nulo → 2FA activo.
- Flujo de login con 2FA:
  1. `POST /auth/login` con email+password válido → si el usuario tiene 2FA activo, responde `{"2fa_required": True, "2fa_token": "<token temporal>"}`. No emite sesión.
  2. El `2fa_token` es un JWT de vida ultra-corta (5 min) firmado con la misma `SECRET_KEY`, que contiene `sub`, `tenant_id`, `purpose: "2fa"`. Este token **no otorga acceso a ningún otro endpoint**.
  3. `POST /auth/2fa/validate` con `2fa_token` + `code` TOTP → si el código es válido, emite sesión real (access + refresh).
- Enrolamiento: `POST /auth/2fa/enroll` (autenticado) → genera secreto, devuelve `secret` y `uri`. `POST /auth/2fa/verify` (autenticado, con `code`) → verifica código, persiste secreto cifrado en User.

**Alternativa descartada**: 2FA obligatorio para todos o a nivel tenant. Se opta por opcional por usuario (más flexible). Cada usuario decide si lo activa.

### D5 — Rate limiting en memoria

```python
from collections import defaultdict
from datetime import datetime, timedelta, timezone

class LoginRateLimiter:
    def __init__(self):
        self._attempts: dict[str, list[datetime]] = defaultdict(list)
    
    def check(self, ip: str, email: str) -> bool:
        key = f"{ip}:{email}"
        now = datetime.now(timezone.utc)
        window_start = now - timedelta(minutes=1)
        self._attempts[key] = [t for t in self._attempts[key] if t > window_start]
        return len(self._attempts[key]) < 5
    
    def record(self, ip: str, email: str) -> None:
        key = f"{ip}:{email}"
        self._attempts[key].append(datetime.now(timezone.utc))
```

- Implementación en memoria (diccionario), no requiere Redis ni infra adicional.
- Límite: 5 intentos por minuto por combinación IP+email.
- **Punto de decisión**: para MVP con un solo tenant es suficiente. Si se necesita sticky rate limiting entre instancias en el futuro, migrar a Redis es directo (misma interfaz).
- El rate limiter se inyecta como singleton via FastAPI lifespan o dependency global.

**Alternativa descartada**: Redis desde el día 0. No se justifica para MVP (overhead de infra, complejidad operativa). Rate limiting en memoria es suficiente para un solo worker; si se escala horizontalmente, se migra a Redis.

### D6 — `get_current_user` dependency

La dependency se implementa en `core/dependencies.py`:

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> UserContext:
    payload = decode_token(token)
    user_id = uuid.UUID(payload["sub"])
    tenant_id = uuid.UUID(payload["tenant_id"])
    
    # Verificar que el tenant existe y está activo
    tenant = await tenant_repo.get(tenant_id)
    if not tenant or tenant.estado != "Activo":
        raise HTTPException(status_code=401, detail="Tenant inactivo o no encontrado")
    
    # Verificar que el usuario existe y no está soft-deleteado
    user_repo = UserRepository(session, tenant_id)
    user = await user_repo.get(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")
    
    return UserContext(user_id=user_id, tenant_id=tenant_id, roles=payload["roles"])
```

- `UserContext` es un DTO que carry `user_id`, `tenant_id`, `roles`.
- `oauth2_scheme` es `fastapi.security.OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")`.
- Esta dependency se inyecta en cualquier endpoint protegido.
- **La identidad/tenant SOLO vienen del JWT verificado**. Si el payload JWT está manipulado, `jwt.decode()` falla con excepción → 401.

### D7 — Modelo User con campos PII cifrados

```python
class User(Base, BaseModelMixin):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    nombre_cifrado: Mapped[str | None] = mapped_column(Text, nullable=True)
    apellido_cifrado: Mapped[str | None] = mapped_column(Text, nullable=True)
    dni_cifrado: Mapped[str | None] = mapped_column(Text, nullable=True)
    roles: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    totp_secret_cifrado: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    __table_args__ = (
        UniqueConstraint("email", "tenant_id", name="uq_users_email_tenant"),
        Index("ix_users_email", "email"),
    )
```

- `email` en texto plano (es identificador de login, no PII sensible).
- `nombre`, `apellido`, `DNI` se almacenan cifrados con AES-256-GCM.
- `roles` como JSONB (`list[str]`), se migrará a tabla separada en C-04.
- `totp_secret_cifrado`: solo no nulo si el usuario activó 2FA.
- Unique constraint compuesto `(email, tenant_id)` → mismo email puede existir en distintos tenants.
- `UserService` expone métodos para crear, buscar por email, verificar password, gestionar 2FA.

### D8 — Estrategia de tests

Todas las pruebas con **DB real** (PostgreSQL), sin mocks:

- `test_auth_login.py`: login OK emite par JWT, login con credencial incorrecta → 401, login con 2FA → 2fa_required, login con tenant inactivo → 401.
- `test_auth_refresh.py`: refresh OK emite nuevo par, refresh con token revocado → 401, reuso de refresh revocado invalida toda la familia.
- `test_auth_2fa.py`: enroll genera secreto, verify activa 2FA, validate con código correcto emite sesión.
- `test_auth_recovery.py`: forgot genera token único, reset cambia password con token válido, reset con token inválido → 401.
- `test_rate_limit.py`: 6 requests en 1 min → 5 OK, 6to 429.
- `test_get_current_user.py`: token válido → UserContext, token expirado → 401, token sin tenant → 401, identidad no se puede suplantar por body/query.

### D9 — Flujo de recuperación de contraseña

1. `POST /auth/forgot` con `{"email": "..."}` → busca usuario por email+tenant, genera token único (UUID v4, hash SHA-256 almacenado en `password_reset_tokens`), expiración 15 min. 
   - **Si `DEBUG=true`** (entorno de desarrollo): devuelve el token en la respuesta (`{"detail": "Token enviado", "token": "..."}`).
   - **Si `DEBUG=false`** (producción): solo simula el envío, responde `{"detail": "Si el email existe, recibirás un enlace de recuperación"}` sin exponer el token.
   - Esto permite desarrollo sin infra de email, pero no expone tokens en producción.
2. `POST /auth/reset` con `{"token": "...", "new_password": "..."}` → verifica token (no expirado, no usado), actualiza password_hash, marca token como usado.

Tabla `password_reset_tokens`:
```python
class PasswordResetToken(Base, BaseModelMixin):
    __tablename__ = "password_reset_tokens"
    
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

## Risks / Trade-offs

- **[Rate limiting en memoria no escala horizontalmente]** → Mitigación: la interfaz `RateLimiter` es abstracta; migrar a Redis en el futuro es un cambio de implementación, no de API. Para MVP con un solo worker, es suficiente.
- **[Refresh token en DB agrega latencia]** → Mitigación: es una query indexada por `token_hash` (único). La latencia es sub-milisegundo. El trade-off (capacidad de revocación) vale la pena.
- **[PII cifrada impide búsqueda por nombre]** → Mitigación: email es el identificador de búsqueda principal. Si se necesita buscar por nombre, se agrega un índice de texto generado a partir del nombre descifrado (feature futura).
- **[Roles como JSONB pre-RBAC requerirá migración de datos en C-04]** → Mitigación: se documenta en las tasks de C-03 y C-04. La migración será agregar tabla `user_roles` y poblar desde `User.roles`.
- **[2FA como dependencia externa (pyotp)]** → Mitigación: `pyotp` es una librería madura, sin dependencias del sistema, implementación del estándar RFC 6238. El secreto nunca sale del backend salvo como URI para el QR.

## Migration Plan

1. Agregar `pyjwt`, `passlib[argon2]`, `pyotp` a `pyproject.toml`.
2. Ejecutar `alembic upgrade head` → migración 002 crea tablas `users`, `refresh_tokens`, `password_reset_tokens`.
3. Ejecutar suite completa de tests (`pytest backend/tests/`) → verde.
4. Rollback: `alembic downgrade -1` → elimina las tres tablas. No hay datos de negocio porque ningún otro change ha creado usuarios reales aún.

## Open Questions

- **¿Seed de usuario admin para desarrollo?** Se puede resolver en apply: agregar un script `seed.py` que cree un usuario admin en el tenant TUPAD. No bloquea el diseño.
- **¿Formato del DTO de error?** Se define en apply: `{"detail": "...", "code": "..."}`. Consistente con C-02.

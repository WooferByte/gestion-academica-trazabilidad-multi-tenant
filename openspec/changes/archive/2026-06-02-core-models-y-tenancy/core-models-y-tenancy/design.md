## Context

C-01 dejó el esqueleto corriendo: FastAPI arranca, `GET /health` responde, la DB async conecta, los slots de `core/` están reservados. Ahora necesitamos la primera entidad real (`Tenant`), el mixin base que toda tabla futura va a heredar, y el repository genérico que garantiza aislamiento multi-tenant desde el día 0. También el cifrado AES-256 para PII (RNF-08).

Este change toca el **cimiento de seguridad del proyecto**: multi-tenancy row-level. Es governance CRÍTICO. Cada decisión de diseño está pensada para que un query sin scope de tenant no pase code review.

## Goals / Non-Goals

**Goals:**

- Modelo `Tenant` como primera entidad SQLAlchemy: tabla `tenants` con UUID PK, timestamps, soft delete, estado.
- Mixin base `BaseModelMixin` con `id` (UUID v4), `tenant_id` (FK → Tenant), `created_at`, `updated_at`, `deleted_at`.
- Soft delete transversal: `deleted_at` set → registro invisible para queries default.
- Repository genérico `BaseRepository[T]` con scope de tenant obligatorio en get, get_multi, create, update, soft_delete, exists.
- Utilidad AES-256-GCM en `core/security.py`: funciones `encrypt()`/`decrypt()` y helpers para atributos `[cifrado]`.
- Fábrica de engine (Alembic) async-ready: migración 001 crea tabla `tenants` con índice único por nombre y código activo.
- Tenancy layer: `core/tenancy.py` con `get_tenant()` dependency, validación de tenant activo.
- Tests: aislamiento multi-tenant, soft delete, round-trip cifrado, timestamps.

**Non-Goals:**

- Modelos de dominio específicos (Usuario, Materia, Carrera → C-06/C-03).
- Auth, JWT, Argon2id (→ C-03).
- RBAC matriz permisos (→ C-04).
- Audit log (→ C-05).
- Seed de datos de tenant (se puede hacer manual para tests; seed automático será parte del onboarding de tenant futuro).

## Decisions

### D1 — Mixin base como clase SQLAlchemy declarativa mixin

Se crea `models/mixins.py` con `BaseModelMixin`:

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Boolean, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declared_attr, Mapped, mapped_column

class BaseModelMixin:
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    @declared_attr
    def tenant_id(cls) -> Mapped[uuid.UUID | None]:
        if cls.__name__ == "Tenant":
            return mapped_column(UUID(as_uuid=True), nullable=True)
        return mapped_column(
            UUID(as_uuid=True),
            ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
```

- **`Tenant`** es la excepción: su `tenant_id` es nullable (sin FK a sí mismo).
- `id` se genera como UUID v4 automático (no secuencial, no expuesto en URLs como selector de sesión).
- `updated_at` usa `onupdate` de SQLAlchemy para auto-actualización.

**Alternativa descartada**: usar `id` como columna en cada modelo sin mixin. Se descarta porque duplica código en N modelos y viola DRY.

### D2 — Soft delete mediante filter en repository, no event listener

El soft delete se implementa **en el repository**, no vía eventos SQLAlchemy ni `@event.listens_for`:

```python
class BaseRepository[T: BaseModelMixin]:
    def __init__(self, session: AsyncSession, tenant_id: uuid.UUID):
        self._session = session
        self._tenant_id = tenant_id

    def _stmt(self) -> Statement:
        """Query base con scope de tenant y exclusión de soft-delete."""
        return (
            select(self._model)
            .where(self._model.tenant_id == self._tenant_id)
            .where(self._model.deleted_at.is_(None))
        )

    async def get(self, id: uuid.UUID) -> T | None:
        stmt = self._stmt().where(self._model.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
```

- El `_stmt()` siempre filtra por `tenant_id` y `deleted_at IS NULL`.
- Si un query necesita saltar el soft delete (raro, solo para admin/auditoría), se usa un método explícito `get_with_deleted()` con scope de tenant.
- **No hay forma de hacer un `get()` sin scope de tenant** — el repository no expone un método sin `tenant_id`. La única manera de romper aislamiento es acceder directamente a la sesión, lo que sería detectado en code review.

**Alternativa descartada**: event listener `before_execute` que inyecta tenant_id. Se descarta porque es magia implícita que dificulta debugging y testing.

### D3 — AES-256-GCM con `cryptography` library

Se implementa en `core/security.py` usando `cryptography.hazmat.primitives.ciphers.aead.AESGCM`:

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
import base64

def _get_key() -> bytes:
    key = settings.ENCRYPTION_KEY.encode("utf-8")
    return key  # settings ya valida que sea 32 bytes

def encrypt(plaintext: str) -> str:
    aesgcm = AESGCM(_get_key())
    nonce = os.urandom(12)  # 96 bits
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)
    # nonce + ciphertext codificado en base64
    return base64.b64encode(nonce + ciphertext).decode("utf-8")

def decrypt(payload: str) -> str:
    raw = base64.b64decode(payload.encode("utf-8"))
    nonce, ciphertext = raw[:12], raw[12:]
    aesgcm = AESGCM(_get_key())
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")
```

- **AEAD autenticado**: GCM garantiza integridad + confidencialidad.
- **Nonce único por cifrado**: `os.urandom(12)` asegura que el mismo texto plano produce distinto ciphertext cada vez.
- **Formato de storage**: base64(nonce(12) + ciphertext(N)) — auto-contenido, no requiere columna separada.
- **Nunca en logs**: todas las capas superiores (services, routers) reciben datos descifrados; la capa de repository/modelo es la única que ve el ciphertext.

**Dependencia agregada**: `cryptography` en `pyproject.toml`.

**Alternativa descartada**: `fernet.Fernet` (simétrico, incluye HMAC). Funciona, pero no permite cifrado a nivel de campo con nonce explícito como AESGCM. AES-256-GCM es el estándar para cifrado en reposo y es más directo para uso por campo.

### D4 — Migración Alembic 001: tenants

```python
"""001_create_tenants_table

Revision ID: 001
Revises: None
"""
def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.create_table(
        "tenants",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("codigo", sa.String(50), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="Activo"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("codigo", name="uq_tenants_codigo"),
    )
    op.create_index("ix_tenants_codigo", "tenants", ["codigo"])

def downgrade():
    op.drop_table("tenants")
```

- `uuid-ossp` extension para UUID generation en DB.
- `estado` como string (no enum nativo de PostgreSQL) por simplicidad inicial; se puede migrar a enum si se necesita.
- Unique `codigo` (código corto: "TUPAD", "OTRA").

### D5 — Tenancy layer en core/tenancy.py

```python
class TenantContext:
    """Portador del tenant activo durante una request."""
    def __init__(self, tenant_id: uuid.UUID):
        self.tenant_id = tenant_id

async def get_tenant() -> TenantContext:
    """Dependency: provee el tenant activo. En C-02 recibe tenant_id inyectado;
       en C-03+ se resolverá desde el JWT autenticado."""
    # TODO(C-03): resolver desde JWT en lugar de depender del caller
    ...
```

- `get_tenant()` se registra como dependency de FastAPI.
- Inicialmente su implementación depende de cómo se inyecte el tenant_id (C-03 definirá `get_current_user` que a su vez deriva el tenant del JWT).
- Mientras tanto, `get_tenant` acepta un tenant_id provisto explícitamente para testing y desarrollo.

### D6 — Estrategia de tests

Todas las pruebas con **DB real** (PostgreSQL via testcontainers o compose), sin mocks.

- `test_tenant_isolation.py`: crea tenant A y B, inserta registros (usando un modelo test), verifica que A no ve los de B.
- `test_soft_delete.py`: crea registro, soft_delete, verifica get/get_multi ya no lo devuelven. Verifica get_with_deleted lo devuelve.
- `test_encryption.py`: `encrypt("hola") != encrypt("hola")` (distinto nonce), `decrypt(encrypt(x)) == x`, decrypt con nonce corrupto falla.
- `test_mixin_timestamps.py`: `created_at` no nulo tras create, `updated_at` cambia tras update.
- `test_base_repository.py`: CRUD completo, paginación, exists, update parcial.

### D7 — Excepciones estandarizadas

En `core/exceptions.py` se agregan excepciones base:

- `AppException(HTTPException)` — base.
- `TenantNotFoundException(AppException)` — 404 si el tenant no existe o está inactivo.
- `EncryptionError(AppException)` — 500 si falla cifrado/descifrado (nonce corrupto, clave inválida).
- `SoftDeletedException(AppException)` — 409 si se intenta operar sobre un registro soft-deleteado.

## Risks / Trade-offs

- **[Tenant_id nullable en modelo Tenant es un caso borde]** → Mitigación: se documenta explícitamente en el mixin con un `if cls.__name__ == "Tenant"`. Solo Tenant usa nullable; cualquier otro modelo con tenant_id nullable sería detectado en code review como bug.
- **[AES-256-GCM nonce de 12 bytes requiere almacenamiento extra]** → Mitigación: es mínimo (12 bytes + ciphertext en base64, ~44% overhead sobre el plaintext para datos cortos como DNI). Aceptable para PII que no se consulta por búsqueda full-text.
- **[Soft delete en repository no aplica a queries arbitrarias]** → Mitigación: todo query del dominio pasa por el repository. Si alguien usa `session.execute(stmt)` directo desde un service, es detectable en code review (regla: services no tocan DB).
- **[Migración 001 crea extensión uuid-ossp que requiere superuser en PostgreSQL]** → Mitigación: se ejecuta con `IF NOT EXISTS`. En entornos restrictivos, el DBA concede el permiso una sola vez. Alternativa: generar UUIDs desde Python (SQLAlchemy `default=uuid.uuid4`) y no usar `uuid_generate_v4()` server-side. Se prefiere el default Python para portabilidad.

## Migration Plan

Deploy de C-02:
1. Agregar `cryptography` a `pyproject.toml`, rebuild imagen.
2. Ejecutar `alembic upgrade head` → migración 001 crea tabla `tenants`.
3. Tests: suite completa en CI.
4. Rollback: `alembic downgrade -1` → elimina tabla `tenants`. No hay datos de negocio que perder porque ningún otro change ha creado tablas aún.

## Open Questions

- **¿Seed de tenant inicial?** TUPAD debería existir como tenant seed para desarrollo. Se puede resolver en apply: un script `seed.py` o migración de datos. No bloquea el diseño.
- **¿Nombre del mixin?** `BaseModelMixin` vs `AuditMixin` vs `TenantScopedMixin`. Recomiendo `BaseModelMixin` porque es más que auditoría: incluye tenant_id que es el core del aislamiento.
- **¿Compatibilidad uuid-ossp vs genUUID Python?** Decisión de apply: si el entorno de desarrollo tiene permisos de superuser, se puede usar uuid-ossp; si no, se generan UUIDs desde Python (que es el default de SQLAlchemy). La migración usa `sa.text("uuid_generate_v4()")` como server_default opcional.

## TDD Obligatorio

Strict TDD aplica a TODAS las tareas: RED (test que falla) → GREEN (código mínimo) → TRIANGULATE (múltiples casos) → REFACTOR.

## Antes de empezar

- Cargar skills: `fastapi-templates`, `postgresql-table-design`, `python-testing-patterns`, `test-driven-development`.
- Leer: `knowledge-base/04_modelo_de_datos.md`, `docs/ARQUITECTURA.md §6 y §8`, `openspec/changes/core-models-y-tenancy/design.md`, `openspec/changes/core-models-y-tenancy/proposal.md`.
- Verificar baseline: `pytest backend/tests/` debe pasar verde con los tests de C-01.

---

## 1. Agregar dependencia `cryptography` y preparar infra

- [x] 1.1 Agregar `cryptography` a `backend/pyproject.toml` en la sección de dependencias
- [x] 1.2 Ejecutar install para confirmar resolución de dependencias
- [x] 1.3 Verificar que la suite de C-01 sigue verde tras la nueva dependencia

## 2. Excepciones estandarizadas (core/exceptions.py)

- [x] 2.1 (RED) Escribir test que importe las excepciones y verifique herencia: `AppException` hereda de `HTTPException`, `TenantNotFoundException` es 404, `EncryptionError` es 500, `SoftDeletedException` es 409
- [x] 2.2 (GREEN) Implementar `AppException`, `TenantNotFoundException`, `EncryptionError`, `SoftDeletedException` en `core/exceptions.py`
- [x] 2.3 (TRIANGULATE) Verificar mensaje personalizado y status code en cada excepción

## 3. Modelo Tenant

- [x] 3.1 (RED) Escribir test que cree un tenant con `nombre` y `codigo`, verifique que `id` es UUID, `created_at`/`updated_at` no nulos, `estado` default "Activo"
- [x] 3.2 (GREEN) Implementar modelo `Tenant` en `models/tenant.py` con SQLAlchemy declarativa, incluyendo `__tablename__ = "tenants"`, unique constraint en `codigo`, índice en `codigo`
- [x] 3.3 (TRIANGULATE) Verificar unique constraint: crear dos tenants con mismo `codigo` → error de integridad
- [x] 3.4 (TRIANGULATE) Verificar FK constraint: modelo con `tenant_id` inválido → FK violation

## 4. Mixin base (BaseModelMixin)

- [x] 4.1 (RED) Escribir test que cree un modelo test que herede de `BaseModelMixin` y verifique: `id` UUID, `tenant_id` FK, timestamps
- [x] 4.2 (GREEN) Implementar `BaseModelMixin` en `models/mixins.py` con `id`, `tenant_id`, `created_at`, `updated_at`, `deleted_at`. Usar `declared_attr` para `tenant_id` con excepción para modelo `Tenant` (nullable)
- [x] 4.3 (TRIANGULATE) Verificar que `created_at` se persiste, `updated_at` cambia en update, `deleted_at` es nullable

## 5. Cifrado AES-256-GCM (core/security.py)

- [x] 5.1 (RED) Escribir test de round-trip: encrypt(plaintext) → decrypt(ciphertext) == plaintext
- [x] 5.2 (GREEN) Implementar funciones `encrypt()` y `decrypt()` usando `cryptography.hazmat.primitives.ciphers.aead.AESGCM` con nonce de 12 bytes random + base64
- [x] 5.3 (RED) Escribir test que verifique que mismo plaintext produce distinto ciphertext (nonce aleatorio)
- [x] 5.4 (TRIANGULATE) Escribir test de ciphertext corrupto → `EncryptionError`
- [x] 5.5 (TRIANGULATE) Escribir test de clave incorrecta → `EncryptionError`
- [x] 5.6 (RED) Escribir test que verifique que `Settings` rechaza `ENCRYPTION_KEY` con longitud != 32
- [x] 5.7 (GREEN) Agregar validación de `ENCRYPTION_KEY` en `core/config.py` (Pydantic validator)

## 6. Tenancy layer (core/tenancy.py)

- [x] 6.1 (RED) Escribir test que cree dos tenants, inyecte `TenantContext` con uno y verifique que el contexto contiene el tenant_id correcto
- [x] 6.2 (GREEN) Implementar `TenantContext` y `get_tenant()` dependency en `core/tenancy.py`. `get_tenant()` acepta `tenant_id` como parámetro (se conectará al JWT en C-03)
- [x] 6.3 (TRIANGULATE) Verificar que el tenant activo está disponible en service/repository cuando se recibe vía DI

## 7. Repository genérico (repositories/base.py)

- [x] 7.1 (RED) Escribir test de `get()`: repository filtrado por tenant A encuentra registros de A y no de B
- [x] 7.2 (GREEN) Implementar `BaseRepository[T]` con `_stmt()` que filtra por `tenant_id` y excluye soft-deleteados. Métodos: `get`, `get_multi`, `create`, `update`, `soft_delete`, `exists`
- [x] 7.3 (RED) Escribir test de `create()` que asigna `tenant_id` automáticamente
- [x] 7.4 (GREEN) Implementar `create()` que setea `tenant_id` del contexto
- [x] 7.5 (RED) Escribir test de `get_multi()` con paginación (skip/limit)
- [x] 7.6 (TRIANGULATE) Escribir test de `exists()` dentro y fuera del tenant
- [x] 7.7 (TRIANGULATE) Escribir test de `update()` merge parcial
- [x] 7.8 (TRIANGULATE) Escribir test de `soft_delete()` que además verifica que `update()` sobre soft-deleteado lanza excepción

## 8. Soft delete transversal

- [x] 8.1 (RED) Escribir test que cree registro, soft_delete, verifique get/get_multi ya no lo devuelven
- [x] 8.2 (GREEN) Implementar soft delete en `BaseRepository`: `soft_delete()` setea `deleted_at`, `_stmt()` filtra `deleted_at.is_(None)`
- [x] 8.3 (RED) Escribir test de `get_with_deleted()` que devuelve registros soft-deleteados
- [x] 8.4 (GREEN) Implementar `get_with_deleted()` que salta el filtro de deleted_at (pero mantiene tenant scope)
- [x] 8.5 (TRIANGULATE) Verificar que `SoftDeletedException` se lanza al intentar actualizar un registro soft-deleteado

## 9. Migración Alembic 001

- [x] 9.1 Crear migración Alembic 001 `001_create_tenants_table` con `revises = None`
- [x] 9.2 La migración debe: crear extensión `uuid-ossp`, crear tabla `tenants` con todas las columnas, unique constraint en `codigo`, índice en `codigo`
- [x] 9.3 Ejecutar `alembic upgrade head` en DB de desarrollo → confirmar tabla creada
- [x] 9.4 Ejecutar `alembic downgrade -1` → confirmar tabla eliminada
- [x] 9.5 Ejecutar `alembic upgrade head` nuevamente → confirmar re-creación

## 10. Tests de integración multi-tenant

- [x] 10.1 (RED) Escribir test de aislamiento: crear varios registros en tenant A y B, verificar get_multi de A no contiene registros de B
- [x] 10.2 (GREEN) Asegurar que el flujo completo Tenant → Repository → get_multi respeta el aislamiento
- [x] 10.3 (TRIANGULATE) Probar aislamiento en get, get_multi, exists, update, soft_delete

## 11. Verificación final

- [x] 11.1 Ejecutar suite completa de tests (`pytest backend/tests/`) → verde
- [x] 11.2 Confirmar cobertura ≥80% líneas, ≥90% reglas de negocio en el código nuevo
- [x] 11.3 Confirmar que ningún archivo `.py` nuevo supera 500 LOC
- [x] 11.4 Confirmar que todos los schemas Pydantic nuevos usan `extra='forbid'`
- [x] 11.5 Confirmar snake_case en funciones y variables del código nuevo

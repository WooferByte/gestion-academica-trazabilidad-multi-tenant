## 1. Modelos y migración

- [x] 1.1 Crear modelo `VersionPadron` en `backend/app/models/version_padron.py` con campos: id, tenant_id, materia_id, cohorte_id, cargado_por, cargado_at, activa. Heredar de Base + BaseModelMixin.
- [x] 1.2 Crear modelo `EntradaPadron` en `backend/app/models/entrada_padron.py` con campos: id, version_id, tenant_id, usuario_id (nullable), nombre, apellidos, email, comision, regional. Heredar de Base + BaseModelMixin.
- [x] 1.3 Agregar ambos modelos a `backend/app/models/__init__.py`.
- [x] 1.4 Agregar `openpyxl` a `pyproject.toml`.
- [x] 1.5 Generar migración Alembic 007 con `alembic revision --autogenerate -m "create_version_padron_tables"`. Revisar constraints (unique compuesto, índices por materia×cohorte, FK a materias/cohortes/usuarios).

## 2. Schemas Pydantic

- [x] 2.1 Crear `backend/app/schemas/padron.py` con: `VersionPadronResponse`, `EntradaPadronResponse`, `ImportPreviewItem`, `ImportPreviewResponse`, `ImportConfirmRequest`, `PadronVaciarResponse`. `extra='forbid'` en todos.

## 3. Repositories

- [x] 3.1 Crear `backend/app/repositories/padron_repository.py` con métodos:
  - `get_activa(materia_id, cohorte_id)` → versión activa o None
  - `crear_version(...)` → inserta VersionPadron
  - `desactivar_version(version_id)` → set activa=False
  - `agregar_entradas(version_id, entradas)` → bulk insert EntradaPadron
  - `get_entradas(version_id)` → lista de entradas
  - `vaciar_materia(materia_id)` → soft delete entradas + desactivar versión
  - Scope de tenant obligatorio en todos los queries.

## 4. Servicios

- [x] 4.1 Crear `backend/app/services/padron_service.py` con:
  - `preview_import(tenant_id, materia_id, cohorte_id, archivo)` → parsea xlsx/csv, retorna preview items
  - `confirm_import(tenant_id, materia_id, cohorte_id, usuario_id, items)` → crea versión + entradas, desactiva anterior
  - `vaciar_materia(tenant_id, materia_id, usuario_id)` → soft delete + audit
  - Validar formato de archivo (xlsx/csv), columnas requeridas.
  - Auditar con `PADRON_CARGAR`.

## 5. Cliente Moodle WS

- [x] 5.1 Crear `backend/app/integrations/moodle_ws.py` con clase `MoodleWSClient`:
  - `__init__(tenant_config)` → recibe URL + token
  - `sync_usuarios(materia_id)` → retorna lista mock de alumnos
  - `sync_actividades(materia_id)` → retorna lista mock de actividades
  - Errores elevan `MoodleWSException` que mapea a 502.

## 6. Router y permisos

- [x] 6.1 Crear `backend/app/api/v1/routers/padron.py` con endpoints:
  - `POST /api/v1/padron/preview` → subir archivo, retorna preview
  - `POST /api/v1/padron/confirm` → confirmar import
  - `POST /api/v1/padron/sync-moodle` → sync on-demand via Moodle WS skeleton
  - `DELETE /api/v1/padron/{materia_id}` → vaciar datos de materia
- [x] 6.2 Registrar router en `backend/app/main.py`.
- [x] 6.3 Agregar permiso `padron:cargar` y `padron:vaciar` en la matriz RBAC (si existe seed data).

## 7. Tests

- [x] 7.1 Test: crear versión → activa, crear segunda → primera se desactiva.
- [x] 7.2 Test: import csv con 3 filas → preview retorna 3 items sin persistir.
- [x] 7.3 Test: confirm import → versión activa + entradas en DB.
- [x] 7.4 Test: entrada con email inexistente → usuario_id = NULL.
- [x] 7.5 Test: vaciar materia → soft delete entradas + versión desactivada + audit.
- [x] 7.6 Test: aislamiento tenant (tenant A no ve datos de tenant B).
- [x] 7.7 Test: Moodle WS skeleton retorna datos mock.
- [x] 7.8 Test: error de Moodle WS mapea a 502.
- [x] 7.9 Test: archivo con formato inválido → 400.

## 8. Validaciones finales

- [x] 8.1 Verificar que todos los archivos tienen ≤500 LOC.
- [x] 8.2 Ejecutar suite de tests existente (safety net) + nuevos tests.
- [x] 8.3 Verificar cobertura ≥80% líneas.

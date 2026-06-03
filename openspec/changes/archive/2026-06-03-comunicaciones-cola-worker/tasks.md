## 1. Modelo y migración

- [x] 1.1 Crear modelo `Comunicacion` en `backend/app/models/comunicacion.py` con campos: id, tenant_id, enviado_por, materia_id, destinatario (cifrado), asunto, cuerpo, estado (enum), lote_id, aprobacion_requerida, enviado_at, creado_at, updated_at, deleted_at
- [x] 1.2 Agregar columna `aprobacion_comunicaciones` (bool, default false) a modelo `Tenant`
- [x] 1.3 Registrar `Comunicacion` en `models/__init__.py`
- [x] 1.4 Crear migración Alembic 009: tabla `comunicaciones` + columna en `tenants` + índices `(estado, tenant_id, deleted_at)` y `(lote_id, tenant_id)`

## 2. Schemas Pydantic

- [x] 2.1 Crear `backend/app/schemas/comunicacion.py` con request/response DTOs: `ComunicacionCreate`, `ComunicacionBulkCreate`, `ComunicacionPreviewRequest`, `ComunicacionPreviewResponse`, `ComunicacionResponse`, `ComunicacionListResponse`, `AprobarLoteRequest`, `CancelarRequest`

## 3. Repositorio

- [x] 3.1 Crear `backend/app/repositories/comunicacion_repository.py` con: `get_pendientes(batch_size)`, `get_by_lote`, `get_by_materia`, `create`, `update_estado`, `count_by_lote`
- [x] 3.2 `ComunicacionRepository` extiende `BaseRepository[Comunicacion]` con tenant-scoped queries

## 4. Servicios

- [x] 4.1 Crear `backend/app/services/comunicacion_service.py` con `ComunicacionService`: métodos `preview`, `encolar`, `encolar_lote`, `aprobar_lote`, `rechazar_lote`, `cancelar`, `listar_por_lote`, `listar_por_materia`
- [x] 4.2 `preview()`: recibe asunto/cuerpo con variables `{{...}}`, sustituye y retorna sin persistir
- [x] 4.3 `encolar()`: cifra destinatario con `security.encrypt()`, crea registro Pendiente, asigna lote_id, audita
- [x] 4.4 `aprobar_lote()`: transiciona lote completo a Pendiente (si estaba esperando aprobación), audita
- [x] 4.5 `rechazar_lote()`: transiciona lote completo a Cancelado, audita

## 5. Worker de despacho

- [x] 5.1 Reescribir `backend/app/workers/main.py`: loop asyncio que cada N segundos consulta comunicaciones Pendientes (sin aprobación requerida o aprobadas), transiciona a Enviando, ejecuta envío (mock SMTP en MVP), y actualiza a Enviado/Error
- [x] 5.2 Implementar `_render_template()`: sustituye `{{alumno.nombre}}`, `{{materia.nombre}}` en asunto y cuerpo
- [x] 5.3 Manejo de señales (SIGTERM/SIGINT) para shutdown graceful
- [x] 5.4 Batch configurable vía env var `WORKER_BATCH_SIZE` (default 50), sleep `WORKER_POLL_INTERVAL` (default 30s)

## 6. Router API

- [x] 6.1 Crear `backend/app/api/v1/routers/comunicaciones.py` con endpoints:
  - `POST /api/v1/comunicaciones/preview` → preview (require `comunicacion:enviar`)
  - `POST /api/v1/comunicaciones/` → encolar individual (require `comunicacion:enviar`)
  - `POST /api/v1/comunicaciones/lote` → encolar múltiple (require `comunicacion:enviar`)
  - `POST /api/v1/comunicaciones/aprobar-lote` → aprobar/rechazar (require `comunicacion:aprobar`)
  - `POST /api/v1/comunicaciones/{id}/cancelar` → cancelar (require `comunicacion:enviar`)
  - `GET /api/v1/comunicaciones?lote_id=X|materia_id=Y` → listar (require `comunicacion:enviar`)
- [x] 6.2 Registrar router en `api/v1/routers/__init__.py` y en `main.py`

## 7. Permisos RBAC

- [x] 7.1 Agregar `comunicacion:enviar` y `comunicacion:aprobar` al seed de permisos

## 8. Tests

- [x] 8.1 Test: máquina de estados (Pendiente → Enviando → Enviado/Error/Cancelado)
- [x] 8.2 Test: preview con y sin variables de sustitución
- [x] 8.3 Test: encolar comunicación cifra destinatario
- [x] 8.4 Test: aprobar/rechazar lote
- [x] 8.5 Test: cancelar comunicación Pendiente vs Enviando
- [x] 8.6 Test: worker procesa Pendiente → Enviado
- [x] 8.7 Test: tenant sin aprobación procesa inmediato vs tenant con aprobación queda Pendiente
- [x] 8.8 Test: RBAC — 403 sin el permiso correspondiente
- [x] 8.9 Test: soft delete no rompe queries existentes

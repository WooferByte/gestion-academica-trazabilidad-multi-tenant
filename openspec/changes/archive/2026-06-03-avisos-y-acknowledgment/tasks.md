## 1. Modelos y migración

- [x] 1.1 Crear modelo `Aviso` en `backend/app/models/aviso.py` con campos: id, tenant_id, alcance (enum: Global/PorMateria/PorCohorte/PorRol), materia_id (FK nullable), cohorte_id (FK nullable), rol_destino (nullable), severidad (enum: Info/Advertencia/Crítico), titulo, cuerpo, inicio_vigencia, fin_vigencia, orden, activo, requiere_ack + mixin soft delete + timestamps
- [x] 1.2 Crear modelo `AcknowledgmentAviso` en `backend/app/models/acknowledgment_aviso.py` con campos: id, aviso_id (FK), usuario_id (FK), confirmado_at — append-only (sin soft delete)
- [x] 1.3 Registrar ambos modelos en `models/__init__.py`
- [x] 1.4 Crear migración Alembic 012: tablas `aviso` y `acknowledgment_aviso` con FK a materia/cohorte/usuario, índices compuestos `(tenant_id, activo, inicio_vigencia, fin_vigencia)` y `(aviso_id, usuario_id)` unique

## 2. Schemas Pydantic

- [x] 2.1 Crear `backend/app/schemas/aviso.py` con DTOs: `AvisoCreate`, `AvisoUpdate`, `AvisoResponse` (incluye `total_acks`, `user_acked`), `AvisoListResponse`, `AckResponse` — todos con `extra='forbid'`

## 3. Repositorio

- [x] 3.1 Crear `backend/app/repositories/aviso_repository.py` con `AvisoRepository(BaseRepository[Aviso])`: métodos `list_visibles(usuario, tenant_id)` con filtro por alcance/rol/cohorte/materia y ventana de vigencia, `get_by_id`, `create`, `update`, `soft_delete`, `count_acks(aviso_id)`, `user_has_acked(aviso_id, usuario_id)`, `create_ack`
- [x] 3.2 Implementar `list_visibles()` con query condicional por alcance (CASE/OR según design decision 1)

## 4. Servicio

- [x] 4.1 Crear `backend/app/services/aviso_service.py` con `AvisoService`: métodos `crear`, `actualizar`, `desactivar`, `listar_avisos_para_usuario`, `obtener_aviso`, `confirmar_lectura`

## 5. Router API

- [x] 5.1 Crear `backend/app/api/v1/routers/avisos.py` con endpoints:
  - `POST /api/v1/avisos` → crear (require `avisos:publicar`)
  - `GET /api/v1/avisos` → listar visibles para el usuario autenticado (sin permiso especial)
  - `GET /api/v1/avisos/{id}` → detalle de aviso (sin permiso especial, 404 si no visible)
  - `PATCH /api/v1/avisos/{id}` → actualizar/desactivar (require `avisos:publicar`)
  - `DELETE /api/v1/avisos/{id}` → soft delete (require `avisos:publicar`)
  - `POST /api/v1/avisos/{id}/ack` → confirmar lectura (sin permiso especial, 409 si ya confirmó)
- [x] 5.2 Registrar router en `api/v1/routers/__init__.py`

## 6. Permisos RBAC

- [x] 6.1 Agregar permiso `avisos:publicar` al seed de permisos, asignado a COORDINADOR y ADMIN

## 7. Tests

- [x] 7.1 Test: creación de aviso global, por materia, por cohorte, por rol
- [x] 7.2 Test: 403 al crear aviso sin permiso `avisos:publicar`
- [x] 7.3 Test: 422 con campos extra en schema (extra='forbid')
- [x] 7.4 Test: visualización solo muestra avisos del alcance correspondiente al usuario
- [x] 7.5 Test: aviso fuera de vigencia no se muestra
- [x] 7.6 Test: orden por `orden` ASC, luego `inicio_vigencia` DESC
- [x] 7.7 Test: confirmación de lectura exitosa (201 + registro en DB)
- [x] 7.8 Test: confirmación duplicada retorna 409
- [x] 7.9 Test: `total_acks` refleja cantidad de confirmaciones
- [x] 7.10 Test: `user_acked` es true si el usuario confirmó
- [x] 7.11 Test: soft delete oculta el aviso
- [x] 7.12 Test: aislamiento multi-tenant (usuario de tenant A no ve avisos de tenant B)

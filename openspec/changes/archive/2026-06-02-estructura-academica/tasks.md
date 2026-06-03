## 1. Migración Alembic 005

- [x] 1.1 Crear migración 005 con tabla `carreras` (id UUID, tenant_id FK, codigo, nombre, estado, created_at, updated_at, deleted_at + unique(tenant_id, codigo))
- [x] 1.2 Agregar tabla `cohortes` (id UUID, tenant_id FK, carrera_id FK, nombre, anio, vig_desde, vig_hasta, estado, created_at, updated_at, deleted_at + unique(tenant_id, carrera_id, nombre))
- [x] 1.3 Agregar tabla `materias` (id UUID, tenant_id FK, codigo, nombre, estado, created_at, updated_at, deleted_at + unique(tenant_id, codigo))
- [x] 1.4 Ejecutar migración y verificar tablas creadas

## 2. Modelo Carrera

- [x] 2.1 Crear `backend/app/models/carrera.py` con clase `Carrera(Base, BaseModelMixin)` y campos codigo, nombre, estado
- [x] 2.2 Crear `backend/app/schemas/carrera.py` con `CarreraCreate`, `CarreraUpdate`, `CarreraResponse`, `CarreraList` (extra='forbid', from_attributes en response)
- [x] 2.3 Crear `backend/app/repositories/carrera.py` con `CarreraRepository(BaseRepository[Carrera])` y método `get_by_codigo`
- [x] 2.4 Crear `backend/app/services/carrera_service.py` con `CarreraService` (CRUD + validación unicidad + regla carrera inactiva sin cohortes abiertas)
- [x] 2.5 Crear `backend/app/api/v1/routers/carreras.py` con 5 endpoints protegidos con `require_permission("estructura:gestionar")`

## 3. Modelo Cohorte

- [x] 3.1 Crear `backend/app/models/cohorte.py` con clase `Cohorte(Base, BaseModelMixin)` y campos carrera_id FK, nombre, anio, vig_desde, vig_hasta, estado
- [x] 3.2 Crear `backend/app/schemas/cohorte.py` con `CohorteCreate`, `CohorteUpdate`, `CohorteResponse`, `CohorteList`
- [x] 3.3 Crear `backend/app/repositories/cohorte.py` con `CohorteRepository(BaseRepository[Cohorte])` y método `get_by_nombre_and_carrera`
- [x] 3.4 Crear `backend/app/services/cohorte_service.py` con `CohorteService` (CRUD + validación unicidad compuesta + verificación carrera activa)
- [x] 3.5 Crear `backend/app/api/v1/routers/cohortes.py` con 5 endpoints protegidos

## 4. Modelo Materia

- [x] 4.1 Crear `backend/app/models/materia.py` con clase `Materia(Base, BaseModelMixin)` y campos codigo, nombre, estado
- [x] 4.2 Crear `backend/app/schemas/materia.py` con `MateriaCreate`, `MateriaUpdate`, `MateriaResponse`, `MateriaList`
- [x] 4.3 Crear `backend/app/repositories/materia.py` con `MateriaRepository(BaseRepository[Materia])` y método `get_by_codigo`
- [x] 4.4 Crear `backend/app/services/materia_service.py` con `MateriaService` (CRUD + validación unicidad)
- [x] 4.5 Crear `backend/app/api/v1/routers/materias.py` con 5 endpoints protegidos

## 5. Registro de routers y exports

- [x] 5.1 Importar y registrar routers `carreras`, `cohortes`, `materias` en `backend/app/api/v1/routers/__init__.py`
- [x] 5.2 Verificar que `backend/app/models/__init__.py` exporta los 3 nuevos modelos
- [x] 5.3 Verificar que `backend/app/repositories/__init__.py` exporta los 3 nuevos repositorios
- [x] 5.4 Verificar que `backend/app/schemas/__init__.py` exporta los schemas

## 6. Tests

- [x] 6.1 Crear `backend/tests/test_carreras.py` con tests de: crear OK, código duplicado (mismo tenant), código duplicado (otro tenant), listar, obtener, actualizar, soft delete, aislamiento multi-tenant, inactivar con cohortes abiertas
- [x] 6.2 Crear `backend/tests/test_cohortes.py` con tests de: crear OK, nombre duplicado (misma carrera), nombre duplicado (distinta carrera), carrera inactiva, carrera inexistente, listar, obtener, soft delete, aislamiento multi-tenant
- [x] 6.3 Crear `backend/tests/test_materias.py` con tests de: crear OK, código duplicado (mismo tenant), código duplicado (otro tenant), listar, actualizar, soft delete, aislamiento multi-tenant
- [x] 6.4 Ejecutar suite completa y verificar 100% verde

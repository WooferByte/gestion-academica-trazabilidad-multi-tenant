## Why

Activia-trace necesita las entidades académicas raíz (Carrera, Cohorte, Materia) como base estructural de todos los módulos posteriores: equipos docentes, padrones, calificaciones, comunicaciones, liquidaciones. Sin estas tablas ningún flujo académico puede operar. C-06 es el primer change que materializa el modelo de datos del dominio académico, siguiendo ADR-006 (Materia como catálogo único, Dictado en change posterior).

## What Changes

- **Modelo Carrera**: ABM completo con código único por tenant, estado activa/inactiva
- **Modelo Cohorte**: ABM completo con unicidad `(tenant_id, carrera_id, nombre)`, vigencia, anio
- **Modelo Materia**: ABM completo con código único por tenant, estado activa/inactiva (catálogo único — ADR-006)
- **Reglas de negocio**: carrera inactiva no admite cohortes abiertas; unicidad compuesta en cada entidad
- **Permisos**: endpoints protegidos con `require_permission("estructura:gestionar")` (ya existe en seed de C-04)
- **Migración 005**: tablas `carreras`, `cohortes`, `materias`
- **Tests**: CRUD por entidad, unicidad, aislamiento multi-tenant, regla carrera inactiva

## Capabilities

### New Capabilities
- `carreras`: Administración de carreras (alta, edición, activar/inactivar) con código único por tenant
- `cohortes`: Administración de cohortes vinculadas a carrera con vigencia y unicidad compuesta
- `materias`: Administración del catálogo único de materias con código único por tenant

### Modified Capabilities
*(ninguna — este change introduce las primeras entidades académicas)*

## Impact

- **Modelos**: nuevas clases `Carrera`, `Cohorte`, `Materia` en `backend/app/models/`
- **Schemas**: nuevos Pydantic schemas request/response por entidad
- **Servicios**: `CarreraService`, `CohorteService`, `MateriaService` con validación de unicidad y regla carrera inactiva
- **Repositorios**: `CarreraRepository`, `CohorteRepository`, `MateriaRepository` con scope tenant
- **Routers**: `/api/v1/admin/carreras`, `/api/v1/admin/cohortes`, `/api/v1/admin/materias`
- **Migración**: nueva versión 005 en Alembic
- **Tests**: archivos `test_carreras.py`, `test_cohortes.py`, `test_materias.py`

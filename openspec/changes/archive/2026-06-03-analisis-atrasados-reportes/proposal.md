## Why

Con C-10 completado (Calificaciones y Umbral), los datos de notas y umbrales ya existen en el sistema pero no hay capacidad de análisis sobre ellos. El PROFESOR no puede detectar alumnos en riesgo, generar rankings, ni obtener reportes consolidados. Este change transforma datos crudos en información accionable: es el paso previo indispensable para que el PROFESOR pueda comunicarse con alumnos atrasados (C-12).

## What Changes

- **Nuevo módulo `/api/analisis/*`** con endpoints de solo lectura para cómputo de alumnos atrasados, ranking, reportes rápidos, notas finales agrupadas, exportación de TPs sin corregir y monitores de seguimiento.
- **Lógica de cálculo en Services** (no en SQL ni en Routers): definición de "atrasado" según RN-06, ranking según RN-09, detección de TPs sin corregir según RN-07/RN-08.
- **Permiso `atrasados:ver`** como guard de todos los endpoints del módulo.
- **Export CSV** de TPs sin corregir y del monitor general.
- **No se crean nuevos modelos ni migraciones** — todo opera sobre `Calificacion`, `UmbralMateria`, `EntradaPadron` y `VersionPadron` existentes.

## Capabilities

### New Capabilities
- `analisis-atrasados`: Cómputo de alumnos atrasados por materia+cohorte (actividades faltantes o nota < umbral, RN-06)
- `analisis-ranking`: Ranking de alumnos por cantidad de actividades aprobadas (RN-09, mínimo 1 actividad aprobada)
- `analisis-reportes-rapidos`: Métricas consolidadas por materia (total alumnos, aprobados, atrasados, actividades)
- `analisis-notas-finales`: Nota final agrupada por alumno ponderando actividades configuradas
- `analisis-exportar-tps-sin-corregir`: Exportación de entregas detectadas como pendientes de corrección (RN-07/08)
- `analisis-monitor-general`: Vista transversal de todos los alumnos del tenant con filtros (coordinación/admin)
- `analisis-monitor-seguimiento`: Vista filtrable por tutor/profesor y por coordinación/admin con rango de fechas

### Modified Capabilities
Ninguna. No hay cambios de requirements en capacidades existentes.

## Impact

- **Nuevos archivos**:
  - `backend/app/routers/analisis_router.py` — endpoints `/api/analisis/*`
  - `backend/app/services/analisis_service.py` — lógica de cálculo
  - `backend/app/schemas/analisis.py` — DTOs request/response
  - `backend/app/repositories/analisis_repository.py` — queries de agregación (solo lectura)
  - `backend/tests/test_analisis/` — tests del módulo
- **Archivos modificados**:
  - `backend/app/core/audit_codes.py` — nuevo código `ANALISIS_CONSULTAR`
  - `backend/app/main.py` — registro del router
- **Sin migraciones**: 0 nuevos modelos, 0 migraciones
- **Dependencias**: C-10 (Calificaciones + Umbral) — completado

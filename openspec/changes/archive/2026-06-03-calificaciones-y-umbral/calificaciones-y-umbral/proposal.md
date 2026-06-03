## Why

El sistema necesita procesar calificaciones reales del LMS para detectar alumnos atrasados. Sin este cambio, no hay datos contra los cuales computar umbrales, rankings ni comunicación. C-09 dejó el padrón versionado; ahora hay que poblarlo con notas.

## What Changes

- Nuevo modelo `Calificacion` (nota numérica y/o textual, `aprobado` derivado, origen Importado/Manual)
- Nuevo modelo `UmbralMateria` (umbral_pct + valores_aprobatorios por asignación)
- Importación de calificaciones desde archivo LMS (F1.1): detección de columnas numéricas (RN-01) y textuales (RN-02), vista previa con actividades detectadas, selección de actividades a incluir
- Importación de reporte de finalización (F1.2): cruce contra calificaciones existentes para detectar entregas sin corregir (RN-07, RN-08)
- Configuración de umbral por materia×cohorte (F2.1, RN-03, default 60%)
- Auditoría con código `CALIFICACIONES_IMPORTAR`
- Migración Alembic **008**
- Test de derivación de `aprobado`, import + preview, selección de actividades, umbral

## Capabilities

### New Capabilities
- `calificaciones-import`: Importar calificaciones desde archivo LMS con preview y selección de actividades
- `umbral-materia-config`: Configurar umbral de aprobación por materia×asignación
- `reporte-finalizacion`: Importar reporte de finalización y detectar entregas sin corregir

### Modified Capabilities
- *(none — no existing capabilities require spec-level changes)*

## Impact

- **Backend**: Nuevos models (`Calificacion`, `UmbralMateria`), schemas, repositories, service (`calificaciones_service.py`), y router (`calificaciones_router.py`)
- **DB**: Migración 008 con tablas `calificacion` y `umbral_materia`
- **Dependencias**: `openpyxl` ya disponible desde C-09
- **Tests**: Nuevo test suite para derivación de aprobado, import/preview, umbral

## Why

C-09 es necesario para que el sistema pueda importar el padrón de alumnos desde Moodle (vía Web Services) o mediante carga manual de archivos `.xlsx`/`.csv`. El padrón versionado es la base sobre la cual se importarán calificaciones (C-10) y se ejecutará el análisis de atrasados (C-11). Sin padrón no hay trazabilidad de alumnos por materia.

## What Changes

- **Modelos `VersionPadron` + `EntradaPadron`** con versionado: una versión activa por materia×cohorte; activar nueva desactiva la anterior automáticamente.
- **Import de padrón manual**: endpoints para subir archivo `.xlsx` (openpyxl) / `.csv`, generar vista previa y confirmar importación (F1.3, F1.4).
- **Cliente Moodle Web Services skeleton** en `integrations/moodle_ws.py`: mock que simula sync de usuarios/actividades; errores mapean a `502` con reintento. La integración real se afina en changes posteriores.
- **Vaciar datos de materia** (F1.5, RN-04): elimina entradas de padrón de la materia (soft delete).
- **Audit `PADRON_CARGAR`**: registra cada importación y cada vaciado.
- **Migración Alembic 007**: tablas `version_padron`, `entrada_padron`.
- **Dependencia nueva**: `openpyxl` para lectura de archivos `.xlsx`.

## Capabilities

### New Capabilities
- `padron-ingesta`: importación de padrón de alumnos con versionado, vista previa, carga manual xlsx/csv, y vaciado de datos por materia. Incluye aislamiento tenant y soft delete.
- `moodle-integration`: cliente Moodle Web Services skeleton con sync on-demand, mapeo de errores a 502, y estructura para sync nocturna futura.

### Modified Capabilities
<!-- No existing capabilities are modified by this change -->

## Impact

- **Backend**: nuevos modelos (`VersionPadron`, `EntradaPadron`), repositorios, servicios, schemas, router `/api/v1/padron/`.
- **Integraciones**: nuevo archivo `integrations/moodle_ws.py`.
- **Base de datos**: migración Alembic 007 con tablas `version_padron` y `entrada_padron`.
- **Dependencias**: agregar `openpyxl` a `requirements.txt` / `pyproject.toml`.
- **Permisos**: nuevo permiso `padron:cargar` (y `padron:vaciar`) en la matriz RBAC.
- **Auditoría**: código `PADRON_CARGAR` ya existe en `audit_codes.py`; se utiliza para import y vaciado.

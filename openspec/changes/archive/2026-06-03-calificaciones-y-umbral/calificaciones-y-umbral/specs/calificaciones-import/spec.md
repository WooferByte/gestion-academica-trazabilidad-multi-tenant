## ADDED Requirements

### Requirement: Preview calificaciones desde archivo LMS
The system SHALL accept xlsx and csv files exported from the LMS, parse them, detect activity columns, and return a preview before persisting.

#### Scenario: Preview con columnas numéricas detectadas
- **WHEN** user uploads an xlsx with columns including headers ending in `(Real)`
- **THEN** the system returns a preview listing detected activities, marking numeric columns with `tipo: numerica` and others as `tipo: textual`

#### Scenario: Preview con columnas textuales
- **WHEN** user uploads a file without headers ending in `(Real)`
- **THEN** all non-identifying columns are marked as `tipo: textual`

#### Scenario: Preview devuelve actividades detectadas y filas
- **WHEN** user calls preview endpoint
- **THEN** response includes `actividades` (list of column names, tipo, sample values) and `total` row count

### Requirement: Seleccionar actividades a importar
The system SHALL allow the user to select which detected activities to include in the import before confirming.

#### Scenario: Selección parcial de actividades
- **WHEN** user confirms import with a subset of detected activities
- **THEN** only selected activities are persisted as Calificacion records

#### Scenario: Confirmar import persiste calificaciones
- **WHEN** user confirms import for materia X
- **THEN** each (alumno × actividad) becomes a Calificacion row linked to the corresponding EntradaPadron

#### Scenario: Import audita con CALIFICACIONES_IMPORTAR
- **WHEN** confirm_import completes successfully
- **THEN** an audit log entry with code `CALIFICACIONES_IMPORTAR` is created with detalle including materia_id, cohorte_id, and actividades count

### Requirement: Detectar columnas numéricas (RN-01)
The system SHALL interpret columns whose header ends in `(Real)` as numeric grade columns.

#### Scenario: Columna con sufijo (Real) es numérica
- **WHEN** a column header is `Parcial 1 (Real)`
- **THEN** the column is classified as `tipo: numerica` and values are parsed as decimals

#### Scenario: Columna sin sufijo es textual
- **WHEN** a column header is `Estado TP`
- **THEN** the column is classified as `tipo: textual`

### Requirement: Mapeo de escala textual a aprobado (RN-02)
The system SHALL map textual values "Satisfactorio" and "Supera lo esperado" as approved for textual-grade activities.

#### Scenario: Textual aprobatorio
- **WHEN** a textual-grade activity has value "Satisfactorio"
- **THEN** `aprobado` is computed as `true`

#### Scenario: Textual no aprobatorio
- **WHEN** a textual-grade activity has value "No satisfactorio"
- **THEN** `aprobado` is computed as `false`

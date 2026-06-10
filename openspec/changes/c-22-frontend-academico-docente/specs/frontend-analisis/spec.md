## ADDED Requirements

### Requirement: Atrasados page displays table of delayed students
The system SHALL display students with pending activities or below-threshold grades in a sortable table.

#### Scenario: Load atrasados from API
- **WHEN** user navigates to `/academico/:materiaId/:cohorteId/atrasados`
- **THEN** the system calls `GET /api/v1/analisis/atrasados?materia_id=X&cohorte_id=Y`
- **AND** displays a table with columns: nombre, actividades totales, actividades aprobadas, badge "Faltantes", badge "Desaprobadas"

#### Scenario: Table row selection for bulk action
- **WHEN** user checks checkboxes on atrasados rows
- **THEN** the "Comunicar" button activates showing selected count
- **WHEN** user clicks "Comunicar"
- **THEN** the system navigates to `/academico/:materiaId/:cohorteId/comunicar` with selected student IDs in navigation state

#### Scenario: Empty atrasados state
- **WHEN** no students are atrasados
- **THEN** the system shows "No hay alumnos atrasados" with a check icon

### Requirement: Ranking page displays ordered student list
The system SHALL display students sorted descending by approved activities.

#### Scenario: Load ranking from API
- **WHEN** user navigates to `/academico/:materiaId/:cohorteId/ranking`
- **THEN** the system calls `GET /api/v1/analisis/ranking?materia_id=X&cohorte_id=Y`
- **AND** displays a table sorted by actividades_aprobadas descending with rank numbers

### Requirement: Notas finales page shows grades by activity
The system SHALL display final grades for selected activities in a matrix view.

#### Scenario: Activity selector
- **WHEN** user navigates to `/academico/:materiaId/:cohorteId/notas`
- **THEN** the system displays checkboxes for each actividad
- **WHEN** user selects activities and clicks "Ver notas"
- **THEN** the system calls `GET /api/v1/analisis/notas-finales?materia_id=X&cohorte_id=Y&actividades=id1,id2`
- **AND** displays a student × activity matrix with grade values

### Requirement: TPs sin corregir page
The system SHALL display TP (trabajos prácticos) that are pending correction, filtered to textual activities only (RN-07/08).

#### Scenario: Load tps-sin-corregir
- **WHEN** user navigates to `/academico/:materiaId/:cohorteId/tps-sin-corregir`
- **THEN** the system calls `GET /api/v1/analisis/tps-sin-corregir?materia_id=X&cohorte_id=Y`
- **AND** displays a table of textual activities without correction

#### Scenario: Export TPs CSV
- **WHEN** user clicks "Exportar CSV"
- **THEN** the system generates a CSV file from the table data and triggers download

### Requirement: Monitor de seguimiento page
The system SHALL provide a monitoring view for tutors/profesores with filters.

#### Scenario: Load monitor seguimiento
- **WHEN** user with role TUTOR or PROFESOR navigates to monitor page
- **THEN** the system calls `GET /api/v1/analisis/monitor-seguimiento?materia_id=X&comision_id=Y&q=search&fecha_desde=...&fecha_hasta=...`
- **AND** displays a searchable, filterable table

#### Scenario: Load monitor general
- **WHEN** user with role COORDINADOR navigates to monitor page
- **THEN** the system calls `GET /api/v1/analisis/monitor-general`
- **AND** displays cross-comisión aggregated data

#### Scenario: Export monitor CSV
- **WHEN** user clicks "Exportar CSV" in any monitor view
- **THEN** the system generates and downloads a CSV file with the current filtered data

### Requirement: Umbral configuration page
The system SHALL allow configuring the approval threshold for a comisión (RN-03: default 60%).

#### Scenario: Load current umbral
- **WHEN** user navigates to `/academico/:materiaId/:cohorteId/umbral`
- **THEN** the system calls `GET /api/v1/umbrales/{materia_id}/{cohorte_id}`
- **AND** displays a slider pre-filled with current value (default 60%)

#### Scenario: Update umbral
- **WHEN** user drags slider to new value and clicks "Guardar"
- **THEN** the system calls `PUT /api/v1/umbrales/{materia_id}/{cohorte_id}` with the new value
- **AND** displays success toast

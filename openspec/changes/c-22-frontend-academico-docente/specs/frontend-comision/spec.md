## ADDED Requirements

### Requirement: Comision dashboard displays materia+cohorte selector
The system SHALL display a cascading selector for materia and cohorte based on the docente's teaching assignments.

#### Scenario: Docente with multiple comisiones sees all assignments
- **WHEN** a docente navigates to `/academico`
- **THEN** the system fetches assigned comisiones via `GET /api/v1/docente/comisiones`
- **AND** displays a dropdown list of materias grouped by cohorte

#### Scenario: Single comision auto-selects
- **WHEN** a docente has exactly one comisión assigned
- **THEN** the system auto-navigates to `/academico/:materiaId/:cohorteId`

### Requirement: Comision dashboard shows KPI cards
The system SHALL display KPI summary cards for the selected comisión: total alumnos, total actividades, aprobados, atrasados, promedio general.

#### Scenario: KPIs load on comision selection
- **WHEN** user selects a materia+cohorte combination
- **THEN** the system calls `GET /api/v1/analisis/reportes-rapidos?materia_id=X&cohorte_id=Y`
- **AND** displays KPI cards with numeric values and trend indicators

#### Scenario: KPI cards show loading skeleton while fetching
- **WHEN** KPIs are being fetched
- **THEN** each KPI card shows a Skeleton component instead of values

#### Scenario: KPI display uses fallback when data shows zero
- **WHEN** a KPI value is 0 or null
- **THEN** the card displays "—" as fallback value

### Requirement: Comision dashboard shows action menu
The system SHALL display a menu of available actions based on user permissions: Importar calificaciones, Configurar umbral, Ver atrasados, Ranking, Notas finales, Comunicar, Monitor.

#### Scenario: Action buttons render based on permissions
- **WHEN** user has `calificaciones:importar` permission
- **THEN** "Importar calificaciones" and "Configurar umbral" buttons are visible
- **WHEN** user has `atrasados:ver` permission
- **THEN** "Ver atrasados", "Ranking", "Notas finales" buttons are visible
- **WHEN** user has `comunicacion:enviar` permission
- **THEN** "Comunicar" button is visible

#### Scenario: Action button click navigates to sub-page
- **WHEN** user clicks an action button
- **THEN** the system navigates to `/academico/:materiaId/:cohorteId/{action-path}`

### Requirement: Comision page shows breadcrumb navigation
The system SHALL display a breadcrumb showing the navigation path: Académico > Materia > Cohorte.

#### Scenario: Breadcrumb reflects current route
- **WHEN** user is on `/academico/:materiaId/:cohorteId/importar`
- **THEN** breadcrumb shows "Académico / [Materia nombre] / [Cohorte nombre] / Importar"

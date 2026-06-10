## ADDED Requirements

### Requirement: Import wizard follows 3-step flow
The system SHALL provide a multi-step wizard for importing calificaciones: Upload → Preview → Confirm.

#### Scenario: Upload step accepts CSV/XLSX file
- **WHEN** user selects a file input and picks a CSV or XLSX file
- **THEN** the system sends a `POST /api/v1/calificaciones/importar/preview` with `Content-Type: multipart/form-data`
- **AND** the upload button shows a loading spinner during upload

#### Scenario: Preview step displays detected activities
- **WHEN** the preview API returns detected activities
- **THEN** the system displays each actividad with name, type, and a checkbox (default: checked)
- **AND** shows a table preview of parsed rows

#### Scenario: Confirm step sends selected activities
- **WHEN** user clicks "Confirmar importación"
- **THEN** the system sends `POST /api/v1/calificaciones/importar/confirmar` with the `file_token` and selected `actividad_ids`
- **AND** displays a success toast with count of imported records

### Requirement: Import padrón flow
The system SHALL provide import flow for student roster (padrón) with preview and confirm.

#### Scenario: Upload padrón file
- **WHEN** user uploads a padrón file
- **THEN** the system calls `POST /api/v1/padron/importar/preview`
- **AND** displays preview of parsed students

#### Scenario: Confirm padrón import
- **WHEN** user confirms padrón import
- **THEN** the system calls `POST /api/v1/padron/importar/confirmar`
- **AND** displays success toast with imported student count

### Requirement: Import finalización report
The system SHALL allow importing a finalización report (final completion data).

#### Scenario: Upload finalización report
- **WHEN** user uploads a finalización report file
- **THEN** the system calls `POST /api/v1/calificaciones/importar/finalizacion`
- **AND** displays success toast with processed count

### Requirement: Vaciar datos de materia
The system SHALL allow emptying all data for a materia+cohorte combination.

#### Scenario: Vaciar with confirmation dialog
- **WHEN** user clicks "Vaciar datos de materia"
- **THEN** the system shows a confirmation Dialog with warning text
- **WHEN** user confirms
- **THEN** the system calls `POST /api/v1/padron/vaciar/{materia_id}/{cohorte_id}`
- **AND** displays success toast

### Requirement: Import tab navigation
The system SHALL display tabs to switch between import types: Calificaciones, Padrón, Finalización.

#### Scenario: Tab switching
- **WHEN** user clicks "Padrón" tab
- **THEN** the padrón import UI is displayed
- **WHEN** user clicks "Calificaciones" tab
- **THEN** the calificaciones import UI is displayed

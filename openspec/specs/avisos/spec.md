# avisos Specification

## Purpose
TBD - created by archiving change c-23a-frontend-equipos-docentes. Update Purpose after archive.
## Requirements
### Requirement: COORDINADOR/ADMIN can create avisos (F3.5)
The system SHALL provide a creation form for avisos with fields: alcance (Global/PorMateria/PorCohorte/PorRol), materia_id, cohorte_id, rol_destino, severidad (Info/Advertencia/Urgente), titulo, cuerpo, inicio_vigencia, fin_vigencia, orden, requiere_ack. Calls `POST /api/v1/avisos`.

#### Scenario: Create global aviso
- **WHEN** a COORDINADOR fills alcance="Global", severidad="Info", titulo="Bienvenidos", cuerpo="Inicio de cuatrimestre", inicio_vigencia=now, fin_vigencia=+30d, requiere_ack=true
- **AND** clicks "Publicar"
- **THEN** the system calls `POST /api/v1/avisos` with the form data
- **AND** redirects to the avisos list showing the new aviso

#### Scenario: Create aviso with conditional fields
- **WHEN** a COORDINADOR selects alcance="PorMateria"
- **THEN** the system shows a materia_id selector
- **AND** hides cohorte_id and rol_destino fields
- **WHEN** the user selects alcance="PorRol"
- **THEN** the system shows the rol_destino selector
- **AND** hides materia_id and cohorte_id fields

#### Scenario: Validation on create
- **WHEN** a COORDINADOR submits without titulo
- **THEN** the system shows inline error "El título es obligatorio"

### Requirement: COORDINADOR/ADMIN can list and filter avisos
The system SHALL display a table of all avisos with columns: titulo, alcance, severidad, inicio_vigencia, fin_vigencia, activo, total_acks. Filters by estado (activo/inactivo), alcance, and date range SHALL be available. Calls `GET /api/v1/avisos`.

#### Scenario: List avisos
- **WHEN** a COORDINADOR navigates to `/avisos`
- **THEN** the system calls `GET /api/v1/avisos`
- **AND** displays a table with all avisos showing titulo, alcance, severidad badge, vigencia badge, and total_acks

#### Scenario: Filter avisos by estado
- **WHEN** a COORDINADOR selects filter "Inactivos"
- **THEN** the list updates to show only avisos where `activo=false`

### Requirement: COORDINADOR/ADMIN can edit avisos
The system SHALL allow editing an existing aviso via a form pre-filled with current values. Calls `PATCH /api/v1/avisos/{id}`.

#### Scenario: Edit aviso
- **WHEN** a COORDINADOR clicks "Editar" on an aviso row, changes the titulo and severidad
- **AND** clicks "Guardar"
- **THEN** the system calls `PATCH /api/v1/avisos/{id}` with the updated fields
- **AND** shows success toast

### Requirement: COORDINADOR/ADMIN can deactivate avisos
The system SHALL allow soft-deleting (deactivating) an aviso. Calls `DELETE /api/v1/avisos/{id}`.

#### Scenario: Deactivate aviso
- **WHEN** a COORDINADOR clicks "Eliminar" on an aviso row
- **THEN** the system shows a confirmation dialog "¿Estás seguro de desactivar este aviso?"
- **AND** upon confirmation, calls `DELETE /api/v1/avisos/{id}` and removes the row from the table

### Requirement: User can view active avisos
The system SHALL display active avisos scoped to the authenticated user's roles, cohortes, and materias. Avísos outside their vigencia window SHALL NOT be shown. Calls `GET /api/v1/avisos`.

#### Scenario: User sees filtered avisos
- **WHEN** a PROFESOR with rol TUTOR assigned to cohort MAR-2025 logs in
- **THEN** the system displays only avisos where alcance is "Global" OR (alcance="PorRol" AND rol_destino="TUTOR") OR (alcance="PorCohorte" AND cohorte matches user's cohortes)
- **AND** avisos outside their vigencia window are not shown

### Requirement: User can acknowledge aviso reading
The system SHALL allow a user to confirm reading an aviso when `requiere_ack=true`. After acknowledgment, the aviso stops being highlighted. Calls `POST /api/v1/avisos/{id}/ack`.

#### Scenario: Acknowledge aviso
- **WHEN** a user sees an aviso with `requiere_ack=true` and `user_acked=false`
- **AND** clicks "Confirmar lectura"
- **THEN** the system calls `POST /api/v1/avisos/{id}/ack`
- **AND** updates the aviso display: `user_acked=true` and `total_acks` increments


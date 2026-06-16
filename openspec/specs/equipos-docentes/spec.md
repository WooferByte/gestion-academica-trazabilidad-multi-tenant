# equipos-docentes Specification

## Purpose
TBD - created by archiving change c-23a-frontend-equipos-docentes. Update Purpose after archive.
## Requirements
### Requirement: User can view Mis Equipos (F4.2)
The system SHALL display a list of the authenticated user's active assignments (comisiones, materias, roles, vigencia). PROFESOR/TUTOR/NEXO/COORDINADOR see only their own assignments. Filters by estado, materia, rol, carrera, cohorte SHALL be available.

#### Scenario: PROFESOR sees their comisiones
- **WHEN** a PROFESOR navigates to `/equipos`
- **THEN** the system displays a table with rows for each of their active asignaciones (materia_nombre, cohorte_nombre, rol, desde, hasta)
- **AND** the user can filter by materia, cohorte, and rol

#### Scenario: COORDINADOR sees all tenant assignments
- **WHEN** a COORDINADOR navigates to `/equipos`
- **THEN** the system displays all active asignaciones for the tenant (not just the user's own)

### Requirement: User can perform individual assignment management (F4.3)
The system SHALL allow COORDINADOR/ADMIN to view, create, edit, and delete individual asignaciones. A form SHALL capture usuario_id, rol, materia/carrera/cohorte context, comisiones, responsable_id, and vigencia.

#### Scenario: COORDINADOR edits an existing asignacion
- **WHEN** a COORDINADOR clicks "Editar" on an asignacion row
- **THEN** the system opens a dialog with pre-filled form fields from the current asignacion values
- **AND** upon submission, the system calls `PATCH /api/v1/asignaciones/{id}` with the updated fields

#### Scenario: COORDINADOR deletes an asignacion (soft delete)
- **WHEN** a COORDINADOR clicks "Eliminar" on an asignacion row
- **THEN** the system shows a confirmation dialog
- **AND** upon confirmation, calls `DELETE /api/v1/asignaciones/{id}` and removes the row from the list

### Requirement: User can perform bulk assignment (F4.4)
The system SHALL provide a form where COORDINADOR/ADMIN selects multiple docentes and assigns them in bulk to a materia×carrera×cohorte×rol combination with vigencia. The request SHALL call `POST /api/v1/equipos/asignacion-masiva`.

#### Scenario: Successful bulk assignment
- **WHEN** a COORDINADOR selects 3 docentes, sets materia, carrera, cohorte, rol "TUTOR", and vigencia dates
- **AND** clicks "Asignar"
- **THEN** the system calls `POST /api/v1/equipos/asignacion-masiva` with `usuario_ids: [id1, id2, id3]`, `materia_id`, `carrera_id`, `cohorte_id`, `rol: "TUTOR"`, `desde` and `hasta`
- **AND** shows a success toast with the count of created asignaciones

#### Scenario: Bulk assignment validation error
- **WHEN** the form is submitted without selecting any docentes
- **THEN** the system shows inline validation error "Seleccioná al menos un docente"

### Requirement: User can clone team between periods (F4.5)
The system SHALL provide a 2-step wizard for COORDINADOR/ADMIN to duplicate asignaciones from an origin (materia×carrera×cohorte) to a destination (materia×carrera×cohorte) with new vigencia dates. Calls `POST /api/v1/equipos/clonar`.

#### Scenario: Successful clone
- **WHEN** a COORDINADOR selects origin (Materia A, Carrera X, Cohort MAR-2025) and destination (Materia A, Carrera X, Cohort AGO-2025) with dates 01/08/2025–31/12/2025
- **AND** confirms the clone
- **THEN** the system calls `POST /api/v1/equipos/clonar` with `{ origen: { materia_id, carrera_id, cohorte_id }, destino: { materia_id, carrera_id, cohorte_id, desde, hasta } }`
- **AND** shows success toast with the count of cloned asignaciones

#### Scenario: Clone preview
- **WHEN** a COORDINADOR selects origin and destination
- **THEN** the system shows a preview of how many asignaciones will be cloned before confirmation

### Requirement: User can modify team validity in bulk (F4.6)
The system SHALL allow COORDINADOR/ADMIN to update the `desde`/`hasta` dates for all asignaciones of a selected team (materia×carrera×cohorte) in one operation. Calls `PATCH /api/v1/equipos/vigencia`.

#### Scenario: Bulk validity update
- **WHEN** a COORDINADOR selects a team (Materia A, Carrera X, Cohort MAR-2025) and sets new `desde` and `hasta` dates
- **AND** clicks "Actualizar Vigencia"
- **THEN** the system calls `PATCH /api/v1/equipos/vigencia` with `{ materia_id, carrera_id, cohorte_id, desde, hasta }`
- **AND** shows success toast with `filas_afectadas` count

### Requirement: User can export team to CSV (F4.7)
The system SHALL allow COORDINADOR/ADMIN to download a CSV file with all asignaciones of a selected team. Calls `GET /api/v1/equipos/exportar?materia_id=&carrera_id=&cohorte_id=`.

#### Scenario: Successful export
- **WHEN** a COORDINADOR selects a team filter (materia, carrera, cohorte) and clicks "Exportar"
- **THEN** the system calls `GET /api/v1/equipos/exportar` with selected filters
- **AND** downloads a CSV file named `equipo-docente.csv`


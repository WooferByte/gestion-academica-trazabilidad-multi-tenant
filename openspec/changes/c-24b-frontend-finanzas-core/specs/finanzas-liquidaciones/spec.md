## ADDED Requirements

### Requirement: Listar liquidaciones
The system SHALL display a list of liquidaciones for the selected cohorte/periodo, showing id, usuario, período, rol, monto_base, monto_plus, total, es_nexo, excluído_por_factura, and estado for each record.

#### Scenario: Listar todas las liquidaciones
- **WHEN** user navigates to `/liquidaciones`
- **THEN** system fetches GET `/api/v1/liquidaciones` with optional `cohorte_id`, `periodo`, `usuario_id` query params
- **THEN** system renders a DataTable with all returned records

#### Scenario: Filtrar por cohorte y período
- **WHEN** user selects a cohorte and a periodo from filter controls
- **THEN** system re-fetches with `cohorte_id` and `periodo` query params

### Requirement: Calcular liquidación
The system SHALL allow triggering calculation of liquidaciones for a given cohorte + periodo via POST.

#### Scenario: Calcular exitoso
- **WHEN** user clicks "Calcular" and confirms
- **THEN** system sends POST `/api/v1/liquidaciones/calcular` with `{ "cohorte_id": "...", "periodo": "..." }`
- **THEN** system shows success toast and refreshes the list

### Requirement: Cerrar liquidación
The system SHALL allow closing an immutable liquidación for a cohorte + periodo via POST with path params.

#### Scenario: Cerrar exitoso
- **WHEN** user clicks "Cerrar" and confirms via ConfirmDialog
- **THEN** system sends POST `/api/v1/liquidaciones/cerrar/{cohorte_id}/{periodo}`
- **THEN** system shows success toast with `{ "cerradas": number, "periodo": string }`

### Requirement: Ver historial de liquidaciones
The system SHALL display historical liquidaciones (cerradas) with same filters as listar.

#### Scenario: Navegar a historial
- **WHEN** user navigates to `/liquidaciones/historial`
- **THEN** system fetches GET `/api/v1/liquidaciones/historial` with optional filters
- **THEN** system renders a DataTable with historical records (read-only)

### Requirement: Exportar liquidaciones a CSV
The system SHALL download a CSV file for a given cohorte + periodo.

#### Scenario: Exportar CSV
- **WHEN** user clicks "Exportar CSV" with cohorte and periodo selected
- **THEN** system fetches GET `/api/v1/liquidaciones/exportar?cohorte_id=...&periodo=...`
- **THEN** system downloads the response as a CSV file

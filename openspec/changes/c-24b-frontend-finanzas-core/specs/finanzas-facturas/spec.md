## ADDED Requirements

### Requirement: Listar facturas
The system SHALL display a list of facturas with filters for usuario_id, periodo, and estado.

#### Scenario: Listar todas las facturas
- **WHEN** user navigates to `/facturas`
- **THEN** system fetches GET `/api/v1/facturas` with optional `usuario_id`, `periodo`, `estado` query params
- **THEN** system renders a DataTable with FacturaResponse fields

### Requirement: Crear factura
The system SHALL allow creating a new factura via POST, returning the created record with status 201.

#### Scenario: Crear factura exitoso
- **WHEN** user fills the create form and submits
- **THEN** system sends POST `/api/v1/facturas` with `{ "usuario_id", "periodo", "detalle", "referencia_archivo"?, "tamano_kb"? }`
- **THEN** system shows success toast and navigates to list

### Requirement: Ver detalle de factura
The system SHALL display the detail of a single factura by its ID.

#### Scenario: Ver detalle
- **WHEN** user clicks a factura row
- **THEN** system fetches GET `/api/v1/facturas/{factura_id}`
- **THEN** system renders a detail view with all fields (including cargada_at, abonada_at)

### Requirement: Cambiar estado de factura
The system SHALL allow toggling between pendiente and abonada states via PATCH.

#### Scenario: Marcar como abonada
- **WHEN** user clicks "Marcar como abonada" on a pendiente factura and confirms
- **THEN** system sends PATCH `/api/v1/facturas/{factura_id}/estado` with `{ "estado": "abonada" }`
- **THEN** system shows success toast and refreshes

#### Scenario: Reabrir factura
- **WHEN** user clicks "Reabrir" on an abonada factura
- **THEN** system sends PATCH `/api/v1/facturas/{factura_id}/estado` with `{ "estado": "pendiente" }`
- **THEN** system shows success toast and refreshes

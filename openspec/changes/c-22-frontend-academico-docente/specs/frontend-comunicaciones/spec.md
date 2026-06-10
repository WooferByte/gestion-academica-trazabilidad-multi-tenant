## ADDED Requirements

### Requirement: Communication flow requires mandatory preview (RN-16)
The system SHALL require a preview step before sending any communication. The "Enviar" button MUST remain disabled until preview is shown.

#### Scenario: Select students and compose
- **WHEN** user navigates to `/academico/:materiaId/:cohorteId/comunicar` with selected student IDs
- **THEN** the system displays the count of selected recipients
- **AND** shows a textarea for composing the message

#### Scenario: Preview is mandatory before send
- **WHEN** user clicks "Vista previa"
- **THEN** the system calls `POST /api/v1/comunicaciones/preview` with recipients and message body
- **AND** displays the rendered preview with recipient list and formatted message
- **AND** enables the "Enviar" button

#### Scenario: Preview must be regenerated if message changes
- **WHEN** user edits the message after preview
- **THEN** the "Enviar" button becomes disabled again
- **AND** a hint reads "Debe generar una nueva vista previa"

### Requirement: Send communication individually
The system SHALL allow sending a communication that is tracked individually per recipient.

#### Scenario: Send individual communication
- **WHEN** user confirms after preview
- **THEN** the system calls `POST /api/v1/comunicaciones` with the message and recipient list
- **AND** navigates to the tracking view showing current status

### Requirement: Send batch communication requires approval (RN-17)
The system SHALL create a batch/lote for mass communications that requires coordinator approval.

#### Scenario: Send batch communication
- **WHEN** user has multiple recipients and clicks "Enviar lote"
- **THEN** the system calls `POST /api/v1/comunicaciones/lote` with message and recipient list
- **AND** displays a notice: "Este envío requiere aprobación de un coordinador"
- **AND** navigates to the tracking view showing lote status as Pendiente 🟡

### Requirement: Communication tracking with status badges (RN-15)
The system SHALL display communication status with distinct colors: Pendiente 🟡, Enviando 🔵, Enviado 🟢, Error 🔴, Cancelado ⚪.

#### Scenario: Track by lote
- **WHEN** user navigates to communication tracking view
- **THEN** the system calls `GET /api/v1/comunicaciones?lote_id=X`
- **AND** displays a table with student name, status badge, timestamp, and error message (if Error)

#### Scenario: Auto-refresh tracking for in-flight items
- **WHEN** any communication has status "Enviando" or "Pendiente"
- **THEN** the system polls every 5 seconds with `refetchInterval: 5000`

### Requirement: Cancel individual communication
The system SHALL allow cancelling a pending communication.

#### Scenario: Cancel pending communication
- **WHEN** user clicks "Cancelar" on a communication with status Pendiente
- **THEN** the system shows a confirmation dialog
- **WHEN** user confirms
- **THEN** the system calls `POST /api/v1/comunicaciones/{id}/cancelar`
- **AND** the status changes to Cancelado ⚪

### Requirement: Approve batch communications
The system SHALL allow COORDINADOR/ADMIN users to approve pending batch communications.

#### Scenario: View pending approvals
- **WHEN** user with `comunicacion:aprobar` permission navigates to approval view
- **THEN** the system displays pending lotes with count of recipients and message preview

#### Scenario: Approve lote
- **WHEN** user clicks "Aprobar" on a pending lote
- **THEN** the system calls `POST /api/v1/comunicaciones/aprobar-lote` with lote ID
- **AND** the lote status updates to Enviando

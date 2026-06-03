## ADDED Requirements

### Requirement: Envíos requieren aprobación según tenant

El sistema SHALL soportar aprobación humana opcional para envíos masivos, configurable por tenant.

#### Scenario: Tenant con aprobación obligatoria
- **WHEN** un usuario encola un lote de comunicaciones en un tenant que tiene `aprobacion_comunicaciones = true`
- **THEN** todas las comunicaciones del lote se crean en estado Pendiente con `aprobacion_requerida = true` y no se procesan hasta ser aprobadas

#### Scenario: Tenant sin aprobación
- **WHEN** un usuario encola un lote en un tenant con `aprobacion_comunicaciones = false`
- **THEN** las comunicaciones se crean en estado Pendiente y el worker las procesa inmediatamente

### Requirement: Aprobar lote de comunicaciones

El sistema SHALL permitir a un usuario con permiso `comunicacion:aprobar` aprobar o rechazar un lote completo.

#### Scenario: Aprobar lote exitosamente
- **WHEN** un usuario con `comunicacion:aprobar` envía un POST a `/api/v1/comunicaciones/aprobar-lote` con `lote_id` y `accion: aprobar`
- **THEN** todas las comunicaciones del lote con `aprobacion_requerida = true` quedan habilitadas para que el worker las procese

#### Scenario: Rechazar lote
- **WHEN** un usuario con `comunicacion:aprobar` envía un POST a `/api/v1/comunicaciones/aprobar-lote` con `lote_id` y `accion: rechazar`
- **THEN** todas las comunicaciones del lote transicionan a Cancelado

#### Scenario: Aprobar sin permiso
- **WHEN** un usuario sin `comunicacion:aprobar` intenta aprobar un lote
- **THEN** el sistema responde 403 Forbidden

### Requirement: Trazabilidad de aprobación

Cada aprobación o rechazo SHALL quedar registrada en el audit log.

#### Scenario: Audit al aprobar lote
- **WHEN** un lote es aprobado
- **THEN** el sistema registra un evento de auditoría con `COMUNICACION_ENVIAR`, detalle del lote y cantidad de comunicaciones afectadas

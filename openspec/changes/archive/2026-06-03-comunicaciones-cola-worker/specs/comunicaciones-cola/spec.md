## ADDED Requirements

### Requirement: Encolar comunicación

El sistema SHALL permitir encolar una comunicación para un destinatario.

#### Scenario: Encolar con datos básicos
- **WHEN** un usuario con permiso `comunicacion:enviar` envía un POST a `/api/v1/comunicaciones/` con `materia_id`, `destinatario`, `asunto` y `cuerpo`
- **THEN** el sistema crea un registro en la tabla `comunicaciones` con estado `Pendiente`, asignando UUID a `lote_id` y cifrando el destinatario con AES-256

#### Scenario: Encolar múltiples destinatarios
- **WHEN** un usuario envía un POST a `/api/v1/comunicaciones/lote` con un array de destinatarios, asunto y cuerpo
- **THEN** el sistema crea un registro por destinatario, todos con el mismo `lote_id` y estado `Pendiente`

#### Scenario: Rechazar envío sin permiso
- **WHEN** un usuario sin permiso `comunicacion:enviar` intenta encolar una comunicación
- **THEN** el sistema responde 403 Forbidden

### Requirement: Estados del mensaje

Cada comunicación SHALL transicionar en orden: Pendiente → Enviando → Enviado | Error | Cancelado.

#### Scenario: Mensaje enviado correctamente
- **WHEN** el worker toma un mensaje Pendiente, inicia el envío y recibe confirmación
- **THEN** el estado transiciona a Enviado y se actualiza `enviado_at`

#### Scenario: Mensaje falla
- **WHEN** el worker toma un mensaje Pendiente, inicia el envío y ocurre un error
- **THEN** el estado transiciona a Error

#### Scenario: Cancelar antes de enviar
- **WHEN** un usuario con permiso `comunicacion:enviar` cancela un mensaje en estado Pendiente
- **THEN** el estado transiciona a Cancelado

#### Scenario: Cancelar envío en progreso
- **WHEN** un usuario cancela un mensaje en estado Enviando
- **THEN** el sistema responde 400 (no se puede cancelar un envío en progreso)

### Requirement: Preview de comunicación

El sistema SHALL generar una vista previa del mensaje con variables sustituidas antes de encolar.

#### Scenario: Preview exitoso
- **WHEN** un usuario envía un POST a `/api/v1/comunicaciones/preview` con `destinatario`, `asunto` y `cuerpo` conteniendo `{{alumno.nombre}}` y `{{materia.nombre}}`
- **THEN** el sistema retorna el asunto y cuerpo renderizados con las variables sustituidas, SIN crear ningún registro en la tabla

#### Scenario: Variable no encontrada
- **WHEN** el cuerpo contiene `{{variable.inexistente}}` y el sistema no encuentra la variable
- **THEN** el sistema reemplaza la variable por una cadena vacía y lo indica en la respuesta

### Requirement: Listar comunicaciones

El sistema SHALL permitir listar comunicaciones por lote o por materia.

#### Scenario: Listar por lote
- **WHEN** un usuario consulta `GET /api/v1/comunicaciones?lote_id=<uuid>`
- **THEN** el sistema retorna todas las comunicaciones de ese lote con su estado y destinatario (descifrado solo para el owner del lote)

#### Scenario: Listar por materia
- **WHEN** un usuario consulta `GET /api/v1/comunicaciones?materia_id=<uuid>`
- **THEN** el sistema retorna las comunicaciones de esa materia, filtradas por tenant

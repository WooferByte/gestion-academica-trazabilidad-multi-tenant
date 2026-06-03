## ADDED Requirements

### Requirement: Worker procesa cola de comunicaciones

El worker SHALL ejecutar un loop infinito que consuma comunicaciones Pendientes y las procese.

#### Scenario: Worker procesa una comunicación Pendiente
- **WHEN** el worker encuentra una comunicación en estado Pendiente (sin aprobación requerida o ya aprobada)
- **THEN** transiciona a Enviando, ejecuta el envío SMTP, y al recibir confirmación transiciona a Enviado con `enviado_at` actualizado

#### Scenario: Worker falla al enviar
- **WHEN** el worker encuentra una comunicación Pendiente y el envío SMTP lanza excepción
- **THEN** transiciona a Error y registra el error en logs

#### Scenario: Worker salta comunicaciones con aprobación pendiente
- **WHEN** el worker encuentra una comunicación con `aprobacion_requerida = true` y sin aprobar
- **THEN** la salta y continúa con la siguiente (no la bloquea)

#### Scenario: Worker procesa en batches
- **WHEN** el worker inicia un ciclo
- **THEN** selecciona hasta N comunicaciones Pendientes (batch configurable, default 50) y las procesa secuencialmente

### Requirement: Plantillas con variables de sustitución

El worker SHALL soportar sustitución de variables en asunto y cuerpo antes de enviar.

#### Scenario: Sustitución simple
- **WHEN** el cuerpo contiene `{{alumno.nombre}}` y el sistema conoce el nombre del alumno destinatario
- **THEN** reemplaza `{{alumno.nombre}}` por el valor real antes del envío

#### Scenario: Sustitución de múltiples variables
- **WHEN** el cuerpo contiene `{{alumno.nombre}}` y `{{materia.nombre}}`
- **THEN** ambas variables se sustituyen por sus valores correspondientes

#### Scenario: Variable sin valor conocido
- **WHEN** una variable en el template no tiene valor en los datos del destinatario
- **THEN** se reemplaza por cadena vacía (sin fallar el envío)

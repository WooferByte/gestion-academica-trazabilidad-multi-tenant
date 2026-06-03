## ADDED Requirements

### Requirement: Cliente Moodle Web Services skeleton

El sistema SHALL implementar un cliente Moodle Web Services en `integrations/moodle_ws.py` con métodos para sync de usuarios y actividades. En C-09, el cliente SHALL ser un skeleton (mock) que retorna datos prefijados y acepta configuración por tenant (`MOODLE_WS_URL`, `MOODLE_WS_TOKEN`). Los errores de conexión SHALL mapear a excepción con código 502.

#### Scenario: Skeleton retorna datos mock
- **WHEN** se invoca `sync_usuarios(materia_id)` en el cliente Moodle WS
- **THEN** retorna una lista simulada de usuarios sin conexión real a Moodle

#### Scenario: Error de conexión mapea a 502
- **WHEN** el cliente Moodle WS encuentra un error de conexión
- **THEN** el servicio eleva una excepción que el router mapea a `HTTPException(502, "Error de integración con Moodle")`

### Requirement: Sync on-demand

El sistema SHALL exponer un endpoint para sincronizar el padrón desde Moodle bajo demanda. En C-09, la sync SHALL usar el skeleton.

#### Scenario: Sync on-demand retorna versión creada
- **WHEN** el usuario solicita sync on-demand para materia M
- **THEN** el sistema ejecuta el skeleton de Moodle WS
- **AND** crea una nueva `VersionPadron` con los datos mock
- **AND** retorna la versión creada

### Requirement: Configuración por tenant

El cliente Moodle WS SHALL leer la configuración (`MOODLE_WS_URL`, `MOODLE_WS_TOKEN`) desde la configuración del tenant, no desde variables globales.

#### Scenario: Configuración tenant-specific
- **WHEN** se instancia el cliente Moodle WS para el tenant A
- **THEN** usa `MOODLE_WS_URL` y `MOODLE_WS_TOKEN` configurados para el tenant A

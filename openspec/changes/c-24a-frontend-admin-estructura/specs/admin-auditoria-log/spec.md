## ADDED Requirements

### Requirement: Log completo de auditoría
El sistema SHALL proveer una vista de log completo de auditoría para usuarios ADMIN, consumiendo la API de C-19, con filtros avanzados y paginación server-side.

#### Scenario: Log completo con paginación server-side
- **WHEN** un ADMIN navega a `/admin/auditoria/log`
- **THEN** el sistema SHALL mostrar una tabla paginada con todos los registros de auditoría del tenant
- **AND** cada fila SHALL contener: fecha y hora, usuario, materia, acción, registros afectados, IP, user agent
- **AND** la paginación SHALL ser server-side (los parámetros limit/offset se envían a la API)

#### Scenario: Filtros combinados
- **WHEN** un ADMIN aplica filtros de rango de fechas, materia, usuario
- **THEN** el sistema SHALL enviar los filtros como query params a la API
- **AND** SHALL recargar la tabla con los resultados filtrados

#### Scenario: Filtro por tipo de acción
- **WHEN** un ADMIN selecciona un tipo de acción específico en el filtro
- **THEN** el sistema SHALL mostrar solo los registros de ese tipo de acción

#### Scenario: Vista sin resultados
- **WHEN** no hay registros que coincidan con los filtros aplicados
- **THEN** el sistema SHALL mostrar un EmptyState con mensaje "No se encontraron registros de auditoría para los filtros seleccionados"

#### Scenario: Acceso restringido a ADMIN
- **WHEN** un COORDINADOR sin permisos adicionales intenta acceder a `/admin/auditoria/log`
- **THEN** el sistema SHALL redirigir al dashboard (solo ADMIN puede ver el log completo según F9.2)

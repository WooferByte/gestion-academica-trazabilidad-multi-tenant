## ADDED Requirements

### Requirement: COORDINADOR/ADMIN puede clonar un equipo docente entre cohortes
El sistema SHALL exponer un endpoint `POST /api/v1/equipos/clonar` que duplica todas las asignaciones vigentes de un equipo origen hacia un destino, actualizando las fechas. Solo accesible con permiso `equipos:asignar`. (Regla RN-12)

#### Scenario: Clonado exitoso entre cohortes
- **WHEN** un usuario con permiso `equipos:asignar` envía POST a `/api/v1/equipos/clonar` con `origen: { materia_id, carrera_id, cohorte_id }` y `destino: { materia_id, carrera_id, cohorte_id, desde, hasta }`
- **THEN** el sistema duplica todas las asignaciones vigentes del origen al destino con las nuevas fechas y retorna 201 con la lista de asignaciones creadas

#### Scenario: Clonado sin asignaciones vigentes en origen
- **WHEN** el equipo origen no tiene asignaciones vigentes
- **THEN** el sistema retorna 200 con lista vacía (sin error)

#### Scenario: Clonado genera auditoría
- **WHEN** el clonado se completa exitosamente
- **THEN** el sistema registra un evento de auditoría con código `ASIGNACION_MODIFICAR`

#### Scenario: Usuario sin permiso recibe 403
- **WHEN** un usuario sin `equipos:asignar` envía POST a `/api/v1/equipos/clonar`
- **THEN** el sistema retorna 403 Forbidden

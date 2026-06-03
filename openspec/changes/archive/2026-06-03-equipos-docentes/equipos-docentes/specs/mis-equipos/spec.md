## ADDED Requirements

### Requirement: Docente puede ver sus propias asignaciones
El sistema SHALL exponer un endpoint `GET /api/v1/equipos/mis-equipos` que retorna las asignaciones del usuario autenticado, con soporte de filtros opcionales.

#### Scenario: Docente consulta mis-equipos sin filtros
- **WHEN** un usuario autenticado con rol PROFESOR envía GET a `/api/v1/equipos/mis-equipos`
- **THEN** el sistema retorna 200 con la lista de asignaciones activas de ese usuario

#### Scenario: Docente filtra por materia y cohorte
- **WHEN** un usuario autenticado envía GET a `/api/v1/equipos/mis-equipos?materia_id=<id>&cohorte_id=<id>`
- **THEN** el sistema retorna solo las asignaciones del usuario que coinciden con materia_id y cohorte_id

#### Scenario: Docente filtra solo vigentes
- **WHEN** un usuario autenticado envía GET a `/api/v1/equipos/mis-equipos?solo_vigentes=true`
- **THEN** el sistema retorna solo asignaciones cuya fecha `hasta` es nula o mayor a la fecha actual

#### Scenario: Usuario no autenticado recibe 401
- **WHEN** un request sin token JWT válido accede a `GET /api/v1/equipos/mis-equipos`
- **THEN** el sistema retorna 401 Unauthorized

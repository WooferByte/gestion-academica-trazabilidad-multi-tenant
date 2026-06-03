## ADDED Requirements

### Requirement: Vista global de encuentros (F6.5)
El sistema SHALL exponer `GET /api/v1/encuentros/instancias` con filtros opcionales (`materia_id`, `desde`, `hasta`, `estado`, `slot_id`, `offset`, `limit`). Solo accesible con permiso `encuentros:gestionar`. Para COORDINADOR/ADMIN: retorna instancias de TODAS las materias del tenant. Para PROFESOR: retorna solo instancias de sus materias asignadas. La respuesta SHALL incluir `total` para paginación y los datos de la materia y el slot asociados.

#### Scenario: Coordinador ve todos los encuentros del tenant
- **WHEN** COORDINADOR consulta `GET /api/v1/encuentros/instancias` sin filtros
- **THEN** el sistema SHALL retornar TODAS las instancias del tenant, paginadas

#### Scenario: Profesor ve solo sus encuentros
- **WHEN** PROFESOR consulta la vista global
- **THEN** el sistema SHALL filtrar instancias solo de las materias donde tiene asignación activa

#### Scenario: Filtro por rango de fechas
- **WHEN** se consulta con `desde=2026-03-01&hasta=2026-03-31`
- **THEN** el sistema SHALL retornar solo instancias dentro de ese rango

### Requirement: Listar slots del tenant
El sistema SHALL exponer `GET /api/v1/encuentros/slots` que retorna los slots filtrables por `materia_id`. Accesible con permiso `encuentros:gestionar`.

#### Scenario: Listar slots por materia
- **WHEN** se consulta `GET /api/v1/encuentros/slots?materia_id=X`
- **THEN** el sistema SHALL retornar los slots de esa materia con sus datos

## ADDED Requirements

### Requirement: Sistema puede mostrar monitor general de actividades (coordinación/admin)
El sistema SHALL devolver una vista transversal del estado de actividades de todos los alumnos del tenant, con filtros disponibles: materia, regional, comisión, búsqueda libre por alumno, estado de actividad (F2.7).

#### Scenario: Monitor general sin filtros devuelve todos los alumnos del tenant
- **WHEN** un COORDINADOR consulta el monitor general sin filtros
- **THEN** la respuesta incluye todos los alumnos con calificaciones en el tenant
- **AND** cada entrada incluye: alumno, materia, actividad, nota, estado (aprobado/desaprobado/sin nota)

#### Scenario: Monitor general filtra por materia
- **WHEN** un COORDINADOR consulta el monitor general con filtro materia_id=M1
- **THEN** solo se incluyen alumnos y actividades de M1

#### Scenario: Monitor general filtra por búsqueda libre de alumno
- **WHEN** un COORDINADOR consulta el monitor general con búsqueda "García"
- **THEN** solo se incluyen alumnos cuyo nombre o apellidos contienen "García" (case-insensitive)

#### Scenario: Monitor general exporta a CSV
- **WHEN** un COORDINADOR consulta el monitor general con ?format=csv
- **THEN** la respuesta tiene Content-Type text/csv con los mismos datos filtrados

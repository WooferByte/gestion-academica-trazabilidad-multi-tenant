## ADDED Requirements

### Requirement: Sistema puede generar ranking de actividades aprobadas por alumno
El sistema SHALL devolver un ranking ordenado de alumnos por cantidad de actividades aprobadas, incluyendo solo aquellos con al menos una actividad aprobada (RN-09).

#### Scenario: Ranking incluye solo alumnos con al menos una aprobada
- **WHEN** se consulta ranking para materia M
- **AND** el alumno A tiene 5 actividades aprobadas, alumno B tiene 0
- **THEN** el ranking incluye a A (posición 1) y NO incluye a B

#### Scenario: Ranking ordenado descendente por cantidad de aprobadas
- **WHEN** se consulta ranking para materia M
- **AND** alumno A tiene 7 aprobadas, alumno B tiene 3, alumno C tiene 7
- **THEN** el orden es: A (1°), C (2°), B (3°)
- **AND** los alumnos con mismo puntaje se ordenan alfabéticamente por apellido+nombre

#### Scenario: Una actividad con aprobado = null no cuenta como aprobada
- **WHEN** se consulta ranking
- **AND** el alumno A tiene una actividad donde aprobado es NULL (sin nota)
- **THEN** esa actividad no se contabiliza como aprobada

#### Scenario: Ranking cruza contra el umbral configurado
- **WHEN** se consulta ranking para materia M con umbral 70%
- **AND** el alumno A tiene nota_numerica = 65
- **THEN** esa actividad NO se contabiliza como aprobada

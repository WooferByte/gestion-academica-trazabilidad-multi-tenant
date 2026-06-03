## ADDED Requirements

### Requirement: Sistema puede computar alumnos atrasados por materia+cohorte
El sistema SHALL devolver la lista de alumnos atrasados para una materia y cohorte dadas, identificando a aquellos con actividades faltantes o nota inferior al umbral (RN-06).

#### Scenario: Alumno sin calificación en una actividad es considerado atrasado
- **WHEN** se consulta atrasados para materia M con umbral 60%
- **AND** el alumno A tiene una actividad sin calificación registrada
- **THEN** el alumno A aparece en la respuesta como atrasado

#### Scenario: Alumno con nota numérica menor al umbral es considerado atrasado
- **WHEN** se consulta atrasados para materia M con umbral 60%
- **AND** el alumno A tiene nota_numerica = 40 en una actividad
- **THEN** el alumno A aparece en la respuesta como atrasado

#### Scenario: Alumno con nota textual no aprobatoria es considerado atrasado
- **WHEN** se consulta atrasados para materia M con valores_aprobatorios = ["Satisfactorio", "Supera"]
- **AND** el alumno A tiene nota_textual = "Regular" en una actividad
- **THEN** el alumno A aparece en la respuesta como atrasado

#### Scenario: Alumno con todas las actividades aprobadas no aparece
- **WHEN** se consulta atrasados para materia M con umbral 60%
- **AND** el alumno A tiene nota_numerica >= 60 en todas las actividades
- **THEN** el alumno A NO aparece en la respuesta

#### Scenario: Usuario sin permiso atrasados:ver recibe 403
- **WHEN** un usuario sin permiso `atrasados:ver` intenta acceder al endpoint
- **THEN** recibe HTTP 403

#### Scenario: Filtro por materia respeta tenant isolation
- **WHEN** se consulta atrasados para materia M en tenant T1
- **THEN** solo se consideran calificaciones del tenant T1

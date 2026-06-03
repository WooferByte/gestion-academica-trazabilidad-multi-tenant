## ADDED Requirements

### Requirement: Sistema puede mostrar monitor de seguimiento filtrado (tutor/profesor)
El sistema SHALL devolver el estado de actividades de los alumnos asignados al TUTOR o PROFESOR, filtrable por alumno, comisión, regional, actividad y mínimo de actividad cumplida (F2.8).

#### Scenario: Tutor ve solo alumnos de sus materias asignadas
- **WHEN** un TUTOR consulta el monitor de seguimiento
- **THEN** la respuesta incluye solo alumnos de las materias donde el TUTOR tiene asignación activa

#### Scenario: Monitor de seguimiento filtra por comisión
- **WHEN** un TUTOR consulta el monitor con filtro comision="A"
- **THEN** solo se incluyen alumnos de la comisión A

#### Scenario: Monitor de seguimiento filtra por mínimo de actividades cumplidas
- **WHEN** un TUTOR consulta el monitor con filtro min_actividades=3
- **THEN** solo se incluyen alumnos con al menos 3 actividades aprobadas

### Requirement: Sistema puede mostrar monitor de seguimiento con rango de fechas (coordinación/admin)
Extiende el monitor de seguimiento con filtro adicional de rango de fechas para acotar el período de análisis (F2.9).

#### Scenario: Coordinador filtra por rango de fechas
- **WHEN** un COORDINADOR consulta el monitor con fecha_desde="2026-03-01" y fecha_hasta="2026-03-31"
- **THEN** solo se incluyen calificaciones con importado_at dentro del rango

#### Scenario: Rango de fechas sin datos devuelve lista vacía
- **WHEN** un COORDINADOR consulta el monitor con un rango sin calificaciones
- **THEN** la respuesta es una lista vacía

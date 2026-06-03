## ADDED Requirements

### Requirement: Importar reporte de finalización de actividades (F1.2)
The system SHALL accept a completion report from the LMS, detect activities marked as completed by the student, and cross-reference against existing Calificacion records.

#### Scenario: Detectar entregas sin calificar (RN-07)
- **WHEN** user uploads a completion report showing activity "TP1" as completed for alumno X
- **AND** there is no Calificacion record for alumno × TP1
- **THEN** the system reports TP1 for alumno X as "posible entrega sin corregir"

#### Scenario: Solo textuales en reporte (RN-08)
- **WHEN** the completion report includes both numeric and textual activities
- **THEN** only textual activities appear in the "posibles entregas sin corregir" table

#### Scenario: Cruce contra calificaciones existentes
- **WHEN** alumno X has Calificacion with nota_numerica for TP1
- **AND** the report marks TP1 as completed
- **THEN** TP1 is NOT included in "posibles entregas sin corregir"

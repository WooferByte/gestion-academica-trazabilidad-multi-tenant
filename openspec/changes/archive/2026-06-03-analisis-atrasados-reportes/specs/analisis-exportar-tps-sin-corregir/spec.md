## ADDED Requirements

### Requirement: Sistema puede exportar listado de TPs sin corregir
El sistema SHALL devolver (en JSON o CSV) el listado de entregas detectadas como pendientes de corrección: actividades donde el reporte de finalización indica "entregado" pero no hay calificación registrada para ese alumno (RN-07, RN-08).

#### Scenario: Export CSV incluye header y filas de entregas sin corregir
- **WHEN** se exportan TPs sin corregir para materia M en formato CSV
- **AND** hay 3 entregas sin calificación
- **THEN** la respuesta tiene Content-Type text/csv
- **AND** incluye header "alumno,actividad,comision" y 3 filas de datos

#### Scenario: Export JSON devuelve lista estructurada
- **WHEN** se exportan TPs sin corregir para materia M en formato JSON
- **AND** hay entregas sin calificación
- **THEN** la respuesta es un array con objetos { alumno_nombre, alumno_apellidos, actividad, comision }

#### Scenario: Sin entregas sin corregir devuelve lista vacía
- **WHEN** se exportan TPs sin corregir para materia M
- **AND** todas las entregas tienen calificación registrada
- **THEN** la respuesta es una lista vacía (o CSV con solo header)

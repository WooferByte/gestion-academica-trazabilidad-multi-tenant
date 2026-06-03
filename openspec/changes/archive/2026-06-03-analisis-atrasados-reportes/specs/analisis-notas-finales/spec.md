## ADDED Requirements

### Requirement: Sistema puede calcular nota final agrupada por alumno
El sistema SHALL calcular una nota final por alumno promediando las notas numéricas de las actividades seleccionadas en el request.

#### Scenario: Nota final promedia actividades seleccionadas
- **WHEN** se solicitan notas finales para materia M con actividades ["TP1", "TP2", "Parcial"]
- **AND** alumno A tiene TP1=80, TP2=90, Parcial=70
- **THEN** la nota final de A es (80+90+70)/3 = 80.0

#### Scenario: Actividad sin nota numérica se excluye del promedio
- **WHEN** se solicitan notas finales para materia M con actividades ["TP1", "TP2"]
- **AND** alumno A tiene TP1=80, TP2 sin nota numérica
- **THEN** la nota final de A es 80.0 (solo TP1 cuenta)

#### Scenario: Alumno sin notas numéricas en actividades seleccionadas no tiene nota final
- **WHEN** se solicitan notas finales para materia M
- **AND** alumno A no tiene nota numérica en ninguna actividad seleccionada
- **THEN** la nota final de A es null

## ADDED Requirements

### Requirement: Sistema puede generar reporte rápido con métricas consolidadas por materia
El sistema SHALL devolver métricas clave de una materia: total de alumnos en padrón, total de actividades, cantidad de alumnos aprobados, cantidad de atrasados, promedio general de notas.

#### Scenario: Reporte con datos completos muestra todas las métricas
- **WHEN** se consulta reporte rápido para materia M con 30 alumnos, 5 actividades, umbral 60%
- **AND** 20 alumnos tienen todas las actividades aprobadas
- **THEN** la respuesta incluye: total_alumnos=30, total_actividades=5, alumnos_aprobados=20, alumnos_atrasados=10, promedio_general (float)

#### Scenario: Reporte sin calificaciones devuelve métricas en cero
- **WHEN** se consulta reporte rápido para materia M sin calificaciones importadas
- **THEN** la respuesta incluye total_alumnos (cantidad en padrón activo) y las demás métricas en 0

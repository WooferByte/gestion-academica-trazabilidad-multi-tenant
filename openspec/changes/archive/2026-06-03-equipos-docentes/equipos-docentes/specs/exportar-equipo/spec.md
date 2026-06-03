## ADDED Requirements

### Requirement: COORDINADOR/ADMIN puede exportar equipo docente a CSV
El sistema SHALL exponer un endpoint `GET /api/v1/equipos/exportar` que genera un archivo CSV descargable con las asignaciones de un equipo filtrado por materia, carrera y/o cohorte. Solo accesible con permiso `equipos:asignar`.

#### Scenario: Exportación exitosa con CSV
- **WHEN** un usuario con permiso `equipos:asignar` envía GET a `/api/v1/equipos/exportar?materia_id=<id>&carrera_id=<id>&cohorte_id=<id>`
- **THEN** el sistema retorna 200 con `Content-Type: text/csv` y un archivo que incluye columnas: docente, rol, materia, carrera, cohorte, comisiones, desde, hasta

#### Scenario: Exportación sin filtros retorna todo el tenant
- **WHEN** un usuario con permiso `equipos:asignar` envía GET a `/api/v1/equipos/exportar` sin filtros
- **THEN** el sistema retorna CSV con todas las asignaciones del tenant

#### Scenario: Exportación sin resultados
- **WHEN** ningún registro coincide con los filtros
- **THEN** el sistema retorna CSV con solo los encabezados (sin filas de datos)

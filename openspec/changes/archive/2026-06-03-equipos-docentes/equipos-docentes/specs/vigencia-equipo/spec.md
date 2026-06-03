## ADDED Requirements

### Requirement: COORDINADOR/ADMIN puede modificar vigencia de todo un equipo en bloque
El sistema SHALL exponer un endpoint `PATCH /api/v1/equipos/vigencia` que actualiza los campos `desde` y/o `hasta` de todas las asignaciones de un equipo (materia × carrera × cohorte). Solo accesible con permiso `equipos:asignar`.

#### Scenario: Modificación de vigencia exitosa
- **WHEN** un usuario con permiso `equipos:asignar` envía PATCH a `/api/v1/equipos/vigencia` con `materia_id, carrera_id, cohorte_id, desde, hasta`
- **THEN** el sistema actualiza todas las asignaciones del equipo con las nuevas fechas y retorna 200 con la cantidad de asignaciones afectadas

#### Scenario: Modificación parcial (solo desde o solo hasta)
- **WHEN** el request incluye solo `desde` (sin `hasta`)
- **THEN** el sistema actualiza únicamente el campo `desde` de todas las asignaciones del equipo

#### Scenario: Equipo sin asignaciones recibe 404
- **WHEN** no existen asignaciones para la combinación materia × carrera × cohorte indicada
- **THEN** el sistema retorna 404 Not Found

#### Scenario: Modificación de vigencia genera auditoría
- **WHEN** la operación se completa exitosamente
- **THEN** el sistema registra un evento de auditoría con código `ASIGNACION_MODIFICAR`

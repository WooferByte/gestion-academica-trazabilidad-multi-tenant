## ADDED Requirements

### Requirement: COORDINADOR/ADMIN puede asignar múltiples docentes en bloque
El sistema SHALL exponer un endpoint `POST /api/v1/equipos/asignacion-masiva` que crea N asignaciones en una sola transacción atómica. Solo accesible con permiso `equipos:asignar`.

#### Scenario: Asignación masiva exitosa
- **WHEN** un usuario con permiso `equipos:asignar` envía POST a `/api/v1/equipos/asignacion-masiva` con un body que incluye `usuario_ids: [...], materia_id, carrera_id, cohorte_id, rol, desde, hasta`
- **THEN** el sistema crea todas las asignaciones en una transacción y retorna 201 con la lista de `AsignacionResponse`

#### Scenario: Asignación masiva parcial falla y se revierte todo
- **WHEN** el request incluye un `usuario_id` que no existe en el tenant
- **THEN** el sistema retorna 422 y NO se persiste ninguna asignación

#### Scenario: Usuario sin permiso recibe 403
- **WHEN** un usuario sin `equipos:asignar` envía POST a `/api/v1/equipos/asignacion-masiva`
- **THEN** el sistema retorna 403 Forbidden

#### Scenario: Asignación masiva genera auditoría
- **WHEN** la operación se completa exitosamente
- **THEN** el sistema registra un evento de auditoría con código `ASIGNACION_MODIFICAR` y metadata de la operación

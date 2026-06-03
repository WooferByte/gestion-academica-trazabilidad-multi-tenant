## ADDED Requirements

### Requirement: Coordinador asigna rol a usuario en contexto académico
El sistema SHALL permitir crear una asignación que vincule un usuario con un rol dentro de un contexto académico (materia, carrera, cohorte) con vigencia temporal.

#### Scenario: Asignación exitosa con todos los contextos
- **WHEN** un COORDINADOR envía POST /api/asignaciones con usuario_id, rol=PROFESOR, materia_id, carrera_id, cohorte_id, comisiones=["A","B"], desde=2026-01-01, hasta=2026-12-31, responsable_id
- **THEN** el sistema crea la asignación y retorna 201

#### Scenario: Asignación sin contexto (rol global)
- **WHEN** un ADMIN crea una asignación con rol=ADMIN y materia_id, carrera_id, cohorte_id todos nulos
- **THEN** el sistema crea la asignación global

#### Scenario: Asignación sin responsable
- **WHEN** se crea una asignación sin responsable_id
- **THEN** el sistema permite la creación (responsable_id es nullable)

#### Scenario: Usuario sin permiso
- **WHEN** un usuario sin `equipos:asignar` intenta crear una asignación
- **THEN** el sistema rechaza con 403 Forbidden

### Requirement: Asignación vencida no otorga permisos
El sistema SHALL derivar el estado de vigencia a partir de las fechas `desde`/`hasta`.

#### Scenario: Asignación vigente
- **WHEN** la fecha actual está dentro del rango [desde, hasta] de la asignación
- **THEN** el sistema considera la asignación como vigente

#### Scenario: Asignación vencida
- **WHEN** la fecha actual es posterior a `hasta` de la asignación
- **THEN** el sistema considera la asignación como vencida y NO otorga permisos

#### Scenario: Asignación vencida se conserva en histórico
- **WHEN** una asignación está vencida
- **THEN** el registro NO se elimina; permanece visible en consultas históricas

### Requirement: Fecha hasta opcional
El sistema SHALL permitir asignaciones sin fecha de fin (vigencia abierta).

#### Scenario: Vigencia abierta
- **WHEN** una asignación se crea con hasta=nulo
- **THEN** la asignación se considera vigente sin límite de fecha

### Requirement: Un usuario puede tener múltiples asignaciones
El sistema SHALL permitir que un usuario tenga varios roles y contextos simultáneamente.

#### Scenario: Multi-rol
- **WHEN** un usuario tiene asignaciones como PROFESOR en materia A y COORDINADOR en materia B
- **THEN** ambas asignaciones coexisten y otorgan permisos según su vigencia

### Requirement: Jerarquía por responsable_id
El sistema SHALL modelar la jerarquía docente mediante responsable_id.

#### Scenario: Asignación con responsable
- **WHEN** se consulta una asignación
- **THEN** la respuesta incluye responsable_id que referencia al usuario supervisor

### Requirement: Coordinador consulta asignaciones
El sistema SHALL listar asignaciones con filtros por materia, carrera, cohorte, usuario, rol y responsable.

#### Scenario: Listado filtrado
- **WHEN** un COORDINADOR envía GET /api/asignaciones?materia_id=X&rol=PROFESOR
- **THEN** el sistema retorna las asignaciones que coinciden con los filtros

#### Scenario: Solo asignaciones del tenant
- **WHEN** se listan asignaciones
- **THEN** el sistema filtra automáticamente por tenant_id del usuario autenticado

### Requirement: Coordinador edita asignación
El sistema SHALL permitir modificar campos de una asignación existente.

#### Scenario: Cambio de fechas de vigencia
- **WHEN** un COORDINADOR envía PATCH /api/asignaciones/{id} con nuevo desde/hasta
- **THEN** el sistema actualiza las fechas y retorna la asignación actualizada

### Requirement: Coordinador elimina asignación (soft delete)
El sistema SHALL permitir eliminar lógicamente una asignación.

#### Scenario: Soft delete
- **WHEN** un COORDINADOR envía DELETE /api/asignaciones/{id}
- **THEN** el sistema marca la asignación como eliminada (deleted_at seteado) sin borrado físico

### Requirement: Aislamiento multi-tenant en asignaciones
El sistema SHALL garantizar que un usuario del tenant A no vea ni modifique asignaciones del tenant B.

#### Scenario: Consulta entre tenants
- **WHEN** un usuario del tenant A consulta asignaciones
- **THEN** el sistema solo retorna asignaciones con tenant_id = A

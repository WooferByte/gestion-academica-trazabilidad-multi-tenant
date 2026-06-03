## ADDED Requirements

### Requirement: Publicación de avisos

El sistema SHALL permitir a usuarios con permiso `avisos:publicar` crear, leer, actualizar y desactivar avisos del sistema.

El aviso SHALL contener: título, cuerpo (rich text), alcance (Global/PorMateria/PorCohorte/PorRol), materia_id (nullable), cohorte_id (nullable), rol_destino (nullable), severidad (Info/Advertencia/Crítico), inicio_vigencia, fin_vigencia, orden, activo, requiere_ack.

El permiso `avisos:publicar` SHALL estar asignado a los roles COORDINADOR y ADMIN.

#### Scenario: Creación exitosa de aviso global

- **WHEN** un COORDINADOR envía POST `/api/v1/avisos` con datos válidos (alcance=Global, título, cuerpo, severidad, vigencia, orden, requiere_ack=true)
- **THEN** el sistema retorna 201 con el aviso creado
- **AND** el aviso tiene `activo=true`, `tenant_id` igual al del usuario autenticado

#### Scenario: Creación de aviso con alcance PorMateria

- **WHEN** un ADMIN envía POST `/api/v1/avisos` con alcance=PorMateria y materia_id válido
- **THEN** el sistema retorna 201
- **AND** el aviso creado tiene materia_id asignado y cohorte_id=null

#### Scenario: Creación de aviso con alcance PorCohorte

- **WHEN** un ADMIN envía POST `/api/v1/avisos` con alcance=PorCohorte y cohorte_id válido
- **THEN** el sistema retorna 201
- **AND** el aviso creado tiene cohorte_id asignado y materia_id=null

#### Scenario: Rechazo por permiso insuficiente

- **WHEN** un TUTOR sin permiso `avisos:publicar` envía POST `/api/v1/avisos`
- **THEN** el sistema retorna 403 Forbidden

#### Scenario: Desactivación de aviso

- **WHEN** un COORDINADOR envía PATCH `/api/v1/avisos/{id}` con `activo=false`
- **THEN** el sistema retorna 200
- **AND** el aviso deja de aparecer en consultas de visualización

#### Scenario: Rechazo por schema inválido (campo extra)

- **WHEN** un COORDINADOR envía POST `/api/v1/avisos` con un campo no declarado en el schema
- **THEN** el sistema retorna 422 Unprocessable Entity
- **AND** el error indica que el campo extra no está permitido

### Requirement: Visualización de avisos por destinatario

El sistema SHALL mostrar a cada usuario únicamente los avisos cuyo alcance coincida con su perfil, según RN-20.

El sistema SHALL filtrar avisos cuya ventana de vigencia incluya el momento actual (`inicio_vigencia <= now() AND fin_vigencia >= now()`), según RN-18.

El sistema SHALL ordenar los avisos por `orden` ASC, luego `inicio_vigencia` DESC.

El sistema SHALL incluir en la respuesta los campos calculados `total_acks` (cantidad de confirmaciones) y `user_acked` (bool, si el usuario confirmó).

#### Scenario: Usuario ve avisos Global

- **WHEN** un ALUMNO solicita GET `/api/v1/avisos`
- **THEN** la respuesta incluye todos los avisos con alcance=Global activos y dentro de vigencia

#### Scenario: Filtro por rol destino

- **WHEN** un ALUMNO solicita GET `/api/v1/avisos`
- **THEN** la respuesta NO incluye avisos con `rol_destino=PROFESOR` (rol diferente al del usuario)

#### Scenario: Filtro por cohorte

- **WHEN** un ALUMNO de la cohorte "2025-A" solicita GET `/api/v1/avisos`
- **THEN** la respuesta incluye avisos con alcance=PorCohorte y cohorte_id="2025-A"
- **AND** NO incluye avisos con alcance=PorCohorte y cohorte_id="2025-B"

#### Scenario: Filtro por materia

- **WHEN** un ALUMNO inscripto en "Matemática" solicita GET `/api/v1/avisos`
- **THEN** la respuesta incluye avisos con alcance=PorMateria y materia_id="Matemática"

#### Scenario: Aviso fuera de vigencia no se muestra

- **WHEN** la hora actual es posterior a `fin_vigencia` de un aviso
- **THEN** GET `/api/v1/avisos` NO incluye ese aviso
- **AND** GET `/api/v1/avisos/{id}` retorna 404 para ese aviso

#### Scenario: Orden por prioridad

- **WHEN** existen dos avisos con `orden=1` y `orden=2`
- **THEN** la respuesta los presenta con `orden=1` primero

### Requirement: Confirmación de lectura (acknowledgment)

El sistema SHALL permitir a cualquier usuario confirmar la lectura de un aviso mediante POST `/api/v1/avisos/{id}/ack`.

Si el aviso tiene `requiere_ack=true`, el sistema SHALL crear un registro en `AcknowledgmentAviso` con `aviso_id`, `usuario_id` y `confirmado_at`.

Si el usuario ya confirmó el aviso, el sistema SHALL retornar 409 Conflict (idempotencia del lado del cliente vía verificación previa con `user_acked`).

El sistema SHALL calcular `total_acks` como COUNT de registros en `AcknowledgmentAviso` agrupados por `aviso_id`.

#### Scenario: Confirmación exitosa

- **WHEN** un ALUMNO envía POST `/api/v1/avisos/{id}/ack` para un aviso que no ha confirmado
- **THEN** el sistema retorna 201
- **AND** se crea un registro en `AcknowledgmentAviso` con `usuario_id` del alumno

#### Scenario: Confirmación duplicada

- **WHEN** un ALUMNO envía POST `/api/v1/avisos/{id}/ack` para un aviso que ya confirmó
- **THEN** el sistema retorna 409 Conflict

#### Scenario: Contador refleja confirmaciones

- **WHEN** 3 usuarios distintos confirman el mismo aviso
- **THEN** GET `/api/v1/avisos/{id}` retorna `total_acks=3`

### Requirement: Multi-tenancy en avisos

Cada aviso SHALL pertenecer exactamente a un tenant, identificado por `tenant_id`.

Las consultas de visualización SHALL filtrar siempre por `tenant_id` del usuario autenticado.

Los usuarios de un tenant NO SHALL ver avisos de otros tenants.

#### Scenario: Aislamiento entre tenants

- **WHEN** un usuario del Tenant-A solicita GET `/api/v1/avisos`
- **THEN** la respuesta solo contiene avisos con `tenant_id` del Tenant-A
- **AND** NO incluye avisos del Tenant-B

### Requirement: Soft delete en avisos

El sistema SHALL usar borrado lógico en `Aviso` mediante el campo `deleted_at` (mixin existente).

Los avisos con `deleted_at IS NOT NULL` NO SHALL aparecer en ninguna consulta de visualización.

`AcknowledgmentAviso` SHALL ser append-only: no se elimina ni modifica.

#### Scenario: Soft delete no mostra aviso eliminado

- **WHEN** un COORDINADOR elimina un aviso (soft delete)
- **THEN** GET `/api/v1/avisos` no incluye ese aviso
- **AND** GET `/api/v1/avisos/{id}` retorna 404

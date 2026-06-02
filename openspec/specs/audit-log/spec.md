## ADDED Requirements

### Requirement: AuditLog append-only model
El sistema SHALL mantener una tabla `audit_log` de solo inserción (append-only) sin update ni delete a nivel aplicación y base de datos.

#### Scenario: Create audit entry
- **WHEN** un usuario autenticado realiza una acción registrable
- **THEN** el sistema SHALL insertar una fila en `audit_log` con `id`, `tenant_id`, `fecha_hora`, `actor_id`, `accion`, `detalle`, `filas_afectadas`, `ip`, `user_agent`
- **AND** la fila SHALL tener `impersonado_id=NULL`

#### Scenario: Append-only constraint at model level
- **WHEN** se intenta llamar a un método `update` sobre una instancia de `AuditLog`
- **THEN** el sistema SHALL rechazar la operación con error
- **AND** NO SHALL existir método `update`, `delete` ni `soft_delete` expuesto públicamente en el repositorio

#### Scenario: Append-only constraint at DB level
- **WHEN** se ejecuta un `UPDATE` o `DELETE` directo contra la tabla `audit_log`
- **THEN** PostgreSQL SHALL rechazar la operación
- **AND** el esquema SHALL usar una política o trigger `block_update_delete` (o simplemente no conceder permisos de UPDATE/DELETE)

### Requirement: Audit log fields
La tabla `audit_log` SHALL tener los siguientes campos:
- `id: UUID` PK
- `tenant_id: UUID` FK → tenants, NOT NULL
- `fecha_hora: timestamp with time zone`, NOT NULL
- `actor_id: UUID` FK → users, NOT NULL (quien ejecutó la acción)
- `impersonado_id: UUID` FK → users, NULL (a quién se impersonaba, si aplica)
- `materia_id: UUID` FK → materias, NULL
- `accion: varchar(100)` NOT NULL — código estandarizado
- `detalle: JSONB` NULL — contexto adicional
- `filas_afectadas: integer` NOT NULL DEFAULT 0
- `ip: varchar(45)` NOT NULL — IPv4 o IPv6
- `user_agent: varchar(500)` NOT NULL

#### Scenario: Insert with all fields
- **WHEN** se registra una importación de calificaciones
- **THEN** el registro SHALL contener `accion="CALIFICACIONES_IMPORTAR"`, `detalle={"origen": "moodle", "comision": "A"}`, `filas_afectadas=30`, `ip="192.168.1.1"`, `user_agent="Mozilla/5.0..."`

#### Scenario: Insert with minimum fields
- **WHEN** se registra una acción sin detalle ni materia asociada
- **THEN** el registro SHALL contener `detalle=NULL`, `materia_id=NULL`, `filas_afectadas=0`

### Requirement: Standardized action codes
El sistema SHALL definir un catálogo inicial de códigos de acción en `app/core/audit_codes.py` como constantes tipadas.

#### Scenario: Catalog contains impersonation codes
- **WHEN** el módulo `audit_codes` es importado
- **THEN** SHALL contener `IMPERSONACION_INICIAR`, `IMPERSONACION_FINALIZAR`, `CALIFICACIONES_IMPORTAR`, `PADRON_CARGAR`, `COMUNICACION_ENVIAR`, `ASIGNACION_MODIFICAR`, `LIQUIDACION_CERRAR`

### Requirement: AuditService dependency
El sistema SHALL proveer una dependency FastAPI `AuditService` que reciba `UserContext` y `AsyncSession` y exponga un método `log(accion, detalle=None, filas_afectadas=0, materia_id=None)`.

#### Scenario: Register action via AuditService
- **WHEN** un endpoint inyecta `AuditService` y llama a `log("CALIFICACIONES_IMPORTAR", detalle={...}, filas_afectadas=30)`
- **THEN** el sistema SHALL insertar un registro en `audit_log` con los datos proporcionados
- **AND** el `actor_id` SHALL ser el `user_id` del `UserContext` actual
- **AND** el `tenant_id` SHALL ser el del `UserContext` actual
- **AND** la IP y user-agent SHALL extraerse del request actual

#### Scenario: Audit under impersonation
- **WHEN** un endpoint registra una acción bajo impersonación
- **THEN** el `actor_id` SHALL ser el impersonador (user_id del UserContext)
- **AND** `impersonado_id` SHALL ser el usuario impersonado
- **AND** el `UserContext.impersonator_id` NO SHALL ser NULL

### Requirement: Migration 004
El sistema SHALL incluir una migración Alembic 004 que cree la tabla `audit_log`.

#### Scenario: Migration creates table
- **WHEN** la migración 004 se ejecuta
- **THEN** la tabla `audit_log` SHALL existir con todos los campos especificados
- **AND** SHALL tener FK a `tenants(id)`, `users(id)` (actor_id), `users(id)` (impersonado_id)

#### Scenario: Rollback drops table
- **WHEN** la migración 004 se revierte
- **THEN** la tabla `audit_log` SHALL ser eliminada

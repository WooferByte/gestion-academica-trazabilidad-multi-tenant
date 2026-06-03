## ADDED Requirements

### Requirement: Admin crea usuario del tenant
El sistema SHALL permitir a un usuario con permiso `usuarios:gestionar` crear un nuevo usuario en su tenant.

#### Scenario: Creación exitosa
- **WHEN** un ADMIN envía POST /api/admin/usuarios con nombre, apellidos, email, dni, cuil, cbu, alias_cbu, banco, regional, legajo, facturador, estado
- **THEN** el sistema crea el usuario, cifra los campos PII con AES-256-GCM, y retorna el usuario creado (sin exponer PII en texto plano)

#### Scenario: Email duplicado en el mismo tenant
- **WHEN** un ADMIN intenta crear un usuario con un email ya existente en su tenant
- **THEN** el sistema rechaza con 409 Conflict indicando unicidad violada

#### Scenario: Email duplicado en distinto tenant
- **WHEN** un ADMIN del tenant A crea un usuario con email que ya existe en el tenant B
- **THEN** el sistema permite la creación (la unicidad es por tenant)

#### Scenario: Usuario sin permiso
- **WHEN** un usuario sin `usuarios:gestionar` intenta crear un usuario
- **THEN** el sistema rechaza con 403 Forbidden

#### Scenario: Roles no se asignan en creación de usuario
- **WHEN** se crea un usuario mediante /api/admin/usuarios
- **THEN** el endpoint NO acepta roles; estos se gestionan exclusivamente vía Asignacion

### Requirement: Admin edita usuario del tenant
El sistema SHALL permitir modificar los datos de un usuario existente.

#### Scenario: Edición exitosa de campos editables
- **WHEN** un ADMIN envía PATCH /api/admin/usuarios/{id} con nombre, apellidos, banco, regional, legajo
- **THEN** el sistema actualiza los campos y retorna el usuario actualizado

#### Scenario: Legajo se trata como atributo de negocio
- **WHEN** se consulta un usuario
- **THEN** el campo legajo se expone en las respuestas (a diferencia de otros PII que se ocultan por defecto)

### Requirement: Admin lista usuarios del tenant
El sistema SHALL listar usuarios del tenant con paginación y filtros.

#### Scenario: Listado paginado
- **WHEN** un ADMIN envía GET /api/admin/usuarios?limit=20&offset=0
- **THEN** el sistema retorna una lista paginada de usuarios sin campos PII en texto plano

#### Scenario: Filtro por estado
- **WHEN** un ADMIN envía GET /api/admin/usuarios?estado=Activo
- **THEN** el sistema retorna solo usuarios activos

### Requirement: Admin desactiva usuario
El sistema SHALL permitir desactivar un usuario (soft delete / cambio de estado).

#### Scenario: Desactivación exitosa
- **WHEN** un ADMIN envía DELETE /api/admin/usuarios/{id}
- **THEN** el sistema marca el usuario como inactivo (no hard delete) y retorna 200

### Requirement: PII cifrada no se expone
El sistema SHALL garantizar que los campos marcados como cifrados nunca se expongan en texto plano en respuestas API, logs ni errores.

#### Scenario: Respuesta API sin PII
- **WHEN** se consulta un usuario mediante GET /api/admin/usuarios/{id}
- **THEN** la respuesta NO incluye los campos cifrados (cuil_cifrado, cbu_cifrado, alias_cbu_cifrado, email, dni_cifrado) en texto plano; se exponen solo como indicadores de presencia (booleanos) o se omiten

#### Scenario: Logs sin PII
- **WHEN** el sistema registra una operación sobre usuarios en el audit log
- **THEN** el detalle JSON no incluye valores de campos cifrados

### Requirement: Unicidad (tenant_id, email)
El sistema SHALL enforce la unicidad del par (tenant_id, email) a nivel de base de datos.

#### Scenario: Constraint de DB
- **WHEN** se intenta insertar un email duplicado dentro del mismo tenant
- **THEN** la base de datos rechaza la operación por violación de unique constraint

### Requirement: Legajo es atributo de negocio, no credencial
El sistema SHALL tratar el legajo como un campo informativo sin implicaciones de autenticación ni autorización.

#### Scenario: Legajo no autentica
- **WHEN** un usuario intenta autenticarse con su legajo en lugar de email
- **THEN** el sistema rechaza el login (solo email es credencial)

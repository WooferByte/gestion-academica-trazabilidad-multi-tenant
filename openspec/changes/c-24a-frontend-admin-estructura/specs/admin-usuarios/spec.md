## ADDED Requirements

### Requirement: Admin visualiza y administra usuarios del tenant
El sistema SHALL proveer una interfaz frontend para que usuarios con permiso `usuarios:gestionar` administren los usuarios del tenant, consumiendo la API de C-07. Los campos PII (dni, cuil, cbu, alias_cbu) se envían en creación/edición pero NUNCA se muestran en texto plano al consultar.

#### Scenario: Listar usuarios con paginación y filtro
- **WHEN** un ADMIN navega a `/admin/usuarios`
- **THEN** el sistema SHALL mostrar una tabla paginada con todos los usuarios del tenant
- **AND** cada fila SHALL contener: nombre completo, email (oculto parcialmente si es PII), legajo, rol, estado, y acciones
- **AND** SHALL existir un filtro por estado (activo/inactivo/todos)

#### Scenario: Crear usuario
- **WHEN** un ADMIN hace click en "Nuevo Usuario"
- **THEN** el sistema SHALL abrir un modal con formulario completo: nombre, apellidos, email, dni, cuil, banco, cbu, alias_cbu, regional, legajo, facturador, estado
- **AND** SHALL enviar POST a `/api/admin/usuarios`
- **AND** SHALL validar email duplicado (mostrar error 409 si existe)

#### Scenario: Editar usuario sin exponer PII
- **WHEN** un ADMIN edita un usuario existente
- **THEN** el formulario SHALL mostrar los campos editables (nombre, apellidos, banco, regional, legajo, estado) con sus valores actuales
- **AND** los campos PII (dni, cuil, cbu, alias_cbu) SHALL aparecer vacíos o con indicador de "dato cifrado — solo se muestra si se reingresa"
- **AND** SHALL enviar PATCH a `/api/admin/usuarios/{id}` solo con los campos modificados

#### Scenario: Desactivar usuario
- **WHEN** un ADMIN hace click en "Desactivar"
- **THEN** el sistema SHALL mostrar un diálogo de confirmación
- **AND** SHALL enviar DELETE a `/api/admin/usuarios/{id}`
- **AND** SHALL refrescar la tabla

#### Scenario: Asignación de roles no se hace desde este módulo
- **WHEN** un ADMIN visualiza un usuario
- **THEN** el sistema SHALL mostrar el rol actual del usuario si está disponible
- **AND** NO SHALL incluir un selector de roles en el formulario de creación/edición (roles se gestionan vía Asignación en C-08)

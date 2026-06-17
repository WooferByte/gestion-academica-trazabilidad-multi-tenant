## ADDED Requirements

### Requirement: Admin visualiza y administra materias
El sistema SHALL proveer una interfaz frontend para que usuarios con permiso `estructura:gestionar` administren el catálogo de materias del tenant, consumiendo la API de C-06.

#### Scenario: Listar materias con paginación
- **WHEN** un ADMIN navega a `/admin/materias`
- **THEN** el sistema SHALL mostrar una tabla paginada con todas las materias del tenant
- **AND** cada fila SHALL contener: código, nombre, estado, y acciones

#### Scenario: Crear materia
- **WHEN** un ADMIN hace click en "Nueva Materia"
- **THEN** el sistema SHALL abrir un modal con código y nombre
- **AND** SHALL enviar POST a `/api/v1/admin/materias`
- **AND** SHALL validar unicidad de código (mostrar error 409 si duplicado)

#### Scenario: Editar materia
- **WHEN** un ADMIN hace click en "Editar"
- **THEN** el sistema SHALL abrir el modal con datos precargados
- **AND** SHALL permitir modificar código y nombre

#### Scenario: Cambiar estado de materia
- **WHEN** un ADMIN cambia el estado de una materia
- **THEN** el sistema SHALL enviar PUT con el nuevo estado
- **AND** SHALL refrescar la tabla

#### Scenario: Soft delete materia
- **WHEN** un ADMIN hace click en "Eliminar"
- **THEN** el sistema SHALL mostrar confirmación y enviar DELETE
- **AND** SHALL refrescar la tabla

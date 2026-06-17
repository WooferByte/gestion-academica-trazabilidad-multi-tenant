## ADDED Requirements

### Requirement: Admin visualiza y administra carreras
El sistema SHALL proveer una interfaz frontend para que usuarios con permiso `estructura:gestionar` administren las carreras del tenant, consumiendo la API de C-06.

#### Scenario: Listar carreras con paginación
- **WHEN** un ADMIN navega a `/admin/carreras`
- **THEN** el sistema SHALL mostrar una tabla paginada con todas las carreras del tenant
- **AND** cada fila SHALL contener: código, nombre, estado (activo/inactivo como Badge), y acciones (editar, cambiar estado, eliminar)
- **AND** la tabla SHALL usar TanStack Query con loading skeleton y empty state

#### Scenario: Crear carrera
- **WHEN** un ADMIN hace click en "Nueva Carrera" y completa el formulario con código y nombre
- **THEN** el sistema SHALL enviar POST a `/api/v1/admin/carreras` con los datos
- **AND** SHALL mostrar un toast de éxito al crear
- **AND** SHALL refrescar la tabla automáticamente

#### Scenario: Validar código duplicado en creación
- **WHEN** un ADMIN ingresa un código que ya existe en el tenant
- **THEN** el sistema SHALL mostrar el error 409 del backend como un mensaje en el formulario
- **AND** NO SHALL cerrar el modal

#### Scenario: Editar carrera
- **WHEN** un ADMIN hace click en "Editar" en una fila
- **THEN** el sistema SHALL abrir un modal con el formulario precargado con los datos actuales
- **AND** SHALL permitir modificar nombre, código y estado
- **AND** SHALL enviar PUT a `/api/v1/admin/carreras/{id}` al confirmar

#### Scenario: Cambiar estado de carrera
- **WHEN** un ADMIN hace click en "Inactivar" en una carrera activa
- **THEN** el sistema SHALL mostrar un diálogo de confirmación
- **AND** si la carrera tiene cohortes abiertas, SHALL mostrar el error 422 del backend sin cambiar el estado
- **AND** si no tiene cohortes abiertas, SHALL cambiar el estado y refrescar la tabla

#### Scenario: Soft delete carrera
- **WHEN** un ADMIN hace click en "Eliminar"
- **THEN** el sistema SHALL mostrar un diálogo de confirmación con advertencia
- **AND** SHALL enviar DELETE a `/api/v1/admin/carreras/{id}`
- **AND** SHALL refrescar la tabla y mostrar toast de éxito

#### Scenario: Acceso sin permiso
- **WHEN** un usuario sin `estructura:gestionar` intenta acceder a `/admin/carreras`
- **THEN** el sistema SHALL redirigir al dashboard con un toast de error (403)

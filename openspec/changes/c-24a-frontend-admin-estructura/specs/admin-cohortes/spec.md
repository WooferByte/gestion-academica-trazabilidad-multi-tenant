## ADDED Requirements

### Requirement: Admin visualiza y administra cohortes
El sistema SHALL proveer una interfaz frontend para que usuarios con permiso `estructura:gestionar` administren las cohortes del tenant, vinculadas a una carrera, consumiendo la API de C-06.

#### Scenario: Listar cohortes con paginación y filtro
- **WHEN** un ADMIN navega a `/admin/cohortes`
- **THEN** el sistema SHALL mostrar una tabla paginada con todas las cohortes del tenant
- **AND** cada fila SHALL contener: nombre, carrera asociada, año, vigencia (desde/hasta), estado, y acciones
- **AND** SHALL existir un filtro por carrera (Select que carga carreras activas)

#### Scenario: Crear cohorte
- **WHEN** un ADMIN hace click en "Nueva Cohorte"
- **THEN** el sistema SHALL abrir un modal con formulario que incluye: selector de carrera (cargado async desde API), nombre, año, vigencia desde y vigencia hasta
- **AND** SHALL enviar POST a `/api/v1/admin/cohortes`
- **AND** SHALL validar que la carrera seleccionada esté activa (si la API responde 422, mostrar error)

#### Scenario: Validar nombre duplicado en misma carrera
- **WHEN** un ADMIN crea una cohorte con nombre ya existente para la misma carrera
- **THEN** el sistema SHALL mostrar el error 409 del backend

#### Scenario: Editar cohorte
- **WHEN** un ADMIN hace click en "Editar" en una fila
- **THEN** el sistema SHALL abrir un modal con el formulario precargado
- **AND** SHALL permitir modificar nombre, año, vigencia y estado

#### Scenario: Soft delete cohorte
- **WHEN** un ADMIN hace click en "Eliminar"
- **THEN** el sistema SHALL mostrar confirmación y enviar DELETE
- **AND** SHALL refrescar la tabla

#### Scenario: Filtro por carrera en listado
- **WHEN** un ADMIN selecciona una carrera en el filtro
- **THEN** el sistema SHALL recargar la tabla mostrando solo cohortes de esa carrera

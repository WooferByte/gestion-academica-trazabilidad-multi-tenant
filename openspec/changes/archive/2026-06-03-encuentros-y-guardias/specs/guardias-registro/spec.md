## ADDED Requirements

### Requirement: Registrar guardia (F6.6)
El sistema SHALL exponer `POST /api/v1/guardias` para que un TUTOR registre una guardia. Solo accesible con permiso `encuentros:gestionar`. Requiere: `asignacion_id`, `materia_id`, `carrera_id`, `cohorte_id`, `dia`, `horario`, `comentarios` (opcional). Estado inicial: `Pendiente`.

#### Scenario: Tutor registra guardia exitosamente
- **WHEN** TUTOR envía POST con datos válidos de guardia
- **THEN** el sistema SHALL crear el registro con estado Pendiente y `creada_at` con timestamp actual

#### Scenario: Guardia con datos faltantes retorna 422
- **WHEN** se omite `asignacion_id` o `materia_id`
- **THEN** el sistema SHALL retornar 422 con errores de validación

### Requirement: Consultar guardias del tenant
El sistema SHALL exponer `GET /api/v1/guardias` con filtros (`materia_id`, `carrera_id`, `cohorte_id`, `estado`, `desde`, `hasta`, `offset`, `limit`). Accesible con permiso `encuentros:gestionar`. COORDINADOR/ADMIN ve todas las guardias del tenant. TUTOR ve solo sus propias guardias.

#### Scenario: Coordinador consulta todas las guardias
- **WHEN** COORDINADOR consulta GET /api/v1/guardias sin filtros
- **THEN** el sistema SHALL retornar todas las guardias del tenant paginadas

#### Scenario: Tutor ve solo sus guardias
- **WHEN** TUTOR consulta GET /api/v1/guardias
- **THEN** el sistema SHALL filtrar por las asignaciones del tutor autenticado

#### Scenario: Filtrar guardias por estado
- **WHEN** se consulta con `estado=Realizada`
- **THEN** el sistema SHALL retornar solo las guardias en ese estado

### Requirement: Exportar guardias a CSV
El sistema SHALL exponer `GET /api/v1/guardias/export` con los mismos filtros que la consulta. Retorna archivo CSV con cabecera y filas de guardias.

#### Scenario: Exportar guardias filtradas
- **WHEN** se consulta `GET /api/v1/guardias/export?materia_id=X`
- **THEN** el sistema SHALL retornar un CSV descargable con Content-Type text/csv

#### Scenario: Exportar sin resultados retorna CSV con cabecera sola
- **WHEN** se consulta export con filtros que no matchean ninguna guardia
- **THEN** el sistema SHALL retornar un CSV con solo la fila de cabecera

### Requirement: Actualizar estado de guardia
El sistema SHALL exponer `PATCH /api/v1/guardias/{id}` para cambiar el estado de una guardia (Pendiente|Realizada|Cancelada) y opcionalmente agregar comentarios.

#### Scenario: Marcar guardia como Realizada
- **WHEN** se actualiza una guardia con `estado=Realizada`
- **THEN** el sistema SHALL persistir el cambio

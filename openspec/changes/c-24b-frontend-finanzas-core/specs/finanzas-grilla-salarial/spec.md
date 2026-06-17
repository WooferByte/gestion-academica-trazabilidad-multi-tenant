## ADDED Requirements

### Requirement: Listar salarios base
The system SHALL display a list of salary bases per role.

#### Scenario: Listar bases
- **WHEN** user navigates to `/finanzas/grilla` bases tab
- **THEN** system fetches GET `/api/v1/grilla-salarial/bases` returning `list[SalarioBaseResponse]` (bare array)
- **THEN** system renders a DataTable with id, rol, monto, desde, hasta fields

### Requirement: Crear salario base
The system SHALL allow creating a new salario base entry.

#### Scenario: Crear base exitoso
- **WHEN** user fills the create form with rol, monto, desde
- **THEN** system sends POST `/api/v1/grilla-salarial/bases` with `{ "rol", "monto", "desde" }`
- **THEN** system shows success toast and refreshes the list

### Requirement: Listar categorías plus
The system SHALL display categorías plus in a paginated table with `{ items, total }` response format.

#### Scenario: Listar categorías plus
- **WHEN** user navigates to `/finanzas/grilla` pluses tab
- **THEN** system fetches GET `/api/v1/admin/categorias-plus` returning `{ items: CategoriaPlusResponse[], total: number }`
- **THEN** system renders a DataTable with id, codigo, nombre, activo fields

### Requirement: Crear categoría plus
The system SHALL allow creating a new categoría plus.

#### Scenario: Crear categoría plus exitoso
- **WHEN** user fills the create form with codigo, nombre
- **THEN** system sends POST `/api/v1/admin/categorias-plus` with `{ "codigo", "nombre", "activo": true }`
- **THEN** system shows success toast and refreshes the list

### Requirement: Editar categoría plus
The system SHALL allow editing codigo, nombre, and activo of a categoría plus.

#### Scenario: Editar categoría plus exitoso
- **WHEN** user edits the form for an existing categoría
- **THEN** system sends PUT `/api/v1/admin/categorias-plus/{categoria_id}` with `{ "codigo"?, "nombre"?, "activo"? }`
- **THEN** system shows success toast and refreshes the list

### Requirement: Eliminar categoría plus
The system SHALL allow deleting a categoría plus, returning 204.

#### Scenario: Eliminar categoría plus exitoso
- **WHEN** user clicks "Eliminar" and confirms
- **THEN** system sends DELETE `/api/v1/admin/categorias-plus/{categoria_id}`
- **THEN** system shows success toast and refreshes the list

### Requirement: Toggle activo/inactivo de categoría plus
The system SHALL allow toggling the activo state of a categoría plus via PATCH.

#### Scenario: Toggle categoría plus
- **WHEN** user clicks toggle on a categoría
- **THEN** system sends PATCH `/api/v1/admin/categorias-plus/{categoria_id}/toggle`
- **THEN** system shows success toast and refreshes the list

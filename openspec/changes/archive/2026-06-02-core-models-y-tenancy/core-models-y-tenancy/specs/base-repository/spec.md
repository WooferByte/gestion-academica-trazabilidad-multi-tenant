## ADDED Requirements

### Requirement: Repository genérico con scope de tenant

El sistema SHALL proveer un `BaseRepository[T]` genérico que implemente CRUD básico y filtre TODAS las queries por `tenant_id` por defecto. El tenant se recibe como dependencia inyectada.

#### Scenario: get filtra por tenant_id

- **GIVEN** dos tenants A y B
- **AND** un registro con `id=X` perteneciente al tenant A
- **WHEN** se ejecuta `repository_a.get(X)`
- **THEN** retorna el registro
- **WHEN** se ejecuta `repository_b.get(X)`
- **THEN** retorna `None` (el registro no pertenece al tenant B)

#### Scenario: get_multi solo devuelve registros del tenant

- **GIVEN** el tenant A tiene 3 registros y el tenant B tiene 5
- **WHEN** se ejecuta `repository_a.get_multi()`
- **THEN** retorna 3 registros
- **AND** ningún registro pertenece al tenant B

#### Scenario: create asigna tenant_id automáticamente

- **GIVEN** un repository inicializado con `tenant_id = T`
- **WHEN** se ejecuta `create(payload)` sin especificar `tenant_id`
- **THEN** el registro se persiste con `tenant_id = T`

#### Scenario: update merge parcial

- **GIVEN** un registro con campos `{nombre: "Foo", codigo: "X"}`
- **WHEN** se ejecuta `update(db_obj, {"nombre": "Bar"})`
- **THEN** el registro actualizado tiene `nombre="Bar"` y `codigo="X"` (no se pierden campos no enviados)

#### Scenario: exists verifica existencia dentro del tenant

- **GIVEN** dos tenants A y B
- **AND** un registro con `codigo="MAT01"` en tenant A
- **WHEN** se ejecuta `repository_a.exists(codigo="MAT01")`
- **THEN** retorna `True`
- **WHEN** se ejecuta `repository_b.exists(codigo="MAT01")`
- **THEN** retorna `False`

#### Scenario: get_multi con paginación

- **GIVEN** 25 registros en el tenant
- **WHEN** se ejecuta `get_multi(skip=0, limit=10)`
- **THEN** retorna los primeros 10 registros
- **WHEN** se ejecuta `get_multi(skip=10, limit=10)`
- **THEN** retorna los siguientes 10 registros

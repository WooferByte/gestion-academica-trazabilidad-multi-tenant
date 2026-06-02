## ADDED Requirements

### Requirement: Soft delete en repository

El repository SHALL implementar eliminación lógica: setear `deleted_at` en lugar de borrado físico. Los métodos `get`, `get_multi`, `exists` SHALL excluir registros con `deleted_at IS NOT NULL`.

#### Scenario: Soft delete marca deleted_at

- **GIVEN** un registro existente sin `deleted_at`
- **WHEN** se ejecuta `soft_delete()` sobre él
- **THEN** el campo `deleted_at` se setea con el timestamp actual
- **AND** el registro persiste en la base de datos (no se borra físicamente)

#### Scenario: get no devuelve registro soft-deleteado

- **GIVEN** un registro que fue soft-deleteado
- **WHEN** se ejecuta `get(id)` con su UUID
- **THEN** retorna `None`

#### Scenario: get_multi excluye soft-deleteados

- **GIVEN** N registros, de los cuales M fueron soft-deleteados
- **WHEN** se ejecuta `get_multi()`
- **THEN** el resultado contiene solo N-M registros (los no eliminados)

#### Scenario: get_with_deleted incluye soft-deleteados

- **GIVEN** un registro soft-deleteado
- **WHEN** se ejecuta `get_with_deleted(id)`
- **THEN** retorna el registro (con `deleted_at` no nulo)

#### Scenario: Intentar operar sobre soft-deleteado lanza excepción

- **GIVEN** un registro soft-deleteado
- **WHEN** se intenta actualizarlo vía `update()`
- **THEN** el sistema rechaza la operación con `SoftDeletedException`

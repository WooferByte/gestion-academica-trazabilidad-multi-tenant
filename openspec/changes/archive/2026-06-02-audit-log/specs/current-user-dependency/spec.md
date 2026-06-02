## MODIFIED Requirements

### Requirement: UserContext DTO

El sistema SHALL proveer un DTO `UserContext` con `user_id` (UUID), `tenant_id` (UUID), `roles` (list[str]) e `impersonator_id` (UUID | None) para ser usado en Services y Repositories.

#### Scenario: UserContext disponible en capas inferiores

- **GIVEN** un usuario autenticado
- **WHEN** se ejecuta un service que recibe `UserContext` como dependencia
- **THEN** el service puede acceder a `user_id`, `tenant_id`, `roles` e `impersonator_id`
- **AND** el repository subyacente filtra por `tenant_id` automáticamente

#### Scenario: UserContext bajo impersonación

- **GIVEN** un usuario autenticado que inició una impersonación
- **WHEN** se ejecuta un service bajo esa sesión
- **THEN** `UserContext.user_id` SHALL ser el target impersonado
- **AND** `UserContext.impersonator_id` SHALL ser el actor real que impersona
- **AND** `UserContext.roles` SHALL ser los roles del target, no del actor

## ADDED Requirements

### Requirement: Resolvedor de tenant

El sistema SHALL proveer un mecanismo para resolver y propagar el tenant activo a través del flujo de request (Routers → Services → Repositories).

#### Scenario: Tenancy dependency provee tenant context

- **GIVEN** una request autenticada con tenant_id = T
- **WHEN** se inyecta la dependency `get_tenant()` en un router
- **THEN** el `TenantContext` recibido tiene `tenant_id = T`

#### Scenario: Repository recibe tenant de la dependency

- **GIVEN** un service que obtiene `TenantContext` vía DI
- **WHEN** instancia un repository
- **THEN** el repository se inicializa con el `tenant_id` del contexto
- **AND** todas las queries del repository filtran por ese `tenant_id`

#### Scenario: Service puede acceder al tenant activo

- **GIVEN** un service con `TenantContext` inyectado
- **WHEN** necesita el tenant_id del usuario actual
- **THEN** accede via `tenant_context.tenant_id`

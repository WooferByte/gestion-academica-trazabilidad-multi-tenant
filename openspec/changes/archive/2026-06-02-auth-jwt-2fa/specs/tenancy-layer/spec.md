## MODIFIED Requirements

### Requirement: Tenancy layer con resolución desde JWT

**Nota**: Este requirement modifica el creado en C-02 (`specs/tenancy-layer/spec.md`). La modificación cambia la fuente de verdad del `tenant_id`: ya no se recibe como parámetro explícito, sino que se resuelve automáticamente desde el JWT autenticado.

El sistema SHALL proveer un mecanismo que derive el `tenant_id` del JWT verificado y lo inyecte en todas las capas que necesiten scope de tenant. **El tenant nunca se obtiene de parámetros de request.**

#### Scenario: Tenant resuelto desde JWT

- **GIVEN** un JWT firmado con `tenant_id = UUID_T1`
- **WHEN** el usuario autenticado ejecuta cualquier operación en el sistema
- **THEN** el `tenant_id` disponible en `UserContext` es `UUID_T1`

#### Scenario: Tenant no suplantable por parámetro

- **GIVEN** un JWT con `tenant_id = UUID_T1`
- **WHEN** el request incluye un query param `tenant_id=UUID_T2` o body con `tenant_id=UUID_T2`
- **THEN** el `tenant_id` efectivo es `UUID_T1` (del JWT), ignorando el parámetro

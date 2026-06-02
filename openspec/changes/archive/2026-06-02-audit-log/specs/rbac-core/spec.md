## ADDED Requirements

### Requirement: Impersonation permission in seed
La migración 004 SHALL agregar el permiso `impersonacion:usar` al catálogo de permisos y asignarlo al rol `ADMIN`.

#### Scenario: Seed impersonacion:usar permission
- **WHEN** la migración 004 se ejecuta
- **THEN** el permiso `impersonacion:usar` SHALL existir en la tabla `permisos`
- **AND** el permiso SHALL tener `modulo="impersonacion"` y `accion="usar"`
- **AND** el rol `ADMIN` SHALL tener este permiso asociado en `rol_permiso`

#### Scenario: Other roles do not get impersonation
- **WHEN** la migración 004 se ejecuta
- **THEN** los roles `ALUMNO`, `TUTOR`, `PROFESOR`, `COORDINADOR`, `NEXO`, `FINANZAS` NO SHALL tener el permiso `impersonacion:usar`

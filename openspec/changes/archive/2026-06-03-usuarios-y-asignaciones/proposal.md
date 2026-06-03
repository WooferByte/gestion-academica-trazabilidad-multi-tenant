## Why

El sistema actual tiene un modelo `User` creado en C-03 con fines exclusivos de autenticación (email, password, roles, TOTP), pero carece del perfil completo de dominio que necesita una plataforma académica: datos fiscales (CUIL, CBU, alias bancario), legajos, regional, facturación y estado del usuario. Tampoco existe el concepto de `Asignacion` que vincule un usuario con un rol dentro de un contexto académico concreto (materia, carrera, cohorte) con vigencia temporal. Sin estos modelos no es posible gestionar equipos docentes (C-08), liquidar honorarios (C-18) ni controlar permisos contextuales. Este change completa el modelo de identidad de dominio y el eje central de autorización contextual del sistema.

## What Changes

- **Enriquecimiento del modelo `users`** (migración 006): se agregan campos PII cifrados (`cuil_cifrado`, `cbu_cifrado`, `alias_cbu_cifrado`), campos de perfil (`banco`, `regional`, `legajo`, `legajo_profesional`, `facturador`, `estado`). `email` pasa a cifrarse. `legajo` es atributo de negocio, no PK ni credencial.
- **Nuevo modelo `Asignacion`**: vincula Usuario ↔ Rol ↔ contexto académico (materia/carrera/cohorte/comisiones) con vigencia (`desde`, `hasta`), jerarquía (`responsable_id`) y estado derivado por fechas.
- **Nuevo permiso `usuarios:gestionar`**: ABM de usuarios del tenant para ADMIN.
- **Nuevo permiso `equipos:asignar`**: CRUD de asignaciones para COORDINADOR/ADMIN.
- **Endpoint `/api/admin/usuarios`**: ABM con PII cifrada en reposo, unicidad `(tenant_id, email)`.
- **Endpoint `/api/asignaciones`**: CRUD con validación de vigencia, contexto y jerarquía.
- **Unicidad `(tenant_id, email)`**: el email es único por tenant; se cifra en reposo.
- **ABC de relación User ↔ Usuario**: se unifica en una sola tabla `users`. El modelo User de C-03 se enriquece con los campos de E4. No hay dos identidades separadas.

## Capabilities

### New Capabilities
- `user-management`: ABM de usuarios del tenant con PII cifrada (AES-256-GCM), unicidad email, legajo como atributo de negocio, validación de campos sensibles no expuestos en respuestas/logs.
- `role-assignments`: CRUD de asignaciones usuario ↔ rol ↔ contexto académico, con vigencia temporal, jerarquía responsable, validación de vencidas, comisiones y contexto nullable.

### Modified Capabilities
- *(none — no existing specs are changing behavior)*

## Impact

- **Modelos**: `backend/app/models/user.py` se modifica (nuevos campos cifrados); se crea `backend/app/models/asignacion.py`.
- **API**: nuevo router `/api/admin/usuarios` y `/api/asignaciones`.
- **Migración**: `backend/alembic/versions/` → migración 006.
- **RBAC**: nuevos permisos en seed (`usuarios:gestionar`, `equipos:asignar`) mapeados a ADMIN y COORDINADOR según la matriz.
- **Seguridad**: PII cifrada (reutiliza `core/security.py`), emails cifrados, campos sensibles excluidos de respuestas API por defecto.
- **Dependencias**: necesita C-06 (Carrera, Cohorte, Materia) para las FKs contextuales de Asignacion.

## Context

Actualmente existe un modelo `User` (C-03, tabla `users`) con fines de autenticación: email, password_hash, nombre_cifrado, apellido_cifrado, dni_cifrado, roles (JSONB), totp_secret_cifrado, is_active. La KB define `Usuario` (E4) como la identidad base de dominio con campos adicionales (cuil, cbu, alias_cbu, banco, regional, legajo, etc.) y `Asignacion` (E5) como el vínculo usuario ↔ rol ↔ contexto académico.

C-06 ya creó Carrera, Cohorte, Materia (migración 005). C-07 necesita estas entidades para las FKs contextuales de Asignacion.

## Goals / Non-Goals

**Goals:**
- Unificar User + Usuario en una sola tabla (`users`), enriqueciéndola con los campos de E4 vía migración 006
- Crear modelo Asignacion con FKs a users, materia, carrera, cohorte y responsable
- ABM de usuarios con PII cifrada (AES-256-GCM) y unicidad (tenant_id, email)
- CRUD de asignaciones con vigencia temporal, jerarquía y aislamiento multi-tenant
- Nuevos permisos `usuarios:gestionar` y `equipos:asignar` en la matriz RBAC

**Non-Goals:**
- NO se modifica el flujo de autenticación (C-03) — el login sigue usando email + password
- NO se implementan features de equipo docente (C-08): asignación masiva, clonación, export
- NO se reemplaza el campo `roles` JSONB de User — coexiste con Asignacion; se mantiene para claims JWT rápidos

## Decisions

### D1: User y Usuario son la misma entidad
**Decisión**: Enriquecer la tabla `users` existente con los campos de E4 en lugar de crear una tabla `usuarios` separada.

**Alternativa considerada**: Crear tabla `usuarios` con FK 1:1 a `users`.

**Por qué**: 
- La KB define Usuario como "identidad base" — exactamente lo que representa User. Crear dos tablas de identidad sería confuso y requeriría sync constante.
- Todas las entidades existentes (audit_log, user_roles) ya referencian `users.id`. Cambiarlas a `usuarios.id` implicaría modificar modelos archivados.
- Una sola tabla simplifica queries: no hay joins para obtener el perfil completo.

### D2: PII cifrada con AES-256-GCM reutilizando core/security.py
**Decisión**: Todos los campos PII (cuil, cbu, alias_cbu, email, dni — además de nombre/apellido ya existentes) se cifran con `encrypt()`/`decrypt()` de `app/core/security.py`.

**Por qué**: 
- Ya existe y está probada en C-03 (nombre_cifrado, apellido_cifrado, dni_cifrado).
- AES-256-GCM con nonce de 12 bytes + ciphertext, todo en base64.
- Consistencia: mismo mecanismo para toda PII del sistema.

**Implementación**: Los schemas Pydantic de response NUNCA exponen campos cifrados en texto plano. Se exponen como metadatos (ej: `tiene_cuil: bool`) o se excluyen directamente. Un método helper descifra solo cuando el endpoint lo requiere explícitamente.

### D3: email se cifra en reposo
**Decisión**: El campo `email` existente en `users` (actualmente texto plano para permitir login) pasa a almacenarse cifrado.

**Trade-off**: El login (C-03) actualmente busca por email en texto plano. Con email cifrado, la búsqueda requiere descifrar columna por columna o mantener un índice de hash.

**Solución**: 
- Se agrega columna `email_hash` (SHA-256 del email normalizado a lowercase) como índice único para búsqueda.
- El login busca por `email_hash` y descifra el `email_cifrado` para verificar coincidencia exacta.
- `email_cifrado` reemplaza al `email` actual como storage.
- Se mantiene unique constraint sobre `email_hash` para enforce unicidad.

### D4: Asignacion con contexto nullable
**Decisión**: materia_id, carrera_id, cohorte_id son todos nullable en Asignacion. Esto permite roles sin contexto académico (ADMIN, FINANZAS) y roles con contexto parcial (NEXO).

**Validación**: Al menos uno de los tres contextos debe ser no nulo, excepto para roles globales (ADMIN, FINANZAS).

### D5: estado_vigencia es derivado, no almacenado
**Decisión**: El campo `estado_vigencia` (Vigente/Vencida) NO se almacena en DB. Se calcula comparando `desde`/`hasta` con la fecha actual en el service layer.

**Por qué**: Es un valor derivado puro. Almacenarlo requeriría sync con un job periódico o trigger, agregando complejidad sin beneficio real. La consulta de "asignaciones vigentes" se resuelve con `WHERE hasta IS NULL OR hasta >= CURRENT_DATE`.

### D6: Nuevos permisos en matriz RBAC
**Decisión**: Se agregan dos permisos:
- `usuarios:gestionar` → rol ADMIN
- `equipos:asignar` → roles COORDINADOR, ADMIN

Se seedean en la migración 006 junto con las tablas.

## Riesgos / Trade-offs

- [R1] El cambio de email a cifrado requiere modificar el login de C-03 → mitigación: agregar email_hash como columna de búsqueda, migración de datos on-premise para emails existentes
- [R2] PII cifrada impide búsqueda directa por DNI/CUIL → mitigación: agregar hash indexado para búsqueda cuando sea necesario en C-08/C-20
- [R3] La relación User ↔ Asignacion ↔ Sistema de permisos actual (user_roles de C-04) puede generar confusión → mitigación: documentar que Asignacion reemplaza a user_roles para el dominio académico; user_roles se deprecará en C-08

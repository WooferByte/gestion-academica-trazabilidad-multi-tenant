## ADDED Requirements

### Requirement: Modelo User

El sistema SHALL tener un modelo `User` que representa una persona física autenticable dentro de un tenant. Cada usuario pertenece a exactamente un tenant.

#### Scenario: Creación de usuario con todos los campos

- **GIVEN** un payload válido con `email`, `password`, `nombre`, `apellido`, `dni` y `roles`
- **WHEN** se crea el usuario vía UserRepository
- **THEN** el usuario se persiste con `id` UUID v4, `email` en texto plano, `password_hash` con Argon2id, `nombre_cifrado`, `apellido_cifrado` y `dni_cifrado` como AES-256, `roles` como lista vacía o la provista, `created_at`/`updated_at` no nulos, `is_active=True`

#### Scenario: Email único por tenant

- **GIVEN** un usuario con `email` "juan@test.com" en tenant A
- **WHEN** se intenta crear otro usuario con el mismo email en el mismo tenant
- **THEN** el sistema rechaza con error de integridad (unique constraint violation)

#### Scenario: Mismo email en distintos tenants

- **GIVEN** un usuario con `email` "juan@test.com" en tenant A
- **WHEN** se crea un usuario con el mismo email en tenant B
- **THEN** la operación es exitosa (no hay conflicto entre tenants)

#### Scenario: Soft delete de usuario

- **GIVEN** un usuario existente
- **WHEN** se ejecuta soft_delete sobre el usuario
- **THEN** `deleted_at` se setea con timestamp actual
- **AND** el usuario ya no aparece en queries default
- **AND** el usuario no puede hacer login

### Requirement: Password hasheado con Argon2id

El sistema SHALL almacenar las contraseñas usando Argon2id. Nunca en texto plano.

#### Scenario: Hash de password

- **GIVEN** una contraseña en texto plano
- **WHEN** se hashea con `hash_password()`
- **THEN** el resultado es un string no vacío que comienza con el prefijo `$argon2id$`

#### Scenario: Verificación de password correcta

- **GIVEN** un hash generado con `hash_password("mi_pass")`
- **WHEN** se verifica con `verify_password("mi_pass", hash)`
- **THEN** el resultado es `True`

#### Scenario: Verificación de password incorrecta

- **GIVEN** un hash generado con `hash_password("mi_pass")`
- **WHEN** se verifica con `verify_password("wrong_pass", hash)`
- **THEN** el resultado es `False`

### Requirement: PII cifrada en reposo

El sistema SHALL cifrar los campos PII (nombre, apellido, DNI) usando AES-256-GCM antés de persistirlos.

#### Scenario: Campos PII se almacenan cifrados

- **GIVEN** un usuario con `nombre="Juan"`, `apellido="Pérez"`
- **WHEN** se persiste el usuario
- **THEN** en la base de datos los campos `nombre_cifrado` y `apellido_cifrado` contienen strings distintos de "Juan" y "Pérez" (cifrados en base64)
- **AND** al descifrar con `decrypt()`, los valores originales se recuperan correctamente

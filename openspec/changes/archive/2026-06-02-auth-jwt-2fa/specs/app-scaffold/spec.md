## MODIFIED Requirements

### Requirement: core/dependencies.py — get_current_user implementado

**Nota**: Este requirement modifica el esqueleto dejado por C-01. El placeholder `# ── RESERVADO para C-03: get_current_user` se reemplaza por implementación real.

El archivo `core/dependencies.py` SHALL proveer la dependency `get_current_user` que extrae y verifica el JWT, resuelve el usuario y el tenant activo, y retorna un `UserContext`.

#### Scenario: get_current_user funciona como dependency

- **GIVEN** un endpoint protegido con `Depends(get_current_user)`
- **WHEN** se envía un request con `Authorization: Bearer <valid_jwt>`
- **THEN** el endpoint recibe `UserContext` con los datos del usuario autenticado
- **WHEN** se envía un request sin token
- **THEN** el endpoint retorna `401`

### Requirement: core/config.py — Settings para JWT

El sistema SHALL agregar opciones de configuración JWT a `Settings`: `refresh_token_expire_days` (INT, default 30).

#### Scenario: Refresh token expire days configurable

- **GIVEN** una variable de entorno `REFRESH_TOKEN_EXPIRE_DAYS=60`
- **WHEN** se accede a `settings.refresh_token_expire_days`
- **THEN** el valor es `60`

### Requirement: core/security.py — funciones JWT y Argon2id

El archivo `core/security.py` SHALL agregar funciones para creación y verificación de JWT, y para hashing/verificación de passwords con Argon2id.

#### Scenario: Creación de JWT

- **GIVEN** un user_id, tenant_id y roles
- **WHEN** se llama a `create_access_token(user_id, tenant_id, roles)`
- **THEN** retorna un string JWT firmado con `SECRET_KEY`
- **AND** el JWT decodificado contiene los claims `sub`, `tenant_id`, `roles`, `exp`, `iat`

#### Scenario: Verificación de JWT

- **GIVEN** un JWT firmado correctamente
- **WHEN** se llama a `decode_token(token)`
- **THEN** retorna el payload decodificado como dict
- **WHEN** el token está vencido
- **THEN** lanza `jwt.ExpiredSignatureError`
- **WHEN** la firma es inválida
- **THEN** lanza `jwt.InvalidSignatureError`

#### Scenario: Hash de password con Argon2id

- **GIVEN** un password en texto plano
- **WHEN** se llama a `hash_password(password)`
- **THEN** retorna un string con formato Argon2id
- **WHEN** se llama a `verify_password(plain, hashed)`
- **THEN** retorna `True` si coincide, `False` si no

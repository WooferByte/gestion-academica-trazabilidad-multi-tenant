## ADDED Requirements

### Requirement: Estructura de directorios Clean Architecture

El backend SHALL organizarse bajo `backend/app/` con una separación estricta por capas: `api/v1/routers/` (transporte HTTP), `services/` (lógica de negocio), `repositories/` (acceso a datos), `models/` (entidades ORM), `schemas/` (DTOs Pydantic), `core/` (configuración y transversales), `integrations/` (clientes externos) y `workers/` (jobs en background). El flujo de dependencia SHALL ser unidireccional Routers → Services → Repositories → Models.

#### Scenario: Existe el árbol de capas completo

- **WHEN** se inspecciona el árbol `backend/app/`
- **THEN** existen los paquetes `api/v1/routers/`, `services/`, `repositories/`, `models/`, `schemas/`, `core/`, `integrations/` y `workers/`
- **AND** cada paquete contiene un `__init__.py` que lo hace importable

#### Scenario: Importabilidad del paquete raíz

- **WHEN** se importa `app` desde el intérprete de Python en el contexto del backend
- **THEN** la importación resuelve sin errores

### Requirement: Slots reservados de transversales

El paquete `core/` SHALL reservar los módulos `security.py`, `permissions.py`, `tenancy.py`, `dependencies.py` y `exceptions.py` como placeholders sin lógica de negocio, para ser completados por changes posteriores (C-02, C-03, C-04). C-01 NO SHALL implementar autenticación, autorización ni resolución de tenant.

#### Scenario: Los slots existen pero están vacíos de lógica

- **WHEN** se inspecciona `backend/app/core/`
- **THEN** existen los archivos `security.py`, `permissions.py`, `tenancy.py`, `dependencies.py` y `exceptions.py`
- **AND** ninguno contiene lógica de auth, RBAC o tenancy (solo placeholder / docstring de intención)

### Requirement: Límite de tamaño de archivo

Cada archivo del backend SHALL no superar las 500 líneas de código (LOC), como convención de mantenibilidad de la Clean Architecture del proyecto.

#### Scenario: Ningún archivo del scaffold excede el límite

- **WHEN** se mide la cantidad de líneas de cualquier archivo `.py` creado en este change
- **THEN** ninguno supera las 500 líneas

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

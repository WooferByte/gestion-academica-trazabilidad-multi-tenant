## Why

Activia-trace necesita enviar comunicaciones a alumnos (emails) como parte del flujo de detección de atrasados (Épica 3). Hoy no existe modelo de datos, cola de procesamiento ni API para gestionar estos envíos. Implementar la cola de comunicaciones con desacoplamiento asincrónico es requisito para habilitar el envío masivo con trazabilidad de estados, preview obligatorio y aprobación humana configurable por tenant.

## What Changes

- Nuevo modelo `Comunicacion` con ciclo de vida Pendiente → Enviando → Enviado | Error | Cancelado
- Worker asíncrono que reemplaza el placeholder no-op en `workers/main.py`: consume la tabla-como-cola y transiciona estados
- API REST `/api/v1/comunicaciones` con endpoints: enviar (encola), preview, aprobar/rechazar, cancelar, listar por lote
- Migración Alembic 009 con tabla `comunicaciones`
- Permisos RBAC: `comunicacion:enviar`, `comunicacion:aprobar`
- Código de auditoría `COMUNICACION_ENVIAR` (ya existe en `audit_codes.py`)
- Destinatario almacenado cifrado con AES-256
- Plantillas de mensajes con variables de sustitución `{{alumno.nombre}}`, `{{materia.nombre}}`

## Capabilities

### New Capabilities
- `comunicaciones-cola`: Envío asincrónico de emails con cola, estados y trazabilidad por lote
- `comunicaciones-aprobacion`: Aprobación humana configurable por tenant para envíos masivos
- `comunicaciones-worker`: Worker de despacho que procesa la cola y transiciona estados

### Modified Capabilities

Ninguna. Espec nueva sin cambios sobre capacidades existentes.

## Impact

- **Backend**: nuevo modelo `Comunicacion`, repositorio, servicio schema, router y worker
- **DB**: migración 009 con tabla `comunicaciones` e índices
- **Worker**: `workers/main.py` se reescribe con lógica real
- **Auth**: dos nuevos permisos en la matriz RBAC (`comunicacion:enviar`, `comunicacion:aprobar`)
- **Auditoría**: código `COMUNICACION_ENVIAR` ya definido en audit_codes.py
- **Frontend (futuro)**: no se toca ahora, pero el API expone todo lo necesario para la UI de comunicaciones

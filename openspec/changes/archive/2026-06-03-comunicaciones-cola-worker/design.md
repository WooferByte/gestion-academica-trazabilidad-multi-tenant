## Context

Activia-trace ya tiene el placeholder del worker en `workers/main.py` (loop no-op, C-01). No existe modelo `Comunicacion`, repositorio, servicio ni router para gestionar envíos. La KB (E21, RN-15, RN-16, RN-17, F3.1–F3.3, FL-02 pasos 7-8, FL-04) define el dominio completo.

Se elige **tabla como cola** (sin RabbitMQ/Redis) para MVP — la comunicación es eventual, no requiere latencia real-time y el volumen esperado es moderado (cientos de envíos/día).

El flag de aprobación se almacena en la tabla `tenants` (columna `aprobacion_comunicaciones bool default false`).

## Goals / Non-Goals

**Goals:**
- Modelo `Comunicacion` con ciclo de vida completo (RN-15)
- API REST para encolar, preview, aprobar/rechazar, cancelar, listar
- Worker asíncrono que reemplaza el placeholder y procesa la cola
- Destinatario cifrado AES-256 en reposo
- Preview obligatorio antes de encolar (RN-16)
- Aprobación configurable por tenant (F3.3, RN-17)
- Migración 009 de Alembic
- Tests: máquina de estados, preview, aprobación, destinatario cifrado, worker

**Non-Goals:**
- Infraestructura de cola externa (RabbitMQ, Redis, SQS)
- Frontend de comunicaciones (se construye en change posterior)
- Mensajería interna entre usuarios (F3.4)
- Tablón de avisos (F3.5)
- Integración con proveedor SMTP real en MVP (se mockea en tests)

## Decisions

### 1. Tabla como cola (DB polling)

| Alternativa | Veredicto |
|-------------|-----------|
| Tabla DB + polling | ✅ Elegido. Sin dependencias externas, transaccional con el modelo, suficiente para MVP |
| RabbitMQ/Redis | Descartado. Complejidad operativa sin beneficio comprobado al volumen esperado |

### 2. Destinatario cifrado AES-256

Se reutiliza `app.core.security.encrypt/decrypt` (AES-GCM existente). El endpoint de listado descifra el destinatario solo para el usuario que creó el lote (el `enviado_por` coincide con el actor).

### 3. Aprobación como flag en tenants

| Alternativa | Veredicto |
|-------------|-----------|
| Columna `aprobacion_comunicaciones` en `tenants` | ✅ Elegido. Simple, ya existe la tabla Tenant con configuración |
| Tabla separada `tenant_config` | Descartado. Over-engineering para un solo flag |

### 4. Worker asyncio nativo

Se usa `asyncio` directamente (sin Celery/ARQ). El placeholder ya usa esta estructura. Se agrega sleep configurable entre batches y manejo de señales para shutdown graceful.

### 5. Plantillas con `str.replace`

Las variables `{{...}}` se resuelven con reemplazo de string simple (sin motor de templates). Suficiente para el patrón de variables conocido.

## Risks / Trade-offs

- **Polling DB sin índice puede degradar**: mitigación → índice compuesto en `(estado, tenant_id, deleted_at)`.
- **Worker single-thread**: si el volumen crece, se escala con múltiples réplicas del worker + batch más pequeño.
- **Sin cola externa, no hay dead-letter queue**: los mensajes en Error requieren reintento manual o reintento programado (futuro).
- **Cifrado del destinatario impide búsqueda por email**: aceptado — se usa `lote_id` como clave de agrupación primaria.
